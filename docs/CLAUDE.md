# Grocery Tracker: development brief

Read this whole file before doing anything. The visual design rules are in `docs/DESIGN.md`; read that before touching any template or CSS.

## 1. What we are building

A single-user, mobile-first web app that stops unplanned grocery trips and impulse spending.

- NFC stickers on the fridge, pantry and cleaning cupboard open a page showing what is in that place, with a stock status per item (plenty, low, out).
- After shopping, the owner logs the trip (store, date, items with prices). Saving the trip records the spend and restocks home in one step.
- A dashboard shows this month's spend, trips this week, and what is running low.

The owner is Voshana, in Melbourne, Australia, shopping at Woolworths, Coles and Aldi, using an iPhone (Safari). Currency is AUD. Time zone is `Australia/Melbourne`.

**Iteration 1 deadline: Wednesday 21 October 2026.** Milestone "Iteration 1 MVP" on GitHub.

## 2. Working agreement (read carefully)

The owner is learning software engineering through this project. Speed matters, but understanding matters more.

1. **One GitHub issue at a time, in order** (section 9). Read the issue first: `gh issue view <n>`. Its "Done when" checklist is the acceptance criteria.
2. **One branch per issue**: `feature/<n>-<short-name>`, created from an up-to-date `main`.
3. **Before writing code, post a short plan**: which files you will create or change and why. Wait for a "go".
4. **Learning mode**: for `app/models.py`, anything in `app/services/`, and tests, first ask: "Do you want to write this yourself, or should I?" If the owner writes it, review their code instead of rewriting it.
5. **Explain as you go** in plain English: what each new file does and any concept that is new (ORM session, dependency injection, HTMX swap, transaction, and so on). Keep explanations short.
6. **Small commits** with clear messages ("Add InventoryItem model"). Never commit `.env`, `*.db`, `.venv/` or `__pycache__/`.
7. **Finish each issue** with: `ruff check .`, `ruff format .`, `pytest`, a manual check in the browser, then open a pull request whose description says `Closes #<n>` and lists what to test on the iPhone. The owner merges with "Squash and merge".
8. **Never** push to `main` directly, delete branches, change Railway settings, or add a dependency without saying why first.
9. If something in this brief seems wrong or conflicts with an issue, stop and ask. Do not silently change scope.

## 3. Tech stack (decided; do not swap)

| Layer | Choice | Notes |
|---|---|---|
| Language | Python 3.13 | Pinned in `.python-version` |
| Web framework | FastAPI + Uvicorn | |
| Templates | Jinja2 (`fastapi.templating.Jinja2Templates`) | Server-side rendered HTML |
| Interactivity | HTMX 2 via `<script src="https://unpkg.com/htmx.org@2">` | No custom JavaScript unless unavoidable |
| Styling | One CSS file, `app/static/app.css`, built on CSS custom properties from `docs/DESIGN.md` | **No Tailwind in iteration 1**: all colours live as tokens in one file |
| Fonts | Google Fonts: Bricolage Grotesque (600, 700) and Figtree (400, 500, 600, 700) | |
| ORM | SQLModel | The owner chose the ORM over raw SQL |
| Database | SQLite locally (`grocery.db`), PostgreSQL on Railway | Same code; only `DATABASE_URL` changes |
| Postgres driver | `psycopg[binary]` | Rewrite `postgres://` or `postgresql://` to `postgresql+psycopg://` in `config.py` |
| Settings | `python-dotenv`, `.env` file | `.env.example` lists every variable |
| Passwords | `bcrypt` package (hashpw / checkpw) | Do not use passlib (unmaintained, breaks with new bcrypt) |
| Sessions | Starlette `SessionMiddleware` (needs `itsdangerous`) | Signed cookie, 30-day `max_age` |
| Tests | pytest + FastAPI `TestClient`, in-memory SQLite | |
| Lint/format | Ruff (config in `pyproject.toml`) | Dev dependency only |
| Hosting | Railway, auto-deploys `main` | Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT` (PORT=8080) |

Runtime packages go in `requirements.txt`; dev-only tools (ruff, pytest) go in `requirements-dev.txt`. Add a package only in the issue that first needs it.

## 4. Architecture rules

Three layers. Keep them separate; this is what lets a React front end replace the templates later.

- **Routes** (`app/routes/`): read the request, call a service, return a template or a redirect. No business rules, no SQL.
- **Services** (`app/services/`): plain Python functions holding the business rules. Take a `Session` and plain values; return model objects or simple data. **Never import Jinja, Request or anything HTML.**
- **Templates** (`app/templates/`): display only. No calculations beyond formatting.

Other rules:

- Get the database session with FastAPI dependency injection: `session: Session = Depends(get_session)`.
- HTMX endpoints return a **partial** template (`app/templates/partials/…`), not a whole page.
- Money is always **integer cents** (`price_cents = 450` for $4.50). Convert to dollars only in templates, with one shared Jinja filter `money` → `$4.50`.
- Never store a value that can be calculated (no `total` column on trips).
- Dates: `trip_date` is a plain `date` chosen by the user. "Today", "this week" and "this month" are calculated in `Australia/Melbourne` with `zoneinfo`. A week runs **Monday to Sunday**.
- SQL logging: `create_engine(..., echo=settings.SQL_ECHO)`; `SQL_ECHO=true` locally (the owner wants to see the SQL), false in production.

## 5. Project structure

```
app/
  main.py              # creates app, mounts static, includes routers, lifespan creates tables
  config.py            # reads .env: DATABASE_URL, SECRET_KEY, SQL_ECHO, ADMIN_USERNAME, ADMIN_PASSWORD
  database.py          # engine, create_db_and_tables(), get_session()
  models.py            # the 7 SQLModel tables
  auth.py              # hash/verify password, require_login dependency
  seed.py              # python -m app.seed : locations, categories, owner user (idempotent)
  services/
    inventory.py       # list_location_items, set_status, add_item, low_and_out_items
    trips.py           # create_trip (with restock), list_trips, get_trip, trip_total_cents
    spending.py        # month_summary, week_summary
  routes/
    auth.py  dashboard.py  locations.py  items.py  trips.py  spending.py
  templates/
    base.html          # head, fonts, app.css, htmx, bottom nav block
    partials/          # HTMX fragments, e.g. inventory_row.html, trip_item_row.html
    dashboard.html  location.html  item_form.html  trip_form.html  trip_detail.html
    trips.html  spending.html  login.html
  static/
    app.css
