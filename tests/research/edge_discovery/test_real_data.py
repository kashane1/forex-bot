"""Tests for the real-artifact loaders in
``research/edge_discovery/real_data.py``.

The committed CAMPAIGN_010-014 artifacts on this branch are real
inputs, so most tests run directly against them. The H4 SQLite store
is gitignored and operator-local; tests for that path either build a
tiny fixture SQLite DB on the fly or guard the assertion with
``pytest.skipif`` so CI on a fresh clone passes.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import pytest
from research.edge_discovery.real_data import (
    EDGE_DISCOVERY_H4_DB_ENV,
    SEVEN_MAJORS,
    StudyInput,
    StudyProvenance,
    assert_real_data_kind,
    fold_pair_summaries_to_frame,
    load_campaign_fold_pair_summaries,
    load_campaign_trades,
    load_campaign_walk_forward_result,
    load_canonical_null_baseline_rollup,
    load_event_fixture_json,
    load_h4_candles_from_sqlite,
    resolve_h4_store_path,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
CAMPAIGN_011_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_011_random_entry_anchor"
CAMPAIGN_014_DIR = REPO_ROOT / "backtests" / "CAMPAIGN_014_calendar_event_window_anomaly"
EVENT_FIXTURE_PATH = REPO_ROOT / "research" / "calendar" / "fixtures" / "campaign_014_events.json"


# ---------------------------------------------------------------------------
# CAMPAIGN walk-forward results
# ---------------------------------------------------------------------------


def test_load_canonical_null_baseline_rollup_is_deduped() -> None:
    """Post-dedupe null comparisons must use the canonical rollup."""
    rollup = load_canonical_null_baseline_rollup()
    assert rollup["canonical"] is True
    assert rollup["aggregate"]["total_trades"] == 1180
    assert rollup["aggregate"]["aggregate_expectancy_r"] == pytest.approx(
        -0.0029154071495408797
    )


def test_load_campaign_011_walk_forward_result_legacy_contaminated() -> None:
    """Pre-fix walk_forward artifact remains loadable but is superseded."""
    r = load_campaign_walk_forward_result(CAMPAIGN_011_DIR)
    assert r.campaign_name == "CAMPAIGN_011_random_entry_anchor"
    assert r.overall_verdict == "REJECT"
    assert r.strategy_evidence is False
    assert r.aggregate["fold_count"] == 8
    assert r.aggregate["folds_passing_gates"] == 0
    assert r.aggregate["total_trades_across_folds"] == 1177
    # Null model expectancy must hug zero — exact match to committed
    # WALK_FORWARD_RESULT.md.
    assert r.aggregate["aggregate_expectancy_r"] == pytest.approx(-0.0024, abs=0.0005)
    assert len(r.fold_metrics) == 8
    assert len(r.source_sha256) == 64


def test_load_campaign_014_walk_forward_result_reject() -> None:
    r = load_campaign_walk_forward_result(CAMPAIGN_014_DIR)
    assert r.campaign_name == "CAMPAIGN_014_calendar_event_window_anomaly"
    assert r.overall_verdict == "REJECT"
    assert r.strategy_evidence is False
    assert r.aggregate["fold_count"] == 8
    assert r.aggregate["folds_passing_gates"] == 0
    assert r.aggregate["total_trades_across_folds"] == 720
    assert r.aggregate["aggregate_expectancy_r"] == pytest.approx(-0.1477, abs=0.001)


def test_load_campaign_walk_forward_result_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match=r"walk_forward results\.json"):
        load_campaign_walk_forward_result(tmp_path / "NO_SUCH_CAMPAIGN")


# ---------------------------------------------------------------------------
# Per-fold per-pair summaries
# ---------------------------------------------------------------------------


def test_load_campaign_011_fold_pair_summaries_has_eight_folds_seven_pairs() -> None:
    summaries = load_campaign_fold_pair_summaries(CAMPAIGN_011_DIR)
    # 8 folds × 7 pairs = 56 summaries per campaign.
    assert len(summaries) == 56
    folds_seen = {s.fold_index for s in summaries}
    assert folds_seen == set(range(8))
    pairs_seen = {s.instrument for s in summaries}
    assert pairs_seen == set(SEVEN_MAJORS)
    for s in summaries:
        assert s.strategy_name == "random_entry_anchor"
        assert s.granularity == "H4"
        assert "expectancy_r" in s.metrics
        assert "trade_count" in s.metrics


def test_fold_pair_summaries_to_frame_lifts_metrics() -> None:
    summaries = load_campaign_fold_pair_summaries(CAMPAIGN_014_DIR)
    df = fold_pair_summaries_to_frame(summaries)
    assert len(df) == 56
    expected_cols = {
        "campaign_name", "fold_index", "instrument", "strategy_name",
        "metric_expectancy_r", "metric_trade_count", "metric_profit_factor",
    }
    assert expected_cols.issubset(set(df.columns))
    # Per-campaign trade count must sum to the published aggregate.
    assert int(df["metric_trade_count"].sum()) == 720


def test_load_campaign_fold_pair_summaries_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="campaign folds dir"):
        load_campaign_fold_pair_summaries(tmp_path / "NO_SUCH_CAMPAIGN")


# ---------------------------------------------------------------------------
# Per-fold per-pair trade CSVs
# ---------------------------------------------------------------------------


def test_load_campaign_014_trades_matches_aggregate_count() -> None:
    trades = load_campaign_trades(CAMPAIGN_014_DIR)
    # 720 trades per the committed aggregate.
    assert len(trades) == 720
    assert {"campaign_name", "fold_index", "instrument", "r_multiple"}.issubset(set(trades.columns))
    assert trades["campaign_name"].nunique() == 1
    assert trades["fold_index"].nunique() == 8
    assert set(trades["instrument"].unique()) == set(SEVEN_MAJORS)
    # entry_time / exit_time are UTC-aware datetimes.
    assert str(trades["entry_time"].dt.tz) == "UTC"


def test_load_campaign_trades_subset_filter_works() -> None:
    eur_only = load_campaign_trades(CAMPAIGN_014_DIR, instruments=["EUR_USD"])
    assert (eur_only["instrument"] == "EUR_USD").all()
    assert len(eur_only) > 0
    assert len(eur_only) < 720  # strictly fewer than the full set


def test_load_campaign_trades_empty_filter_returns_empty_frame_with_schema() -> None:
    empty = load_campaign_trades(CAMPAIGN_014_DIR, instruments=["NOT_A_PAIR"])
    assert empty.empty
    assert "instrument" in empty.columns
    assert "campaign_name" in empty.columns


# ---------------------------------------------------------------------------
# Event fixture JSON (CAMPAIGN_014)
# ---------------------------------------------------------------------------


def test_load_event_fixture_json_committed_real_fixture() -> None:
    events = load_event_fixture_json(EVENT_FIXTURE_PATH)
    # Committed fixture has 281 events across NFP/FOMC/ECB/BoJ/BoE.
    assert events.event_count == 281
    assert events.classes == ("BoE", "BoJ", "ECB", "FOMC", "NFP")
    assert "event_class" in events.frame.columns
    assert "event_id" in events.frame.columns
    assert str(events.frame.index.tz) == "UTC"
    assert len(events.source_sha256) == 64


def test_load_event_fixture_json_missing(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="event fixture JSON not found"):
        load_event_fixture_json(tmp_path / "no_such.json")


def test_load_event_fixture_json_rejects_empty_events(tmp_path: Path) -> None:
    p = tmp_path / "empty.json"
    p.write_text(json.dumps({"schema_version": "x", "events": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="empty events array"):
        load_event_fixture_json(p)


def test_load_event_fixture_json_rejects_bad_schema(tmp_path: Path) -> None:
    p = tmp_path / "bad.json"
    p.write_text(json.dumps({"events": [{"foo": "bar"}]}), encoding="utf-8")
    with pytest.raises(ValueError, match="missing required keys"):
        load_event_fixture_json(p)


# ---------------------------------------------------------------------------
# H4 SQLite store
# ---------------------------------------------------------------------------


def _build_fake_h4_db(path: Path) -> None:
    """Build a tiny H4 candles SQLite store with the same schema the
    real ``campaign_002.sqlite3`` uses. ~5 rows per pair, EUR_USD only,
    for a unit test."""
    with sqlite3.connect(path) as conn:
        conn.execute(
            "CREATE TABLE candles ("
            "instrument TEXT, granularity TEXT, time TEXT, complete INTEGER, "
            "volume INTEGER, price_components TEXT, "
            "bid_o TEXT, bid_h TEXT, bid_l TEXT, bid_c TEXT, "
            "ask_o TEXT, ask_h TEXT, ask_l TEXT, ask_c TEXT, "
            "mid_o TEXT, mid_h TEXT, mid_l TEXT, mid_c TEXT, "
            "source TEXT, request_hash TEXT, inserted_at TEXT)"
        )
        rows = [
            ("EUR_USD", "H4", "2024-01-02T22:00:00+00:00", 1, 100, "BA",
             "1.1000", "1.1010", "1.0995", "1.1005",
             "1.1002", "1.1012", "1.0997", "1.1007",
             None, None, None, None, "fake", None, "2024-01-02"),
            ("EUR_USD", "H4", "2024-01-03T02:00:00+00:00", 1, 100, "BA",
             "1.1005", "1.1020", "1.1000", "1.1015",
             "1.1007", "1.1022", "1.1002", "1.1017",
             None, None, None, None, "fake", None, "2024-01-03"),
            ("EUR_USD", "H4", "2024-01-03T06:00:00+00:00", 1, 100, "BA",
             "1.1015", "1.1025", "1.1010", "1.1020",
             "1.1017", "1.1027", "1.1012", "1.1022",
             None, None, None, None, "fake", None, "2024-01-03"),
            # incomplete bar - must be excluded
            ("EUR_USD", "H4", "2024-01-03T10:00:00+00:00", 0, 50, "BA",
             "1.1020", "1.1030", "1.1015", "1.1025",
             "1.1022", "1.1032", "1.1017", "1.1027",
             None, None, None, None, "fake", None, "2024-01-03"),
            # wrong granularity - must be excluded
            ("EUR_USD", "D", "2024-01-02T22:00:00+00:00", 1, 100, "BA",
             "1.1000", "1.1010", "1.0995", "1.1005",
             "1.1002", "1.1012", "1.0997", "1.1007",
             None, None, None, None, "fake", None, "2024-01-02"),
        ]
        conn.executemany(
            "INSERT INTO candles VALUES (" + ",".join(["?"] * 21) + ")", rows
        )


def test_load_h4_candles_from_sqlite_fake_db(tmp_path: Path) -> None:
    db = tmp_path / "fake.sqlite3"
    _build_fake_h4_db(db)
    sample = load_h4_candles_from_sqlite(db, "EUR_USD")
    # 3 complete H4 rows for EUR_USD (incomplete and D rows excluded).
    assert sample.row_count == 3
    assert sample.instrument == "EUR_USD"
    assert sample.granularity == "H4"
    assert "close" in sample.frame.columns
    assert str(sample.frame.index.tz) == "UTC"
    # Mid is the bid/ask average; check first row.
    first = sample.frame.iloc[0]
    assert first["close"] == pytest.approx((1.1005 + 1.1007) / 2.0)


def test_load_h4_candles_from_sqlite_date_range_filter(tmp_path: Path) -> None:
    db = tmp_path / "fake.sqlite3"
    _build_fake_h4_db(db)
    sample = load_h4_candles_from_sqlite(
        db, "EUR_USD",
        from_time="2024-01-03T00:00:00+00:00",
        to_time="2024-01-03T05:00:00+00:00",
    )
    assert sample.row_count == 1  # only the 02:00 row


def test_load_h4_candles_from_sqlite_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="H4 SQLite store not found"):
        load_h4_candles_from_sqlite(tmp_path / "no_such.sqlite3", "EUR_USD")


def test_load_h4_candles_from_sqlite_zero_rows(tmp_path: Path) -> None:
    db = tmp_path / "fake.sqlite3"
    _build_fake_h4_db(db)
    with pytest.raises(ValueError, match="zero completed H4 rows"):
        load_h4_candles_from_sqlite(db, "USD_JPY")


def test_resolve_h4_store_path_env_var_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    db = tmp_path / "env.sqlite3"
    db.write_bytes(b"")  # existence is all that matters
    monkeypatch.setenv(EDGE_DISCOVERY_H4_DB_ENV, str(db))
    resolved = resolve_h4_store_path(tmp_path)
    assert resolved == db


def test_resolve_h4_store_path_repo_root_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(EDGE_DISCOVERY_H4_DB_ENV, raising=False)
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db = data_dir / "campaign_002.sqlite3"
    db.write_bytes(b"")
    resolved = resolve_h4_store_path(tmp_path)
    assert resolved == db


def test_resolve_h4_store_path_returns_none_when_absent(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(EDGE_DISCOVERY_H4_DB_ENV, raising=False)
    # tmp_path has no data/ dir, no parent .claude/worktrees ancestry.
    assert resolve_h4_store_path(tmp_path) is None


def test_resolve_h4_store_path_worktree_fallback(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Simulate the worktree layout
    ``<root>/.claude/worktrees/<name>/`` and check that the loader
    finds the canonical data dir at ``<root>/data/``."""
    monkeypatch.delenv(EDGE_DISCOVERY_H4_DB_ENV, raising=False)
    root = tmp_path / "myrepo"
    worktree = root / ".claude" / "worktrees" / "branch_a"
    worktree.mkdir(parents=True)
    (root / "data").mkdir()
    db = root / "data" / "campaign_002.sqlite3"
    db.write_bytes(b"")
    resolved = resolve_h4_store_path(worktree)
    assert resolved == db


