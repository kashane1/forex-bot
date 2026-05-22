"""Logging must redact tokens and account ids."""

from __future__ import annotations

import json

from forex_bot.logging_config import JsonFormatter, _scrub_mapping


def test_scrub_mapping_redacts_token_keys():
    out = _scrub_mapping({"access_token": "abc", "OANDA_ACCESS_TOKEN": "xyz", "ok": 1})
    assert out["access_token"] == "[REDACTED]"
    assert out["OANDA_ACCESS_TOKEN"] == "[REDACTED]"
    assert out["ok"] == 1


def test_scrub_mapping_redacts_bearer_in_strings():
    out = _scrub_mapping({"headers": "Authorization: Bearer abc123def456"})
    assert "[REDACTED]" in out["headers"]
    assert "abc123def456" not in out["headers"]


def test_scrub_mapping_redacts_long_hex():
    out = _scrub_mapping({"id": "0123456789abcdef0123456789abcdef0123"})
    assert out["id"] == "[REDACTED]"


def test_scrub_mapping_redacts_oanda_account_id_in_url():
    out = _scrub_mapping({"msg": "GET https://api/v3/accounts/101-001-12345678-001/orders"})
    assert "12345678" not in out["msg"]
    assert "101-001-XXXXXXX-XXX" in out["msg"]


def test_scrub_mapping_redacts_oanda_token_pattern():
    fake_token = "abcdef0123456789abcdef0123456789-abcdef0123456789abcdef0123456789"
    out = _scrub_mapping({"msg": f"Authorization: Bearer {fake_token}"})
    assert fake_token not in out["msg"]


def test_scrub_value_preserves_short_account_prefix():
    """Keep the broker prefix (101-001) for debugging while masking unique part."""
    from forex_bot.logging_config import _scrub_value

    out = _scrub_value("account=101-001-12345678-001")
    assert "12345678" not in out
    assert "101-001" in out


def test_json_formatter_does_not_serialize_unsafe_extras():
    import logging

    formatter = JsonFormatter()
    record = logging.LogRecord(
        name="t",
        level=logging.INFO,
        pathname="t.py",
        lineno=1,
        msg="hello",
        args=(),
        exc_info=None,
    )
    record.extra = {"OANDA_ACCESS_TOKEN_PRACTICE": "should_be_hidden"}
    out = formatter.format(record)
    parsed = json.loads(out)
    assert parsed["extra"]["OANDA_ACCESS_TOKEN_PRACTICE"] == "[REDACTED]"
