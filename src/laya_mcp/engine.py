"""Core inference engine wrapping laya.Router."""

from __future__ import annotations

import os
import time
from typing import Any

import torch

LAYA_DEVICE = os.getenv("LAYA_DEVICE", "cuda" if torch.cuda.is_available() else "cpu")
LAYA_PRELOAD = [
    m.strip()
    for m in os.getenv("LAYA_PRELOAD", "english,multilingual").split(",")
    if m.strip()
]

_router = None


def get_router():
    """Returns the persistent singleton laya.Router."""
    global _router
    if _router is None:
        from laya import Router

        device = LAYA_DEVICE
        if device == "cuda" and not torch.cuda.is_available():
            device = "cpu"
        _router = Router(device=device, max_loaded=max(2, len(LAYA_PRELOAD)))
        _router.preload(LAYA_PRELOAD)
    return _router


def get_health() -> dict[str, Any]:
    """Inspects device status, CUDA availability, and loaded checkpoints."""
    gpu_name = None
    if torch.cuda.is_available():
        try:
            gpu_name = torch.cuda.get_device_name(0)
        except Exception:
            gpu_name = "Unknown CUDA Device"

    return {
        "status": "ok",
        "cuda": torch.cuda.is_available(),
        "device": LAYA_DEVICE,
        "preloaded": list(LAYA_PRELOAD),
        "torch": torch.__version__,
        "gpu_name": gpu_name,
        "router_loaded": _router is not None,
    }


def decide_choice(
    state: Any,
    instructions: str,
    criteria: dict[str, str],
    model: str | None = None,
) -> dict[str, Any]:
    """Executes a categorical discrete choice prediction."""
    router = get_router()
    questions = {
        "decision": {
            "type": "choice",
            "instructions": instructions,
            "criteria": criteria,
        }
    }
    kwargs: dict[str, Any] = {}
    if model:
        kwargs["model"] = model

    t0 = time.perf_counter()
    result = router.predict(state, questions, **kwargs)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    out = dict(result) if isinstance(result, dict) else {"result": result}
    out["meta"] = {
        "latency_ms": round(latency_ms, 2),
        "device": LAYA_DEVICE,
        "cuda_available": torch.cuda.is_available(),
    }
    return out


def decide_score(
    state: Any,
    instructions: str,
    criteria: list[str],
    model: str | None = None,
) -> dict[str, Any]:
    """Executes a scoring prediction against criteria."""
    router = get_router()
    questions = {
        "decision": {
            "type": "score",
            "instructions": instructions,
            "criteria": criteria,
        }
    }
    kwargs: dict[str, Any] = {}
    if model:
        kwargs["model"] = model

    t0 = time.perf_counter()
    result = router.predict(state, questions, **kwargs)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    out = dict(result) if isinstance(result, dict) else {"result": result}
    out["meta"] = {
        "latency_ms": round(latency_ms, 2),
        "device": LAYA_DEVICE,
        "cuda_available": torch.cuda.is_available(),
    }
    return out


def decide_noul(
    state: Any,
    instructions: str,
    model: str | None = None,
) -> dict[str, Any]:
    """Executes a binary or continuous scalar probabilistic prediction."""
    router = get_router()
    questions = {
        "decision": {
            "type": "noul",
            "instructions": instructions,
        }
    }
    kwargs: dict[str, Any] = {}
    if model:
        kwargs["model"] = model

    t0 = time.perf_counter()
    result = router.predict(state, questions, **kwargs)
    latency_ms = (time.perf_counter() - t0) * 1000.0

    out = dict(result) if isinstance(result, dict) else {"result": result}
    out["meta"] = {
        "latency_ms": round(latency_ms, 2),
        "device": LAYA_DEVICE,
        "cuda_available": torch.cuda.is_available(),
    }
    return out
