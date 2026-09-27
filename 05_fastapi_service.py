"""第 5 课：启动包含普通响应与 SSE 的 FastAPI 服务。"""

import uvicorn

from agent_lab.api import app

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
