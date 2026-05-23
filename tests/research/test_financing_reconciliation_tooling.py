"""Tests for scripts/reconcile_financing_fixtures.py.

Covers: happy-path reconciliation, deterministic JSON +
markdown output, schema-failure exit codes, missing-file exit
codes, mismatch classification, strategy_evidence /
financing_in_engine_pnl / financing_is_live_blocker rails,
defense-in-depth MODELED refusal, and import isolation
(script must not import broker / OANDA modules, must not read
env vars).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "reconcile_financing_fixtures.py"
FIXTURES = REPO_ROOT / "research" / "financing" / "fixtures"


@pytest.fixture
def script_module():
    """Import the script as a module (it doesn't ship as a
    package, so we load it from the file path).

    Done once per test for isolation."""
    spec = importlib.util.spec_from_file_location(
        "reconcile_financing_fixtures", SCRIPT
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# ---------- Happy-path reconciliation ----------


def _run_clean(script_module, tmp_path: Path, extra: list[str] | None = None) -> int:
    args = [
        "--observed",
        str(FIXTURES / "observed_multi_day_with_triple.json"),
        "--rates",
        str(FIXTURES / "rates_two_week_eur_usd.json"),
        "--output",
        str(tmp_path),
        "--missing-rate-policy",
        "skip",
        "--generated-at-utc",
        "2026-05-23T12:00:00+00:00",
    ]
    if extra:
        args.extend(extra)
    return script_module.run(args)


def test_happy_path_exits_zero(script_module, tmp_path: Path) -> None:
    code = _run_clean(script_module, tmp_path)
    assert code == script_module.EXIT_OK
    assert (tmp_path / "reconciliation.json").exists()
    assert (tmp_path / "reconciliation.md").exists()


def test_happy_path_json_shape(script_module, tmp_path: Path) -> None:
    _run_clean(script_module, tmp_path)
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    assert payload["tool"] == script_module.TOOL_NAME
    assert payload["tool_version"] == script_module.TOOL_VERSION
    assert payload["strategy_evidence"] is False
    assert payload["financing_in_engine_pnl"] is False
    assert payload["financing_is_live_blocker"] is True
    assert payload["financing_treatment"] == "estimated"
    assert payload["summary"]["row_count"] == 4
    assert payload["summary"]["match"] == 3
    assert payload["summary"]["mismatch"] == 0
    assert payload["summary"]["missing_in_calculated"] == 1


def test_happy_path_md_contains_required_sections(
    script_module, tmp_path: Path
) -> None:
    _run_clean(script_module, tmp_path)
    text = (tmp_path / "reconciliation.md").read_text(encoding="utf-8")
    assert "# Financing Reconciliation" in text
    assert "## Inputs" in text
    assert "## Window" in text
    assert "## Summary" in text
    assert "## Rows" in text
    assert "strategy_evidence: false" in text
    assert "financing_treatment: estimated" in text
    assert "financing_is_live_blocker: true" in text
    assert "financing_in_engine_pnl: false" in text


# ---------- Determinism ----------


def test_json_output_is_deterministic(
    script_module, tmp_path: Path
) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    _run_clean(script_module, a)
    _run_clean(script_module, b)
    assert (a / "reconciliation.json").read_text(encoding="utf-8") == (
        b / "reconciliation.json"
    ).read_text(encoding="utf-8")


def test_md_output_is_deterministic(script_module, tmp_path: Path) -> None:
    a = tmp_path / "a"
    b = tmp_path / "b"
    _run_clean(script_module, a)
    _run_clean(script_module, b)
    assert (a / "reconciliation.md").read_text(encoding="utf-8") == (
        b / "reconciliation.md"
    ).read_text(encoding="utf-8")


# ---------- Exit codes ----------


def test_missing_observed_file_exits_schema(
    script_module, tmp_path: Path
) -> None:
    code = script_module.run(
        [
            "--observed",
            str(tmp_path / "does-not-exist.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
        ]
    )
    assert code == script_module.EXIT_SCHEMA


def test_invalid_observed_schema_exits_schema(
    script_module, tmp_path: Path
) -> None:
    bad = tmp_path / "bad-observed.json"
    bad.write_text(
        json.dumps({"kind": "wrong", "schema_version": 1}),
        encoding="utf-8",
    )
    code = script_module.run(
        [
            "--observed",
            str(bad),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
        ]
    )
    assert code == script_module.EXIT_SCHEMA


def test_missing_rate_fixture_exits_schema(
    script_module, tmp_path: Path
) -> None:
    code = script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_multi_day_with_triple.json"),
            "--rates",
            str(tmp_path / "does-not-exist.json"),
            "--output",
            str(tmp_path),
        ]
    )
    assert code == script_module.EXIT_SCHEMA


def test_default_conservative_policy_produces_mismatch(
    script_module, tmp_path: Path
) -> None:
    """Running with the default conservative policy against the
    multi-day fixture pair yields a mismatch on the rate
    fixture's intentionally-missing 5/19 date (calculator
    fires the -1.296 fallback vs observed -0.054). Exit 2."""
    code = script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_multi_day_with_triple.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
            "--generated-at-utc",
            "2026-05-23T12:00:00+00:00",
        ]
    )
    assert code == script_module.EXIT_MISMATCH
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    assert payload["summary"]["mismatch"] == 1


def test_mismatch_classification_appears_in_output(
    script_module, tmp_path: Path
) -> None:
    """The default-conservative run must contain a row whose
    classification is exactly 'mismatch'."""
    script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_multi_day_with_triple.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
        ]
    )
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    classes = [row["classification"] for row in payload["rows"]]
    assert "mismatch" in classes


def test_missing_rate_error_policy_exits_5(
    script_module, tmp_path: Path
) -> None:
    """With --missing-rate-policy error and a rate fixture
    that omits 5/19, the calculator raises and the CLI exits
    EXIT_MISSING_RATE_ERROR (5)."""
    code = script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_multi_day_with_triple.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
            "--missing-rate-policy",
            "error",
        ]
    )
    assert code == script_module.EXIT_MISSING_RATE_ERROR


def test_naive_generated_at_utc_exits_schema(
    script_module, tmp_path: Path
) -> None:
    code = script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_multi_day_with_triple.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
            "--generated-at-utc",
            "2026-05-23T12:00:00",  # no offset
        ]
    )
    assert code == script_module.EXIT_SCHEMA


# ---------- Strategy-evidence + MODELED rails ----------


def test_strategy_evidence_remains_false_in_outputs(
    script_module, tmp_path: Path
) -> None:
    _run_clean(script_module, tmp_path)
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    assert payload["strategy_evidence"] is False
    md = (tmp_path / "reconciliation.md").read_text(encoding="utf-8")
    assert "strategy_evidence: true" not in md


def test_modeled_is_never_emitted(
    script_module, tmp_path: Path
) -> None:
    _run_clean(script_module, tmp_path)
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    assert payload["financing_treatment"] != "modeled"
    md = (tmp_path / "reconciliation.md").read_text(encoding="utf-8")
    assert "financing_treatment: modeled" not in md


def test_build_report_refuses_modeled_treatment(script_module) -> None:
    """Defense-in-depth: even if a future bug allowed a MODELED
    rate source through the loader and calculator, _build_report
    raises RuntimeError before any file is written."""
    from research.financing.models import FinancingTreatment

    with pytest.raises(RuntimeError, match="MODELED"):
        script_module._build_report(
            observed=[],
            rate_source_name="x",
            rate_source_treatment=FinancingTreatment.MODELED,
            inputs_block={},
            window_open=script_module._parse_now("2026-05-23T00:00:00+00:00"),
            window_close=script_module._parse_now("2026-05-23T01:00:00+00:00"),
            home_currency="USD",
            calc_events_by_key={},
            tolerance=1e-9,
            generated_at_utc=script_module._parse_now("2026-05-23T12:00:00+00:00"),
        )


# ---------- Import isolation ----------


def test_script_does_not_import_forex_bot() -> None:
    """Grep-enforced rail: the reconciliation script must not
    import any broker / OANDA / forex_bot module."""
    text = SCRIPT.read_text(encoding="utf-8")
    for line_no, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if not (stripped.startswith("import ") or stripped.startswith("from ")):
            continue
        for forbidden in ("forex_bot", "oanda"):
            if forbidden in stripped:
                raise AssertionError(
                    f"scripts/reconcile_financing_fixtures.py:{line_no} "
                    f"imports {forbidden}: {stripped}"
                )


def test_script_does_not_read_env_vars(
    script_module, tmp_path: Path, monkeypatch
) -> None:
    """The script must not read OANDA-shaped env vars. Verify
    by setting tripwire vars first, then installing an
    ``os.environ.get`` spy that records every call during the
    run; any access of OANDA_* / *TOKEN* / *SECRET* / *KEY*
    vars fails the test.

    Ordering matters: ``monkeypatch.setenv`` itself uses
    ``os.environ.get`` internally, so the spy is installed
    AFTER any tripwires are set."""
    monkeypatch.setenv("OANDA_ACCESS_TOKEN", "TRIPWIRE")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "TRIPWIRE")

    forbidden_substrings = ("OANDA_", "TOKEN", "SECRET", "ACCESS_KEY")
    accessed: list[str] = []

    real_get = os.environ.get

    def _spy(key, default=None):
        accessed.append(key)
        return real_get(key, default)

    monkeypatch.setattr(os.environ, "get", _spy)

    _run_clean(script_module, tmp_path)

    bad = [k for k in accessed if any(s in k for s in forbidden_substrings)]
    assert bad == [], f"script read forbidden env vars: {bad}"


def test_script_does_not_print_credentials(
    script_module, tmp_path: Path, monkeypatch, capsys
) -> None:
    """Tripwire env values must never appear in stdout or
    stderr."""
    monkeypatch.setenv("OANDA_ACCESS_TOKEN", "TRIPWIRE_TOKEN_VALUE_XYZ")
    monkeypatch.setenv("OANDA_ACCOUNT_ID", "TRIPWIRE_ACCOUNT_ID_QQQ")
    _run_clean(script_module, tmp_path)
    captured = capsys.readouterr()
    for needle in ("TRIPWIRE_TOKEN_VALUE_XYZ", "TRIPWIRE_ACCOUNT_ID_QQQ"):
        assert needle not in captured.out
        assert needle not in captured.err


# ---------- Sanity: outputs are small ----------


def test_outputs_are_small(script_module, tmp_path: Path) -> None:
    _run_clean(script_module, tmp_path)
    for name in ("reconciliation.json", "reconciliation.md"):
        size = (tmp_path / name).stat().st_size
        assert size < 50 * 1024, f"{name} is {size} bytes — > 50 KB"


# ---------- Empty observed file ----------


def test_empty_observed_file_produces_empty_report(
    script_module, tmp_path: Path
) -> None:
    code = script_module.run(
        [
            "--observed",
            str(FIXTURES / "observed_same_day_no_rollover.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
            "--generated-at-utc",
            "2026-05-23T12:00:00+00:00",
        ]
    )
    assert code == script_module.EXIT_OK
    payload = json.loads((tmp_path / "reconciliation.json").read_text(encoding="utf-8"))
    assert payload["summary"]["row_count"] == 0
    assert payload["summary"]["match"] == 0
    assert payload["summary"]["mismatch"] == 0
    md = (tmp_path / "reconciliation.md").read_text(encoding="utf-8")
    assert "_no rows_" in md


# ---------- main() is callable for completeness ----------


def test_main_callable(script_module, tmp_path: Path) -> None:
    """main(argv) delegates to run(argv). Exists so callers can
    use either entrypoint."""
    code = script_module.main(
        [
            "--observed",
            str(FIXTURES / "observed_same_day_no_rollover.json"),
            "--rates",
            str(FIXTURES / "rates_two_week_eur_usd.json"),
            "--output",
            str(tmp_path),
            "--generated-at-utc",
            "2026-05-23T12:00:00+00:00",
        ]
    )
    assert code == script_module.EXIT_OK


# ---------- Module is importable without forex_bot in sys.modules ----------


def test_script_module_does_not_pull_in_forex_bot(
    script_module,
) -> None:
    """After importing the script, no submodule of forex_bot
    should be in sys.modules. This catches any future change
    that adds a transitive forex_bot import."""
    forex_modules = [m for m in sys.modules if m == "forex_bot" or m.startswith("forex_bot.")]
    # Other tests in the suite legitimately import forex_bot
    # (e.g. test_financing_fixtures.test_loaded_event_field_set_matches_canonical_schema).
    # Re-check only what the script itself pulled in by importing
    # only it in an isolated child interpreter; but importlib
    # already exec'd it once, so the module set may include
    # forex_bot. Approach: import the script via subprocess as a
    # fresh interpreter, then inspect.
    import subprocess

    code = (
        "import sys, importlib.util\n"
        f"spec = importlib.util.spec_from_file_location('r', r'{SCRIPT}')\n"
        "mod = importlib.util.module_from_spec(spec)\n"
        "spec.loader.exec_module(mod)\n"
        "names = sorted(m for m in sys.modules if m == 'forex_bot' or m.startswith('forex_bot.'))\n"
        "print('\\n'.join(names))\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        check=True,
    )
    forex_modules = [
        line for line in result.stdout.strip().splitlines() if line
    ]
    assert forex_modules == [], (
        "importing the script pulled in forex_bot modules: "
        + ", ".join(forex_modules)
    )
