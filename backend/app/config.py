from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(os.getenv("MOE_DEBATE_CONFIG", Path(__file__).resolve().parents[1] / "config.toml"))


@dataclass(frozen=True)
class DatabaseConfig:
    host: str = "127.0.0.1"
    port: int = 3306
    user: str = "moe_debate"
    password: str = "moe_debate_password"
    database: str = "moe_debate"
    charset: str = "utf8mb4"


def _read_config_file() -> dict[str, Any]:
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as config_file:
        return tomllib.load(config_file)


def database_config() -> DatabaseConfig:
    raw = _read_config_file().get("database", {})
    return DatabaseConfig(
        host=os.getenv("MOE_DEBATE_DB_HOST", raw.get("host", DatabaseConfig.host)),
        port=int(os.getenv("MOE_DEBATE_DB_PORT", raw.get("port", DatabaseConfig.port))),
        user=os.getenv("MOE_DEBATE_DB_USER", raw.get("user", DatabaseConfig.user)),
        password=os.getenv("MOE_DEBATE_DB_PASSWORD", raw.get("password", DatabaseConfig.password)),
        database=os.getenv("MOE_DEBATE_DB_NAME", raw.get("database", DatabaseConfig.database)),
        charset=os.getenv("MOE_DEBATE_DB_CHARSET", raw.get("charset", DatabaseConfig.charset)),
    )
