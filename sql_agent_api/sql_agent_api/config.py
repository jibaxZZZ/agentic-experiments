from __future__ import annotations

from functools import lru_cache

from pydantic import AnyUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: AnyUrl = Field(alias="DATABASE_URL")

    openai_api_key: str = Field(alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-5-nano", alias="OPENAI_MODEL")
    openai_api_base: str | None = Field(default=None, alias="OPENAI_API_BASE")

    mcp_server_url: AnyUrl = Field(alias="MCP_SERVER_URL")
    mcp_sse_path: str = Field(default="/sse", alias="MCP_SSE_PATH")

    log_level: str = Field(default="INFO", alias="LOG_LEVEL")
    log_json: bool = Field(default=True, alias="LOG_JSON")

    metrics_host: str = Field(default="0.0.0.0", alias="METRICS_HOST")
    metrics_port: int = Field(default=9101, alias="METRICS_PORT")

    langsmith_api_key: str | None = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str | None = Field(default=None, alias="LANGSMITH_PROJECT")
    langsmith_endpoint: str | None = Field(default=None, alias="LANGSMITH_ENDPOINT")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        env_file_encoding="utf-8",
        case_sensitive=False,
        validate_assignment=True,
    )

    @property
    def mcp_sse_url(self) -> str:
        base = str(self.mcp_server_url).rstrip("/")
        path = self.mcp_sse_path if self.mcp_sse_path.startswith("/") else f"/{self.mcp_sse_path}"
        return f"{base}{path}"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
