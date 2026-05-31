# Next Prompt — After Cross Factor-Discovery Planning

The expanded-FX factor-discovery roadmap is complete. The 15-instrument universe
(7 USD majors + 8 populated non-USD crosses) has been mapped, 24 cross-enabled
factor families enumerated, the failure-prone ones fenced, the survivors ranked,
a 5-family shortlist drawn, and **exactly one next direction chosen: an
independent, pre-registered replication of the locked C1 factor on the non-USD
crosses** (to settle whether C1 is a genuine multi-TF-confluence effect or a
residual-USD artifact).

The next sprint **may open a factor-discovery screen** of that one frozen factor.
It is **not** a campaign, **not** a strategy, **not** an approval. It runs a
single pre-registered replication and produces a verdict — exactly as the
original C1, H16, and H03 front-gate screens did.

---

## Recommended next sprint — C1 cross replication front-gate screen

> Branch: `research-c1-cross-replication-screen-001`
>
> **A single, fresh, pre-registered front-gate replication of the locked C1
> factor on the 8 non-USD crosses.** Replication, NOT a re-tune. Produce a
> verdict (`C1_ARTIFACT` / `C1_GENUINE_BUT_COST_DEFEATED` /
> `C1_GENUINE_AND_COST_SURVIVING`) with committed evidence. Build no strategy,
> create no campaign, approve nothing, enable no paper/demo/live.
>
> Read first (this planning sprint's outputs):
> - `NEXT_FACTOR_DISCOVERY_DIRECTION.md` — the chosen direction + stop criteria.
> - `CROSS_UNIVERSE_FACTOR_SHORTLIST.md` (S1) — thesis, failure modes, gate reqs.
> - `DO_NOT_REPEAT_LIST.md` — the C1-replication-vs-re-tune fence (§1).
> - `C1_CROSS_PAIR_STUDY.md` + `project_c1_factor_validation` memory — the locked
>   C1 definition and the majors result it must NOT be re-tuned against.
> - `NONUSD_CROSS_COST_BASELINE.md` — the measured cross spreads the cost gate uses.
> - `MULTI_MARKET_FRONT_GATE_FRAMEWORK.md` — Stage-2/Stage-3 evidence bar.
>
> The sprint MUST:
>
> 1. **Pre-register before touching cross data.** In a committed precommit doc,
>    freeze: the exact C1 definition (H4 trend, H1 trend, M15 aligned; EMA 20/50,
>    slope-3; rising-edge + 60-min cooldown; signed forward return at 30/60min) —
>    copied verbatim from the locked majors definition, **changed in no way**; the
>    8-cross instrument set; the matched-null design + seed count; the
>    multiple-comparison correction across 8 pairs; and the **net-of-cost decision
>    rule** using `forex_bot.research.cost_models` (round-trip measured cross
>    spread + two-legged carry, `debit_r`). No threshold is chosen after seeing a
>    cross number.
> 2. **Reuse the existing runner as a replication.** Drive the existing C1
>    validation harness (`scripts/run_c1_factor_validation.py`) over the crosses
>    (widen its pair set to the populated crosses; the materialized H4M1/H1/M15
>    bars already exist). Do NOT fork the C1 logic, do NOT add per-cross
>    parameters, do NOT introduce a vol/threshold filter tuned to crosses.
> 3. **Report sign + magnitude + matched-null Z + net-of-cost per cross**, read
>    directly from committed CSVs (artifact-first; verify CSV-on-disk before
>    writing any number — the integrity lesson from the discovery sprint).
> 4. **Emit one verdict** against the pre-stated stop criteria in
>    `NEXT_FACTOR_DISCOVERY_DIRECTION.md`. A net-of-cost-positive result is NOT
>    expected (cross spreads are wider); the deliverable is the
>    artifact-vs-genuine answer, not a tradable.
> 5. **Stop at the verdict.** If the verdict is `C1_GENUINE_AND_COST_SURVIVING`
>    (not expected), the sprint still creates **no** campaign — it recommends a
>    *separate, later* pre-committed campaign sprint subject to human approval.
>
> Deliverable: a precommit doc + a result doc + a verdict, all under
> `docs/research/`. New code limited to widening the existing C1 runner's pair set
> and any cross-cost wiring; NO new strategy, signal, entry/exit, or campaign code.

---

## Guardrails carried into the next sprint

- **No campaign of any number** (no CAMPAIGN_032; the C1 screen is a *screen*,
  not a campaign).
- **Replication only** — the C1 definition is frozen and copied verbatim; any
  parameter change converts it into a forbidden re-tune (`DO_NOT_REPEAT_LIST` §1).
- No new factor family is opened (S2–S5 are explicitly *later* sprints; carry
  remains prerequisite-blocked on financing-data ingest).
- No strategy approved; `configs/approved_strategies.yaml` stays `approved: []`;
  paper/demo/live stay blocked; `forex_bot.approval` fails closed.
- No credentials, no broker/trading-API calls; the cross data is already
  populated, so no new ingestion is required.
- Pre-registration precedes any conditioned number; matched-null +
  multiple-comparison + measured-cost gate are mandatory (Stage-2/Stage-3 bar).
- Freeze stays intact; the sprint produces evidence and a verdict, nothing
  order-capable.

---

## Sprint after that (do NOT start it now — for context only)

If C1 replicates as genuine (cost-defeated or surviving), the **second** cross
factor sprint is **S2 — the cross-implied currency-strength index** (a fresh
breadth-pure discovery, pre-registered, cost-first). If C1 evaporates as an
artifact, the next move is instead the **financing-data prerequisite** (ingest
real swap rates) that unblocks the carry families — or a venue/history expansion
— rather than more factor mining on this corpus. Either way: a new sprint, a
fresh pre-commit, no campaign.