@pytest.mark.skipif(
    resolve_h4_store_path(REPO_ROOT) is None,
    reason="real H4 SQLite store not present on this machine — expected on a fresh clone",
)
def test_real_h4_store_has_seven_majors_when_present() -> None:
    """Smoke test against the real operator-local H4 store. Skipped
    when the store is absent; this protects fresh-clone CI."""
    db = resolve_h4_store_path(REPO_ROOT)
    assert db is not None
    for pair in SEVEN_MAJORS:
        sample = load_h4_candles_from_sqlite(db, pair)
        # Each major has ~9,931+ H4 bars covering 2020-2026.
        assert sample.row_count > 9_000, f"{pair} has only {sample.row_count} H4 rows"
        assert sample.granularity == "H4"


# ---------------------------------------------------------------------------
# Provenance dataclasses
# ---------------------------------------------------------------------------


def test_study_provenance_roundtrip() -> None:
    p = StudyProvenance(
        data_kind="real",
        inputs=[StudyInput(kind="event_fixture_json", path="x.json", sha256="a" * 64, rows=10)],
        date_coverage={"start_utc": "2020-01-01T00:00:00+00:00", "end_utc": "2026-05-20T00:00:00+00:00"},
        pair_universe=["EUR_USD", "USD_JPY"],
        limitations=["CPI absent from committed fixture"],
        exploratory_only=True,
    )
    d = p.to_dict()
    assert d["data_kind"] == "real"
    assert d["inputs"][0]["kind"] == "event_fixture_json"
    assert d["exploratory_only"] is True
    assert_real_data_kind(p)


def test_assert_real_data_kind_rejects_real_with_empty_inputs() -> None:
    p = StudyProvenance(
        data_kind="real",
        inputs=[],
        date_coverage={},
        pair_universe=[],
        limitations=[],
        exploratory_only=True,
    )
    with pytest.raises(ValueError, match="claims data_kind='real' but no inputs"):
        assert_real_data_kind(p)


def test_assert_real_data_kind_rejects_non_exploratory() -> None:
    p = StudyProvenance(
        data_kind="real",
        inputs=[StudyInput(kind="x", path="x", sha256="x", rows=1)],
        date_coverage={},
        pair_universe=[],
        limitations=[],
        exploratory_only=False,
    )
    with pytest.raises(ValueError, match="exploratory_only=True"):
        assert_real_data_kind(p)


def test_synthetic_fallback_data_kind_allowed() -> None:
    """The synthetic-fallback path is legal — no inputs required."""
    p = StudyProvenance(
        data_kind="synthetic-fallback",
        inputs=[],
        date_coverage={"start_utc": "x", "end_utc": "y"},
        pair_universe=["EUR_USD"],
        limitations=["real H4 store absent — fell back to synthetic fixture"],
        exploratory_only=True,
    )
    assert_real_data_kind(p)
