from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator
from typing import Any, Protocol

from .models import AgentEvent, AssistantTurn, ToolCall
from .tooling import ToolRegistry


class ModelAdapter(Protocol):
    async def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AssistantTurn: ...


class AgentLoop:
    """Minimal framework-free model → tool → model loop."""

    def __init__(self, model: ModelAdapter, registry: ToolRegistry, *, max_steps: int = 8, tool_timeout: float = 10) -> None:
        self.model = model
        self.registry = registry
        self.max_steps = max_steps
        self.tool_timeout = tool_timeout

    async def stream(self, user_message: str) -> AsyncIterator[AgentEvent]:
        messages: list[dict[str, Any]] = [{"role": "user", "content": user_message}]
        for _ in range(self.max_steps):
            turn = await self.model.complete(messages, self.registry.schemas())
            if not turn.tool_calls:
                yield AgentEvent(type="message.completed", data={"text": turn.text})
                return
            messages.append({"role": "assistant", "content": turn.text, "tool_calls": [{"id": call.id, "type": "function", "function": {"name": call.name, "arguments": call.arguments}} for call in turn.tool_calls]})
            results = await asyncio.gather(*(self._execute(call) for call in turn.tool_calls))
            for call, result in zip(turn.tool_calls, results, strict=True):
                yield AgentEvent(type="tool.started", data={"call_id": call.id, "name": call.name})
                yield AgentEvent(type="tool.completed", data={"call_id": call.id, "name": call.name, "result": result.model_dump()})
                messages.append({"type": "function_call_output", "call_id": call.id, "output": result.model_dump_json()})
        yield AgentEvent(type="error", data={"code": "max_steps", "message": f"Agent exceeded {self.max_steps} steps"})

    async def run(self, user_message: str) -> str:
        async for event in self.stream(user_message):
            if event.type == "message.completed":
                return str(event.data["text"])
            if event.type == "error":
                raise RuntimeError(str(event.data["message"]))
        raise RuntimeError("Agent finished without a result")

    async def _execute(self, call: ToolCall):
        try:
            arguments = json.loads(call.arguments)
            if not isinstance(arguments, dict):
                raise TypeError("arguments must be a JSON object")
        except (json.JSONDecodeError, TypeError) as exc:
            from .models import ToolResult
            return ToolResult(ok=False, error_code="invalid_json", error_message=str(exc))
        return await self.registry.execute(call.name, arguments, self.tool_timeout)
