from __future__ import annotations

import asyncio
import inspect
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, ValidationError

from .models import ToolResult

ToolFunction = Callable[..., Any]


@dataclass(frozen=True, slots=True)
class ToolDefinition:
    name: str
    description: str
    arguments_model: type[BaseModel]
    function: ToolFunction

    def schema(self) -> dict[str, Any]:
        parameters = self.arguments_model.model_json_schema()
        parameters["additionalProperties"] = False
        return {"type": "function", "function": {"name": self.name, "description": self.description, "parameters": parameters, "strict": True}}


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"duplicate tool: {tool.name}")
        self._tools[tool.name] = tool

    def schemas(self) -> list[dict[str, Any]]:
        return [tool.schema() for tool in self._tools.values()]

    async def execute(self, name: str, arguments: dict[str, Any], timeout: float) -> ToolResult:
        tool = self._tools.get(name)
        if tool is None:
            return ToolResult(ok=False, error_code="unknown_tool", error_message=f"Tool {name!r} is not registered")
        try:
            validated = tool.arguments_model.model_validate(arguments)
        except ValidationError as exc:
            return ToolResult(ok=False, error_code="invalid_arguments", error_message=str(exc))

        async def invoke() -> Any:
            values = validated.model_dump()
            if inspect.iscoroutinefunction(tool.function):
                return await tool.function(**values)
            return await asyncio.to_thread(tool.function, **values)

        try:
            value = await asyncio.wait_for(invoke(), timeout=timeout)
            return value if isinstance(value, ToolResult) else ToolResult(ok=True, data=value)
        except TimeoutError:
            return ToolResult(ok=False, error_code="tool_timeout", error_message=f"Tool {name!r} exceeded {timeout:g}s", retryable=True)
        except Exception as exc:  # noqa: BLE001 - third-party tools are an isolation boundary.
            return ToolResult(ok=False, error_code="tool_error", error_message=str(exc))
