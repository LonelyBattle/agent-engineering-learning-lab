# Agent Engineering Learning Lab

一套基于 Python 与阿里云百炼 OpenAI 兼容接口的 Agent 工程学习实验室。先手写 Agent Loop 和工具注册表，再进入 MCP、LangGraph、记忆、Agentic RAG、多 Agent、评估与部署。

## 当前可运行内容

- `01_async_pydantic.py`：异步、超时、并发与 Pydantic v2
- `02_minimal_agent_loop.py`：逐事件观察手写 Agent Loop
- `03_function_calling_tools.py`：五工具 Schema 与错误处理实验
- `04_mcp_filesystem_server.py`：安全文件系统 MCP 启动入口
- `05_fastapi_service.py`：FastAPI 与 SSE 启动入口
- `src/agent_lab/`：Pydantic v2 数据模型、工具注册表、五个教学工具、无框架 Agent Loop
- `src/agent_lab/api.py`：FastAPI `/chat`、`/health` 与 SSE 流式接口
- `src/agent_lab/mcp_server.py`：限制在沙箱目录内的 FastMCP 文件系统服务
- `tests/`：不消耗模型额度的单元测试和故障测试
- `agent_learning_with_bailian.ipynb`：十阶段总览与进阶实验
- `docs/ROADMAP.md`：16 周学习与验收路线

## 快速开始

要求 Python 3.11+。

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
pytest
```

设置 Key 后运行 CLI：

可选配置：

```powershell
$env:DASHSCOPE_API_KEY="你的百炼 API Key"
python -m agent_lab.cli "查一下杭州天气，并添加一个明天复习异步编程的待办"
```

启动 HTTP API 或 MCP Server：

```powershell
uvicorn agent_lab.api:app --reload
$env:AGENT_WORKSPACE="./agent_workspace"
python -m agent_lab.mcp_server
```

## 学习顺序

1. 依次运行主目录中的 `01_...py` 到 `05_...py`。
2. 阅读 `src/agent_lab/models.py` 和 `tooling.py`，理解类型与工具注册。
3. 阅读 `src/agent_lab/agent.py`，画出模型—工具—模型的循环。
4. 修改主目录实验文件，故意制造超时、错参和未知工具。
5. 再进入 Notebook 的 LangGraph、RAG、多 Agent 等进阶章节。

## 安全边界

- 不要把 API Key 写入 Notebook 或提交到 Git。
- 工具参数经过 Pydantic 校验；未知工具、超时与循环上限均返回结构化错误。
- 文件系统 MCP 被限制在专用工作目录内，但生产部署仍需加入认证、租户隔离和审计。
- Notebook 中的 Prompt Injection 检查仅用于教学，不能代替权限控制、输入隔离和人工确认。
- 天气、汇率及 Wikipedia 接口适合学习；生产项目应选择具有正式 SLA 的数据服务。

## 项目状态

第一阶段运行时、API 和安全 MCP 已模块化；LangGraph、记忆、Agentic RAG、多 Agent 与评估位于 Notebook 中，按 `docs/ROADMAP.md` 逐步拆分。
