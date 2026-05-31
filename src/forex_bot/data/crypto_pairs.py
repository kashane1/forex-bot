"""Crypto instruments accepted by shared Postgres research store helpers."""

from __future__ import annotations

CRYPTO_INSTRUMENTS: tuple[str, ...] = ("BTC_USD", "ETH_USD")

CRYPTO_MATERIALIZED_FROM_M1: tuple[str, ...] = ("M5", "M15", "H1", "H4", "D1")
