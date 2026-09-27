# 16 周 Agent 工程路线

每周结束必须留下：可运行程序、失败测试、复盘记录。不要仅以“看完教程”为完成标准。

| 周 | 主题 | 仓库入口 | 验收产物 |
|---:|---|---|---|
| 1 | asyncio、httpx、超时与并发 | `tools.py` | 并发 API 聚合器与错误测试 |
| 2 | Pydantic v2、FastAPI | `models.py`、`api.py` | Todo API 与接口测试 |
| 3 | 手写 Agent Loop | `agent.py` | 模型—工具—模型闭环 |
| 4 | 五工具与故障处理 | `tooling.py`、`tools.py` | 超时、错参、未知工具、循环保护 |
| 5 | FastAPI 与 SSE | `api.py` | `/chat` 与结构化流事件 |
| 6 | FastMCP | `mcp_server.py` | 安全文件系统 MCP 与路径攻击测试 |
| 7–8 | LangGraph | Notebook 第 4 章 | 周末旅行图、条件分支、checkpoint |
| 9 | 基础 RAG | Notebook 第 6 章 | 固定语料、引用、拒答、30 条评测集 |
| 10 | Agentic RAG | Notebook 第 6 章 | 查询重写、多轮检索、证据门控 |
| 11 | 三层记忆 | Notebook 第 5 章 | 工作、会话、长期记忆及删除能力 |
| 12–13 | 多 Agent | Notebook 第 7 章 | researcher/writer/reviewer/supervisor |
| 14 | 评估与观测 | Notebook 第 8 章 | trace、RAG 指标、对抗集、可靠性报告 |
| 15 | 部署与安全 | Notebook 第 9 章 | Docker、注入测试、最小权限与审计 |
| 16 | 成本与作品集 | README 验收表 | 三个项目、架构图、测试与成本报告 |

## 第一阶段练习

1. 为 `ToolRegistry` 增加重复调用去重，并写测试。
2. 将 Todo 从进程内列表迁移至 SQLite。
3. 模拟一次模型同时调用天气和汇率，验证并行执行。
4. 为外部 HTTP 工具增加只重试 429/5xx 的指数退避。
5. 给 `/chat/stream` 增加请求 ID，并贯穿日志与事件。

## 三个毕业项目

- Agentic RAG：多轮检索、引用、拒答、记忆、评估与注入测试。
- 多 Agent 写作：结构化交接、证据溯源、最多两轮返工、单/多 Agent 对比。
- 安全 MCP：鉴权、路径隔离、覆盖保护、审计、Docker 与客户端集成测试。
