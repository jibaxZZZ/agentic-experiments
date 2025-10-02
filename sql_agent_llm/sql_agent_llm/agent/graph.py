from __future__ import annotations

from typing import Any
from uuid import uuid4

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from ..config import Settings
from ..prompts import SYSTEM_PROMPT
from ..tools import build_tools
from ..mcp_client import MCPToolClient


class AgentGraph:
    def __init__(self, settings: Settings, client: MCPToolClient) -> None:
        self._settings = settings
        self._client = client
        self._memory = MemorySaver()
        self._graph = self._build_graph()

    def _build_graph(self):  # noqa: ANN202 - library typing noise
        llm = ChatOpenAI(
            model=self._settings.openai_model,
            temperature=0.1,
            **self._settings.openai_kwargs(),
        )
        tools = build_tools(self._client)
        return create_react_agent(
            llm,
            tools,
            prompt=SYSTEM_PROMPT,
            checkpointer=self._memory,
        )

    async def run(self, question: str, *, thread_id: str | None = None) -> dict[str, Any]:
        thread = thread_id or str(uuid4())
        result = await self._graph.ainvoke(
            {"messages": [HumanMessage(content=question)]},
            config={"configurable": {"thread_id": thread}},
        )
        result.setdefault("config", {})
        result["config"]["thread_id"] = thread
        return result
