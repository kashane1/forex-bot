"""Non-time-based bar construction (range bars, volatility bars) from M1.

Pure, deterministic, lookahead-free builders that fold an ordered stream of
:class:`forex_bot.domain.candles.Candle` rows into event-driven bars. No broker
calls, no DB writes, no network. See the design specs for the exact rules:

  * docs/research/RANGE_BAR_CONSTRUCTION_SPEC.md
  * docs/research/VOLATILITY_BAR_CONSTRUCTION_SPEC.md

Range bars complete when price moves ``threshold_pips`` from the bar open (in
either direction). Volatility bars complete when a cumulative movement proxy
(absolute close-to-close, or true range) reaches the threshold. Both are
candle-atomic: a single M1 row closes at most one bar and any overshoot is
recorded (never split into synthetic sub-bars, which M1 OHLC cannot justify).

Internal price/pip arithmetic uses ``Decimal`` so that completion at an exact
threshold is deterministic and free of binary float-representation error; bar
records expose ``float`` OHLC for downstream DataFrame/JSON use.
"""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Literal

from forex_bot.domain.candles import Candle

PriceBasis = Literal["bid", "ask", "mid"]
DuplicatePolicy = Literal["reject", "keep_first", "keep_last"]
VolatilityMethod = Literal["abs_close", "true_range"]
ThresholdMode = Literal["fixed", "atr_scaled"]

_PIP_JPY = Decimal("0.01")
_PIP_DEFAULT = Decimal("0.0001")


def pip_size(instrument: str) -> Decimal:
    """Pip size for FX majors: 0.01 for JPY-quote pairs, else 0.0001."""
    return _PIP_JPY if instrument.upper().endswith("JPY") else _PIP_DEFAULT


# --------------------------------------------------------------------------- #
# Configs
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class RangeBarConfig:
    """Configuration for :func:`build_range_bars`."""

    instrument: str
    threshold_pips: float
    price_basis: PriceBasis = "mid"
    emit_incomplete_final: bool = False
    require_sorted: bool = True
    duplicate_policy: DuplicatePolicy = "reject"

    def __post_init__(self) -> None:
        if self.threshold_pips <= 0:
            raise ValueError("threshold_pips must be positive")
        if self.price_basis not in ("bid", "ask", "mid"):
            raise ValueError(f"unknown price_basis: {self.price_basis}")


@dataclass(frozen=True)
class VolatilityBarConfig:
    """Configuration for :func:`build_volatility_bars`."""

    instrument: str
    method: VolatilityMethod = "abs_close"
    threshold_mode: ThresholdMode = "fixed"
    threshold_pips: float | None = None
    atr_multiple: float | None = None
    atr_window: int | None = None
    price_basis: PriceBasis = "mid"
    emit_incomplete_final: bool = False
    require_sorted: bool = True
    duplicate_policy: DuplicatePolicy = "reject"

    def __post_init__(self) -> None:
        if self.method not in ("abs_close", "true_range"):
            raise ValueError(f"unknown method: {self.method}")
        if self.price_basis not in ("bid", "ask", "mid"):
            raise ValueError(f"unknown price_basis: {self.price_basis}")
        if self.threshold_mode == "fixed":
            if self.threshold_pips is None or self.threshold_pips <= 0:
                raise ValueError("fixed threshold_mode requires positive threshold_pips")
        elif self.threshold_mode == "atr_scaled":
            if self.atr_multiple is None or self.atr_multiple <= 0:
                raise ValueError("atr_scaled threshold_mode requires positive atr_multiple")
            if self.atr_window is None or self.atr_window <= 0:
                raise ValueError("atr_scaled threshold_mode requires positive atr_window")
        else:
            raise ValueError(f"unknown threshold_mode: {self.threshold_mode}")


# --------------------------------------------------------------------------- #
# Bar records
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class RangeBar:
    instrument: str
    price_basis: str
    threshold_pips: float
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_time: datetime
    close_time: datetime
    source_count: int
    source_start_time: datetime
    source_end_time: datetime
    completion_reason: str  # "range_up" | "range_down" | "incomplete"
    thresholds_crossed: int
    overshoot_pips: float
    incomplete: bool = False

    @property
    def time(self) -> datetime:
        """Canonical bar timestamp = completion (close) time."""
        return self.close_time


