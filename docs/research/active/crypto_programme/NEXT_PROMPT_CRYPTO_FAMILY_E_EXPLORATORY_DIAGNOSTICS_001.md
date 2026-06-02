# Next Prompt — Crypto Family E Exploratory Diagnostics 001

**Precondition:** Start this sprint **only after** the derivatives data readiness gate in `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md` is met (full BTC+ETH funding backfill validated; perp OHLCV + USD-quoted reference available where a diagnostic needs them; a **frozen derivatives cost model** written). If the gate is not met, the next sprint is derivatives **backfill**, not diagnostics.

---

We are starting the Crypto Family E exploratory diagnostics sprint.

Work directly on `main`. Commit after each meaningful phase.

## Hard rules

- **Do not create a campaign.**
- **Do not create a strategy.**
- **Do not create a front gate.**
- **Do not approve anything**; do not edit `configs/approved_strategies.yaml`.
- **Do not enable paper/demo/live.**
- **Do not call trading/order/account/private APIs; no API keys.**
- **Run exploratory diagnostics only.**
- **Use BTC and ETH only.** No altcoins, no universe expansion.
- Do not treat any result as tradable edge. A statistically-real effect is not an edge.
- Do not tune or revive Family C or Family B.

## What to do

1. Confirm the data-readiness gate (funding/OHLCV/basis/OI coverage) and the frozen derivatives cost model exist; if not, stop and run backfill instead.
2. Use the **pre-registered hypotheses** in `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md` — do not invent new ones post-hoc. Pre-register thresholds and regime definitions before reading results.
3. For each diagnostic run:
   - compare against **matched nulls** (matched-random, shuffled-timestamp, randomized sign/rank — and wrong-pairing null for basis/cross-asset);
   - include **conservative costs and funding cashflows** (gross, spread-only, all-in, 2× stress; funding sign: long pays short when funding_rate > 0);
   - report **BTC-only, ETH-only, and pooled** — flag single-asset artifacts;
   - apply multiple-comparisons discipline (Holm / forking-path) across horizons and regime cells.
4. Classify each diagnostic with the pre-committed labels: **rejected**, **statistical_only_cost_defeated**, **cost_defeated**, or **candidate_for_front_gate**.
5. Write per-diagnostic result docs + a synthesis, and a next-prompt stub.

## Order of attack

Diagnostics 1–2 (funding-only) are closest to runnable; 3–7 require additional backfill (basis, OI history) and may be deferred or run low-power with documented coverage limits.

## Expected outcome

Given Family C and Family B both closed `STATISTICAL_ONLY_COST_DEFEATED`, the honest prior is that most Family E diagnostics land **rejected** or **statistical_only_cost_defeated**. A `candidate_for_front_gate` requires a real effect that is **net-positive after 2× stress and robust across BTC and ETH** — and even then it earns only a future pre-registered front-gate screen, never a campaign or approval from exploratory results.

## Scaffolding available

- `research/crypto/derivatives_registry.py`, `derivatives_models.py` (incl. `funding_cashflow`, `compute_basis`), `derivatives_sources.py` (public parsers), `derivatives_validation.py`.
- `scripts/ingest_crypto_derivatives_public_data.py` (dry-run default; OKX funding/OI wired; extend for perp OHLCV / mark-index / USD reference before use).
- `scripts/validate_crypto_derivatives_store.py`.
- Source hierarchy + geo constraints: `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md` (Binance/Bybit geo-blocked here; OKX/Deribit reachable).

Paper/demo/live remain blocked. `configs/approved_strategies.yaml` remains empty.
