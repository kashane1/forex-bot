# CAMPAIGN_020 — Test Lockbox Not Opened

**Date:** 2026-05-27  
**Reason:** Train gate failed and screening did not pass.

## Blockers

1. **train_expectancy_gte_zero** failed (−0.035 R under `next_bar_open`).
2. **backtrader_parity_pass** not satisfied (no C020 parity run).
3. Gate discipline: validation uplift does **not** authorize test when train fails.

Test window 2025-01-01 → 2026-05-20 was **not** executed.
