# Crypto Family E — Exploratory Diagnostics 001 — Summary

**Sprint:** `crypto-family-e-exploratory-diagnostics-001`
**Date:** 2026-06-02
**Type:** Exploratory diagnostics only. No strategy, campaign, front gate, or approval.

---

1. **Current branch:** `main` (worked directly on main; no branch/worktree).

2. **Commit hashes by phase:**

| Phase | Commit | Title |
|-------|--------|-------|
| 0 | `11d9af6` | plan + truth audit |
| 1 | `078a530` | frozen run spec (pre-registration) |
| 2 | `6c5ae2f` | runner + helpers + 21 tests |
| 3 | `ca28b48` | data-readiness audit (preflight) |
| 4 | `1e601dd` | high-power results 1/2/3/6 |
| 5 | `51c7e67` | OI diagnostics 4/5 (low-power) |
| 6 | `90ffc6b` | regime conditioning (diag 7) + notable-cell audit |
| 7 | `80a034e` | synthesis + decision |
| 8 | `621d26c` | roadmap/status updates |
| 9 | `aab307d` | next prompt (pause synthesis) |
| 10 | (this summary) | final validation + summary |

3. **Crypto state at start:** BTC/USD + ETH/USD only; Stage 1–2 complete; Family C & B both `STATISTICAL_ONLY_COST_DEFEATED`; Family E derivatives data-prep + backfill complete; frozen perp cost model; `approved: []`; paper/demo/live blocked; FX archived.

4. **Data-readiness audit result:** PASS for high-power diagnostics (BTC+ETH 6,953 complete 8h funding windows, 56,186 basis rows, 56,267 H1 OHLCV, 6.4y USD-quoted). WARN/low-power for OI (180d aggregate daily only). See `CRYPTO_FAMILY_E_DATA_READINESS_AUDIT_001.md`.

5. **Run spec summary:** `CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md` — frozen **before** results: instruments/venue, 8h funding resample (sum of hourly, no lookahead), open-to-open forward returns, decile/persistence thresholds, horizons, frozen regimes (vol/trend/abs-funding/basis terciles), matched/shuffled/sign/wrong-pairing nulls (seed 20260602, 1000 draws), cost variants + funding cashflow, Holm, and the `candidate_for_front_gate` gate.

6. **Diagnostics executed:** 1 funding mean reversion, 2 funding trend continuation, 3 basis compression/expansion, 6 cross-asset confirmation, 7 regime conditioning (on 1–3), plus 4/5 OI (low-power).

7. **Diagnostics skipped/deferred:** none skipped; 4 & 5 run only as explicitly low-power (`blocked_low_power_oi`).

8. **Diagnostic 1 — `rejected`.** Pooled gross within null (shuffled p 0.26–0.83); BTC mildly +, ETH opposite-signed (single-asset, not robust); all-in negative at 8/24/72h.

9. **Diagnostic 2 — `rejected`.** No monotone gradient across k∈{3,6,9}; continuation within null; best cell (k3/h24) all-in −0.0017.

10. **Diagnostic 3 — `rejected`.** Best raw shuffled p≈0.013–0.017 (h4) → Holm-adjusted 0.22–0.27 (does not clear); reversion AND expansion both raw-"significant" = forking-path artifact.

11. **Diagnostic 4 — `blocked_low_power_oi`.** Only 180d aggregate daily OI; cannot power an OI-impulse test.

12. **Diagnostic 5 — `blocked_low_power_oi`.** Same OI depth gap; interaction not over-interpreted; forward OI collection recommended.

13. **Diagnostic 6 — `rejected`.** Agreement (directional) and disagreement (relative-value) cohorts within null; paired cost-defeated; wrong-pairing control confirms no cross-asset information.

