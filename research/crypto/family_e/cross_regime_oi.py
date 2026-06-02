"""Family E diagnostics 6 (cross-asset), 7 (regime conditioning), 4/5 (OI, low-power).

Cross-asset and regime cells reuse the cohort evaluation + null engine from
``diagnostics.evaluate_cohort``. OI diagnostics are deliberately constrained: with
only ~180d aggregate daily OI they default to a low-power classification.
"""

from __future__ import annotations

import numpy as np

from research.crypto.family_e.data import (
    FUNDING_SETTLEMENT_HOURS,
    InstrumentSeries,
    build_basis_sample,
    build_funding_persistence_sample,
    build_funding_sample,
    funding_8h_windows,
)
from research.crypto.family_e.diagnostics import (
    MIN_COHORT,
    _decile_signs,
    evaluate_cohort,
)
from research.crypto.family_e.nulls import DEFAULT_N_DRAWS

# ----------------------------------------------------------------------------- #
# Diagnostic 6 — cross-asset confirmation (BTC <-> ETH)
# ----------------------------------------------------------------------------- #


def _aligned_funding(series_by_inst: dict[str, InstrumentSeries], horizon_h: int) -> dict:
    insts = list(series_by_inst)
    samples = {i: build_funding_sample(series_by_inst[i], horizon_h=horizon_h) for i in insts}
    maps = {
        i: {int(h): k for k, h in enumerate(samples[i].entry_hours)} for i in insts
    }
    common = sorted(set.intersection(*[set(m) for m in maps.values()]))
    return {"insts": insts, "samples": samples, "maps": maps, "common": common}


