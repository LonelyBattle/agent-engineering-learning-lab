"""第 3 课：查看工具 Schema，并练习正常调用与错误处理。"""

import asyncio

from agent_lab.tools import build_registry


async def main() -> None:
    registry = build_registry()
    print("已注册工具：")
    for schema in registry.schemas():
        print("-", schema["function"]["name"])

    examples = [
        ("manage_todo", {"action": "add", "title": "学习 function calling", "todo_id": None}),
        ("manage_todo", {"action": "list", "title": None, "todo_id": None}),
        ("invented_tool", {}),
        ("convert_currency", {"amount": "错误", "source": "USD", "target": "CNY"}),
    ]
    for name, arguments in examples:
        result = await registry.execute(name, arguments, timeout=1)
        print(name, result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
