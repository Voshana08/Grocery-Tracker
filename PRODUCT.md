# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

Mobile-first web app, used on phones: iPhone (Safari) and Android (Chrome). Both must be tested. No native app.

## Users

- **Now:** the owner, Voshana, a budget-conscious young adult in Melbourne, Australia, who shops at Woolworths, Coles and Aldi, often several times a week. Iteration 1 is single-user.
- **Eventually:** other people like the owner. Multi-user accounts are a backlog item (issue #28), not built yet. Screens should not assume the reader built the app or knows its internals.

Situations of use:
- Standing at the fridge, pantry or cleaning cupboard after tapping an NFC sticker: one hand, in a hurry, checking what is low and changing a status.
- In the kitchen after unpacking the shopping: logging the trip (store, date, items, prices).
- Glancing at the dashboard to see this week's trips, this month's spend, and what to buy next time.

## Product Purpose

Stop unplanned grocery trips and impulse spending. Knowing what is at home, and what is running low, means one planned shop instead of several top-up trips.

Success is **fewer trips per week and spending within a monthly budget**. Overspending and forgetting things (which causes extra trips) matter equally.

## Positioning

Inventory starts at the place it lives: an NFC tag on the fridge, pantry and cleaning cupboard opens that place's stock list in one tap. Logging a trip records the spend **and** restocks home in one step, so spending and stock stay connected without double entry. Trips, not just dollars, are the main measure.

## Operating Context

- Three home locations with NFC tags: Fridge (`/t/fridge`), Pantry (`/t/pantry`), Cleaning cupboard (`/t/cleaning`). The tag URLs are written on physical stickers and never change.
- Stores: Woolworths, Coles, Aldi, Other. Currency AUD. Time zone Australia/Melbourne. Weeks run Monday to Sunday.
- Stock is tracked as a status per item (plenty, low, out), not exact quantities.

## Capabilities and Constraints

- Iteration 1: location pages with one-tap status changes, add item, log a trip (which restocks home), trips list and detail, monthly spending by category, dashboard, single-user login. Full scope and build order: `CLAUDE.md`.
- Stack is decided: FastAPI JSON API, React front end (Vite, plain JavaScript), SQLite locally and PostgreSQL on Railway. See `CLAUDE.md`.
- Money is stored as integer cents; totals are always calculated, never stored.
- **Undecided:** the weekly trip target and the monthly budget amount. The app does not yet store or show either; showing progress against them is future work and needs the owner's numbers first.
- Out of scope for iteration 1 (backlog): receipt scanning, barcodes, product photos, exact quantities, recipes, price history, AI summaries, multiple users, login rate limiting (issue #31).

## Brand Commitments

- Name: **Grocery Tracker**.
- Voice: short, friendly, plain ("Buy next time", not "Inventory deficiencies"). Sentence case. Errors say how to fix the problem.
- Money is shown honestly: spending is never styled as a success.
- The design must not look AI-generated or templated. The owner is happy to change the design until it feels right.

## Evidence on Hand

- No real users, testimonials, usage data or screenshots yet. Do not invent any.
- Sample product names in mockups are illustrative only.
- Design brief: `docs/DESIGN.md`. Mockups: the Claude Design canvas linked from it.

## Product Principles

1. **Fewer trips is the goal.** Every screen should make it easier to plan one shop instead of several; trip counts are shown prominently and honestly.
2. **One glance, one tap.** At a tag, the answer to "what's low?" and the action to change it come first.
3. **Spending and stock stay connected.** One action (logging a trip) updates both; nothing is entered twice.
4. **Never lose what the user typed.** Errors keep the input and say how to fix it.
5. **Honest, not motivational.** Show the real numbers plainly; no streaks, praise or guilt.

## Accessibility & Inclusion

WCAG 2.2 AA: text contrast 4.5:1, input borders 3:1, 44 × 44 px touch targets, 16 px inputs (prevents iOS zoom), status never shown by colour alone, visible focus rings, real buttons, links and labels.
