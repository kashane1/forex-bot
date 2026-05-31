# Backtrader Exit Parity — Status and Next Step

**Branch:** `infra-backtrader-exit-parity-diagnostics-001`  
**Date:** 2026-05-27  
**Evidence class:** `parity_diagnostic_only` — `strategy_evidence: false`

---

## Backtrader status

| Item | Status |
|---|---|
| Backtrader installed | **Yes** — 1.9.78.123 via `backtrader-lane` extra |
| Deduped H4 feed | **Yes** — `data/campaign_002.sqlite3` via `load_deduped_h4_frame` |
| C008/C009/C018 replay | **Complete** |
| Fixture tests | **6/6 pass** (stop, time, target, protective, same-bar precedence, no ratchet) |

---

## Parity close enough?

| Dimension | Verdict |
|---|---|
| Exit-reason shares | **CLOSE_MATCH** — pathology direction preserved |
| Trade counts | **MATERIAL_DIVERGENCE** — ~20–25% fewer BT entries |
| Expectancy R by exit | Directionally consistent; BT rounds to −1R on stops |

**Conclusion:** Exit findings from the custom engine are **corroborated at the distribution level**. Trade-count gap requires **entry orchestration** follow-up before treating full-trade-list parity as proven.

---

## Custom engine bug suspected?

**No** for exit precedence / protective-stop / target behavior. **Possible** entry-bar indexing or RiskEngine equity-window coupling in the Backtrader orchestration layer — not proven in bespoke engine.

---

## Further exit research allowed?

**Yes, diagnostic only** — exit pathology (stop/time split, target capping, protective exits) is reproducible. Any new exit hypothesis still requires precommit + REJECT-by-default gates. No strategy approval.

---

## Financing blocked?

**Yes.** Manual overnight sample path **paused** by operator directive. Observed financing capture remains empty. MODELED financing overlay blocked for promotion. No practice trades placed in this sprint.

---

## Approval statement

**No strategy is approved.** `configs/approved_strategies.yaml` remains `approved: []`. Paper/demo/live remain blocked. Broad strategy search remains paused.

---

## Recommended next sprint

**`research-exit-hypothesis-precommit-002`**

**Why:** Exit-reason distributions corroborate bespoke findings (stop/time split, C009 target capping, C018 protective exits). Trade-count gap is entry-orchestration noise for exit pathology conclusions — not sufficient to open `infra-engine-exit-bug-investigation-001`. Financing remains blocked without manual sample; new strategy discovery deferred while broad search paused.

**Not selected:**
- `research-financing-manual-rate-source-expansion-001` — financing still blocked; manual sample paused
- `infra-engine-exit-bug-investigation-001` — exit shares match; no exit bug signal
- `research-new-candidate-strategy-discovery-with-confluence-001` — broad search still paused

---

## Artifacts

| File | Purpose |
|---|---|
| [`research/backtrader_exit_parity/c008_parity_summary.json`](../../research/backtrader_exit_parity/c008_parity_summary.json) | C008 BT aggregates |
| [`research/backtrader_exit_parity/c009_parity_summary.json`](../../research/backtrader_exit_parity/c009_parity_summary.json) | C009 BT aggregates |
| [`research/backtrader_exit_parity/c018_parity_summary.json`](../../research/backtrader_exit_parity/c018_parity_summary.json) | C018 BT aggregates |
| [`research/backtrader_exit_parity/exit_reason_comparison.csv`](../../research/backtrader_exit_parity/exit_reason_comparison.csv) | Side-by-side counts |
| [`docs/research/BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md`](BACKTRADER_EXIT_PARITY_DIVERGENCE_ANALYSIS.md) | Root-cause taxonomy |
