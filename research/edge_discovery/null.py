"""Random-entry null baseline for the edge-discovery lab.

Compares a study's per-signal returns against a sample-matched random
baseline. The baseline draws ``n_trades`` random entry timestamps from
the candle frame (with the same forward window length the study used)
and computes their log-returns. Repeated across ``len(seeds)`` seeds,
the per-seed means form the null distribution.

The output is intentionally descriptive: per-seed means, a bootstrap-
style mean / std, and the gap between the study's mean and the null's
mean. The lab does not publish p-values — it reports the gap and a
qualitative band (within-null, slightly-above-null, materially-above-
null) so studies don't get cited as significance tests.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from research.edge_discovery.windows import Side


@dataclass(frozen=True)
class NullBaseline:
    """Random-entry null result for a sample-matched window.

    ``per_seed_means`` is one mean per seed. ``mean_of_means`` is the
    grand mean across seeds; ``std_of_means`` is the std across seeds.
    """

    per_seed_means: pd.Series
    mean_of_means: float
    std_of_means: float
    n_trades_per_seed: int
    window_bars: int
    seeds_used: tuple[int, ...]
    extras: dict[str, object] = field(default_factory=dict)


def random_null_baseline(
    frame: pd.DataFrame,
    *,
    n_trades: int,
    window_bars: int,
    seeds: Iterable[int] = range(20),
    side: Side = Side.LONG,
    apply_cost_overlay_fn=None,
    instrument: str | None = None,
    cost_kwargs: dict | None = None,
) -> NullBaseline:
    """Build a random-entry null distribution.

    For each seed: draw ``n_trades`` random entry-bar indices (uniform
    over bars that have at least ``window_bars`` of forward data),
    compute the signed log-return over that window, optionally apply
    the cost overlay, and record the mean.

    If ``apply_cost_overlay_fn`` is provided (typically
    ``research.edge_discovery.costs.apply_cost_overlay``) and
    ``instrument`` is supplied, post-cost means are returned; otherwise
    pre-cost.
    """
    if "close" not in frame.columns:
        raise ValueError("frame must have a 'close' column — use load_candles_csv()")
    if n_trades < 1:
        raise ValueError(f"n_trades must be >= 1, got {n_trades}")
    if window_bars < 1:
        raise ValueError(f"window_bars must be >= 1, got {window_bars}")

    closes = frame["close"].to_numpy(dtype=float)
    n = len(closes)
    max_entry = n - window_bars - 1
    if max_entry < 0:
        raise ValueError(
            f"frame has only {n} bars; need at least window_bars+2 = {window_bars + 2}"
        )

    sign = float(side.value)
    seed_tuple = tuple(int(s) for s in seeds)
    per_seed = []
    for s in seed_tuple:
        rng = np.random.default_rng(s)
        entries = rng.integers(0, max_entry + 1, size=n_trades)
        ep = closes[entries]
        xp = closes[entries + window_bars]
        good = (ep > 0) & (xp > 0)
        if not good.any():
            per_seed.append(0.0)
            continue
        log_ret = np.log(xp[good] / ep[good]) * sign
        if apply_cost_overlay_fn is not None and instrument is not None:
            df = pd.DataFrame({
                "entry_price": ep[good],
                "log_return": log_ret,
                "bars_held": np.full(int(good.sum()), window_bars, dtype=int),
            })
            kwargs = cost_kwargs or {}
            df2 = apply_cost_overlay_fn(df, instrument, **kwargs)
            per_seed.append(float(df2["log_return_post_cost"].mean()))
        else:
            per_seed.append(float(log_ret.mean()))

    arr = pd.Series(per_seed, index=list(seed_tuple), name="seed_mean")
    return NullBaseline(
        per_seed_means=arr,
        mean_of_means=float(arr.mean()),
        std_of_means=float(arr.std(ddof=1)) if len(arr) > 1 else 0.0,
        n_trades_per_seed=int(n_trades),
        window_bars=int(window_bars),
        seeds_used=seed_tuple,
    )


def compare_to_null(study_mean: float, null: NullBaseline) -> dict[str, object]:
    """Descriptive comparison band — never a significance test.

    Returns a dict with ``gap`` (study - null mean), ``gap_in_null_stds``
    (how many null stds the gap spans), and a qualitative ``band``:

      - ``"within_null"`` if |gap| <= 1 * null_std
      - ``"slightly_above_null"`` if gap is +1..+2 null stds
      - ``"materially_above_null"`` if gap is > +2 null stds
      - ``"slightly_below_null"`` if gap is -1..-2 null stds
      - ``"materially_below_null"`` if gap is < -2 null stds
      - ``"null_collapsed"`` if null_std is 0 (e.g. single seed)

    These bands are descriptive shorthand for human review, not
    statistical significance. The lab explicitly does not multiple-
    test-correct and does not control family-wise error.
    """
    gap = float(study_mean) - null.mean_of_means
    if null.std_of_means == 0:
        return {
            "gap": gap,
            "gap_in_null_stds": None,
            "band": "null_collapsed",
        }
    stds = gap / null.std_of_means
    if stds > 2.0:
        band = "materially_above_null"
    elif stds > 1.0:
        band = "slightly_above_null"
    elif stds < -2.0:
        band = "materially_below_null"
    elif stds < -1.0:
        band = "slightly_below_null"
    else:
        band = "within_null"
    return {"gap": gap, "gap_in_null_stds": float(stds), "band": band}
