"""
Tool Registry

Manages tool definitions, schemas, and execution routing.
"""

import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field

from app.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ToolDefinition:
    name: str
    description: str
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]
    endpoint_url: Optional[str] = None
    method: str = "POST"
    auth_type: str = "none"
    handler: Optional[Callable] = None
    enabled: bool = True


class ToolRegistry:
    """Central registry for all tools available to voice agents."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        """Register a tool definition."""
        self._tools[tool.name] = tool
        logger.info("tool.registered", name=tool.name)

    def unregister(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self, enabled_only: bool = True) -> List[ToolDefinition]:
        tools = list(self._tools.values())
        if enabled_only:
            tools = [t for t in tools if t.enabled]
        return tools

    def get_openai_tools_format(self) -> List[Dict[str, Any]]:
        """Return tools in OpenAI function-calling format."""
        result = []
        for tool in self.list_tools():
            result.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                },
            })
        return result

    async def execute(self, name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name with given parameters."""
        tool = self._tools.get(name)
        if not tool:
            return {"error": f"Tool '{name}' not found"}

        if not tool.enabled:
            return {"error": f"Tool '{name}' is disabled"}

        logger.info("tool.executing", name=name, params=params)

        # If tool has a local handler, call it
        if tool.handler:
            try:
                if asyncio.iscoroutinefunction(tool.handler):
                    result = await tool.handler(**params)
                else:
                    result = tool.handler(**params)
                return {"tool": name, "result": result, "status": "ok"}
            except Exception as e:
                logger.error("tool.handler_failed", name=name, error=str(e))
                return {"tool": name, "error": str(e), "status": "error"}

        # If tool has an endpoint, call it via HTTP
        if tool.endpoint_url:
            import httpx
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    headers = {}
                    if tool.auth_type == "bearer":
                        # Token resolution happens at call time
                        pass
                    elif tool.auth_type == "demiurge":
                        from app.config import settings
                        if settings.DEMIURGE_SECRETS_TOKEN:
                            headers["Authorization"] = f"Bearer {settings.DEMIURGE_SECRETS_TOKEN}"

                    if tool.method.upper() == "GET":
                        resp = await client.get(tool.endpoint_url, params=params, headers=headers)
                    else:
                        resp = await client.post(tool.endpoint_url, json=params, headers=headers)
                    resp.raise_for_status()
                    return {"tool": name, "result": resp.json(), "status": "ok"}
            except Exception as e:
                logger.error("tool.endpoint_failed", name=name, error=str(e))
                return {"tool": name, "error": str(e), "status": "error"}

        return {"error": f"Tool '{name}' has no handler or endpoint"}


# Singleton
_tool_registry: Optional[ToolRegistry] = None


def get_tool_registry() -> ToolRegistry:
    global _tool_registry
    if _tool_registry is None:
        _tool_registry = ToolRegistry()
    return _tool_registry
