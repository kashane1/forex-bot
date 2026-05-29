# CAMPAIGN_025 — selected-champion validation result

**Validation was NOT run.** The train matrix produced
`REJECT_MATRIX_NO_TRAIN_CANDIDATE` (0/16 candidates eligible), so there is **no
train-selected champion** to validate. Per the frozen protocol, validation is only
permitted on a single train-selected champion; with no champion, no promotion-style
validation runs.

---

## Why no validation

- Train selection (`research/campaign_025/train_matrix/train_matrix_candidate_selection.json`)
  → `champion_candidate_id: null`, `classification: REJECT_MATRIX_NO_TRAIN_CANDIDATE`.
- The runner's `--validate-champion` mode reads that selection and returns
  `validation_run: false` when no champion exists. It was not forced.
- This honors the rules: **no validation-based selection, no rescue logic, no
  tuning after train results, no inventing a champion.**

## Confirmation of invariants

- Validation did **not** select or modify any parameter (it did not run).
- The test lockbox remains **closed** (test window 2025-01-01 → 2026-05-20 untouched).
- No `SINGLE_PAIR_REVIEW_ONLY_CANDIDATE`: USD_JPY is the only weakly-positive pair
  on a few candidates, but its edge is small and does **not** survive 2× cost
  stress, so it is not "materially strong"; aggregate evidence is negative.
- **No approval. Paper/demo/live blocked. `approved_strategies.yaml` = `approved: []`.**

## Final classification (this sprint)

`REJECT_MATRIX_NO_TRAIN_CANDIDATE / TEST_LOCKBOX_CLOSED / NOT_APPROVED`.

Backtrader parity is **not** required (there is nothing that passed train to
promote); see `CAMPAIGN_025_BACKTRADER_PARITY_READINESS.md`.
