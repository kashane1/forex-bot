"""Realistic shapes of OANDA v20 JSON responses. Not real account data."""

from __future__ import annotations

ACCOUNT_SUMMARY = {
    "account": {
        "id": "001-001-1234567-001",
        "currency": "USD",
        "balance": "500.0000",
        "NAV": "498.4500",
        "marginUsed": "12.5000",
        "marginAvailable": "485.9500",
        "marginCloseoutPercent": "0.02573",
        "unrealizedPL": "-1.5500",
        "pl": "-1.5500",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "pendingOrderCount": 0,
        "lastTransactionID": "42",
        "createdTime": "2024-01-01T00:00:00Z",
    },
    "lastTransactionID": "42",
}

INSTRUMENTS_LIST = {
    "instruments": [
        {
            "name": "EUR_USD",
            "type": "CURRENCY",
            "displayName": "EUR/USD",
            "pipLocation": -4,
            "displayPrecision": 5,
            "tradeUnitsPrecision": 0,
            "minimumTradeSize": "1",
            "maximumOrderUnits": "100000000",
            "marginRate": "0.02",
            "minimumTrailingStopDistance": "0.00050",
            "maximumTrailingStopDistance": "1.00000",
        },
        {
            "name": "USD_JPY",
            "type": "CURRENCY",
            "displayName": "USD/JPY",
            "pipLocation": -2,
            "displayPrecision": 3,
            "tradeUnitsPrecision": 0,
            "minimumTradeSize": "1",
            "maximumOrderUnits": "100000000",
            "marginRate": "0.04",
        },
    ]
}

CANDLES_RESPONSE = {
    "instrument": "EUR_USD",
    "granularity": "H4",
    "candles": [
        {
            "complete": True,
            "volume": 1234,
            "time": "2026-05-20T20:00:00.000000000Z",
            "bid": {"o": "1.0795", "h": "1.0810", "l": "1.0790", "c": "1.0805"},
            "ask": {"o": "1.0797", "h": "1.0812", "l": "1.0792", "c": "1.0807"},
        },
        {
            "complete": False,
            "volume": 200,
            "time": "2026-05-21T00:00:00.000000000Z",
            "bid": {"o": "1.0805", "h": "1.0809", "l": "1.0803", "c": "1.0808"},
            "ask": {"o": "1.0807", "h": "1.0811", "l": "1.0805", "c": "1.0810"},
        },
    ],
}

PRICING_RESPONSE = {
    "prices": [
        {
            "type": "PRICE",
            "instrument": "EUR_USD",
            "time": "2026-05-21T12:00:00.000000000Z",
            "tradeable": True,
            "status": "tradeable",
            "bids": [{"price": "1.07990", "liquidity": 10000000}],
            "asks": [{"price": "1.08010", "liquidity": 10000000}],
            "closeoutBid": "1.07985",
            "closeoutAsk": "1.08015",
        }
    ]
}

ORDER_FILL_RESPONSE = {
    "orderCreateTransaction": {
        "id": "100",
        "type": "MARKET_ORDER",
        "instrument": "EUR_USD",
        "units": "100",
        "stopLossOnFill": {"price": "1.07810"},
    },
    "orderFillTransaction": {
        "id": "101",
        "type": "ORDER_FILL",
        "orderID": "100",
        "instrument": "EUR_USD",
        "units": "100",
        "price": "1.08015",
        "tradeOpened": {"tradeID": "200", "units": "100"},
    },
    "lastTransactionID": "101",
}

ORDER_REJECT_RESPONSE = {
    "orderRejectTransaction": {
        "id": "102",
        "type": "MARKET_ORDER_REJECT",
        "instrument": "EUR_USD",
        "rejectReason": "MARKET_HALTED",
    },
    "lastTransactionID": "102",
}

OPEN_TRADES_RESPONSE = {
    "trades": [
        {
            "id": "200",
            "instrument": "EUR_USD",
            "price": "1.08015",
            "openTime": "2026-05-21T12:00:00.000000000Z",
            "initialUnits": "100",
            "currentUnits": "100",
            "state": "OPEN",
            "stopLossOrder": {"id": "201"},
        }
    ],
    "lastTransactionID": "201",
}

