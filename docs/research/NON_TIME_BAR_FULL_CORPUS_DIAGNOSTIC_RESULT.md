# Non-Time Bar Full-Corpus Diagnostic Result

**Sprint:** `infra-range-and-volatility-bars-001` · Phase 6
**Date:** 2026-05-29
**Status:** infrastructure diagnostics. **No strategy evidence. No approval.**

Full local M1 corpus (7 majors, 2021-05-27 → 2026-05-26, ~1.79M–1.84M M1 rows
per pair) folded through the deterministic builders. **No broker/network
calls.** Only compact JSON summaries/manifests committed; full bars never
written.

## Commands run

```
python scripts/generate_non_time_bar_diagnostics.py --bar-type range \
    --thresholds 5 10 15 20 --run-label full_corpus
python scripts/generate_non_time_bar_diagnostics.py --bar-type volatility --method abs_close \
    --thresholds 10 20 --run-label full_corpus
python scripts/generate_non_time_bar_diagnostics.py --bar-type volatility --method true_range \
    --thresholds 10 20 --run-label full_corpus_tr
```

Artifacts: `research/non_time_bars/full_corpus/` and `.../full_corpus_tr/`
(`<pair>_<type>_summary.json` + `<type>_diagnostics_manifest.json`).

---

## 1. Range bars — pair-level bar counts & compression vs M1

`bar_count` · `×compression vs M1` · `median source M1 rows/bar`:

| pair | 5 pip | 10 pip | 15 pip | 20 pip |
|------|------:|------:|------:|------:|
| EUR_USD | 113,803 ×16 (m7) | 31,664 ×58 (m23) | 14,535 ×127 (m51) | 8,346 ×221 (m92) |
| GBP_USD | 174,718 ×11 (m5) | 50,283 ×37 (m15) | 23,140 ×79 (m33) | 13,334 ×138 (m58) |
| USD_JPY | 237,197 ×8 (m4) | 72,940 ×25 (m11) | 34,841 ×53 (m21) | 20,547 ×90 (m36) |
| AUD_USD | 87,012 ×21 (m10) | 23,505 ×78 (m37) | 10,802 ×169 (m85) | 6,103 ×299 (m163) |
| USD_CAD | 124,076 ×15 (m7) | 34,170 ×54 (m22) | 15,495 ×118 (m49) | 8,749 ×210 (m91) |
| USD_CHF | 89,224 ×20 (m9) | 24,290 ×74 (m31) | 10,963 ×163 (m69) | 6,212 ×288 (m130) |
| NZD_USD | 75,085 ×24 (m12) | 20,199 ×90 (m46) | 9,176 ×199 (m107) | 5,188 ×352 (m202) |

Compression-vs-M15 (approx) = compression-vs-M1 ÷ 15. E.g. EUR_USD 10-pip
×58 vs M1 ≈ **×3.9 vs M15** (a 10-pip EUR_USD range bar is ~4× coarser than M15).

## 2. Volatility bars — bar counts & compression vs M1

`abs_close` (cumulative |Δclose|):

| pair | 10 pip | 20 pip |
|------|------:|------:|
| EUR_USD | 149,414 ×12 | 78,172 ×24 |
| GBP_USD | 187,566 ×10 | 99,268 ×19 |
| USD_JPY | 218,411 ×8 | 116,965 ×16 |
| AUD_USD | 135,713 ×13 | 70,485 ×26 |
| USD_CAD | 158,222 ×12 | 82,894 ×22 |
| USD_CHF | 132,515 ×13 | 69,042 ×26 |
| NZD_USD | 125,709 ×15 | 65,082 ×28 |

`true_range` (cumulative TR) — TR ≥ |Δclose| per row, so for the same pip
threshold a TR bar completes after fewer rows ⇒ **more, finer bars**:

| pair | 10 pip | 20 pip |
|------|------:|------:|
| EUR_USD | 261,010 ×7 | 138,139 ×13 |
| GBP_USD | 326,774 ×6 | 175,446 ×10 |
| USD_JPY | 381,199 ×5 | 207,622 ×9 |
| AUD_USD | 228,641 ×8 | 119,987 ×15 |
| USD_CAD | 269,496 ×7 | 142,843 ×13 |
| USD_CHF | 221,462 ×8 | 116,598 ×15 |
| NZD_USD | 213,894 ×9 | 111,856 ×16 |

`true_range` produces ~1.7–1.8× as many bars as `abs_close` at the same pip
threshold — they are **not** interchangeable, exactly as the spec warns.

## 3. Session & weekday distribution (representative)

USD_JPY range 10-pip (UTC-hour buckets): london_ny_overlap 21,363 · tokyo 21,001
· london 15,862 · new_york 9,937 · rollover_late 4,777. Bars concentrate in the
Tokyo and London/NY-overlap sessions — the expected USD_JPY activity profile.

