# EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_SUMMARY

**Status:** sprint summary (Phase 10). Infrastructure / diagnostic / idea-selection
evidence only. Approves nothing; creates no campaign (no CAMPAIGN_027); opens no
test lockbox; `configs/approved_strategies.yaml` stays `approved: []`; paper /
demo / live stay blocked.

---

**1. Branch.** `research-edge-discovery-front-gate-idea-selection-001`
(off `origin/main` @ `5063011`, the merged null-benchmark lab).

**2. Commit hashes by phase.**
- P0 truth audit + plan — `0ab6271`
- P1 idea inventory — `4e7f524`
- P2 opportunity map — `1296b45`
- P3 signal probes — `4996c0e`
- P4 matched-null + matrix sanity — `1fd01c3`
- P5 filter ablation — `f07dd75`
- P6 idea ranking + decision — `5afdb83`
- P7 next-campaign precommit prompt — `e1abbbc`
- P8 artifact contract + compatibility checklist — `41f2fef`
- P9 status/index/manifest/backlog + data correction — `694b0f9`
- P10 validation + this summary — (this commit)

**3. Files changed by phase.**
- P0: `EDGE_DISCOVERY_FRONT_GATE_IDEA_SELECTION_001_PLAN.md`.
- P1: `EDGE_DISCOVERY_IDEA_INVENTORY.md`.
- P2: `build_opportunity_map.py` + `opportunity_map_*.{csv,json}`,
  `cost_feasibility_flags.json`, `EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md`.
- P3: `run_signal_probes.py` + `signal_probe_*.{csv,json}`,
  `skipped_signal_probes.json`, `.gitignore`, `EDGE_DISCOVERY_SIGNAL_PROBE_RESULTS.md`.
- P4: `run_matched_null_screening.py` + `matched_null_probe_*`,
  `matrix_sanity_probe_results.json`, `probe_compatibility_gaps.json`,
  `EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md`.
- P5: `run_filter_ablation.py` + `filter_ablation_probe_summary.csv`,
  `filter_contribution_scores.csv`, `filter_failure_reasons.json`,
  `EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md`.
- P6: `EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md`.
- P7: `NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md`.
- P8: `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md` (addendum),
  `EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md`.
- P9: `STRATEGY_STATUS.md`, `EVIDENCE_INDEX.md`, `EVIDENCE_MANIFEST.json`,
  `FUTURE_RESEARCH_BACKLOG.md`, + plan/opportunity-map data corrections.
- P10: this summary.
- (Reproducible local artifacts `ledgers/` and `frames/` are **gitignored** — no
  bulky/raw-candle data committed.)

**4. Candidate idea families considered (12).** Asia range breakout; Asia range
fade; London open expansion; NY open continuation/reversal; USD_JPY single-pair
probe; z-score mean reversion + regime filters; failed-breakout fade; volatility
compression→expansion; high-volatility exhaustion→reversal; event-window anomaly;
carry/financing swing; pair/timeframe/session opportunity mining.