@dataclass(frozen=True)
class VolatilityBar:
    instrument: str
    price_basis: str
    method: str
    threshold_mode: str
    threshold_pips: float  # effective threshold used for THIS bar
    open: float
    high: float
    low: float
    close: float
    volume: int
    open_time: datetime
    close_time: datetime
    source_count: int
    source_start_time: datetime
    source_end_time: datetime
    movement_pips: float
    completion_reason: str  # "volatility" | "incomplete"
    thresholds_crossed: int
    overshoot_pips: float
    incomplete: bool = False

    @property
    def time(self) -> datetime:
        """Canonical bar timestamp = completion (close) time."""
        return self.close_time


# --------------------------------------------------------------------------- #
# Shared input normalisation
# --------------------------------------------------------------------------- #


def _basis_ohlc(
    candle: Candle, basis: PriceBasis
) -> tuple[Decimal, Decimal, Decimal, Decimal]:
    """Extract (open, high, low, close) Decimals for the chosen price basis.

    ``mid`` falls back to ``(bid + ask) / 2`` per field, mirroring
    ``CandleFrame.from_candles``. Missing required components raise ValueError.
    """
    if basis == "bid":
        fields = (candle.bid_o, candle.bid_h, candle.bid_l, candle.bid_c)
    elif basis == "ask":
        fields = (candle.ask_o, candle.ask_h, candle.ask_l, candle.ask_c)
    else:
        fields = (candle.mid_o, candle.mid_h, candle.mid_l, candle.mid_c)
        if any(component is None for component in fields):
            bid = (candle.bid_o, candle.bid_h, candle.bid_l, candle.bid_c)
            ask = (candle.ask_o, candle.ask_h, candle.ask_l, candle.ask_c)
            if any(b is None for b in bid) or any(a is None for a in ask):
                raise ValueError(f"missing mid (and bid/ask fallback) price at {candle.time}")
            return tuple((b + a) / 2 for b, a in zip(bid, ask, strict=True))  # type: ignore[return-value]
    if any(component is None for component in fields):
        raise ValueError(f"missing {basis} price at {candle.time}")
    return tuple(fields)  # type: ignore[return-value]


def _ordered_rows(
    candles: Iterable[Candle],
    instrument: str,
    *,
    require_sorted: bool,
    duplicate_policy: DuplicatePolicy,
) -> list[Candle]:
    """Validate instrument homogeneity, ordering, and duplicate timestamps.

    Returns the rows in strictly increasing time order. Under the defaults
    (require_sorted, reject duplicates) nothing is silently reordered/dropped.
    """
    rows = list(candles)
    if not rows:
        return rows
    instruments = {row.instrument for row in rows}
    if instruments != {instrument}:
        raise ValueError(
            f"input instruments {sorted(instruments)} do not match config instrument {instrument!r}"
        )
    if require_sorted:
        for prev, cur in zip(rows, rows[1:], strict=False):
            if cur.time < prev.time:
                raise ValueError(f"input not sorted: {cur.time} follows {prev.time}")
    else:
        rows = sorted(rows, key=lambda row: row.time)

    # Duplicate-timestamp handling.
    seen: dict[datetime, int] = {}
    for row in rows:
        seen[row.time] = seen.get(row.time, 0) + 1
    duplicates = [ts for ts, count in seen.items() if count > 1]
    if duplicates:
        if duplicate_policy == "reject":
            raise ValueError(f"duplicate source timestamps: {sorted(duplicates)[:5]}")
        deduped: dict[datetime, Candle] = {}
        for row in rows:
            if duplicate_policy == "keep_first" and row.time in deduped:
                continue
            deduped[row.time] = row  # keep_last overwrites; keep_first kept above
        rows = [deduped[ts] for ts in sorted(deduped)]
    return rows


def _streaming_validate(
    candles: Iterable[Candle],
    instrument: str,
    *,
    duplicate_policy: DuplicatePolicy,
) -> Iterator[Candle]:
    """Memory-bounded validation for already-time-ordered input streams.

    Yields rows one at a time (peak memory = one buffered row), enforcing
    instrument homogeneity and non-decreasing time, and applying the duplicate
    policy via single-row lookahead. Unlike :func:`_ordered_rows` it cannot
    globally re-sort, so the input MUST be time-ordered (out-of-order raises).
    Used by the ``stream_*`` builders for full-corpus folds.
    """
    prev: Candle | None = None
    for row in candles:
        if row.instrument != instrument:
            raise ValueError(
                f"input instrument {row.instrument!r} does not match config instrument {instrument!r}"
            )
        if prev is None:
            prev = row
            continue
        if row.time < prev.time:
            raise ValueError(f"input not sorted: {row.time} follows {prev.time}")
        if row.time == prev.time:
            if duplicate_policy == "reject":
                raise ValueError(f"duplicate source timestamp: {row.time}")
            if duplicate_policy == "keep_last":
                prev = row
            # keep_first: drop current, retain buffered prev
            continue
        yield prev
        prev = row
    if prev is not None:
        yield prev


