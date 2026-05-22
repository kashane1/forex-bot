# CAMPAIGN_003 Post-Mortem

Status: **CAMPAIGN_003 is accepted as a valid negative result.** This
document is the immutable summary. It does not revise, rescue, or
re-tune `trend_following 0.2.0-c003`.

## One-paragraph summary

CAMPAIGN_003 tested one controlled hypothesis: the frozen Donchian
breakout, restricted to favourable conditions (H4 only, 6-pair universe
excluding NZD_USD, and an ADX-14 > 25 trend-strength gate), would lift
trend-following expectancy across break-even. It did not. The ADX
filter cut trade count roughly in half and improved expectancy
modestly, but the untouched-test result stayed negative. The verdict
is **REJECT**.

## What CAMPAIGN_003 established

| Fact | Evidence |
|---|---|
| Real OANDA data was reused | H4 candles from `data/campaign_002.sqlite3`; provenance raw/normalized SHA256 verified to match the CAMPAIGN_002 report. No re-fetch, no synthetic data. |
| Per-signal rejection export is now permanent | `write_all` always emits `*_risk_rejections.csv`; covered by `tests/unit/test_rejection_export.py`. |
| RiskEngine wired in | All 42 runs invoked `RiskEngine.evaluate()` (`mode="backtest"`). |
| The ADX-filtered strategy was rejected | See untouched-test metrics below. |

### Untouched-test metrics (2025-01-01 → 2026-05-20)

| metric | value |
|---|---|
| return | **−0.63%** |
| profit factor | **0.77** |
| expectancy | **−0.071 R** |
| win rate | 35.2% |
| pairs positive | **1 of 6** (only EUR_USD) |
| financing-stressed expectancy | −0.099 R |

stress_2x expectancy was −0.150 R. Every pre-committed Task-5 gate that
could fail, failed.

### Comparison vs CAMPAIGN_002 H4 (same 6 pairs)

| split | CAMPAIGN_002 H4 | CAMPAIGN_003 +ADX |
|---|---|---|
| untouched test | −1.02%, PF 0.75, exp −0.085 R, 204 trades | −0.63%, PF 0.77, exp −0.071 R, 101 trades |
| full | −5.62%, PF 0.67, exp −0.147 R | −3.42%, PF 0.71, exp −0.121 R |

The ADX filter is a *real* but *insufficient* improvement: it removes
breakouts taken in chop (≈50% fewer trades) and nudges every metric in
the right direction, but does not produce a positive edge.

## Conclusion: stop iterating the Donchian breakout entry

CAMPAIGN_002 showed the Donchian-20 breakout entry loses on the real
2020-2026 majors. CAMPAIGN_003 showed that *conditioning when* that
entry fires — the most disciplined possible salvage — is not enough.
Two controlled campaigns now agree: the breakout-on-close entry has no
positive edge on this universe, and further filtering of it is not a
productive use of research effort.

**Decision:** stop iterating the Donchian breakout entry family for
now. The next campaign (CAMPAIGN_004) tests a genuinely different entry
family — volatility-compression breakout — per hypothesis H-11 in the
[hypothesis backlog](HYPOTHESIS_BACKLOG.md). `trend_following
0.2.0-c003` is not paper-traded, not demo-traded, not promoted.