def diagnostic_6_cross_asset(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    out: dict = {
        "name": "diagnostic_6_cross_asset_confirmation",
        "hypothesis": (
            "BTC/ETH funding agreement strengthens a directional (reversion) signal; "
            "disagreement predicts relative-value reversion of the extreme asset."
        ),
        "horizons": {},
    }
    insts = list(series_by_inst)
    if len(insts) != 2:
        out["status"] = "needs_two_assets"
        return out
    a, b = insts
    for h in (8, 24):
        al = _aligned_funding(series_by_inst, h)
        common = al["common"]
        sa, sb = al["samples"][a], al["samples"][b]
        ia = [al["maps"][a][t] for t in common]
        ib = [al["maps"][b][t] for t in common]
        sig_a, ret_a, fund_a = sa.signal[ia], sa.fwd_ret[ia], sa.funding_hold[ia]
        sig_b, ret_b, fund_b = sb.signal[ib], sb.fwd_ret[ib], sb.funding_hold[ib]
        # per-asset deciles on the aligned sample
        da, _ = _decile_signs(sig_a, top_sign=1.0, bottom_sign=-1.0)  # +1 top,-1 bottom membership
        db, _ = _decile_signs(sig_b, top_sign=1.0, bottom_sign=-1.0)
        both_top = (da > 0) & (db > 0)
        both_bottom = (da < 0) & (db < 0)
        agree = both_top | both_bottom
        # exactly one extreme, other neutral (inner deciles)
        a_extreme_only = (da != 0) & (db == 0)
        b_extreme_only = (db != 0) & (da == 0)

        # --- agreement directional: fade both legs (reversion direction) ---
        # top extreme -> short (-1); bottom -> long (+1)
        legs_signs = np.concatenate([-da[agree], -db[agree]])
        legs_ret = np.concatenate([ret_a[agree], ret_b[agree]])
        legs_fund = np.concatenate([fund_a[agree], fund_b[agree]])
        legs_lab = np.concatenate(
            [np.array([a] * int(agree.sum()), dtype=object),
             np.array([b] * int(agree.sum()), dtype=object)]
        )
        agreement = evaluate_cohort(
            legs_signs, legs_ret, legs_fund, legs_lab, legs_signs != 0,
            seed=seed + h, n_draws=n_draws,
        )
        agreement["n_windows"] = int(agree.sum())

        # --- disagreement relative-value: fade extreme leg, opposite on neutral leg ---
        rv_signs_list, rv_ret_list, rv_fund_list, rv_lab_list = [], [], [], []
        # case A extreme, B neutral: short/long A by -da, opposite on B
        rv_signs_list += [-da[a_extreme_only], da[a_extreme_only]]
        rv_ret_list += [ret_a[a_extreme_only], ret_b[a_extreme_only]]
        rv_fund_list += [fund_a[a_extreme_only], fund_b[a_extreme_only]]
        rv_lab_list += [
            np.array([a] * int(a_extreme_only.sum()), dtype=object),
            np.array([b] * int(a_extreme_only.sum()), dtype=object),
        ]
        # case B extreme, A neutral
        rv_signs_list += [-db[b_extreme_only], db[b_extreme_only]]
        rv_ret_list += [ret_b[b_extreme_only], ret_a[b_extreme_only]]
        rv_fund_list += [fund_b[b_extreme_only], fund_a[b_extreme_only]]
        rv_lab_list += [
            np.array([b] * int(b_extreme_only.sum()), dtype=object),
            np.array([a] * int(b_extreme_only.sum()), dtype=object),
        ]
        rv_signs = np.concatenate(rv_signs_list) if rv_signs_list else np.zeros(0)
        rv_ret = np.concatenate(rv_ret_list) if rv_ret_list else np.zeros(0)
        rv_fund = np.concatenate(rv_fund_list) if rv_fund_list else np.zeros(0)
        rv_lab = np.concatenate(rv_lab_list) if rv_lab_list else np.array([], dtype=object)
        disagreement = evaluate_cohort(
            rv_signs, rv_ret, rv_fund, rv_lab, rv_signs != 0,
            seed=seed + h + 500, n_draws=n_draws,
        )
        disagreement["n_windows"] = int(a_extreme_only.sum() + b_extreme_only.sum())

        # --- wrong-pairing null: BTC signal cohort vs ETH returns (and vice-versa) ---
        wp_signs = np.concatenate([-da[agree], -db[agree]])
        wp_ret = np.concatenate([ret_b[agree], ret_a[agree]])  # swapped returns
        wp_fund = np.concatenate([fund_b[agree], fund_a[agree]])
        wrong_pairing = evaluate_cohort(
            wp_signs, wp_ret, wp_fund, legs_lab, wp_signs != 0,
            seed=seed + h + 900, n_draws=n_draws,
        )

        out["horizons"][h] = {
            "n_common_windows": len(common),
            "agreement_directional": agreement,
            "disagreement_relative_value": disagreement,
            "wrong_pairing_control": wrong_pairing,
        }
    return out


# ----------------------------------------------------------------------------- #
# Diagnostic 7 — regime conditioning (applied to 1, 2, 3)
# ----------------------------------------------------------------------------- #


def _log_returns_by_hour(series: InstrumentSeries) -> dict[int, float]:
    hours = sorted(series.close_px)
    out: dict[int, float] = {}
    for i in range(1, len(hours)):
        h0, h1 = hours[i - 1], hours[i]
        if h1 == h0 + 1:
            p0, p1 = series.close_px[h0], series.close_px[h1]
            if p0 > 0 and p1 > 0:
                out[h1] = float(np.log(p1 / p0))
    return out


def _regime_values(series: InstrumentSeries, entry_hours: np.ndarray, signal: np.ndarray) -> dict:
    """Continuous regime variables per entry (nan where inputs missing)."""
    rets = _log_returns_by_hour(series)
    windows = funding_8h_windows(series.funding)
    n = entry_hours.size
    vol = np.full(n, np.nan)
    trend = np.full(n, np.nan)
    abs_funding = np.full(n, np.nan)
    basis = np.full(n, np.nan)
    for idx, e in enumerate(entry_hours):
        e = int(e)
        prior = [rets.get(e - j) for j in range(0, 24)]
        if all(v is not None for v in prior):
            vol[idx] = float(np.std(np.array(prior, dtype=float), ddof=1))
        p_now, p_then = series.open_px.get(e), series.open_px.get(e - 168)
        if p_now and p_then and p_now > 0 and p_then > 0:
            trend[idx] = float(np.log(p_now / p_then))
        # most recent completed 8h funding window ending at/before e
        last_win = (e // FUNDING_SETTLEMENT_HOURS) * FUNDING_SETTLEMENT_HOURS
        if last_win in windows:
            abs_funding[idx] = abs(windows[last_win])
        bvals = series.basis_bps.get(e - 1)
        if bvals is not None:
            basis[idx] = bvals
    return {"volatility": vol, "trend": trend, "abs_funding": abs_funding, "basis": basis}


def _tercile_labels(values: np.ndarray) -> np.ndarray:
    labels = np.full(values.size, -1, dtype=int)  # -1 = excluded (nan)
    finite = np.isfinite(values)
    if finite.sum() < 30:
        return labels
    lo = float(np.percentile(values[finite], 33.333))
    hi = float(np.percentile(values[finite], 66.667))
    labels[finite & (values <= lo)] = 0
    labels[finite & (values > lo) & (values <= hi)] = 1
    labels[finite & (values > hi)] = 2
    return labels


def diagnostic_7_regime_conditioning(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    """Condition diag 1 (funding reversion, h=24), 2 (continuation k=6,h=24), 3 (basis, h=24)."""
    out: dict = {
        "name": "diagnostic_7_regime_conditioning",
        "regimes": ["volatility", "trend", "abs_funding", "basis"],
        "base_diagnostics": {},
    }
    specs = [
        ("diag1_funding_reversion_h24", lambda s: build_funding_sample(s, horizon_h=24),
         -1.0, 1.0, True),
        ("diag2_continuation_k6_h24", lambda s: build_funding_persistence_sample(s, k=6, horizon_h=24),
         None, None, False),
        ("diag3_basis_reversion_h24", lambda s: build_basis_sample(s, horizon_h=24),
         -1.0, 1.0, True),
    ]
    for name, builder, top_sign, bottom_sign, is_decile in specs:
        block: dict = {}
        for regime in out["regimes"]:
            regime_cells: dict = {}
            pooled_signs, pooled_fwd, pooled_fund, pooled_lab, pooled_terc = [], [], [], [], []
            for inst, series in series_by_inst.items():
                sample = builder(series)
                if is_decile:
                    signs, _ = _decile_signs(sample.signal, top_sign=top_sign, bottom_sign=bottom_sign)
                else:
                    signs = sample.signal.copy()
                rv = _regime_values(series, sample.entry_hours, sample.signal)
                terc = _tercile_labels(rv[regime])
                labels = np.array([inst] * sample.n, dtype=object)
                pooled_signs.append(signs)
                pooled_fwd.append(sample.fwd_ret)
                pooled_fund.append(sample.funding_hold)
                pooled_lab.append(labels)
                pooled_terc.append(terc)
            ps = np.concatenate(pooled_signs)
            pf = np.concatenate(pooled_fwd)
            pfu = np.concatenate(pooled_fund)
            pl = np.concatenate(pooled_lab)
            pt = np.concatenate(pooled_terc)
            for t in (0, 1, 2):
                mask = (pt == t) & (ps != 0)
                regime_cells[f"tercile_{t}"] = evaluate_cohort(
                    ps, pf, pfu, pl, mask,
                    seed=seed + hash((name, regime, t)) % 100000, n_draws=n_draws,
                )
            block[regime] = regime_cells
        out["base_diagnostics"][name] = block
    return out


# ----------------------------------------------------------------------------- #
# Diagnostics 4 & 5 — OI impulse / funding-OI interaction (LOW-POWER)
# ----------------------------------------------------------------------------- #


def oi_availability(series_by_inst: dict[str, InstrumentSeries]) -> dict:
    return {
        inst: {
            "n_oi_rows": len(s.oi_usd),
            "low_power": len(s.oi_usd) < 365,  # < ~1y daily OI is low-power
        }
        for inst, s in series_by_inst.items()
    }


def diagnostics_4_5_oi_low_power(
    series_by_inst: dict[str, InstrumentSeries], *, seed: int, n_draws: int = DEFAULT_N_DRAWS
) -> dict:
    """Honest low-power OI block — only ~180d aggregate daily OI is available.

    We report coverage and (if any) a directional OI-impulse statistic, but the
    classification is forced to a low-power label: the sample cannot support a
    front-gate-grade conclusion. No interaction edge is over-interpreted.
    """
    avail = oi_availability(series_by_inst)
    enough = all(
        len(s.oi_usd) >= MIN_COHORT for s in series_by_inst.values()
    )
    return {
        "name": "diagnostics_4_5_oi_low_power",
        "availability": avail,
        "evaluable": enough,
        "note": (
            "Only ~180d aggregate daily OI (OKX rubik venue-aggregate USD notional) is "
            "freely available; per-instrument multi-year OI is the binding gap. "
            "Diagnostics 4 (OI impulse) and 5 (funding/OI interaction) are LOW-POWER and "
            "cannot reach candidate_for_front_gate from this sample."
        ),
    }
