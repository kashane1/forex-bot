#!/usr/bin/env python3
"""Read-only OANDA practice DAILY_FINANCING capture.

Practice environment only. GET transaction endpoints only.
No order/trade/position mutation. Credentials never printed.

See docs/research/OBSERVED_FINANCING_CAPTURE_READONLY_001_PLAN.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import httpx
from research.financing.observed import (
    hash_account_id,
    parse_transactions_batch,
    sanitize_identifier_fields,
)

TOOL_NAME = "capture_observed_financing_readonly"
TOOL_VERSION = "1"

PRACTICE_REST_HOST = "https://api-fxpractice.oanda.com"
LIVE_HOST_MARKER = "api-fxtrade.oanda.com"

PRACTICE_TOKEN_ENV = "OANDA_ACCESS_TOKEN_PRACTICE"
PRACTICE_ACCOUNT_ENV = "OANDA_ACCOUNT_ID_PRACTICE"

DEFAULT_OUT = Path("research/financing/observed")
RAW_OUT = Path("research/financing/observed/raw")

ALLOWED_PATH_SUFFIXES = (
    "",
    "/summary",
    "/transactions",
    "/transactions/sinceid",
    "/transactions/idrange",
)

DENYLIST_PATH_FRAGMENTS = (
    "/orders",
    "/trades/",
    "/positions/",
    "/openTrades",
    "/openPositions",
    "/pendingOrders",
    "/transactions/stream",
    "/configure",
    "/funding",
)

EXIT_OK = 0
EXIT_MISSING_CREDS = 2
EXIT_NOT_PRACTICE = 3
EXIT_IO = 4
EXIT_HTTP = 5
EXIT_RUNTIME = 6
EXIT_FORBIDDEN = 7


class _SupportsRequest(Protocol):
    def get(self, url: str, **kwargs: Any) -> httpx.Response: ...


def _read_practice_creds() -> tuple[str | None, str | None]:
    token = os.environ.get(PRACTICE_TOKEN_ENV)
    account_id = os.environ.get(PRACTICE_ACCOUNT_ENV)
    return token, account_id


def _credential_status() -> dict[str, bool]:
    env = os.environ.get("OANDA_ENVIRONMENT", os.environ.get("OANDA_ENV", "")).lower()
    return {
        "account_id_present": bool(os.environ.get(PRACTICE_ACCOUNT_ENV, "").strip()),
        "access_token_present": bool(os.environ.get(PRACTICE_TOKEN_ENV, "").strip()),
        "environment_is_practice": env in {"", "practice", "demo"},
        "live_token_present": bool(os.environ.get("OANDA_ACCESS_TOKEN_LIVE", "").strip()),
    }


def _is_allowed_url(url: str, account_id: str) -> bool:
    if LIVE_HOST_MARKER in url:
        return False
    prefix = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    if not url.startswith(prefix):
        return False
    tail_path = url[len(prefix):].split("?", 1)[0]
    for frag in DENYLIST_PATH_FRAGMENTS:
        if frag in tail_path:
            return False
    if tail_path in ALLOWED_PATH_SUFFIXES:
        return True
    if tail_path.startswith("/transactions/") and tail_path.count("/") == 2:
        seg = tail_path.split("/")[-1]
        return seg.isdigit()
    return False


def _safe_get(
    client: _SupportsRequest,
    url: str,
    account_id: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if LIVE_HOST_MARKER in url:
        raise RuntimeError("refusing live-host URL")
    for frag in DENYLIST_PATH_FRAGMENTS:
        if frag in url:
            raise RuntimeError(f"refusing denylisted endpoint fragment: {frag}")
    if not _is_allowed_url(url, account_id):
        raise RuntimeError("refusing non-allowlisted URL")
    response = client.get(url, params=params)
    if response.status_code in {401, 403}:
        raise RuntimeError(f"auth failed: {response.status_code}")
    if response.status_code >= 400:
        raise RuntimeError(f"http {response.status_code}")
    return response.json()


def make_client(token: str, *, timeout_seconds: float = 30.0) -> httpx.Client:
    return httpx.Client(
        timeout=timeout_seconds,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Datetime-Format": "RFC3339",
        },
    )


def confirm_practice_account(
    client: _SupportsRequest,
    account_id: str,
    *,
    require_practice_tag: bool,
) -> dict[str, Any]:
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    payload = _safe_get(client, url, account_id)
    if require_practice_tag:
        tags = (payload.get("account") or {}).get("tags") or []
        if not any(str(t).upper() == "PRACTICE" for t in tags):
            raise RuntimeError("account is not tagged PRACTICE")
    return payload


def get_account_summary(client: _SupportsRequest, account_id: str) -> dict[str, Any]:
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/summary"
    return _safe_get(client, url, account_id)


def get_transactions_range(
    client: _SupportsRequest,
    account_id: str,
    from_iso: str,
    to_iso: str,
    *,
    tx_type: str | None = "DAILY_FINANCING",
) -> list[dict[str, Any]]:
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/transactions"
    params: dict[str, Any] = {"from": from_iso, "to": to_iso}
    if tx_type:
        params["type"] = tx_type
    payload = _safe_get(client, url, account_id, params=params)
    return list(payload.get("transactions") or [])


def default_date_range(days: int = 180) -> tuple[str, str]:
    to_dt = datetime.now(UTC)
    from_dt = to_dt - timedelta(days=days)
    return from_dt.isoformat().replace("+00:00", "Z"), to_dt.isoformat().replace("+00:00", "Z")


def build_status_payload(
    *,
    status: str,
    credential_status: dict[str, bool],
    **extra: Any,
) -> dict[str, Any]:
    return {
        "tool": TOOL_NAME,
        "tool_version": TOOL_VERSION,
        "strategy_evidence": False,
        "not_approved": True,
        "status": status,
        "credential_status": credential_status,
        **extra,
    }


def build_sanitized_output(
    *,
    account_id_hash: str,
    account_currency: str,
    from_iso: str,
    to_iso: str,
    transactions: list[dict[str, Any]],
    provenance: str,
) -> dict[str, Any]:
    parsed, events = parse_transactions_batch(transactions)
    sanitized_txs = [tx.model_dump() for tx in parsed]
    flat_events = [e.model_dump() for e in events]
    by_instrument: dict[str, float] = defaultdict(float)
    for ev in events:
        if ev.instrument:
            by_instrument[ev.instrument] += float(Decimal(ev.financing))
    return {
        "kind": "observed_financing_events",
        "schema_version": 1,
        "synthetic": False,
        "diagnostic_label": "OBSERVED_FINANCING_DIAGNOSTIC",
        "provenance": provenance,
        "account_currency": account_currency,
        "account_id_hash": account_id_hash,
        "capture_window": {"from": from_iso, "to": to_iso},
        "daily_financing_count": len(parsed),
        "event_count": len(flat_events),
        "financing_total_by_instrument": dict(by_instrument),
        "transactions": sanitized_txs,
        "events": flat_events,
    }


def write_outputs(
    out_dir: Path,
    *,
    status: dict[str, Any],
    sanitized: dict[str, Any] | None,
    manifest: dict[str, Any],
    raw_transactions: list[dict[str, Any]] | None = None,
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "observed_financing_capture_status.json").write_text(
        json.dumps(status, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    (out_dir / "observed_financing_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8",
    )
    if sanitized is not None:
        (out_dir / "observed_daily_financing_sanitized.json").write_text(
            json.dumps(sanitized, indent=2, sort_keys=True) + "\n", encoding="utf-8",
        )
    if raw_transactions is not None:
        raw_dir = out_dir / "raw"
        raw_dir.mkdir(parents=True, exist_ok=True)
        sanitized_raw = [sanitize_identifier_fields(tx) for tx in raw_transactions]
        (raw_dir / "transactions_raw_sanitized_ids.json").write_text(
            json.dumps(sanitized_raw, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def run(argv: list[str] | None = None, *, client_factory: Any = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--days", type=int, default=180)
    parser.add_argument("--from-iso", default=None)
    parser.add_argument("--to-iso", default=None)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--require-practice-tag", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args(argv)

    cred_status = _credential_status()
    token, account_id = _read_practice_creds()

    if not cred_status["environment_is_practice"]:
        status = build_status_payload(
            status="BLOCKED_NOT_PRACTICE_ENVIRONMENT",
            credential_status=cred_status,
        )
        try:
            write_outputs(args.output, status=status, sanitized=None, manifest={"blocked": True})
        except OSError:
            return EXIT_IO
        return EXIT_NOT_PRACTICE

    if not token or not account_id:
        status = build_status_payload(
            status="BLOCKED_CREDENTIALS_MISSING",
            credential_status=cred_status,
        )
        write_outputs(args.output, status=status, sanitized=None, manifest={"blocked": True})
        print(f"[{TOOL_NAME}] BLOCKED_CREDENTIALS_MISSING", file=sys.stderr)
        return EXIT_MISSING_CREDS

    if cred_status["live_token_present"]:
        # Informational only — we never read live token.
        pass

    from_iso, to_iso = (
        (args.from_iso, args.to_iso)
        if args.from_iso and args.to_iso
        else default_date_range(args.days)
    )

    factory = client_factory or make_client
    try:
        client = factory(token)
    except Exception:
        return EXIT_RUNTIME

    try:
        account_payload = confirm_practice_account(
            client, account_id, require_practice_tag=args.require_practice_tag,
        )
    except RuntimeError as exc:
        status = build_status_payload(
            status="BLOCKED_NOT_PRACTICE_ACCOUNT",
            credential_status=cred_status,
            error=str(exc),
        )
        write_outputs(args.output, status=status, sanitized=None, manifest={"blocked": True})
        return EXIT_NOT_PRACTICE

    account_currency = (account_payload.get("account") or {}).get("currency", "USD")
    account_id_hash = hash_account_id(account_id)
    provenance = f"oanda-practice-readonly-{datetime.now(UTC).date().isoformat()}"

    manifest = {
        "tool": TOOL_NAME,
        "endpoint_allowlist": list(ALLOWED_PATH_SUFFIXES),
        "endpoint_denylist_fragments": list(DENYLIST_PATH_FRAGMENTS),
        "host": PRACTICE_REST_HOST,
        "methods_allowed": ["GET"],
        "strategy_evidence": False,
        "capture_window": {"from": from_iso, "to": to_iso},
        "type_filter": "DAILY_FINANCING",
    }

    if args.dry_run:
        try:
            _ = get_account_summary(client, account_id)
        except RuntimeError:
            return EXIT_HTTP
        status = build_status_payload(
            status="DRY_RUN_OK",
            credential_status=cred_status,
            capture_window={"from": from_iso, "to": to_iso},
        )
        write_outputs(args.output, status=status, sanitized=None, manifest=manifest)
        print(f"[{TOOL_NAME}] dry-run OK")
        return EXIT_OK

    try:
        raw_all = get_transactions_range(
            client, account_id, from_iso, to_iso, tx_type="DAILY_FINANCING",
        )
        if not raw_all:
            raw_all = get_transactions_range(
                client, account_id, from_iso, to_iso, tx_type=None,
            )
            raw_all = [t for t in raw_all if t.get("type") == "DAILY_FINANCING"]
    except RuntimeError as exc:
        status = build_status_payload(
            status="ERROR",
            credential_status=cred_status,
            error=str(exc),
        )
        write_outputs(args.output, status=status, sanitized=None, manifest=manifest)
        return EXIT_HTTP

    daily_count = len(raw_all)
    if daily_count == 0:
        status = build_status_payload(
            status="OBSERVED_FINANCING_EMPTY",
            credential_status=cred_status,
            capture_window={"from": from_iso, "to": to_iso},
            transactions_fetched=0,
            daily_financing_count=0,
            likely_reasons=[
                "no overnight positions in capture window",
                "practice account has no DAILY_FINANCING history",
                "research freeze prevented order submission",
            ],
        )
        write_outputs(args.output, status=status, sanitized=None, manifest=manifest)
        print(f"[{TOOL_NAME}] OBSERVED_FINANCING_EMPTY")
        return EXIT_OK

    sanitized = build_sanitized_output(
        account_id_hash=account_id_hash,
        account_currency=account_currency,
        from_iso=from_iso,
        to_iso=to_iso,
        transactions=raw_all,
        provenance=provenance,
    )
    status = build_status_payload(
        status="OBSERVED_FINANCING_CAPTURED",
        credential_status=cred_status,
        capture_window={"from": from_iso, "to": to_iso},
        transactions_fetched=len(raw_all),
        daily_financing_count=daily_count,
        event_count=sanitized["event_count"],
        instruments=sorted(sanitized["financing_total_by_instrument"].keys()),
    )
    write_outputs(
        args.output,
        status=status,
        sanitized=sanitized,
        manifest=manifest,
        raw_transactions=raw_all,
    )
    print(
        f"[{TOOL_NAME}] captured {daily_count} DAILY_FINANCING transactions, "
        f"{sanitized['event_count']} events"
    )
    return EXIT_OK


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()
