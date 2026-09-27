import os
from pathlib import Path

from fastmcp import FastMCP

mcp = FastMCP("secure-filesystem-lab")
ROOT = Path(os.getenv("AGENT_WORKSPACE", "agent_workspace")).resolve()
ROOT.mkdir(parents=True, exist_ok=True)
MAX_FILE_BYTES = 1_000_000


def safe_path(relative_path: str) -> Path:
    candidate = (ROOT / relative_path).resolve()
    if not candidate.is_relative_to(ROOT):
        raise ValueError("路径超出 AGENT_WORKSPACE")
    return candidate


@mcp.tool
def list_directory(path: str = ".") -> list[dict[str, object]]:
    target = safe_path(path)
    if not target.is_dir():
        raise ValueError("目录不存在")
    return [{"name": item.name, "is_directory": item.is_dir(), "size": item.stat().st_size if item.is_file() else None} for item in sorted(target.iterdir())]


@mcp.tool
def read_file(path: str) -> str:
    target = safe_path(path)
    if not target.is_file():
        raise ValueError("文件不存在")
    if target.stat().st_size > MAX_FILE_BYTES:
        raise ValueError("文件过大")
    return target.read_text(encoding="utf-8")


@mcp.tool
def write_file(path: str, content: str, overwrite: bool = False) -> dict[str, object]:
    target = safe_path(path)
    if target.exists() and not overwrite:
        raise FileExistsError("文件已存在；显式设置 overwrite=true 才能覆盖")
    encoded = content.encode("utf-8")
    if len(encoded) > MAX_FILE_BYTES:
        raise ValueError("内容过大")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(encoded)
    return {"path": str(target.relative_to(ROOT)), "bytes": len(encoded)}


@mcp.tool
def search_content(query: str, path: str = ".", limit: int = 20) -> list[dict[str, object]]:
    if not query or not 1 <= limit <= 100:
        raise ValueError("query 不能为空且 limit 必须为 1..100")
    base = safe_path(path)
    results: list[dict[str, object]] = []
    for file in base.rglob("*"):
        if not file.is_file() or file.stat().st_size > MAX_FILE_BYTES:
            continue
        try:
            for line_number, line in enumerate(file.read_text(encoding="utf-8").splitlines(), start=1):
                if query.casefold() in line.casefold():
                    results.append({"path": str(file.relative_to(ROOT)), "line": line_number, "text": line[:300]})
                    if len(results) >= limit:
                        return results
        except UnicodeDecodeError:
            continue
    return results


if __name__ == "__main__":
    mcp.run(transport="http", host="127.0.0.1", port=8001)
