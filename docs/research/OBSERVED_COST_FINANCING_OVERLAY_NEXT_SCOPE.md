# Observed Cost / Financing Overlay — Next Sprint Scope

**Recommended sprint:** `infra-observed-cost-financing-overlay-local-first-001`

## Current financing coverage

| Mode | Status |
|------|--------|
| Modeled / estimated | Many campaigns (`financing_treatment: estimated`) |
| Observed manual CSV | Loader exists; not universal |
| Triple rollover | Partial / documented gaps |
| Practice overnight capture | Read-only pilot documented; sample plan blocked on human sample |

## Unmodeled / partial gaps

- Multi-day holds without financing overlay understate carry cost
- Weekly rebalance strategies (C016/C017 family)
- Overnight mean-reversion holds (C008/C019)

## Campaign types most affected

1. Weekly rebalance (C016, C017)
2. Holds > 5 days
3. Carry-sensitive pairs (USD/JPY, high-yield crosses)

## Data inputs needed

| Input | Source | OANDA orders? |
|-------|--------|---------------|
| Financing transactions | Read-only transaction history API | **No** mutation |
| Manual rate CSV | Committed fixtures | No |
| Hold calendar | Derived from trade CSVs | No |

## Sprint options

### A — Local-first (preferred)

- Use committed financing fixtures + `financing.py` overlay on existing trade CSVs
- Produce `financing_adjusted_expectancy_r` diagnostic columns
- No live credentials required if fixtures suffice

### B — Read-only observed capture

- `scripts/` pilot pattern from `OBSERVED_FINANCING_CAPTURE_READONLY_001`
- Practice account read-only; **no order/trade/position mutation**

## This sprint

**Docs only** — no full overlay implementation (not trivial with safe local fixtures alone).

## Blocker statement

Financing remains a **blocker for approving multi-day/weekly strategies**, not for intraday H4 campaigns with short holds.
