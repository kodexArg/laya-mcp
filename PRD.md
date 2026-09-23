# Product Requirements Document (PRD) — laya-mcp

## Overview

`laya-mcp` is a Linux service that activates and exposes a Model Context Protocol (MCP) server capable of running `laya` on a local GPU for fast System 1 inferences.

## Purpose & Scope

The service provides a standardized, low-latency MCP interface over stdio (with background daemon management) for local LLMs, AI agents, and IDEs. It allows agents to offload fast categorical routing, scoring, and binary decisions directly to local tensor accelerators without overhead.

## Core Capabilities

- **Local GPU Inference**: Leverages local CUDA acceleration to execute `laya` models.
- **Model Context Protocol (MCP)**: Exposes standard MCP tools for choice, scoring, and binary validation (`noul`).
- **System Integration**: Operates as an enabled, persistent Linux user service that manages model residency and provides instant stdio communication for connected clients.
