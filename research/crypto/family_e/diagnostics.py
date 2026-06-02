"""Family E exploratory diagnostics 1, 2, 3, 6 (and OI 4, 5 low-power).

Each diagnostic produces raw per-cell edges + null p-values. Holm adjustment and
final classification are applied by the runner across the whole test family
(see reporting.holm_adjust / reporting.classify). Nothing here sizes, executes,
or walks forward — these are exploratory return statistics only.
"""

from __future__ import annotations

import numpy as np

from research.crypto.family_e.costs import (
    COST_VARIANTS,
    CostVariant,
    funding_includes,
    round_trip_cost_fraction,
)
from research.crypto.family_e.data import (
    EligibleSample,
    InstrumentSeries,
    build_basis_sample,
    build_funding_persistence_sample,
    build_funding_sample,
)
from research.crypto.family_e.nulls import DEFAULT_N_DRAWS, cohort_edge, run_cohort_nulls

MIN_COHORT = 100  # minimum eligible cohort size to evaluate a cell


def _cost_array(inst_labels: np.ndarray, variant: CostVariant) -> np.ndarray:
    return np.array(
        [round_trip_cost_fraction(str(i), variant=variant) for i in inst_labels], dtype=float
    )


def evaluate_cohort(
    signs_full: np.ndarray,
    fwd_ret: np.ndarray,
    funding_hold: np.ndarray,
    inst_labels: np.ndarray,
    mask: np.ndarray,
    *,
    seed: int,
    n_draws: int,
) -> dict:
    """Per-variant edges + null p-values for a cohort (single instrument or pooled)."""
    n_cohort = int(mask.sum())
    edges: dict[str, float] = {}
    for variant in COST_VARIANTS:
        cost_full = _cost_array(inst_labels, variant)
        edges[variant] = cohort_edge(
            signs_full[mask],
            fwd_ret[mask],
            funding_hold[mask],
            cost_full[mask],
            include_funding=funding_includes(variant),
        )
    result: dict = {"n": n_cohort, "edges": edges}
    if n_cohort >= MIN_COHORT:
        zero_cost = np.zeros(fwd_ret.size, dtype=float)
        result["nulls_gross"] = {
            k: v.as_dict()
            for k, v in run_cohort_nulls(
                mask=mask,
                signs_full=signs_full,
                fwd_ret=fwd_ret,
                funding_hold=funding_hold,
                cost_frac_full=zero_cost,
                include_funding=False,
                seed=seed,
                n_draws=n_draws,
            ).items()
        }
        result["nulls_all_in"] = {
            k: v.as_dict()
            for k, v in run_cohort_nulls(
                mask=mask,
                signs_full=signs_full,
                fwd_ret=fwd_ret,
                funding_hold=funding_hold,
                cost_frac_full=_cost_array(inst_labels, "all_in"),
                include_funding=True,
                seed=seed + 100,
                n_draws=n_draws,
            ).items()
        }
    return result


def _decile_signs(signal: np.ndarray, *, top_sign: float, bottom_sign: float) -> tuple[
    np.ndarray, dict[str, float]
]:
    """Signs array: top decile -> top_sign, bottom decile -> bottom_sign, else 0."""
    if signal.size == 0:
        return np.zeros(0), {"p10": 0.0, "p90": 0.0}
    p10 = float(np.percentile(signal, 10))
    p90 = float(np.percentile(signal, 90))
    signs = np.zeros(signal.size, dtype=float)
    signs[signal >= p90] = top_sign
    signs[signal <= p10] = bottom_sign
    return signs, {"p10": p10, "p90": p90}


def _pool(samples: dict[str, EligibleSample], signs_by_inst: dict[str, np.ndarray]) -> tuple[
    np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray
]:
    signs = np.concatenate([signs_by_inst[i] for i in samples])
    fwd = np.concatenate([samples[i].fwd_ret for i in samples])
    fund = np.concatenate([samples[i].funding_hold for i in samples])
    labels = np.concatenate(
        [np.array([i] * samples[i].n, dtype=object) for i in samples]
    )
    return signs, fwd, fund, labels, signs != 0


