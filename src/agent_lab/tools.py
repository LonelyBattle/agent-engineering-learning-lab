from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Literal

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .tooling import ToolDefinition, ToolRegistry

LOGGER = logging.getLogger("agent_lab")
TODOS: list[dict[str, object]] = []


class StrictArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")


class WeatherArgs(StrictArgs):
    city: str = Field(min_length=1, max_length=80)


class ExchangeArgs(StrictArgs):
    amount: float = Field(gt=0, le=10_000_000)
    source: str = Field(min_length=3, max_length=3)
    target: str = Field(min_length=3, max_length=3)


class TodoArgs(StrictArgs):
    action: Literal["add", "list", "complete"]
    title: str | None
    todo_id: int | None


class LogArgs(StrictArgs):
    level: Literal["debug", "info", "warning", "error"]
    message: str = Field(min_length=1, max_length=1000)


class SearchArgs(StrictArgs):
    query: str = Field(min_length=2, max_length=200)
    limit: int = Field(ge=1, le=5)


async def weather(city: str) -> dict[str, object]:
    async with httpx.AsyncClient(timeout=8) as client:
        geo = await client.get("https://geocoding-api.open-meteo.com/v1/search", params={"name": city, "count": 1, "language": "zh"})
        geo.raise_for_status()
        matches = geo.json().get("results") or []
        if not matches:
            raise ValueError(f"未找到城市：{city}")
        point = matches[0]
        forecast = await client.get("https://api.open-meteo.com/v1/forecast", params={"latitude": point["latitude"], "longitude": point["longitude"], "current": "temperature_2m,precipitation,wind_speed_10m"})
        forecast.raise_for_status()
        return {"city": point["name"], **forecast.json()["current"]}


async def exchange_rate(amount: float, source: str, target: str) -> dict[str, object]:
    source, target = source.upper(), target.upper()
    async with httpx.AsyncClient(timeout=8) as client:
        response = await client.get("https://api.frankfurter.app/latest", params={"amount": amount, "from": source, "to": target})
        response.raise_for_status()
        payload = response.json()
        if target not in payload.get("rates", {}):
            raise ValueError(f"不支持的币种：{source}/{target}")
        return {"amount": amount, "source": source, "target": target, "result": payload["rates"][target]}


def todo(action: str, title: str | None, todo_id: int | None) -> object:
    if action == "add":
        if not title:
            raise ValueError("add 操作需要 title")
        item = {"id": len(TODOS) + 1, "title": title, "completed": False}
        TODOS.append(item)
        return item
    if action == "complete":
        if todo_id is None:
            raise ValueError("complete 操作需要 todo_id")
        for item in TODOS:
            if item["id"] == todo_id:
                item["completed"] = True
                return item
        raise ValueError(f"待办不存在：{todo_id}")
    return TODOS.copy()


def write_log(level: str, message: str) -> dict[str, str]:
    getattr(LOGGER, level)(message)
    return {"level": level, "message": message, "timestamp": datetime.now(UTC).isoformat()}


async def search(query: str, limit: int) -> list[dict[str, str]]:
    async with httpx.AsyncClient(timeout=8, headers={"User-Agent": "agent-engineering-lab/0.1"}) as client:
        response = await client.get("https://zh.wikipedia.org/w/api.php", params={"action": "query", "list": "search", "srsearch": query, "format": "json", "utf8": 1, "srlimit": limit})
        response.raise_for_status()
        return [{"title": item["title"], "snippet": item["snippet"]} for item in response.json()["query"]["search"]]


def build_registry() -> ToolRegistry:
    registry = ToolRegistry()
    for definition in [
        ToolDefinition("get_weather", "查询指定城市的实时天气。", WeatherArgs, weather),
        ToolDefinition("convert_currency", "按最新公开汇率换算货币。", ExchangeArgs, exchange_rate),
        ToolDefinition("manage_todo", "添加、列出或完成本地待办。", TodoArgs, todo),
        ToolDefinition("write_log", "写入一条结构化应用日志。", LogArgs, write_log),
        ToolDefinition("search_web", "在中文维基百科搜索背景资料。", SearchArgs, search),
    ]:
        registry.register(definition)
    return registry
