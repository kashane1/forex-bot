# Backtrader CAMPAIGN_015 — Provenance-Repair Result + Next-Step Decision (Phase 5)

**Sprint:** [BT C015 Provenance Repair 001](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_001_PLAN.md)
**Branch:** `infra-backtrader-campaign-015-provenance-repair-001`
**Date:** 2026-05-26
**Final sprint label:** **`BT_DIVERGENCE_NEEDS_DEBUG`**
**Recommended next step:** infra sprint that **aligns the BT and bespoke
time windows** (BT runs only on the 8 bespoke test windows, or bespoke
runs full-window without walk-forward), so any residual signal-rule
divergence can be isolated from the window-coverage gap. No
CAMPAIGN_015 work should derive a new candidate from this evidence
until that alignment is done.

> Decision document only. Does NOT approve any strategy.
> `configs/approved_strategies.yaml` remains `approved: []`.

---

## 1 · Was the provenance mismatch repaired?

**Yes.** Phase 1 documented the mismatch in full (all 7 instruments
sha-drifted vs the committed `*.provenance.json` sidecars). Phase 2
patched the root cause (`scripts/export_lean_parity_data.py` now
normalises `Candle.time` to UTC before serialisation, and dedupes
the duplicate H4 rows that the canonical DB carries), re-exported
all 7 instruments against `data/campaign_002.sqlite3`, and rebuilt
the matching sidecars + `EXPORT_MANIFEST.json`. The Phase 1 diagnostic
re-run confirms:

```
status: ALL BT-STRICT PREFLIGHT PASS
```

See: [BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RE_EXPORT.md](BACKTRADER_CAMPAIGN_015_PROVENANCE_REPAIR_RE_EXPORT.md).

---

## 2 · Did Backtrader run?

**Yes.** Phase 3 dry-run preflight: 7 instruments runnable, 0 blocked.
Phase 4 full run: 575 total trades across 7 instruments, 9,933–9,937
candles per pair, -51.43 account-currency total PnL.
See: [BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md](BACKTRADER_CAMPAIGN_015_PREFLIGHT_AFTER_PROVENANCE_REPAIR.md)
and
[BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md](BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md).

---

## 3 · Did Backtrader broadly reproduce CAMPAIGN_015?

**No** — not in the form we can currently compare. The compare-harness
reports a 3.5× trade-count gap on every pair, ranging from +137%
(GBP_USD) to +1,280% (NZD_USD). The harness's auto-label is
`SIGNAL_RULE_MISMATCH`.

But the underlying reason is not (or not only) a signal-rule problem.
The two engines are running on *fundamentally different time windows*:

- **BT** iterates the full ~6.4-year CSV (~9,933 H4 bars per pair).
- **Bespoke** walks-forward through 8 × 180-day rolling test windows
  (≈ 3.95 years of *test* coverage); each fold re-warms for 540 days
  during which no trade is counted.

A pure window-coverage adjustment (1.6×) accounts for a sizeable
fraction of the 3.5× gap; the remaining ~2.2× could be (a) additional
firing during what would have been bespoke's per-fold re-warmup
periods, (b) a real off-by-one or risk-engine difference in the BT
adapter, or (c) both. The current evidence cannot tell.

Win rates on most pairs (BT vs bespoke) sit in the same 0.25–0.5
band (EUR_USD 0.317 vs 0.333; GBP_USD 0.340 vs 0.415; USD_JPY
0.375 vs 0.529; AUD_USD 0.303 vs 0.375; USD_CAD 0.259 vs 0.348). The
strategy *family* is recognisably the same; the trade-firing rate
is what diverges.

---

## 4 · Divergence class (binding label)

**`TIMESTAMP_MISMATCH`** (primary, this sprint).
The compare-harness's auto-label `SIGNAL_RULE_MISMATCH` is faithful
to the inputs it sees but is **superseded** by the time-window
analysis above. A future window-aligned re-run is required before
any further classification.

---

## 5 · Does this alter CAMPAIGN_015's approval status?

**No.** CAMPAIGN_015 is still REJECT on the bespoke gates
(`fold_pass_rate_ge_5_of_8` 0/8; `trade_count_min_200` 164 < 200).
`configs/approved_strategies.yaml` remains `approved: []`. Paper /
demo / live remain blocked. No diagnostic in this infra sprint can
move any of those.

---

## 6 · Does this unblock the next research step?

**Partially.**

