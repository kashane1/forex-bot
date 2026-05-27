"""Load repo-local ``.env`` files for CLI scripts and agents."""

from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def project_root() -> Path:
    """Repository root (parent of ``src/``)."""
    return _REPO_ROOT


def load_project_dotenv(*, root: Path | None = None, override_local: bool = True) -> bool:
    """Load ``.env`` then ``.env.local`` from *root* (default: repo root).

    Returns True when at least one file was loaded.
    """
    root = root or _REPO_ROOT
    loaded = False
    try:
        from dotenv import load_dotenv
    except ImportError:
        return False

    env_path = root / ".env"
    if env_path.is_file():
        load_dotenv(env_path)
        loaded = True
    local_path = root / ".env.local"
    if local_path.is_file():
        load_dotenv(local_path, override=override_local)
        loaded = True
    return loaded


def bootstrap_environ(environ: dict[str, str] | None = None) -> dict[str, str]:
    """Return *environ* when provided; otherwise load dotenv and use ``os.environ``."""
    if environ is not None:
        return environ
    load_project_dotenv()
    return os.environ
