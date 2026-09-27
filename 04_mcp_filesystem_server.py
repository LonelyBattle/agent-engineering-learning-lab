"""第 4 课：启动安全文件系统 MCP Server。"""

from agent_lab.mcp_server import mcp

if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)
