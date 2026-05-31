#!/usr/bin/env python3
"""Runner — gross carry factor-validation (research-only).

Executes the FROZEN protocol (docs/research/CARRY_FACTOR_PROTOCOL.md) end to end
and writes every number to research/carry/factor_validation/ so the Phase 3-7 docs
can quote on-disk values, never buffered expectations. Read-only on the spot store;
no broker, no costs, no approval.

Usage:
    python scripts/run_carry_factor_validation.py
"""
from __future__ import annotations

import json
import sqlite3
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from research.carry.carry_factor import (
    MAJORS,
    SEED,
    build_weights,
    carry_accrual,
    cell_stats,
    currency_log_returns,
    currency_usd_levels,
    currency_yields,
    forward_spot_return,
    holm_bonferroni,
    instrument_carry,
    instrument_log_levels,
    lag_matrix,
    matched_z,
    null_matched_random,
    null_randomized_ranks,
    null_shuffled_timestamp,
    rank_stability,
)
from research.carry.carry_rates import (
    CURRENCIES,
    build_rate_panel,
    monthly_rate_matrix,
)

DB = ROOT / "data" / "campaign_002.sqlite3"
RATE_SERIES_CSV = ROOT / "docs" / "research" / "carry_rates" / "rate_series.csv"
OUT = ROOT / "research" / "carry" / "factor_validation"
WINDOW_START = "2021-05-01"  # month-start of first spot close (base month)
HORIZONS = [1, 3, 6, 12]
N_DRAWS = 2000


def load_month_end_mid(db: Path) -> pd.DataFrame:
    con = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    try:
        cols = {}
        meta = {}
        for pair in MAJORS:
            q = (
                "SELECT time, bid_c, ask_c FROM candles "
                "WHERE instrument=? AND granularity='H1' ORDER BY time"
            )
            df = pd.read_sql_query(q, con, params=(pair,))
            df["time"] = pd.to_datetime(df["time"], utc=True)
            df["mid"] = (df["bid_c"].astype(float) + df["ask_c"].astype(float)) / 2.0
            df["month"] = df["time"].dt.tz_convert("UTC").dt.tz_localize(None).dt.to_period("M")
            me = df.groupby("month")["mid"].last()
            me.index = me.index.to_timestamp()
            cols[pair] = me
            meta[pair] = {"n_h1_rows": len(df), "first": str(df["time"].min()), "last": str(df["time"].max())}
        wide = pd.DataFrame(cols).sort_index()
        wide = wide[wide.index >= pd.Timestamp(WINDOW_START)]
        return wide, meta
    finally:
        con.close()


def load_rate_matrix() -> pd.DataFrame:
    raw = pd.read_csv(RATE_SERIES_CSV, parse_dates=["date"])
    by_ccy = {c: raw[raw["currency"] == c][["date", "rate"]].rename(columns={"rate": "value"}) for c in CURRENCIES}
    panel = build_rate_panel(by_ccy)
    return monthly_rate_matrix(panel)


def jsonable(o):
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, float) and np.isnan(o):
        return None
    raise TypeError(type(o))


