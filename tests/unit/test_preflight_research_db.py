from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[2]


def _load_script(name: str):
    path = _REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


preflight = _load_script("preflight_research_db")


def test_env_absent_blocked(capsys):
    rc = preflight.main([], environ={})
    out = json.loads(capsys.readouterr().out)
    assert rc == 2
    assert out["status"] == "BLOCKED"


def test_url_redaction_in_blocked_payload(capsys):
    rc = preflight.main([], environ={"FOREX_BOT_RESEARCH_DATABASE_URL": "postgresql://u:p@db.internal/forex_bot"})
    out = json.loads(capsys.readouterr().out)
    assert rc == 1
    assert "p@" not in out["error"]


def test_create_schema_path_mocked(monkeypatch):
    called = {"create": False}

    def fake_report(*, create_schema, environ=None):
        called["create"] = create_schema
        return {"status": "PASS"}

    monkeypatch.setattr(preflight, "build_report", fake_report)
    assert preflight.main(["--create-schema"], environ={}) == 0
    assert called["create"] is True
