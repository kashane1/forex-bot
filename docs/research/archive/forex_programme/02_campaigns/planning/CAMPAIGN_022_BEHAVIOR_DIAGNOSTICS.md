# CAMPAIGN_022 — Behavior Diagnostics

**Date:** 2026-05-28 · **Strategy:** `h4_h1_pullback_resolution_entry 0.1.0-c022`
**Diagnostic only — no retuning, no threshold changes.** Verdict remains REJECT.

Question this phase answers: did the pullback-resolution structure *materially change trade
behavior* versus prior all-green alignment systems, and why does it lose?

Source: per-trade records under `backtests/CAMPAIGN_022_h4_h1_pullback_resolution/` (base cost),
aggregated in `research/campaign_022/behavior_diagnostics.json` + `hold_diagnostics.json`.

## Headline behavior (base cost)

| metric | overall | train | validation |
|---|---|---|---|
| trades | 2396 | 1369 | 1027 |
| win rate | 32.6% | 33.6% | 31.3% |
| mean R | −0.131 | −0.104 | −0.166 |
| median R | −0.734 | −0.744 | −0.722 |
| avg win R | +1.24 | +1.29 | +1.17 |
| avg loss R | −0.79 | −0.81 | −0.77 |
| % trades losing ≥0.9R | 42.3% | 41.6% | 43.2% |
| % trades ≥ +1.0R | 14.9% | 16.4% | 13.0% |

## Exit behavior

| exit reason | share | mean R |
|---|---|---|
| hard stop (−2×ATR) | 60.1% | −0.86 |
| time stop (32 bars) | 39.9% | +0.96 |

- avg hold ≈ 0.31 calendar days (~19 of 32 M15 bars); median 0.22 days.
- only 5.2% of trades hold > 1 day → financing overlay immaterial.

## Interpretation of the analyses requested

- **Trade frequency:** ~2396 base trades over train+val (7 majors, ~4 yr). Frequent intraday
  participation, as designed for an M15 trigger.
- **Hard-stop vs time-stop rate:** 60% stop / 40% time. The majority of entries are stopped at
  −2×ATR before the 32-bar clock; the strategy bleeds on stops faster than time-exits recover.
- **Continuation quality / directional efficiency:** time-exits average **+0.96R** — i.e. when a
  trade survives the early window the H4-direction continuation *does* pay. But only 40% survive;
  60% are whipsawed out first. Win rate 32.6% with a +1.24 / −0.79 payoff needs ≈39% wins to break
  even — the entry timing falls ~6 points short.
- **Time-to-profit:** winners need most of the 32-bar window (avg 19 bars held overall, and winners
  are concentrated in the time-exit bucket), indicating the edge, where present, is slow relative to
  the −2×ATR stop distance.
- **Chop participation / late-trend chasing:** the M15 EMA20 reclaim after an H1 holding-pullback
  fires into too many failed resolutions — the pullback "resolves" on the trigger bar but price
  reverses through the stop. The hypothesis that resolving-pullback entries avoid chop is **not**
  supported; if anything the reclaim trigger buys local noise.

## Requested analyses NOT derivable from current artifacts (honest gap)

H4 ADX distribution, H1 pullback-depth distribution, per-session and per-volatility-regime splits,
and MFE/MAE are **not recorded** in the trade exporter for C022 (only entry/exit/R/bars/exit_reason/
spread). Producing them would require instrumenting the frozen strategy to emit signal features —
out of scope for a diagnostic phase under the no-modification rule. They are not needed to reach the
verdict (train gate already fails decisively) and are flagged here rather than fabricated.

## Behavioral verdict

C022 did change behavior versus all-green alignment — it trades more and enters earlier on the
reclaim — but the change is **net negative**: earlier entries are whipsawed, stop rate dominates,
and aggregate expectancy is worse than C020. Pullback-resolution, as frozen, does not improve
trend-continuation capture.
