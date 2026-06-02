# Crypto Family E — Exploratory Diagnostics 001 — Plan (Phase 0)

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Branch:** `main` (worked directly on main; no branch/worktree)
**Date:** 2026-06-02
**Type:** Exploratory diagnostics ONLY. **Not** a campaign, strategy, front gate, tuning, or paper/demo/live sprint. No approval.

---

## 1. Current repo state (truth audit)

| Check | Result |
|-------|--------|
| Current branch | `main` |
| Working tree | clean (verified before Phase 0 commit) |
| `origin/main` | fetched; 0 commits behind |
| FX programme | archived/closed — not reopened, not modified |
| `configs/approved_strategies.yaml` | `approved: []` (verified empty) |
| Paper/demo/live | blocked — `check_research_freeze.py` confirms loops refuse |
| Crypto campaign / strategy / front gate / approval | none exist |
| Universe | BTC/USD + ETH/USD (perps `BTC_PERP_USD`, `ETH_PERP_USD`) only — no altcoins |
| Family C Trend Persistence | `STATISTICAL_ONLY_COST_DEFEATED` |
| Family B Relative Value | `STATISTICAL_ONLY_COST_DEFEATED` |
| Family E derivatives data prep | complete |
| Derivatives backfill | complete (diagnostics 1–3, 6, 7 data-ready) |
| Derivatives cost model | FROZEN (`CRYPTO_DERIVATIVES_COST_MODEL_001.md`) |

### Baseline validation (Phase 0 step 11)

| Command | Result |
|---------|--------|
| `pytest tests/ -q` | **2543 passed** in 42s |
| `check_research_freeze.py` | **ALL CHECKS PASSED** |
| `validate_research_archive.py` | **ALL CHECKS PASSED** (747 evidence links resolve) |
| `scan_artifacts_for_secrets.py` | **PASSED** |
| `ruff check src tests scripts research` | **60 errors, all PRE-EXISTING** in prior-sprint files (none in files this sprint creates) |

**Pre-existing ruff failures** (documented, unrelated to this sprint): `research/crypto/diagnostics/{relative_value,trend_persistence}.py`, `research/crypto/{validation,trend_persistence,coinbase}.py`, `research/nonusd_cross_population/_cost_baseline.py`, `research/edge_discovery/vol_managed_tsmom.py`, several `scripts/run_*` and `tests/*` files. All new code in this sprint must be ruff-clean; this baseline count must not increase.

---

## 2. Data-readiness audit

Data lives as **gitignored** CSVs under `research/crypto/derivatives/backfill/<inst>/` (regenerable via `scripts/backfill_crypto_derivatives.py --execute-public-fetch`). Files verified present for BTC_PERP_USD and ETH_PERP_USD:

| Series | File | Rows (each inst) | Window | Status |
|--------|------|------------------|--------|--------|
| Funding (1h realized) | `funding.csv` | 56,186 | 2020-01-01 → 2026-06-02 | ~99.86% cov, 79 gaps, logged-not-interpolated |
| Index (1h) | `index_h1.csv` | 56,186 | same | PASS |
| Perp OHLCV H1 | `ohlcv_h1.csv` | 56,267 | same | PASS |
| Perp OHLCV D1 | `ohlcv_d1.csv` | 2,345 | same | PASS |
| Basis H1 | `basis_h1.csv` | 56,186 | same | PASS (USD, perp_close − index_close) |
| OI daily | `oi_daily.csv` | 180 | 2025-12-05 → 2026-06 | **SHALLOW** (OKX rubik venue-aggregate USD notional) |

**Funding cadence note:** Deribit funding is **continuous/hourly-realized** (`funding_interval_hours = 1`). 8h-cadence diagnostics resample by **summing** `interest_1h` over 8h windows. Not pooled with native-8h venues.

**OI caveat:** only ~180d aggregate daily OI — diagnostics 4/5 are **low-power** by construction and default to `blocked_low_power_oi` / `exploratory_low_power_only`.

---

## 3. Exact diagnostics to run

| # | Diagnostic | Data | Power | Phase |
|---|-----------|------|-------|-------|
| 1 | Funding mean reversion | funding + perp OHLCV | high | 4 |
| 2 | Funding trend continuation | funding + perp OHLCV | high | 4 |
| 3 | Basis compression / expansion | basis_h1 + perp OHLCV | high | 4 |
| 6 | Cross-asset confirmation (BTC↔ETH) | funding + basis, both assets | high | 4 |
| 7 | Regime conditioning (applied to 1–3) | above + regime vars | high | 6 |
| 4 | OI impulse | OI daily + perp OHLCV | **low** | 5 |
| 5 | Funding/OI interaction | funding + OI + perp OHLCV | **low** | 5 |

### Diagnostics deferred / caveated

- **4 & 5**: run only as explicitly-labeled low-power on ~180d aggregate OI. They may **not** reach `candidate_for_front_gate` unless the doc directly justifies why the shallow sample is sufficient (default: it is not). Preferred labels: `blocked_low_power_oi` or `exploratory_low_power_only`.

---

## 4. Pre-registered thresholds & quantile definitions

Frozen in detail in `CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md` (Phase 1, written **before** any results are read). Summary:

