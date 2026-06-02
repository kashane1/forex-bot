# Crypto Programme Pause Synthesis 001 — Summary

**Sprint:** `crypto-programme-pause-synthesis-001`
**Date:** 2026-06-02
**Type:** Docs-only programme synthesis + decision. No strategy, campaign, front gate, or approval.

---

1. **Branch:** `main` (no branch/worktree). Tree clean.

2. **Commit hashes by phase:**

| Phase | Commit | Title |
|-------|--------|-------|
| 0 | `d86a525` | plan + truth audit |
| 1–2 | `2b590f2` | synthesis + restart criteria |
| 3 | `0f1d577` | roadmap/README/status updates |
| 4 | (this summary) | final validation + summary |

3. **State at start:** Family C & B `STATISTICAL_ONLY_COST_DEFEATED`; Family E exploratory diagnostics `NO CANDIDATE`; `approved: []`; paper/demo/live blocked; FX archived; cost models frozen.

4. **Decision:** **`PAUSE_CRYPTO_RESEARCH`.** Three factor families failed the front-gate bar on the BTC/ETH corpus; further drilling has low expected information value.

5. **Failure-mode diagnosis:** C and B were **cost-defeated** (real gross structure, no edge after spread/fees — the FX S4 pattern). Family E shifted the binding constraint to **idea-quality / market efficiency**: on the *cheaper* perp venue (16–18 bps all-in), funding mean-reversion / continuation / cross-asset signals sit **within their matched nulls**, and the lone basis signal failed **full-family Holm** (forking-path), not cost. OI depth (180d) is a secondary limit affecting only diagnostics 4/5.

6. **Carried thread evaluated:** downtrend-conditioned funding mean reversion — the only net-positive-after-2× result in the programme (BTC+ETH both 2×-positive, within-regime Holm p≈0.032) — classified **notable-but-unproven**: single regime slice on a *rejected* base diagnostic, borderline/failing full-family Holm. Preserved for a *fresh, independently pre-registered* re-test with walk-forward only; **not run** here.

7. **OI forward-collection evaluated:** low value as a *next step* (high-power diagnostics failed on non-OI data); retained as a **conditional reopen path** (a new-data trigger), not a reason to re-drill 1/2/3/6.

8. **Options weighed:** front-gate design (rejected — no candidate), OI collection (not now), Family D (rejected — re-samples cost-defeated spot OHLCV), **pause (chosen)**.

9. **Deliverables:** `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md` (decision + inventory + diagnosis), `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md` (standing governance bar, mirrors FX), roadmap + README updates, superseded next-prompt, this summary.

10. **Restart bar:** documented in `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md` — requires ≥1 external trigger (new external thesis / new external data such as deep OI, order-flow, options, on-chain / structurally-different spec / slow non-latency mechanism) **plus** the full falsification panel (matched nulls, all-in + 2×, full-family MC, BTC+ETH robustness, walk-forward, structural distinctness). Threshold/timeframe/regime re-slicing and altcoin expansion are explicitly insufficient.

11. **Validation:**
    - `pytest tests/ -q` → **2564 passed** (no code changed this sprint).
    - `check_research_freeze.py` → **ALL CHECKS PASSED**.
    - `validate_research_archive.py` → **ALL CHECKS PASSED** (all new doc links resolve).
    - `scan_artifacts_for_secrets.py` → **PASSED**.
    - `ruff check src tests scripts research` → **60 errors, all pre-existing** (docs-only; unchanged).
    - `git status --short` → clean.

12. **Safety confirmations:**

| Item | Status |
|------|--------|
| Standing decision recorded | `PAUSE_CRYPTO_RESEARCH` |
| No strategy / campaign / front gate / approval | ✓ |
| `approved: []` | ✓ |
| Paper/demo/live blocked | ✓ |
| BTC/ETH only; no altcoins | ✓ |
| FX archive untouched | ✓ |
| Frozen cost models unchanged | ✓ |
| No code / no raw data / no `.env` / no DB committed | ✓ (docs-only) |

13. **Next sprint:** **None queued.** Crypto research is paused. The only sanctioned work until a restart trigger (per the restart-criteria doc) is non-strategy: external-data acquisition, external-thesis sourcing, or engineering — not factor mining on the current corpus.

14. **Files to review first:** `CRYPTO_PROGRAMME_PAUSE_SYNTHESIS_001.md`, `CRYPTO_STRATEGY_RESEARCH_RESTART_CRITERIA.md`, `CRYPTO_FAMILY_E_EXPLORATORY_SYNTHESIS_001.md`, `../../CRYPTO_RESEARCH_PROGRAMME_ROADMAP.md`.
