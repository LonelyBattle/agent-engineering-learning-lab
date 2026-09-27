import argparse
import asyncio

from .factory import build_agent


async def _run(prompt: str) -> None:
    print(await build_agent().run(prompt))


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the learning agent")
    parser.add_argument("prompt", help="User request")
    args = parser.parse_args()
    asyncio.run(_run(args.prompt))


if __name__ == "__main__":
    main()
