from __future__ import annotations

from pathlib import Path

from forex_bot.project_env import bootstrap_environ, load_project_dotenv, project_root


def test_project_root_points_at_repo(tmp_path: Path, monkeypatch) -> None:
    fake_repo = tmp_path / "repo"
    (fake_repo / "src" / "forex_bot").mkdir(parents=True)
    monkeypatch.setattr("forex_bot.project_env._REPO_ROOT", fake_repo)
    assert project_root() == fake_repo


def test_bootstrap_environ_honors_explicit_environ() -> None:
    explicit = {"FOREX_BOT_RESEARCH_DATABASE_URL": "postgresql://localhost/test"}
    assert bootstrap_environ(explicit) is explicit


def test_load_project_dotenv_reads_repo_files(tmp_path: Path, monkeypatch) -> None:
    import os

    (tmp_path / ".env").write_text("OANDA_ENVIRONMENT=practice\n", encoding="utf-8")
    (tmp_path / ".env.local").write_text(
        "FOREX_BOT_RESEARCH_DATABASE_URL=postgresql://localhost:5432/forex_bot\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("FOREX_BOT_RESEARCH_DATABASE_URL", raising=False)
    assert load_project_dotenv(root=tmp_path) is True
    assert os.environ["FOREX_BOT_RESEARCH_DATABASE_URL"].endswith("/forex_bot")
