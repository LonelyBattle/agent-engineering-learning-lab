from typing import Any

from openai import AsyncOpenAI

from .models import AssistantTurn, ToolCall


class OpenAICompatibleAdapter:
    def __init__(self, *, api_key: str, base_url: str, model: str) -> None:
        if not api_key:
            raise ValueError("DASHSCOPE_API_KEY 未配置")
        self.client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.model = model

    async def complete(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> AssistantTurn:
        # The compatible endpoint currently uses Chat Completions style messages.
        normalized = [item for item in messages if item.get("type") != "function_call_output"]
        for item in messages:
            if item.get("type") == "function_call_output":
                normalized.append({"role": "tool", "tool_call_id": item["call_id"], "content": item["output"]})
        response = await self.client.chat.completions.create(model=self.model, messages=normalized, tools=tools, tool_choice="auto")
        message = response.choices[0].message
        calls = [ToolCall(id=call.id, name=call.function.name, arguments=call.function.arguments) for call in message.tool_calls or []]
        return AssistantTurn(text=message.content or "", tool_calls=calls)
