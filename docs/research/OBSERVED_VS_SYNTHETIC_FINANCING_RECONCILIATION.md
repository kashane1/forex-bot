# Observed vs Synthetic Financing Reconciliation

**Sprint:** `infra-observed-financing-capture-readonly-002`  
**Module:** `src/forex_bot/research/financing_reconciliation.py`

## Observed sample size

**0 financing entries** in committed observed fixture (capture blocked / practice account empty in prior sprint).

## Inference limitations

- Cannot infer per-instrument financing rates from observed data
- Cannot validate triple-rollover magnitude vs synthetic stress
- `FinancingOverlayMode.OBSERVED_PRACTICE_FIXTURE` correctly returns unavailable when entries empty

## Synthetic reference (local-first sprint)

| Ledger | Synthetic drag (ΔR) |
|--------|---------------------|
| C019 train+validation | -0.082 |
| C016 weekly | -0.052 |
| C017 weekly | -0.044 |
| C008 forensic train | -0.080 |

## Synthetic vs observed directional comparison

**Inconclusive** — no observed entries. Synthetic stress should be treated as a **conservative directional bound** (typically reduces net R) until practice capture yields `DAILY_FINANCING` rows.

## Overlay assumptions

No adjustment recommended from empty observed sample. When capture succeeds, reconcile:

- per-instrument financing totals vs stress-implied drag
- long vs short splits where `openTradeFinancings` present

## No-approval statement

Reconciliation is diagnostic infrastructure only.
