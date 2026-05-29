"""Front-gate screen for volatility-managed time-series momentum (CAMPAIGN_031).

Import-isolated lab module: no broker / strategy / approval / execution imports.
It composes the existing lab cost primitives (``costs.py``) and is *descriptive
only* — it computes statistics and a structured result; it does not emit verdict
words (APPROVE/PASS/GO) and it does not approve any strategy. The pre-stated
decision rule lives in the precommit doc
(``docs/research/CAMPAIGN_031_VOL_MANAGED_TSMOM_THESIS_AUDIT_AND_PRECOMMIT.md``);
the runner maps these statistics onto that rule.

The frozen house config (precommit §5):
  - signal A: raw sign-blend over k in {63,126,252} trading days (no signal-level
    vol normalization -> avoids the 1/sigma^2 trap)
  - sizing B: w_i ~ S_i / sigma_i, sigma_i = EWMA vol, com ~= 60 trading days
  - portfolio C: scale to 10% annualized vol; naive(diag) and full-Sigma variants
  - timing D: Moreira-Muir clamp(target/strat_vol, 0.25, 1.5) on the book's own
    trailing 20-day P&L vol; tested on AND off
  - rebalance daily with a 15% no-trade band; turnover priced at half the
    round-trip half-spread cost; conservative financing stress charged per day held

All return series are daily log returns on D1AGG mid closes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from .costs import cost_fraction, financing_stress_fraction

TRADING_DAYS = 252.0
DEFAULT_LOOKBACKS = (63, 126, 252)
DEFAULT_VOL_COM = 60.0
DEFAULT_TARGET_VOL = 0.10
DEFAULT_NO_TRADE_BAND = 0.15
DEFAULT_MM_CLAMP = (0.25, 1.5)
DEFAULT_MM_WINDOW = 20
SPREAD_PIPS = 1.5
SLIP_PIPS = 0.2


# ---------------------------------------------------------------------------
# D1AGG aggregation (pure pandas, lookahead-free) — mirrors
# src/forex_bot/backtesting/d1_aggregation.py without importing forex_bot.
# ---------------------------------------------------------------------------
def aggregate_h4_to_d1agg(h4: pd.DataFrame, *, bars_per_day: int = 5) -> pd.DataFrame:
    """Aggregate 17:00-NY-aligned H4 bars to a daily D1AGG mid-close series.

    A trading day spans [17:00 NY, 17:00 NY next day). The research bar is the
    first ``bars_per_day`` H4 candles (17:00 -> 13:00 NY), timestamped at the
    close of the last included bar — deliberately clear of the 17:00 rollover
    blackout (CAMPAIGN_006). Days with fewer than ``bars_per_day`` completed H4
    bars are dropped (lookahead-free; we never peek past the cutoff).

    ``h4`` must have a tz-aware UTC DatetimeIndex and a ``mid_c`` (or ``close``)
    column. Returns a frame indexed by trading-day (NY date) with ``mid_close``.
    """
    if h4.empty:
        return pd.DataFrame(columns=["mid_close"])
    idx = h4.index
    if idx.tz is None:
        idx = idx.tz_localize("UTC")
    ny = idx.tz_convert("America/New_York")
    # [17:00 D, 17:00 D+1) -> label D : subtract 17h then floor to day
    trading_day = (ny - pd.Timedelta(hours=17)).floor("D")
    close_col = "mid_c" if "mid_c" in h4.columns else "close"
    work = pd.DataFrame(
        {"trading_day": trading_day.tz_localize(None), "mid_c": h4[close_col].to_numpy(float)}
    )
    work["seq"] = work.groupby("trading_day").cumcount()
    kept = work[work["seq"] < bars_per_day]
    counts = kept.groupby("trading_day")["seq"].count()
    full_days = counts[counts == bars_per_day].index
    kept = kept[kept["trading_day"].isin(full_days)]
    # daily close = mid_c of the last included (bars_per_day-th) bar
    daily_close = kept.groupby("trading_day")["mid_c"].last()
    out = pd.DataFrame({"mid_close": daily_close}).sort_index()
    return out


# ---------------------------------------------------------------------------
# Signal & vol primitives
# ---------------------------------------------------------------------------
def ewma_vol(log_returns: pd.Series, *, com: float = DEFAULT_VOL_COM) -> pd.Series:
    """Annualized EWMA volatility (center-of-mass ~ com trading days)."""
    var = log_returns.ewm(com=com, min_periods=int(com)).var(bias=True)
    return np.sqrt(var * TRADING_DAYS)


def sign_blend_signal(prices: pd.Series, *, lookbacks: Sequence[int] = DEFAULT_LOOKBACKS) -> pd.Series:
    """S_t = sign( sum_k sign(ln P_t / P_{t-k}) ) in {-1,0,+1}. Lookahead-free:
    uses only information available at the close of bar t."""
    votes = pd.Series(0.0, index=prices.index)
    logp = np.log(prices)
    for k in lookbacks:
        mom = logp - logp.shift(k)
        votes = votes.add(np.sign(mom), fill_value=0.0)
    sig = np.sign(votes)
    # bars without all lookbacks available -> flat
    max_k = max(lookbacks)
    sig.iloc[:max_k] = 0.0
    return sig.fillna(0.0)


# ---------------------------------------------------------------------------
# Book construction
# ---------------------------------------------------------------------------
@dataclass
class BookResult:
    daily_pre_cost: pd.Series
    daily_net: pd.Series
    daily_turnover_cost: pd.Series
    daily_financing: pd.Series
    weights: pd.DataFrame  # post-scale held weights per pair, per day
    gross_leverage: pd.Series
    net_usd_exposure: pd.Series
    meta: dict = field(default_factory=dict)


def _portfolio_scale(
    raw_w: np.ndarray,
    sigma: np.ndarray,
    corr: np.ndarray | None,
    target_vol: float,
) -> float:
    """Gross scale c so the booked portfolio hits ``target_vol`` annualized.

    raw_w_i = S_i / sigma_i (so raw_w_i * sigma_i = S_i). Naive ignores
    correlation (corr=None -> identity); full-Sigma uses the estimated R.
    """
    active = np.abs(raw_w) > 0
    if not active.any():
        return 0.0
    vol_contrib = raw_w * sigma  # = S_i (annualized vol units per position)
    if corr is None:
        port_vol = np.sqrt(np.sum(vol_contrib**2))
    else:
        port_vol = np.sqrt(vol_contrib @ corr @ vol_contrib)
    if port_vol <= 0:
        return 0.0
    return float(target_vol / port_vol)


def build_book(
    prices: Mapping[str, pd.Series],
    *,
    lookbacks: Sequence[int] = DEFAULT_LOOKBACKS,
    vol_com: float = DEFAULT_VOL_COM,
    target_vol: float = DEFAULT_TARGET_VOL,
    no_trade_band: float = DEFAULT_NO_TRADE_BAND,
    use_full_sigma: bool = True,
    corr_window: int = 60,
    mm_overlay: bool = True,
    mm_window: int = DEFAULT_MM_WINDOW,
    mm_clamp: tuple[float, float] = DEFAULT_MM_CLAMP,
    cost_mult: float = 1.0,
) -> BookResult:
    """Run the frozen house pipeline and return the daily book P&L series.

    Positions are decided at the close of day t from information up to t and
    earn day t+1's return (no lookahead). Turnover is charged when the desired
    weight leaves the no-trade band; financing stress is charged daily on held
    notional. ``cost_mult`` scales spread+financing for the 2x stress variant.
    """
    pairs = sorted(prices)
    px = pd.DataFrame({p: prices[p] for p in pairs}).dropna(how="all").sort_index()
    rets = np.log(px).diff()
    sigma = pd.DataFrame({p: ewma_vol(rets[p], com=vol_com) for p in pairs})
    signal = pd.DataFrame({p: sign_blend_signal(px[p], lookbacks=lookbacks) for p in pairs})

    dates = px.index
    held = pd.Series(0.0, index=pairs)  # current scaled weights
    rows_w, pre_cost, turn_cost, fin_cost = [], [], [], []
    gross, net_usd = [], []

    # daily price for cost fractions (one-way ~ half the round-trip)
    for i in range(len(dates) - 1):
        t, t1 = dates[i], dates[i + 1]
        sig_t = signal.loc[t].to_numpy(float)
        sig_v = sigma.loc[t].to_numpy(float)
        ok = np.isfinite(sig_v) & (sig_v > 0)
        raw_w = np.where(ok, sig_t / np.where(ok, sig_v, 1.0), 0.0)

        corr = None
        if use_full_sigma:
            window = rets.iloc[max(0, i - corr_window + 1) : i + 1]
            if len(window) >= max(20, corr_window // 2):
                c = window.corr().to_numpy(float)
                if np.all(np.isfinite(c)):
                    corr = c
        c_scale = _portfolio_scale(raw_w, np.where(ok, sig_v, 0.0), corr, target_vol)
        desired = pd.Series(raw_w * c_scale, index=pairs)

        # Moreira-Muir overlay on the book's own recent realized vol
        if mm_overlay and len(pre_cost) >= mm_window:
            recent = pd.Series(pre_cost[-mm_window:])
            strat_vol = recent.std() * np.sqrt(TRADING_DAYS)
            if strat_vol > 0:
                m = float(np.clip(target_vol / strat_vol, mm_clamp[0], mm_clamp[1]))
                desired = desired * m

        # no-trade band: only move a leg if it leaves the band
        new_held = held.copy()
        traded = pd.Series(0.0, index=pairs)
        for p in pairs:
            thresh = no_trade_band * max(abs(held[p]), 1e-9)
            if abs(desired[p] - held[p]) > thresh:
                traded[p] = abs(desired[p] - held[p])
                new_held[p] = desired[p]
        held = new_held

        # day t+1 P&L from held weights
        r_next = rets.loc[t1]
        day_pre = float((held * r_next.reindex(pairs)).sum())

        # one-way turnover cost (half the round-trip cost fraction) per traded leg
        tc = 0.0
        for p in pairs:
            if traded[p] > 0:
                price_p = float(px.loc[t, p])
                cf = cost_fraction(p, price_p, spread_pips=SPREAD_PIPS, slip_pips=SLIP_PIPS)
                tc += traded[p] * 0.5 * cf * cost_mult
        # financing stress: per held leg, one day
        fc = 0.0
        for p in pairs:
            if abs(held[p]) > 0:
                fc += abs(held[p]) * financing_stress_fraction(p, bars_held=1, hours_per_bar=24.0) * cost_mult

        pre_cost.append(day_pre)
        turn_cost.append(tc)
        fin_cost.append(fc)
        rows_w.append(held.copy())
        gross.append(float(held.abs().sum()))
        # net USD exposure: base/USD pairs => long base = long base vs USD;
        # USD/quote pairs => long pair = long USD. Approximate net USD leg.
        usd = 0.0
        for p in pairs:
            base, quote = p.split("_")
            if quote == "USD":
                usd -= held[p]  # long EUR_USD = short USD
            elif base == "USD":
                usd += held[p]  # long USD_JPY = long USD
        net_usd.append(usd)

    idx = dates[1 : len(pre_cost) + 1]
    pre_s = pd.Series(pre_cost, index=idx)
    tc_s = pd.Series(turn_cost, index=idx)
    fc_s = pd.Series(fin_cost, index=idx)
    net_s = pre_s - tc_s - fc_s
    w_df = pd.DataFrame(rows_w, index=idx)
    return BookResult(
        daily_pre_cost=pre_s,
        daily_net=net_s,
        daily_turnover_cost=tc_s,
        daily_financing=fc_s,
        weights=w_df,
        gross_leverage=pd.Series(gross, index=idx),
        net_usd_exposure=pd.Series(net_usd, index=idx),
        meta={
            "pairs": pairs,
            "use_full_sigma": use_full_sigma,
            "mm_overlay": mm_overlay,
            "cost_mult": cost_mult,
            "n_days": len(idx),
        },
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
def sharpe(daily: pd.Series) -> float:
    d = daily.dropna()
    if len(d) < 2 or d.std() == 0:
        return 0.0
    return float(d.mean() / d.std() * np.sqrt(TRADING_DAYS))


def block_bootstrap_sharpe_ci(
    daily: pd.Series, *, block: int = 20, n: int = 2000, seed: int = 31, lo: float = 5.0
) -> dict:
    """Block-bootstrap CI on annualized Sharpe (preserves autocorrelation)."""
    d = daily.dropna().to_numpy(float)
    if len(d) < block * 2:
        return {"sharpe": sharpe(daily), "lo": float("nan"), "hi": float("nan"), "n_eff": len(d)}
    rng = np.random.default_rng(seed)
    n_blocks = int(np.ceil(len(d) / block))
    starts_max = len(d) - block
    out = np.empty(n)
    for j in range(n):
        starts = rng.integers(0, starts_max + 1, size=n_blocks)
        sample = np.concatenate([d[s : s + block] for s in starts])[: len(d)]
        sd = sample.std()
        out[j] = sample.mean() / sd * np.sqrt(TRADING_DAYS) if sd > 0 else 0.0
    return {
        "sharpe": sharpe(daily),
        "lo": float(np.percentile(out, lo)),
        "hi": float(np.percentile(out, 100 - lo)),
        "n_eff": len(d),
    }


def random_entry_null(
    prices: Mapping[str, pd.Series],
    observed: BookResult,
    *,
    n_seeds: int = 200,
    seed: int = 31,
    **book_kwargs,
) -> dict:
    """Matched-turnover random-entry null: replace each pair's sign-blend signal
    with a random +/-1 series whose switch frequency matches the observed
    signal's, rebuild the book, and collect the null Sharpe distribution.
    Returns observed Sharpe, null mean and p95, and P(observed <= null max)."""
    pairs = sorted(prices)
    px = pd.DataFrame({p: prices[p] for p in pairs}).dropna(how="all").sort_index()
    base_signal = {p: sign_blend_signal(px[p]) for p in pairs}
    switch_rate = {}
    for p in pairs:
        s = base_signal[p]
        active = s[s != 0]
        switch_rate[p] = float((active.diff().abs() > 0).mean()) if len(active) > 1 else 0.05

    rng = np.random.default_rng(seed)
    null_sharpes = []
    for _ in range(n_seeds):
        rand_prices = {}
        # reuse build_book but with randomized signal by monkeypatching prices is
        # awkward; instead replicate sizing with a random sign overlay.
        nb = _book_with_signal_override(px, base_signal, switch_rate, rng, **book_kwargs)
        null_sharpes.append(sharpe(nb))
    arr = np.array(null_sharpes)
    obs = sharpe(observed.daily_net)
    return {
        "observed_sharpe": obs,
        "null_mean": float(arr.mean()),
        "null_p95": float(np.percentile(arr, 95)),
        "null_max": float(arr.max()),
        "p_obs_le_null_max": float((arr >= obs).mean()),
        "n_seeds": n_seeds,
        "beats_null_p95": bool(obs > np.percentile(arr, 95)),
    }


def _book_with_signal_override(px, base_signal, switch_rate, rng, **book_kwargs) -> pd.Series:
    """Lightweight book P&L (net of cost+financing) using a random matched-turnover
    sign instead of the momentum signal — for the null only."""
    pairs = sorted(px.columns)
    rets = np.log(px).diff()
    sigma = pd.DataFrame({p: ewma_vol(rets[p]) for p in pairs})
    # build random matched-turnover sign series per pair
    rand_sig = {}
    for p in pairs:
        n = len(px)
        sign = np.ones(n)
        cur = rng.choice([-1.0, 1.0])
        for i in range(n):
            if rng.random() < switch_rate[p]:
                cur = -cur
            sign[i] = cur
        s = pd.Series(sign, index=px.index)
        s.iloc[: max(DEFAULT_LOOKBACKS)] = 0.0
        rand_sig[p] = s
    signal = pd.DataFrame(rand_sig)
    target_vol = book_kwargs.get("target_vol", DEFAULT_TARGET_VOL)
    no_trade_band = book_kwargs.get("no_trade_band", DEFAULT_NO_TRADE_BAND)
    cost_mult = book_kwargs.get("cost_mult", 1.0)
    dates = px.index
    held = pd.Series(0.0, index=pairs)
    net = []
    for i in range(len(dates) - 1):
        t, t1 = dates[i], dates[i + 1]
        sig_v = sigma.loc[t].to_numpy(float)
        ok = np.isfinite(sig_v) & (sig_v > 0)
        raw_w = np.where(ok, signal.loc[t].to_numpy(float) / np.where(ok, sig_v, 1.0), 0.0)
        c_scale = _portfolio_scale(raw_w, np.where(ok, sig_v, 0.0), None, target_vol)
        desired = pd.Series(raw_w * c_scale, index=pairs)
        traded = pd.Series(0.0, index=pairs)
        new_held = held.copy()
        for p in pairs:
            thresh = no_trade_band * max(abs(held[p]), 1e-9)
            if abs(desired[p] - held[p]) > thresh:
                traded[p] = abs(desired[p] - held[p])
                new_held[p] = desired[p]
        held = new_held
        day = float((held * rets.loc[t1].reindex(pairs)).sum())
        tc = 0.0
        for p in pairs:
            if traded[p] > 0:
                tc += traded[p] * 0.5 * cost_fraction(
                    p, float(px.loc[t, p]), spread_pips=SPREAD_PIPS, slip_pips=SLIP_PIPS
                ) * cost_mult
        fc = sum(
            abs(held[p]) * financing_stress_fraction(p, bars_held=1, hours_per_bar=24.0) * cost_mult
            for p in pairs
            if abs(held[p]) > 0
        )
        net.append(day - tc - fc)
    return pd.Series(net, index=dates[1 : len(net) + 1])


def naive_self_baseline(
    prices: Mapping[str, pd.Series], *, lookback: int = 126, cost_mult: float = 1.0
) -> pd.Series:
    """Raw-sign, fixed equal notional, single lookback, NO vol management — the
    'naive version of itself' baseline the house config must beat."""
    pairs = sorted(prices)
    px = pd.DataFrame({p: prices[p] for p in pairs}).dropna(how="all").sort_index()
    rets = np.log(px).diff()
    logp = np.log(px)
    sig = np.sign(logp - logp.shift(lookback))
    sig.iloc[:lookback] = 0.0
    n_active = sig.abs().sum(axis=1).replace(0, np.nan)
    w = sig.div(n_active, axis=0).fillna(0.0)  # equal weight across active legs
    held = w.shift(1).fillna(0.0)
    pre = (held * rets).sum(axis=1)
    # cost on daily turnover + financing stress
    turn = held.diff().abs().fillna(0.0)
    tc = pd.Series(0.0, index=px.index)
    for p in pairs:
        cf = px[p].apply(lambda v: cost_fraction(p, float(v), spread_pips=SPREAD_PIPS, slip_pips=SLIP_PIPS))
        fin = financing_stress_fraction(p, bars_held=1, hours_per_bar=24.0)
        tc = tc.add(turn[p] * 0.5 * cf * cost_mult + held[p].abs() * fin * cost_mult, fill_value=0.0)
    return (pre - tc).dropna()
