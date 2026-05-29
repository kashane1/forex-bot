"""CAMPAIGN_031 front-gate screen runner — volatility-managed TSMOM.

Pulls H4 (train window ONLY) for the 7 USD majors from the research Postgres
store, aggregates to D1AGG daily mid closes, runs the import-isolated screen
(``research/edge_discovery/vol_managed_tsmom.py``), and writes JSON + Markdown
artifacts to ``research/campaign_031/front_gate/``.

Freeze discipline: train window only (2020-01-01 -> 2022-12-31). The validation
window (2023-2024) and the test/lockbox (2025-01 -> 2026-05) are never queried.
The runner refuses any ``to`` past the train end. It approves nothing and writes
no verdict word; it records statistics against the pre-stated decision rule in
``docs/research/CAMPAIGN_031_VOL_MANAGED_TSMOM_THESIS_AUDIT_AND_PRECOMMIT.md``.
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from research.edge_discovery import vol_managed_tsmom as vm  # noqa: E402

PAIRS = ["AUD_USD", "EUR_USD", "GBP_USD", "NZD_USD", "USD_CAD", "USD_CHF", "USD_JPY"]
TRAIN_FROM = "2020-01-01T00:00:00Z"
TRAIN_TO = "2022-12-31T23:59:59Z"  # HARD train ceiling; validation/test never touched
OUT_DIR = _REPO / "research" / "campaign_031" / "front_gate"


def _connect():
    url = os.environ.get("FOREX_BOT_RESEARCH_DATABASE_URL")
    if not url:
        raise SystemExit("FOREX_BOT_RESEARCH_DATABASE_URL not set; cannot run screen.")
    import psycopg

    return psycopg.connect(url)


def load_h4(conn, instrument: str) -> pd.DataFrame:
    q = (
        "SELECT time_utc, mid_c FROM market_data.candles "
        "WHERE instrument = %s AND granularity = 'H4' AND complete = true "
        "AND time_utc >= %s AND time_utc <= %s ORDER BY time_utc ASC"
    )
    df = pd.read_sql_query(q, conn, params=[instrument, TRAIN_FROM, TRAIN_TO])
    df["time_utc"] = pd.to_datetime(df["time_utc"], utc=True)
    return df.set_index("time_utc")


def main() -> None:
    assert TRAIN_TO < "2023", "train ceiling must stay below validation window"
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    conn = _connect()
    daily = {}
    coverage = {}
    for p in PAIRS:
        h4 = load_h4(conn, p)
        d1 = vm.aggregate_h4_to_d1agg(h4)
        daily[p] = d1["mid_close"]
        coverage[p] = {
            "h4_rows": int(len(h4)),
            "d1agg_days": int(len(d1)),
            "from": str(d1.index.min().date()) if len(d1) else None,
            "to": str(d1.index.max().date()) if len(d1) else None,
        }
    conn.close()

    # ---- house config: full-Sigma C, MM on ----
    house = vm.build_book(daily, use_full_sigma=True, mm_overlay=True, cost_mult=1.0)
    house_2x = vm.build_book(daily, use_full_sigma=True, mm_overlay=True, cost_mult=2.0)
    # ablations
    no_mm = vm.build_book(daily, use_full_sigma=True, mm_overlay=False, cost_mult=1.0)
    naive_c = vm.build_book(daily, use_full_sigma=False, mm_overlay=True, cost_mult=1.0)

    def book_stats(b: vm.BookResult) -> dict:
        ci = vm.block_bootstrap_sharpe_ci(b.daily_net)
        return {
            "n_days": int(b.meta["n_days"]),
            "sharpe_pre_cost": vm.sharpe(b.daily_pre_cost),
            "sharpe_net": vm.sharpe(b.daily_net),
            "sharpe_net_lo5": ci["lo"],
            "sharpe_net_hi95": ci["hi"],
            "ann_return_net": float(b.daily_net.mean() * vm.TRADING_DAYS),
            "ann_vol_net": float(b.daily_net.std() * np.sqrt(vm.TRADING_DAYS)),
            "total_turnover_cost": float(b.daily_turnover_cost.sum()),
            "total_financing": float(b.daily_financing.sum()),
            "mean_gross": float(b.gross_leverage.mean()),
            "mean_abs_net_usd": float(b.net_usd_exposure.abs().mean()),
            "mean_gross_nonzero": float(b.gross_leverage[b.gross_leverage > 0].mean())
            if (b.gross_leverage > 0).any()
            else 0.0,
        }

    null = vm.random_entry_null(daily, house, n_seeds=200, use_full_sigma=False, mm_overlay=True)
    naive_self = vm.naive_self_baseline(daily, lookback=126)

    result = {
        "campaign": "CAMPAIGN_031",
        "sprint": "campaign-031-vol-managed-tsmom-front-gate-screen-001",
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "freeze": "intact; train-only; validation/test untouched; nothing approved",
        "train_window": {"from": TRAIN_FROM, "to": TRAIN_TO},
        "universe": PAIRS,
        "data_caveat": "7 USD-legged majors only, no crosses; ~3y train -> ~3 annual cycles "
        "after 252d warmup. Underpowered for a slow-signal deflated-Sharpe claim.",
        "coverage": coverage,
        "books": {
            "house_full_sigma_mm_on": book_stats(house),
            "house_2x_cost_stress": book_stats(house_2x),
            "ablation_mm_off": book_stats(no_mm),
            "ablation_naive_C": book_stats(naive_c),
        },
        "baselines": {
            "random_entry_matched_turnover_null": null,
            "naive_self_sharpe_net": vm.sharpe(naive_self),
        },
        "frozen_decision_inputs": {
            "house_net_sharpe_gt_0": vm.sharpe(house.daily_net) > 0,
            "house_2x_net_sharpe_gt_0": vm.sharpe(house_2x.daily_net) > 0,
            "boot_lo5_gt_0": book_stats(house)["sharpe_net_lo5"] > 0,
            "beats_null_p95": null["beats_null_p95"],
            "beats_naive_self": vm.sharpe(house.daily_net) > vm.sharpe(naive_self),
        },
    }

    (OUT_DIR / "vol_managed_tsmom_screen.json").write_text(json.dumps(result, indent=2))
    _write_md(result)
    print(json.dumps(result["books"], indent=2))
    print("\nfrozen_decision_inputs:", json.dumps(result["frozen_decision_inputs"], indent=2))
    print("null:", json.dumps(result["baselines"], indent=2))


def _write_md(r: dict) -> None:
    di = r["frozen_decision_inputs"]
    advances = all(di.values())
    h = r["books"]["house_full_sigma_mm_on"]
    lines = [
        "# CAMPAIGN_031 — Vol-Managed TSMOM Front-Gate Screen (results)",
        "",
        f"_Generated: {r['generated_utc']} · Freeze: {r['freeze']}_",
        "",
        f"**Train window:** {r['train_window']['from']} → {r['train_window']['to']} (train only).",
        f"**Universe:** {', '.join(r['universe'])}.",
        "",
        f"> Data caveat: {r['data_caveat']}",
        "",
        "## House config (full-Σ C, MM on)",
        "",
        f"- Sharpe pre-cost: **{h['sharpe_pre_cost']:.3f}**, net: **{h['sharpe_net']:.3f}** "
        f"(boot 5–95%: {h['sharpe_net_lo5']:.3f} … {h['sharpe_net_hi95']:.3f})",
        f"- Ann return net: {h['ann_return_net']*100:.2f}% · ann vol: {h['ann_vol_net']*100:.2f}% · "
        f"days: {h['n_days']}",
        f"- Total turnover cost: {h['total_turnover_cost']:.4f} · total financing: {h['total_financing']:.4f}",
        f"- Mean |net-USD| exposure: {h['mean_abs_net_usd']:.3f} · mean gross (active): {h['mean_gross_nonzero']:.3f}",
        "",
        "## Baselines & ablations",
        "",
        f"- 2× cost/financing stress Sharpe net: **{r['books']['house_2x_cost_stress']['sharpe_net']:.3f}**",
        f"- MM-off Sharpe net: {r['books']['ablation_mm_off']['sharpe_net']:.3f} "
        f"(MM adds {h['sharpe_net'] - r['books']['ablation_mm_off']['sharpe_net']:+.3f})",
        f"- Naive-C Sharpe net: {r['books']['ablation_naive_C']['sharpe_net']:.3f}",
        f"- Naive-self baseline Sharpe net: {r['baselines']['naive_self_sharpe_net']:.3f}",
        f"- Random-entry matched-turnover null: mean {r['baselines']['random_entry_matched_turnover_null']['null_mean']:.3f}, "
        f"p95 {r['baselines']['random_entry_matched_turnover_null']['null_p95']:.3f}, "
        f"observed {r['baselines']['random_entry_matched_turnover_null']['observed_sharpe']:.3f}, "
        f"P(obs≤null max) {r['baselines']['random_entry_matched_turnover_null']['p_obs_le_null_max']:.3f}",
        "",
        "## Frozen decision inputs (precommit §7)",
        "",
    ]
    for k, v in di.items():
        lines.append(f"- {k}: **{v}**")
    lines += [
        "",
        f"All advance-conditions met: **{advances}**.",
        "",
        "This artifact records statistics against the pre-stated decision rule. The verdict "
        "(`EARNS_A_SCAFFOLD` / `DOES_NOT_EARN_A_SCAFFOLD` / `INSUFFICIENT_POWER` / "
        "`COST_FINANCING_DEFEATED`) is assigned in the Phase-3 interpretation memo, not here. "
        "Freeze intact; nothing approved; lockbox untouched.",
    ]
    (OUT_DIR / "vol_managed_tsmom_screen.md").write_text("\n".join(lines))


if __name__ == "__main__":
    main()
