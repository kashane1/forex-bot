from __future__ import annotations

import pytest

from forex_bot.data.research_db import (
    DEFAULT_RESEARCH_SCHEMA,
    RESEARCH_DB_ENV_VAR,
    ResearchDatabaseBlocked,
    ResearchDatabaseUnsafe,
    get_research_database_config,
    redact_database_url,
)


def test_missing_env_gives_clear_blocked_result():
    with pytest.raises(ResearchDatabaseBlocked, match=RESEARCH_DB_ENV_VAR):
        get_research_database_config(environ={})


def test_password_redaction_works():
    url = "postgresql://user:secret@localhost:5432/forex_bot"
    redacted = redact_database_url(url)
    assert "secret" not in redacted
    assert redacted == "postgresql://user:***@localhost:5432/forex_bot"


def test_schema_defaults_to_market_data():
    cfg = get_research_database_config(
        environ={RESEARCH_DB_ENV_VAR: "postgresql://localhost:5432/forex_bot"}
    )
    assert cfg.schema == DEFAULT_RESEARCH_SCHEMA


def test_refuses_obviously_live_or_prod_database_name():
    with pytest.raises(ResearchDatabaseUnsafe, match="live/prod"):
        get_research_database_config(
            environ={RESEARCH_DB_ENV_VAR: "postgresql://localhost:5432/forex_bot_prod"}
        )


def test_refuses_non_local_host_by_default():
    with pytest.raises(ResearchDatabaseUnsafe, match="non-local"):
        get_research_database_config(
            environ={RESEARCH_DB_ENV_VAR: "postgresql://db.internal:5432/forex_bot"}
        )
