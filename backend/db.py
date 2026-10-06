"""Read/light-write access to the local campus_customs.db SQLite database.

The catalogue and inventory are read-only for the storefront; only the
`users` table is written (account creation). All product price and stock
information served to shoppers and to the agent comes straight from here, so
answers stay grounded in real data.
"""
from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from typing import Iterator, Optional

from config import DB_PATH
from models import Product, SizeStock


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def _json_list(value: str | None) -> list[str]:
    if not value:
        return []
    try:
        parsed = json.loads(value)
        if isinstance(parsed, list):
            return [str(x) for x in parsed]
    except (json.JSONDecodeError, TypeError):
        pass
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _image_url(image_file_path: str) -> str:
    """Map a stored path like 'products/foo.jpg' to the served media URL."""
    name = image_file_path.replace("\\", "/").split("/")[-1]
    return f"/media/products/{name}"


def _row_to_product(row: sqlite3.Row, inventory: list[SizeStock]) -> Product:
    return Product(
        product_id=row["product_id"],
        name=row["name"],
        garment_type=row["garment_type"],
        description=row["description"],
        colors=_json_list(row["colors"]),
        search_tags=_json_list(row["search_tags"]),
        image_url=_image_url(row["image_file_path"]),
        price=float(row["price"]),
        inventory=inventory,
        total_stock=sum(s.quantity for s in inventory),
    )


def _inventory_for(conn: sqlite3.Connection, product_ids: list[str]) -> dict[str, list[SizeStock]]:
    if not product_ids:
        return {}
    placeholders = ",".join("?" for _ in product_ids)
    order = "CASE size WHEN 'XS' THEN 0 WHEN 'S' THEN 1 WHEN 'M' THEN 2 " \
            "WHEN 'L' THEN 3 WHEN 'XL' THEN 4 WHEN 'XXL' THEN 5 ELSE 6 END"
    rows = conn.execute(
        f"SELECT product_id, size, quantity FROM inventory "
        f"WHERE product_id IN ({placeholders}) ORDER BY product_id, {order}",
        product_ids,
    ).fetchall()
    out: dict[str, list[SizeStock]] = {}
    for r in rows:
        out.setdefault(r["product_id"], []).append(
            SizeStock(size=r["size"], quantity=r["quantity"])
        )
    return out


# Tokens that carry no product meaning; ignored during search so a stray word
# (e.g. a price phrase the model included) doesn't wipe out all matches.
_STOPWORDS = {
    "a", "an", "the", "and", "or", "for", "with", "in", "of", "to", "me",
    "show", "find", "want", "need", "some", "any", "please", "yale",
    "under", "below", "over", "above", "less", "more", "than", "cheap",
    "cheapest", "price", "priced", "around", "about", "between",
}


# Map common shopper phrasings/misspellings to the catalogue's wording. Each key
# is normalized to one or more canonical variants that actually appear in the
# product text, so e.g. "hoody" and "tshirt" still find products.
_SYNONYMS: dict[str, list[str]] = {
    "hoody": ["hoodie"], "hoodies": ["hoodie"], "hooded": ["hoodie"],
    "tshirt": ["t-shirt"], "tshirts": ["t-shirt"], "tee": ["t-shirt"],
    "tees": ["t-shirt"], "teeshirt": ["t-shirt"],
    "sweater": ["sweatshirt", "sweater"], "sweaters": ["sweatshirt"],
    "jumper": ["sweatshirt"], "crew": ["crewneck"], "crews": ["crewneck"],
    "quarterzip": ["quarter-zip"], "quarter-zip": ["quarter-zip"],
    "1/4": ["quarter-zip", "1/4"], "qtr": ["quarter-zip"],
    "fullzip": ["full-zip"], "jackets": ["jacket"], "longsleeve": ["long sleeve"],
    "pullovers": ["pullover"], "grey": ["gray"],
}


def _token_variants(token: str) -> list[str]:
    """Return the search variants for one token (synonyms + gentle plural)."""
    if token in _SYNONYMS:
        return _SYNONYMS[token]
    variants = {token}
    # Gentle singularization so "hoodies"/"crewnecks" match "hoodie"/"crewneck".
    if len(token) > 3 and token.endswith("s"):
        variants.add(token[:-1])
    return list(variants)


