"""OANDA v20 REST client implementing the Broker Protocol.

Endpoint reference: https://developer.oanda.com/rest-live-v20/
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from decimal import Decimal
from typing import Any

import httpx

from forex_bot.broker.base import BrokerEnvironment
from forex_bot.broker.errors import (
    BrokerAuthError,
    BrokerInvalidAccountError,
    BrokerOrderRejectError,
    BrokerRateLimitError,
    BrokerServerError,
    BrokerUnknownStatusError,
)
from forex_bot.broker.mapping import (
    is_heartbeat,
    map_account_details,
    map_account_snapshot,
    map_broker_order,
    map_candle,
    map_heartbeat,
    map_instrument,
    map_position,
    map_price,
    map_trade,
    map_transaction,
)
from forex_bot.domain.account import AccountDetails, AccountSnapshot
from forex_bot.domain.candles import Candle, CandleRequest
from forex_bot.domain.instruments import Instrument
from forex_bot.domain.market import Quote
from forex_bot.domain.orders import BrokerOrder, BrokerOrderResult, OrderPlan
from forex_bot.domain.positions import Position, Trade
from forex_bot.domain.transactions import Heartbeat, Transaction
from forex_bot.logging_config import get_logger

logger = get_logger(__name__)

REST_HOSTS: dict[BrokerEnvironment, str] = {
    "practice": "https://api-fxpractice.oanda.com",
    "live": "https://api-fxtrade.oanda.com",
}
STREAM_HOSTS: dict[BrokerEnvironment, str] = {
    "practice": "https://stream-fxpractice.oanda.com",
    "live": "https://stream-fxtrade.oanda.com",
}


class OandaBroker:
    def __init__(
        self,
        *,
        environment: BrokerEnvironment,
        account_id: str,
        access_token: str,
        timeout_seconds: float = 10.0,
        max_retries: int = 3,
        client: httpx.Client | None = None,
    ) -> None:
        if not access_token:
            raise BrokerAuthError("missing OANDA access token")
        if not account_id:
            raise BrokerInvalidAccountError("missing OANDA account id")
        self.environment: BrokerEnvironment = environment
        self.account_id = account_id
        self._token = access_token
        self._max_retries = max_retries
        self._client = client or httpx.Client(
            base_url=REST_HOSTS[environment],
            timeout=timeout_seconds,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept-Datetime-Format": "RFC3339",
                "Content-Type": "application/json",
            },
        )
        self._stream_client: httpx.Client | None = None

    def close(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass
        if self._stream_client is not None:
            try:
                self._stream_client.close()
            except Exception:
                pass

    # ---------- helpers ----------

    def _account_path(self, tail: str) -> str:
        return f"/v3/accounts/{self.account_id}{tail}"

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        try:
            response = self._client.request(method, path, **kwargs)
        except httpx.TimeoutException as exc:
            if method.upper() == "POST":
                raise BrokerUnknownStatusError(f"timeout on {method} {path}") from exc
            raise BrokerServerError(f"timeout on {method} {path}") from exc
        except httpx.HTTPError as exc:
            raise BrokerServerError(f"http error on {method} {path}: {exc}") from exc

        if response.status_code in {401, 403}:
            raise BrokerAuthError(f"auth failed {response.status_code}: {response.text[:200]}")
        if response.status_code == 404:
            raise BrokerInvalidAccountError(
                f"not found {response.status_code}: {response.text[:200]}"
            )
        if response.status_code == 429:
            raise BrokerRateLimitError(f"rate limited: {response.text[:200]}")
        if response.status_code >= 500:
            raise BrokerServerError(f"server {response.status_code}: {response.text[:200]}")
        if response.status_code >= 400:
            body = response.text[:500]
            code = None
            try:
                payload = response.json()
                code = payload.get("errorCode")
            except Exception:
                payload = {}
            raise BrokerOrderRejectError(f"{response.status_code}: {body}", code=code)

        if not response.content:
            return {}
        return response.json()

    # ---------- account ----------

    def get_account_summary(self) -> AccountSnapshot:
        payload = self._request("GET", self._account_path("/summary"))
        return map_account_snapshot(payload)

    def get_account_details(self) -> AccountDetails:
        payload = self._request("GET", self._account_path(""))
        return map_account_details(payload)

    def list_instruments(self) -> list[Instrument]:
        payload = self._request("GET", self._account_path("/instruments"))
        return [map_instrument(item) for item in payload.get("instruments", [])]

    # ---------- market data ----------

    def _candle_params(self, request: CandleRequest) -> dict[str, Any]:
        params: dict[str, Any] = {
            "granularity": request.granularity,
            "price": request.price,
            "dailyAlignment": request.daily_alignment,
            "alignmentTimezone": request.alignment_timezone,
            "weeklyAlignment": request.weekly_alignment,
            "includeFirst": "true" if request.include_first else "false",
        }
        if request.count is not None:
            params["count"] = request.count
        if request.from_time is not None:
            params["from"] = request.from_time.isoformat().replace("+00:00", "Z")
        if request.to_time is not None:
            params["to"] = request.to_time.isoformat().replace("+00:00", "Z")
        return params

    def get_candles(self, request: CandleRequest) -> list[Candle]:
        payload = self._request(
            "GET",
            self._account_path(f"/instruments/{request.instrument}/candles"),
            params=self._candle_params(request),
        )
        candles = [
            map_candle(request.instrument, request.granularity, item)
            for item in payload.get("candles", [])
        ]
        return candles

    def get_candles_with_raw(self, request: CandleRequest) -> tuple[list[Candle], bytes]:
        """Same as get_candles but also returns raw response bytes so callers
        can compute a data-provenance hash. Bypasses _request() so that we
        get the original byte stream OANDA sent, not pydantic's re-encoding.
        """
        path = self._account_path(f"/instruments/{request.instrument}/candles")
        try:
            response = self._client.request("GET", path, params=self._candle_params(request))
        except httpx.TimeoutException as exc:
            raise BrokerServerError(f"timeout on GET {path}") from exc
        except httpx.HTTPError as exc:
            raise BrokerServerError(f"http error on GET {path}: {exc}") from exc

        if response.status_code in {401, 403}:
            raise BrokerAuthError(f"auth failed {response.status_code}")
        if response.status_code == 404:
            raise BrokerInvalidAccountError(
                f"not found {response.status_code}: {response.text[:200]}"
            )
        if response.status_code == 429:
            raise BrokerRateLimitError(f"rate limited: {response.text[:200]}")
        if response.status_code >= 500:
            raise BrokerServerError(f"server {response.status_code}: {response.text[:200]}")
        if response.status_code >= 400:
            raise BrokerOrderRejectError(f"{response.status_code}: {response.text[:500]}")

        raw = response.content
        payload = response.json() if raw else {}
        candles = [
            map_candle(request.instrument, request.granularity, item)
            for item in payload.get("candles", [])
        ]
        return candles, raw

    def get_prices(self, instruments: list[str]) -> list[Quote]:
        if not instruments:
            return []
        payload = self._request(
            "GET",
            self._account_path("/pricing"),
            params={"instruments": ",".join(instruments)},
        )
        return [map_price(p) for p in payload.get("prices", [])]

    def stream_prices(self, instruments: list[str]) -> Iterator[Quote | Heartbeat]:
        if not instruments:
            return iter(())
        url = f"{STREAM_HOSTS[self.environment]}/v3/accounts/{self.account_id}/pricing/stream"
        params = {"instruments": ",".join(instruments)}
        return self._line_stream(url, params, _parse_price_stream_line)

    # ---------- trades / orders / positions ----------

    def list_open_orders(self) -> list[BrokerOrder]:
        payload = self._request("GET", self._account_path("/openOrders"))
        return [map_broker_order(item) for item in payload.get("orders", [])]

    def list_open_trades(self) -> list[Trade]:
        payload = self._request("GET", self._account_path("/openTrades"))
        return [map_trade(item) for item in payload.get("trades", [])]

    def list_positions(self) -> list[Position]:
        payload = self._request("GET", self._account_path("/openPositions"))
        return [map_position(item) for item in payload.get("positions", [])]

    def submit_order(self, plan: OrderPlan) -> BrokerOrderResult:
        if self.environment == "live":
            # Defense in depth. The executor is supposed to gate this, but we
            # refuse here too if the executor was misconfigured.
            from forex_bot.config import ConfigError  # local to avoid cycle

            raise ConfigError(
                "OandaBroker.submit_order called against live environment. "
                "Live execution requires explicit config gates."
            )
        body = _build_market_order_body(plan)
        try:
            payload = self._request(
                "POST", self._account_path("/orders"), content=json.dumps(body)
            )
        except BrokerOrderRejectError as exc:
            return BrokerOrderResult(
                status="REJECTED",
                client_order_id=plan.client_order_id,
                error_code=exc.code,
                error_message=str(exc),
                raw={},
            )
        except BrokerUnknownStatusError as exc:
            return BrokerOrderResult(
                status="UNKNOWN",
                client_order_id=plan.client_order_id,
                error_message=str(exc),
                raw={},
            )
        return _build_order_result(payload, plan)

    def close_trade(self, trade_id: str, units: Decimal | None = None) -> BrokerOrderResult:
        body: dict[str, Any] = {"units": "ALL" if units is None else str(units)}
        try:
            payload = self._request(
                "PUT",
                self._account_path(f"/trades/{trade_id}/close"),
                content=json.dumps(body),
            )
        except BrokerOrderRejectError as exc:
            return BrokerOrderResult(
                status="REJECTED",
                error_code=exc.code,
                error_message=str(exc),
                raw={},
            )
        except BrokerUnknownStatusError as exc:
            return BrokerOrderResult(status="UNKNOWN", error_message=str(exc), raw={})
        return _build_order_result(payload, plan=None)

    # ---------- transactions ----------

    def get_transactions_since(self, last_transaction_id: str) -> list[Transaction]:
        payload = self._request(
            "GET",
            self._account_path("/transactions/sinceid"),
            params={"id": last_transaction_id},
        )
        return [map_transaction(item) for item in payload.get("transactions", [])]

    def stream_transactions(self) -> Iterator[Transaction | Heartbeat]:
        url = f"{STREAM_HOSTS[self.environment]}/v3/accounts/{self.account_id}/transactions/stream"
        return self._line_stream(url, params=None, line_parser=_parse_transaction_stream_line)

    # ---------- streaming primitive ----------

    def _line_stream(
        self,
        url: str,
        params: dict[str, Any] | None,
        line_parser: Any,
    ) -> Iterator[Quote | Heartbeat | Transaction]:
        if self._stream_client is None:
            self._stream_client = httpx.Client(
                timeout=httpx.Timeout(connect=10.0, read=None, write=10.0, pool=10.0),
                headers={
                    "Authorization": f"Bearer {self._token}",
                    "Accept-Datetime-Format": "RFC3339",
                },
            )
        with self._stream_client.stream("GET", url, params=params) as response:
            if response.status_code in {401, 403}:
                raise BrokerAuthError("stream auth failed")
            if response.status_code >= 400:
                raise BrokerServerError(f"stream {response.status_code}: {response.text[:200]}")
            for line in response.iter_lines():
                if not line:
                    continue
                event = line_parser(line)
                if event is not None:
                    yield event


def _parse_price_stream_line(line: str) -> Quote | Heartbeat | None:
    payload = json.loads(line)
    if is_heartbeat(payload):
        return map_heartbeat(payload)
    if payload.get("type") == "PRICE":
        return map_price(payload)
    return None


def _parse_transaction_stream_line(line: str) -> Transaction | Heartbeat | None:
    payload = json.loads(line)
    if is_heartbeat(payload):
        return map_heartbeat(payload)
    return map_transaction(payload)


def _build_market_order_body(plan: OrderPlan) -> dict[str, Any]:
    units = plan.units if plan.side == "buy" else -plan.units
    body: dict[str, Any] = {
        "order": {
            "type": "MARKET",
            "instrument": plan.instrument,
            "units": str(units),
            "timeInForce": "FOK",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {
                "price": str(plan.stop_loss_price),
                "timeInForce": "GTC",
            },
            "clientExtensions": {
                "id": plan.client_order_id,
                "tag": f"{plan.strategy_name}:{plan.strategy_version}",
                "comment": f"config_hash={plan.config_hash}",
            },
        }
    }
    if plan.take_profit_price is not None:
        body["order"]["takeProfitOnFill"] = {
            "price": str(plan.take_profit_price),
            "timeInForce": "GTC",
        }
    if plan.trailing_stop_pips is not None:
        body["order"]["trailingStopLossOnFill"] = {
            "distance": str(plan.trailing_stop_pips),
            "timeInForce": "GTC",
        }
    return body


def _build_order_result(payload: dict[str, Any], plan: OrderPlan | None) -> BrokerOrderResult:
    last_tx = payload.get("lastTransactionID")
    fill_tx = payload.get("orderFillTransaction") or {}
    create_tx = payload.get("orderCreateTransaction") or {}
    cancel_tx = payload.get("orderCancelTransaction") or {}
    reject_tx = payload.get("orderRejectTransaction") or {}

    if reject_tx:
        return BrokerOrderResult(
            status="REJECTED",
            broker_order_id=reject_tx.get("orderID") or create_tx.get("id"),
            client_order_id=plan.client_order_id if plan else None,
            last_transaction_id=last_tx,
            error_code=reject_tx.get("rejectReason"),
            error_message=str(reject_tx),
            raw=payload,
        )

    if fill_tx:
        return BrokerOrderResult(
            status="FILLED",
            broker_order_id=fill_tx.get("orderID") or create_tx.get("id"),
            client_order_id=plan.client_order_id if plan else None,
            fill_transaction_id=fill_tx.get("id"),
            fill_price=Decimal(str(fill_tx["price"])) if "price" in fill_tx else None,
            filled_units=Decimal(str(fill_tx["units"])) if "units" in fill_tx else None,
            trade_opened_id=(fill_tx.get("tradeOpened") or {}).get("tradeID"),
            last_transaction_id=last_tx,
            raw=payload,
        )

    if cancel_tx:
        return BrokerOrderResult(
            status="CANCELLED",
            broker_order_id=create_tx.get("id"),
            client_order_id=plan.client_order_id if plan else None,
            last_transaction_id=last_tx,
            error_code=cancel_tx.get("reason"),
            error_message=str(cancel_tx),
            raw=payload,
        )

    return BrokerOrderResult(
        status="PENDING",
        broker_order_id=create_tx.get("id"),
        client_order_id=plan.client_order_id if plan else None,
        last_transaction_id=last_tx,
        raw=payload,
    )
