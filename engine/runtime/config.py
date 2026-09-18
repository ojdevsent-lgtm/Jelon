from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

@dataclass
class RuntimeConfig:
    model_path: Path | None = None
    data_dir: Path = Path("data")
    max_steps: int = 12
    autonomy: str = "ask"
    browser_enabled: bool = False
    network_enabled: bool = False
    allowed_workspace: Path = Path(".")
    extra: dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if self.max_steps < 1 or self.max_steps > 100:
            raise ValueError("max_steps must be between 1 and 100")
        if self.autonomy not in {"ask", "trusted_workspace", "authorized_repo"}:
            raise ValueError("Unsupported autonomy mode")
