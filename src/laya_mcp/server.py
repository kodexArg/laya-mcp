"""Model Context Protocol (MCP) server definitions."""

from __future__ import annotations

from typing import Annotated, Any

from mcp.server.mcpserver import MCPServer
from pydantic import Field
from starlette.requests import Request
from starlette.responses import JSONResponse

from laya_mcp.engine import (
    decide_choice,
    decide_noul,
    decide_score,
    get_health,
)

mcp = MCPServer(
    name="laya-mcp",
    version="0.1.0",
    instructions="Fast System 1 typed decision routing via local GPU acceleration using Laya.",
)


@mcp.custom_route("/health", methods=["GET"])
async def route_health(request: Request) -> JSONResponse:
    """HTTP health probe for monitoring and daemon check."""
    return JSONResponse(get_health())


@mcp.tool(
    name="laya_choice",
    description="Categorical routing and discrete decision making. Returns chosen category, probabilities, confidence, and action.",
)
def tool_laya_choice(
    state: Annotated[
        Any,
        Field(description="The context, document, email, or text to classify."),
    ],
    instructions: Annotated[
        str,
        Field(
            description="Clear decision question, e.g., 'What department should handle this ticket?'"
        ),
    ],
    criteria: Annotated[
        dict[str, str],
        Field(
            description="Dictionary mapping each category name to its description or criteria."
        ),
    ],
    model: Annotated[
        str | None,
        Field(
            description="Optional checkpoint override (e.g. 'english' or 'multilingual')."
        ),
    ] = None,
) -> dict[str, Any]:
    return decide_choice(
        state=state, instructions=instructions, criteria=criteria, model=model
    )


@mcp.tool(
    name="laya_score",
    description="Numeric evaluation and matching against criteria. Returns scores for each criterion.",
)
def tool_laya_score(
    state: Annotated[
        Any,
        Field(description="The context or text to evaluate."),
    ],
    instructions: Annotated[
        str,
        Field(description="Scoring question or prompt."),
    ],
    criteria: Annotated[
        list[str],
        Field(
            description="List of criteria statements to score against the state."
        ),
    ],
    model: Annotated[
        str | None,
        Field(description="Optional checkpoint override."),
    ] = None,
) -> dict[str, Any]:
    return decide_score(
        state=state, instructions=instructions, criteria=criteria, model=model
    )


@mcp.tool(
    name="laya_noul",
    description="Fast binary or continuous scalar probabilistic check (sentiment, risk, churn, urgency). Returns scalar confidence 0.0-1.0.",
)
def tool_laya_noul(
    state: Annotated[
        Any,
        Field(description="The context or text to evaluate."),
    ],
    instructions: Annotated[
        str,
        Field(
            description="Binary / scalar question, e.g., 'Does the user threaten to cancel or churn?'"
        ),
    ],
    model: Annotated[
        str | None,
        Field(description="Optional checkpoint override."),
    ] = None,
) -> dict[str, Any]:
    return decide_noul(state=state, instructions=instructions, model=model)


@mcp.tool(
    name="laya_health",
    description="Returns device status, GPU model, CUDA availability, and loaded model checkpoints.",
)
def tool_laya_health() -> dict[str, Any]:
    return get_health()
