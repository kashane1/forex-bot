"""H16 overshoot-exhaustion fade — front-gate screen helpers (diagnostic-only).

Pure, DB-free functions that measure **conditional forward returns** after
non-time-bar completions, bucketed by completion **overshoot**, for the
`research-non-time-bar-overshoot-frontgate-001` screen. This is a
*conditional-distribution measurement*, not a strategy: there are no positions,
stops, sizing, PnL, equity, or signals here, and nothing is approved.

The "fade return" convention (see H16_OVERSHOOT_EXHAUSTION_HYPOTHESIS.md):
``fade_k(i) = −completion_dir(i) × (mid_close[i+k] − mid_close[i])`` in pips —
**positive ⇒ price reverted** against the completion move (the hypothesised
exhaustion); negative ⇒ continuation.

All functions are deterministic (the permutation null takes an explicit seed) so they
are unit-testable without a database. Impure DB streaming + bar building lives in
``scripts/screen_h16_overshoot_exhaustion.py``.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

BUCKET_NAMES = ("small", "medium", "large", "extreme")


# --------------------------------------------------------------------------- #
# Forward fade returns
# --------------------------------------------------------------------------- #


def to_pips(price_diff: float, pip_size: float) -> float:
    """Convert a price difference to pips."""
    if pip_size <= 0:
        raise ValueError("pip_size must be positive")
    return price_diff / pip_size


def fade_returns(
    closes: list[float], dirs: list[int], pip_size: float, horizon: int
) -> list[float | None]:
    """Per-bar fade return in pips at the given horizon (None where it runs off the end).

    ``fade = −dir[i] × (closes[i+horizon] − closes[i]) / pip_size``.
    """
    if horizon < 1:
        raise ValueError("horizon must be >= 1")
    if len(closes) != len(dirs):
        raise ValueError("closes and dirs must be the same length")
    n = len(closes)
    out: list[float | None] = []
    for i in range(n):
        j = i + horizon
        if j >= n:
            out.append(None)
            continue
        out.append(-dirs[i] * (closes[j] - closes[i]) / pip_size)
    return out


# --------------------------------------------------------------------------- #
# Bucketing by overshoot
# --------------------------------------------------------------------------- #


def quantile_edges(values: list[float]) -> tuple[float, float, float]:
    """Quartile edges (q25, q50, q75) of a value list (>= 2 values)."""
    if len(values) < 2:
        raise ValueError("need >= 2 values for quartile edges")
    q = statistics.quantiles(sorted(values), n=4)
    return (q[0], q[1], q[2])


def bucket_label(value: float, edges: tuple[float, float, float]) -> str:
    """Map a value to small/medium/large/extreme by the quartile edges."""
    q25, q50, q75 = edges
    if value <= q25:
        return "small"
    if value <= q50:
        return "medium"
    if value <= q75:
        return "large"
    return "extreme"


def top_tail_threshold(values: list[float], frac: float = 0.05) -> float:
    """Value at the (1−frac) quantile — the lower edge of the top ``frac`` tail."""
    if not 0.0 < frac < 1.0:
        raise ValueError("frac must be in (0, 1)")
    if not values:
        raise ValueError("values must be non-empty")
    ordered = sorted(values)
    idx = min(len(ordered) - 1, max(0, math.ceil((1.0 - frac) * len(ordered)) - 1))
    return ordered[idx]


# --------------------------------------------------------------------------- #
# Conditional statistics
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class BucketStats:
    n: int
    mean: float | None
    median: float | None
    std: float | None
    sem: float | None
    reversion_rate: float | None  # fraction of fade returns > 0

    def as_dict(self) -> dict:
        return {
            "n": self.n,
            "mean": self.mean,
            "median": self.median,
            "std": self.std,
            "sem": self.sem,
            "reversion_rate": self.reversion_rate,
        }


def bucket_stats(fades: list[float]) -> BucketStats:
    """Summary stats of a list of fade returns (None-safe for empty/singleton)."""
    xs = [x for x in fades if x is not None]
    n = len(xs)
    if n == 0:
        return BucketStats(0, None, None, None, None, None)
    mean = statistics.fmean(xs)
    median = statistics.median(xs)
    std = statistics.pstdev(xs) if n >= 2 else 0.0
    sem = (std / math.sqrt(n)) if (std is not None and n >= 1) else None
    reversion_rate = sum(1 for x in xs if x > 0) / n
    return BucketStats(
        n=n,
        mean=round(mean, 5),
        median=round(median, 5),
        std=round(std, 5),
        sem=round(sem, 5) if sem is not None else None,
        reversion_rate=round(reversion_rate, 4),
    )


def autocorr_lag1(values: list[float]) -> float | None:
    """Lag-1 autocorrelation of a series (None if < 3 points or zero variance)."""
    xs = [v for v in values if v is not None]
    n = len(xs)
    if n < 3:
        return None
    mean = statistics.fmean(xs)
    denom = sum((x - mean) ** 2 for x in xs)
    if denom == 0:
        return None
    num = sum((xs[i] - mean) * (xs[i + 1] - mean) for i in range(n - 1))
    return round(num / denom, 4)


def conditional_followon_rate(labels: list[str], target: tuple[str, ...]) -> dict:
    """P(next label in target | current label in target) vs the base rate of target.

    Used to test whether large/extreme overshoots **cluster** (a large overshoot being
    more likely to be followed by another).
    """
    n = len(labels)
    if n < 2:
        return {"base_rate": None, "conditional_rate": None, "lift": None, "n_target": 0}
    target_set = set(target)
    base = sum(1 for x in labels if x in target_set) / n
    cur_target = [i for i in range(n - 1) if labels[i] in target_set]
    if not cur_target:
        return {"base_rate": round(base, 4), "conditional_rate": None, "lift": None, "n_target": 0}
    follow = sum(1 for i in cur_target if labels[i + 1] in target_set) / len(cur_target)
    lift = (follow / base) if base > 0 else None
    return {
        "base_rate": round(base, 4),
        "conditional_rate": round(follow, 4),
        "lift": round(lift, 4) if lift is not None else None,
        "n_target": len(cur_target),
    }


# --------------------------------------------------------------------------- #
# Permutation (shuffle) null
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class PermutationNull:
    observed_mean: float
    n_group: int
    null_mean: float
    null_p05: float
    null_p95: float
    pct_rank: float  # fraction of null draws <= observed (0..1)
    one_sided_p_ge: float  # P(null >= observed) — small ⇒ observed unusually high
    draws: int

    def as_dict(self) -> dict:
        return {
            "observed_mean": round(self.observed_mean, 5),
            "n_group": self.n_group,
            "null_mean": round(self.null_mean, 5),
            "null_p05": round(self.null_p05, 5),
            "null_p95": round(self.null_p95, 5),
            "pct_rank": round(self.pct_rank, 4),
            "one_sided_p_ge": round(self.one_sided_p_ge, 4),
            "draws": self.draws,
        }


def permutation_null_group_mean(
    fades: list[float], in_group: list[bool], *, draws: int, seed: int
) -> PermutationNull:
    """Permutation null for "is the group's mean fade unusually high?".

    The group is the set of bars flagged ``in_group`` (e.g. large+extreme overshoot).
    The null shuffles which fade returns are assigned to the group (breaking the
    overshoot↔return link), recomputing the group-size mean ``draws`` times with a
    fixed ``seed``. Returns the observed mean's position in that null distribution.
    """
    xs = [(f, g) for f, g in zip(fades, in_group, strict=True) if f is not None]
    if not xs:
        raise ValueError("no non-None fades")
    vals = [f for f, _ in xs]
    n_group = sum(1 for _, g in xs if g)
    if n_group == 0 or n_group == len(vals):
        raise ValueError("group must be a non-trivial subset")
    observed = statistics.fmean([f for f, g in xs if g])

    rng = random.Random(seed)
    null_means: list[float] = []
    for _ in range(draws):
        sample = rng.sample(vals, n_group)
        null_means.append(statistics.fmean(sample))
    null_means.sort()
    null_mean = statistics.fmean(null_means)
    p05 = null_means[max(0, math.ceil(0.05 * draws) - 1)]
    p95 = null_means[min(draws - 1, math.ceil(0.95 * draws) - 1)]
    le = sum(1 for m in null_means if m <= observed) / draws
    ge = sum(1 for m in null_means if m >= observed) / draws
    return PermutationNull(
        observed_mean=observed,
        n_group=n_group,
        null_mean=null_mean,
        null_p05=p05,
        null_p95=p95,
        pct_rank=le,
        one_sided_p_ge=ge,
        draws=draws,
    )
