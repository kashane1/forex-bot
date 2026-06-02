"""Pure pagination/windowing helpers for the crypto derivatives backfill.

No network I/O here — the script owns the httpx loop; these helpers are unit-
testable and deterministic. Time is in epoch milliseconds (UTC).
"""

from __future__ import annotations

# Conservative per-call spans (ms) below each venue's observed per-call cap.
HOUR_MS = 3_600_000
DAY_MS = 86_400_000
# Deribit funding ≈744 hourly rows/call → 30-day windows are safe.
DERIBIT_FUNDING_SPAN_MS = 30 * DAY_MS
# Deribit chart returned 1441 ticks for 60d@1H → 30-day 1H windows are safe.
DERIBIT_CHART_1H_SPAN_MS = 30 * DAY_MS
# 1D chart returned full multi-year history in one call → one wide window.
DERIBIT_CHART_1D_SPAN_MS = 4000 * DAY_MS


def chunk_time_windows(start_ms: int, end_ms: int, span_ms: int) -> list[tuple[int, int]]:
    """Split ``[start_ms, end_ms]`` into ascending ``(s, e)`` windows of ``span_ms``.

    The final window is clamped to ``end_ms``. Raises if inputs are invalid.
    """
    if span_ms <= 0:
        raise ValueError("span_ms must be positive")
    if end_ms < start_ms:
        raise ValueError("end_ms must be >= start_ms")
    windows: list[tuple[int, int]] = []
    cursor = start_ms
    while cursor <= end_ms:
        win_end = min(cursor + span_ms - 1, end_ms)
        windows.append((cursor, win_end))
        cursor = win_end + 1
    return windows


def expected_hourly_rows(start_ms: int, end_ms: int) -> int:
    """Expected count of hourly slots in ``[start_ms, end_ms]`` (inclusive grid)."""
    if end_ms < start_ms:
        return 0
    return int((end_ms - start_ms) // HOUR_MS) + 1
