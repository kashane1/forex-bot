# Forex Strategy-Search Programme — Final Lessons Learned

**Sprint:** `research-forex-strategy-search-archive-001` · Phase 2
**Type:** Retrospective documentation. No verdict change, no approval.
**Date:** 2026-05-31
**Supersedes:** `FOREX_BOT_RESEARCH_LESSONS_LEARNED_001.md`, `PROGRAMME_LESSONS_LEARNED.md` (as programme terminal lessons)

---

## Executive summary

The research **process worked** — it repeatedly killed plausible-looking leads
before they became false confidence. The **market did not cooperate** — no
mechanism tested on this corpus and these data classes produced a tradable edge.
The headline failure mode evolved from **cost-defeated** to **idea quality /
market efficiency** once the financing-free futures carry diagnostic confirmed
carry is genuinely non-predictive, not merely financing-blocked.

---

## 1. What worked

### 1a. Governance & freeze enforcement

- **Machine-enforced approval gate** (`configs/approved_strategies.yaml` +
  `check_research_freeze.py`) made "no strategy is approved" a checked invariant,
  not a promise. Every sprint could move fast because the gate could not be
  silently weakened.
- **Pre-commit discipline** — locked-definition docs before runs prevented
  post-hoc threshold drift and made rejects auditable.
- **Train-gate terminality** — failing train gate stopped validation rescue
  attempts; the TEST lockbox stayed sealed until earned (it never was).

### 1b. Falsification infrastructure

- **Matched-null benchmarks** separated "loses less than random" from "makes money."
- **Cost-feasibility gates** caught sub-spread effects before expensive campaigns.
- **Filter-ablation and multiple-comparison gates** exposed forking-path risk (C027).
- **Independent parity harnesses** (C029) confirmed rejects were the strategy's, not
  bookkeeping artifacts.

### 1c. Honest cost modeling

- **Bid/ask spread data** changed every conclusion; mid-only backtests would have
  overstated edges.
- **Conservative cost stress (2×)** and **financing overlays** flipped multiple
  "borderline" results negative before they reached scaffold stage.
- **Turnover amplification anti-pattern** (C012→C013 slope) was codified after
  empirical demonstration.

### 1d. Platform engineering

- Pure, unit-tested feature modules with causality tests caught lookahead before
  analysis depended on them.
- Deterministic, resumable scripts + compact committed summaries kept the repo
  reviewable across 31 campaigns.
- Additive market expansion (crosses, futures) preserved spot corpus untouched.

### 1e. Decision-forcing venue tests

- The futures pivot was the correct final experiment: it removed the financing
  wall and tested the programme's last hope (carry) under fair conditions.
- The null result (`CARRY_DOES_NOT_SURVIVE_IN_FUTURES`) converted an ambiguous
  "maybe cost-fixable" narrative into a decisive conclusion.

---

## 2. What failed

### 2a. No tradable edge found

- **31 campaigns, zero approvals.** Every numbered campaign ended rejected,
  cost-defeated, or financing-defeated.
- **Direction remained null** across sessions, hours, vol regimes, macro regimes,
  and instrument breadth. Continuation ≈ reversion ≈ 0.49–0.50 everywhere tested.
- **Indicator confluence entries** sat at AUC ≈ 0.50 — structural features (EMA
  reclaim, ADX, pullback depth, RSI, MTF confluence) did not separate winners
  from losers.

### 2b. Genuine effects were too small or non-predictive

- **C1** — real on USD majors but failed cross replication (USD-regime artifact).
- **S4** — real triangular no-arb reversion but ~10× inside the retail cost band.
- **Spot carry** — mechanical accrual exists; spot-predictive leg statistically zero.
- **Futures carry** — confirmed non-predictive (h3 +0.04 %/qtr, t = 0.09); the
  accrual premium was the rate differential, not a tradable price edge.

### 2c. Exit/stop tweaks cannot rescue absent entry edges

- Protective stops (C018), thesis invalidation (C019), early-exit management rules,
  and stop geometry variants all failed to convert negative train expectancy.
- MFE:MAE after arbitrary entry < 1 — no free favorable asymmetry to harvest.
- "Wider stops fix it" is false: early-exit counterfactuals *reduced* expectancy.

### 2d. Breadth and venue changes did not help

- **Cross expansion** broke USD-collinearity (S2 breadth passed) and found genuine
  RV structure (S4) but did not move the cost wall.
- **Non-time-bar alt clocks** changed sampling, not edge; C029 gross-positive but
  net-negative after M1-resolved cost.
- **Futures venue** removed financing penalty and accrual benefit simultaneously;
  carry predictive content stayed null.

---

## 3. Recurring failure modes

| Mode | Mechanism | Examples |
|------|-----------|----------|
| **Within-null / no effect** | Signal does not predict forward returns | C020–023, S2, S3, H16, H03, macro context |
| **Cost-defeated** | Gross effect exists but < round-trip spread | C026, C029, C1 validation, C008/C027 |
| **Financing-defeated** | Overnight holding cost erases gross premium | C031, spot carry |
| **Failed replication** | Effect real in discovery universe, artifact elsewhere | C1 cross (S1) |
| **Selection noise** | Best-of-N inflation without economic prior | C028 |
| **Turnover amplification** | Filter increases trade count without signal quality | C012→C013 monotonic worsening |
| **USD/regime artifact** | Collinear with one macro cycle or USD leg | C016, C1 replication, C031 book |
| **Rescue-by-exit fallacy** | Exit tweak applied to absent entry edge | C018, C019, post-entry management |
| **No-stop illusion** | Fixed-horizon hold through adverse excursion | London compression lead |

