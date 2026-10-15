# Grocery Tracker: development brief

Read this whole file before doing anything. The visual design rules are in `docs/DESIGN.md`; read that before touching any component or CSS.

> **Stack change, 15 October 2026.** The owner switched the front end from Jinja + HTMX to **React**. FastAPI is now a JSON API. The data model, business rules and build order are unchanged; only the presentation layer moved. Where `docs/DESIGN.md` or a GitHub issue still mentions Jinja, HTMX or `app/static/app.css`, this file wins.

## 1. What we are building

A single-user, mobile-first web app that stops unplanned grocery trips and impulse spending.

- NFC stickers on the fridge, pantry and cleaning cupboard open a page showing what is in that place, with a stock status per item (plenty, low, out).
- After shopping, the owner logs the trip (store, date, items with prices). Saving the trip records the spend and restocks home in one step.
- A dashboard shows this month's spend, trips this week, and what is running low.

The owner is Voshana, in Melbourne, Australia, shopping at Woolworths, Coles and Aldi, using an iPhone (Safari). Currency is AUD. Time zone is `Australia/Melbourne`.

**Iteration 1 deadline: Wednesday 21 October 2026.** Milestone "Iteration 1 MVP" on GitHub.

## 2. Working agreement (read carefully)

The owner is learning software engineering through this project. Speed matters, but understanding matters more. The owner knows Python well and is **new to JavaScript and React**.

1. **One GitHub issue at a time, in order** (section 10). Read the issue first: `gh issue view <n>`. Its "Done when" checklist is the acceptance criteria (read "page" as "React page + API endpoint" where the issue predates the stack change).
2. **One branch per issue**: `feature/<n>-<short-name>`, created from an up-to-date `main`.
3. **Before writing code, post a short plan**: which files you will create or change and why. Wait for a "go".
4. **Claude writes all the code; the owner reviews it.** Review checkpoints: in #8, stop after the backend half (tests green, endpoint visible in `/docs`) for review before starting the frontend. From #9 on, the owner reviews once per issue, in the pull request.
5. **Explain all the code**, Python included, in plain English: after each chunk of work, a short walkthrough in chat of what every new file and function does and any new concept. For React, relate ideas to Python where it helps (a component is a function that returns UI; props are arguments; state is a variable that redraws the screen when it changes; `useEffect` runs code after the screen is drawn). Every PR description also has a "New concepts" section.
6. **Small commits** with clear messages ("Add InventoryItem model"). Never commit `.env`, `*.db`, `.venv/`, `__pycache__/`, `node_modules/` or `frontend/dist/`.
7. **Finish each issue** with the checks in section 11, a manual check in the browser at 390 px and 412 px wide (iPhone and common Android widths), then a pull request whose description says `Closes #<n>` and lists what to test on the phones. The owner merges with "Squash and merge".
8. **Never** push to `main` directly, delete branches, change Railway settings, or add a dependency (Python or npm) without saying why first.
9. If something in this brief seems wrong or conflicts with an issue, stop and ask. Do not silently change scope.

## 3. Tech stack (decided; do not swap)

### Backend (`backend/`)

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.13 | Pinned in `.python-version`; Ruff `target-version = "py313"` |
| Web framework | FastAPI + Uvicorn | JSON API only, every route under `/api` |
| Request/response shapes | Pydantic models in `schemas.py` | Every route declares `response_model`; never return table objects directly |
| ORM | SQLModel | The owner chose the ORM over raw SQL |
| Database | SQLite locally (`grocery.db`), PostgreSQL on Railway | Same code; only `DATABASE_URL` changes |
| Postgres driver | `psycopg[binary]` | Rewrite `postgres://` or `postgresql://` to `postgresql+psycopg://` in `config.py` |
| Settings | `python-dotenv`, `.env` file | `.env.example` lists every variable |
| Passwords | `bcrypt` package (hashpw / checkpw) | Do not use passlib (unmaintained, breaks with new bcrypt) |
| Sessions | Starlette `SessionMiddleware` (needs `itsdangerous`) | Signed, HTTP-only cookie, `same_site="lax"`, 30-day `max_age` |
| Tests | pytest + FastAPI `TestClient` (needs `httpx`), in-memory SQLite | |
| Lint/format | Ruff (config in `pyproject.toml`) | Dev dependency only |

Runtime packages go in `backend/requirements.txt`; dev-only tools (ruff, pytest, httpx) go in `backend/requirements-dev.txt`. Add a package only in the issue that first needs it.

### Frontend (`frontend/`)

