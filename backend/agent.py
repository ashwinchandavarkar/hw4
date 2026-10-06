"""PydanticAI shopping agent entry point and wiring.

The agent loads its system prompt from `prompts/prompt.md`, talks to
`gpt-5.6-luna` through Portkey (see `tools.build_model`), and is given the
database-backed tools in `tools.AGENT_TOOLS`. `run_chat` is the single entry the
FastAPI `/api/chat` endpoint calls per turn.
"""
from __future__ import annotations

from functools import lru_cache

from pydantic_ai import Agent, RunContext
from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    UserPromptPart,
)

import audit
import db
from config import PROMPT_PATH
from models import ChatMessage, Product, ProductLookup
from tools import AGENT_TOOLS, ShopDeps, build_model


@lru_cache(maxsize=1)
def _system_prompt() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


@lru_cache(maxsize=1)
def get_agent() -> Agent[ShopDeps, str]:
    """Build (once) and return the configured shopping agent."""
    agent = Agent(
        build_model(),
        deps_type=ShopDeps,
        system_prompt=_system_prompt(),
        tools=AGENT_TOOLS,
        retries=2,
    )

    @agent.system_prompt
    def _runtime_context(ctx: RunContext[ShopDeps]) -> str:
        """Per-turn context: who is chatting and what they're viewing."""
        d = ctx.deps
        parts: list[str] = []
        if d.customer_name:
            who = d.customer_name
            if d.customer_email:
                who += f" ({d.customer_email})"
            first = d.customer_first_name or d.customer_name.split()[0]
            parts.append(
                f"You are chatting with {who}, a signed-in customer. Their first "
                f"name is {first}; greet them by it when natural. Never reveal "
                f"their password or data about other customers."
            )
        else:
            parts.append("You are chatting with a guest (not signed in).")
        if d.current_product:
            p = d.current_product
            sizes = ", ".join(
                f"{s.size} ({'in stock' if s.available else 'out of stock'})"
                for s in p.sizes
            )
            parts.append(
                f"The shopper is currently on the product page for "
                f'"{p.name}" (product_id: {p.product_id}), ${p.price:.2f}, '
                f"colors: {', '.join(p.colors) or 'n/a'}; sizes: {sizes}. "
                f"If they say 'this', 'this one', or 'it', they mean this product."
            )
        return "\n".join(parts)

    return agent


def _to_history(history: list[ChatMessage]) -> list[ModelMessage]:
    """Convert prior turns into PydanticAI message history."""
    messages: list[ModelMessage] = []
    for m in history[-12:]:
        if m.role == "user":
            messages.append(ModelRequest(parts=[UserPromptPart(content=m.content)]))
        elif m.role == "assistant":
            messages.append(ModelResponse(parts=[TextPart(content=m.content)]))
    return messages


async def run_chat(
    message: str,
    history: list[ChatMessage],
    *,
    customer_name: str | None = None,
    customer_first_name: str | None = None,
    customer_email: str | None = None,
    current_product: ProductLookup | None = None,
) -> tuple[str, list[Product]]:
    """Run one chat turn; return (reply_text, products_to_display).

    `customer_*` identify the signed-in shopper (if any) and `current_product`
    is the product page they are viewing, both exposed to the agent via deps.
    """
    deps = ShopDeps(
        customer_name=customer_name,
        customer_first_name=customer_first_name,
        customer_email=customer_email,
        current_product=current_product,
    )
    result = await get_agent().run(
        message,
        deps=deps,
        message_history=_to_history(history),
    )
    products = db.get_products_by_ids(deps.surfaced)

    # Append to the audit trail (never overwrites prior runs).
    try:
        audit.append_entries(
            audit.entries_from_run(result, customer=customer_name or "guest")
        )
    except Exception:
        # Auditing must never break a chat response.
        pass

    return result.output, products[:12]
