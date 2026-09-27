"""第 1 课：asyncio、超时、并发与 Pydantic v2。"""

import asyncio
from time import perf_counter

from pydantic import BaseModel, Field


class FetchTask(BaseModel):
    name: str = Field(min_length=1)
    delay: float = Field(ge=0, le=5)


class FetchResult(BaseModel):
    name: str
    elapsed: float
    ok: bool


async def simulate_fetch(task: FetchTask, timeout: float = 1.0) -> FetchResult:
    started = perf_counter()
    try:
        async with asyncio.timeout(timeout):
            await asyncio.sleep(task.delay)
        return FetchResult(name=task.name, elapsed=perf_counter() - started, ok=True)
    except TimeoutError:
        return FetchResult(name=task.name, elapsed=perf_counter() - started, ok=False)


async def main() -> None:
    tasks = [FetchTask(name="weather", delay=0.1), FetchTask(name="exchange", delay=1.5)]
    results = await asyncio.gather(*(simulate_fetch(task) for task in tasks))
    for result in results:
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(main())
