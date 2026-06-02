"""Matched-null infrastructure for Family E diagnostics (deterministic seeds).

A cohort is defined by a boolean ``mask`` over the eligible sample plus per-entry
direction ``signs`` ∈ {+1, -1}. The observed edge is the mean net signed return.
Nulls perturb the signal→return link and rebuild the edge distribution:

* ``shuffled``       — permute (fwd_ret, funding_hold) pairs against the signal;
* ``randomized_sign``— randomize the per-entry direction within the cohort;
* ``matched_random`` — random entries of the same cohort size with random signs.

``wrong_pairing`` (basis / cross-asset) is built by the diagnostic layer by
swapping one instrument's forward returns onto another's signal.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from research.crypto.family_e.costs import net_returns

BASE_SEED = 20260602
DEFAULT_N_DRAWS = 1000


@dataclass(frozen=True)
class NullResult:
    observed: float
    null_mean: float
    null_p05: float
    null_p95: float
    p_value_greater: float  # P(null >= observed)
    p_value_two_sided: float
    n_draws: int
    seed: int

    def as_dict(self) -> dict[str, float | int]:
        return {
            "observed": self.observed,
            "null_mean": self.null_mean,
            "null_p05": self.null_p05,
            "null_p95": self.null_p95,
            "p_value_greater": self.p_value_greater,
            "p_value_two_sided": self.p_value_two_sided,
            "n_draws": self.n_draws,
            "seed": self.seed,
        }


def cohort_edge(
    signs: np.ndarray,
    fwd_ret: np.ndarray,
    funding_hold: np.ndarray,
    cost_frac: np.ndarray | float,
    *,
    include_funding: bool,
) -> float:
    """Mean net return over a cohort (0.0 for an empty cohort)."""
    if signs.size == 0:
        return 0.0
    net = net_returns(signs, fwd_ret, funding_hold, cost_frac, include_funding=include_funding)
    return float(np.mean(net))


def _summarize(observed: float, nulls: np.ndarray, *, n_draws: int, seed: int) -> NullResult:
    if nulls.size == 0:
        return NullResult(observed, 0.0, 0.0, 0.0, 1.0, 1.0, 0, seed)
    p_greater = float(np.mean(nulls >= observed))
    p_two = float(np.mean(np.abs(nulls) >= abs(observed)))
    return NullResult(
        observed=observed,
        null_mean=float(np.mean(nulls)),
        null_p05=float(np.percentile(nulls, 5)),
        null_p95=float(np.percentile(nulls, 95)),
        p_value_greater=p_greater,
        p_value_two_sided=p_two,
        n_draws=n_draws,
        seed=seed,
    )


def run_cohort_nulls(
    *,
    mask: np.ndarray,
    signs_full: np.ndarray,
    fwd_ret: np.ndarray,
    funding_hold: np.ndarray,
    cost_frac_full: np.ndarray,
    include_funding: bool,
    seed: int,
    n_draws: int = DEFAULT_N_DRAWS,
) -> dict[str, NullResult]:
    """Return {null_name: NullResult} for the cohort defined by ``mask``/``signs_full``.

    ``cost_frac_full`` is a per-entry round-trip cost-fraction array over the full
    sample (so BTC/ETH pooling carries the right per-leg cost). All RNGs use
    deterministic seeds derived from ``seed``.
    """
    cohort_signs = signs_full[mask]
    cohort_ret = fwd_ret[mask]
    cohort_fund = funding_hold[mask]
    cohort_cost = cost_frac_full[mask]
    observed = cohort_edge(
        cohort_signs, cohort_ret, cohort_fund, cohort_cost, include_funding=include_funding
    )
    n_total = fwd_ret.size
    n_cohort = int(mask.sum())

    rng_shuffle = np.random.default_rng(seed + 1)
    rng_sign = np.random.default_rng(seed + 2)
    rng_match = np.random.default_rng(seed + 3)

    shuffled: list[float] = []
    sign_null: list[float] = []
    matched: list[float] = []
    if n_cohort > 0 and n_total > 0:
        for _ in range(n_draws):
            # shuffled: permute (ret, funding) pairs across the full sample, keep cohort mask
            perm = rng_shuffle.permutation(n_total)
            shuffled.append(
                cohort_edge(
                    cohort_signs,
                    fwd_ret[perm][mask],
                    funding_hold[perm][mask],
                    cohort_cost,
                    include_funding=include_funding,
                )
            )
            # randomized sign within cohort
            sign_null.append(
                cohort_edge(
                    rng_sign.choice(np.array([-1.0, 1.0]), size=n_cohort),
                    cohort_ret,
                    cohort_fund,
                    cohort_cost,
                    include_funding=include_funding,
                )
            )
            # matched-random entries of same size, random signs
            idx = rng_match.choice(n_total, size=n_cohort, replace=False)
            matched.append(
                cohort_edge(
                    rng_match.choice(np.array([-1.0, 1.0]), size=n_cohort),
                    fwd_ret[idx],
                    funding_hold[idx],
                    cost_frac_full[idx],
                    include_funding=include_funding,
                )
            )
    return {
        "shuffled": _summarize(observed, np.array(shuffled), n_draws=n_draws, seed=seed + 1),
        "randomized_sign": _summarize(
            observed, np.array(sign_null), n_draws=n_draws, seed=seed + 2
        ),
        "matched_random": _summarize(
            observed, np.array(matched), n_draws=n_draws, seed=seed + 3
        ),
    }