Weekday (USD_JPY 10-pip): Mon–Fri 12.6k–15.3k each; **Sunday only 1,441** (the
partial Sunday-evening FX open) — sane.

## 4. Elapsed-time distribution (event-driven cadence)

Median wall-clock minutes per range bar, range across the 7 pairs:

| threshold | median dwell (min) | median source M1 rows | multi-threshold bars |
|-----------|-------------------:|----------------------:|---------------------:|
| 5 pip  | 3–12  | 4–12  | 2.7–9.0% |
| 10 pip | 10–46 | 11–46 | 1.5–4.3% |
| 15 pip | 20–108| 21–107| 1.2–3.4% |
| 20 pip | 35–205| 36–202| 0.9–2.8% |

`incomplete_final_bars = 0` for every pair/threshold (emit-incomplete off by
default — confirms the trailing partial bar is correctly dropped).

## 5. Comparison to M15 / M5 row counts

Per pair there are ~1.8M M1 rows ≈ 122k M15 rows ≈ 367k M5 rows over the window.
So:
- **5-pip range** (75k–237k bars) ≈ M5–M15 cadence — i.e. as frequent as a fast
  time bar.
- **10-pip range** (20k–73k bars) ≈ ~0.2–0.6× M15 count — between M15 and H1.
- **15/20-pip range** (5k–35k bars) ≈ H1–H4 cadence.
- **abs_close 20-pip / true_range 20-pip** sit in the 10-pip-range neighbourhood.

## 6. Thresholds that are too noisy

**5-pip range** is the noisy end: median dwell of only 3–12 minutes and the
highest multi-threshold-crossing rate (up to **9%** on GBP_USD/USD_JPY, where a
single volatile M1 minute routinely jumps several 5-pip thresholds). At 5 pips
the bar is barely coarser than M5 and increasingly reflects M1 microstructure /
spread noise rather than structure. **`true_range 10-pip`** is similarly fine
(×5–9 vs M1). Not recommended as a primary research timeframe without a strong
reason.

## 7. Thresholds that are too sparse

**20-pip range on the low-pip-range pairs** (AUD_USD 6,103; NZD_USD 5,188;
USD_CHF 6,212 bars over ~5 years) is the sparse end — median dwell 130–205 min
and only ~5–6k bars total, which is thin for train/validation splitting. 15-pip
is already borderline-sparse for AUD/NZD.

## 8. Recommended default thresholds for future research

- **Primary range threshold: 10 pip.** Best balance across all 7 pairs:
  20k–73k bars, ~M15–H1 cadence, multi-threshold crossings ≤4.3%, comfortably
  splittable for train/validation.
- **Secondary range threshold: 15 pip** for a coarser H1-ish view (drop to
  10-pip-only for AUD_USD/NZD_USD where 15-pip thins out).
- **Volatility: `true_range 20-pip` (primary)** — comparable cadence to 10-pip
  range with a path-length rather than displacement trigger; **`abs_close 20-pip`**
  as the simpler companion. Avoid the 10-pip volatility variants as primary
  (too fine).
- **Important caveat — a single pip threshold is NOT cadence-uniform across
  pairs.** USD_JPY yields ~3× the bars of NZD_USD at the same pip threshold
  (pip-volatility differs). A future campaign comparing pairs should either use
  **per-pair thresholds** or the **`atr_scaled` volatility mode** (already
  implemented, prior-window-only) to equalise cadence. This is a design input
  for the next sprint, not a defect.

## 9. Known limitations

- M1 OHLC is not tick data: intrabar path is unknown, so within-candle overshoot
  is attributed to one bar (recorded via `thresholds_crossed` / `overshoot_pips`),
  and `true_range`/`abs_close` undercount true realized volatility (lower bounds).
- Pip thresholds are **price-space, not cost-space** — none of these bars are
  net-of-spread tradable moves. Cost feasibility is a strategy-time concern.
- Weekend/holiday gaps mean some bars straddle a multi-day gap (249–294 such bars
  per USD_JPY series); `source_start_time`/`source_end_time` make them auditable.

## 10. Is the infrastructure ready for strategy scaffolding?

**Yes — the infrastructure is ready.** It is deterministic (Decimal-exact
completion, causal-prefix tested), lookahead-free, fully provenance-tagged, and
produces structurally sane, internally consistent diagnostics across all 7
pairs and the full threshold grid. A future sprint can scaffold a non-time-bar
campaign on top of it. **This sprint did not search for or find an edge, and
approves nothing.** `configs/approved_strategies.yaml` remains `approved: []`;
paper/demo/live remain blocked.
