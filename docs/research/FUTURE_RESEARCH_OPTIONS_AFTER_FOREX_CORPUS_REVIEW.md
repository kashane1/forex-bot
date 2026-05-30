# Future Research Options — After the Forex Corpus Review

**Purpose:** enumerate and rank the plausible next research directions
that follow from this viability review. No option here creates a
campaign, approves a strategy, or trades. Phase 6 selects exactly one.

## Scoring scheme

Each option is scored **1–5 on every axis, where 5 is most favorable
for proceeding**. Note the orientation of the "cost", "complexity", and
"repeat-risk" axes: a **high score means low cost / low complexity / low
risk of repeating prior failures** (i.e., favorable). The composite is
the simple mean (equal weight) — a decision aid, not a verdict.

| Axis | 5 (favorable) ↔ 1 (unfavorable) |
|------|---------------------------------|
| Novelty | genuinely new search space ↔ rehash of tested ground |
| Cost (effort+money) | cheap/free ↔ expensive |
| Data availability | already have / free ↔ paid/hard to source |
| Implementation complexity | trivial ↔ large new infra |
| Expected edge potential | structurally better-conditioned ↔ same cost wall |
| Repeat-risk (low=good) | unlikely to repeat prior failures ↔ likely to |

---

## Options, scored

### Option 1 — Stop strategy research; harden infrastructure/docs
Pause idea generation entirely; invest in cost/execution simulation,
evidence-archive hygiene, the front-gate lab, and documentation.
- Novelty **2** · Cost **5** · Data **5** · Complexity **5** · Edge
  potential **2** · Repeat-risk **5** → **composite 4.0**
- *Read:* very cheap and safe, directly compounds future work, but
  produces no new edge by itself. A strong *complement*, weak as the
  sole direction.

### Option 2 — Continue current corpus only if a new external thesis appears
The Phase 3 decision. Keep the corpus in control/baseline mode; run a
single front-gate screen only behind a genuine, cost-aware new thesis.
- Novelty **2** · Cost **5** · Data **5** · Complexity **5** · Edge
  potential **2** · Repeat-risk **3** → **composite 3.7**
- *Read:* correct as a *standing policy*, but passive — it waits for an
  input that may not arrive, and the cost wall caps its edge potential.

### Option 3 — Add non-USD FX crosses
Ingest EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, … on the existing pipeline.
- Novelty **3** · Cost **5** · Data **5** · Complexity **4** · Edge
  potential **3** · Repeat-risk **3** → **composite 3.8**
- *Read:* the **cheapest genuinely-new data** (same broker, same
  loaders, same cost model). Breaks USD-leg crowding and finally powers
  breadth families (cross-sectional, carry, relative-value) that were
  underpowered on 7 USD majors. **Does not fix the cost wall** — spreads
  are wider — so it addresses crowding/breadth, not the squeeze.

### Option 4 — Add an index / metal / crypto research lane
Open one non-FX lane (index futures/CFD, metals, or crypto).
- Novelty **4** · Cost **3** · Data **4** (crypto/metals free; index
  futures partial) · Complexity **3** · Edge potential **4** ·
  Repeat-risk **4** → **composite 3.7**
- *Read:* the strongest move on **edge-source diversity** — different
  return drivers (equity premium, trend persistence, crypto momentum/
  carry) than spot-FX noise, with larger gross edges that can clear
  higher cost. More infra than crosses; crypto needs 24/7 handling.

### Option 5 — Add higher-quality tick / futures data
Bring in true tick/L2 (unlocks microstructure) and/or futures (better
cost profile + deep history).
- Novelty **4** · Cost **2** · Data **2** (mostly paid) · Complexity
  **2** · Edge potential **4** · Repeat-risk **4** → **composite 3.0**
- *Read:* highest *ceiling* (the only way to fix both the cost profile
  *and* the missing-microstructure ceiling) but the **most expensive and
  complex**, and tick data is overfit-prone. Better sequenced *after* a
  cheaper lane proves the multi-market approach.

### Option 6 — Build a multi-market front-gate discovery lab
Generalize the existing edge-discovery lab (matched-null + ablation +
MCC + cost-feasibility) to ingest and screen *any* instrument/asset
class uniformly.
- Novelty **4** · Cost **3** · Data **4** (reuses whatever is ingested)
  · Complexity **3** · Edge potential **4** (force-multiplier) ·
  Repeat-risk **5** → **composite 3.8**
- *Read:* doesn't find an edge by itself, but makes **every** subsequent
  market lane cheap and methodologically consistent, and is the single
  best guard against repeating prior failures. Natural enabler for
  Options 3/4/5. Builds on infra that already exists and works.

### Option 7 — Focus on cost/execution simulation before any new ideas
Sharpen the cost/slippage/financing/observed-rate model and execution
realism before generating ideas.
- Novelty **2** · Cost **4** · Data **4** · Complexity **4** · Edge
  potential **2** · Repeat-risk **5** → **composite 3.5**
- *Read:* since cost is *the* binding constraint, better cost modeling
  raises the trustworthiness of every future screen — but, like Option
  1, it produces no edge alone. Best folded into whichever lane is
  chosen.

### Option 8 — Convert the project into a market-research lab (not a bot)
Reframe the deliverable from "a trading bot" to "a market-research /
front-gate lab" whose output is *evidence and decisions*, not orders.
- Novelty **3** · Cost **4** · Data **5** · Complexity **4** · Edge
  potential **2** (reframing, not edge) · Repeat-risk **5** →
  **composite 3.8**
- *Read:* arguably what the project *already is* under the freeze.
  Formalizing it is cheap and honest, lowers pressure to force an
  approval, and pairs naturally with Option 6. Not an edge source.

---

## Ranking (by composite, with judgment)

| Rank | Option | Composite | One-line |
|------|--------|-----------|----------|
| 1 | **Opt 1 — harden infra/docs** | 4.0 | cheapest, compounds everything, no edge alone |
| =2 | **Opt 3 — non-USD crosses** | 3.8 | cheapest *new data*; fixes crowding not cost |
| =2 | **Opt 6 — multi-market front-gate lab** | 3.8 | force-multiplier + best repeat-risk guard |
| =2 | **Opt 8 — reframe as research lab** | 3.8 | honest, cheap; pairs with Opt 6 |
| 5 | **Opt 3+6 (combined)** | — | *see Phase 6 — the pragmatic pairing* |
| 6 | **Opt 4 — index/metal/crypto lane** | 3.7 | best edge-diversity; more infra |
| =6 | **Opt 2 — corpus only w/ new thesis** | 3.7 | correct standing policy; passive |
| 8 | **Opt 7 — cost/execution sim first** | 3.5 | raises trust; fold into chosen lane |
| 9 | **Opt 5 — tick/futures data** | 3.0 | highest ceiling, most cost/complexity |

### Judgment beyond the arithmetic

The pure composites cluster the cheap-but-no-edge options (1, 7, 8) near
the top because low cost/complexity scores dominate. The *edge* options
(4, 5) score lower because they cost more — but they are the only ones
that attack the structural problem (different cost profile / different
drivers). The sensible synthesis is a **sequenced pairing**: a
**force-multiplier enabler (Opt 6)** plus the **cheapest new data that
exercises it (Opt 3)**, with cost-modeling (Opt 7) and the lab reframing
(Opt 8) folded in — deferring the expensive lanes (4 then 5) until the
multi-market approach has earned them. Phase 6 makes this concrete and
picks exactly one direction for the next sprint.
