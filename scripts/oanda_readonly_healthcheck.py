#!/usr/bin/env python3
"""Read-only OANDA practice API health check.

Verifies that the repo can safely talk to the OANDA **practice**
read-only endpoints. The script is *structurally* incapable of
submitting or modifying an order: it calls only the read-only methods
of the Broker protocol (every one a `GET`) and never `submit_order` or
`close_trade`.

Safety gates (all enforced before any network call):
  * refuses any environment that is not unambiguously practice
    (the `forex_bot.guards` practice-data environment guard);
  * refuses a config that enables `app.allow_order_submission`;
  * refuses missing / placeholder credentials.

Redaction: the account id is redacted to first-3 / last-3 characters
in every output; the access token is never printed, logged, or written.

Exit codes:
  0  all read-only checks passed
  1  one or more endpoint checks failed (report still written)
  2  refused — unsafe config, non-practice environment, or missing creds

Usage:
    python scripts/oanda_readonly_healthcheck.py \\
        [--config configs/paper.yaml] \\
        [--out docs/research/OANDA_READONLY_HEALTHCHECK_RESULT.md]

See docs/research/OANDA_PRACTICE_READONLY_001_PLAN.md.
"""

from __future__ import annotations

import argparse
import sys
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from forex_bot.broker.errors import BrokerError, BrokerRateLimitError
from forex_bot.broker.oanda import REST_HOSTS, OandaBroker
from forex_bot.config import ConfigError, Settings, load_settings
from forex_bot.domain.candles import CandleRequest
from forex_bot.guards import assert_practice_data_environment

DEFAULT_CONFIG = ROOT / "configs" / "paper.yaml"
DEFAULT_OUT = ROOT / "docs" / "research" / "OANDA_READONLY_HEALTHCHECK_RESULT.md"

# A small, safe instrument set for the pricing snapshot.
PRICING_INSTRUMENTS = ["EUR_USD", "USD_JPY"]
CANDLE_INSTRUMENT = "EUR_USD"

# The OANDA endpoints this healthcheck is permitted to touch — every one
# a GET. The script calls nothing else.
READONLY_ENDPOINTS = (
    "GET /v3/accounts/{id}/summary",
    "GET /v3/accounts/{id}",
    "GET /v3/accounts/{id}/instruments",
    "GET /v3/accounts/{id}/pricing",
    "GET /v3/accounts/{id}/instruments/{instrument}/candles",
    "GET /v3/accounts/{id}/transactions/sinceid",
    "GET /v3/accounts/{id}/openTrades",
    "GET /v3/accounts/{id}/openPositions",
    "GET /v3/accounts/{id}/pendingOrders",
)
# Endpoints this healthcheck must NEVER touch. Listed for the report and
# asserted against by the test-suite.
FORBIDDEN_ENDPOINTS = (
    "POST /v3/accounts/{id}/orders",
    "PUT /v3/accounts/{id}/orders/{id}",
    "PUT /v3/accounts/{id}/orders/{id}/cancel",
    "PUT /v3/accounts/{id}/trades/{id}/close",
    "PUT /v3/accounts/{id}/trades/{id}/orders",
    "PUT /v3/accounts/{id}/positions/{instrument}/close",
)


class UnsafeConfigError(RuntimeError):
    """Raised when the healthcheck refuses to run for a safety reason."""


def redact_account_id(account_id: str | None) -> str:
    """Redact an account id to first-3 / last-3 characters."""
    aid = (account_id or "").strip()
    if len(aid) >= 8:
        return f"{aid[:3]}…{aid[-3:]}"
    return "<short-or-empty>"


# --------------------------------------------------------------------------
# Result model
# --------------------------------------------------------------------------


@dataclass
class EndpointResult:
    name: str
    http: str
    status: str  # "OK" | "FAIL" | "SKIP"
    latency_ms: float | None
    detail: str
    error: str | None = None


@dataclass
class HealthcheckReport:
    environment: str
    host: str
    account_id_redacted: str
    results: list[EndpointResult] = field(default_factory=list)
    instrument_count: int | None = None
    sample_instruments: list[str] = field(default_factory=list)
    sample_price_instrument: str | None = None
    sample_price_time: str | None = None
    sample_candle_instrument: str | None = None
    sample_candle_time: str | None = None
    notes: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        """True if no endpoint check FAILed (a SKIP does not fail the run)."""
        return not any(r.status == "FAIL" for r in self.results)

    @property
    def failures(self) -> list[EndpointResult]:
        return [r for r in self.results if r.status == "FAIL"]