def _decile_diagnostic(
    series_by_inst: dict[str, InstrumentSeries],
    *,
    sample_builder,
    horizons: tuple[int, ...],
    top_sign: float,
    bottom_sign: float,
    seed: int,
    n_draws: int,
) -> dict:
    out: dict = {"horizons": {}, "skipped": {}, "direction": {"top": top_sign, "bottom": bottom_sign}}
    for h in horizons:
        samples = {i: sample_builder(s, horizon_h=h) for i, s in series_by_inst.items()}
        signs_by_inst: dict[str, np.ndarray] = {}
        cell: dict = {}
        for inst, sample in samples.items():
            signs, cuts = _decile_signs(sample.signal, top_sign=top_sign, bottom_sign=bottom_sign)
            signs_by_inst[inst] = signs
            labels = np.array([inst] * sample.n, dtype=object)
            ev = evaluate_cohort(
                signs, sample.fwd_ret, sample.funding_hold, labels, signs != 0,
                seed=seed + h, n_draws=n_draws,
            )
            ev["decile_cuts"] = cuts
            cell[inst] = ev
            out["skipped"].setdefault(inst, sample.n_skipped)
        p_signs, p_fwd, p_fund, p_labels, p_mask = _pool(samples, signs_by_inst)
        cell["pooled"] = evaluate_cohort(
            p_signs, p_fwd, p_fund, p_labels, p_mask, seed=seed + h + 50, n_draws=n_draws
        )
        out["horizons"][h] = cell
    return out


def diagnostic_1_funding_mean_reversion(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    # high positive funding -> short (-1); high negative funding -> long (+1)
    res = _decile_diagnostic(
        series_by_inst,
        sample_builder=build_funding_sample,
        horizons=(8, 24, 72),
        top_sign=-1.0,
        bottom_sign=1.0,
        seed=seed,
        n_draws=n_draws,
    )
    res["name"] = "diagnostic_1_funding_mean_reversion"
    res["hypothesis"] = (
        "Extreme positive (negative) 8h funding predicts negative (positive) forward "
        "perp returns as crowded carry unwinds."
    )
    return res


def diagnostic_3_basis_compression_expansion(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    # convergence/reversion: high basis -> short; low basis -> long
    reversion = _decile_diagnostic(
        series_by_inst,
        sample_builder=build_basis_sample,
        horizons=(4, 24),
        top_sign=-1.0,
        bottom_sign=1.0,
        seed=seed,
        n_draws=n_draws,
    )
    # expansion/momentum: high basis -> long; low basis -> short (opposite signs)
    expansion = _decile_diagnostic(
        series_by_inst,
        sample_builder=build_basis_sample,
        horizons=(4, 24),
        top_sign=1.0,
        bottom_sign=-1.0,
        seed=seed + 7,
        n_draws=n_draws,
    )
    return {
        "name": "diagnostic_3_basis_compression_expansion",
        "hypothesis": "Stretched perp-vs-index basis predicts convergence (reversion) or expansion (momentum).",
        "reversion": reversion,
        "expansion": expansion,
    }


def diagnostic_2_funding_trend_continuation(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    out: dict = {
        "name": "diagnostic_2_funding_trend_continuation",
        "hypothesis": "Persistent same-sign funding over k settlements aligns with directional continuation.",
        "k_values": {},
    }
    for k in (3, 6, 9):
        k_block: dict = {"horizons": {}, "skipped": {}}
        for h in (24, 72):
            samples = {
                i: build_funding_persistence_sample(s, k=k, horizon_h=h)
                for i, s in series_by_inst.items()
            }
            # continuation: trade in the sign of persistence
            cont_signs = {i: samples[i].signal.copy() for i in samples}
            cell: dict = {}
            for inst, sample in samples.items():
                labels = np.array([inst] * sample.n, dtype=object)
                mask = cont_signs[inst] != 0
                cell[inst] = {
                    "continuation": evaluate_cohort(
                        cont_signs[inst], sample.fwd_ret, sample.funding_hold, labels, mask,
                        seed=seed + k * 1000 + h, n_draws=n_draws,
                    ),
                    "contrarian": evaluate_cohort(
                        -cont_signs[inst], sample.fwd_ret, sample.funding_hold, labels, mask,
                        seed=seed + k * 2000 + h, n_draws=n_draws,
                    ),
                }
                k_block["skipped"].setdefault(inst, sample.n_skipped)
            p_signs, p_fwd, p_fund, p_labels, p_mask = _pool(samples, cont_signs)
            cell["pooled"] = {
                "continuation": evaluate_cohort(
                    p_signs, p_fwd, p_fund, p_labels, p_mask,
                    seed=seed + k * 3000 + h, n_draws=n_draws,
                ),
                "contrarian": evaluate_cohort(
                    -p_signs, p_fwd, p_fund, p_labels, p_mask,
                    seed=seed + k * 4000 + h, n_draws=n_draws,
                ),
            }
            k_block["horizons"][h] = cell
        out["k_values"][k] = k_block
    return out
