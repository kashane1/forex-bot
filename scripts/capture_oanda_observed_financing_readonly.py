#!/usr/bin/env python3
"""Read-only OANDA practice financing capture (dry-run by default).

No order/trade/position mutation. No live environment. Credentials never logged.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

import httpx
from research.financing.observed import (
    hash_account_id,
    parse_transactions_batch,
    redact_transaction_id,
)

from forex_bot.research.oanda_readonly import (
    PRACTICE_REST_HOST,
    assert_no_token_in_log_line,
    assert_readonly_get_url,
    safe_log_url,
)
from forex_bot.research.observed_financing_fixture import (
    ObservedFinancingEntry,
    ObservedFinancingFixture,
    classify_transaction_type,
    effective_date_from_time,
    empty_observed_fixture,
    validate_observed_fixture,
)

TOOL = "capture_oanda_observed_financing_readonly"
DEFAULT_FIXTURE_OUT = ROOT / "research/observed_financing_capture_readonly/observed_practice_financing.json"
DEFAULT_OUTPUT_DIR = ROOT / "research/financing/observed"
RAW_DIR = DEFAULT_OUTPUT_DIR / "raw"

PRACTICE_TOKEN_ENV = "OANDA_ACCESS_TOKEN_PRACTICE"
PRACTICE_ACCOUNT_ENV = "OANDA_ACCOUNT_ID_PRACTICE"


def _credential_status() -> dict[str, bool]:
    env = os.environ.get("OANDA_ENVIRONMENT", os.environ.get("OANDA_ENV", "")).lower()
    return {
        "account_id_present": bool(os.environ.get(PRACTICE_ACCOUNT_ENV, "").strip()),
        "access_token_present": bool(os.environ.get(PRACTICE_TOKEN_ENV, "").strip()),
        "environment_is_practice": env in {"", "practice", "demo"},
    }


def _make_client(token: str) -> httpx.Client:
    return httpx.Client(
        timeout=30.0,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Datetime-Format": "RFC3339",
        },
    )


def _safe_get(
    client: httpx.Client,
    url: str,
    account_id: str,
    *,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    assert_readonly_get_url(url, account_id)
    log_line = f"GET {safe_log_url(url)}"
    assert_no_token_in_log_line(log_line)
    response = client.get(url, params=params)
    if response.status_code in {401, 403}:
        raise RuntimeError(f"auth failed: {response.status_code}")
    if response.status_code >= 400:
        raise RuntimeError(f"http {response.status_code}")
    return response.json()


def _fetch_transactions(
    client: httpx.Client,
    account_id: str,
    from_iso: str,
    to_iso: str,
    *,
    max_transactions: int,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/transactions"
    params = {"from": from_iso, "to": to_iso}
    payload = _safe_get(client, url, account_id, params=params)
    txs = list(payload.get("transactions") or [])[:max_transactions]
    types = Counter(str(t.get("type", "UNKNOWN")) for t in txs)
    return txs, types


def _entries_from_transactions(
    transactions: list[dict[str, Any]],
    *,
    account_currency: str,
) -> tuple[list[ObservedFinancingEntry], Counter[str]]:
    _parsed, events = parse_transactions_batch(transactions)
    entries: list[ObservedFinancingEntry] = []
    type_counter: Counter[str] = Counter()
    for raw in transactions:
        raw_type = str(raw.get("type", "UNKNOWN"))
        type_counter[raw_type] += 1
        if classify_transaction_type(raw_type) != "financing":
            continue
    for i, ev in enumerate(events):
        entries.append(
            ObservedFinancingEntry(
                local_id=f"obs_{i:05d}",
                transaction_id_hash=ev.transaction_id_redacted.replace("tx_", "txh_"),
                instrument=ev.instrument,
                side=None,
                units=ev.units,
                financing_home=ev.financing,
                account_currency=account_currency,
                transaction_time=ev.time,
                effective_date=effective_date_from_time(ev.time),
                transaction_type="DAILY_FINANCING",
                raw_type="DAILY_FINANCING",
            )
        )
    return entries, type_counter


def build_fixture(
    *,
    account_id_hash: str,
    account_currency: str,
    capture_window: dict[str, str],
    transactions: list[dict[str, Any]],
    type_counter: Counter[str],
) -> ObservedFinancingFixture:
    entries, _ = _entries_from_transactions(transactions, account_currency=account_currency)
    financing_n = sum(1 for t in transactions if classify_transaction_type(str(t.get("type"))) == "financing")
    unknown_n = sum(
        1 for t in transactions if classify_transaction_type(str(t.get("type"))) == "unknown"
    )
    fixture = ObservedFinancingFixture(
        captured_at_utc=datetime.now(UTC).isoformat(),
        account_id_hash=account_id_hash,
        capture_window=capture_window,
        account_currency=account_currency,
        entries=entries,
        transaction_counts={
            "total": len(transactions),
            "financing": financing_n,
            "unknown": unknown_n,
        },
    )
    validate_observed_fixture(fixture.model_dump())
    return fixture


def write_status(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "capture_status.json").write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def run(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start-date", type=str, default=None)
    parser.add_argument("--end-date", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--fixture-out", type=Path, default=DEFAULT_FIXTURE_OUT)
    parser.add_argument("--dry-run", action="store_true", help="Force no network")
    parser.add_argument("--execute-readonly-capture", action="store_true")
    parser.add_argument("--max-transactions", type=int, default=500)
    args = parser.parse_args(argv)
    dry_run = args.dry_run or not args.execute_readonly_capture

    cred = _credential_status()
    base_status = {
        "tool": TOOL,
        "strategy_evidence": False,
        "not_approved": True,
        "credential_status": cred,
    }

    if not cred["environment_is_practice"]:
        write_status(
            args.output_dir,
            {**base_status, "blocker": "BLOCKED_PRACTICE_ENV_NOT_CONFIRMED"},
        )
        print(f"[{TOOL}] BLOCKED_PRACTICE_ENV_NOT_CONFIRMED", file=sys.stderr)
        return 3

    if not args.start_date or not args.end_date:
        if dry_run:
            end = date.today()
            start = end - timedelta(days=14)
            from_iso = datetime.combine(start, datetime.min.time(), tzinfo=UTC).isoformat().replace(
                "+00:00", "Z"
            )
            to_iso = datetime.combine(end, datetime.max.time(), tzinfo=UTC).isoformat().replace(
                "+00:00", "Z"
            )
        else:
            write_status(args.output_dir, {**base_status, "blocker": "BLOCKED_NO_DATE_BOUNDS"})
            print(f"[{TOOL}] BLOCKED_NO_DATE_BOUNDS", file=sys.stderr)
            return 4
    else:
        from_iso = f"{args.start_date}T00:00:00Z"
        to_iso = f"{args.end_date}T23:59:59Z"

    capture_window = {"from": from_iso, "to": to_iso}

    if dry_run:
        write_status(
            args.output_dir,
            {
                **base_status,
                "status": "DRY_RUN_OK",
                "capture_window": capture_window,
                "network_called": False,
                "credentials_required_for_execute": True,
            },
        )
        print(f"[{TOOL}] dry-run OK (no network)")
        return 0

    if not cred["access_token_present"] or not cred["account_id_present"]:
        write_status(
            args.output_dir,
            {**base_status, "blocker": "BLOCKED_READONLY_CREDENTIALS"},
        )
        print(f"[{TOOL}] BLOCKED_READONLY_CREDENTIALS", file=sys.stderr)
        return 2

    token = os.environ[PRACTICE_TOKEN_ENV]
    account_id = os.environ[PRACTICE_ACCOUNT_ENV]
    account_id_hash = hash_account_id(account_id)

    client = _make_client(token)
    account_url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    account_payload = _safe_get(client, account_url, account_id)
    tags = (account_payload.get("account") or {}).get("tags") or []
    if not any(str(t).upper() == "PRACTICE" for t in tags):
        write_status(
            args.output_dir,
            {**base_status, "blocker": "BLOCKED_PRACTICE_ENV_NOT_CONFIRMED"},
        )
        return 3

    account_currency = (account_payload.get("account") or {}).get("currency", "USD")

    try:
        transactions, type_counter = _fetch_transactions(
            client,
            account_id,
            from_iso,
            to_iso,
            max_transactions=args.max_transactions,
        )
    except RuntimeError as exc:
        write_status(
            args.output_dir,
            {**base_status, "status": "ERROR", "error": str(exc)},
        )
        return 5

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    raw_path = RAW_DIR / "transactions_raw_local.json"
    sanitized_raw = [
        {**{k: v for k, v in t.items() if k not in {"accountID", "userID", "requestID"}}, "id": redact_transaction_id(str(t.get("id", "")))}
        for t in transactions
    ]
    raw_path.write_text(json.dumps(sanitized_raw, indent=2) + "\n", encoding="utf-8")

    if not any(classify_transaction_type(str(t.get("type"))) == "financing" for t in transactions):
        fixture = empty_observed_fixture(
            account_id_hash=account_id_hash,
            captured_at_utc=datetime.now(UTC).isoformat(),
            capture_window=capture_window,
            account_currency=account_currency,
        )
        args.fixture_out.parent.mkdir(parents=True, exist_ok=True)
        args.fixture_out.write_text(
            json.dumps(fixture.model_dump(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        write_status(
            args.output_dir,
            {
                **base_status,
                "status": "OBSERVED_FINANCING_EMPTY",
                "capture_window": capture_window,
                "transaction_count": len(transactions),
                "financing_transaction_count": 0,
                "unknown_transaction_type_count": sum(
                    1
                    for t in transactions
                    if classify_transaction_type(str(t.get("type"))) == "unknown"
                ),
                "fixture_path": str(args.fixture_out.relative_to(ROOT)),
                "raw_local_path": str(raw_path.relative_to(ROOT)),
            },
        )
        print(f"[{TOOL}] OBSERVED_FINANCING_EMPTY transactions={len(transactions)}")
        return 0

    fixture = build_fixture(
        account_id_hash=account_id_hash,
        account_currency=account_currency,
        capture_window=capture_window,
        transactions=transactions,
        type_counter=type_counter,
    )
    args.fixture_out.parent.mkdir(parents=True, exist_ok=True)
    args.fixture_out.write_text(
        json.dumps(fixture.model_dump(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    write_status(
        args.output_dir,
        {
            **base_status,
            "status": "OBSERVED_FINANCING_CAPTURED",
            "capture_window": capture_window,
            "transaction_count": len(transactions),
            "financing_transaction_count": fixture.transaction_counts.get("financing", 0),
            "unknown_transaction_type_count": fixture.transaction_counts.get("unknown", 0),
            "fixture_path": str(args.fixture_out.relative_to(ROOT)),
            "raw_local_path": str(raw_path.relative_to(ROOT)),
        },
    )
    print(
        f"[{TOOL}] captured financing={fixture.transaction_counts.get('financing', 0)} "
        f"entries={len(fixture.entries)}"
    )
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
