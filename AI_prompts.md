# Campus Customs website — AI prompt log

This file logs the prompts given to the vibe coder while building the Campus
Customs customer website. Each problem is described in my own words (the full
assignment page and its URL are deliberately **not** pasted). There is one
section per problem, in the order the problems were worked; each has at least one
prompt, and a follow-up prompt with a one-line note on what was missing wherever
a follow-up was needed.

Evidence of completion is the running website, the database reads/writes it
performs, and the screenshots captured during the build — no separate proof
essay is included.

---

## Problem 1 — Project setup, data, and tech stack

### Prompt
> We're building a real customer website for Campus Customs, Yale's licensed
> spirit-wear shop. Use a React + Vite + TypeScript frontend and a Python
> FastAPI backend powered by a PydanticAI agent. Unzip the provided `data.zip`
> in the `HW 4` folder so the project has `data/campus_customs.db` (catalogue,
> inventory, and users tables, including the test user) and `data/products/`
> (the product images, whose paths match the catalogue table). Create a Python
> virtual environment inside the project, wire the agent's AI calls through the
> Portkey gateway using `PORTKEY_API_KEY` and the `gpt-5.6-luna` model, and
> scaffold the backend and frontend.

### Follow-up
> Confirm every `image_file_path` in the catalogue resolves to a real file in
> `data/products/`, and check the tables load.

*What was missing:* the first prompt set up the data but didn't verify the
catalogue→image paths were all present (result: 102/102 images, 0 missing).

---

## Problem 2 — Examine the database and start `output/harness.md`

### Prompt
> Open `data/campus_customs.db` and work out the fields in every table — at least
> `catalogue`, `inventory`, and `users`. Start `output/harness.md` and document
> each table and each field, and for every field add a brief note on why it's
> relevant to the Campus Customs shop or chatbot. Keep this harness file as the
> running spec and expand it in later problems with the models, tools, safety
> rules, and system design.

### Follow-up
*None needed* — a single schema introspection surfaced all four tables
(`catalogue`, `inventory`, `users`, and a `chat_messages` history table) with
their types, keys, and value ranges, which were documented directly.

---

## Problem 3 — Multi-page storefront frontend (React + Vite + TypeScript)

### Prompt
> Build the React + Vite + TypeScript frontend with a black-and-yellow Bulldog
> theme and a top navigation bar linking Home, Products, About Us, Log in, and
> Create account. Write Home and About Us copy in Campus Customs' voice (inspired
> by yalebulldogblue.com but in your own words, not copied). On the Products page,
> show each product's image (from the catalogue image paths), name, price, and a
> short description, and make each card open a dedicated single-product page with
> a large image, the full description, price, and available sizes/stock. Add a
> floating chat panel pinned to the bottom-right corner on every page. Keep a
> small FastAPI backend (`backend/main.py`) serving product info and images.

### Follow-up
> A chat/search for "grace hopper crewneck" returned nothing even though the
> product exists. Make the catalogue search tokenized — split the query into
> words and require each word to appear in some field — instead of matching the
> whole phrase contiguously.

*What was missing:* the first search matched the entire query as one substring,
so multi-word searches whose words aren't adjacent in the data failed.

---

## Problem 4 — Account creation and login

### Prompt
> Build a standard account creation and login flow. Signup collects first name,
> last name, email, password, and a password confirmation; login takes email and
> password. Store new accounts in the `users` table, and protect passwords so
> that neither a human nor an AI system can read them in plaintext — hash them
> with a salted one-way function and never store or return the raw password.
> Match the `pbkdf2_sha256$salt$hash` format already in the database. Use the
> existing test account (`test@campuscustoms.yale.edu` / `password`) while
> developing and verify both that it can log in and that a brand-new account can
> log in. Then update `output/harness.md` to explain how authentication works —
> what user info is stored and how passwords are protected.

