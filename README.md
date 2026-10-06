# Campus Customs — customer website (HW 4)

A working storefront for **Campus Customs** (Yale Bulldog Blue), the officially
licensed Yale spirit-wear shop on Broadway in New Haven. Shoppers can browse the
catalogue, create an account, and chat with an AI assistant that pulls up
matching products with **accurate, database-grounded** prices and inventory.

- **Frontend:** React + Vite + TypeScript (black-and-gold Bulldog theme).
- **Backend:** Python FastAPI.
- **Agent:** PydanticAI, routed through the Portkey gateway to `gpt-5.6-luna`,
  with tools that read the local `campus_customs.db` so it never invents a price
  or a stock number.

## Project structure

```
hw4/
├── AI_prompts.md          # prompt log, one section per problem
├── requirements.txt       # Python backend dependencies
├── .env.example           # placeholder env values (copy to .env)
├── .gitignore
├── README.md
├── frontend/              # Vite + React + TypeScript app
├── backend/
│   ├── main.py            # FastAPI app — uvicorn main:app --reload --port 8000
│   ├── agent.py           # agent entry point & wiring
│   ├── tools.py           # agent tools (DB-backed)
│   ├── models.py          # Pydantic / PydanticAI types
│   ├── prompts/prompt.md  # system prompt (brand voice + safety rules)
│   └── db.py · auth.py · config.py · guardrails.py · audit.py
└── output/                # harness.md, design.md, usability.md,
                           # app_check.html, app_check_images/, audit_trail.json
```

## Local data pack (not in Git)

The provided `data/` folder is **excluded from Git** (see `.gitignore`). Before
running, place the data pack at the project root so you have:

```
hw4/
└── data/
    ├── campus_customs.db          # catalogue, inventory, users
    └── products/                  # product images referenced by the catalogue
```

(Unzip the provided `data.zip` into the project root to create this.)

## Setup

### 1. Environment key

Copy `.env.example` to `.env` in the project root and set your Portkey key:

```
PORTKEY_API_KEY=your-portkey-key-here
```

The real `.env` is never committed.

### 2. Backend (FastAPI + PydanticAI)

From the project root:

```powershell
py -3.12 -m venv backend\.venv
backend\.venv\Scripts\python -m pip install -r requirements.txt
```

Run the API from the `backend/` folder:

```powershell
cd backend
..\backend\.venv\Scripts\uvicorn main:app --reload --port 8000
```

or, equivalently, with the venv's Python:

```powershell
cd backend
.venv\Scripts\python -m uvicorn main:app --reload --port 8000
```

The backend reads `data/campus_customs.db` and serves product images from
`data/products/` at `/media/products/...`.

### 3. Frontend (React + Vite + TS)

From the project root:

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The Vite dev server proxies `/api` and `/media` to
the backend on port 8000.

## Using the site

- **Browse** products with search, garment-type filter, sort, and an
  "in stock only" toggle; click a card for the full product page.
- **Create an account** or **log in** (the seeded test account is
  `test@campuscustoms.yale.edu` / `password`).
- **Chat** via the bottom-right assistant ("Dan"): ask about hoodies, a
  residential college, a gift, a budget, or a specific size. Matching products
  appear as clickable cards. Logged-in shoppers' chat history is saved and
  reloaded on return.

## Documentation (`output/`)

- `harness.md` — full system spec: DB schema, model fields, tools, safety rules,
  limits, and how to run everything.
- `design.md` — creative design choices and why they encourage purchases.
- `usability.md` — the four usability improvements.
- `app_check.html` — live-test screenshots with captions (opens directly).
- `audit_trail.json` — append-only log of agent-loop activity.

## Project instructions honored

- Portkey + `gpt-5.6-luna` for all agent AI calls.
- Python virtual environment lives inside the project (`backend/.venv`).
- Black-and-gold (yellow) theme throughout.
- The database and product images are **not** committed.