**5. Data availability.** Local SQLite store `data/campaign_002.sqlite3` (the
lab's worktree-resolvable path): **H4, H1, D** on the 7 majors, 2020-01→2026-05.
Event fixture `campaign_014_events.json`; slow-macro FRED caches; financing proxy
`forex_bot.financing`; C011 null baseline JSON. **Sub-H4 (M1/M5/M15) is
out-of-scope for the lab, not nonexistent:** M1-materialized M5/M15/H1/H4M1 exist
in the local research **Postgres** store, but the import-isolated lab reads SQLite
+ committed files only.

**6. Opportunity-map findings.** **All 14 pair×TF and 56 pair×TF×session cells are
`COST_FEASIBLE`** (H4 spread/ATR 0.043–0.105; H1 0.091–0.221) — 3–10× cheaper than
the rejected M5 (~0.45), so any null result here is a true no-edge result, not a
cost mirage. **USD_JPY is cheapest and most volatile** (cost-advantaged venue).
Session vol gradient is weak (H1 London ATR ≈ Asian), demoting "London open
expansion." H4 is the cleaner screening target; H1 adds session resolution.

**7. Signal probes run (6).** z-score reversion (H4), failed-breakout fade (H4),
Asia-range breakout (H1), NY-open continuation (H1), vol compression→expansion
(H4), USD_JPY z-score overlay (H4). All non-sparse (3.2k–11.9k signals).

**8. Signal probes skipped/blocked (2).** Carry/financing swing
(`COMPATIBILITY_BLOCKED` — no local carry/swap-rate table); sub-hour
open-expansion (out-of-scope — lab has no sub-H4 data path).

**9. Matched-null screening results.** The two Phase-3 survivors (z-score
reversion, failed-breakout fade) **`BEATS_MATCHED_NULL` on all six modes**
(timestamp-random, side-shuffled, pair-matched, session-matched,
holding-period-matched, full) at percentile 100, effect 3.6–6.0 — real reversion
*information*. **But strategy post-cost expectancy is negative** under the
conservative financing-inclusive overlay (z-score −0.000033, failed-breakout
−0.000010): the information is not, by itself, a tradable edge.

**10. Filter-ablation results.** On z-score reversion: **3/5 filters add edge**
(`low_vol`, `strong_extension` |z|≥2.5, `quiet_session` all `FILTER_ADDS_EDGE`);
`long_side` `FILTER_HURTS_EDGE` (the edge is short-side); `cost_adv_pair`
`FILTER_ONLY_REDUCES_SAMPLE`. The edge-adding subset (n=1,065, short-biased) is
**post-cost positive under both optimistic (+0.000754) and conservative
financing-inclusive (+0.000626) cost**, hit 0.55, **pair-robust 6/7**, **positive
4/7 years** (cured the Phase-4 single-year 2023 dominance; 2024 & 2026-partial
still negative — a recency risk).

**11. Multiple-comparison sanity.** `matrix_sanity` over the screened variants:
**`LIKELY_SELECTION_NOISE`**; the apparent "best" (USD_JPY single-pair) has
`prob_best_le_null_max = 0.94` — i.e. it is best-of-N noise. Confirms **USD_JPY's
value is cost, not signal.** A standing caution; the chosen all-pair filtered
subset is a distinct, more robust object (pair-robust both at the trigger level,
5/7, and in the filtered subset, 6/7).

**12. Idea ranking.** 1) z-score reversion (low-vol/quiet-session/strong-
extension, short) — **CAMPAIGN_ELIGIBLE (borderline)**. 2) failed-breakout fade —
REJECT_CHEAPLY. 3) USD_JPY standalone — REJECT_CHEAPLY. 4) Asia-range breakout —
REJECT_CHEAPLY. 5) NY-open continuation — REJECT_CHEAPLY. 6) vol
compression→expansion — REJECT_CHEAPLY. 7) London open expansion —
REJECT_CHEAPLY. 8) high-vol exhaustion — INCONCLUSIVE. 9) Asia range fade —
INCONCLUSIVE. 10) event-window — COMPATIBILITY_BLOCKED/sparse. 11)
carry/financing — COMPATIBILITY_BLOCKED. 12) opportunity mining — done (Phase 2).

**13. Campaign-eligibility decision.** Exactly **one** idea is CAMPAIGN_ELIGIBLE
(borderline/conditional): the H4 low-vol quiet-session strong-extension
short-biased z-score mean reversion. It is the first idea in the program to clear
the full edge-discovery battery. No other idea is eligible. **No CAMPAIGN_027
should be created** absent an explicit human instruction.

**14. Was a next-campaign prompt drafted?** **Yes** —
`NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md` (a *draft*, NOT executed).

**15. If drafted, which idea and why.** The eligible z-score reversion idea —
because it uniquely passed cost feasibility, forward-return information, all six
matched nulls, filter-adds-edge ablation, conservative financing cost,
pair-robustness (6/7), and multi-year positivity (4/7), with four explicit
pre-registered campaign kill-conditions (recency, filter forking-path,
conditioning narrowness, selection-noise).

