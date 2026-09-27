import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse

from .factory import build_agent
from .models import ChatRequest

app = FastAPI(title="Agent Engineering Lab", version="0.1.0")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/chat")
async def chat(request: ChatRequest) -> dict[str, str]:
    try:
        return {"answer": await build_agent().run(request.message)}
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail="Agent timed out") from exc


@app.post("/chat/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    async def events():
        try:
            async for event in build_agent().stream(request.message):
                yield f"event: {event.type}\ndata: {event.model_dump_json()}\n\n"
        except Exception as exc:  # noqa: BLE001 - SSE must finish with a valid error event.
            payload = json.dumps({"type": "error", "message": str(exc)}, ensure_ascii=False)
            yield f"event: error\ndata: {payload}\n\n"
    return StreamingResponse(events(), media_type="text/event-stream")