- ✅ The CSV/provenance lock-step is restored, so any future sprint
  that wants to run the BT lane gets a clean preflight.
- ✅ The `scripts/export_lean_parity_data.py` tz-determinism bug is
  fixed at the root — future exports across machines / timezones will
  produce identical CSVs and provenance.
- ✅ The new `scripts/diagnose_backtrader_csv_provenance.py` lets any
  future sprint confirm the bundle is BT-strict-pass in one command.
- ✅ The new `scripts/build_lean_parity_export_manifest.py` consolidates
  the 7 sidecars into one manifest for downstream verification.
- ❌ The BT-vs-bespoke comparison itself is **not** PASS or TOLERABLE_DRIFT.
  It is `TIMESTAMP_MISMATCH`, and a windowed re-run is the necessary
  next step.

---

## 7 · Should we now collect more H4 data and rerun frozen CAMPAIGN_015?

**Not yet.** The Phase 5 of the prior post-run-diagnostics sprint
recommended `COLLECT_MORE_DATA_FIRST` with `RUN_BACKTRADER_OR_NULL_FIRST`
as a hard precondition. This sprint has *partially* satisfied the
BT precondition — the lane runs — but the comparison itself is not
yet a clean cross-engine corroboration. **Extending the data universe
*now* would be premature.** The correct sequencing is:

1. **Window-align the BT vs bespoke comparison** (this is the missing
   piece). Either:
   - run BT only on the 8 bespoke test windows (modify BT adapter to
     accept a window list, OR run BT 8 times with date filters and
     aggregate), OR
   - run bespoke full-window without walk-forward (a new mode in
     `scripts/run_campaign_015.py`).
   Both are infra work; both produce a clean apples-to-apples comparison.
2. **Re-classify divergence** with the aligned numbers. If
   `PASS` or `TOLERABLE_DRIFT`, the BT precondition is fully satisfied.
3. **Only then**, consider an infra sprint to extend the H4 universe
   and re-run the frozen CAMPAIGN_015 config on more years.

---

## 8 · Remaining infra blockers (post this sprint)

- **Window alignment** for BT vs bespoke comparison (see §7).
- **DB-level duplicate H4 rows** in `data/campaign_002.sqlite3` — this
  sprint deduped at the *export* layer (one canonical bar per UTC
  timestamp), which is sufficient for the BT lane. The bespoke still
  consumes the raw duplicate rows directly via `CandleRepo.list()`;
  this didn't *appear* to affect the rehydrate trade list (164 trades
  reproduced exactly), but is worth scrubbing in a follow-up data
  hygiene sprint.
- **Per-fold BT mode** does not exist yet; only the whole-window
  `scripts/run_backtrader_parity.py --campaign CAMPAIGN_015` path is
  wired up.

None of these blockers affects the CAMPAIGN_015 strategy itself or
its REJECT verdict.

---

## 9 · Final sprint label

**`BT_DIVERGENCE_NEEDS_DEBUG`**.

- Not `BT_VERIFICATION_PASS`: trade counts differ by 3.5×.
- Not `BT_TOLERABLE_DRIFT`: the drift is too large to attribute solely
  to known approximations.
- Not `BT_STILL_BLOCKED`: the lane runs, and the provenance repair
  is fully effective; the BLOCKED state of the prior sprint is gone.
- `BT_DIVERGENCE_NEEDS_DEBUG` matches the evidence: the lane works,
  the divergence is real, the root cause cannot be isolated without
  a windowed re-run.

---

## 10 · Safety invariants

- `configs/approved_strategies.yaml` is `approved: []`. ✓
- Paper / demo / live loops refuse to start. ✓
- CAMPAIGN_015 strategy parameters / frozen config / gates / runner /
  anti-overfit classifier — all untouched. ✓
- Bespoke engine — untouched. ✓
- BT adapter strategy — untouched. ✓
- The `config_hash` for the rehydrate
  (`17ddfd7eb87d93c502f148642c8ee883c66cb72bfa8ca72f981624a0dcfdd93c`)
  is unchanged. ✓
- No broker call, no `.env`, no live OANDA, no Lean / QuantConnect. ✓
- No prior campaign evidence was modified
  (the prior `BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON.md` is a
  read-only historical record; the new
  `BACKTRADER_CAMPAIGN_015_POST_RUN_COMPARISON_AFTER_PROVENANCE_REPAIR.md`
  is an addition, not a replacement). ✓