**16. If no prompt — n/a** (a prompt was drafted).

**17. Future artifact-contract updates.** `FUTURE_CAMPAIGN_ARTIFACT_REQUIREMENTS.md`
extended: confirmed emission items 1–8 and promoted 4 implicit fields to explicit
(timeframe, null-benchmark-compat fields + C011 ref, reproducibility manifest,
random-seed metadata) → binding list items 1–12. New
`EDGE_DISCOVERY_COMPATIBILITY_CHECKLIST.md` (pass/fail gate, sections A–E).

**18. Was CAMPAIGN_027 created?** **No.** (Expected: no.)

**19. Was any strategy approved?** **No.** (Expected: no.)

**20. Does `approved_strategies.yaml` remain `approved: []`?** **Yes.** (Expected: yes.)

**21. Do paper/demo/live remain blocked?** **Yes** — freeze gate confirms the
order-capable loops refuse; no executor/broker/OANDA file changed. (Expected: yes.)

**22. Was the test lockbox opened?** **No.** (Expected: no.)

**23. Archive / freeze / secrets status.** All green (see item 25).

**24. Ruff / pytest results.** See item 25 (ruff clean; pytest 2157 pass / 3 skip).

**25. Validation (Phase 10 re-run).**
- `pytest tests/ -q` → **2157 passed, 3 skipped** (skips are local-data-absent only).
- `ruff check src tests scripts research` → **All checks passed**.
- `check_research_freeze.py` → **ALL CHECKS PASSED** (loops refuse; no creds).
- `validate_research_archive.py` → **ALL CHECKS PASSED** (evidence-index links resolve).
- `scan_artifacts_for_secrets.py` → **PASSED**.
- `configs/approved_strategies.yaml` → `approved: []`.
- No executor/broker/OANDA/loop/approval/execution file changed vs `main`.
- No `.env`/credentials/DB dumps/raw candles/bulky artifacts committed
  (ledgers/frames gitignored).
- C011 remains the null benchmark; C025 and C026 remain REJECT.

**26. Known limitations.** (a) The eligible idea's edge is **wafer-thin** and sits
near the cost band — robust *only* in the filtered low-vol/quiet/short subset and
**not** positive in every year (2024, 2026-partial negative). (b) The 3-of-5
filter retention is a **forking-path** risk requiring precommit + clean
re-confirmation. (c) Sub-H1 ideas were **out-of-scope** (lab reads SQLite only;
Postgres M1 data not wired in). (d) Carry/event ideas were **data-blocked**. (e)
The "edge" is *information* (beats nulls); whether it is a *durable tradable
profit* is exactly what a precommitted train/validation/test campaign must decide
— this sprint deliberately did not.

**27. Recommended next step.** Do **not** open a campaign automatically. If a
human wants to pursue the one eligible idea, run the **drafted precommit prompt**
as a *scaffold* sprint (assign the next unused campaign number after grep-verify;
C027 expected free), honoring the four pre-registered kill-conditions, full
train/validation/test discipline, and Backtrader-parity-before-promotion.
Otherwise the front gate's verdict stands: every other family is cheaply rejected,
inconclusive, or data-blocked, and no campaign is warranted.

## Exact files to review first

1. [`EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md`](EDGE_DISCOVERY_IDEA_RANKING_AND_DECISION.md) — the decision.
2. [`EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md`](EDGE_DISCOVERY_FILTER_ABLATION_RESULTS.md) — why the one idea is (borderline) eligible.
3. [`EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md`](EDGE_DISCOVERY_MATCHED_NULL_SCREENING_RESULTS.md) — information-vs-tradability + selection-noise.
4. [`NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md`](NEXT_CAMPAIGN_PROMPT_FROM_EDGE_DISCOVERY_FRONT_GATE.md) — the draft prompt (NOT executed).
5. [`EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md`](EDGE_DISCOVERY_OPPORTUNITY_MAP_REFRESH.md) — the cost/vol facts that shaped selection.
