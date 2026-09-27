from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class ToolResult(BaseModel):
    ok: bool
    data: Any | None = None
    error_code: str | None = None
    error_message: str | None = None
    retryable: bool = False


class ToolCall(BaseModel):
    id: str
    name: str
    arguments: str


class AssistantTurn(BaseModel):
    text: str = ""
    tool_calls: list[ToolCall] = Field(default_factory=list)


class ChatRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=20_000)


class AgentEvent(BaseModel):
    type: Literal["tool.started", "tool.completed", "message.completed", "error"]
    data: dict[str, Any]
