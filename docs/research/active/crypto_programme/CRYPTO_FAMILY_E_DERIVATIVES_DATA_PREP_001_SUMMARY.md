# Crypto Family E — Derivatives / Funding / OI Data Prep 001 — Summary

**Sprint:** `crypto-family-e-derivatives-data-prep-001`
**Branch:** `main`
**Date:** 2026-06-02
**Type:** Data preparation + diagnostics infrastructure ONLY. No factor, front gate, campaign, strategy, or approval.

---

1. **Current branch:** `main` (worked directly on main; no branch/worktree).

2. **Commit hashes by phase:**

| Phase | Commit | Title |
|-------|--------|-------|
| 0 | `c8913e3` | plan + truth audit |
| 1 | `ab4646a` | public derivatives data source review |
| 2 | `35f859a` | derivatives data model + provenance design |
| 3 | `e9e877a` | registry, public source adapters, dry-run ingest |
| 4 | `7ac9cb4` | validation tooling + policy + manifests |
| 5 | `b1f4e41` | tiny public derivatives pilot (OKX BTC/ETH funding + OI) |
| 6 | `6abfd9c` | Family E exploratory diagnostic design (no execution) |
| 7 | `4f8e14d` | next prompt for Family E exploratory diagnostics |
| 8 | (this summary) | final validation + summary |

3. **Crypto programme state at start:** BTC/USD + ETH/USD only; Stage 1 design + Stage 2 spot ingestion complete (Coinbase spot, M1 + materialized M5–D1); Stage 3 diagnostics in progress; Family C **STATISTICAL_ONLY_COST_DEFEATED**; Family B **STATISTICAL_ONLY_COST_DEFEATED**; no campaign/strategy; `approved: []`; paper/demo/live blocked; FX archived.

4. **Why Family E prep over Family D:** Families C and B were both spot-OHLCV-based and both cost-defeated. Family D (non-time bars) mostly re-samples the same spot OHLCV — no new information. Family E adds genuinely crypto-native derivatives data (funding, OI, basis, perp OHLCV) the repo did not have. Family D is deferred, not rejected.

5. **Public data sources reviewed:** Binance USDⓈ-M, Binance COIN-M, Bybit v5, OKX v5, Kraken Futures, Deribit, Coinbase International, and CCXT (as an adapter) — compared on perp symbol mapping, funding history, open interest, mark/index, basis feasibility, perp OHLCV, timestamps, rate limits, historical depth, public/free status, redistribution suitability, and caveats.

6. **Selected source / hierarchy:** Primary funding+mark+perp-OHLCV = **Binance USDⓈ-M**; OI history = **Bybit v5**; USD-quoted cross-check = **Kraken Futures**; tertiary = OKX/Deribit. **Direct `httpx` chosen over CCXT** (matches repo convention, keeps the public-endpoint allowlist enforceable). **Runtime reality (Phase 5):** Binance (451) and Bybit (403) are geo-blocked from this host; the pilot used **OKX** public v5 per the documented failover. Open-interest deep history is the binding free-data gap across all venues.

7. **Data model implemented/documented:** `CRYPTO_DERIVATIVES_DATA_MODEL.md` — canonical perps `BTC_PERP_USD`/`ETH_PERP_USD` with venue-native symbols stored separately; logical datasets `perp_ohlcv`, `funding_rates`, `open_interest`, `mark_index_price`, `basis` (derived), `provenance`/`fetch_manifests`; UTC interval-end timestamp policy for funding/OI; data-quality rules; funding cashflow sign convention; cost placeholders (no execution); git policy. No DB migration forced — dataclass + manifest loader contract is the deliverable.

8. **Registry / source adapter changes:** `research/crypto/derivatives_registry.py` (BTC/ETH-only perp registry, canonical↔venue maps, guards), `research/crypto/derivatives_models.py` (record dataclasses + `funding_cashflow` + `compute_basis`), `research/crypto/derivatives_sources.py` (public-endpoint allowlist, credential refusal, venue parsers for Binance/Bybit/OKX + `count_payload_rows`), `scripts/ingest_crypto_derivatives_public_data.py` (dry-run default, `--execute-public-fetch` gated, BTC/ETH-only + credential guards).

9. **Validation tooling added:** `research/crypto/derivatives_validation.py` (PASS/WARN/FAIL per data class), `scripts/validate_crypto_derivatives_store.py` (fixture self-check + manifest summary), `CRYPTO_DERIVATIVES_VALIDATION_POLICY.md`, manifest format.

