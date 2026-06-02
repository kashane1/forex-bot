"""Family E exploratory diagnostics on BTC/ETH perpetual derivatives data.

Reusable, lookahead-free helpers for funding / basis / OI diagnostics. Reads the
gitignored Deribit-canonical backfill CSVs. No execution, sizing, walk-forward,
or strategy logic lives here — these are exploratory return statistics only.

See CRYPTO_FAMILY_E_EXPLORATORY_RUN_SPEC_001.md for the frozen pre-registration.
"""