---

## 4. Recurring false assumptions

1. **"A small gross edge will survive cost if we optimize execution."** It didn't —
   C029 was gross +0.084R and still net-negative; S4 was genuine but 10× inside
   the band.
2. **"Lower timeframe / more bars = more opportunity."** M5/M15 increased turnover
   and spread drag without improving signal (C021, C025, C026 ladder).
3. **"Crosses add diversification that fixes the cost wall."** Crosses are wider;
   breadth added history/microstructure walls unchanged.
4. **"Non-time bars fix lookahead / sampling and reveal hidden edge."** Alt clocks
   are a legitimate tool but not an edge source on this corpus.
5. **"Carry is financing-defeated; a fair venue will rescue it."** Falsified by
   futures diagnostic — carry is non-predictive, not merely cost-blocked.
6. **"Post-entry signals can salvage entry-null trades."** Descriptively real
   post-entry separation reduced expectancy when acted on.
7. **"Almost flat / less-bad = worth another parameter pass."** Flatness is not
   edge; gates correctly rejected wafer-thin survivors (C027).
8. **"Macro context will identify tradable regimes."** Slow context carried no
   actionable conditioning; existing session/rollover filters already dominated.
9. **"More filters improve signal quality."** Turnover amplification made results
   monotonically worse (C012→C013).
10. **"Validation uplift rescues train failure."** Gate discipline correctly
    treated validation as confirmation, not rescue (C008, C020, C027).

---

## 5. Process successes

1. **Cheap falsification before expensive campaigns** — front gates, cost-feasibility
   screens, and matched-null batteries saved months of scaffold work.
2. **Evidence integrity remediation** — dedup audit, forensic replays, and parity
   drills prevented contaminated verdicts from driving decisions.
3. **Explicit separation of "effect exists" vs "tradable edge exists"** — carry
   gross existence vs spot-predictive null; C027 above null but below profitability.
4. **Pre-registered terminal decisions** — programme-direction Option E triggered
   automatically when futures carry failed; no ambiguity about next step.
5. **Do-not-repeat list** — closed lanes documented with rationale before cross
   expansion could re-run them in new costumes.
6. **Additive infrastructure pattern** — crosses and futures bolted on without
   breaking spot corpus; high reuse for any future restart.

---

## 6. Process weaknesses

1. **Single-cycle history ceiling** — ~2021–2026 spot window contained one monotonic
   rate cycle; regime theses were non-identifiable. Futures EOD extended carry to
   24 years but still found null.
2. **Missing data legs** — JP rate leg absent for macro differentials; financing
   used estimates until FRED ingest; S4 needed tick data never acquired.
3. **Campaign contamination risk** — duplicate H4 candles invalidated early
   bespoke metrics; required dedup sprint and reruns.
4. **Power limits on slow signals** — C031 ~3 annual cycles; bootstrap CI ±0.9
   Sharpe; acknowledged but still falsified.
5. **Late venue test** — futures pivot came after extensive spot mining; ideally
   would have been earlier, though the spot work was necessary to identify cost
   as the proximate killer before testing venue independence.
6. **Documentation volume** — ~1000 research docs create navigation overhead;
   this archive sprint consolidates the terminal ledger.

---

## 7. Durable rules for any future restart

1. Precommit hypothesis + cost/stop/multiple-testing model **before** any run.
2. Always run: realistic intrabar stop + conservative cost + multiple-testing
   haircut + year/half-split + latency-independence (for context features).
3. Count every cell searched; carry the count into significance haircuts.
4. Separate "effect exists" from "tradable edge exists" in every result doc.
5. Require a stated economic mechanism before coding — no mechanism, no campaign.
6. Treat **new data class or new market** as the unlock, not new parameters on
   old data.
7. Keep the TEST window sealed until a fully-precommitted campaign earns one
   final look.
8. Never reopen a closed lane without a new external thesis — re-tunes are
   forbidden (see `DO_NOT_REPEAT_LIST.md`).
9. Venue changes test cost structure; they cannot manufacture predictability
   (proven by futures carry null).
10. Prefer no-trade filters as the first, safest use of any context signal.

---

## 8. What would have fooled us without the diagnostics

| Lead | Looked promising | Killed by |
|------|------------------|-----------|
| No-stop London compression | +2.2/+6.1 pips both splits | Intrabar stop + Bonferroni ×12 + year breakdown |
| C008 validation uplift | +0.161 R, 6/6 pairs | Train gate fail; lockbox sealed |
| C027 matched-null pass | Above structure-matched null | Net train expectancy wafer-thin; 4/8 gates fail |
| C029 gross-positive | +0.0839R gross PF>1 | M1-resolved cost → net −0.019R |
| C031 pre-cost Sharpe | +0.32 | Financing ≈4× spread → net −0.07 |
| Post-entry management signals | Descriptive separation | Counterfactual early exits reduce expectancy |
| Spot carry gross premium | +0.74 %/qtr accrual | Spot-predictive leg ≈ 0; futures confirms |

---

## 9. Cross-references

- Closed lanes: `DO_NOT_REPEAT_LIST.md`
- Restart gates: `FOREX_STRATEGY_SEARCH_ARCHIVE_DECISION.md` §4
- Evidence ledger: `FOREX_STRATEGY_SEARCH_FINAL_EVIDENCE_INVENTORY.md`
- Prior pause memo: `STRATEGY_SEARCH_PAUSE_AFTER_USDJPY_MACRO_CONTEXT.md`
