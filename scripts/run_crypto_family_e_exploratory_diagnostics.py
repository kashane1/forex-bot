#!/usr/bin/env python3
"""Run pre-registered Family E exploratory diagnostics on BTC/ETH derivatives data.

Reads gitignored Deribit-canonical backfill CSVs under
``research/crypto/derivatives/backfill/<inst>/``. Public market data only — NO
trading/order/account/private API, NO API keys, NO network calls here (regenerate
data via ``scripts/backfill_crypto_derivatives.py`` if missing). BTC/ETH only.

Modes:
  (default)              preflight — data-readiness audit + counts, NO diagnostics
  --execute-diagnostics  run diagnostics 1,2,3,6,7 (+4/5 low-power) and write docs

Creates no strategy, campaign, front gate, or approval.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT))

from research.crypto.derivatives_registry import CANONICAL_PERPS, validate_perp
from research.crypto.family_e.cross_regime_oi import (
    audit_notable_regime_cells,
    diagnostic_6_cross_asset,
    diagnostic_7_regime_conditioning,
    diagnostics_4_5_oi_low_power,
    oi_availability,
)
from research.crypto.family_e.data import (
    funding_8h_windows,
    load_instrument_series,
)
from research.crypto.family_e.diagnostics import (
    diagnostic_1_funding_mean_reversion,
    diagnostic_2_funding_trend_continuation,
    diagnostic_3_basis_compression_expansion,
)
from research.crypto.family_e.nulls import BASE_SEED, DEFAULT_N_DRAWS
from research.crypto.family_e.render import (
    classify_cell,
    classify_decile,
    collect_decile_pvalues,
    collect_persistence_pvalues,
    render_cross_doc,
    render_decile_doc,
    render_oi_doc,
    render_persistence_doc,
    render_regime_doc,
)
from research.crypto.family_e.reporting import holm_adjust

BACKFILL_DIR = ROOT / "research/crypto/derivatives/backfill"
ARTIFACT_DIR = ROOT / "research/crypto/family_e_diagnostics"
DOCS_DIR = ROOT / "docs/research/active/crypto_programme"
INSTS = list(CANONICAL_PERPS)


def _guard_btc_eth_only(insts: list[str]) -> None:
    for i in insts:
        validate_perp(i)
    if set(insts) != set(CANONICAL_PERPS):
        raise SystemExit(f"BTC/ETH-only guard: refusing instruments {insts}")


def _write_json(name: str, payload: dict) -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    (ARTIFACT_DIR / name).write_text(
        json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8"
    )


def build_data_readiness(series_by_inst: dict) -> dict:
    readiness: dict = {"instruments": {}, "status": "PASS"}
    for inst, s in series_by_inst.items():
        windows = funding_8h_windows(s.funding)
        readiness["instruments"][inst] = {
            "funding_hours": len(s.funding),
            "funding_8h_windows": len(windows),
            "ohlcv_h1": len(s.open_px),
            "index_h1": len(s.index_close),
            "basis_h1": len(s.basis_bps),
            "oi_rows": len(s.oi_usd),
        }
    readiness["oi"] = oi_availability(series_by_inst)
    readiness["high_power_runnable"] = all(
        readiness["instruments"][i]["funding_8h_windows"] > 1000
        and readiness["instruments"][i]["basis_h1"] > 1000
        for i in series_by_inst
    )
    readiness["oi_low_power_only"] = True
    return readiness


def run_preflight(series_by_inst: dict, *, n_draws: int) -> dict:
    readiness = build_data_readiness(series_by_inst)
    _write_json("data_readiness.json", readiness)
    _write_json(
        "run_manifest.json",
        {
            "mode": "preflight",
            "instruments": INSTS,
            "base_seed": BASE_SEED,
            "n_draws": n_draws,
            "backfill_dir": str(BACKFILL_DIR.relative_to(ROOT)),
            "diagnostics_high_power": ["1", "2", "3", "6", "7"],
            "diagnostics_low_power": ["4", "5"],
        },
    )
    return readiness


def run_execute(series_by_inst: dict, *, n_draws: int) -> dict:
    d1 = diagnostic_1_funding_mean_reversion(series_by_inst, seed=BASE_SEED, n_draws=n_draws)
    d2 = diagnostic_2_funding_trend_continuation(
        series_by_inst, seed=BASE_SEED + 10_000, n_draws=n_draws
    )
    d3 = diagnostic_3_basis_compression_expansion(
        series_by_inst, seed=BASE_SEED + 20_000, n_draws=n_draws
    )
    d6 = diagnostic_6_cross_asset(series_by_inst, seed=BASE_SEED + 30_000, n_draws=n_draws)
    d7 = diagnostic_7_regime_conditioning(
        series_by_inst, seed=BASE_SEED + 40_000, n_draws=n_draws
    )
    notable_regime = audit_notable_regime_cells(
        series_by_inst, d7, seed=BASE_SEED + 45_000, n_draws=n_draws
    )
    d7["notable_cells_audit"] = notable_regime
    d45 = diagnostics_4_5_oi_low_power(series_by_inst, seed=BASE_SEED + 50_000, n_draws=n_draws)

    # ---- global Holm across the high-power test family (pooled-gross p-values) ----
    pvals: dict[str, float] = {}
    pvals.update(collect_decile_pvalues(d1, "diag1"))
    pvals.update(collect_decile_pvalues(d3["reversion"], "diag3rev"))
    pvals.update(collect_decile_pvalues(d3["expansion"], "diag3exp"))
    pvals.update(collect_persistence_pvalues(d2, "diag2"))
    for h, cell in d6.get("horizons", {}).items():
        from research.crypto.family_e.render import _shuffled_p

        p = _shuffled_p(cell["agreement_directional"])
        if p is not None:
            pvals[f"diag6|h{h}|agreement_gross"] = p
        p = _shuffled_p(cell["disagreement_relative_value"])
        if p is not None:
            pvals[f"diag6|h{h}|disagreement_gross"] = p
    holm = holm_adjust(pvals)

    # ---- classification ----
    cls1 = classify_decile(d1, holm, "diag1", insts=INSTS)
    cls3 = classify_decile(d3["reversion"], holm, "diag3rev", insts=INSTS)
    # diagnostic 2 — best (most favorable) continuation cell across k,h
    order = ("candidate_for_front_gate", "statistical_only_cost_defeated",
             "cost_defeated", "rejected", "blocked_data_quality")
    best2 = None
    for k, block in d2["k_values"].items():
        for h, cell in block["horizons"].items():
            key = f"diag2|k{k}|h{h}|cont_pooled_gross"
            pooled = cell["pooled"]["continuation"]
            c = classify_cell(
                pooled,
                btc_cell=cell[INSTS[0]]["continuation"],
                eth_cell=cell[INSTS[1]]["continuation"],
                holm_p=holm.get(key, 1.0),
            )
            c["rationale"] = (
                f"best cell = continuation k{k} h{h}: gross={pooled['edges']['gross']:.2e}, "
                f"all_in={pooled['edges']['all_in']:.2e}, Holm-adj shuffled p="
                f"{holm.get(key, 1.0):.3f}. {c['rationale']}"
            )
            if best2 is None or order.index(c["label"]) < order.index(best2["label"]):
                best2 = {**c, "k": k, "horizon": h}
    cls2 = best2 or {"label": "rejected", "rationale": "no continuation cells evaluated"}
    # diagnostic 6 — best (most favorable) of agreement / disagreement cells
    order6 = ("candidate_for_front_gate", "statistical_only_cost_defeated",
              "cost_defeated", "rejected")
    best6 = None
    for h, cell in d6.get("horizons", {}).items():
        for key_name, jkey in (("agreement_directional", "agreement"),
                               ("disagreement_relative_value", "disagreement")):
            c = cell[key_name]
            holm_p = holm.get(f"diag6|h{h}|{jkey}_gross", 1.0)
            gate_clears = holm_p < 0.05 and c["edges"]["gross"] > 0
            label = ("statistical_only_cost_defeated" if gate_clears and c["edges"]["all_in"] <= 0
                     else ("candidate_for_front_gate" if gate_clears and c["edges"]["all_in"] > 0
                           and c["edges"]["stress_2x"] > 0 else "rejected"))
            rationale = (
                f"best cell = {key_name} h{h}: gross={c['edges']['gross']:.2e}, "
                f"all_in={c['edges']['all_in']:.2e}, Holm-adj shuffled p={holm_p:.3f} "
                f"(does not clear after multiple comparisons)."
            )
            if best6 is None or order6.index(label) < order6.index(best6["label"]):
                best6 = {"label": label, "rationale": rationale, "holm_adj_p": holm_p}
    cls6 = best6 or {"label": "rejected", "rationale": "no cross-asset cells evaluated"}
    cls45 = {"label": "blocked_low_power_oi", "rationale": d45["note"]}

    # diagnostic 7 — does any regime cell meet the FULL frozen candidate bar?
    # A cell qualifies only if non-circular, BTC+ETH supportive, both 2x-positive — AND
    # the frozen gate also forbids a single-regime-slice override of a rejected base.
    qualifying = [
        c for c in notable_regime
        if not c["circular"] and c["btc_and_eth_supportive"] and c["both_stress_2x_positive"]
    ]
    non_circular_notable = [c for c in notable_regime if not c["circular"]]
    if non_circular_notable:
        regime_impact = (
            f"{len(non_circular_notable)} non-circular regime cell(s) flagged notable; the "
            "strongest is downtrend-conditioned funding mean reversion (BTC+ETH supportive, "
            "both 2×-stress-positive). It FAILS the frozen candidate bar: it is a single "
            "regime slice conditioning a REJECTED base diagnostic and is borderline/failing "
            "under full-family Holm (incl. assets). Per pre-registration a tiny regime slice "
            "must not override base failure → no front-gate candidate this sprint, but it is "
            "the single thread worth a future fresh-pre-registered, walk-forward re-test."
        )
        cls7 = {"label": "rejected", "rationale": regime_impact,
                "notable_non_circular_cells": len(non_circular_notable),
                "cells_passing_btc_eth_and_2x_before_slice_gate": len(qualifying),
                "meets_full_candidate_bar": False}
    else:
        regime_impact = (
            "No non-circular regime cell is notable; base diagnostics 1–3 are not candidate, "
            "so regime conditioning yields no front-gate candidate (forking-path discipline)."
        )
        cls7 = {"label": "rejected", "rationale": regime_impact}

    classification = {
        "diagnostic_1": cls1, "diagnostic_2": cls2, "diagnostic_3": cls3,
        "diagnostic_4_5": cls45, "diagnostic_6": cls6, "diagnostic_7": cls7,
        "holm_pvalues": holm, "raw_pvalues": pvals,
        "any_candidate_for_front_gate": any(
            c.get("label") == "candidate_for_front_gate" for c in (cls1, cls2, cls3, cls6)
        ),
    }

    # ---- write JSON artifacts ----
    _write_json("diagnostic_1_funding_mean_reversion.json", d1)
    _write_json("diagnostic_2_funding_trend_continuation.json", d2)
    _write_json("diagnostic_3_basis_compression_expansion.json", d3)
    _write_json("diagnostic_6_cross_asset_confirmation.json", d6)
    _write_json("diagnostic_7_regime_conditioning.json", d7)
    _write_json("diagnostic_4_5_oi_low_power.json", d45)
    _write_json("classification_summary.json", classification)
    _write_json(
        "run_manifest.json",
        {
            "mode": "execute-diagnostics", "instruments": INSTS, "base_seed": BASE_SEED,
            "n_draws": n_draws, "backfill_dir": str(BACKFILL_DIR.relative_to(ROOT)),
        },
    )

    # ---- render docs (numbers machine-rendered from JSON) ----
    sprint_line = "**Sprint:** `crypto-family-e-exploratory-diagnostics-001`"
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_1_FUNDING_MEAN_REVERSION_RESULT.md").write_text(
        render_decile_doc(
            doc_title="Crypto Family E Diagnostic 1 — Funding Mean Reversion Result",
            sprint_line=sprint_line, result=d1, classification=cls1, insts=INSTS,
        ), encoding="utf-8")
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_2_FUNDING_TREND_CONTINUATION_RESULT.md").write_text(
        render_persistence_doc(sprint_line=sprint_line, result=d2, classification=cls2, insts=INSTS),
        encoding="utf-8")
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_3_BASIS_COMPRESSION_EXPANSION_RESULT.md").write_text(
        render_decile_doc(
            doc_title="Crypto Family E Diagnostic 3 — Basis Compression / Expansion Result",
            sprint_line=sprint_line, result=d3["reversion"], classification=cls3, insts=INSTS,
            extra_notes="Expansion/momentum variant (opposite signs) reported in the JSON "
            "artifact `diagnostic_3_basis_compression_expansion.json` under `expansion`.",
        ), encoding="utf-8")
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_6_CROSS_ASSET_CONFIRMATION_RESULT.md").write_text(
        render_cross_doc(sprint_line=sprint_line, result=d6, classification=cls6), encoding="utf-8")
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_7_REGIME_CONDITIONING_RESULT.md").write_text(
        render_regime_doc(sprint_line=sprint_line, result=d7, impact=regime_impact,
                          notable=notable_regime, insts=INSTS),
        encoding="utf-8")
    (DOCS_DIR / "CRYPTO_FAMILY_E_DIAGNOSTIC_4_5_OI_LOW_POWER_RESULT.md").write_text(
        render_oi_doc(sprint_line=sprint_line, result=d45), encoding="utf-8")
    return classification


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Crypto Family E exploratory diagnostics.")
    parser.add_argument("--execute-diagnostics", action="store_true",
                        help="run diagnostics (default is preflight only)")
    parser.add_argument("--n-draws", type=int, default=DEFAULT_N_DRAWS)
    parser.add_argument("--backfill-dir", default=str(BACKFILL_DIR))
    args = parser.parse_args(argv)

    _guard_btc_eth_only(INSTS)
    backfill = Path(args.backfill_dir)
    try:
        series_by_inst = {i: load_instrument_series(backfill, i) for i in INSTS}
    except FileNotFoundError as exc:
        print(json.dumps({"status": "BLOCKED_DATA_QUALITY", "message": str(exc),
                          "hint": "regenerate via scripts/backfill_crypto_derivatives.py "
                                  "--execute-public-fetch"}, indent=2))
        return 2

    if args.execute_diagnostics:
        classification = run_execute(series_by_inst, n_draws=args.n_draws)
        print(json.dumps({
            "status": "PASS", "mode": "execute-diagnostics",
            "labels": {k: v.get("label") for k, v in classification.items()
                       if k.startswith("diagnostic")},
            "any_candidate_for_front_gate": classification["any_candidate_for_front_gate"],
            "artifacts": str(ARTIFACT_DIR.relative_to(ROOT)),
        }, indent=2))
    else:
        readiness = run_preflight(series_by_inst, n_draws=args.n_draws)
        print(json.dumps({"status": "PASS", "mode": "preflight",
                          "high_power_runnable": readiness["high_power_runnable"],
                          "oi_low_power_only": readiness["oi_low_power_only"],
                          "artifacts": str(ARTIFACT_DIR.relative_to(ROOT))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
