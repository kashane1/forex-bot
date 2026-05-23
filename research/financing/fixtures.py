"""Loader / adapter for committed financing fixtures.

Two top-level shapes (``kind``):

* ``observed_financing_events`` → :func:`load_observed_event_fixture`
  returns ``ObservedEventDict`` rows whose field names, types, and
  validation rules mirror the canonical
  ``forex_bot.domain.transactions.ObservedFinancingEvent`` model
  field-for-field. The loader **does not** import that model — the
  package-wide import-isolation rail forbids importing from
  ``forex_bot``. A reconciliation test confirms the loaded shape
  matches the canonical model's field set.

* ``financing_rates`` → :func:`load_rate_fixture` returns a
  :class:`research.financing.rates.TableRateSource`.

Strict validation: every rejection raises
:class:`FixtureValidationError` with a strict, human-readable
message identifying the file path, the row index (where
applicable), and the offending field.

No network, no broker calls, no clock reads. Pure pass over JSON.

See ``docs/research/FINANCING_OBSERVED_FIXTURE_SCHEMA.md`` for the
on-disk schema.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, TypedDict

from research.financing.models import FinancingTreatment, RatePair
from research.financing.rates import TableRateSource

_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
_CURRENCY_RE = re.compile(r"^[A-Z]{3}$")
_HEX64_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

SCHEMA_VERSION = 1

_EVENT_FILE_TOP_KEYS = {
    "kind",
    "schema_version",
    "synthetic",
    "provenance",
    "account_currency",
    "account_id_hash",
    "events",
}
_EVENT_ROW_KEYS = {
    "transaction_id",
    "instrument",
    "trade_id",
    "units",
    "financing",
    "time",
}
_EVENT_ROW_REQUIRED = {"transaction_id", "financing", "time"}

_RATE_FILE_TOP_KEYS = {
    "kind",
    "schema_version",
    "synthetic",
    "provenance",
    "rate_unit",
    "missing_dates",
    "rates",
}
_RATE_ROW_KEYS = {
    "date_utc",
    "instrument",
    "long_annual_bp",
    "short_annual_bp",
}
_RATE_ROW_REQUIRED = _RATE_ROW_KEYS


class FixtureValidationError(ValueError):
    """Raised by the loader when a fixture file fails schema
    validation. The error message names the file, the row index
    (if applicable), and the offending field."""


class ObservedEventDict(TypedDict):
    """One loaded observed financing event.

    Field names, types, and semantics mirror
    ``forex_bot.domain.transactions.ObservedFinancingEvent``
    field-for-field. ``event_key`` is the canonical SHA-1
    derivation (sha1 of ``transaction_id|instrument|trade_id``).
    """

    transaction_id: str
    account_id_hash: str
    instrument: str | None
    trade_id: str | None
    units: Decimal | None
    financing: Decimal
    currency: str
    time: datetime
    source: str
    event_key: str


def canonical_event_key(
    transaction_id: str,
    instrument: str | None,
    trade_id: str | None,
) -> str:
    """The same SHA-1 derivation used by
    ``ObservedFinancingEvent.event_key``. Defined here so the
    loader can compute it without importing from ``forex_bot``."""
    raw = f"{transaction_id}|{instrument or ''}|{trade_id or ''}"
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()


def _ctx(path: Path | None, row_index: int | None, message: str) -> str:
    parts = []
    if path is not None:
        parts.append(f"{path}")
    if row_index is not None:
        parts.append(f"row {row_index}")
    parts.append(message)
    return " — ".join(parts)


def _require_top_keys(
    payload: dict[str, Any], allowed: set[str], required: set[str], path: Path
) -> None:
    extra = set(payload) - allowed
    if extra:
        raise FixtureValidationError(
            _ctx(path, None, f"unknown top-level keys: {sorted(extra)}")
        )
    missing = required - set(payload)
    if missing:
        raise FixtureValidationError(
            _ctx(path, None, f"missing required top-level keys: {sorted(missing)}")
        )


def _check_common_top(payload: dict[str, Any], expected_kind: str, path: Path) -> None:
    if payload.get("kind") != expected_kind:
        raise FixtureValidationError(
            _ctx(path, None, f"kind must be {expected_kind!r}, got {payload.get('kind')!r}")
        )
    if payload.get("schema_version") != SCHEMA_VERSION:
        raise FixtureValidationError(
            _ctx(
                path,
                None,
                f"schema_version must be {SCHEMA_VERSION}, got "
                f"{payload.get('schema_version')!r}",
            )
        )
    if not isinstance(payload.get("synthetic"), bool):
        raise FixtureValidationError(
            _ctx(path, None, "synthetic must be a boolean")
        )
    if not isinstance(payload.get("provenance"), str) or not payload["provenance"]:
        raise FixtureValidationError(
            _ctx(path, None, "provenance must be a non-empty string")
        )


def _parse_decimal_string(value: Any, path: Path, row_index: int, field: str) -> Decimal:
    if not isinstance(value, str):
        raise FixtureValidationError(
            _ctx(
                path,
                row_index,
                f"{field!r} must be a stringified Decimal (numeric literals "
                f"forbidden), got {type(value).__name__}",
            )
        )
    try:
        return Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise FixtureValidationError(
            _ctx(path, row_index, f"{field!r} is not parseable as Decimal: {value!r}")
        ) from exc


def _parse_aware_datetime(value: Any, path: Path, row_index: int) -> datetime:
    if not isinstance(value, str):
        raise FixtureValidationError(
            _ctx(
                path,
                row_index,
                f"'time' must be a string ISO-8601 timestamp, got {type(value).__name__}",
            )
        )
    try:
        # `datetime.fromisoformat` accepts "+00:00" since Python 3.11
        # and "Z" since 3.11. The fixtures use explicit offsets so this
        # path is straightforward.
        dt = datetime.fromisoformat(value)
    except ValueError as exc:
        raise FixtureValidationError(
            _ctx(path, row_index, f"'time' is not a valid ISO-8601 timestamp: {value!r}")
        ) from exc
    if dt.tzinfo is None:
        raise FixtureValidationError(
            _ctx(
                path,
                row_index,
                f"'time' must be timezone-aware (naive timestamps rejected): {value!r}",
            )
        )
    return dt


def _check_event_row_keys(row: dict[str, Any], path: Path, row_index: int) -> None:
    if not isinstance(row, dict):
        raise FixtureValidationError(
            _ctx(path, row_index, f"event row must be a JSON object, got {type(row).__name__}")
        )
    extra = set(row) - _EVENT_ROW_KEYS
    if extra:
        raise FixtureValidationError(
            _ctx(path, row_index, f"unknown event-row keys: {sorted(extra)}")
        )
    missing = _EVENT_ROW_REQUIRED - set(row)
    if missing:
        raise FixtureValidationError(
            _ctx(path, row_index, f"missing required event-row keys: {sorted(missing)}")
        )


def _check_rate_row_keys(row: dict[str, Any], path: Path, row_index: int) -> None:
    if not isinstance(row, dict):
        raise FixtureValidationError(
            _ctx(path, row_index, f"rate row must be a JSON object, got {type(row).__name__}")
        )
    extra = set(row) - _RATE_ROW_KEYS
    if extra:
        raise FixtureValidationError(
            _ctx(path, row_index, f"unknown rate-row keys: {sorted(extra)}")
        )
    missing = _RATE_ROW_REQUIRED - set(row)
    if missing:
        raise FixtureValidationError(
            _ctx(path, row_index, f"missing required rate-row keys: {sorted(missing)}")
        )


def _check_instrument(value: Any, path: Path, row_index: int) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not _INSTRUMENT_RE.fullmatch(value):
        raise FixtureValidationError(
            _ctx(
                path,
                row_index,
                f"'instrument' must match {_INSTRUMENT_RE.pattern} or be null, got {value!r}",
            )
        )


def _parse_event_row(
    row: dict[str, Any],
    *,
    path: Path,
    row_index: int,
    account_currency: str,
    account_id_hash: str,
    source: str,
) -> ObservedEventDict:
    _check_event_row_keys(row, path, row_index)

    tx_id = row["transaction_id"]
    if not isinstance(tx_id, str) or not tx_id:
        raise FixtureValidationError(
            _ctx(path, row_index, "'transaction_id' must be a non-empty string")
        )

    instrument = row.get("instrument")
    _check_instrument(instrument, path, row_index)

    trade_id = row.get("trade_id")
    if trade_id is not None and (not isinstance(trade_id, str) or not trade_id):
        raise FixtureValidationError(
            _ctx(path, row_index, "'trade_id' must be a non-empty string or null")
        )

    units = (
        None
        if row.get("units") is None
        else _parse_decimal_string(row["units"], path, row_index, "units")
    )

    financing = _parse_decimal_string(row["financing"], path, row_index, "financing")

    when = _parse_aware_datetime(row["time"], path, row_index)

    return ObservedEventDict(
        transaction_id=tx_id,
        account_id_hash=account_id_hash,
        instrument=instrument,
        trade_id=trade_id,
        units=units,
        financing=financing,
        currency=account_currency,
        time=when,
        source=source,
        event_key=canonical_event_key(tx_id, instrument, trade_id),
    )


def load_observed_event_fixture(path: str | Path) -> list[ObservedEventDict]:
    """Load and validate an observed-events fixture file.

    Returns events sorted by
    ``(time, instrument or "", trade_id or "")`` for
    deterministic downstream consumption.

    Raises ``FixtureValidationError`` on any schema violation.
    """
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise FixtureValidationError(
            _ctx(p, None, f"could not read file: {exc}")
        ) from exc

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(_ctx(p, None, f"invalid JSON: {exc}")) from exc

    if not isinstance(payload, dict):
        raise FixtureValidationError(
            _ctx(p, None, f"top-level must be a JSON object, got {type(payload).__name__}")
        )

    _require_top_keys(payload, _EVENT_FILE_TOP_KEYS, _EVENT_FILE_TOP_KEYS, p)
    _check_common_top(payload, "observed_financing_events", p)

    account_currency = payload["account_currency"]
    if not isinstance(account_currency, str) or not _CURRENCY_RE.fullmatch(account_currency):
        raise FixtureValidationError(
            _ctx(
                p,
                None,
                f"account_currency must match {_CURRENCY_RE.pattern}, got "
                f"{account_currency!r}",
            )
        )

    account_id_hash = payload["account_id_hash"]
    if not isinstance(account_id_hash, str) or not _HEX64_RE.fullmatch(account_id_hash):
        raise FixtureValidationError(
            _ctx(
                p,
                None,
                "account_id_hash must be a 64-character lowercase SHA-256 hex digest",
            )
        )

    events_raw = payload["events"]
    if not isinstance(events_raw, list):
        raise FixtureValidationError(
            _ctx(p, None, f"'events' must be an array, got {type(events_raw).__name__}")
        )

    source = payload["provenance"]
    parsed = [
        _parse_event_row(
            row,
            path=p,
            row_index=i,
            account_currency=account_currency,
            account_id_hash=account_id_hash,
            source=source,
        )
        for i, row in enumerate(events_raw)
    ]

    parsed.sort(key=lambda e: (e["time"], e["instrument"] or "", e["trade_id"] or ""))
    return parsed


def _parse_rate_row(
    row: dict[str, Any], path: Path, row_index: int
) -> tuple[date, str, RatePair]:
    _check_rate_row_keys(row, path, row_index)

    date_value = row["date_utc"]
    if not isinstance(date_value, str) or not _DATE_RE.fullmatch(date_value):
        raise FixtureValidationError(
            _ctx(path, row_index, f"'date_utc' must be YYYY-MM-DD, got {date_value!r}")
        )
    try:
        d = date.fromisoformat(date_value)
    except ValueError as exc:
        raise FixtureValidationError(
            _ctx(path, row_index, f"'date_utc' is not a valid date: {date_value!r}")
        ) from exc

    instrument = row["instrument"]
    if not isinstance(instrument, str) or not _INSTRUMENT_RE.fullmatch(instrument):
        raise FixtureValidationError(
            _ctx(
                path,
                row_index,
                f"'instrument' must match {_INSTRUMENT_RE.pattern}, got {instrument!r}",
            )
        )

    long_bp = row["long_annual_bp"]
    short_bp = row["short_annual_bp"]
    for field, val in (("long_annual_bp", long_bp), ("short_annual_bp", short_bp)):
        if isinstance(val, bool) or not isinstance(val, (int, float)):
            raise FixtureValidationError(
                _ctx(path, row_index, f"{field!r} must be numeric, got {type(val).__name__}")
            )

    return d, instrument, RatePair(long_annual_bp=float(long_bp), short_annual_bp=float(short_bp))


def load_rate_fixture(
    path: str | Path,
    *,
    treatment: FinancingTreatment = FinancingTreatment.ESTIMATED,
) -> tuple[TableRateSource, list[date]]:
    """Load and validate a rates fixture file.

    Returns ``(source, missing_dates)`` — the populated
    ``TableRateSource`` and the explicit ``missing_dates`` list
    from the file (for tests that want to assert which dates
    are intentionally absent).

    ``treatment`` must not be ``MODELED`` — ``TableRateSource``
    refuses it, and so does this loader.

    Raises ``FixtureValidationError`` on any schema violation.
    """
    if treatment == FinancingTreatment.MODELED:
        raise FixtureValidationError(
            "treatment must not be MODELED — reserved for the future "
            "observed-rate path in src/forex_bot/financing.py"
        )
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise FixtureValidationError(
            _ctx(p, None, f"could not read file: {exc}")
        ) from exc

    try:
        payload: Any = json.loads(text)
    except json.JSONDecodeError as exc:
        raise FixtureValidationError(_ctx(p, None, f"invalid JSON: {exc}")) from exc

    if not isinstance(payload, dict):
        raise FixtureValidationError(
            _ctx(p, None, f"top-level must be a JSON object, got {type(payload).__name__}")
        )

    _require_top_keys(payload, _RATE_FILE_TOP_KEYS, _RATE_FILE_TOP_KEYS, p)
    _check_common_top(payload, "financing_rates", p)

    if payload["rate_unit"] != "annual_bp":
        raise FixtureValidationError(
            _ctx(
                p,
                None,
                f"rate_unit must be 'annual_bp' in v1, got {payload['rate_unit']!r}",
            )
        )

    missing_raw = payload["missing_dates"]
    if not isinstance(missing_raw, list):
        raise FixtureValidationError(
            _ctx(
                p, None, f"'missing_dates' must be an array, got {type(missing_raw).__name__}"
            )
        )
    missing_dates: list[date] = []
    for i, m in enumerate(missing_raw):
        if not isinstance(m, str) or not _DATE_RE.fullmatch(m):
            raise FixtureValidationError(
                _ctx(p, None, f"missing_dates[{i}] must be YYYY-MM-DD, got {m!r}")
            )
        try:
            missing_dates.append(date.fromisoformat(m))
        except ValueError as exc:
            raise FixtureValidationError(
                _ctx(p, None, f"missing_dates[{i}] is not a valid date: {m!r}")
            ) from exc

    rates_raw = payload["rates"]
    if not isinstance(rates_raw, list):
        raise FixtureValidationError(
            _ctx(p, None, f"'rates' must be an array, got {type(rates_raw).__name__}")
        )

    table: dict[tuple[date, str], RatePair] = {}
    for i, row in enumerate(rates_raw):
        d, instrument, pair = _parse_rate_row(row, p, i)
        key = (d, instrument)
        if key in table:
            raise FixtureValidationError(
                _ctx(p, i, f"duplicate (date_utc, instrument) row: {d.isoformat()} {instrument}")
            )
        table[key] = pair

    # Cross-check: every missing_dates entry must be absent from rates.
    rate_dates = {d for (d, _instr) in table}
    overlap = sorted(d for d in missing_dates if d in rate_dates)
    if overlap:
        raise FixtureValidationError(
            _ctx(
                p,
                None,
                f"missing_dates entries also present in rates: "
                f"{[d.isoformat() for d in overlap]}",
            )
        )

    source = TableRateSource(
        table,
        name=payload["provenance"],
        treatment=treatment,
    )
    return source, missing_dates


def utc_date_of(event: ObservedEventDict) -> date:
    """Convenience helper — the UTC date of an event's rollover
    moment. Useful for reconciliation tests that compare loaded
    events to calculator output keyed on rollover date."""
    return event["time"].astimezone(UTC).date()


__all__ = [
    "SCHEMA_VERSION",
    "FixtureValidationError",
    "ObservedEventDict",
    "canonical_event_key",
    "load_observed_event_fixture",
    "load_rate_fixture",
    "utc_date_of",
]
