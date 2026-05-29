# Next-Action Options After the Strategy-Search Pause

**Sprint:** `strategy-search-pause-after-usdjpy-macro-context-001` · **Phase 5**
**Status:** decision-support. Standing decision is `PAUSE_STRATEGY_RESEARCH`. None of these
options is a strategy/campaign; each is a separate, later, explicitly-authorized sprint.

---

## The options

### Option 1 — Stop strategy research; use the bot infra for learning / monitoring only
- **What:** freeze strategy mining; keep the read-only research/monitoring tooling alive.
- **Pros:** zero overfitting risk; preserves all infrastructure; lowest effort.
- **Cons:** no progress toward an edge until a new trigger appears.
- **Effort:** minimal. **Overfit risk:** none. **Unlocks a restart?** no (waits for one).

### Option 2 — Build external data-acquisition infrastructure
- **What:** acquire/ingest the data that would make blocked theses *testable*: verified JP
  rate leg, longer multi-cycle history, verified BOJ/CPI economic-event calendar,
  rate-differential series, (optionally) options/vol or order-flow proxy.
- **Pros:** directly removes the binding constraints found this program (rate-regime
  non-identifiability; missing JP leg; deferred calendar). Pure infrastructure, no strategy.
- **Cons:** sourcing/verification effort; some data may be costly or unavailable.
- **Effort:** medium–high. **Overfit risk:** none (no strategy). **Unlocks a restart?**
  yes — satisfies restart trigger #2.

### Option 3 — Research public / academic FX strategies externally (before any code)
- **What:** literature/market-structure review *outside the repo* to source a genuinely
  different, mechanism-backed thesis; bring back a written brief, not code.
- **Pros:** the only path that can satisfy restart trigger #1/#3; cheap; no repo risk.
- **Cons:** may not yield a usable, codable, cost-surviving thesis; requires judgment.
- **Effort:** low–medium. **Overfit risk:** none. **Unlocks a restart?** potentially — if a
  qualifying thesis is found.

### Option 4 — Improve engineering infrastructure
- **What:** CI, docs, data provenance, parity coverage, dashboards/observability.
- **Pros:** compounding quality; makes any future restart faster and safer.
- **Cons:** does not itself create an edge.
- **Effort:** variable. **Overfit risk:** none. **Unlocks a restart?** no (enabling only).

### Option 5 — Build a paper-trading simulator for non-strategy operational testing
- **What:** an operational harness to exercise order/lifecycle plumbing **without** an
  approved strategy (no live signals; no approval).
- **Pros:** de-risks future operationalization; surfaces execution bugs early.
- **Cons:** must stay strictly non-strategy and not touch the live/approval gates; easy to
  scope-creep into "just test this signal."
- **Effort:** medium. **Overfit risk:** none if kept non-strategy. **Unlocks a restart?** no.

### Option 6 — Archive the strategy-search state and return later
- **What:** snapshot the current state (this pause sprint does most of it), then step away.
- **Pros:** clean stopping point; nothing rots; easy to resume.
- **Cons:** no forward progress.
- **Effort:** minimal. **Overfit risk:** none. **Unlocks a restart?** no.

---

## Recommendation

**Primary next action: Option 1 + Option 3 in combination —**

> **Pause strategy mining (Option 1) and do external thesis sourcing *outside the repo*
> (Option 3). Only restart when a restart criterion is met.**

Rationale: the binding problem is **not** tooling or compute — it is the **absence of a
genuinely new, mechanism-backed thesis or new data**. More mining of the current data is
explicitly forbidden by the restart criteria and the lessons learned. External thesis
sourcing is the cheapest path that can actually satisfy a restart trigger, and it carries
zero overfitting/repo risk.

**Secondary (only if the user wants active progress now): Option 2** — build the
external-data-acquisition infrastructure (especially a verified JP rate leg + multi-cycle
history + event calendar), since that *directly* removes the constraints that made the
macro-context lane non-identifiable. This is infrastructure, not strategy, and would unlock
restart trigger #2.

**Explicitly not recommended now:** Options 4/5 as a *primary* focus (useful but they do not
move us toward an edge), and **any** return to strategy mining on the current data.

See `NEXT_SPRINT_PROMPT_AFTER_STRATEGY_SEARCH_PAUSE.md` for the drafted next prompt
(non-strategy: merge-readiness/archive, or external-data infra, or an external-thesis brief).