OPEN_POSITIONS_RESPONSE = {
    "positions": [
        {
            "instrument": "EUR_USD",
            "long": {"units": "100", "averagePrice": "1.08015"},
            "short": {"units": "0"},
            "unrealizedPL": "0.50",
        }
    ],
    "lastTransactionID": "201",
}

OPEN_ORDERS_EMPTY = {"orders": []}

TRANSACTIONS_SINCEID_RESPONSE = {
    "transactions": [
        {
            "id": "42",
            "type": "MARKET_ORDER",
            "accountID": "001-001-1234567-001",
            "time": "2026-05-21T11:55:00.000000000Z",
            "instrument": "EUR_USD",
            "units": "100",
            "price": "1.08000",
        },
        {
            "id": "43",
            "type": "ORDER_FILL",
            "accountID": "001-001-1234567-001",
            "time": "2026-05-21T11:55:01.000000000Z",
            "instrument": "EUR_USD",
            "units": "100",
            "price": "1.08015",
            "pl": "0",
        },
    ],
    "lastTransactionID": "43",
}

# A DAILY_FINANCING transaction with a per-instrument / per-trade
# breakdown. Mixed signs: EUR_USD and GBP_USD are debits, USD_JPY a
# credit. GBP_USD has no openTradeFinancings (position-level only).
DAILY_FINANCING_TRANSACTION = {
    "id": "512",
    "type": "DAILY_FINANCING",
    "accountID": "001-001-1234567-001",
    "time": "2024-03-04T22:00:00.000000000Z",
    "financing": "-0.8234",
    "accountBalance": "499.1766",
    "positionFinancings": [
        {
            "instrument": "EUR_USD",
            "financing": "-0.5123",
            "openTradeFinancings": [
                {"tradeID": "200", "financing": "-0.3000"},
                {"tradeID": "205", "financing": "-0.2123"},
            ],
        },
        {
            "instrument": "USD_JPY",
            "financing": "0.3111",
            "openTradeFinancings": [{"tradeID": "210", "financing": "0.3111"}],
        },
        {"instrument": "GBP_USD", "financing": "-0.6222"},
    ],
}

# A DAILY_FINANCING transaction with no per-position breakdown — only the
# account-level total is available.
DAILY_FINANCING_NO_BREAKDOWN = {
    "id": "513",
    "type": "DAILY_FINANCING",
    "accountID": "001-001-1234567-001",
    "time": "2024-03-05T22:00:00.000000000Z",
    "financing": "-0.4500",
    "accountBalance": "498.7266",
}

# An ORDER_FILL that realized financing when it closed a trade.
ORDER_FILL_WITH_FINANCING = {
    "id": "514",
    "type": "ORDER_FILL",
    "accountID": "001-001-1234567-001",
    "time": "2024-03-06T14:00:00.000000000Z",
    "instrument": "EUR_USD",
    "units": "-100",
    "price": "1.08550",
    "pl": "1.2000",
    "financing": "-0.1850",
    "tradesClosed": [{"tradeID": "200", "units": "-100"}],
}

ACCOUNT_DETAILS_RESPONSE = {
    "account": {
        "id": "001-001-1234567-001",
        "currency": "USD",
        "balance": "500.0000",
        "NAV": "500.5000",
        "marginUsed": "12.5000",
        "marginAvailable": "488.0000",
        "marginCloseoutPercent": "0.025",
        "unrealizedPL": "0.5000",
        "pl": "0.0000",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "pendingOrderCount": 0,
        "lastTransactionID": "201",
        "createdTime": "2024-01-01T00:00:00Z",
        "trades": [{"id": "200", "instrument": "EUR_USD"}],
        "orders": [],
        "positions": [
            {
                "instrument": "EUR_USD",
                "long": {"units": "100"},
                "short": {"units": "0"},
            }
        ],
    },
    "lastTransactionID": "201",
}
