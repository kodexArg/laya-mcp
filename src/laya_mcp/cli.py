"""Command-line interface and entrypoints for laya-mcp."""

from __future__ import annotations

import argparse
import logging
import os
import sys

import anyio
import httpx
from mcp.client.sse import sse_client
from mcp.server.stdio import stdio_server

from laya_mcp.server import mcp

logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)

DEFAULT_PORT = int(os.getenv("LAYA_MCP_PORT", "28005"))
DEFAULT_HOST = os.getenv("LAYA_MCP_HOST", "127.0.0.1")


def is_daemon_running(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    """Checks if the local resident daemon is running and healthy."""
    try:
        with httpx.Client(timeout=0.3) as client:
            r = client.get(f"http://{host}:{port}/health")
            return r.status_code == 200
    except Exception:
        return False


async def bridge_stdio_to_daemon(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Bridges stdin/stdout to the resident background MCP daemon via SSE."""
    url = f"http://{host}:{port}/sse"
    async with stdio_server() as (stdin_r, stdout_w):
        async with sse_client(url) as (sse_r, sse_w):

            async def forward_in():
                async for item in stdin_r:
                    if not isinstance(item, Exception):
                        await sse_w.send(item)

            async def forward_out():
                async for item in sse_r:
                    if not isinstance(item, Exception):
                        await stdout_w.send(item)

            async with anyio.create_task_group() as tg:
                tg.start_soon(forward_in)
                tg.start_soon(forward_out)


def run_stdio(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Runs stdio mode. Prioritizes the daemon bridge to eliminate model loading cold-starts."""
    if is_daemon_running(host, port):
        anyio.run(bridge_stdio_to_daemon, host, port)
    else:
        # Fallback to direct in-process stdio execution
        mcp.run(transport="stdio")


def run_daemon(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> None:
    """Runs the resident background daemon on the specified port."""
    print("[laya-mcp] Initializing GPU router and preloading checkpoints...", file=sys.stderr)
    from laya_mcp.engine import get_router

    get_router()
    print(f"[laya-mcp] Models preloaded. Starting SSE daemon on http://{host}:{port}...", file=sys.stderr)
    mcp.run(transport="sse", host=host, port=port)


def main() -> None:
    parser = argparse.ArgumentParser(description="laya-mcp: Model Context Protocol server for Laya")
    subparsers = parser.add_subparsers(dest="command", help="Mode of operation")

    stdio_p = subparsers.add_parser("stdio", help="Run over stdio transport")
    stdio_p.add_argument("--host", default=DEFAULT_HOST)
    stdio_p.add_argument("--port", type=int, default=DEFAULT_PORT)

    daemon_p = subparsers.add_parser("daemon", help="Run background daemon service")
    daemon_p.add_argument("--host", default=DEFAULT_HOST)
    daemon_p.add_argument("--port", type=int, default=DEFAULT_PORT)

    subparsers.add_parser("direct", help="Force in-process direct stdio without daemon")

    args = parser.parse_args()

    if args.command in ("daemon", "service"):
        run_daemon(host=args.host, port=args.port)
    elif args.command == "direct":
        mcp.run(transport="stdio")
    else:
        host = getattr(args, "host", DEFAULT_HOST)
        port = getattr(args, "port", DEFAULT_PORT)
        run_stdio(host=host, port=port)


if __name__ == "__main__":
    main()
