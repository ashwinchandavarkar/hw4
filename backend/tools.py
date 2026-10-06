"""Tools and model wiring for the Campus Customs shopping agent.

Every tool reads the local `campus_customs.db` so the agent's answers stay
grounded in real price and inventory data. Each product a tool touches is
recorded on the run context (`ShopDeps`), and those products become the cards
shown on the website alongside the reply.

All model traffic is routed through the Portkey OpenAI-compatible gateway.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from openai import AsyncOpenAI
from pydantic_ai import RunContext
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openai import OpenAIProvider

import db
from config import DEFAULT_MODEL, PORTKEY_BASE_URL, PORTKEY_PROVIDER, require_portkey_key
from models import (
    CatalogueSearchResult,
    Product,
    ProductLookup,
    SizeAvailability,
    SizeStockResult,
)


@dataclass
class ShopDeps:
    """Per-request context passed to the agent and its tools.

    Carries who is chatting (name/email, if signed in), which product page the
    shopper is viewing (so "this"/"it" resolves), and collects the product_ids
    the agent surfaces so they can be shown on the website.
    """

    surfaced: list[str] = field(default_factory=list)
    customer_name: str | None = None
    customer_first_name: str | None = None
    customer_email: str | None = None
    current_product: "ProductLookup | None" = None

    def surface(self, product_ids: list[str]) -> None:
        for pid in product_ids:
            if pid not in self.surfaced:
                self.surfaced.append(pid)


def build_model() -> OpenAIChatModel:
    """Return a PydanticAI model whose requests are routed through Portkey."""
    client = AsyncOpenAI(
        api_key=require_portkey_key(),
        base_url=PORTKEY_BASE_URL,
        default_headers={"x-portkey-provider": PORTKEY_PROVIDER},
    )
    return OpenAIChatModel(DEFAULT_MODEL, provider=OpenAIProvider(openai_client=client))


def to_lookup(p: Product) -> ProductLookup:
    """Convert a DB product into the grounded facts the agent consumes."""
    return ProductLookup(
        product_id=p.product_id,
        name=p.name,
        garment_type=p.garment_type,
        description=p.description,
        price=p.price,
        colors=p.colors,
        sizes=[
            SizeAvailability(size=s.size, quantity=s.quantity, available=s.quantity > 0)
            for s in p.inventory
        ],
        total_stock=p.total_stock,
        in_stock=p.in_stock,
    )


# ----- Tools (registered on the agent in agent.py) -----

def search_catalogue(
    ctx: RunContext[ShopDeps],
    query: str,
    garment_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    max_results: int = 12,
) -> CatalogueSearchResult:
    """Search the Campus Customs catalogue for products and return their real
    descriptions, prices, and per-size stock from the database. Put product
    attributes (color, team, college, garment, occasion) in `query`; use
    `min_price`/`max_price` for price limits and `garment_type` to restrict the
    category — do NOT put prices or words like "under" in `query`. The products
    returned here are shown to the shopper on the page, so search for the items
    worth showing them. Use this for any question about what we carry or price."""
    products = db.list_products(
        search=query or None,
        garment_type=garment_type,
        min_price=min_price,
        max_price=max_price,
        limit=max(1, min(max_results, 24)),
    )
    ctx.deps.surface([p.product_id for p in products])
    return CatalogueSearchResult(
        query=query,
        count=len(products),
        products=[to_lookup(p) for p in products],
    )


def get_product_details(ctx: RunContext[ShopDeps], product_id: str) -> ProductLookup | str:
    """Return the full grounded facts for one product_id: description, price,
    and stock for every size. Use this to confirm a product's price or overall
    availability before quoting them."""
    product = db.get_product(product_id)
    if not product:
        return f"No product with id '{product_id}'."
    ctx.deps.surface([product.product_id])
    return to_lookup(product)


def check_size_availability(
    ctx: RunContext[ShopDeps], product_id: str, size: str
) -> SizeStockResult | str:
    """Check whether a specific size of a product is in stock, reading the real
    inventory quantity. Use this whenever the customer asks about a particular
    size. If that size is out of stock, the result says so explicitly."""
    product = db.get_product(product_id)
    if not product:
        return f"No product with id '{product_id}'."
    ctx.deps.surface([product.product_id])
    want = size.strip().upper()
    match = next((s for s in product.inventory if s.size.upper() == want), None)
    if match is None:
        sizes = ", ".join(s.size for s in product.inventory) or "none"
        return SizeStockResult(
            product_id=product.product_id, name=product.name, size=size,
            price=product.price, quantity=0, available=False,
            message=f"{product.name} is not offered in size {size}. "
                    f"Available sizes: {sizes}.",
        )
    available = match.quantity > 0
    if available:
        message = (f"{product.name} in size {match.size} is in stock "
                   f"({match.quantity} available) at ${product.price:.2f}.")
    else:
        message = (f"Sorry — {product.name} in size {match.size} is currently "
                   f"OUT OF STOCK.")
    return SizeStockResult(
        product_id=product.product_id, name=product.name, size=match.size,
        price=product.price, quantity=match.quantity, available=available,
        message=message,
    )


def list_garment_types(ctx: RunContext[ShopDeps]) -> list[str]:
    """List the garment types Campus Customs carries."""
    return db.garment_types()


AGENT_TOOLS = [
    search_catalogue,
    get_product_details,
    check_size_availability,
    list_garment_types,
]
