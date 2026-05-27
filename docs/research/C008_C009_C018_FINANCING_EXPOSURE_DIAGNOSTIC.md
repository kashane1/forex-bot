# C008 / C009 / C018 Financing Exposure Diagnostic

**Date:** 2026-05-27  
**Branch:** `research-financing-modeled-pnl-and-carry-readiness-001`  
**Label:** `SYNTHETIC_FINANCING_DIAGNOSTIC`  
**Machine-readable:** [`research/financing/c008_c009_c018_financing_exposure.json`](../../research/financing/c008_c009_c018_financing_exposure.json)

> **Not verdict-changing.** Conservative stress rates only. No observed broker financing. C008/C009/C018 verdicts unchanged.

---

## 1. Method

- Source: existing deduped forensic trade CSVs (local `backtests/`, gitignored)
- Rate source: `default_stress_rate_source()` — conservative bp/day, debit-on-both-sides
- Tool: `scripts/generate_c008_c009_c018_financing_exposure.py` → `apply_financing_overlay`
- R adjustment: `net_r = gross_r + financing_r` where `financing_r = cashflow_stress_usd / risk_usd`

---

## 2. Aggregate expectancy (gross vs synthetic-net)

| campaign | split | trades | gross exp R | net exp R | financing drag R | avg rollovers |
|---|---|---:|---:|---:|---:|---:|
| C008 | train | 216 | −0.025 | **−0.105** | −0.080 | ~4.2 |
| C008 | validation | 138 | +0.161 | **+0.069** | −0.092 | ~4.5 |
| C009 | train | 252 | −0.025 | **−0.060** | −0.034 | ~3.8 |
| C009 | validation | 151 | +0.186 | **+0.140** | −0.046 | ~3.9 |
| C018 | train | 236 | −0.119 | **−0.172** | −0.054 | ~4.0 |
| C018 | validation | 142 | +0.194 | **+0.129** | −0.065 | ~4.1 |

---

## 3. Key findings

1. **Multi-day H4 holds carry meaningful financing drag** — typically **0.05–0.09 R per trade** under conservative stress.
2. **Validation uplift is partially carry-inflated.** C008 validation drops from +0.161 R gross to +0.069 R net (−57% reduction). C018 validation drops from +0.194 R to +0.129 R (−33%).
3. **C018 vs C008 validation net:** C018 net +0.129 R vs C008 net +0.069 R — protective-stop uplift survives financing stress but margin narrows.
4. **Train failures worsen under financing.** C018 train −0.119 R gross → −0.172 R net; train gate failure is **not** explained away by financing.
5. **C009 midline target exits had shorter effective holds** — lower drag (−0.046 R val) vs C008/C018 (~−0.065 to −0.092 R).

---

## 4. Validation uplift concentration

Financing drag is **uniformly negative** on all pairs under stress (debit-on-both-sides). Validation uplift is **not** concentrated in financing-hostile pairs alone — the gross-to-net reduction is broad-based across the six-pair universe. Side-specific carry asymmetry **cannot** be assessed until observed long/short rates exist.

---

## 5. Verdict impact

**None.** This diagnostic uses synthetic conservative stress only. C008 REJECT, C009 REJECT, C018 REJECT stand.

---

## 6. Command

```bash
python scripts/generate_c008_c009_c018_financing_exposure.py
```

Requires local trade CSVs under `backtests/CAMPAIGN_008_*`, `CAMPAIGN_009_*`, `CAMPAIGN_018_*`.
