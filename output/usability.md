# Campus Customs — usability improvements

Four improvements (two front-end, two agent/backend). All are functional in the
running app.

## Front-end

### FE1 — "Add to Bag" with size selection + live cart
**What was added.** The single-product page now has a size picker (only in-stock
sizes are selectable, sold-out sizes are disabled) and an **Add to Bag** button.
A **Bag** item in the top nav shows a live count badge, and a `/cart` page lists
the chosen items (image, name, size, price, quantity), lets the shopper remove
lines, and shows the order total. The bag persists in `localStorage`, so it
survives navigation and refreshes.

**Why it helps.** Browsing merchandise without a way to collect items is a dead
end. A real add-to-bag flow with size selection moves shoppers toward purchase,
prevents picking a sold-out size, and the persistent bag means a shopper can
keep browsing (or come back) without losing their picks — the core of any store.

### FE2 — Sort and "In stock only" controls on the Products page
**What was added.** The Products page gained a **Sort** dropdown (Featured,
Price: low→high, Price: high→low, Name A–Z) and an **In stock only** toggle,
applied instantly to the grid alongside the existing search and type filter.

**Why it helps.** With 100+ products, shoppers want to shop by budget and skip
items they can't buy. Sorting by price and hiding out-of-stock items makes the
catalogue far faster to navigate and reduces the frustration of clicking into a
product that turns out to be unavailable.

## Agent / backend

### BE1 — Safety guardrail (safer, and cheaper/faster)
**What was added.** `/api/chat` runs a fast pre-check (`backend/guardrails.py`)
before calling the model. Messages that try to extract credentials, other
customers' data, or to override the assistant's instructions (prompt injection)
get a safe, canned reply and **never reach the LLM**.

**Why it helps.** It protects customer data (the users table holds password
hashes and emails) by refusing exfiltration attempts deterministically rather
than relying only on the prompt. Because these messages short-circuit before the
model call, they also cost nothing and respond instantly — safer for shoppers
and cheaper for the business.

### BE2 — Typo- and synonym-tolerant catalogue search (more accurate)
**What was added.** The catalogue search normalizes each query word through a
synonym/variant map and a gentle plural rule, so shopper phrasing matches the
catalogue's wording: `hoody`/`hoodies` → hoodie, `tshirt`/`tee`/`tees` →
t-shirt, `sweater` → sweatshirt, `quarterzip`/`1/4 zip`/`quarter zip` →
quarter-zip, `jumper` → sweatshirt, and similar. Each word matches any of its
variants across all product fields.

**Why it helps.** Shoppers rarely type the exact catalogue term. Previously
"hoody" or "tshirt" could return nothing; now the agent (and the on-page search)
find the right products, so answers are accurate and the shopper sees relevant
gear instead of an empty result.
