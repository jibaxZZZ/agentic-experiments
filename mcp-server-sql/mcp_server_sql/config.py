from functools import lru_cache
from typing import Dict

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    postgres_url: str | None = Field(default=None, alias="DATABASE_URL_POSTGRES")
    mysql_url: str | None = Field(default=None, alias="DATABASE_URL_MYSQL")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")
    metrics_host: str = Field(default="0.0.0.0", alias="METRICS_HOST")
    metrics_port: int = Field(default=8001, alias="METRICS_PORT")
    mcp_host: str = Field(default="127.0.0.1", alias="MCP_SERVER_HOST")
    mcp_port: int = Field(default=8000, alias="MCP_SERVER_PORT")
    mcp_transport: str = Field(default="stdio", alias="MCP_SERVER_TRANSPORT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
    )

    def get_available_databases(self) -> Dict[str, str]:
        dsn_by_name: Dict[str, str] = {}
        if self.postgres_url:
            dsn_by_name["postgres"] = self.postgres_url
        if self.mysql_url:
            dsn_by_name["mysql"] = self.mysql_url
        return dsn_by_name


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
