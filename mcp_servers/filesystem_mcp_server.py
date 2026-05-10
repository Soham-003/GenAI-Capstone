from __future__ import annotations

from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("pipeline-metadata-server")


@mcp.tool()
def list_pipeline_docs(path: str = "data/docs") -> list[str]:
    base = Path(path)
    if not base.exists():
        return []
    return [str(p) for p in base.rglob("*.md")]


@mcp.tool()
def read_doc(path: str) -> str:
    p = Path(path)
    if not p.exists():
        return f"File not found: {path}"
    return p.read_text(encoding="utf-8")


if __name__ == "__main__":
    mcp.run()
