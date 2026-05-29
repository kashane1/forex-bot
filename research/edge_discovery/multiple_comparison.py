"""Multiple-comparison / selection-noise sanity checks for the lab.

When a campaign tries N parameter variants and reports the best one, the best
is upward-biased: even with *no* real differences between variants, the maximum
of N noisy estimates is elevated. This module asks "is the best variant
meaningfully better than what best-of-N selection would produce by chance?" and
"does the best variant survive dropping a pair or a time block?".

It works on a **matrix result table** — one row per variant, with a metric
column (e.g. ``expectancy_r``) and a label column. This is exactly the shape of
``research/campaign_025/train_matrix/train_matrix_metrics.csv`` and its C026
counterpart, so the retrospective can run it directly.

Diagnostics:
  * variant count, best, median, best-minus-median spread
  * best-vs-null (gap to a supplied null reference, e.g. the C011 baseline)
  * a bootstrap **best-of-N-under-noise** reference: resample N variant metrics
    from a null centred at the null reference (or the median) with the observed
    cross-variant dispersion, and compare the real best to the distribution of
    the resampled maxima — ``prob_best_le_null_max`` is how often noise alone
    produces a best at least this good
  * ``deflated_improvement`` = best − mean(resampled maxima)
  * optional pair-holdout and time-block-holdout stability for the best variant

Descriptive flags (never a verdict):
  * ``ROBUST_MATRIX_SIGNAL`` — best clears the null *and* the best-of-N band
  * ``LIKELY_SELECTION_NOISE`` — best is within the best-of-N noise band
  * ``FRAGILE_SINGLE_PAIR_RESULT`` — best flips sign when one pair is dropped
  * ``FRAGILE_TIME_BLOCK_RESULT`` — best flips sign when one time block is dropped
  * ``TOO_MANY_VARIANTS_FOR_EVIDENCE`` — N exceeds ``too_many_variants``
  * ``INCONCLUSIVE`` — best does not even reach the null reference

Deterministic given ``seed``. Import-isolated: numpy / pandas only.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

MATRIX_FLAGS = (
    "ROBUST_MATRIX_SIGNAL",
    "LIKELY_SELECTION_NOISE",
    "FRAGILE_SINGLE_PAIR_RESULT",
    "FRAGILE_TIME_BLOCK_RESULT",
    "TOO_MANY_VARIANTS_FOR_EVIDENCE",
    "INCONCLUSIVE",
)


@dataclass(frozen=True)
class HoldoutStability:
    """Leave-one-group-out stability for the best variant."""

    kind: str  # "pair" | "time_block"
    full_value: float
    leave_one_out: dict[str, float]
    min_value: float
    max_value: float
    sign_flips: bool
    dominant_group: str | None

    def to_dict(self) -> dict[str, object]:
        return {
            "kind": self.kind,
            "full_value": self.full_value,
            "leave_one_out": dict(self.leave_one_out),
            "min_value": self.min_value,
            "max_value": self.max_value,
            "sign_flips": self.sign_flips,
            "dominant_group": self.dominant_group,
        }


@dataclass(frozen=True)
class MatrixSanityResult:
    metric: str
    higher_is_better: bool
    n_variants: int
    best_label: str
    best_value: float
    median_value: float
    best_minus_median: float
    null_reference: float | None
    best_vs_null: float | None
    expected_max_under_null: float
    expected_max_p95: float
    deflated_improvement: float
    prob_best_le_null_max: float
    pair_holdout: HoldoutStability | None
    time_block_holdout: HoldoutStability | None
    fragility_score: float
    flags: list[str]
    seed: int
    n_resample: int
    notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return {
            "metric": self.metric,
            "higher_is_better": self.higher_is_better,
            "n_variants": self.n_variants,
            "best_label": self.best_label,
            "best_value": self.best_value,
            "median_value": self.median_value,
            "best_minus_median": self.best_minus_median,
            "null_reference": self.null_reference,
            "best_vs_null": self.best_vs_null,
            "expected_max_under_null": self.expected_max_under_null,
            "expected_max_p95": self.expected_max_p95,
            "deflated_improvement": self.deflated_improvement,
            "prob_best_le_null_max": self.prob_best_le_null_max,
            "pair_holdout": self.pair_holdout.to_dict() if self.pair_holdout else None,
            "time_block_holdout": self.time_block_holdout.to_dict() if self.time_block_holdout else None,
            "fragility_score": self.fragility_score,
            "flags": list(self.flags),
            "seed": self.seed,
            "n_resample": self.n_resample,
            "notes": list(self.notes),
        }


def holdout_stability(
    group_values: Mapping[str, float],
    *,
    kind: str,
    weights: Mapping[str, float] | None = None,
    higher_is_better: bool = True,
) -> HoldoutStability:
    """Leave-one-group-out stability of a (weighted) mean over groups.

    ``group_values`` maps each group (pair or time block) to the best variant's
    metric on that group; ``weights`` (e.g. trade counts) makes the aggregate a
    weighted mean — defaults to equal weights. ``sign_flips`` is True when any
    leave-one-out aggregate has the opposite sign of the full aggregate (a
    single-group dependency).
    """
    groups = list(group_values)
    if not groups:
        raise ValueError("group_values is empty")
    w = {g: float(weights[g]) if weights and g in weights else 1.0 for g in groups}

    def _wmean(keys: list[str]) -> float:
        tot = sum(w[g] for g in keys)
        if tot <= 0:
            return 0.0
        return sum(group_values[g] * w[g] for g in keys) / tot

    full = _wmean(groups)
    loo: dict[str, float] = {}
    for g in groups:
        rest = [x for x in groups if x != g]
        loo[g] = _wmean(rest) if rest else full
    vals = list(loo.values())
    sign_flips = any((full > 0 > v) or (full < 0 < v) for v in vals)
    # The group whose removal moves the aggregate most adversely.
    adverse = (lambda v: full - v) if higher_is_better else (lambda v: v - full)
    dominant = max(loo, key=lambda g: adverse(loo[g])) if loo else None
    return HoldoutStability(
        kind=kind,
        full_value=full,
        leave_one_out=loo,
        min_value=min(vals),
        max_value=max(vals),
        sign_flips=sign_flips,
        dominant_group=dominant,
    )


def _expected_max_under_null(
    values: np.ndarray,
    *,
    n_variants: int,
    center: float,
    sigma: float,
    n_resample: int,
    seed: int,
) -> tuple[float, float, np.ndarray]:
    """Bootstrap the maximum of ``n_variants`` draws from N(center, sigma).

    Returns ``(mean_max, p95_max, maxima)``. When sigma is 0 (degenerate), the
    maxima collapse to ``center``.
    """
    rng = np.random.default_rng(seed)
    if sigma <= 0:
        maxima = np.full(n_resample, center)
    else:
        draws = rng.normal(center, sigma, size=(n_resample, n_variants))
        maxima = draws.max(axis=1)
    return float(maxima.mean()), float(np.quantile(maxima, 0.95)), maxima


def matrix_sanity(
    table: pd.DataFrame,
    *,
    metric_col: str,
    label_col: str,
    higher_is_better: bool = True,
    null_reference: float | None = None,
    null_std: float | None = None,
    best_group_values: Mapping[str, float] | None = None,
    best_group_weights: Mapping[str, float] | None = None,
    group_kind: str = "pair",
    time_block_values: Mapping[str, float] | None = None,
    time_block_weights: Mapping[str, float] | None = None,
    n_resample: int = 2000,
    seed: int = 0,
    too_many_variants: int = 50,
) -> MatrixSanityResult:
    """Selection-noise + fragility diagnostics for a matrix-result table.

    ``best_group_values`` (and optionally ``time_block_values``) drive the
    holdout-fragility checks for the selected best variant; omit them to skip
    those checks (e.g. when per-pair breakdowns are unavailable).
    """
    if table is None or table.empty:
        raise ValueError("table is empty; nothing to check")
    for col in (metric_col, label_col):
        if col not in table.columns:
            raise ValueError(f"table missing column {col!r}")
    vals = table[metric_col].astype(float).to_numpy()
    n = len(vals)
    best_idx = int(np.argmax(vals)) if higher_is_better else int(np.argmin(vals))
    best_value = float(vals[best_idx])
    best_label = str(table[label_col].iloc[best_idx])
    median_value = float(np.median(vals))
    best_minus_median = best_value - median_value if higher_is_better else median_value - best_value

    center = null_reference if null_reference is not None else median_value
    sigma = null_std if null_std is not None else (float(np.std(vals, ddof=1)) if n > 1 else 0.0)
    # Work in "higher is better" space for the max bootstrap.
    if higher_is_better:
        b_val, b_center = best_value, center
    else:
        b_val, b_center, sigma = -best_value, -center, sigma
    exp_mean, exp_p95, maxima = _expected_max_under_null(
        vals, n_variants=n, center=b_center, sigma=sigma, n_resample=n_resample, seed=seed
    )
    prob_best_le_null_max = float((maxima >= b_val).mean())
    deflated = b_val - exp_mean

    best_vs_null = None
    if null_reference is not None:
        best_vs_null = (best_value - null_reference) if higher_is_better else (null_reference - best_value)

    pair_holdout = None
    if best_group_values:
        pair_holdout = holdout_stability(
            best_group_values, kind=group_kind, weights=best_group_weights,
            higher_is_better=higher_is_better,
        )
    time_block_holdout = None
    if time_block_values:
        time_block_holdout = holdout_stability(
            time_block_values, kind="time_block", weights=time_block_weights,
            higher_is_better=higher_is_better,
        )

    flags, fragility = _matrix_flags(
        best_vs_null=best_vs_null,
        prob_best_le_null_max=prob_best_le_null_max,
        deflated=deflated,
        n=n,
        too_many_variants=too_many_variants,
        pair_holdout=pair_holdout,
        time_block_holdout=time_block_holdout,
    )

    notes: list[str] = []
    if null_std is None:
        notes.append(
            "null_std not supplied; used cross-variant dispersion as the noise scale "
            "(conservative — treats all variant spread as noise)"
        )
    if best_group_values is None:
        notes.append("pair-holdout skipped: no per-pair values supplied")
    if time_block_values is None:
        notes.append("time-block-holdout skipped: no per-time-block values supplied")

    return MatrixSanityResult(
        metric=metric_col,
        higher_is_better=higher_is_better,
        n_variants=n,
        best_label=best_label,
        best_value=best_value,
        median_value=median_value,
        best_minus_median=best_minus_median,
        null_reference=null_reference,
        best_vs_null=best_vs_null,
        expected_max_under_null=(exp_mean if higher_is_better else -exp_mean),
        expected_max_p95=(exp_p95 if higher_is_better else -exp_p95),
        deflated_improvement=deflated,
        prob_best_le_null_max=prob_best_le_null_max,
        pair_holdout=pair_holdout,
        time_block_holdout=time_block_holdout,
        fragility_score=fragility,
        flags=flags,
        seed=seed,
        n_resample=n_resample,
        notes=notes,
    )


def _matrix_flags(
    *,
    best_vs_null: float | None,
    prob_best_le_null_max: float,
    deflated: float,
    n: int,
    too_many_variants: int,
    pair_holdout: HoldoutStability | None,
    time_block_holdout: HoldoutStability | None,
) -> tuple[list[str], float]:
    flags: list[str] = []
    if n > too_many_variants:
        flags.append("TOO_MANY_VARIANTS_FOR_EVIDENCE")

    # Does the best even reach the null reference?
    reaches_null = best_vs_null is None or best_vs_null > 0
    if best_vs_null is not None and best_vs_null <= 0:
        flags.append("INCONCLUSIVE")

    # Selection-noise vs robust: the best must clear the null AND be unlikely
    # under best-of-N noise (low prob_best_le_null_max).
    if reaches_null and prob_best_le_null_max <= 0.05 and deflated > 0:
        flags.append("ROBUST_MATRIX_SIGNAL")
    else:
        flags.append("LIKELY_SELECTION_NOISE")

    if pair_holdout is not None and pair_holdout.sign_flips:
        flags.append("FRAGILE_SINGLE_PAIR_RESULT")
    if time_block_holdout is not None and time_block_holdout.sign_flips:
        flags.append("FRAGILE_TIME_BLOCK_RESULT")

    # Fragility score in [0, 1]: blends selection-noise probability with holdout
    # sign flips (each flip adds weight).
    frag = prob_best_le_null_max
    if pair_holdout is not None and pair_holdout.sign_flips:
        frag = max(frag, 0.75)
    if time_block_holdout is not None and time_block_holdout.sign_flips:
        frag = max(frag, 0.75)
    return flags, float(min(1.0, frag))
