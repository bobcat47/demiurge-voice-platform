"""
Agent Runtime

Orchestrates a single agent's behavior during a call.
Manages LLM context, tool selection, memory, and response generation.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone

from app.providers.llm.base import LLMProvider, LLMMessage, LLMResponse
from app.providers.llm.factory import get_llm_provider
from app.tools.registry import ToolRegistry, get_tool_registry
from app.core.logger import get_logger
from app.config import settings

logger = get_logger(__name__)


class AgentRuntime:
    """
    Runtime environment for a voice agent during an active call.

    [MOCKED] Full real-time streaming loop is stubbed.
    The synchronous request/response path works for testing.
    """

    def __init__(
        self,
        agent_id: str,
        agent_config: Dict[str, Any],
        llm_provider: Optional[LLMProvider] = None,
        tool_registry: Optional[ToolRegistry] = None,
    ):
        self.agent_id = agent_id
        self.config = agent_config
        self.system_prompt = agent_config.get("system_prompt", "You are a helpful voice assistant.")
        self.llm_provider = llm_provider or get_llm_provider(
            agent_config.get("llm_provider"),
            agent_config.get("llm_model"),
        )
        self.tools = tool_registry or get_tool_registry()
        self.memory_enabled = agent_config.get("memory_enabled", True)
        self.enabled_tool_names = agent_config.get("tools_enabled", [])

        # Conversation context
        self.messages: List[LLMMessage] = []
        self._add_system_message()

        self.start_time = datetime.now(timezone.utc)
        self.turn_count = 0

    def _add_system_message(self):
        self.messages.append(LLMMessage(role="system", content=self.system_prompt))

    async def on_user_input(self, text: str) -> str:
        """Process user input and generate agent response."""
        self.messages.append(LLMMessage(role="user", content=text))
        self.turn_count += 1

        # Build tool list
        available_tools = None
        if self.enabled_tool_names:
            tool_defs = [self.tools.get(name) for name in self.enabled_tool_names if self.tools.get(name)]
            available_tools = self.tools.get_openai_tools_format() if tool_defs else None

        try:
            response: LLMResponse = await self.llm_provider.complete(
                messages=self.messages,
                tools=available_tools,
                temperature=0.7,
            )
        except Exception as e:
            logger.error("agent_runtime.llm_failed", error=str(e))
            return "I'm sorry, I'm having trouble processing that. Could you repeat?"

        # Handle tool calls
        if response.tool_calls:
            tool_results = []
            for tc in response.tool_calls:
                tool_name = tc.get("function", {}).get("name", "")
                try:
                    import json
                    args = json.loads(tc.get("function", {}).get("arguments", "{}"))
                except Exception:
                    args = {}

                logger.info("agent_runtime.tool_call", tool=tool_name, args=args)
                result = await self.tools.execute(tool_name, args)
                tool_results.append({"tool": tool_name, "result": result})

            # Add assistant message with tool_calls
            self.messages.append(LLMMessage(
                role="assistant",
                content=response.content or "",
                tool_calls=response.tool_calls,
            ))

            # Add tool results
            for tr in tool_results:
                self.messages.append(LLMMessage(
                    role="tool",
                    content=str(tr["result"]),
                ))

            # Get final response after tool execution
            try:
                final = await self.llm_provider.complete(self.messages, temperature=0.7)
                response_text = final.content or ""
            except Exception as e:
                logger.error("agent_runtime.tool_followup_failed", error=str(e))
                response_text = response.content or ""
        else:
            response_text = response.content or ""
            self.messages.append(LLMMessage(role="assistant", content=response_text))

        return response_text

    async def on_interrupt(self):
        """Handle user interruption (barge-in)."""
        logger.info("agent_runtime.interrupted", agent_id=self.agent_id)

    def get_context_window(self) -> List[Dict[str, str]]:
        """Return current conversation context."""
        return [{"role": m.role, "content": m.content} for m in self.messages]

    def get_stats(self) -> Dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "turn_count": self.turn_count,
            "context_messages": len(self.messages),
            "elapsed_seconds": (datetime.now(timezone.utc) - self.start_time).total_seconds(),
        }
