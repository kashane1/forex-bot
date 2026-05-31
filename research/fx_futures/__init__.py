"""FX-futures venue diagnostic — research-only, import-isolated.

Additive futures support for the carry diagnostic
(`research-fx-futures-carry-diagnostic-001`). Builds NO trades, NO entry/exit,
NO PnL ledger, NO approval. Substitutes a free/local CME FX-futures continuous
series for the spot series so the FROZEN carry factor can be re-evaluated under a
futures venue. No first-party trading imports.
"""
