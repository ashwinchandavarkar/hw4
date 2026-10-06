"""Campus Customs FastAPI backend — run with `uvicorn main:app --reload --port 8000`.

Routes:
  GET  /api/health
  GET  /api/products            list / search catalogue (price + inventory)
  GET  /api/products/{id}       single product
  GET  /api/garment-types       distinct garment types (for filters)
  POST /api/auth/signup         create an account
  POST /api/auth/login          log in
  GET  /api/auth/me             current user (Bearer token)
  POST /api/chat                talk to the PydanticAI shopping agent
  GET  /media/products/...      product images (served from local data dir)
"""
from __future__ import annotations

import json
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

import audit
import auth
import db
import guardrails
from agent import run_chat
from config import PRODUCTS_DIR
from models import (
    AuthResponse,
    ChatHistoryTurn,
    ChatRequest,
    ChatResponse,
    LoginRequest,
    Product,
    PublicUser,
    SignupRequest,
)
from tools import to_lookup

app = FastAPI(title="Campus Customs API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve product images from the local (gitignored) data directory.
if PRODUCTS_DIR.exists():
    app.mount("/media/products", StaticFiles(directory=PRODUCTS_DIR), name="products")


def _public_user(row) -> PublicUser:
    keys = row.keys()
    return PublicUser(
        id=row["id"],
        first_name=row["first_name"] if "first_name" in keys else None,
        last_name=row["last_name"] if "last_name" in keys else None,
        name=row["name"],
        email=row["email"],
    )


def current_user(request: Request) -> Optional[dict]:
    header = request.headers.get("Authorization", "")
    if not header.lower().startswith("bearer "):
        return None
    uid = auth.read_token(header[7:].strip())
    if uid is None:
        return None
    with db.get_conn() as conn:
        row = conn.execute("SELECT * FROM users WHERE id = ?", (uid,)).fetchone()
    return dict(row) if row else None


def require_user(request: Request) -> dict:
    user = current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return user


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/products", response_model=list[Product])
def products(
    search: Optional[str] = Query(default=None),
    garment_type: Optional[str] = Query(default=None),
    limit: int = Query(default=500, ge=1, le=1000),
) -> list[Product]:
    return db.list_products(search=search, garment_type=garment_type, limit=limit)


@app.get("/api/products/{product_id}", response_model=Product)
def product(product_id: str) -> Product:
    found = db.get_product(product_id)
    if not found:
        raise HTTPException(status_code=404, detail="Product not found")
    return found


@app.get("/api/garment-types", response_model=list[str])
def garment_types() -> list[str]:
    return db.garment_types()


@app.post("/api/auth/signup", response_model=AuthResponse)
def signup(body: SignupRequest) -> AuthResponse:
    if db.find_user_by_email(body.email):
        raise HTTPException(status_code=409, detail="An account with that email already exists.")
    password_hash = auth.hash_password(body.password)
    row = db.create_user(body.first_name, body.last_name, body.email, password_hash)
    user = _public_user(row)
    return AuthResponse(token=auth.issue_token(user.id), user=user)


@app.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest) -> AuthResponse:
    row = db.find_user_by_email(body.email)
    if not row or not auth.verify_password(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")
    user = _public_user(row)
    return AuthResponse(token=auth.issue_token(user.id), user=user)


@app.get("/api/auth/me", response_model=PublicUser)
def me(user: dict = Depends(require_user)) -> PublicUser:
    return PublicUser(
        id=user["id"],
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        name=user["name"],
        email=user["email"],
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(body: ChatRequest, request: Request) -> ChatResponse:
    user = current_user(request)  # None for guests

    # Safety guardrail: block credential/other-user/prompt-injection requests
    # before any model call (safer and cheaper). Still persisted for a signed-in
    # user so their history stays complete.
    safe = guardrails.check_message(body.message)
    if safe is not None:
        audit.log_simple(
            customer=(user["name"] if user else "guest"),
            note="blocked message (credentials / other-user data / injection)",
            stop_reason="blocked_by_guardrail",
        )
        if user:
            db.save_chat_message(user["id"], "user", body.message, None)
            db.save_chat_message(user["id"], "assistant", safe, None)
        return ChatResponse(reply=safe, products=[])

    # Page context: which product the shopper is currently viewing.
    current_product = None
    if body.current_product_id:
        product = db.get_product(body.current_product_id)
        if product:
            current_product = to_lookup(product)

    reply, matched = await run_chat(
        body.message,
        body.history,
        customer_name=(user["name"] if user else None),
        customer_first_name=(user.get("first_name") if user else None),
        customer_email=(user["email"] if user else None),
        current_product=current_product,
    )

    # Persist history only for logged-in users; guests are not saved.
    if user:
        db.save_chat_message(user["id"], "user", body.message, None)
        products_json = json.dumps([p.model_dump() for p in matched]) if matched else None
        db.save_chat_message(user["id"], "assistant", reply, products_json)

    return ChatResponse(reply=reply, products=matched)


@app.get("/api/chat/history", response_model=list[ChatHistoryTurn])
def chat_history(user: dict = Depends(require_user)) -> list[ChatHistoryTurn]:
    """Return the signed-in shopper's saved chat history, oldest first."""
    turns: list[ChatHistoryTurn] = []
    for row in db.get_chat_history(user["id"]):
        products: list[Product] = []
        if row["products_json"]:
            try:
                products = [Product(**p) for p in json.loads(row["products_json"])]
            except (json.JSONDecodeError, TypeError, ValueError):
                products = []
        turns.append(
            ChatHistoryTurn(role=row["role"], content=row["content"], products=products)
        )
    return turns
