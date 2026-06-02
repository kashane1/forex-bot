# Crypto Derivatives Backfill 001 — Summary

**Sprint:** `crypto-derivatives-backfill-001`
**Branch:** `main`
**Date:** 2026-06-02
**Type:** Public-data backfill + frozen cost model ONLY. No factor, front gate, campaign, strategy, or approval.

---

1. **Branch:** `main` (worked directly; no branch/worktree).

2. **Commit hashes by phase:**

| Phase | Commit | Title |
|-------|--------|-------|
| 0 | `af949b6` | plan — Deribit-primary deep backfill |
| 1–2 | `9bae85b` | Deribit/OKX-rubik adapters + backfill scaffold |
| 3–5 | `1b971df` | executed backfill + frozen perp cost model |
| 6–8 | (this summary) | result, readiness gate, indexes, final validation |

3. **Why this sprint:** It was the recommended next step after `crypto-family-e-derivatives-data-prep-001` — turn the public-data scaffolding into a real, validated, BTC/ETH-only derivatives dataset and freeze a perp cost model, so the Family E diagnostics readiness gate can be met.

4. **Source decision (revised at runtime):** Binance (451) and Bybit (403) stayed geo-blocked; OKX funding/OI history proved shallow. Endpoint probing chose **Deribit** (USD inverse perps) as canonical for funding/index/perp-OHLCV — reachable, USD-quoted (no USDT confound), deep to ~2019, ~744 rows/call, with hourly `index_price` carried free in the funding payload. **OKX `rubik`** supplied ~180d daily aggregate OI (the residual gap).

5. **Data backfilled (2020-01-01 → 2026-06-02, both BTC_PERP_USD and ETH_PERP_USD):**

| Class | Rows/instrument | Status |
|-------|-----------------|--------|
| Funding (hourly realized, USD) | 56,186 | WARN (79 gaps; 99.86% coverage) |
| Index (hourly, USD) | 56,186 | PASS |
| Perp OHLCV H1 (USD) | 56,267 | PASS |
| Perp OHLCV D1 (USD) | 2,345 | PASS |
| Basis H1 (derived, bps) | 56,186 | PASS |
| Open interest (daily, USD-notional aggregate) | 180 | PASS |

Overall validation **WARN** — solely from minor funding gaps + shallow OI (both logged, not interpolated). Sanity: funding mildly positive (longs pay), basis median +2.4 bps (mild contango) — plausible, **no edge claimed**.

6. **Frozen cost model:** `CRYPTO_DERIVATIVES_COST_MODEL_001.md` — perp taker 10 bps round-trip, half-spread 2/3 bps BTC/ETH, horizon slippage, and the funding cashflow sign convention (long pays short when funding_rate > 0). Immutability rule applied.

7. **Code added:** Deribit + OKX-rubik parsers in `research/crypto/derivatives_sources.py`; `research/crypto/derivatives_backfill.py` (pure chunking helpers); `scripts/backfill_crypto_derivatives.py` (dry-run default, `--execute-public-fetch`, BTC/ETH-only + credential guards).

8. **Tests:** **+8** (Deribit funding/index/chart parsers, OKX OI-volume parser, time-window chunking edge cases). **Storage / git policy:** Normalized CSVs under `research/crypto/derivatives/backfill/<inst>/` — **gitignored**. Committed: backfill manifest + validation summary JSON + docs. No raw payloads, CSVs, DB files, or credentials staged (verified).

9. **Factor diagnostic run?** **No.**

10. **Strategy created?** **No.** **Campaign?** **No.** **Front gate?** **No.** **Approval?** **No.**

11. **Trading/private/order API used?** **No** — public market-data only; no keys required or present.

12. **BTC/ETH-only preserved?** **Yes** — registry + script guards refuse anything else.

13. **`approved: []` empty?** **Yes.** **Paper/demo/live blocked?** **Yes.** **FX touched?** **No.**

14. **Validation results:**
    - `pytest tests/ -q` → **2543 passed** (prior 2535; +8).
    - `check_research_freeze.py` → **PASS** · `validate_research_archive.py` → **PASS** · `scan_artifacts_for_secrets.py` → **PASSED**.
    - `ruff` on the 4 new/changed sprint files → **clean**; full repo count unchanged at 60 pre-existing.
    - `git status` → clean; branch `main`.

15. **Residual gaps:** deep per-instrument OI history still missing (only ~180d aggregate free) — diagnostics 4/5 low-power until forward-collection; Deribit funding is continuous/hourly (resample to 8h at diagnostics time); 79 hourly funding gaps each.

16. **Family E readiness:** **MET for diagnostics 1–3, 6, 7** (funding/basis/OHLCV, 6.4y, USD + frozen cost model); 4/5 low-power.

17. **Recommended next sprint:** **Crypto Family E exploratory diagnostics** — run pre-registered diagnostics 1–3 (and 6/7) per `NEXT_PROMPT_CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001.md`: matched nulls, gross/spread/all-in/2× costs **with funding cashflows**, BTC-only/ETH-only/pooled, classify rejected / statistical-only / cost-defeated / candidate. Exploratory only — no campaign/strategy/approval. Honest prior given C+B: likely rejected or statistical-only.

18. **Files to review first:** `CRYPTO_DERIVATIVES_BACKFILL_001_PLAN.md` → `..._RESULT.md` → `CRYPTO_DERIVATIVES_COST_MODEL_001.md` → `NEXT_PROMPT_CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001.md`; code `scripts/backfill_crypto_derivatives.py`, `research/crypto/derivatives_{sources,backfill}.py`.

---

## Safety confirmations

| Item | Status |
|------|--------|
| FX closed/archived, untouched | ✓ |
| Research freeze intact | ✓ |
| Paper/demo/live blocked | ✓ |
| No trading/order/private API; no keys | ✓ (public-only) |
| No bulky raw/CSV/DB in git | ✓ (gitignored; manifests/summary only) |
| No strategy/campaign/front-gate/approval | ✓ |
| BTC/ETH only | ✓ |
| `approved: []` | ✓ |