# --------------------------------------------------------------------------- #
# Range bars
# --------------------------------------------------------------------------- #


def build_range_bars(candles: Iterable[Candle], config: RangeBarConfig) -> list[RangeBar]:
    """Fold M1 candles into range bars per RANGE_BAR_CONSTRUCTION_SPEC.md.

    Materialises and validates the full input (supports ``require_sorted=False``
    re-sort and all duplicate policies). For large corpora use
    :func:`stream_range_bars`.
    """
    rows = _ordered_rows(
        candles,
        config.instrument,
        require_sorted=config.require_sorted,
        duplicate_policy=config.duplicate_policy,
    )
    return list(_fold_range_bars(iter(rows), config))


def stream_range_bars(candles: Iterable[Candle], config: RangeBarConfig) -> Iterator[RangeBar]:
    """Memory-bounded range-bar fold over an already-time-ordered stream.

    Validates incrementally (single-row buffer); the input MUST be time-ordered.
    Yields completed bars as they form, so a multi-million-row corpus folds in
    ~one-chunk peak memory.
    """
    rows = _streaming_validate(candles, config.instrument, duplicate_policy=config.duplicate_policy)
    yield from _fold_range_bars(rows, config)


def _fold_range_bars(rows: Iterator[Candle], config: RangeBarConfig) -> Iterator[RangeBar]:
    psize = pip_size(config.instrument)
    threshold = Decimal(str(config.threshold_pips))

    bar_open: Decimal | None = None
    high = low = close = Decimal(0)
    volume = 0
    open_time: datetime | None = None
    end_time: datetime | None = None
    source_count = 0

    for row in rows:
        o, h, lo, c = _basis_ohlc(row, config.price_basis)
        if bar_open is None:
            bar_open, high, low, close = o, h, lo, c
            volume = row.volume
            open_time = end_time = row.time
            source_count = 1
        else:
            high = max(high, h)
            low = min(low, lo)
            close = c
            volume += row.volume
            end_time = row.time
            source_count += 1

        up_span = (high - bar_open) / psize
        down_span = (bar_open - low) / psize
        move = max(up_span, down_span)
        if move >= threshold:
            reason = "range_up" if up_span >= down_span else "range_down"
            yield RangeBar(
                instrument=config.instrument,
                price_basis=config.price_basis,
                threshold_pips=float(threshold),
                open=float(bar_open),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=volume,
                open_time=open_time,  # type: ignore[arg-type]
                close_time=row.time,
                source_count=source_count,
                source_start_time=open_time,  # type: ignore[arg-type]
                source_end_time=row.time,
                completion_reason=reason,
                thresholds_crossed=int(move // threshold),
                overshoot_pips=float(move - threshold),
                incomplete=False,
            )
            bar_open = None

    if bar_open is not None and config.emit_incomplete_final:
        up_span = (high - bar_open) / psize
        down_span = (bar_open - low) / psize
        yield RangeBar(
            instrument=config.instrument,
            price_basis=config.price_basis,
            threshold_pips=float(threshold),
            open=float(bar_open),
            high=float(high),
            low=float(low),
            close=float(close),
            volume=volume,
            open_time=open_time,  # type: ignore[arg-type]
            close_time=end_time,  # type: ignore[arg-type]
            source_count=source_count,
            source_start_time=open_time,  # type: ignore[arg-type]
            source_end_time=end_time,  # type: ignore[arg-type]
            completion_reason="incomplete",
            thresholds_crossed=0,
            overshoot_pips=float(max(up_span, down_span) - threshold),
            incomplete=True,
        )


# --------------------------------------------------------------------------- #
# Volatility bars
# --------------------------------------------------------------------------- #


def build_volatility_bars(
    candles: Iterable[Candle], config: VolatilityBarConfig
) -> list[VolatilityBar]:
    """Fold M1 candles into volatility bars per VOLATILITY_BAR_CONSTRUCTION_SPEC.md.

    Materialises and validates the full input. For large corpora use
    :func:`stream_volatility_bars`.
    """
    rows = _ordered_rows(
        candles,
        config.instrument,
        require_sorted=config.require_sorted,
        duplicate_policy=config.duplicate_policy,
    )
    return list(_fold_volatility_bars(iter(rows), config))


def stream_volatility_bars(
    candles: Iterable[Candle], config: VolatilityBarConfig
) -> Iterator[VolatilityBar]:
    """Memory-bounded volatility-bar fold over an already-time-ordered stream."""
    rows = _streaming_validate(candles, config.instrument, duplicate_policy=config.duplicate_policy)
    yield from _fold_volatility_bars(rows, config)


def _fold_volatility_bars(
    rows: Iterator[Candle], config: VolatilityBarConfig
) -> Iterator[VolatilityBar]:
    psize = pip_size(config.instrument)
    atr_window = config.atr_window or 0
    atr_multiple = Decimal(str(config.atr_multiple)) if config.atr_multiple is not None else None

    # Rolling window of prior COMPLETED M1 true ranges (pips) for atr_scaled.
    tr_window: list[Decimal] = []

    bar_open: Decimal | None = None
    high = low = close = Decimal(0)
    volume = 0
    open_time: datetime | None = None
    end_time: datetime | None = None
    source_count = 0
    movement = Decimal(0)
    effective_threshold: Decimal | None = None
    prev_close: Decimal | None = None  # carries across bar boundaries

    for row in rows:
        o, h, lo, c = _basis_ohlc(row, config.price_basis)

        # Per-row movement increment (pips), using only this row + prev close.
        ref_close = prev_close if prev_close is not None else o
        tr_pips = max(h - lo, abs(h - ref_close), abs(lo - ref_close)) / psize
        increment = tr_pips if config.method == "true_range" else abs(c - ref_close) / psize

        if bar_open is None:
            # Resolve the threshold for this forming bar from PRIOR data only.
            if config.threshold_mode == "fixed":
                effective_threshold = Decimal(str(config.threshold_pips))
            elif len(tr_window) < atr_window:
                # Warm-up: not enough prior completed rows. Record this row in
                # the prior-window and skip (no bar opens yet).
                tr_window.append(tr_pips)
                if len(tr_window) > atr_window:
                    tr_window.pop(0)
                prev_close = c
                continue
            else:
                atr_prior = sum(tr_window, Decimal(0)) / Decimal(len(tr_window))
                effective_threshold = atr_multiple * atr_prior  # type: ignore[operator]
            bar_open, high, low, close = o, h, lo, c
            volume = row.volume
            open_time = end_time = row.time
            source_count = 1
            movement = increment
        else:
            high = max(high, h)
            low = min(low, lo)
            close = c
            volume += row.volume
            end_time = row.time
            source_count += 1
            movement += increment

        assert effective_threshold is not None
        if movement >= effective_threshold:
            yield VolatilityBar(
                instrument=config.instrument,
                price_basis=config.price_basis,
                method=config.method,
                threshold_mode=config.threshold_mode,
                threshold_pips=float(effective_threshold),
                open=float(bar_open),
                high=float(high),
                low=float(low),
                close=float(close),
                volume=volume,
                open_time=open_time,  # type: ignore[arg-type]
                close_time=row.time,
                source_count=source_count,
                source_start_time=open_time,  # type: ignore[arg-type]
                source_end_time=row.time,
                movement_pips=float(movement),
                completion_reason="volatility",
                thresholds_crossed=int(movement // effective_threshold),
                overshoot_pips=float(movement - effective_threshold),
                incomplete=False,
            )
            bar_open = None
            effective_threshold = None

        # This row is now a completed prior row for any future atr_scaled window.
        tr_window.append(tr_pips)
        if len(tr_window) > atr_window:
            tr_window.pop(0)
        prev_close = c

    if bar_open is not None and config.emit_incomplete_final:
        yield VolatilityBar(
            instrument=config.instrument,
            price_basis=config.price_basis,
            method=config.method,
            threshold_mode=config.threshold_mode,
            threshold_pips=float(effective_threshold) if effective_threshold is not None else 0.0,
            open=float(bar_open),
            high=float(high),
            low=float(low),
            close=float(close),
            volume=volume,
            open_time=open_time,  # type: ignore[arg-type]
            close_time=end_time,  # type: ignore[arg-type]
            source_count=source_count,
            source_start_time=open_time,  # type: ignore[arg-type]
            source_end_time=end_time,  # type: ignore[arg-type]
            movement_pips=float(movement),
            completion_reason="incomplete",
            thresholds_crossed=0,
            overshoot_pips=0.0,
            incomplete=True,
        )
