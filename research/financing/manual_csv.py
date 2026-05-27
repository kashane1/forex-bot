"""Manual CSV financing rate schedule loader.

CSV columns (header required):
  date,instrument,long_annual_bp,short_annual_bp

``date`` is ISO ``YYYY-MM-DD``. Rates are annualized basis points;
negative = debit, positive = credit (same convention as ``RatePair``).

Diagnostic only — ``strategy_evidence: false``.
"""

from __future__ import annotations

import csv
import re
from datetime import date
from pathlib import Path

from research.financing.models import FinancingSourceType, FinancingTreatment, RatePair
from research.financing.rates import TableRateSource

_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_INSTRUMENT_RE = re.compile(r"^[A-Z]{3}_[A-Z]{3}$")
_REQUIRED_COLUMNS = frozenset(
    {"date", "instrument", "long_annual_bp", "short_annual_bp"}
)


class ManualCsvValidationError(ValueError):
    """Raised when a manual CSV rate schedule fails validation."""


def load_manual_csv_rate_schedule(
    path: str | Path,
    *,
    name: str | None = None,
    treatment: FinancingTreatment = FinancingTreatment.ESTIMATED,
) -> TableRateSource:
    """Load a manual CSV rate schedule into a ``TableRateSource``.

    Raises ``ManualCsvValidationError`` on schema violations.
    ``treatment=MODELED`` is refused.
    """
    if treatment == FinancingTreatment.MODELED:
        raise ManualCsvValidationError(
            "Manual CSV schedules may not declare treatment=MODELED."
        )
    p = Path(path)
    try:
        text = p.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManualCsvValidationError(f"could not read {p}: {exc}") from exc

    reader = csv.DictReader(text.splitlines())
    if reader.fieldnames is None:
        raise ManualCsvValidationError(f"{p}: missing header row")
    cols = {c.strip() for c in reader.fieldnames}
    missing = _REQUIRED_COLUMNS - cols
    if missing:
        raise ManualCsvValidationError(
            f"{p}: missing columns {sorted(missing)}; have {sorted(cols)}"
        )

    table: dict[tuple[date, str], RatePair] = {}
    for row_num, row in enumerate(reader, start=2):
        d_str = row["date"].strip()
        inst = row["instrument"].strip()
        if not _DATE_RE.fullmatch(d_str):
            raise ManualCsvValidationError(
                f"{p} row {row_num}: invalid date {d_str!r}"
            )
        if not _INSTRUMENT_RE.fullmatch(inst):
            raise ManualCsvValidationError(
                f"{p} row {row_num}: invalid instrument {inst!r}"
            )
        try:
            long_bp = float(row["long_annual_bp"])
            short_bp = float(row["short_annual_bp"])
        except (TypeError, ValueError) as exc:
            raise ManualCsvValidationError(
                f"{p} row {row_num}: invalid rate values"
            ) from exc
        key = (date.fromisoformat(d_str), inst)
        if key in table:
            raise ManualCsvValidationError(
                f"{p} row {row_num}: duplicate ({d_str}, {inst})"
            )
        table[key] = RatePair(long_annual_bp=long_bp, short_annual_bp=short_bp)

    return TableRateSource(
        table,
        name=name or f"manual_csv:{p.name}",
        treatment=treatment,
        source_type=FinancingSourceType.MANUAL_CSV,
    )
