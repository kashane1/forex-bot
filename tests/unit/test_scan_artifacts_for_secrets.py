"""Tests for the artifact secret-scan script
(Phase 9, oanda-practice-readonly-001).

Cover the pure scan logic: credential-value extraction, value matching,
and the OANDA token / account-id patterns — including that they do NOT
flag a bare SHA-256 hash or a redacted account id.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


scan = _load_script("scan_artifacts_for_secrets")


# --------------------------------------------------------------------------
# collect_secret_values
# --------------------------------------------------------------------------


def test_collect_secret_values_extracts_real_values():
    env = {
        "OANDA_ACCESS_TOKEN_PRACTICE": "realtoken0123456789",
        "OANDA_ACCOUNT_ID_PRACTICE": "101-001-12345678-001",
    }
    values = scan.collect_secret_values(env)
    assert "OANDA_ACCESS_TOKEN_PRACTICE" in values
    assert "OANDA_ACCOUNT_ID_PRACTICE" in values
    # the account id also gets a no-dash variant.
    assert "10100112345678001" in values.values()


def test_collect_secret_values_ignores_placeholders_and_empty():
    env = {
        "OANDA_ACCESS_TOKEN_PRACTICE": "realtoken",
        "OANDA_ACCESS_TOKEN_LIVE": "replace_me_only_when_ready",
        "OANDA_ACCOUNT_ID_LIVE": "",
    }
    values = scan.collect_secret_values(env)
    assert "OANDA_ACCESS_TOKEN_PRACTICE" in values
    assert "OANDA_ACCESS_TOKEN_LIVE" not in values
    assert "OANDA_ACCOUNT_ID_LIVE" not in values


# --------------------------------------------------------------------------
# scan_text — value scan
# --------------------------------------------------------------------------


def test_value_scan_finds_a_planted_value():
    values = {"OANDA_ACCESS_TOKEN_PRACTICE": "supersecrettoken"}
    kinds = scan.scan_text(
        "broker config: supersecrettoken in here",
        values=values,
        check_patterns=False,
    )
    assert len(kinds) == 1
    assert "OANDA_ACCESS_TOKEN_PRACTICE" in kinds[0]


def test_value_scan_clean_text_has_no_findings():
    values = {"OANDA_ACCESS_TOKEN_PRACTICE": "supersecrettoken"}
    kinds = scan.scan_text("ordinary text", values=values, check_patterns=False)
    assert kinds == []


# --------------------------------------------------------------------------
# scan_text — pattern scan
# --------------------------------------------------------------------------


def test_pattern_scan_flags_token_and_account_shapes():
    token = "a" * 64 + "-" + "b" * 16
    account = "101-001-12345678-001"
    assert scan.scan_text(token, values={}, check_patterns=True)
    assert scan.scan_text(account, values={}, check_patterns=True)


def test_pattern_scan_does_not_flag_a_bare_sha256():
    # A committed data hash is 64 hex with no token-style suffix.
    assert scan.scan_text("f" * 64, values={}, check_patterns=True) == []


def test_pattern_scan_does_not_flag_a_redacted_account_id():
    # The first-3 / last-3 redaction uses an ellipsis — not digit-shaped.
    assert scan.scan_text("account 101…001", values={}, check_patterns=True) == []


def test_pattern_scan_disabled_runs_value_scan_only():
    values = {"OANDA_ACCOUNT_ID_PRACTICE": "101-001-12345678-001"}
    text = "101-001-12345678-001 plus " + "a" * 64 + "-" + "b" * 16
    kinds = scan.scan_text(text, values=values, check_patterns=False)
    # token-shaped string present, but patterns disabled -> only the value.
    assert len(kinds) == 1
    assert "OANDA_ACCOUNT_ID_PRACTICE" in kinds[0]
