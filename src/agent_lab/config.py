from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    dashscope_api_key: str = ""
    bailian_base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    bailian_model: str = "qwen-plus"
    agent_max_steps: int = Field(default=8, ge=1, le=30)
    agent_tool_timeout: float = Field(default=10.0, gt=0, le=120)


settings = Settings()