14. **Diagnostic 7 — `rejected`.** Notable cell = downtrend-conditioned funding mean reversion (pooled n=901, all-in +0.0036, 2× +0.0019; BTC 2× +0.0027, ETH 2× +0.0011 — BTC+ETH both supportive, both 2×-stress-positive). **Fails the frozen candidate bar**: single regime slice on a *rejected* base diagnostic; full-family Holm borderline/failing. The basis-tercile cell is circular (regime variable = the diagnostic's own signal).

15. **Matched-null results summary:** Across diagnostics 1/2/6 the observed pooled edges sat inside the matched-null band (shuffled p ≫ 0.05). Diagnostic 3 produced raw p<0.05 at h4 but did not survive Holm. The only cells clearing nulls after adjustment were regime-conditional (and either circular or single-slice on a rejected base).

16. **Cost / funding / 2× stress summary:** Frozen `CRYPTO_DERIVATIVES_COST_MODEL_001.md` (BTC 16 bps / ETH 18 bps all-in RT at H1/8h; 2× = 32/36 bps; funding cashflow long-pays-short). All-in and 2× were net-negative for every base diagnostic; the only 2×-positive result was the sub-bar regime cell. **Cost model unchanged by results.**

17. **BTC-only vs ETH-only vs pooled robustness:** Diagnostic 1 base is single-asset (BTC +, ETH −). The notable regime cell is the only BTC+ETH-robust positive — but sub-bar. No base diagnostic was robustly positive across both assets net-of-cost.

18. **Multiple-comparisons / forking-path conclusion:** Holm across the high-power family removed diagnostic 3's raw significance. Regime conditioning surfaced the highest forking-path risk; the discipline (frozen regimes, Holm, single-slice gate, circularity flag) correctly prevented a sub-bar cell from being mislabeled a candidate.

19. **Any `candidate_for_front_gate`?** **No.**

20. **Any strategy created?** **No.**

21. **Any campaign created?** **No.**

22. **Any front gate created?** **No.**

23. **Approved strategies remain empty?** **Yes** — `approved: []`.

24. **Paper/demo/live remain blocked?** **Yes.**

25. **Validation commands and results:**
    - `pytest tests/ -q` → **2564 passed** (baseline 2543 + 21 new).
    - `check_research_freeze.py` → **ALL CHECKS PASSED**.
    - `validate_research_archive.py` → **ALL CHECKS PASSED** (6,317 artifact files; all evidence links resolve).
    - `scan_artifacts_for_secrets.py` → **PASSED**.
    - `ruff check src tests scripts research` → **60 errors, all pre-existing** (unchanged from baseline; the sprint's new files are ruff-clean).
    - `git status --short` → clean.

26. **Recommended next sprint:** `NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md` — a docs-only programme-pause synthesis (three families now miss the bar; Family D low-info; OI-collection low-value alone). Carries forward the downtrend-funding-reversion thread + forward-OI as conditional reopen paths under fresh pre-registration.

27. **Files to review first:**
    1. `CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md`
    2. `CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md` (frozen pre-registration)
    3. `CRYPTO_FAMILY_E_DATA_READINESS_AUDIT_001.md`
    4. `CRYPTO_FAMILY_E_DIAGNOSTIC_7_REGIME_CONDITIONING_RESULT.md` (notable-cell audit)
    5. `CRYPTO_FAMILY_E_DIAGNOSTIC_{1,2,3,6}_*_RESULT.md`, `_4_5_OI_LOW_POWER_RESULT.md`
    6. code: `research/crypto/family_e/`, `scripts/run_crypto_family_e_exploratory_diagnostics.py`, `tests/test_crypto_family_e_diagnostics.py`
    7. `NEXT_PROMPT_CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`

---

## Safety confirmations

| Item | Status |
|------|--------|
| Current branch `main`, tree clean | ✓ |
| FX not reopened | ✓ |
| BTC/ETH-only scope preserved; no altcoins | ✓ |
| No strategy / campaign / front gate / approval | ✓ |
| No paper/demo/live enablement | ✓ |
| No private/trading/order API; no API keys | ✓ (public data only; no network in runner) |
| No raw bulky data / `.env` / DB files committed | ✓ (backfill CSVs gitignored; only compact JSON + docs) |
| Cost model unchanged | ✓ (frozen) |
| Run spec committed BEFORE result docs | ✓ (Phase 1 `078a530` precedes Phase 4 `1e601dd`) |
| Classifications honest and match the gates | ✓ |
