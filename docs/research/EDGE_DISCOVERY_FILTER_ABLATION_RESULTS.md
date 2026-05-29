# EDGE_DISCOVERY_FILTER_ABLATION_RESULTS

**Status:** diagnostic / filter-ablation (Phase 5 of
`research-edge-discovery-front-gate-idea-selection-001`). Protocol **level 2**.
Descriptive only — no verdict word, no strategy, no campaign, no approval, no
test lockbox.

> Engine: `research/edge_discovery/front_gate_idea_selection/run_filter_ablation.py`.
> Artifacts: `filter_ablation_probe_summary.csv`, `filter_contribution_scores.csv`,
> `filter_failure_reasons.json`. Prototype: **`zscore_reversion_h4`** (the
> strongest Phase-4 survivor). `failed_breakout_fade_h4` was REJECTED_CHEAPLY in
> Phase 4 and is not ablated.

---

## Prototype and filters

`zscore_reversion_h4` at h12 (11,925 trigger signals, |z|≥2 over a 20-bar mean,
side = toward the mean). Five filters, chosen on **structural/prior grounds, not
in-sample winners**:

- `f_low_vol` — trailing-window ATR percentile ≤ 0.33 (reversion thesis: works
  in calm/range regimes)
- `f_strong_extension` — |z| ≥ 2.5 (deeper extension reverts harder)
- `f_quiet_session` — UTC session ∈ {asia, london} (calmer, cheaper)
- `f_cost_adv_pair` — pair ∈ {USD_JPY, GBP_USD, AUD_USD, EUR_USD} (Phase-2 cheapest)
- `f_long_side` — direction = long (test whether one side carries the edge)

## Trigger-only baseline

n = 11,924; pre-cost +0.000318; **post-cost +0.000055** (h12, realized-spread
overlay) — the marginal positive from Phase 3.

## Filter contributions (lab noise-aware flags)

| Filter | marginal gain | reduction | flag |
|---|---|---|---|
| `f_low_vol` | **+0.000301** | 0.64 | **`FILTER_ADDS_EDGE`** |
| `f_strong_extension` | **+0.000208** | 0.53 | **`FILTER_ADDS_EDGE`** |
| `f_quiet_session` | **+0.000234** | 0.55 | **`FILTER_ADDS_EDGE`** |
| `f_cost_adv_pair` | +0.000098 | 0.43 | `FILTER_ONLY_REDUCES_SAMPLE` |
| `f_long_side` | **−0.000199** | 0.51 | **`FILTER_HURTS_EDGE`** |

- **Three filters genuinely add edge** (low-vol, strong-extension, quiet-session)
  — the marginal expectancy gain exceeds the noise band, not merely a smaller
  sample. This is the first time in the program a filter battery has produced
  `FILTER_ADDS_EDGE` rather than `FILTER_ONLY_REDUCES_SAMPLE`.
- `f_cost_adv_pair` only reduces the sample (no real edge gain) — the cost
  advantage helps the *level* but not the *signal*.
- `f_long_side` **hurts** — the reversion edge lives on the **short** side
  (selling rips), consistent with reversion-from-overbought in an up-drifting
  carry universe. So a campaign would be short-biased, not symmetric.

## Cumulative / leave-one-out

- Cumulative low_vol → +strong → +quiet reaches **post-cost +0.000761** at
  n=1,065 (hit 0.552) — ~14× the trigger-only post-cost. Adding `f_cost_adv_pair`
  (+0.000726, n=615) and `f_long_side` (+0.000309, n=286) does not help / hurts.
- Leave-one-out confirms: dropping any of the three edge-adders lowers post-cost;
  dropping `f_long_side` *raises* it (it was a drag).

**Best evidence-backed configuration:** `low_vol & strong_extension &
quiet_session` (drop the sample-only and edge-hurting filters), short-biased.

## Decisive checks on the edge-adding subset (n = 1,065)

The Phase-4 blockers were (a) does it survive *conservative* cost, and (b) is it
still a 2023-regime artifact? Both were tested here:

| | optimistic cost (realized spread + slip) | conservative cost (1.5-pip spread + slip + **financing**) |
|---|---|---|
| overall post-cost | **+0.000761** | **+0.000626** |
| positive years | **5/7** | **4/7** |

- **Survives conservative cost.** Financing over the 48-hour (h12) hold shaves
  only ~0.00013; the edge does **not** vanish (unlike the *trigger-level* signal,
  which Phase 4 flipped negative under financing). The filters lift the signal
  clear of the cost band.
- **Pair-robust:** positive in **6/7 pairs** (only USD_CHF ≈ −0.00006, flat);
  AUD_USD/NZD_USD strongest. No single-pair dependence.
- **Partly time-robust, with a recency concern:** under conservative cost,
  positive 2020 (+0.0009), 2022 (+0.0014), 2023 (+0.0019), 2025 (+0.0008);
  **negative 2021 (−0.0001), 2024 (−0.0006), 2026-partial (−0.0003)** (4/7
  positive; 5/7 under optimistic cost). The filters cured the Phase-4
  *single-year* (2023-only) dominance — it is now multi-year positive — but
  **two of the three most recent periods (2024, 2026) are negative**, a
  deterioration/recency risk that train/validation/test must adjudicate.

## Is a strategy campaign justified?

This is the **only idea in the sprint** for which the answer is *plausibly yes*:
it clears every cheap edge-discovery diagnostic that C025/C026 failed —
cost-feasible, forward-return information present, **beats all six matched
nulls**, **filters add edge** (not just reduce sample), **survives conservative
financing cost**, **pair-robust (6/7)**, and **multi-year positive (4/7)**.

Remaining, *documented* risks (not front-gate-disqualifying, but pre-registered
campaign kill-conditions): (1) **recency** — 2024 and 2026-partial negative;
(2) **filter forking-path** — three of five filters were retained after seeing
the ablation, so the configuration must be **precommitted** and re-confirmed on
a clean train/validation/test split; (3) **conditioning narrowness** — the edge
is specific to low-vol quiet-session short-side reversion (defensible, but it
must be precommitted as such, not generalized); (4) the cross-variant
matrix-sanity `LIKELY_SELECTION_NOISE` flag (Phase 4) — applied to the raw
USD_JPY single-pair variant, but a standing caution.

**Phase 6 ranks this `CAMPAIGN_ELIGIBLE (borderline/conditional)` and Phase 7
drafts the single permitted precommit prompt** — which itself opens no campaign
and approves nothing.