### Follow-up
> The test account wouldn't log in because the stored `pbkdf2_sha256$salt$hash`
> format omits the iteration count. Using the provided test password, determine
> the iteration count the database was seeded with (it's 120,000), set that as
> the default so new accounts match, and have the verifier try that count first.

*What was missing:* the first build defaulted to the wrong PBKDF2 iteration count
(100,000), so the seeded test account failed to verify until the real count
(120,000) was identified and applied.

---

## Problem 5 — PydanticAI shop agent behind FastAPI (four-file structure)

### Prompt
> Build the shop chatbot as a PydanticAI agent behind FastAPI and connect it to
> the frontend chat widget. Put the FastAPI app in `backend/main.py` (the file run
> with `uvicorn main:app --reload --port 8000`) and organize the agent into four
> files beside it: `backend/prompts/prompt.md` (system prompt), `backend/agent.py`
> (entry point and wiring), `backend/tools.py` (the agent's tools), and
> `backend/models.py` (the Pydantic/PydanticAI types). Expose a `/api/chat`
> endpoint plus the product and auth endpoints. Route the model through Portkey to
> `gpt-5.6-luna` using the key from the course `.env`. Put the Campus Customs brand
> voice (from the yalebulldogblue.com research) and basic safety rules in the
> prompt file, add/update the chat-response and product-card types in `models.py`,
> and document in `output/harness.md` how the frontend talks to FastAPI and how
> the agent is initialized (prompt file + model).

### Follow-up
> A "quarter-zips under $75" query returned nothing even though many exist at $72,
> because the agent put the price phrase into the text search. Add `min_price` /
> `max_price` arguments to the search tool (filtered in the database), tell the
> agent to use them instead of writing prices into `query`, and ignore stray
> stopword/number tokens in the text search.

*What was missing:* the first build had only text search, so price constraints
expressed in words ("under $75") broke the query.

---

## Problem 6 — Database lookup tools (price, inventory, size-specific stock)

### Prompt
> Give the agent tools that retrieve real information from `campus_customs.db` —
> product descriptions, product prices, and inventory quantities, including
> size-specific stock when the customer asks about a particular size. Require the
> agent to use the database for these facts rather than making up prices or
> inventory, and if a requested size is out of stock, have it clearly tell the
> customer it's unavailable. Expand `prompts/prompt.md` to explain when the agent
> should use these tools for price and inventory questions, add or update the
> matching return types in `models.py`, and document each lookup tool in
> `output/harness.md`, explaining which fields the lookup-result models include
> and why.

### Follow-up
*None needed* — the structured tools (`search_catalogue` →
`CatalogueSearchResult`, `get_product_details` → `ProductLookup`,
`check_size_availability` → `SizeStockResult`) returned grounded facts on the
first build; verified that an out-of-stock size (Ice Hockey Hoodie in Medium) is
reported as unavailable and that prices/descriptions match the database.

---

## Problem 7 — Matching products appear on the page from the conversation

### Prompt
> As the shopper chats, the products the agent is talking about should appear on
> the page. Record every product the agent surfaces through its tools during a
> turn, then return those products (resolved to full records with image URL and
> live inventory) alongside the reply. Show them as clickable cards in the chat
> and surface them on the Products page so the display stays in sync with the
> conversation.

### Follow-up
*None needed* — surfacing tool-touched products and returning them with the reply
worked on the first pass (verified live across several chats).

---

## Problem 8 — Chat history, customer identity, and page context

### Prompt
> When a shopper is logged in, save their chat history in an appropriate database
> table and reload it when they return; guests can chat but their history is not
> saved. Make sure the agent knows which customer is chatting by passing their
> name and email through the agent dependencies, and pass enough page context
> that the agent knows which product the shopper is viewing — so on a product
> page, "Do you have this in pink?" resolves to that product. Document in
> `output/harness.md` how chat history is stored, which customer fields the agent
> sees, and how the current page/product context reaches the agent.

### Follow-up
> When asked "what's my first name?" the agent hedged because it only had the
> full name. Pass the customer's first name through deps as well and have the
> context prompt state it explicitly.

*What was missing:* the first build passed only the full name, so the agent was
unsure of the first name; adding `customer_first_name` to the deps fixed it
("Your first name is Test.").

---

## Problem 9 — Usability improvements (2 front-end, 2 agent/backend)

### Prompt
> Choose and implement two front-end usability improvements that make the site
> more attractive or easier to use, and two agent/backend improvements that make
> the agent more accurate, useful, safe, faster, or cheaper. Document each in
> `output/usability.md` (what was added and why it helps a Campus Customs shopper
> or the business), and make sure all four are actually visible/functional in the
> running app. I chose: (FE1) an "Add to Bag" flow with size selection, a nav bag
> badge, and a persistent cart page; (FE2) sort + "in stock only" controls on the
> Products page; (BE1) a pre-LLM safety guardrail that blocks credential /
> other-customer-data / prompt-injection messages with a safe canned reply; and
> (BE2) typo/synonym-tolerant catalogue search.

### Follow-up
*None needed* — all four were verified in the running app (cart badge + cart
page, sort/in-stock filter, guardrail returning a safe reply with no model call,
and "hoody"/"tshirt"/"1/4 zip" searches returning the right products).

---

## Problem 10 — Creative storefront design

### Prompt
> Add creative, imaginative design so the site feels like a genuine Campus
> Customs storefront rather than a generic layout — make thoughtful choices
> around fonts, colors, visual hierarchy, motion and interactions, product
> presentation, and the overall chat experience. Write a short, concrete summary
> in `output/design.md` explaining what changed and why it should encourage
> shoppers to stay and buy.

### Follow-up
*None needed* — added a collegiate Oswald/Archivo type system, a layered
black-and-gold palette with a reusable gold gradient, a larger animated hero,
card hover zoom with a "View details" reveal, gold-gradient buttons with a shine
sweep, and a personified chat ("Dan, your shop guide" with a bulldog avatar,
pulsing launcher, pop-in panel, animated typing dots, and quick-reply chips),
all verified in the running app and guarded by `prefers-reduced-motion`.

---

## Problem 11 — Live app check page (`output/app_check.html`)

### Prompt
> Test the live website and document it in `output/app_check.html`, a page that
> opens directly in a browser. Include clear screenshots with brief captions for
> three checks: (1) chat checking an item's inventory with accurate stock and
> price from the database, (2) dynamic product-search cards appearing after a
> category question like "hoodies", and (3) one of the Problem 9 usability
> improvements. Give each test its own heading, screenshot, and a one or two
> sentence explanation; store the images in `output/app_check_images/` and
> reference them with relative paths like `app_check_images/inventory.png`.

### Follow-up
*None needed* — captured the three screenshots from the running app, saved them
as PNGs under `output/app_check_images/`, and built the standalone page; verified
the HTML and all three images serve correctly via their relative paths.

---

## Problem 12 — Audit trail, safety rules, and complete harness doc

### Prompt
> Keep `output/audit_trail.json` as an append-only record of agent-loop activity
> — time, tool name, brief arguments/results, and stop reason — and never
> overwrite it between runs. Add appropriate safety rules to `prompts/prompt.md`.
> Complete `output/harness.md` so the whole system is clearly documented: the
> model fields in `models.py` and why they were chosen, the available tools and
> agent capabilities, the safety rules, and important specs like loop limits,
> result limits, the models used, and how to run the frontend and backend.

### Follow-up
*None needed* — added `backend/audit.py` (append-only writer that extracts
tool calls + a final stop-reason record from each run), wired it into `run_chat`
and the guardrail path, expanded the prompt's safety section to six rules, and
filled out harness.md §2/§4/§5/§6. Verified the trail accumulates across runs
(3 → 4 → 6 entries) without resetting.

---

## Problem 13 — Package the project and push to GitHub (final)

### Prompt
> Prepare the repository for submission following the file structure specified
> in the final problem. Write a README and a `.gitignore` that **excludes the
> database and the product images** (`data/`), keep secrets out of git via a
> `.env.example`, and give me exact `git` commands to create a public GitHub
> repository and push. I'll run the push and submit the repo URL on Canvas.

### Follow-up
*Pending the pasted file structure* — the final layout will be matched to the
structure the assignment specifies before the push commands are finalized.

---

## Appendix — yalebulldogblue.com research (context for Problem 5)

Research of the real store informed the agent's voice and product knowledge:
Campus Customs at 57 Broadway, New Haven, selling **licensed** Yale gear since
1973 (also *Yale Bulldog Blue* online); voice "casual comfort, classic Bulldog
pride" / "Big Pride, Big Yale"; catalogue across tees, crewnecks, hoodies,
quarter-zips, and jackets spanning the 14 residential colleges, 25+ sports,
relationship lines, classic marks (Handsome Dan, "Boola Boola", "Lux et
Veritas"), and "The Game" rivalry gear; sizes XS–XXL. These facts shape the
prompt; all prices and stock come from the database.
