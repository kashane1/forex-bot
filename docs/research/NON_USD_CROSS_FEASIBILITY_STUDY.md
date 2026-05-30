# Non-USD Cross Feasibility Study

**Purpose:** assess whether non-USD FX crosses are worth adding to the
research corpus as the first multi-market expansion — their cost profile,
advantages/disadvantages versus the USD majors, and whether they address
the structural problems the viability review identified (USD-leg
crowding, breadth-poverty). **Design/research only — no ingestion, no
backtest, no broker calls.** Cost figures are qualitative retail
estimates to be confirmed by a cost sprint.

## The question being answered

The viability review found the seven USD-major corpus is (a)
**structurally cost-defeated** and (b) **breadth-poor** (every pair
shares the USD leg → correlated signals, a structural USD bet,
underpowered cross-sectional/carry/relative-value families). Crosses are
the cheapest new data we can add on the existing pipeline. The question
is **not** "are crosses cheaper to trade?" (they are not) but **"do
crosses fix the breadth/crowding limitation enough to justify adding
them, given they do not fix the cost wall?"**

## Instruments evaluated

EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY, NZD_JPY, EUR_AUD, EUR_CHF, GBP_CHF.

## Expected cost profile

Crosses are **generally wider** than EUR_USD because their spread roughly
compounds the two underlying legs. Rough ordering (tightest → widest):

| Band | Crosses | Implication |
|------|---------|-------------|
| Near-major (≈1–2 pip) | EUR_GBP, EUR_JPY | best cost candidates; closest to passing a cost gate |
| Moderate (≈1.5–3 pip) | AUD_JPY, EUR_CHF, EUR_AUD | carry/cross themes; cost wall higher |
| Wide/volatile (≈2.5–4 pip) | GBP_JPY, NZD_JPY, GBP_CHF | cost-hostile individually; valued for breadth/independence |

Carry crosses (AUD_JPY, NZD_JPY) have **financing as a first-order
driver** — an instrument-specific financing model is mandatory or any
result is meaningless. JPY crosses inherit JPY-funding behaviour; CHF
crosses inherit safe-haven behaviour.

**Net cost verdict:** crosses **do not relieve** the two-sided cost
squeeze; if anything the spread wall is higher. They must therefore be
justified on *what they add*, not on cost.

## Likely advantages over USD majors

1. **Break USD-leg crowding.** Crosses are not a restatement of the USD
   factor, so they provide **independent legs** for cross-sectional and
   relative-value designs — the exact thing missing when C016
   (cross-sectional) and C028 (relative-value) were underpowered, and
   when C031's book collapsed to "a structural USD bet".
2. **Genuine carry breadth.** AUD_JPY/NZD_JPY (and to a degree EUR_JPY)
   express classic FX carry that 7 USD majors cannot — making a carry
   study *possible* (it was data-blocked before), albeit still
   cost/financing-gated.
3. **Independent replication for existing factors.** The C1 verdict and
   the non-time-bar/H16/H03 closeouts all named "non-USD crosses" as a
   reopen condition specifically to supply **independent replications**
   and settle the residual USD share. Crosses let a *previously
   validated factor* be re-screened on fresh, non-collinear data
   (a legitimate fresh screen, **not** a re-tune).
4. **Cheapest possible expansion.** Same OANDA model, same H4 bid/ask +
   M1 pipeline, same cost-model shape → lowest implementation risk of any
   new market.

## Likely disadvantages

1. **No cost relief** — wider spreads; the binding constraint is
   unchanged. A factor that was cost-defeated on majors will likely be
   cost-defeated on crosses too unless it is *materially stronger* there.
2. **Wider/again-correlated in stress.** In risk-off, JPY and CHF
   crosses co-move strongly (safe-haven), so "breadth" partially
   collapses exactly when it matters — independence is regime-dependent.
3. **Structural breaks & thin history.** EUR_CHF has the 2015 SNB-peg
   removal (a hard discontinuity); thinner crosses (NZD_JPY, GBP_CHF)
   have wider, less stable spreads and lower liquidity.
4. **Same sample length.** Crosses from the same vendor share the ~6.4y
   window — they add **breadth, not history**, so slow/regime/macro
   underpowering is *not* solved by crosses alone.
5. **Volume is still a tick-count proxy** — crosses do not unlock the
   microstructure lane.

## Do crosses address the previously observed crowding/cost issues?

| Issue | Addressed by crosses? |
|-------|------------------------|
| USD-leg crowding / correlated signals | **Yes** — primary benefit; adds independent legs |
| Breadth-poverty (cross-sectional/carry/RV underpowered) | **Yes (partially)** — enables breadth families; regime-dependent independence |
| Two-sided cost squeeze (spread + financing) | **No** — crosses are wider; cost wall unchanged or higher |
| Short sample (~6.4y) | **No** — same window |
| No true tick/L2 (microstructure) | **No** — still tick-count proxy |

## Verdict — are they worth adding?

**Yes — worth adding, with scoped expectations.** Crosses are the
**cheapest, lowest-risk, highest-information** expansion available and
they directly attack the two limitations crosses *can* fix
(crowding/breadth) while honestly **not** fixing the cost wall. Their
research value is twofold: (1) enabling breadth families that were
data-blocked, and (2) supplying **independent replications** to settle
the residual-USD question for genuine factors like C1 via a fresh
pre-registered screen.

They are **not** expected to, by themselves, produce a cost-surviving
directional edge where majors failed — so they should be framed as a
**breadth/replication and capability** expansion that exercises the
multi-market gate, with the understanding that the *cost-structure* fix
(futures) and the *new-driver* fix (crypto/index/metals) are separate,
later expansions.

**Recommended first wave:** EUR_GBP, EUR_JPY, GBP_JPY, AUD_JPY (lowest
cost + clearest breadth/carry value), then NZD_JPY, EUR_AUD, EUR_CHF,
GBP_CHF (window EUR_CHF around 2015). Ingestion is specified — not
performed — in `MULTI_MARKET_DATA_ACQUISITION_ROADMAP.md` and chosen in
`NEXT_DATA_EXPANSION_DECISION.md`.
