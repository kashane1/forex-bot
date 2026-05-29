# Non-time-bar next-research decision

**Sprint:** `research-external-non-time-bar-thesis-discovery-001` · Phase 7
**Type:** research-direction decision. Approves nothing; creates no campaign.

---

## 1. Decision

**Option 2 — run front-gate screening on exactly ONE shortlisted idea
(H16 · overshoot-exhaustion fade)**, with **H03 · thin-move fade** as the pre-declared
fallback and **H12 · spread-state filter** evaluated as a G4 filter-ablation. This is a
**front-gate screen, not a campaign** — it produces diagnostics + a pass/block verdict,
approves nothing, and opens no test lockbox.

We explicitly do **not** choose:
- **Option 1 (keep paused)** — the sprint produced a genuinely new, cheap, intraday,
  financing-free idea (H16) that is **not pre-empted by any prior rejection**; the
  cheapest honest way to resolve it is the one screen the lab was built for, not
  indefinite pause.
- **Option 3 (retire)** — premature: H16/H03 are new microstructure questions never
  tested here; we should let the front gate kill them on evidence, not assumption.
- **Option 4 (require new infrastructure first)** — not needed: the edge-discovery lab
  (matched nulls, cost-feasibility, filter-ablation, forward-returns) already exists, and
  H16 reuses the overshoot metric the feasibility tooling already computes. Only a thin
  event→forward-return adapter is required, which is part of *running* the screen.

## 2. Why H16 is the single idea to screen first

| criterion | H16 overshoot-exhaustion fade |
|---|---|
| Externally/structurally distinct from every rejected family | yes (bar-completion geometry; not trend/breakout/level-reversion) |
| Pre-empted by C027 (reversion) / C031 (TSMOM) / C029 (breakout)? | **no** |
| Implementation cost | lowest (overshoot metric already computed) |
| Financing exposure (C031 lesson) | none (intraday, closes before NY rollover) |
| Cost-feasible cell available (feasibility study) | yes (range ≥ 25–30 pip / vol ≥ 50 pip) |
| Falsifiable against a matched null | yes (geometry-matched null) |

## 3. Pre-declared screen design (to avoid the C028 selection-noise trap)

To prevent the front-gate screen from becoming a variant hunt:
- **One primary hypothesis (H16), one fallback (H03), declared *before* running.** No
  sweeping many thresholds/pairs and keeping the best; if multiple cells are examined,
  the `multiple_comparison` best-of-N test is binding and a non-robust "winner" is **not**
  evidence.
- **Both directions pre-registered:** overshoot→reversion is the thesis; if the data
  show overshoot→continuation instead, that is a *different* hypothesis and must be
  treated as a new, separately-registered claim, not a saved result.
- **Cost-feasible cell only** (per feasibility study) and **H12 spread-state filter on**,
  so the screen reflects realistically tradeable conditions.
- **≥ 2 pairs** (G5) — no single-pair artifact (the C027 failure).

## 4. Binding stop criteria (what kills the lane)

If, in the front-gate screen, **both H16 and the H03 fallback** fail to **beat their
structure-matched nulls post-cost on ≥ 2 pairs** (lab flags `WITHIN_MATCHED_NULL` /
`BELOW_MATCHED_NULL`, or `COST_HOSTILE` on the traded cell), then:
- the **directional / microstructure non-time-bar search on the current 7-major M1
  corpus is treated as exhausted** (→ effectively Option 3), and
- reopening requires **new data** (≥ 10–15y history, non-USD crosses, or true tick data),
  not another idea on the same corpus.

This makes the screen a genuine decision point, not an open-ended invitation.

## 5. What this decision does NOT do

No campaign / no CAMPAIGN_030 / no scaffold / no approval / no
`approved_strategies.yaml` edit / no paper-demo-live / no OANDA / no test lockbox. The
next sprint is a **front-gate screening** sprint whose only outputs are diagnostics and a
pass/block verdict. The drafted prompt is in
[`NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md`](NEXT_PROMPT_AFTER_NON_TIME_BAR_THESIS_DISCOVERY.md).

## 6. Status snapshot

- Non-time-bar **lane:** still PAUSED for *campaigns*; one **front-gate screen** is
  authorised on H16 (this does not un-pause the lane — a campaign still requires a
  passing screen + the lane re-entry criteria).
- Approved strategies: `approved: []`. Paper/demo/live: blocked. Freeze: intact.
