# Next Prompt — After Cross Relative-Value Factor Validation

The S4 cross relative-value factor-validation study is complete. Verdict:
**`FACTOR_REAL_BUT_WEAK`** — triangular no-arbitrage RV structure **genuinely
exists** and its deviations revert (overwhelmingly null-separated: 20/20 cells,
beats the conservative wrong-triangle null; stable across all 8 relationships, 6
years, 5 sessions), but the reversion is **confined to the no-arb/microstructure
band** (~0.5 bp vs ~5 bp cost band; front-loaded; 4/8 half-life ≤1 bar). It is the
programme's **first non-rejected factor** — real, yet too small (within-band) for a
front-gate screen.

## The shortlist is now fully resolved

| Family | Verdict |
|---|---|
| S1 — C1 replication on crosses | REPLICATION_FAILED (USD artifact) |
| S2 — currency-strength index | FACTOR_REJECTED (real descriptor, non-predictive) |
| S3 — cross-sectional momentum | pre-falsified by S2 |
| **S4 — cross relative-value** | **FACTOR_REAL_BUT_WEAK** (real, within cost band) |
| S5 — regime gate | moot (no surviving generator) |

The **no-new-data cross factor-discovery shortlist (S1–S5) is exhausted.** One real
factor was found (S4); it is sub-cost-band on this corpus. **Do NOT build a
front-gate screen for S4** — its existence study already shows it is ~10× inside the
cost band; a screen would simply re-hit C028's two-/three-leg cost wall. That is not
a re-tune worth running.

## Recommended next sprint — project-level direction synthesis (docs-only)

> Branch: `research-cross-factor-programme-synthesis-001`
>
> **A project-level synthesis and direction decision** after the S1–S5 shortlist
> exhaustion — exactly the checkpoint the corpus-viability review was for the
> majors. Docs-only. No factor, no screen, no campaign, no strategy, no approval.
>
> The sprint must:
> 1. **Synthesize the cross-data programme** (data population → planning → S1 C1
>    replication → S2 currency strength → S4 cross RV): what the 8-cross expansion
>    did and did not deliver. Headline: breadth was real (S2 broke the USD-artifact
>    suspicion; S4 found genuine no-arb RV structure) but **every effect is null,
>    cost-defeated, or sub-cost-band** — the venue's structural cost-defeat now holds
>    even where genuine structure exists.
> 2. **Weigh the remaining levers** against that evidence, each as a *future*
>    direction (not executed here):
>    - **(a) Financing-data ingest for carry** — the **one untested mechanism** (a
>      different return source: interest-rate differential, not spread/reversion).
>      Prerequisite = a **data sprint** to ingest real OANDA swap/financing rates for
>      AUD_JPY/NZD_JPY/EUR_JPY; carry cannot be honestly tested on the registry's
>      *estimate* rates (that repeats C031). **Recommended as the most concrete next
>      step** if the programme continues on this venue.
>    - **(b) Lower-cost venue / true tick-L2 data** — S4 proved real RV structure
>      exists but is sub-*retail*-cost-band; it is the kind of effect that lives at
>      institutional cost structures. Revisiting it needs a different cost/data
>      regime (a venue/data lift), per the standing corpus-reopen conditions.
>    - **(c) Conclude the no-new-data search** — declare the OANDA spot-FX corpus
>      (majors + crosses, 5y, M5, retail spreads) exhausted for no-new-data factor
>      discovery, keeping it as a control/baseline.
> 3. **Choose one** direction and write its next prompt. If (a), the follow-on is a
>    **data-ingest sprint** (not a factor screen). No campaign in any branch.
>
> Deliverable: a synthesis doc + a direction decision + a next prompt. No code, no
> screen, no campaign.

## Guardrails carried into the next sprint

- **No campaign of any number.**
- **Do not front-gate S4** (sub-cost-band; out of scope; would re-hit the cost wall).
- **Do not run S3** (pre-falsified). **Do not revive** C1 or the naive C028 RV.
- **Carry stays prerequisite-blocked** on a real financing-data ingest (a data
  sprint, never a factor screen on estimate rates).
- No strategy approved; `approved: []`; paper/demo/live blocked; `forex_bot.approval`
  fails closed.
- Read-only research-DB access is acceptable (no trading APIs, no broker creds).
- Freeze stays intact; evidence + a decision, nothing order-capable.

## Why a synthesis, not another factor screen

S1–S5 are resolved; the corpus produced exactly one real factor and it is
sub-cost-band. Continuing to mine the same M5 mids for a *different* no-new-data
directional/reversion factor would be variant-hunting against a freeze. The
high-value moves now are a **different return source** (carry → needs data) or a
**different cost/data regime** (venue/tick → a lift) — both decisions that deserve a
deliberate project-level synthesis rather than a reflexive next screen.