tests/
  conftest.py          # in-memory SQLite engine, session and TestClient fixtures
  test_inventory.py  test_trips.py  test_spending.py  test_auth.py
docs/
  DESIGN.md  database-diagram.png  mvp-plan.pdf  vision.pdf
```

## 6. Data model (7 tables)

Matches `docs/database-diagram.png`. Table names are SQLModel defaults (lowercase class name).

| Table | Fields | Rules |
|---|---|---|
| `User` | id, username (unique), password_hash | One row in iteration 1 |
| `Location` | id, name, slug (unique, indexed) | Seeded: Fridge/`fridge`, Pantry/`pantry`, Cleaning cupboard/`cleaning`. Slugs never change (they are written on the NFC tags) |
| `Category` | id, name (unique) | Seeded, in this order: Fruit & veg, Meat & seafood, Dairy & eggs, Pantry staples, Snacks & drinks, Toiletries, Cleaning, Other |
| `Product` | id, name, category_id → Category, default_location_id → Location, image_url (nullable), created_at | Look up by case-insensitive name before creating, to avoid duplicates |
| `InventoryItem` | id, product_id → Product, location_id → Location, status (enum plenty/low/out), quantity (nullable), unit (nullable), updated_at | **Unique (product_id, location_id)**. quantity/unit stay empty this iteration (exact amounts are backlog) |
| `ShoppingTrip` | id, store, trip_date, notes (nullable), created_at | store ∈ Woolworths, Coles, Aldi, Other |
| `TripItem` | id, trip_id → ShoppingTrip, product_id → Product, location_id → Location, price_cents (int ≥ 0), quantity_bought (int ≥ 1, default 1) | location_id is where it went **this time** (may differ from the product's default) |

Timestamps are timezone-aware UTC (`datetime.now(timezone.utc)` via `default_factory`).

## 7. Business rules (must have tests)

1. **Saving a trip restocks home.** In ONE transaction: create the trip and its items; for each item, find the InventoryItem for (product, trip item's location), create it if missing, set status `plenty` and `updated_at` now. If anything fails, nothing is saved.
2. **Trip total** = sum of `price_cents × quantity_bought` over its items. Calculated, never stored.
3. **Monthly spend** for a calendar month (Melbourne time): total cents, number of trips, and total per category (via the product's category). Categories with zero spend are omitted. A month with no trips returns zero and an empty list (the page shows an empty state).
4. **Trips this week**: count and total for Monday–Sunday of the current Melbourne week, plus which weekdays had a trip (for the dashboard's 7-day row).
5. **Low and out**: every InventoryItem whose status is `low` or `out`, grouped by location, ordered out first, then low, then product name.
6. **Validation on the trip form**: store required; date required; at least one item; every item needs a product name and a price that parses to ≥ 0 with at most 2 decimal places. On error, re-render the form **with every typed row kept**, an error banner ("1 item needs a price before saving") and the field highlighted.
7. **Login**: every page except `/login`, `/health` and static files requires a logged-in session; otherwise redirect to `/login?next=<path>` and return there after login. Sessions last 30 days so tag taps do not ask to log in. Wrong password shows "Username or password is incorrect" (never say which).

## 8. Pages and routes

| Route | Purpose | Issue |
|---|---|---|
| `GET /health` | `{"status": "ok"}`, no login | done |
| `GET /login`, `POST /login`, `POST /logout` | Single-user login | #16 |
| `GET /` | Dashboard | #14 (spend and week parts after #11) |
| `GET /t/{slug}` | Location page opened by the NFC tag; 404 page for unknown slug | #8 |
| `POST /inventory/{id}/status` | HTMX: set plenty/low/out, returns the updated row partial | #9 |
| `GET /items/new?location=<slug>`, `POST /items` | Add an item; location pre-selected when coming from a tag page | #10 |
| `GET /trips/new`, `POST /trips` | Log a trip; `GET /trips/new/row` returns one blank item row (HTMX) | #11, #12 |
| `GET /trips`, `GET /trips/{id}` | Trips list (newest first) and trip detail | #13 |
| `GET /spending?month=YYYY-MM` | Monthly spend by category, defaults to current month, previous/next month links | #15 |

Product name suggestions on the trip and item forms use a `<datalist>` of existing product names (no JavaScript).

## 9. Build order (GitHub issues)

Work in this order; each issue's checklist on GitHub is the acceptance criteria.

1. **#8 Location page**: `config.py`, `database.py`, `models.py`, `seed.py`, `base.html`, `app.css` tokens, `GET /t/{slug}`, `location.html` (from the Fridge design). Test: page lists seeded items; unknown slug 404s.
2. **#9 Status buttons**: HTMX segmented control; test the service.
3. **#10 Add item**: form with location pre-filled from `?location=`; creates Product (or reuses by name) and InventoryItem.
4. **#11 Log a trip**: trip form, HTMX add-row, validation rule 6, prices to cents.
5. **#12 Restock**: rule 1 inside `create_trip`; tests for new item, existing item set back to plenty, and rollback.
6. **#13 Trips list and detail.**
7. **#14 Dashboard**: month spend, week row, location tiles with counts, "Buy next time" list.
8. **#15 Spending page**: rule 3, month navigation, empty state; tests for totals.
9. **#16 Login**: rule 7; `seed.py` creates the owner from `ADMIN_USERNAME`/`ADMIN_PASSWORD`; tests for redirect and wrong password.
10. **#17 Deploy with Postgres**: add Railway Postgres, set variables (`DATABASE_URL`, `SECRET_KEY`, `ADMIN_*`, `SQL_ECHO=false`), run seed, check every page on the iPhone. Guide the owner through the Railway dashboard; do not change Railway yourself.
11. **#18 Real-trip test and retro**: help the owner file bugs as issues with a `bug` label.

## 10. Out of scope for iteration 1

Do not build these, even partially: receipt scanning, barcodes or calories, product photos, Open Food Facts lookup, exact quantities, recipes, discounts or price history, AI summaries, multiple users, React, native app, payments. They are backlog issues #19–#29. If the owner asks for one mid-iteration, remind them it is backlog and ask whether to swap it in for something else.

## 11. Commands

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
python -m app.seed                 # safe to run repeatedly
uvicorn app.main:app --reload      # http://127.0.0.1:8000
pytest
ruff check . && ruff format .
```

To test on the iPhone before deploying: `ngrok http 8000`.

## 12. Definition of done (every issue)

- Every checkbox on the GitHub issue is met.
- Works on iPhone Safari at 390 px wide, matching `docs/DESIGN.md`.
- Business rules touched by the issue have passing tests.
- `ruff check .` and `pytest` pass.
- PR opened with `Closes #<n>`, a short summary and iPhone test steps.
