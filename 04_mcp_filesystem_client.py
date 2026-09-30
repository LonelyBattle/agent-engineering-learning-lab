"""第 4 课：连接并调用安全文件系统 MCP Server。"""

import asyncio
import json

from fastmcp import Client


MCP_URL = "http://127.0.0.1:8001/mcp"


def show_result(title: str, result: object) -> None:
    """以便于阅读的格式打印 MCP 工具返回值。"""
    data = getattr(result, "data", result)
    print(f"\n{title}:")
    print(json.dumps(data, ensure_ascii=False, indent=2, default=str))


async def main() -> None:
    async with Client(MCP_URL) as client:
        tools = await client.list_tools()
        print("已连接 MCP Server，可用工具：")
        for tool in tools:
            print(f"- {tool.name}: {tool.description or '无描述'}")

        # overwrite=True 让本示例可以重复执行。
        write_result = await client.call_tool(
            "write_file",
            {
                "path": "demo/hello.txt",
                "content": "你好，MCP！\n这是客户端写入的文件。",
                "overwrite": True,
            },
        )
        show_result("写入结果", write_result)

        read_result = await client.call_tool(
            "read_file",
            {"path": "demo/hello.txt"},
        )
        show_result("读取结果", read_result)

        search_result = await client.call_tool(
            "search_content",
            {"query": "客户端", "path": ".", "limit": 10},
        )
        show_result("搜索结果", search_result)

        list_result = await client.call_tool(
            "list_directory",
            {"path": "demo"},
        )
        show_result("目录内容", list_result)


if __name__ == "__main__":
    asyncio.run(main())
