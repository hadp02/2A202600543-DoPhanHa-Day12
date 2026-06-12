"""A2A delegation helper.

Provides `delegate(endpoint, question, context_id, trace_id, depth)` which
sends a message to another A2A agent and returns the text response.
"""

from __future__ import annotations

import logging
from uuid import uuid4
import time
from datetime import datetime, timezone

from agents.common.tracing_client import fire_and_forget_trace_event

import httpx

from a2a.client import A2AClient
from a2a.types import (
    AgentCard,
    Message,
    MessageSendParams,
    Part,
    Role,
    SendMessageRequest,
    TextPart,
)

logger = logging.getLogger(__name__)


async def delegate(
    endpoint: str,
    question: str,
    context_id: str,
    trace_id: str,
    depth: int,
    caller_name: str = "unknown",
) -> str:
    """Send a question to an A2A agent and return the text response."""
    async with httpx.AsyncClient(timeout=300.0) as http_client:
        card_url = f"{endpoint}/.well-known/agent.json"
        card_resp = await http_client.get(card_url)
        card_resp.raise_for_status()
        agent_card = AgentCard.model_validate(card_resp.json())

        client = A2AClient(httpx_client=http_client, agent_card=agent_card)

        message = Message(
            role=Role.user,
            parts=[Part(root=TextPart(text=question))],
            message_id=str(uuid4()),
            context_id=context_id,
            metadata={
                "trace_id": trace_id,
                "context_id": context_id,
                "delegation_depth": depth,
            },
        )

        request = SendMessageRequest(
            id=str(uuid4()),
            params=MessageSendParams(message=message),
        )

        callee_name = agent_card.name if agent_card else endpoint

        start_time = time.time()
        timestamp_start = datetime.now(timezone.utc).isoformat()
        fire_and_forget_trace_event(trace_id, caller_name, callee_name, "started", 0.0, timestamp_start, question)

        response = await client.send_message(request)
        latency = time.time() - start_time

        text = _extract_text(response)

        timestamp_end = datetime.now(timezone.utc).isoformat()
        fire_and_forget_trace_event(trace_id, caller_name, callee_name, "completed", latency, timestamp_end, text)

        return text


def _extract_text(response: object) -> str:
    """Walk the response tree and collect all TextPart.text values."""
    text = ""
    if hasattr(response, "root"):
        response = response.root

    result = getattr(response, "result", None)
    if result is None:
        return text

    artifacts = getattr(result, "artifacts", None)
    if artifacts:
        for artifact in artifacts:
            parts = getattr(artifact, "parts", []) or []
            for part in parts:
                text += _part_text(part)
        if text:
            return text

    parts = getattr(result, "parts", None)
    if parts:
        for part in parts:
            text += _part_text(part)

    if not text:
        history = getattr(result, "history", None)
        if history:
            for msg in history:
                msg_parts = getattr(msg, "parts", []) or []
                for part in msg_parts:
                    text += _part_text(part)

    return text


def _part_text(part: object) -> str:
    """Extract text from a Part object."""
    inner = getattr(part, "root", part)
    return getattr(inner, "text", "") or ""
