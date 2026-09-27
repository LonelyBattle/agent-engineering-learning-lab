import asyncio

import pytest
from pydantic import BaseModel, ConfigDict

from agent_lab.tooling import ToolDefinition, ToolRegistry


class Args(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: int


@pytest.mark.asyncio
async def test_unknown_tool_is_structured_error() -> None:
    result = await ToolRegistry().execute("invented", {}, timeout=1)
    assert not result.ok
    assert result.error_code == "unknown_tool"


@pytest.mark.asyncio
async def test_invalid_arguments_do_not_execute_tool() -> None:
    registry = ToolRegistry()
    registry.register(ToolDefinition("double", "double", Args, lambda value: value * 2))
    result = await registry.execute("double", {"value": "not-an-int"}, timeout=1)
    assert result.error_code == "invalid_arguments"


@pytest.mark.asyncio
async def test_timeout_is_retryable() -> None:
    async def slow(value: int) -> int:
        await asyncio.sleep(0.1)
        return value

    registry = ToolRegistry()
    registry.register(ToolDefinition("slow", "slow", Args, slow))
    result = await registry.execute("slow", {"value": 1}, timeout=0.01)
    assert result.error_code == "tool_timeout"
    assert result.retryable


def test_schema_is_strict() -> None:
    definition = ToolDefinition("double", "double", Args, lambda value: value * 2)
    schema = definition.schema()["function"]
    assert schema["strict"] is True
    assert schema["parameters"]["additionalProperties"] is False
