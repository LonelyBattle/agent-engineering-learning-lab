from .agent import AgentLoop
from .config import settings
from .openai_adapter import OpenAICompatibleAdapter
from .tools import build_registry


def build_agent() -> AgentLoop:
    model = OpenAICompatibleAdapter(api_key=settings.dashscope_api_key, base_url=settings.bailian_base_url, model=settings.bailian_model)
    return AgentLoop(model, build_registry(), max_steps=settings.agent_max_steps, tool_timeout=settings.agent_tool_timeout)