| Layer | Choice | Notes |
|---|---|---|
| Runtime | Node.js, current LTS | Pinned in `frontend/.nvmrc`; only needed to develop and build, not on the iPhone |
| Build tool | Vite, created with the `react` template | Dev server on port 5173 with hot reload |
| UI library | React | Function components and hooks only; no class components |
| Language | **Plain JavaScript (JSX), not TypeScript** | Keeps the new material small for the owner. TypeScript is backlog |
| Routing | React Router 8 (`react-router` package) | URLs in section 9 |
| Data fetching | Built-in `fetch`, wrapped once in `src/api/client.js` | No axios, no React Query, no Redux in iteration 1 |
| Styling | Plain CSS: `src/styles/tokens.css` (the `:root` tokens from `docs/DESIGN.md`) + `src/styles/app.css` | **No Tailwind, no CSS-in-JS, no component library.** Components use the variables, never raw hex |
| Fonts | Google Fonts: Bricolage Grotesque (600, 700) and Figtree (400, 500, 600, 700) | Linked in `index.html` |
| Lint | oxlint, as set up by the Vite template (it replaced ESLint) | `npm run lint` |

### Hosting

| What | Choice |
|---|---|
| Platform | Railway, auto-deploys `main`, one service plus Railway Postgres |
| Build | A multi-stage `Dockerfile` at the repo root: stage 1 (Node) runs `npm ci && npm run build` in `frontend/`; stage 2 (Python) installs the backend and copies `frontend/dist` in |
| Start command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` from `backend/` |
| Serving React | In production FastAPI serves the built files, and any non-`/api` path returns `index.html` so React Router can handle it (this is what makes `/t/fridge` work when an NFC tag is tapped). Front end and API share one domain, so **no CORS setup is needed** |

## 4. Architecture rules

```
iPhone Safari ──▶ React (pages, components) ──fetch /api/...──▶ FastAPI routes ──▶ services ──▶ SQLModel ──▶ database
```

### Backend: three layers, kept separate

- **Routes** (`backend/app/routes/`): read the request, call a service, return a Pydantic schema. No business rules, no SQL. Raise `HTTPException` for 404 and similar.
- **Services** (`backend/app/services/`): plain Python functions holding the business rules. Take a `Session` and plain values; return model objects or simple data. **Never import FastAPI, Request or anything HTTP.** These are the functions the tests target.
- **Schemas** (`backend/app/schemas.py`): Pydantic classes for request bodies and responses (e.g. `LocationOut`, `InventoryItemOut`, `StatusUpdate`, `TripCreate`). They are the contract between the back end and the front end.

### Frontend

- **Pages** (`frontend/src/pages/`): one component per route; fetch data, hold state, handle loading and error.
- **Components** (`frontend/src/components/`): reusable pieces from `docs/DESIGN.md` section 3 (StatusControl, StatusBadge, BottomNav, Card, ErrorBanner, WeekRow, LocationTile, EmptyState...). They receive data through props and do not fetch.
- **API client** (`frontend/src/api/client.js`): the only place that calls `fetch`. Sends `credentials: "include"`, parses JSON, throws a readable error for non-2xx responses, and on **401** sends the user to `/login?next=<current path>`, except for `/api/auth/*` calls, where the 401 is returned to the page (so the login form can show "Username or password is incorrect" and the login page does not redirect to itself).
- **Formatting** (`frontend/src/lib/format.js`): `formatMoney(cents)` → `$4.50`, plus the date formats from `docs/DESIGN.md` section 5 (use `Intl.DateTimeFormat("en-AU", { timeZone: "Australia/Melbourne", ... })`). No other file formats money or dates.
- **Routing**: React Router's declarative style (`<BrowserRouter><Routes><Route .../>`), not loaders or framework mode. Pages fetch in `useEffect`.
- **Errors**: the error `client.js` throws carries `status`, so a page can check `err.status === 404` (e.g. "This tag isn't set up") and show the error banner for anything else. While a page loads it shows plain "Loading…" text.
- No business rules in React. React may check a form before sending it, for quick feedback, but **the API is the source of truth** and validates everything again.

### Shared rules

- Get the database session with FastAPI dependency injection: `session: Session = Depends(get_session)`.
- Money is always **integer cents** in the database and in JSON (`"price_cents": 450`). The trip form sends cents: React converts the typed "4.50" with a helper that does not use floating-point maths (split on the dot). The helper rejects anything that is not digits with at most 2 decimal places (`4.555`, `abc`, `-1`, empty) and React shows a field error; the API only ever sees cents, so this check cannot happen anywhere else.
- Never store a value that can be calculated (no `total` column on trips; the API calculates totals and includes them in responses).
- Dates in JSON are ISO strings: `"2026-10-15"` for dates, timezone-aware UTC for timestamps. "Today", "this week" and "this month" are calculated **in the API** in `Australia/Melbourne` with `zoneinfo`. A week runs **Monday to Sunday**.
- Error responses are JSON: `{"detail": "..."}` for simple errors; validation errors use FastAPI's standard 422 shape, which React maps to inline field errors.
- SQL logging: `create_engine(..., echo=settings.SQL_ECHO)`; `SQL_ECHO=true` locally (the owner wants to see the SQL), false in production.

## 5. Project structure

The current skeleton (`app/` at the repo root) moves into `backend/` as part of issue #8.

```
backend/
  app/
    main.py            # creates app, lifespan creates tables, SessionMiddleware, includes routers, serves frontend/dist in production
    config.py          # reads .env: DATABASE_URL, SECRET_KEY, SQL_ECHO, ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_DISPLAY_NAME
    database.py        # engine, create_db_and_tables(), get_session()
    models.py          # the 7 SQLModel tables
    schemas.py         # Pydantic request/response shapes
    auth.py            # hash/verify password, require_login dependency
    seed.py            # python -m app.seed : locations, categories, owner user (idempotent)
    services/
      inventory.py     # get_location_with_items, set_status, add_item, low_and_out_items
      trips.py         # create_trip (with restock), list_trips, get_trip, trip_total_cents
      spending.py      # month_summary, week_summary
    routes/
      auth.py  dashboard.py  locations.py  inventory.py  products.py  trips.py  spending.py
  tests/
    conftest.py        # in-memory SQLite engine, session and TestClient fixtures
    test_inventory.py  test_trips.py  test_spending.py  test_auth.py
  requirements.txt  requirements-dev.txt  pyproject.toml  .env.example  .python-version
frontend/
  index.html  vite.config.js  package.json  .nvmrc
  src/
    main.jsx           # mounts <App/> and the router
    App.jsx            # route table (section 9)
    api/client.js
    lib/format.js
    pages/             # DashboardPage, LocationPage, AddItemPage, TripFormPage, TripSavedPage, TripsPage, TripDetailPage, SpendingPage, LoginPage, NotFoundPage
    components/
    styles/tokens.css  styles/app.css
docs/
  DESIGN.md  database-diagram.png  mvp-plan.pdf  vision.pdf
Dockerfile  .gitignore  README.md  CLAUDE.md
```

## 6. Data model (7 tables)

Matches `docs/database-diagram.png`, except `User.display_name`, added after the diagram was drawn. Table names are SQLModel defaults (lowercase class name).

| Table | Fields | Rules |
|---|---|---|
| `User` | id, username (unique), display_name, password_hash | One row in iteration 1. `display_name` (required) is the name in the greeting and account button, seeded from `ADMIN_DISPLAY_NAME`. `seed.py` refuses an `ADMIN_PASSWORD` shorter than 12 characters |
| `Location` | id, name, slug (unique, indexed) | Seeded: Fridge/`fridge`, Pantry/`pantry`, Cleaning cupboard/`cleaning`. Slugs never change (they are written on the NFC tags) |
| `Category` | id, name (unique) | Seeded, in this order: Fruit & veg, Meat & seafood, Dairy & eggs, Pantry staples, Snacks & drinks, Toiletries, Cleaning, Other |
| `Product` | id, name, category_id → Category, default_location_id → Location, image_url (nullable), created_at | Look up by case-insensitive name before creating, to avoid duplicates |
| `InventoryItem` | id, product_id → Product, location_id → Location, status (enum plenty/low/out), quantity (nullable), unit (nullable), updated_at | **Unique (product_id, location_id)**. quantity/unit stay empty this iteration (exact amounts are backlog) |
| `ShoppingTrip` | id, store, trip_date, notes (nullable), created_at | store ∈ Woolworths, Coles, Aldi, Other |
| `TripItem` | id, trip_id → ShoppingTrip, product_id → Product, location_id → Location, price_cents (int ≥ 0), quantity_bought (int ≥ 1, default 1) | location_id is where it went **this time** (may differ from the product's default) |

Timestamps are timezone-aware UTC (`datetime.now(timezone.utc)` via `default_factory`).

## 7. Business rules (must have backend tests)

1. **Saving a trip restocks home.** In ONE transaction: create the trip and its items; for each item, find the InventoryItem for (product, trip item's location), create it if missing, set status `plenty` and `updated_at` now. If anything fails, nothing is saved.
2. **Trip total** = sum of `price_cents × quantity_bought` over its items. Calculated, never stored; included in trip responses as `total_cents`.
3. **Monthly spend** for a calendar month (Melbourne time): total cents, number of trips, and total per category (via the product's category). Categories with zero spend are omitted. A month with no trips returns zero and an empty list (the page shows an empty state).
4. **Trips this week**: count and total for Monday–Sunday of the current Melbourne week, plus which weekdays had a trip (for the dashboard's 7-day row).
5. **Low and out**: every InventoryItem whose status is `low` or `out`, grouped by location, ordered out first, then low, then product name.
6. **Validation on the trip form**: store required; date required; at least one item; every item needs a product name and a price in cents ≥ 0. The API rejects bad input with **422** and field-level errors (which row, which field). React keeps every typed row in state, so nothing is lost on error, shows an error banner ("1 item needs a price before saving") and highlights the field.
7. **Login**: every `/api` route except `POST /api/auth/login` and `GET /api/health` requires a logged-in session and returns **401** otherwise. React's API client turns a 401 (from any non-auth route) into a redirect to `/login?next=<path>` and returns there after login. Sessions last 30 days so tag taps do not ask to log in. A wrong password returns 401 with "Username or password is incorrect" (never say which part).

## 8. API endpoints

All JSON. All under `/api`. Interactive docs at `http://127.0.0.1:8000/docs` while developing.

| Method and path | Purpose | Issue |
|---|---|---|
| `GET /api/health` | `{"status": "ok"}`, no login | done (move to `/api/health` in #8) |
| `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` | Single-user login; `me` returns `username` and `display_name`, or 401 | #16 |
| `GET /api/locations` | The 3 locations (`name`, `slug`) for the add-item form; #14 adds low/out counts for the dashboard tiles | #10, #14 |
| `GET /api/locations/{slug}` | `{"name", "slug", "items": [{"id", "name", "category", "status"}]}`, items sorted by product name; 404 for an unknown slug | #8 |
| `PATCH /api/inventory/{id}` | Body `{"status": "low"}`; returns the updated item | #9 |
| `GET /api/categories` | For the category selects | #10 |
| `GET /api/products?search=` | Existing products (`id`, `name`, `category_id`) for suggestions (`<datalist>`) and category auto-fill; `search` matches part of the name, ignoring capitals | #10 |
| `POST /api/items` | Body `{product_name, category_id, location_slug, status}`. Reuses the Product by name (ignoring capitals) or creates it; adds it to the location. **If it is already in that location, its status is updated instead** (owner's choice). Unknown category or location: 422 on that field | #10 |
| `POST /api/trips` | Log a trip (rules 1 and 6); returns the saved trip with `total_cents` | #11, #12 |
| `GET /api/trips/{id}` | One trip with its items and `total_cents` (the Trip saved page uses it after a reload) | #11 |
| `GET /api/trips` | Trips list, newest first (same day: latest logged first): `id`, `store`, `trip_date`, `item_count`, `total_cents`, counted and summed in one SQL query | #13 |
| `GET /api/dashboard` | Month spend, trips this week (rule 4), low and out items (rule 5) | #14 |
| `GET /api/spending?month=YYYY-MM` | Monthly spend by category (rule 3); defaults to the current month | #15 |

## 9. Frontend routes (React Router)

| URL | Page | Notes |
|---|---|---|
| `/` | Dashboard | Bottom nav, Home active |
| `/t/:slug` | Location page | **The URL written on the NFC tags; never change it.** Unknown slug → "This tag isn't set up" |
| `/items/new?location=<slug>` | Add item | Location pre-selected from the query string |
| `/trips/new` | Log a trip | "Add another item" adds a row to React state (no server call) |
| `/trips/:id/saved` | Trip saved confirmation | |
| `/trips`, `/trips/:id` | Trips list and detail | Bottom nav, Trips active on the list |
| `/spending?month=YYYY-MM` | Spending | Bottom nav, Spending active |
| `/login?next=` | Login | No bottom nav |
| anything else | Not found | Link home |

Status changes on the location page update the screen immediately and send the PATCH; if the PATCH fails, put the old status back and show the error banner.

## 10. Build order (GitHub issues)

Work in this order; each issue's checklist on GitHub is the acceptance criteria. Each feature is built as a **vertical slice**: model → service → test → endpoint → React page.

1. **#8 Location page**, one PR built in two halves (convert the existing branch in place):
   - *Backend half*: move the code, `.env`, `pyproject.toml`, requirements files and `.python-version` into `backend/`; recreate `.venv` and `grocery.db` there. Set the `/api` prefix once in `main.py` (`app.include_router(router, prefix="/api")`); health moves to `/api/health`; remove the `/` route and the `/static` mount. Delete the Jinja leftovers (`app/templating.py`, `app/templates/`, `app/static/`). `GET /api/locations/{slug}` with schema. Tests: service tests for `list_location_items` (right items, name order, only that location) plus two client tests (JSON shape, unknown slug 404s). Add `seed_samples.py`. **Stop for the owner's review.**
   - *Frontend half*: Node 24 LTS via `nvm`, pinned in `frontend/.nvmrc`. Vite `react` template with its demo files removed, the dev proxy (section 12), `tokens.css`, `api/client.js`, React Router, and `LocationPage` from the Fridge mockup (sorted out → low → plenty on load; see `docs/DESIGN.md`).
2. **#9 Status buttons**: `set_status` service and test, `PATCH /api/inventory/{id}`, `StatusControl` component.
3. **#10 Add item**: categories and product-suggestion endpoints, `POST /api/items`, `AddItemPage` with location pre-filled from `?location=`.
4. **#11 Log a trip**: `TripCreate` schema, validation (rule 6), `TripFormPage` with add-row, remove-row, discard confirm, price-to-cents helper (`lib/format.js`). The Trip saved page was pulled forward into #11.
5. **#12 Restock**: rule 1 inside `create_trip` (it already saves in one transaction); tests for new item, existing item set back to plenty, and rollback (done: `set_stock` is shared with add item). Adds the "Every item is now marked Plenty at home." line to the Trip saved page.
6. **#13 Trips list and detail.**
7. **#14 Dashboard**: `GET /api/locations` counts and `GET /api/dashboard`; month spend, week row, location tiles, "Buy next time" list.
8. **#15 Spending page**: rule 3, month navigation, empty state; tests for totals.
9. **#16 Login**: rule 7; `User.display_name`; `SessionMiddleware`; `seed.py` creates the owner from `ADMIN_USERNAME`/`ADMIN_PASSWORD`; tests for 401 and wrong password; `LoginPage` and 401 redirect in the API client.
10. **#17 Deploy with Postgres**: `Dockerfile`, FastAPI serving `frontend/dist` with the `index.html` fallback, Railway Postgres, variables (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_*`, `SQL_ECHO=false`), run seed, check every page on the iPhone, including a real tag tap. Guide the owner through the Railway dashboard; do not change Railway yourself.
11. **#18 Real-trip test and retro**: help the owner file bugs as issues with a `bug` label.

## 11. Commands

Two terminals while developing.

```bash
# Terminal 1: API on http://127.0.0.1:8000  (docs at /docs)
cd backend
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed                 # safe to run repeatedly
uvicorn app.main:app --reload

# Terminal 2: React on http://localhost:5173
cd frontend
npm install
npm run dev
```

Checks before every pull request:

```bash
cd backend && ruff check . && ruff format --check . && pytest
cd frontend && npm run lint && npm run build
```

To test on the iPhone before deploying: run `npm run dev -- --host` and open the Mac's local IP on port 5173 on the same Wi-Fi, or `ngrok http 5173`.

## 12. Dev proxy (why there is no CORS)

In development, `vite.config.js` proxies `/api` to `http://127.0.0.1:8000`. The browser only ever talks to port 5173, so the session cookie and API calls are same-origin, exactly like production. Do not add `CORSMiddleware`; if a CORS error appears, the proxy is misconfigured.

## 13. Out of scope for iteration 1

Do not build these, even partially: receipt scanning, barcodes or calories, product photos, Open Food Facts lookup, exact quantities, recipes, discounts or price history, AI summaries, multiple users, native app, payments, **TypeScript, Tailwind, Redux or other state libraries, React Query, offline/PWA support, frontend unit tests** (business rules are tested in the backend). Also **rate limiting on login** (backlog issue for the next iteration; a 12+ character password covers iteration 1). Most are backlog issues #19–#29. If the owner asks for one mid-iteration, remind them it is backlog and ask whether to swap it in for something else.

## 14. Definition of done (every issue)

- Every checkbox on the GitHub issue is met.
- Works on iPhone Safari and Android Chrome (390 px and 412 px wide), matching `docs/DESIGN.md`. See `PRODUCT.md` for who the app is for.
- Every new endpoint has a `response_model` and appears correctly in `/docs`.
- Business rules touched by the issue have passing backend tests.
- `ruff check .`, `pytest`, `npm run lint` and `npm run build` pass.
- PR opened with `Closes #<n>`, a short summary and phone test steps (iPhone and Android).