def stats_dict(cs):
    return {
        "n": cs.n, "n_independent": cs.n_independent, "mean": cs.mean, "std": cs.std,
        "ann_ratio": cs.ann_ratio, "sign_consistency": cs.sign_consistency, "nw_t": cs.nw_t,
    }


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(SEED)

    # ---- panels ----
    month_end_mid, spot_meta = load_month_end_mid(DB)
    rate_matrix_full = load_rate_matrix()
    # align carry signal to the spot months
    months = month_end_mid.index
    rate_matrix = rate_matrix_full.reindex(months).ffill()

    usd_levels = currency_usd_levels(month_end_mid)
    ccy_ln_levels = np.log(usd_levels)
    inst_ln_levels = instrument_log_levels(usd_levels)
    ccy_yields = currency_yields(rate_matrix)            # decimal annualized
    inst_carry = instrument_carry(rate_matrix)           # annualized %
    inst_yields = inst_carry / 100.0

    # signals (rate level) with primary 1-month lag
    ccy_signal_primary = lag_matrix(rate_matrix.reindex(columns=CURRENCIES), 1)
    inst_signal_primary = lag_matrix(inst_carry, 1)

    artifacts = {
        "seed": SEED,
        "db": str(DB.relative_to(ROOT)),
        "window_start": WINDOW_START,
        "n_months": len(months),
        "months": [str(m.date()) for m in months],
        "spot_meta": spot_meta,
        "rank_stability_currency": rank_stability(ccy_signal_primary),
        "rank_stability_instrument": rank_stability(inst_signal_primary),
    }

    # =================================================================== #
    # Phase 2 — exposures (no returns): weights for primary cell + variants
    # =================================================================== #
    w_ccy_hml3 = build_weights(ccy_signal_primary, "hml", 3)
    w_ccy_hml2 = build_weights(ccy_signal_primary, "hml", 2)
    w_ccy_rank = build_weights(ccy_signal_primary, "rank")
    w_inst_hml4 = build_weights(inst_signal_primary, "hml", 4)

    w_ccy_hml3.to_csv(OUT / "weights_currency_hml3.csv")
    w_inst_hml4.to_csv(OUT / "weights_instrument_hml4.csv")
    ccy_signal_primary.to_csv(OUT / "signal_currency_rate_lag1.csv")
    # avg long/short composition
    def composition(w):
        longs = (w > 0).sum().sort_values(ascending=False)
        shorts = (w < 0).sum().sort_values(ascending=False)
        return {"months_long": longs[longs > 0].to_dict(), "months_short": shorts[shorts > 0].to_dict()}
    artifacts["exposures"] = {
        "currency_hml3": composition(w_ccy_hml3),
        "instrument_hml4": composition(w_inst_hml4),
        "mean_abs_gross_currency_hml3": float(w_ccy_hml3.abs().sum(axis=1).mean()),
    }

    # =================================================================== #
    # Phase 3 — response study  (layer × scheme × metric × horizon)
    # =================================================================== #
    def response(weights, ln_levels, yield_signal):
        out = {}
        for h in HORIZONS:
            spot = forward_spot_return(weights, ln_levels, h)
            acc = carry_accrual(weights, yield_signal, h).reindex(spot.index)
            tot = (spot + acc).dropna()
            out[str(h)] = {
                "total": stats_dict(cell_stats(tot, h)),
                "spot_only": stats_dict(cell_stats(spot.dropna(), h)),
                "carry_accrual_mean": float(acc.mean()),
            }
        return out

    response_study = {
        "currency_hml3": response(w_ccy_hml3, ccy_ln_levels, ccy_yields),
        "currency_hml2": response(w_ccy_hml2, ccy_ln_levels, ccy_yields),
        "currency_rank": response(w_ccy_rank, ccy_ln_levels, ccy_yields),
        "instrument_hml4": response(w_inst_hml4, inst_ln_levels, inst_yields),
    }
    # unconditional baselines
    eq_w = pd.DataFrame(0.0, index=ccy_signal_primary.index, columns=CURRENCIES)
    nonusd = [c for c in CURRENCIES if c != "USD"]
    eq_w[nonusd] = 1.0 / len(nonusd)  # long all non-USD vs nothing -> use dollar-neutral instead:
    eq_dn = pd.DataFrame(0.0, index=ccy_signal_primary.index, columns=CURRENCIES)
    eq_dn[nonusd] = 1.0 / len(nonusd)
    eq_dn["USD"] = -1.0  # long basket of non-USD funded in USD (the "all currencies" carry-naive book)
    response_study["unconditional_longall_vs_usd"] = response(eq_dn, ccy_ln_levels, ccy_yields)
    artifacts["response_study"] = response_study

    # =================================================================== #
    # Phase 4 — cross-sectional validation
    # =================================================================== #
    # per-currency: mean forward 3m spot return vs mean rank, and slope
    h = 3
    fwd3 = ccy_ln_levels.shift(-h) - ccy_ln_levels
    per_ccy = {}
    for c in CURRENCIES:
        yld = ccy_yields[c].reindex(fwd3.index)
        tot_c = fwd3[c] + yld * (h / 12.0)
        per_ccy[c] = {
            "mean_rate": float(rate_matrix[c].mean()),
            "mean_fwd3_spot": float(fwd3[c].mean()),
            "mean_fwd3_total": float(tot_c.mean()),
        }
    # cross-sectional slope: regress mean_fwd3_total on mean_rate across currencies
    rates = np.array([per_ccy[c]["mean_rate"] for c in CURRENCIES])
    tots = np.array([per_ccy[c]["mean_fwd3_total"] for c in CURRENCIES])
    slope = float(np.polyfit(rates, tots, 1)[0])
    corr = float(np.corrcoef(rates, tots)[0, 1])
    artifacts["cross_sectional"] = {
        "per_currency": per_ccy,
        "fwd3_total_vs_rate_slope": slope,
        "fwd3_total_vs_rate_corr": corr,
    }

    # per-year HML-3 total (3m)
    spot3 = forward_spot_return(w_ccy_hml3, ccy_ln_levels, 3)
    acc3 = carry_accrual(w_ccy_hml3, ccy_yields, 3).reindex(spot3.index)
    tot3 = (spot3 + acc3).dropna()
    by_year = {str(y): {"n": int(g.shape[0]), "mean": float(g.mean()), "sign": float((g > 0).mean())}
               for y, g in tot3.groupby(tot3.index.year)}
    artifacts["by_year"] = by_year

    # rate-regime: USD rate 3m change sign
    usd_chg = rate_matrix["USD"].diff(3)
    regime = pd.Series(np.where(usd_chg > 0.1, "hiking", np.where(usd_chg < -0.1, "cutting", "hold")), index=rate_matrix.index)
    reg3 = regime.reindex(tot3.index)
    by_regime = {r: {"n": int((reg3 == r).sum()), "mean": float(tot3[reg3 == r].mean()) if (reg3 == r).any() else None}
                 for r in ["hiking", "hold", "cutting"]}
    artifacts["by_rate_regime"] = by_regime

    # risk regime: cross-sectional dispersion of monthly FX returns (calm/turbulent)
    ccy_ret = currency_log_returns(usd_levels)
    disp = ccy_ret[nonusd].std(axis=1)
    med = disp.median()
    calm = disp <= med
    calm3 = calm.reindex(tot3.index)
    artifacts["by_risk_regime"] = {
        "calm": {"n": int(calm3.sum()), "mean": float(tot3[calm3].mean()) if calm3.any() else None},
        "turbulent": {"n": int((~calm3).sum()), "mean": float(tot3[~calm3].mean()) if (~calm3).any() else None},
    }

    # drop-one currency (3m total HML-3)
    drop_one = {}
    for c in CURRENCIES:
        sig = ccy_signal_primary.drop(columns=[c])
        w = build_weights(sig, "hml", 3)
        s = forward_spot_return(w, ccy_ln_levels.drop(columns=[c]), 3)
        a = carry_accrual(w, ccy_yields.drop(columns=[c]), 3).reindex(s.index)
        t = (s + a).dropna()
        drop_one[c] = {"mean": float(t.mean()), "n": len(t)}
    artifacts["drop_one_currency"] = drop_one

    # =================================================================== #
    # Phase 5 — nulls vs the PRIMARY cell (currency HML-3, total, h=3)
    # =================================================================== #
    obs_mean = float(tot3.mean())
    nulls = {}
    nr = null_randomized_ranks(ccy_signal_primary, ccy_ln_levels, ccy_yields, 3, "hml", 3, N_DRAWS, rng)
    nt = null_shuffled_timestamp(ccy_signal_primary, ccy_ln_levels, ccy_yields, 3, "hml", 3, N_DRAWS, rng)
    nm = null_matched_random(ccy_signal_primary, ccy_ln_levels, ccy_yields, 3, 3, N_DRAWS, rng)
    nulls["randomized_ranks"] = matched_z(obs_mean, nr)
    nulls["shuffled_timestamp"] = matched_z(obs_mean, nt)
    nulls["matched_random"] = matched_z(obs_mean, nm)
    uncond_mean = float(response_study["unconditional_longall_vs_usd"]["3"]["total"]["mean"])
    nulls["unconditional_baseline"] = {"baseline_mean": uncond_mean, "observed_mean": obs_mean,
                                       "observed_minus_baseline": obs_mean - uncond_mean}
    nulls["observed_primary_mean"] = obs_mean
    artifacts["nulls_primary_cell"] = nulls

    # Holm-Bonferroni across horizon family (currency HML-3 total), null = randomized ranks
    pfam = {}
    for hh in HORIZONS:
        s = forward_spot_return(w_ccy_hml3, ccy_ln_levels, hh)
        a = carry_accrual(w_ccy_hml3, ccy_yields, hh).reindex(s.index)
        t = (s + a).dropna()
        draws = null_randomized_ranks(ccy_signal_primary, ccy_ln_levels, ccy_yields, hh, "hml", 3, N_DRAWS, rng)
        pfam[str(hh)] = matched_z(float(t.mean()), draws)["p_one_sided"]
    artifacts["holm_bonferroni_horizon_family"] = holm_bonferroni(pfam)
    artifacts["p_by_horizon_randomized_null"] = pfam

    # =================================================================== #
    # Phase 6 — robustness grid (3m total mean, currency layer unless noted)
    # =================================================================== #
    robustness = {}
    for k in (2, 3):
        w = build_weights(ccy_signal_primary, "hml", k)
        s = forward_spot_return(w, ccy_ln_levels, 3)
        a = carry_accrual(w, ccy_yields, 3).reindex(s.index)
        robustness[f"hml_k{k}"] = float((s + a).dropna().mean())
    robustness["rank_weighted"] = float(
        (forward_spot_return(w_ccy_rank, ccy_ln_levels, 3)
         + carry_accrual(w_ccy_rank, ccy_yields, 3).reindex(forward_spot_return(w_ccy_rank, ccy_ln_levels, 3).index)).dropna().mean()
    )
    for lag in (0, 1, 2):
        sig = lag_matrix(rate_matrix.reindex(columns=CURRENCIES), lag)
        w = build_weights(sig, "hml", 3)
        s = forward_spot_return(w, ccy_ln_levels, 3)
        a = carry_accrual(w, ccy_yields, 3).reindex(s.index)
        robustness[f"lag{lag}m"] = float((s + a).dropna().mean())
    # ranking variable = 3m change in rate (carry momentum)
    mom = lag_matrix(rate_matrix.reindex(columns=CURRENCIES).diff(3), 1)
    wmom = build_weights(mom, "hml", 3)
    smom = forward_spot_return(wmom, ccy_ln_levels, 3)
    amom = carry_accrual(wmom, ccy_yields, 3).reindex(smom.index)
    robustness["rank_by_rate_momentum"] = float((smom + amom).dropna().mean())
    for m in (3, 4, 5):
        w = build_weights(inst_signal_primary, "hml", m)
        s = forward_spot_return(w, inst_ln_levels, 3)
        a = carry_accrual(w, inst_yields, 3).reindex(s.index)
        robustness[f"instrument_hml{m}"] = float((s + a).dropna().mean())
    artifacts["robustness_3m_total_mean"] = robustness

    # ---- write ----
    (OUT / "carry_factor_validation.json").write_text(json.dumps(artifacts, indent=2, default=jsonable))
    print(f"wrote {OUT / 'carry_factor_validation.json'}")
    print(f"n_months={artifacts['n_months']}  primary_obs_mean={obs_mean:.6f}")
    print("nulls:", {k: round(v["z"], 2) for k, v in nulls.items() if isinstance(v, dict) and "z" in v})
    print("by_year:", {y: round(v["mean"], 4) for y, v in by_year.items()})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
