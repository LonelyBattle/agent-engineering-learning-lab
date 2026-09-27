"""第 2 课：运行无框架的最小 Agent Loop。"""

import argparse
import asyncio

from agent_lab.factory import build_agent


async def main(prompt: str) -> None:
    agent = build_agent()
    async for event in agent.stream(prompt):
        print(event.model_dump_json(indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", nargs="?", default="列出我的待办")
    arguments = parser.parse_args()
    asyncio.run(main(arguments.prompt))
