"""Walk-forward / rolling-window split helper."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class WalkForwardSplit:
    train_start: datetime
    train_end: datetime
    test_start: datetime
    test_end: datetime


def walk_forward_splits(
    start: datetime,
    end: datetime,
    train_months: int,
    test_months: int,
    roll_months: int,
) -> list[WalkForwardSplit]:
    splits: list[WalkForwardSplit] = []
    cursor = start
    while True:
        train_end = cursor + timedelta(days=30 * train_months)
        test_end = train_end + timedelta(days=30 * test_months)
        if test_end > end:
            break
        splits.append(
            WalkForwardSplit(
                train_start=cursor,
                train_end=train_end,
                test_start=train_end,
                test_end=test_end,
            )
        )
        cursor = cursor + timedelta(days=30 * roll_months)
    return splits
