"""Helpers for the local research PostgreSQL store."""

from __future__ import annotations

import os
from dataclasses import dataclass
from urllib.parse import SplitResult, urlsplit, urlunsplit

DEFAULT_RESEARCH_SCHEMA = "market_data"
RESEARCH_DB_ENV_VAR = "FOREX_BOT_RESEARCH_DATABASE_URL"
_UNSAFE_DB_NAME_TOKENS = ("prod", "production", "live")
_SAFE_LOCAL_HOSTS = {"", "localhost", "127.0.0.1", "::1"}


class ResearchDatabaseError(RuntimeError):
    """Base class for research database configuration failures."""


class ResearchDatabaseBlocked(ResearchDatabaseError):
    """Raised when the local research DB was requested but is not configured."""


class ResearchDatabaseUnsafe(ResearchDatabaseError):
    """Raised when the configured research DB looks unsafe."""


@dataclass(frozen=True)
class ResearchDatabaseConfig:
    url: str
    schema: str = DEFAULT_RESEARCH_SCHEMA
    allow_non_local: bool = False

    @property
    def redacted_url(self) -> str:
        return redact_database_url(self.url)

    @property
    def database_name(self) -> str:
        return _parsed_url(self.url).path.lstrip("/")

    @property
    def host(self) -> str:
        return _parsed_url(self.url).hostname or ""


def _parsed_url(url: str) -> SplitResult:
    parsed = urlsplit(url)
    if parsed.scheme not in {"postgresql", "postgres"}:
        raise ResearchDatabaseUnsafe(
            f"Unsupported research database URL scheme in {redact_database_url(url)}"
        )
    if not parsed.path or parsed.path == "/":
        raise ResearchDatabaseUnsafe(
            f"Research database URL must include a database name: {redact_database_url(url)}"
        )
    return parsed


def redact_database_url(url: str) -> str:
    parsed = urlsplit(url)
    if "@" not in parsed.netloc:
        return url
    userinfo, hostinfo = parsed.netloc.rsplit("@", 1)
    username = userinfo.split(":", 1)[0] if userinfo else ""
    netloc = f"{username}:***@{hostinfo}" if username else f"***@{hostinfo}"
    return urlunsplit((parsed.scheme, netloc, parsed.path, parsed.query, parsed.fragment))


def validate_research_database_url(
    url: str,
    *,
    allow_non_local: bool = False,
) -> ResearchDatabaseConfig:
    parsed = _parsed_url(url)
    db_name = parsed.path.lstrip("/")
    lowered = db_name.lower()
    if any(token in lowered for token in _UNSAFE_DB_NAME_TOKENS):
        raise ResearchDatabaseUnsafe(
            f"Refusing research DB that looks live/prod: {redact_database_url(url)}"
        )
    host = parsed.hostname or ""
    if not allow_non_local and host not in _SAFE_LOCAL_HOSTS:
        raise ResearchDatabaseUnsafe(
            f"Refusing non-local research DB host in {redact_database_url(url)}"
        )
    return ResearchDatabaseConfig(url=url, schema=DEFAULT_RESEARCH_SCHEMA, allow_non_local=allow_non_local)


def get_research_database_config(
    *,
    environ: dict[str, str] | None = None,
    require: bool = True,
    allow_non_local: bool = False,
) -> ResearchDatabaseConfig:
    env = environ if environ is not None else os.environ
    raw = env.get(RESEARCH_DB_ENV_VAR, "").strip()
    if not raw:
        if require:
            raise ResearchDatabaseBlocked(
                f"{RESEARCH_DB_ENV_VAR} is not set; local Postgres research DB is BLOCKED."
            )
        raise ResearchDatabaseBlocked(f"{RESEARCH_DB_ENV_VAR} is not set.")
    return validate_research_database_url(raw, allow_non_local=allow_non_local)
