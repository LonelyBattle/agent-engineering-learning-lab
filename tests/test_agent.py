from typing import Any

import pytest
from pydantic import BaseModel

from agent_lab.agent import AgentLoop
from agent_lab.models import AssistantTurn, ToolCall
from agent_lab.tooling import ToolDefinition, ToolRegistry


class EchoArgs(BaseModel):
    text: str


class FakeModel:
    def __init__(self, turns: list[AssistantTurn]) -> None:
        self.turns = iter(turns)
        self.messages: list[list[dict[str, Any]]] = []

    async def complete(self, messages, tools):
        self.messages.append(messages.copy())
        return next(self.turns)


@pytest.mark.asyncio
async def test_agent_calls_tool_then_returns_answer() -> None:
    model = FakeModel([
        AssistantTurn(tool_calls=[ToolCall(id="1", name="echo", arguments='{"text":"hi"}')]),
        AssistantTurn(text="完成"),
    ])
    registry = ToolRegistry()
    registry.register(ToolDefinition("echo", "echo", EchoArgs, lambda text: text))
    assert await AgentLoop(model, registry).run("test") == "完成"
    assert model.messages[1][-1]["type"] == "function_call_output"


@pytest.mark.asyncio
async def test_bad_json_becomes_tool_output() -> None:
    model = FakeModel([
        AssistantTurn(tool_calls=[ToolCall(id="1", name="echo", arguments="not-json")]),
        AssistantTurn(text="参数错误"),
    ])
    registry = ToolRegistry()
    registry.register(ToolDefinition("echo", "echo", EchoArgs, lambda text: text))
    assert await AgentLoop(model, registry).run("test") == "参数错误"
    assert "invalid_json" in model.messages[1][-1]["output"]


@pytest.mark.asyncio
async def test_max_steps_stops_loop() -> None:
    model = FakeModel([AssistantTurn(tool_calls=[ToolCall(id=str(i), name="missing", arguments="{}")]) for i in range(2)])
    with pytest.raises(RuntimeError, match="exceeded"):
        await AgentLoop(model, ToolRegistry(), max_steps=2).run("loop")
