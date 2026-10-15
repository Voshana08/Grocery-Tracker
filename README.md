# Grocery Tracker

A single-user, mobile-first web app that stops unplanned grocery trips and impulse spending.

NFC stickers on the fridge, pantry and cleaning cupboard open a page showing what's in that
place, with a stock status per item (plenty, low, out). After shopping, logging the trip
records the spend and restocks home in one step. A dashboard shows this month's spend, trips
this week, and what's running low.

The second iteration will suggest recipes from the ingredients you have at home.

See `CLAUDE.md` for the full development brief and `docs/DESIGN.md` for the visual design
spec — both are the source of truth for how this app is built.

## Tech stack

- Python 3.13, FastAPI + Uvicorn
- Jinja2 templates, HTMX for interactivity, plain CSS (no framework)
- SQLModel, SQLite locally / PostgreSQL in production
- Ruff for lint/format, pytest for tests

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env

python -m app.seed                 # seed locations and categories (safe to re-run)
uvicorn app.main:app --reload      # http://127.0.0.1:8000
```

## Development

```bash
pytest                             # run tests
ruff check . && ruff format .      # lint and format
```

## Project structure

```
app/
  main.py          # app setup, static files, routers
  config.py        # reads .env
  database.py      # engine, session, table creation
  models.py        # SQLModel tables
  seed.py          # python -m app.seed
  services/        # business logic
  routes/          # FastAPI routers
  templates/        # Jinja2 templates
  static/          # app.css
tests/
docs/              # development brief, design spec, mockups
```

## Status

Iteration 1 is in progress, built issue by issue (see `CLAUDE.md` section 10). The
location page (`GET /t/{slug}`) is live; the dashboard and trip-logging pages have templates
but no routes yet.