def _meaningful_tokens(text: str) -> list[str]:
    tokens: list[str] = []
    for raw in text.lower().split():
        token = raw.strip("$.,!?()[]")
        # Drop stopwords, pure numbers, and currency amounts like "$75".
        if not token or token in _STOPWORDS or token.replace(".", "").isdigit():
            continue
        tokens.append(token)
    return tokens


def list_products(
    search: str | None = None,
    garment_type: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    limit: int = 500,
) -> list[Product]:
    """Return catalogue products, optionally filtered by text, type, or price."""
    clauses: list[str] = []
    params: list[object] = []
    if search:
        # Tokenize: every meaningful word must appear in some searchable field
        # (AND across tokens, OR across fields). Matches queries like "grace
        # hopper crewneck" even when the words are not contiguous in the data.
        fields = "LOWER(name || ' ' || description || ' ' || search_tags " \
                 "|| ' ' || colors || ' ' || garment_type)"
        for token in _meaningful_tokens(search):
            # Each word must match at least one of its variants (synonym/plural).
            variants = _token_variants(token)
            ors = " OR ".join(f"{fields} LIKE ?" for _ in variants)
            clauses.append(f"({ors})")
            params.extend(f"%{v}%" for v in variants)
    if garment_type:
        clauses.append("LOWER(garment_type) LIKE ?")
        params.append(f"%{garment_type.lower()}%")
    if min_price is not None:
        clauses.append("price >= ?")
        params.append(min_price)
    if max_price is not None:
        clauses.append("price <= ?")
        params.append(max_price)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM catalogue {where} ORDER BY name LIMIT ?",
            [*params, limit],
        ).fetchall()
        inv = _inventory_for(conn, [r["product_id"] for r in rows])
        return [_row_to_product(r, inv.get(r["product_id"], [])) for r in rows]


def get_products_by_ids(product_ids: list[str]) -> list[Product]:
    if not product_ids:
        return []
    placeholders = ",".join("?" for _ in product_ids)
    with get_conn() as conn:
        rows = conn.execute(
            f"SELECT * FROM catalogue WHERE product_id IN ({placeholders})",
            product_ids,
        ).fetchall()
        inv = _inventory_for(conn, [r["product_id"] for r in rows])
        by_id = {r["product_id"]: _row_to_product(r, inv.get(r["product_id"], [])) for r in rows}
    # preserve requested order
    return [by_id[pid] for pid in product_ids if pid in by_id]


def get_product(product_id: str) -> Optional[Product]:
    found = get_products_by_ids([product_id])
    return found[0] if found else None


def garment_types() -> list[str]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT DISTINCT garment_type FROM catalogue ORDER BY garment_type"
        ).fetchall()
    return [r["garment_type"] for r in rows]


# ----- Users -----

def find_user_by_email(email: str) -> Optional[sqlite3.Row]:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)
        ).fetchone()


# ----- Chat history -----

def save_chat_message(
    user_id: int, role: str, content: str, products_json: str | None = None
) -> None:
    """Persist one chat turn for a logged-in user."""
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_messages (user_id, role, content, products_json) "
            "VALUES (?, ?, ?, ?)",
            (user_id, role, content, products_json),
        )


def get_chat_history(user_id: int, limit: int = 100) -> list[sqlite3.Row]:
    """Return a user's chat turns in chronological order (oldest first)."""
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT role, content, products_json, created_at FROM chat_messages "
            "WHERE user_id = ? ORDER BY id ASC LIMIT ?",
            (user_id, limit),
        ).fetchall()
    return rows


def create_user(
    first_name: str, last_name: str, email: str, password_hash: str
) -> sqlite3.Row:
    full_name = f"{first_name} {last_name}".strip()
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO users (name, email, password_hash, first_name, last_name) "
            "VALUES (?, ?, ?, ?, ?)",
            (full_name, email, password_hash, first_name, last_name),
        )
        user_id = cur.lastrowid
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
