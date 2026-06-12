"""Shared LLM factory for all agents.

When OPENROUTER_API_KEY is set → uses OpenRouter (real LLM).
When OPENROUTER_API_KEY is empty → uses a mock ChatModel that returns
canned legal responses, so the full A2A pipeline still works without an API key.
"""

import os
import logging
from typing import Any, List, Optional

logger = logging.getLogger(__name__)


def get_llm():
    """Return a ChatModel — real or mock depending on env."""
    api_key = os.getenv("OPENROUTER_API_KEY", "")

    if api_key:
        from langchain_openai import ChatOpenAI
        logger.info("Using OpenRouter LLM: %s", os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash"))
        return ChatOpenAI(
            model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash"),
            openai_api_key=api_key,
            openai_api_base="https://openrouter.ai/api/v1",
            temperature=0.3,
        )
    else:
        logger.warning("OPENROUTER_API_KEY not set — using MockLegalLLM")
        return _MockLegalLLM()


# ---------------------------------------------------------------------------
# Mock LLM — used when no API key is configured
# ---------------------------------------------------------------------------

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatResult, ChatGeneration


class _MockLegalLLM(BaseChatModel):
    """A mock ChatModel that returns canned legal responses.

    This allows the full multi-agent pipeline to function without
    an external API key — perfect for development and testing.
    """

    model_name: str = "mock-legal-llm"

    @property
    def _llm_type(self) -> str:
        return "mock-legal-llm"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        # Get the last human message to determine response
        last_msg = messages[-1].content.lower() if messages else ""
        response = self._pick_response(last_msg)
        return ChatResult(generations=[ChatGeneration(message=AIMessage(content=response))])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> ChatResult:
        return self._generate(messages, stop, **kwargs)

    @staticmethod
    def _pick_response(question: str) -> str:
        """Return a contextual mock response based on keywords."""

        # Routing-style JSON responses (for Law Agent's check_routing node)
        if "needs_tax" in question and "needs_compliance" in question:
            return '{"needs_tax": true, "needs_compliance": true}'

        if any(kw in question for kw in ["tax", "irs", "thuế", "evasion"]):
            return (
                "[Mock Tax Analysis] Under IRC §§ 6651-6663, tax evasion carries "
                "severe penalties including fines up to $250,000 and imprisonment "
                "up to 5 years. The IRS Criminal Investigation division handles "
                "referrals. Civil penalties include accuracy-related penalties (20%) "
                "and fraud penalties (75%). Officers and directors may face personal "
                "liability under the responsible person doctrine."
            )

        if any(kw in question for kw in ["compliance", "sec", "sox", "regulatory", "fcpa", "aml"]):
            return (
                "[Mock Compliance Analysis] Regulatory violations can trigger "
                "SEC enforcement actions, including cease-and-desist orders, "
                "civil monetary penalties, and disgorgement. SOX violations "
                "carry criminal penalties up to $5M in fines and 20 years "
                "imprisonment. Companies should implement robust compliance "
                "programs as mitigating factors per DOJ guidelines."
            )

        if any(kw in question for kw in ["contract", "breach", "liability", "law", "legal"]):
            return (
                "[Mock Legal Analysis] A breach of contract exposes the breaching "
                "party to compensatory damages, consequential damages (if foreseeable), "
                "and potentially punitive damages in cases of fraud or bad faith. "
                "The non-breaching party may seek specific performance or rescission. "
                "Under the Uniform Commercial Code (UCC), additional remedies include "
                "cover and market price differential damages."
            )

        # Aggregation/synthesis responses
        if "synthesi" in question or "combine" in question or "cohesive" in question:
            return (
                "[Mock Synthesized Analysis] Based on the multi-agent analysis:\n\n"
                "## Legal Implications\n"
                "Contract breaches carry significant civil liability including "
                "compensatory and consequential damages.\n\n"
                "## Tax Consequences\n"
                "Tax evasion triggers both civil penalties (20-75% of underpayment) "
                "and potential criminal prosecution.\n\n"
                "## Regulatory Exposure\n"
                "Regulatory violations may result in SEC enforcement, fines, "
                "and executive personal liability.\n\n"
                "*This analysis is for educational purposes only.*"
            )

        # Default legal response
        return (
            "[Mock Agent Response] This is a simulated response from the Legal "
            "Multi-Agent System. The system routes questions through specialist "
            "agents (Law, Tax, Compliance) for comprehensive analysis. "
            "Set OPENROUTER_API_KEY to enable real LLM responses."
        )
