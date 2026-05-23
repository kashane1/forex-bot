#!/usr/bin/env python3
"""Read-only OANDA practice pilot for capturing DAILY_FINANCING
transactions.

Authorized scope (per
docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md §3):

- read-only OANDA practice transaction history;
- one-shot capture, no daemon, no SQLite write;
- redacted fixture-shape JSON output under --output (default
  /tmp/...), never committed.

Defense in depth:

- practice REST host hard-coded
  (``https://api-fxpractice.oanda.com``);
- URL-prefix allowlist refuses anything else (including the
  live host ``api-fxtrade.oanda.com`` and any non-transaction
  endpoint);
- no ``POST`` / ``PUT`` / ``DELETE`` / ``PATCH`` method
  appears in this script;
- no ``submit_order`` / ``close_trade`` import;
- credentials read only from ``OANDA_ACCESS_TOKEN_PRACTICE`` /
  ``OANDA_ACCOUNT_ID_PRACTICE``; ``OANDA_*_LIVE`` are
  explicitly never read;
- raw account id is hashed at the boundary via SHA-256;
  the hash is what flows into the output;
- token value is never printed or logged.

Exit codes:

- 0  success
- 2  missing practice credentials (no values printed)
- 3  live env detected or PRACTICE tag missing
- 4  output I/O error
- 5  HTTP / parse failure (no credential value in message)
- 6  RuntimeError (defense-in-depth)

The script is intentionally self-contained:

- no imports from ``forex_bot``;
- only ``httpx``, ``argparse``, ``json``, ``os``, stdlib;
- no SQLite write;
- no network call inside tests (tests inject a mock HTTP
  client).

See docs/research/FINANCING_OBSERVED_CAPTURE_PILOT_001_PLAN.md
and docs/research/FINANCING_OBSERVED_CAPTURE_EXISTING_PATH_AUDIT.md.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Protocol

import httpx

TOOL_NAME = "capture_oanda_observed_financing_pilot"
TOOL_VERSION = "1"

PRACTICE_REST_HOST = "https://api-fxpractice.oanda.com"
# Defense: the script never touches the live host. The
# allowlist below rejects anything else, including any string
# containing "fxtrade".

PRACTICE_TOKEN_ENV = "OANDA_ACCESS_TOKEN_PRACTICE"
PRACTICE_ACCOUNT_ENV = "OANDA_ACCOUNT_ID_PRACTICE"
# OANDA_*_LIVE are explicitly NOT consulted. Tests pin this.

EXIT_OK = 0
EXIT_MISSING_CREDS = 2
EXIT_NOT_PRACTICE = 3
EXIT_IO = 4
EXIT_HTTP = 5
EXIT_RUNTIME = 6


class _SupportsRequest(Protocol):
    def get(self, url: str, **kwargs: Any) -> httpx.Response: ...


def hash_account_id_local(account_id: str) -> str:
    """SHA-256 hex of an account id. Mirrors
    ``forex_bot.domain.transactions.hash_account_id`` so the
    pilot stays import-isolated."""
    return hashlib.sha256(account_id.strip().encode("utf-8")).hexdigest()


def _is_allowed_url(url: str, account_id: str) -> bool:
    """URL-prefix allowlist. Returns True iff the URL is a
    read-only practice transaction endpoint for this
    account."""
    prefix = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    allowed_paths = (
        "",  # GET /v3/accounts/{accountID}
        "/summary",
        "/transactions",
        "/transactions/sinceid",
    )
    # Explicit by-id path is conservative; we accept it via
    # startswith check below.
    if not url.startswith(prefix):
        return False
    tail = url[len(prefix):]
    # Strip query string for the comparison.
    tail_path = tail.split("?", 1)[0]
    if tail_path in allowed_paths:
        return True
    # Allow /transactions/{id} (single-transaction lookup). OANDA
    # transaction ids are integer strings; this also implicitly
    # rejects /transactions/stream (which is a denylisted
    # streaming endpoint).
    if not tail_path.startswith("/transactions/"):
        return False
    id_segment = tail_path[len("/transactions/"):]
    return id_segment.isdigit()


def _safe_get(
    client: _SupportsRequest,
    url: str,
    account_id: str,
    params: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """A defensive HTTP GET wrapper. Refuses URLs outside the
    allowlist; refuses any URL containing the live host
    substrings; surfaces 4xx/5xx with non-credential
    messages."""
    if "fxtrade" in url:
        raise RuntimeError("refusing live-host URL")
    if not _is_allowed_url(url, account_id):
        raise RuntimeError(f"refusing non-allowlisted URL: {url}")
    response = client.get(url, params=params)
    if response.status_code in {401, 403}:
        # Body may include the account id but never the token;
        # we still strip the body for safety.
        raise RuntimeError(f"auth failed: {response.status_code}")
    if response.status_code >= 400:
        raise RuntimeError(f"http {response.status_code} on {url}")
    try:
        return response.json()
    except Exception as exc:
        raise RuntimeError(f"non-JSON response from {url}: {exc}") from exc


def make_client(token: str, *, timeout_seconds: float = 10.0) -> httpx.Client:
    """Build an httpx.Client with the practice base URL and
    Bearer auth. Token is sent in the Authorization header;
    never logged."""
    return httpx.Client(
        timeout=timeout_seconds,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept-Datetime-Format": "RFC3339",
        },
    )


# ---------- Parsing helpers (mirrors src/forex_bot/broker/mapping.py) ----------


def _decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return None


def _parse_rfc3339(value: str) -> datetime:
    """OANDA RFC3339 uses "Z" or "+00:00"; Python's
    fromisoformat accepts both since 3.11."""
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def parse_daily_financing(
    payload: dict[str, Any],
    *,
    account_id_hash: str,
    account_currency: str,
) -> list[dict[str, Any]]:
    """Parse a DAILY_FINANCING payload into fixture-shape event
    dicts. Mirrors map_daily_financing in
    src/forex_bot/broker/mapping.py without importing it
    (import isolation)."""
    if payload.get("type") != "DAILY_FINANCING":
        return []
    tx_id = str(payload["id"])
    when = _parse_rfc3339(payload.get("time", "1970-01-01T00:00:00Z"))

    def _event(
        instrument: str | None, trade_id: str | None,
        units: Any, financing: Any,
    ) -> dict[str, Any]:
        units_dec = _decimal(units)
        fin_dec = _decimal(financing)
        return {
            "transaction_id": tx_id,
            "instrument": instrument,
            "trade_id": trade_id,
            "units": str(units_dec) if units_dec is not None else None,
            "financing": str(fin_dec if fin_dec is not None else Decimal("0")),
            "time": when.isoformat(),
        }

    events: list[dict[str, Any]] = []
    for pf in payload.get("positionFinancings") or []:
        instrument = pf.get("instrument")
        open_trade_financings = pf.get("openTradeFinancings") or []
        if open_trade_financings:
            for otf in open_trade_financings:
                trade_id = str(otf["tradeID"]) if otf.get("tradeID") else None
                events.append(_event(
                    instrument, trade_id,
                    otf.get("units"), otf.get("financing"),
                ))
        else:
            events.append(_event(instrument, None, None, pf.get("financing")))

    if not events:
        events.append(_event(None, None, None, payload.get("financing")))
    return events


def parse_observed_financing_events(
    payload: dict[str, Any],
    *,
    account_id_hash: str,
    account_currency: str,
) -> list[dict[str, Any]]:
    """Dispatcher: DAILY_FINANCING → per-instrument/per-trade;
    any other transaction with non-zero financing → one event;
    otherwise empty."""
    if payload.get("type") == "DAILY_FINANCING":
        return parse_daily_financing(
            payload,
            account_id_hash=account_id_hash,
            account_currency=account_currency,
        )
    fin = _decimal(payload.get("financing"))
    if fin is None or fin == 0:
        return []
    when = _parse_rfc3339(payload.get("time", "1970-01-01T00:00:00Z"))
    units_dec = _decimal(payload.get("units"))
    return [{
        "transaction_id": str(payload["id"]),
        "instrument": payload.get("instrument"),
        "trade_id": None,
        "units": str(units_dec) if units_dec is not None else None,
        "financing": str(fin),
        "time": when.isoformat(),
    }]


# ---------- Practice-tag confirmation ----------


def confirm_practice_account(
    client: _SupportsRequest,
    account_id: str,
    *,
    require_practice_tag: bool,
) -> dict[str, Any]:
    """GET /v3/accounts/{id} → returns the raw payload (used
    locally only). If require_practice_tag is True and the
    account is not tagged PRACTICE, raises RuntimeError."""
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}"
    payload = _safe_get(client, url, account_id)
    if require_practice_tag:
        account = payload.get("account") or {}
        tags = account.get("tags") or []
        if not any(str(tag).upper() == "PRACTICE" for tag in tags):
            raise RuntimeError(
                "account is not tagged PRACTICE — refusing under "
                "--require-practice-tag"
            )
    return payload


def get_account_summary_practice(
    client: _SupportsRequest, account_id: str,
) -> dict[str, Any]:
    """GET /v3/accounts/{id}/summary — read-only."""
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/summary"
    return _safe_get(client, url, account_id)


def get_transactions_since(
    client: _SupportsRequest,
    account_id: str,
    since_transaction_id: str,
) -> list[dict[str, Any]]:
    """GET /v3/accounts/{id}/transactions/sinceid?id=... —
    read-only. Returns the list of raw transaction payloads."""
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/transactions/sinceid"
    payload = _safe_get(
        client, url, account_id, params={"id": since_transaction_id},
    )
    return list(payload.get("transactions") or [])


def get_transactions_range(
    client: _SupportsRequest,
    account_id: str,
    from_iso: str,
    to_iso: str,
) -> list[dict[str, Any]]:
    """GET /v3/accounts/{id}/transactions?from=...&to=... —
    read-only."""
    url = f"{PRACTICE_REST_HOST}/v3/accounts/{account_id}/transactions"
    payload = _safe_get(
        client, url, account_id, params={"from": from_iso, "to": to_iso},
    )
    return list(payload.get("transactions") or [])


# ---------- Output ----------


def build_capture_output(
    *,
    account_id_hash: str,
    account_currency: str,
    provenance: str,
    events: list[dict[str, Any]],
    synthetic: bool = False,
) -> dict[str, Any]:
    """Build the fixture-shape capture output dict.

    Matches the v1 schema in
    docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md."""
    if "PRACTICE" not in provenance.upper() and not synthetic:
        # Soft guidance — provenance should make the
        # environment explicit for downstream review.
        pass
    return {
        "kind": "observed_financing_events",
        "schema_version": 1,
        "synthetic": synthetic,
        "provenance": provenance,
        "account_currency": account_currency,
        "account_id_hash": account_id_hash,
        "events": sorted(
            events,
            key=lambda e: (e["time"], e.get("instrument") or "", e.get("trade_id") or ""),
        ),
    }


def dump_capture(output_dir: Path, payload: dict[str, Any]) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / "observed_financing.json"
    out_path.write_text(
        json.dumps(payload, sort_keys=True, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return out_path


# ---------- CLI orchestration ----------


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Read-only OANDA practice DAILY_FINANCING capture pilot. "
            "Practice only; no orders; no mutation; credentials never "
            "printed; raw output under --output (default /tmp/); never "
            "commits."
        )
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("/tmp/financing_observed_capture"),
        help="Output directory for the redacted JSON dump.",
    )
    mode = parser.add_mutually_exclusive_group(required=False)
    mode.add_argument(
        "--since-transaction-id",
        type=str,
        default=None,
        help="Fetch transactions starting at this id (exclusive).",
    )
    mode.add_argument(
        "--range",
        nargs=2,
        metavar=("FROM_ISO", "TO_ISO"),
        default=None,
        help="Date-range fetch: ISO-8601 from and to.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Verify creds, practice tag, and connectivity to "
            "/summary, then exit 0 without fetching transactions."
        ),
    )
    parser.add_argument(
        "--require-practice-tag",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Require the account's tags to include PRACTICE. Default on.",
    )
    parser.add_argument(
        "--provenance",
        type=str,
        default=None,
        help=(
            "Provenance label for the output (must not contain account "
            "id or token). Default 'oanda-practice-YYYY-MM-DD'."
        ),
    )
    return parser.parse_args(argv)


def _read_practice_creds() -> tuple[str | None, str | None]:
    """Read practice creds from the documented env vars only.

    OANDA_*_LIVE are NOT consulted — explicit policy. Returns
    (token, account_id) tuple; either may be None."""
    token = os.environ.get(PRACTICE_TOKEN_ENV)
    account_id = os.environ.get(PRACTICE_ACCOUNT_ENV)
    return token, account_id


def _default_provenance() -> str:
    return f"oanda-practice-{datetime.now(UTC).date().isoformat()}"


def run(
    argv: list[str] | None = None,
    *,
    client_factory: Any = None,
) -> int:
    """Top-level entrypoint. ``client_factory`` is injectable
    for tests; in production it is ``make_client``."""
    args = _parse_args(argv)
    token, account_id = _read_practice_creds()
    if not token or not account_id:
        # No credential VALUE is included in this message — only
        # the env var names.
        print(
            "[capture_oanda_observed_financing_pilot] missing practice "
            f"credentials: set {PRACTICE_TOKEN_ENV} and "
            f"{PRACTICE_ACCOUNT_ENV}; refusing.",
            file=sys.stderr,
        )
        return EXIT_MISSING_CREDS

    factory = client_factory or make_client
    try:
        client = factory(token)
    except Exception as exc:
        print(
            f"[capture_oanda_observed_financing_pilot] failed to build "
            f"HTTP client: {type(exc).__name__}",
            file=sys.stderr,
        )
        return EXIT_RUNTIME

    try:
        # 1) Practice-tag check (also confirms auth + account exists).
        try:
            account_payload = confirm_practice_account(
                client, account_id,
                require_practice_tag=args.require_practice_tag,
            )
        except RuntimeError as exc:
            print(
                f"[capture_oanda_observed_financing_pilot] {exc}",
                file=sys.stderr,
            )
            return EXIT_NOT_PRACTICE

        account_currency = (
            account_payload.get("account", {}).get("currency", "USD")
        )

        if args.dry_run:
            # Lightweight follow-up to confirm /summary works.
            try:
                _ = get_account_summary_practice(client, account_id)
            except RuntimeError as exc:
                print(
                    f"[capture_oanda_observed_financing_pilot] /summary failed: {exc}",
                    file=sys.stderr,
                )
                return EXIT_HTTP
            print(
                "[capture_oanda_observed_financing_pilot] dry-run OK: practice "
                "credentials valid, account tagged PRACTICE (or skipped), "
                "/summary reachable."
            )
            return EXIT_OK

        # 2) Fetch the transaction set.
        try:
            if args.since_transaction_id is not None:
                raw_transactions = get_transactions_since(
                    client, account_id, args.since_transaction_id,
                )
            elif args.range is not None:
                from_iso, to_iso = args.range
                raw_transactions = get_transactions_range(
                    client, account_id, from_iso, to_iso,
                )
            else:
                # No mode → use /summary to discover the last id and
                # fetch since (last_id - some_margin). Conservative:
                # we only fetch since the most recent id, which is
                # often the cheapest read.
                summary_payload = get_account_summary_practice(client, account_id)
                last_id = (
                    summary_payload.get("account", {}).get("lastTransactionID")
                    or summary_payload.get("lastTransactionID")
                )
                if not last_id:
                    print(
                        "[capture_oanda_observed_financing_pilot] could not "
                        "discover lastTransactionID; pass --since-transaction-id "
                        "or --range.",
                        file=sys.stderr,
                    )
                    return EXIT_HTTP
                raw_transactions = get_transactions_since(
                    client, account_id, str(last_id),
                )
        except RuntimeError as exc:
            print(
                f"[capture_oanda_observed_financing_pilot] fetch failed: {exc}",
                file=sys.stderr,
            )
            return EXIT_HTTP

        # 3) Parse + redact.
        account_id_hash = hash_account_id_local(account_id)
        events = _flatten_events(
            raw_transactions,
            account_id_hash=account_id_hash,
            account_currency=account_currency,
        )

        # 4) Dump.
        provenance = args.provenance or _default_provenance()
        out = build_capture_output(
            account_id_hash=account_id_hash,
            account_currency=account_currency,
            provenance=provenance,
            events=events,
            synthetic=False,
        )
        try:
            out_path = dump_capture(args.output, out)
        except OSError as exc:
            print(
                f"[capture_oanda_observed_financing_pilot] output I/O error: {exc}",
                file=sys.stderr,
            )
            return EXIT_IO

        print(
            f"[capture_oanda_observed_financing_pilot] wrote {len(events)} "
            f"event(s) to {out_path}"
        )
        return EXIT_OK
    finally:
        try:
            client.close()
        except Exception:
            pass


def _flatten_events(
    raw_transactions: Iterable[dict[str, Any]],
    *,
    account_id_hash: str,
    account_currency: str,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for tx in raw_transactions:
        events.extend(parse_observed_financing_events(
            tx,
            account_id_hash=account_id_hash,
            account_currency=account_currency,
        ))
    return events


def main(argv: list[str] | None = None) -> int:
    return run(argv)


if __name__ == "__main__":  # pragma: no cover — exercised via main()
    sys.exit(main())