- **Funding extremes:** top/bottom decile of the 8h-summed funding rate, computed per-instrument on the eligible sample.
- **Funding persistence k ∈ {3, 6, 9}** settlements (same-sign).
- **Basis extremes:** top/bottom decile of `basis_bps`.
- **Horizons:** D1 funding/D2 = 8h/24h/72h (diag 1), 24h/72h (diag 2), 4h/24h (diag 3), 8h/24h (diag 6).
- **Regimes (frozen before reading base results):** prior-24h realized-vol tercile; prior-7d perp-return trend sign/magnitude; absolute-funding tercile; basis tercile.

---

## 5. Null-baseline plan

For every diagnostic, the observed effect must clear a **matched null band**, not merely be non-zero:

- **matched-random entries** at the same timestamps/frequency;
- **shuffled-timestamp** signal→forward-return mapping;
- **randomized sign/rank** of the signal;
- **wrong-pairing null** for basis & cross-asset (BTC basis vs ETH return, and vice-versa).

All nulls use **deterministic seeds**, recorded in artifacts.

---

## 6. Cost / funding treatment

Frozen `CRYPTO_DERIVATIVES_COST_MODEL_001.md` (immutable for this sprint):

- Round-trip all-in = `2×half_spread + 2×slippage + taker_rt`. BTC H1/8h = **16 bps**, ETH = **18 bps**; 2× stress BTC = **32 bps**.
- **Funding cashflow** (the distinguishing perp cost): when `funding_rate > 0`, **longs pay shorts**. Any hold across funding intervals includes realized funding = Σ(`interest_1h` × notional) with that sign (`derivatives_models.funding_cashflow`).
- Variants reported per diagnostic: **gross / spread-only / all-in / 2× stress**.
- **The cost model is NOT adjusted based on diagnostic outcomes.**

---

## 7. Multiple-comparisons plan

- **Holm** adjustment (or documented equivalent) applied across diagnostics × horizons × assets × regimes.
- Raw p-values reported too, but **classification respects the adjusted / forking-path interpretation**.
- Regime conditioning (diag 7) is the highest forking-path risk — regime definitions are frozen in the run spec before base results are read.

---

## 8. Classification labels (pre-committed)

`rejected` · `statistical_only_cost_defeated` · `cost_defeated` · `candidate_for_front_gate` · `blocked_data_quality` · `blocked_low_power_oi`

`candidate_for_front_gate` requires **all**: clears matched null after multiple-comparisons adjustment; all-in net-positive; 2× stress net-positive; BTC-only **and** ETH-only both directionally supportive; pooled supportive; sufficient observations; not dependent on a small regime slice; not OI-depth-limited. **Even then the sprint stops at `candidate_for_front_gate`** — no campaign/strategy/front gate/approval.

Honest prior given Family C & B both `STATISTICAL_ONLY_COST_DEFEATED`: most diagnostics land `rejected` or `statistical_only_cost_defeated`.

---

## 9. No-strategy / no-campaign / no-front-gate / no-approval rules

- Do not create a campaign / strategy / front gate.
- Do not approve anything; do not edit `approved_strategies.yaml` except to verify it stays empty.
- Do not enable paper/demo/live.
- Do not call trading/order/account/private APIs; no API keys; no private endpoints; no leverage assumptions.
- Do not introduce altcoins or expand beyond BTC/ETH.
- Do not tune thresholds after seeing results; do not invent new hypotheses post-hoc; do not adjust the cost model from outcomes.
- Do not run a train/validation/test strategy backtest. Do not create CAMPAIGN_032.
- Do not commit raw bulky data, caches, `.env`, keys, DB files, or heavy artifacts.

---

## 10. Blocked conditions

- If any required series (funding/OHLCV/index/basis for BTC or ETH) is missing and not regenerable → `blocked_data_quality` doc, stop that diagnostic.
- OI diagnostics default to `blocked_low_power_oi` / `exploratory_low_power_only`.

---

## 11. Expected deliverables

- `CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md` (Phase 1, pre-registration).
- Runner `scripts/run_crypto_family_e_exploratory_diagnostics.py` + helpers under `research/crypto/family_e/` + tests (Phase 2).
- `CRYPTO_FAMILY_E_DATA_READINESS_AUDIT_001.md` (Phase 3).
- Per-diagnostic result docs 1/2/3/6 (Phase 4), 4/5 (Phase 5), 7 (Phase 6).
- Compact JSON artifacts under `research/crypto/family_e_diagnostics/`.
- `CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md` (Phase 7).
- Roadmap/README/status updates (Phase 8).
- Next-prompt doc (Phase 9).
- `CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001_SUMMARY.md` (Phase 10).

---

## Safety confirmations (start of sprint)

| Item | Status |
|------|--------|
| FX remains closed/archived | ✓ (not touched) |
| Research freeze intact | ✓ |
| Paper/demo/live blocked | ✓ |
| No trading/order/private API; no keys | ✓ |
| No bulky raw data in git | ✓ (backfill CSVs gitignored) |
| No strategy/campaign/front-gate/approval | ✓ |
| BTC/ETH only | ✓ |
| `approved: []` | ✓ |
| Cost model frozen | ✓ |