# --------------------------------------------------------------------------
# Safety gates (no network)
# --------------------------------------------------------------------------


def run_safety_gates(settings: Settings) -> None:
    """Refuse to run unless the config is read-only-safe and the
    environment is unambiguously practice. Pure — makes no network call.

    Order matters: the static, credential-free config flag is checked
    first, then the practice-data environment guard.
    """
    if settings.app.allow_order_submission:
        raise UnsafeConfigError(
            "config enables app.allow_order_submission — refusing to run a "
            "read-only healthcheck under an order-submitting config. Use a "
            "read-only config such as configs/paper.yaml "
            "(allow_order_submission: false)."
        )
    try:
        assert_practice_data_environment(settings)
    except ConfigError as exc:
        raise UnsafeConfigError(f"practice-data environment guard refused: {exc}") from exc


# --------------------------------------------------------------------------
# Read-only endpoint checks
# --------------------------------------------------------------------------


def run_healthcheck(
    broker: Any,
    *,
    pricing_instruments: list[str] | None = None,
    candle_instrument: str = CANDLE_INSTRUMENT,
) -> HealthcheckReport:
    """Probe every read-only endpoint the repo relies on. One endpoint
    failure never aborts the run — each is recorded and the rest proceed.

    `broker` only needs the read-only methods of the Broker protocol;
    `submit_order` / `close_trade` are never referenced here.
    """
    pricing = pricing_instruments or PRICING_INSTRUMENTS
    raw_account_id = (getattr(broker, "account_id", "") or "").strip()
    report = HealthcheckReport(
        environment=getattr(broker, "environment", "<unknown>"),
        host=REST_HOSTS.get(getattr(broker, "environment", ""), "<unknown>"),
        account_id_redacted=redact_account_id(raw_account_id),
    )

    def scrub(text: str) -> str:
        """Strip the account id from any text before it enters the report.
        OANDA error bodies echo the request path, which contains the
        account id — without this, a failing endpoint would leak it."""
        if raw_account_id and raw_account_id in text:
            return text.replace(raw_account_id, report.account_id_redacted)
        return text

    def record(
        name: str,
        http: str,
        call: Callable[[], Any],
        summarize: Callable[[Any], str],
    ) -> Any:
        """Run one read-only call; append its result; return the value or
        None on failure. The healthcheck must never crash on a bad call."""
        start = time.monotonic()
        try:
            value = call()
        except BrokerRateLimitError as exc:
            ms = (time.monotonic() - start) * 1000.0
            report.notes.append(f"{name}: HTTP 429 rate limit observed")
            report.results.append(
                EndpointResult(
                    name, http, "FAIL", ms, "rate limited (429)",
                    error=scrub(str(exc)),
                )
            )
            return None
        except BrokerError as exc:
            ms = (time.monotonic() - start) * 1000.0
            report.results.append(
                EndpointResult(
                    name, http, "FAIL", ms, "broker error",
                    error=scrub(f"{type(exc).__name__}: {exc}"),
                )
            )
            return None
        except Exception as exc:
            ms = (time.monotonic() - start) * 1000.0
            report.results.append(
                EndpointResult(
                    name, http, "FAIL", ms, "unexpected error",
                    error=scrub(f"{type(exc).__name__}: {exc}"),
                )
            )
            return None
        ms = (time.monotonic() - start) * 1000.0
        try:
            detail = summarize(value)
        except Exception as exc:
            report.results.append(
                EndpointResult(
                    name, http, "FAIL", ms, "response parse error",
                    error=scrub(f"{type(exc).__name__}: {exc}"),
                )
            )
            return None
        report.results.append(EndpointResult(name, http, "OK", ms, scrub(detail)))
        return value

    summary = record(
        "account summary",
        "GET /v3/accounts/{id}/summary",
        broker.get_account_summary,
        lambda s: (
            f"currency={s.currency} openTrades={s.open_trade_count} "
            f"openPositions={s.open_position_count} "
            f"pendingOrders={s.pending_order_count}"
        ),
    )
    record(
        "account details",
        "GET /v3/accounts/{id}",
        broker.get_account_details,
        lambda d: (
            f"openTradeIds={len(d.open_trade_ids)} "
            f"openPositionInstruments={len(d.open_position_instruments)} "
            f"pendingOrderIds={len(d.pending_order_ids)}"
        ),
    )
    instruments = record(
        "instruments list",
        "GET /v3/accounts/{id}/instruments",
        broker.list_instruments,
        lambda ins: f"{len(ins)} tradeable instruments",
    )
    if instruments is not None:
        report.instrument_count = len(instruments)
        report.sample_instruments = sorted(i.name for i in instruments)[:8]

    quotes = record(
        "pricing snapshot",
        "GET /v3/accounts/{id}/pricing",
        lambda: broker.get_prices(pricing),
        lambda qs: f"{len(qs)} quote(s) for {', '.join(pricing)}",
    )
    if quotes:
        report.sample_price_instrument = quotes[0].instrument
        report.sample_price_time = quotes[0].time.isoformat()

    candles = record(
        f"latest {candle_instrument} H4 candle",
        f"GET /v3/accounts/{{id}}/instruments/{candle_instrument}/candles",
        lambda: broker.get_candles(
            CandleRequest(
                instrument=candle_instrument, granularity="H4", price="BA", count=5
            )
        ),
        lambda cs: (
            f"{len(cs)} candle(s) returned, "
            f"{sum(1 for c in cs if c.complete)} complete"
        ),
    )
    if candles:
        complete = [c for c in candles if c.complete]
        if complete:
            report.sample_candle_instrument = candle_instrument
            report.sample_candle_time = complete[-1].time.isoformat()

    if summary is not None and summary.last_transaction_id:
        last_id = summary.last_transaction_id
        record(
            "transaction history (read)",
            "GET /v3/accounts/{id}/transactions/sinceid",
            lambda: broker.get_transactions_since(last_id),
            lambda txs: (
                f"{len(txs)} transaction(s) since last id — "
                "read-only history endpoint reachable"
            ),
        )
    else:
        report.results.append(
            EndpointResult(
                "transaction history (read)",
                "GET /v3/accounts/{id}/transactions/sinceid",
                "SKIP",
                None,
                "no lastTransactionID from account summary — skipped",
            )
        )

    record(
        "open trades (read)",
        "GET /v3/accounts/{id}/openTrades",
        broker.list_open_trades,
        lambda t: f"{len(t)} open trade(s)",
    )
    record(
        "open positions (read)",
        "GET /v3/accounts/{id}/openPositions",
        broker.list_positions,
        lambda p: f"{len(p)} open position(s)",
    )
    record(
        "pending orders (read)",
        "GET /v3/accounts/{id}/pendingOrders",
        broker.list_open_orders,
        lambda o: f"{len(o)} pending order(s)",
    )

    return report