10. **Synthetic fixtures / tests added:** fixtures for Binance funding/perp-klines/mark-klines, Bybit OI, OKX funding/OI. **46 new tests** across registry, sources, validation, and ingest (symbol mapping, public allowlist, dry-run default, unknown/altcoin refusal, credential refusal, funding-direction convention, timestamp parsing, duplicate dedup, OHLCV sanity, OI availability, basis). Full suite **2535 passed** (baseline 2489).

11. **Pilot result:** **Succeeded** via OKX (failover). BTC + ETH 8h funding (30 rows each, 2026-05-23T16:00→2026-06-02T08:00) + BTC OI snapshot — all validated **PASS**, no credentials. See `CRYPTO_DERIVATIVES_PUBLIC_DATA_PILOT_RESULT.md`. Basis deferred (USDT-vs-USD confound). No pilot-blocked doc needed.

12. **Full backfill run?** **No.** Only the tiny pilot (90 funding rows + 1 OI snapshot). Full backfill is a future sprint, gated on data readiness.

13. **Factor diagnostic run?** **No.**

14. **Strategy created?** **No.**

15. **Campaign created?** **No.**

16. **Front gate created?** **No.**

17. **Trading/private/order API used?** **No** — public market-data only; no API keys required or present.

18. **BTC/ETH-only scope preserved?** **Yes** — registry guards refuse any non-BTC/ETH perp; parsers refuse unauthorized symbols.

19. **Approved strategies remain empty?** **Yes** — `approved: []`.

20. **Paper/demo/live remain blocked?** **Yes.**

21. **Validation commands and results:**
    - `pytest tests/ -q` → **2535 passed**
    - `check_research_freeze.py` → **ALL CHECKS PASSED**
    - `validate_research_archive.py` → **ALL CHECKS PASSED**
    - `scan_artifacts_for_secrets.py` → **PASSED**
    - `ruff check src tests scripts research` → 60 errors, **all pre-existing** in prior-sprint files; the 10 new files in this sprint are **ruff-clean** (count unchanged from baseline 60).
    - `git status --short` → clean.

22. **Known data-source caveats:** Binance/Bybit geo-blocked from this host (451/403); deep free **OI history** unavailable (snapshots only) — likely forward-collection; OKX/Binance/Bybit linear perps are **USDT-quoted** (≠USD without basis adjustment); Kraken `v3 PI_*` deprecated → `v4 PF_*`; Deribit funding is continuous/hourly (not pooled with 8h venues).

23. **Remaining blockers (for diagnostics):** full BTC+ETH funding backfill not yet run; perp OHLCV + mark/index endpoints not yet wired/backfilled; USD-quoted basis series absent; OI history gap; a **frozen derivatives cost model** must be written before diagnostics; canonical store binding (Postgres vs parquet) deferred.

24. **Family E exploratory diagnostics ready?** **Not yet.** The data-prep layer (registry/sources/validation/pilot) is in place, but the data-readiness gate in `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md` is not met. Diagnostics 1–2 (funding-only) are closest to runnable after a funding backfill.

25. **Recommended next sprint:** **Crypto derivatives backfill** — full BTC+ETH funding (+ perp OHLCV, mark/index, a USD-quoted reference for basis) under the geo constraint (OKX/Deribit reachable), resolve the OI-history gap, and write+freeze the derivatives cost model. **Then** `NEXT_PROMPT_CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001.md`.

26. **Files to review first:**
    1. `CRYPTO_FAMILY_E_DERIVATIVES_DATA_PREP_001_PLAN.md`
    2. `CRYPTO_DERIVATIVES_PUBLIC_DATA_SOURCE_REVIEW.md`
    3. `CRYPTO_DERIVATIVES_DATA_MODEL.md`
    4. `CRYPTO_DERIVATIVES_PUBLIC_DATA_PILOT_RESULT.md`
    5. `CRYPTO_FAMILY_E_DIAGNOSTIC_DESIGN.md`
    6. `NEXT_PROMPT_CRYPTO_FAMILY_E_EXPLORATORY_DIAGNOSTICS_001.md`
    7. code: `research/crypto/derivatives_{registry,models,sources,validation}.py`, `scripts/ingest_crypto_derivatives_public_data.py`, `scripts/validate_crypto_derivatives_store.py`

---

## Safety confirmations

| Item | Status |
|------|--------|
| FX remains closed/archived | ✓ (not touched) |
| Research freeze intact | ✓ |
| Paper/demo/live blocked | ✓ |
| No trading/order/private API; no keys | ✓ (public-only) |
| No bulky raw data in git | ✓ (raw gitignored; manifests/fixtures only) |
| No strategy/campaign/front-gate/approval | ✓ |
| BTC/ETH only | ✓ |
| `approved: []` | ✓ |
