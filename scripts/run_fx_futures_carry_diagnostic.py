"""Runner: FX-futures carry diagnostic (research-only, decision-forcing).

Phases 2-4 of research-fx-futures-carry-diagnostic-001:
  - ingest free/local CME FX-futures continuous EOD (Yahoo) [network]
  - build monthly USD-per-currency futures levels + coverage report
  - run the FROZEN carry factor on futures returns (PRIMARY: cached 61-mo signal
    incl. JPY; DEEP: live FRED, JPY-excluded)
  - null battery on the primary cell

Writes JSON artifacts under research/fx_futures/diagnostic/. NO trades, NO
strategy, NO approval. Network steps require connectivity; pass --offline to
reuse already-ingested raw data.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
from research.fx_futures import carry_diagnostic as DIAG  # noqa: N812
from research.fx_futures import continuous, fred, ingest

RAW_DIR = Path("research/fx_futures/raw")
DEEP_DIR = Path("research/fx_futures/raw_fred")
OUT_DIR = Path("research/fx_futures/diagnostic")
CACHED_SIGNAL = Path("research/carry/factor_validation/signal_currency_rate_lag1.csv")


def load_cached_signal() -> pd.DataFrame:
    df = pd.read_csv(CACHED_SIGNAL)
    df["month"] = pd.to_datetime(df["month"])
    return df.set_index("month")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--offline", action="store_true", help="reuse ingested raw data")
    ap.add_argument("--fetched-on", default="2026-05-31")
    ap.add_argument("--n-draws", type=int, default=2000)
    args = ap.parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # ---- ingest / load futures ------------------------------------------------
    if not args.offline or not (RAW_DIR / "provenance.json").exists():
        manifest = ingest.ingest(RAW_DIR, fetched_on=args.fetched_on)
    else:
        manifest = json.loads((RAW_DIR / "provenance.json").read_text())
    raw = ingest.load_raw(RAW_DIR)
    usd_levels = continuous.month_end_levels(raw)
    cov = continuous.coverage_report(usd_levels)
    (OUT_DIR / "coverage.json").write_text(json.dumps(
        {"provenance": manifest, "coverage": cov}, indent=2))

    # ---- PRIMARY: cached frozen signal (incl. JPY), 61-mo window --------------
    signal = load_cached_signal()  # cols: EUR,GBP,JPY,AUD,NZD,CHF,CAD
    primary = DIAG.run_diagnostic(signal, usd_levels, yield_signal=None,
                                  n_draws=args.n_draws, run_nulls=True)
    primary["drop_one_currency_h3"] = DIAG.drop_one_currency(signal, usd_levels, h=3)
    (OUT_DIR / "primary.json").write_text(json.dumps(primary, indent=2, default=float))

    # ---- DEEP: live FRED (JPY-excluded), full futures window ------------------
    deep_result = None
    try:
        if not args.offline or not (DEEP_DIR / "_deep_rate_matrix.csv").exists():
            rate_mat = fred.fetch_deep_rates(DEEP_DIR, fetched_on=args.fetched_on)
        else:
            rate_mat = fred.load_deep_rates(DEEP_DIR)
        # build lag-1 signal over the non-USD reachable currencies
        nonusd = [c for c in rate_mat.columns if c != "USD"]
        deep_signal = rate_mat[nonusd].shift(1)  # lag 1 month (FROZEN)
        deep_levels = usd_levels[[c for c in usd_levels.columns if c in (["USD"] + nonusd)]]
        deep_result = DIAG.run_diagnostic(deep_signal.dropna(how="all"), deep_levels,
                                          yield_signal=None, n_draws=args.n_draws,
                                          run_nulls=True)
        deep_result["jpy_excluded"] = True
        deep_result["note"] = ("FRED IR3TIB01JPM156N retired (404); deep run is "
                               "JPY-excluded breadth test over full futures history")
        deep_result["drop_one_currency_h3"] = DIAG.drop_one_currency(
            deep_signal.dropna(how="all"), deep_levels, h=3)
        (OUT_DIR / "deep.json").write_text(json.dumps(deep_result, indent=2, default=float))
    except Exception as e:
        (OUT_DIR / "deep_error.json").write_text(json.dumps(
            {"error": type(e).__name__, "msg": str(e)[:200]}, indent=2))

    # ---- console summary ------------------------------------------------------
    pc = primary["cells"][f"h{DIAG.PRIMARY_H}"]
    print("=== FX FUTURES CARRY DIAGNOSTIC ===")
    print(f"coverage: {cov['n_months']} months {cov['first']}..{cov['last']} "
          f"(missing={cov['missing_months']})")
    print(f"PRIMARY h3 mean={pc['mean']:.6f} nw_t={pc['nw_t']:.3f} "
          f"sign={pc['sign_consistency']:.3f} n={pc['n']}")
    nz = primary["nulls"]
    print(f"  nulls: rand_ranks Z={nz['randomized_ranks']['z']:.2f} "
          f"shuf_ts Z={nz['shuffled_timestamp']['z']:.2f} "
          f"matched_rand Z={nz['matched_random']['z']:.2f}")
    print(f"  drop-JPY h3={primary['drop_one_currency_h3'].get('drop_JPY'):.6f} "
          f"full={primary['drop_one_currency_h3'].get('full'):.6f}")
    if deep_result is not None:
        dc = deep_result["cells"]["h3"]
        print(f"DEEP (ex-JPY) {deep_result['n_months']} months h3 mean={dc['mean']:.6f} "
              f"nw_t={dc['nw_t']:.3f}")
    print("written:", OUT_DIR)


if __name__ == "__main__":
    main()