# --------------------------------------------------------------------------
# Report rendering
# --------------------------------------------------------------------------


def render_report(
    report: HealthcheckReport,
    *,
    config_path: str,
    generated_at: datetime,
) -> str:
    """Render the healthcheck report as Markdown. Contains only redacted /
    aggregate information — never a credential value."""
    lines: list[str] = []
    status_word = "PASS" if report.ok else "FAIL"
    lines += [
        "# OANDA Read-Only Healthcheck Result — "
        "`oanda-practice-readonly-001` Phase 2",
        "",
        f"**Generated:** {generated_at.isoformat()} · "
        f"**Branch:** `oanda-practice-readonly-001`",
        f"**Config:** `{config_path}` · **Overall:** **{status_word}**",
        "",
        "> Read-only diagnostic. This healthcheck calls only OANDA "
        "**practice** read-only (`GET`) endpoints. **No order was "
        "submitted, created, modified, or closed.** It is not a strategy "
        "campaign and produces no trading verdict.",
        "",
        "## Environment",
        "",
        "| field | value |",
        "|---|---|",
        f"| broker environment | `{report.environment}` |",
        f"| OANDA host | `{report.host}` |",
        f"| account id (redacted) | `{report.account_id_redacted}` |",
        "",
        "## Endpoint results",
        "",
        "| endpoint | HTTP | status | latency | detail |",
        "|---|---|---|---|---|",
    ]
    for r in report.results:
        latency = f"{r.latency_ms:.0f} ms" if r.latency_ms is not None else "—"
        detail = r.detail if r.status != "FAIL" else (r.error or r.detail)
        lines.append(
            f"| {r.name} | `{r.http}` | {r.status} | {latency} | {detail} |"
        )

    ok_n = sum(1 for r in report.results if r.status == "OK")
    fail_n = len(report.failures)
    skip_n = sum(1 for r in report.results if r.status == "SKIP")
    lines += [
        "",
        f"**{ok_n} OK · {fail_n} FAIL · {skip_n} SKIP** "
        f"out of {len(report.results)} read-only endpoint checks.",
        "",
        "## Instrument metadata",
        "",
        f"- instrument count: "
        f"{report.instrument_count if report.instrument_count is not None else 'n/a'}",
        f"- sample instruments: "
        f"{', '.join(report.sample_instruments) if report.sample_instruments else 'n/a'}",
        "",
        "## Sample market data",
        "",
        f"- sample price snapshot: "
        f"{report.sample_price_instrument or 'n/a'} @ "
        f"{report.sample_price_time or 'n/a'}",
        f"- latest complete candle: "
        f"{report.sample_candle_instrument or 'n/a'} H4 @ "
        f"{report.sample_candle_time or 'n/a'}",
        "",
        "## Rate-limit / retry observations",
        "",
    ]
    if report.notes:
        lines += [f"- {n}" for n in report.notes]
    else:
        lines.append("- none — no HTTP 429 or retry was observed during this run.")

    lines += ["", "## Failures and follow-ups", ""]
    if report.failures:
        for r in report.failures:
            lines.append(f"- **{r.name}** (`{r.http}`): {r.error or r.detail}")
        lines.append("")
        lines.append(
            "Follow-up: re-run the healthcheck; if a failure persists, "
            "investigate before relying on the affected endpoint. A failure "
            "here blocks no other safe phase that does not need that endpoint."
        )
    else:
        lines.append("- none — every read-only endpoint check passed.")

    lines += [
        "",
        "## Endpoints NOT called (forbidden in this sprint)",
        "",
        "This healthcheck never calls any order / trade / position "
        "mutating endpoint:",
        "",
    ]
    lines += [f"- `{e}`" for e in FORBIDDEN_ENDPOINTS]
    lines += [
        "",
        "## Safety statement",
        "",
        "- **No order was submitted, created, modified, or closed.** Only "
        "read-only (`GET`) endpoints were called.",
        "- The run was gated to the OANDA **practice** environment; the "
        "live host was never contacted.",
        "- The account id is redacted (first-3 / last-3); the access token "
        "was never printed, logged, or written.",
        "- This is a diagnostic only — `strategy_evidence: false`. It "
        "approves no strategy and produces no trading recommendation.",
        "",
    ]
    return "\n".join(lines)


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Read-only OANDA practice API health check."
    )
    ap.add_argument("--config", default=str(DEFAULT_CONFIG))
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    args = ap.parse_args(argv)

    try:
        settings = load_settings(Path(args.config))
    except ConfigError as exc:
        print(f"REFUSED: config error — {exc}", file=sys.stderr)
        return 2

    try:
        run_safety_gates(settings)
    except UnsafeConfigError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 2

    # The gate guarantees practice + present credentials.
    account_id, token = settings.broker_credentials()
    broker = OandaBroker(
        environment="practice",
        account_id=account_id,
        access_token=token,
        timeout_seconds=settings.broker.request_timeout_seconds,
        max_retries=settings.broker.max_retries,
    )
    try:
        report = run_healthcheck(broker)
    finally:
        broker.close()

    try:
        cfg_display = str(Path(args.config).resolve().relative_to(ROOT))
    except ValueError:
        cfg_display = str(args.config)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        render_report(
            report, config_path=cfg_display, generated_at=datetime.now(UTC)
        ),
        encoding="utf-8",
    )

    ok_n = sum(1 for r in report.results if r.status == "OK")
    fail_n = len(report.failures)
    skip_n = sum(1 for r in report.results if r.status == "SKIP")
    try:
        out_display = str(out_path.resolve().relative_to(ROOT))
    except ValueError:
        out_display = str(out_path)
    print(
        f"healthcheck: {ok_n} OK / {fail_n} FAIL / {skip_n} SKIP — "
        f"report written to {out_display}"
    )
    print("no orders submitted; only read-only GET endpoints were called.")
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
