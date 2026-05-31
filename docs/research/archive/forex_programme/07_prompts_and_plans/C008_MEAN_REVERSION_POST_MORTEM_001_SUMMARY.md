# C008 Mean-Reversion Post-Mortem — Sprint 001 Summary

**Date:** 2026-05-26  
**Branch:** `research-c008-mean-reversion-post-mortem-001`  
**Base branch:** `infra-external-data-ingest-blocker-resolution-001`

> **No strategy approved.** C008/C009 remain **REJECT**. CAMPAIGN_018 not created. No retuning. No new trade performance claims.

---

## 1. Branch name

`research-c008-mean-reversion-post-mortem-001`

## 2. Commit hashes by phase

| phase | commit | message |
|---:|---|---|
| 0 | `d3d0658` | docs: phase 0 plan and truth audit |
| 1 | `9349b9d` | docs: phase 1 evidence reconstruction |
| 2–4 | `2fb5871` | infra: trade anatomy, cross-asset, confluence overlays |
| 5–6 | `2e684c7` | docs: human review post-mortem and future gate |
| 7 | `596cecb` | docs: archive/backlog updates |
| 8 | *(this commit)* | docs: final summary and validation close-out |

## 3. Files changed by phase

| phase | key paths |
|---:|---|
| 0 | `C008_MEAN_REVERSION_POST_MORTEM_001_PLAN.md` |
| 1 | `C008_C009_EVIDENCE_RECONSTRUCTION.md` |
| 2 | `c008_trade_anatomy.json`, `C008_TRADE_ANATOMY_DIAGNOSTICS.md` |
| 3 | `c008_cross_asset_regime_overlay.json`, `C008_CROSS_ASSET_REGIME_OVERLAY.md` |
| 4 | `c008_confluence_overlay.json`, `C008_CONFLUENCE_OVERLAY_DIAGNOSTIC.md` |
| 5 | `C008_HUMAN_REVIEW_POST_MORTEM.md` |
| 6 | `FUTURE_MEAN_REVERSION_RESEARCH_GATE.md` |
| 7 | `EVIDENCE_INDEX.md`, `FUTURE_RESEARCH_BACKLOG.md`, `EVIDENCE_MANIFEST.json` |
| 8 | this summary, `scripts/run_c008_post_mortem_diagnostics.py` |

## 4. C008 evidence reconstruction

`mean_reversion 0.1.0-c008`, H4, 6 pairs. Train: 216 trades, −0.017 R, PF 1.02. Validation: 138 trades, **+0.172 R**, PF 1.29, **6/6 pairs positive**. Full-window stress_2x +0.027 R. Test window **not opened**.

## 5. C009 evidence reconstruction

`mean_reversion 0.2.0-c009` — midline exit only change. Train: 252 trades, **−0.062 R**, PF 0.97. Validation: 151 trades, +0.170 R, PF 1.37, 4/6 pairs. Midline exit **worsened train** vs C008.

## 6. Exact C008 failed gate

**train expectancy ≥ 0** — observed **−0.017 R** → FAIL. All other screening gates passed.

## 7. Exact C009 failed gate

**train expectancy ≥ 0** — observed **−0.062 R** → FAIL.

## 8. Trade anatomy findings

- Validation edge is **100% time-stop driven** (44/44 winners exited via 40-bar time stop, +1.83 R exp on time exits).
- Train losers are **98% hard-stop** (153/156).
- USD_CAD train weak (−0.382 R); all validation pairs positive.
- London session validation strong (+0.612 R); spread/cost similar train vs validation winners.

## 9. Cross-asset regime overlay findings

354/354 trades joined to full-window FRED features. Descriptive macro shift: validation era predominantly risk-on + higher rates + inverted curve vs train's mixed risk/neutral. **No edge claim** — fixed buckets only.

## 10. Confluence overlay findings

Train: 44 C-grade (`risk_off_headwind`); validation: 0 C/REJECT. Grades describe context, not outcomes — even A-grade train trades lost when stopped out. `cross_asset_missing` absent.

## 11. Retuning performed?

**No.**

## 12. New trade performance claim?

**No** — descriptive diagnostics on existing REJECT campaigns only.

## 13. Strategy approved?

**No** — `approved: []`.

## 14. CAMPAIGN_018 created?

**No.**

## 15. Paper/demo/live blocked?

**Yes** — freeze passes.

## 16. Validation results

| command | result |
|---|---|
| `pytest tests/ -q` | PASS (1653) |
| `ruff check src tests scripts research` | PASS |
| `check_research_freeze.py` | PASS |
| `validate_research_archive.py` | PASS |
| `scan_artifacts_for_secrets.py` | PASS |

## 17. Remaining blockers

- C008/C009 evidence integrity LIKELY_CONTAMINATED — rerun before any promotion consideration.
- Test lockbox never opened for either campaign.
- Financing unmodeled in-engine.
- Exit structure (time vs stop) unexplained as tradable policy without new pre-registered campaign.
- Broad strategy search still paused.

## 18. Recommended next sprint

**`research-stop-and-exit-diagnostics-001`** — exit pathology (time-stop winners vs stop losers) is the dominant explanatory gap; C009 midline rescue falsified; cross-asset/confluence alone do not explain train gate failure.

## 19. Files to review first

1. `docs/research/C008_C009_EVIDENCE_RECONSTRUCTION.md`
2. `docs/research/C008_TRADE_ANATOMY_DIAGNOSTICS.md`
3. `docs/research/C008_HUMAN_REVIEW_POST_MORTEM.md`
4. `research/c008_post_mortem/c008_trade_anatomy.json`
5. `docs/research/FUTURE_MEAN_REVERSION_RESEARCH_GATE.md`
6. `backtests/CAMPAIGN_008_RANGE_MEAN_REVERSION_REPORT.md`

---

**Disclaimer:** Diagnostic post-mortem only. Not strategy evidence.
