from __future__ import annotations

import os

from .config import Settings

AGENT_ENV_KEYS = {
    "OPENAI_API_KEY": "openai_api_key",
    "OPENAI_MODEL": "openai_model",
    "OPENAI_API_BASE": "openai_api_base",
    "MCP_SERVER_URL": "mcp_server_url",
    "MCP_SSE_PATH": "mcp_sse_path",
    "LOG_LEVEL": "log_level",
    "LOG_JSON": "log_json",
    "LANGSMITH_API_KEY": "langsmith_api_key",
    "LANGSMITH_PROJECT": "langsmith_project",
    "LANGSMITH_ENDPOINT": "langsmith_endpoint",
    "METRICS_HOST": "metrics_host",
    "METRICS_PORT": "metrics_port",
}


def apply_agent_environment(settings: Settings, extra_env: dict[str, str] | None = None) -> None:
    # Ensure variables réservées au backend n'interfèrent pas avec l'agent
    os.environ.pop("DATABASE_URL", None)
    for env_key, attr in AGENT_ENV_KEYS.items():
        value = getattr(settings, attr)
        if value is not None:
            os.environ[env_key] = str(value)
        else:
            os.environ.pop(env_key, None)
    if extra_env:
        for key, value in extra_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
