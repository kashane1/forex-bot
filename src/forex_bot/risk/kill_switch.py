"""File- and config-based kill switch."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class KillSwitch:
    path: Path
    trading_enabled: bool

    def is_active(self) -> bool:
        if not self.trading_enabled:
            return True
        return self.path.exists()

    def reason(self) -> str:
        if not self.trading_enabled:
            return "trading_enabled=false in config"
        if self.path.exists():
            return f"kill switch file present at {self.path}"
        return "kill switch inactive"
