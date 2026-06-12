import logging
import os
import httpx
import asyncio

logger = logging.getLogger(__name__)

REGISTRY_URL = os.getenv("REGISTRY_URL", "http://localhost:10000")

async def send_trace_event(trace_id: str, caller: str, callee: str, status: str, latency: float, timestamp: str, content: str = "") -> None:
    """Send a trace event to the Registry."""
    trace_data = {
        "trace_id": trace_id,
        "caller": caller,
        "callee": callee,
        "status": status,
        "latency": latency,
        "timestamp": timestamp,
        "content": content
    }
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(f"{REGISTRY_URL}/trace", json=trace_data)
    except Exception as e:
        logger.warning("Failed to send trace data to registry: %s", e)

def fire_and_forget_trace_event(trace_id: str, caller: str, callee: str, status: str, latency: float, timestamp: str, content: str = ""):
    """Wrapper to run send_trace_event asynchronously without awaiting it."""
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(send_trace_event(trace_id, caller, callee, status, latency, timestamp, content))
    except RuntimeError:
        asyncio.run(send_trace_event(trace_id, caller, callee, status, latency, timestamp, content))
