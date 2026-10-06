"""Pydantic schemas shared by the API, the agent tools, and the frontend."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, EmailStr, Field, model_validator


class SizeStock(BaseModel):
    """Inventory for a single size of a product."""

    size: str
    quantity: int


class Product(BaseModel):
    """A catalogue product with price, inventory, and a servable image URL."""

    product_id: str
    name: str
    garment_type: str
    description: str
    colors: list[str] = Field(default_factory=list)
    search_tags: list[str] = Field(default_factory=list)
    image_url: str
    price: float
    inventory: list[SizeStock] = Field(default_factory=list)
    total_stock: int = 0

    @property
    def in_stock(self) -> bool:
        return self.total_stock > 0


# ----- Agent database-lookup result types -----
# These are the structured values the agent's tools return. They carry the
# grounded facts (description, price, per-size stock) the agent must rely on
# instead of guessing, and nothing else — no image URLs or search tags, which
# the model doesn't need to answer price/inventory questions.

class SizeAvailability(BaseModel):
    """Stock for one size, with an explicit availability flag."""

    size: str
    quantity: int               # units on hand for this size
    available: bool             # True when quantity > 0 (so the model can't misread 0)


class ProductLookup(BaseModel):
    """Grounded product facts returned by the catalogue/details tools."""

    product_id: str             # stable id, used to reference or fetch the product
    name: str                   # product name to quote back to the shopper
    garment_type: str           # category (hoodie, crewneck, quarter-zip, ...)
    description: str            # catalogue description, for accurate answers
    price: float                # authoritative price in USD — never invented
    colors: list[str] = Field(default_factory=list)
    sizes: list[SizeAvailability] = Field(default_factory=list)  # per-size stock
    total_stock: int = 0        # sum across sizes; 0 means fully out of stock
    in_stock: bool = False      # convenience flag for "is anything available"


class CatalogueSearchResult(BaseModel):
    """What `search_catalogue` returns: the matches and how many there were."""

    query: str
    count: int
    products: list[ProductLookup] = Field(default_factory=list)


class SizeStockResult(BaseModel):
    """What `check_size_availability` returns for a specific product + size."""

    product_id: str
    name: str
    size: str
    price: float
    quantity: int               # units of the requested size
    available: bool             # True only if that specific size is in stock
    message: str                # human-readable verdict, incl. an out-of-stock notice


# ----- Auth -----

class SignupRequest(BaseModel):
    first_name: str = Field(min_length=1, max_length=80)
    last_name: str = Field(min_length=1, max_length=80)
    email: EmailStr
    password: str = Field(min_length=8, max_length=256)
    confirm_password: str = Field(min_length=8, max_length=256)

    @model_validator(mode="after")
    def _passwords_match(self) -> "SignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class PublicUser(BaseModel):
    id: int
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    name: str
    email: str


class AuthResponse(BaseModel):
    token: str
    user: PublicUser


# ----- Chat -----

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    history: list[ChatMessage] = Field(default_factory=list)
    # Page context: the product the shopper is currently viewing, if any, so the
    # agent can resolve "this"/"it" to a specific product.
    current_product_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    products: list[Product] = Field(default_factory=list)


class ChatHistoryTurn(BaseModel):
    """One persisted chat turn, replayed when a logged-in shopper returns."""

    role: str
    content: str
    products: list[Product] = Field(default_factory=list)


class AuditEntry(BaseModel):
    """One appended record of agent-loop activity (see output/audit_trail.json)."""

    timestamp: str                 # ISO-8601 UTC time of the run
    iteration: int                 # step index within the agent loop
    customer: str                  # "guest" or the signed-in shopper's name
    tool_name: Optional[str] = None  # tool called this step; None for the final step
    arguments: str = ""            # brief, truncated tool arguments
    result_summary: str = ""       # brief, truncated tool result or final reply
    stop_reason: Optional[str] = None  # why the loop ended, on the final entry
