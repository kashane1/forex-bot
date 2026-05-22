#!/usr/bin/env python3
"""Rehydrate / verify a local real OANDA practice H4 candle store.

Builds a reproducible local SQLite store of **real OANDA practice** H4
bid/ask candles for the six major pairs, 2020-01-01 .. 2026-05-20, with
full provenance (source label, host, window, counts, and raw +
normalized SHA-256 hashes recorded in `data_sources`).

Safety:
  * **Practice only.** The practice-data environment guard must pass;
    a live environment, an ambiguous one, or missing credentials all
    abort the fetch.
  * **No synthetic fallback.** If a fetch cannot run, the script stops
    and reports — it never fabricates candles.
  * **No credential leakage.** Account ids and tokens are never printed.
  * The SQLite store lives under `data/` (gitignored) and is **not**
    committed.

Modes:
  * default — fetch/upsert all six pairs (idempotent: re-running tops up);
  * --verify — read-only: summarize an existing store, no OANDA call,
    no credentials needed.

Usage:
    python scripts/rehydrate_oanda_h4_store.py [--config configs/paper.yaml]
    python scripts/rehydrate_oanda_h4_store.py --verify

See docs/research/OANDA_H4_DATA_REHYDRATION.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.broker.oanda import OandaBroker
from forex_bot.config import ConfigError, Settings, load_settings
from forex_bot.data.db import Database
from forex_bot.data.repositories import CandleRepo, DataSourceRecord, DataSourceRepo
from forex_bot.domain.candles import Candle, CandleRequest
from forex_bot.guards import assert_practice_data_environment

H4_PAIRS = ["EUR_USD", "GBP_USD", "USD_JPY", "AUD_USD", "USD_CAD", "USD_CHF"]
WINDOW_FROM = "2020-01-01"
WINDOW_TO = "2026-05-20"
DEFAULT_DB = ROOT / "data" / "oanda_h4_research.sqlite3"
DEFAULT_CONFIG = ROOT / "configs" / "paper.yaml"
CAMPAIGN_TAG = "h4_research_rehydration"
_PAGE_SIZE = 2500


# --------------------------------------------------------------------------
# Hashing
# --------------------------------------------------------------------------


def _normalized_row(c: Candle) -> str:
    """The deterministic, normalized string form of one candle."""
    return "|".join(
        str(x)
        for x in (
            c.instrument, c.granularity, c.time.isoformat(),
            c.bid_o, c.bid_h, c.bid_l, c.bid_c,
            c.ask_o, c.ask_h, c.ask_l, c.ask_c, c.volume,
        )
    )


def normalized_candle_hash(candles: list[Candle]) -> str:
    """SHA-256 over the normalized candle rows (time-sorted) — a stable
    content hash independent of fetch order."""
    hasher = hashlib.sha256()
    for c in sorted(candles, key=lambda x: x.time):
        hasher.update(_normalized_row(c).encode("utf-8"))
    return hasher.hexdigest()


# --------------------------------------------------------------------------
# Store verification (read-only, no credentials)
# --------------------------------------------------------------------------


def store_manifest(db: Database, pairs: list[str]) -> dict:
    """Summarize a local H4 store: per-pair candle counts, coverage, and
    the recorded provenance. Read-only — no OANDA call."""
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    pair_info: dict[str, dict] = {}
    for pair in pairs:
        candles = candle_repo.list(pair, "H4", completed_only=True)
        provenance = ds_repo.latest_for(pair, "H4")
        pair_info[pair] = {
            "candle_count": len(candles),
            "first_ts": candles[0].time.isoformat() if candles else None,
            "last_ts": candles[-1].time.isoformat() if candles else None,
            "content_hash": normalized_candle_hash(candles) if candles else None,
            "source": provenance["source"] if provenance else None,
            "raw_sha256": provenance["raw_sha256"] if provenance else None,
            "normalized_sha256": provenance["normalized_sha256"] if provenance else None,
        }
    sources = {
        info["source"] for info in pair_info.values() if info["source"]
    }
    return {
        "store": "h4_research",
        "pairs": pair_info,
        "total_candles": sum(p["candle_count"] for p in pair_info.values()),
        "distinct_sources": sorted(sources),
        "all_real_oanda": bool(sources) and all(s.startswith("oanda") for s in sources),
    }


# --------------------------------------------------------------------------
# Fetch (real OANDA practice only)
# --------------------------------------------------------------------------


def _parse_day(value: str) -> datetime:
    return datetime.fromisoformat(value).replace(tzinfo=UTC)


def fetch_pair(
    broker: OandaBroker,
    candle_repo: CandleRepo,
    *,
    instrument: str,
    price: str,
    from_dt: datetime,
    to_dt: datetime,
    daily_alignment: int,
    alignment_tz: str,
    weekly_alignment: str,
    host: str,
    account_redacted: str,
) -> DataSourceRecord:
    """Paginated H4 fetch for one pair. Mirrors the proven `fetch-candles`
    pagination: forward by `from`, clip to `to`, completed candles only."""
    raw_hasher = hashlib.sha256()
    kept_all: list[Candle] = []
    pages = 0
    written = 0
    dropped = 0
    cursor = from_dt
    while cursor < to_dt:
        request = CandleRequest(
            instrument=instrument,
            granularity="H4",
            price=price,  # type: ignore[arg-type]
            count=_PAGE_SIZE,
            from_time=cursor,
            to_time=None,
            daily_alignment=daily_alignment,
            alignment_timezone=alignment_tz,
            weekly_alignment=weekly_alignment,
            include_first=True,
        )
        candles, raw = broker.get_candles_with_raw(request)
        if not candles:
            break
        in_window = [c for c in candles if c.time <= to_dt]
        kept = [c for c in in_window if c.complete]
        dropped += len(in_window) - len(kept)
        if kept:
            raw_hasher.update(raw)
            kept_all.extend(kept)
            written += candle_repo.upsert_many(
                kept,
                source="oanda-practice",
                price_components=price,
                request_hash=hashlib.sha1(raw).hexdigest()[:16],
            )
        pages += 1
        last_in_window = in_window[-1].time if in_window else cursor
        last_received = candles[-1].time
        if last_received <= cursor:
            break
        cursor = last_received + timedelta(seconds=1)
        if last_in_window >= to_dt:
            break

    return DataSourceRecord(
        instrument=instrument,
        granularity="H4",
        source="oanda-practice",
        host=host,
        from_time=from_dt.isoformat(),
        to_time=to_dt.isoformat(),
        price_components=price,
        page_count=pages,
        candles_written=written,
        candles_dropped_incomplete=dropped,
        first_ts=kept_all[0].time.isoformat() if kept_all else None,
        last_ts=kept_all[-1].time.isoformat() if kept_all else None,
        raw_sha256=raw_hasher.hexdigest() if pages else None,
        normalized_sha256=normalized_candle_hash(kept_all) if kept_all else None,
        request_params_json=json.dumps(
            {"instrument": instrument, "granularity": "H4", "price": price,
             "from": from_dt.isoformat(), "to": to_dt.isoformat()},
            sort_keys=True,
        ),
        broker_account_id_redacted=account_redacted,
        campaign=CAMPAIGN_TAG,
    )


def rehydrate(settings: Settings, db: Database, *, from_dt: datetime, to_dt: datetime) -> dict:
    """Fetch all six majors into the store. Requires a verified practice
    environment (the caller must have run the env guard)."""
    guard = assert_practice_data_environment(settings)
    broker = OandaBroker(
        environment="practice",
        account_id=settings.broker_credentials()[0],
        access_token=settings.broker_credentials()[1],
        timeout_seconds=settings.broker.request_timeout_seconds,
        max_retries=settings.broker.max_retries,
    )
    candle_repo = CandleRepo(db)
    ds_repo = DataSourceRepo(db)
    host = "https://api-fxpractice.oanda.com"
    results: dict[str, dict] = {}
    try:
        for pair in H4_PAIRS:
            record = fetch_pair(
                broker, candle_repo,
                instrument=pair,
                price=settings.market.candle_price_components,
                from_dt=from_dt, to_dt=to_dt,
                daily_alignment=settings.market.daily_alignment,
                alignment_tz=settings.market.alignment_timezone,
                weekly_alignment=settings.market.weekly_alignment,
                host=host,
                account_redacted=guard.account_id_redacted,
            )
            ds_repo.insert(record)
            results[pair] = {
                "candles_written": record.candles_written,
                "dropped_incomplete": record.candles_dropped_incomplete,
                "pages": record.page_count,
                "raw_sha256": record.raw_sha256,
                "normalized_sha256": record.normalized_sha256,
            }
            print(
                f"  {pair}: {record.candles_written} H4 candles, "
                f"{record.page_count} pages, normalized_sha256="
                f"{(record.normalized_sha256 or '')[:16]}…"
            )
    finally:
        broker.close()
    return results


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def _print_manifest(manifest: dict) -> None:
    print(f"H4 research store — {manifest['total_candles']} candles total")
    print(f"  sources: {manifest['distinct_sources']} "
          f"(all real OANDA: {manifest['all_real_oanda']})")
    for pair, info in manifest["pairs"].items():
        print(
            f"  {pair}: {info['candle_count']} candles "
            f"[{info['first_ts']} .. {info['last_ts']}] "
            f"content_hash={(info['content_hash'] or 'n/a')[:16]}…"
        )


def main() -> int:
    ap = argparse.ArgumentParser(description="Rehydrate/verify the OANDA H4 store.")
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--from", dest="from_date", default=WINDOW_FROM)
    ap.add_argument("--to", dest="to_date", default=WINDOW_TO)
    ap.add_argument(
        "--verify", action="store_true",
        help="read-only: summarize an existing store, no OANDA call",
    )
    args = ap.parse_args()
    db_path = Path(args.db)
    try:
        db_display = str(db_path.resolve().relative_to(ROOT))
    except ValueError:
        db_display = str(db_path)

    if args.verify:
        if not db_path.exists():
            print(
                f"BLOCKER: no H4 store at {db_display}. Run a rehydration "
                "fetch first (requires OANDA practice credentials).",
                file=sys.stderr,
            )
            return 1
        manifest = store_manifest(Database(db_path), H4_PAIRS)
        _print_manifest(manifest)
        if not manifest["all_real_oanda"]:
            print(
                "BLOCKER: store contains non-OANDA (synthetic?) sources — "
                "refusing to treat it as a real-data store.",
                file=sys.stderr,
            )
            return 2
        return 0

    # Fetch mode — requires real OANDA practice credentials.
    try:
        settings = load_settings(Path(args.config))
        assert_practice_data_environment(settings)
    except ConfigError as exc:
        print(
            "BLOCKER: cannot fetch — the practice-data environment guard "
            f"refused: {exc}\n"
            "Provide OANDA *practice* credentials (OANDA_ACCOUNT_ID_PRACTICE / "
            "OANDA_ACCESS_TOKEN_PRACTICE) and retry. This script never falls "
            "back to synthetic data.",
            file=sys.stderr,
        )
        return 2

    print(f"rehydrating H4 store → {db_display} (practice OANDA, six majors)")
    db = Database(db_path)
    rehydrate(
        settings, db,
        from_dt=_parse_day(args.from_date), to_dt=_parse_day(args.to_date),
    )
    print()
    _print_manifest(store_manifest(db, H4_PAIRS))
    print(f"\n[store written] {db_display}  (gitignored — not committed)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
