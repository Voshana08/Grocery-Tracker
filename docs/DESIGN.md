# Grocery Tracker: design brief

The visual source of truth for iteration 1. The approved mockups (Dashboard, Fridge, Log a trip) are in Claude Design: https://claude.ai/artifact/XUgFLZMWLRoR8wQFFahy2a. Where this file and a mockup disagree, this file wins.

## 1. Who it is for and how it should feel

- **User:** a budget-conscious young adult in Melbourne who shops at Woolworths, Coles and Aldi up to five times a week and wants to stop wasting money and trips.
- **Where it is used:** standing at the fridge after tapping an NFC tag, or in the kitchen after unpacking the shopping. One hand, often in a hurry.
- **Feel:** fresh food and a paper shopping bag, not a bank. Calm, warm, practical. "Fresh market" palette.

### Principles

1. **One glance, one tap.** The tag page must answer "what's low?" without scrolling and change a status in a single tap.
2. **Honest about money.** Spending is shown in neutral ink, never in green. Green means action or "stocked", not "you spent".
3. **Trips are the enemy.** Shopping days are highlighted in carrot orange so a busy week is impossible to miss.
4. **Never lose typing.** A validation error keeps everything the user entered.
5. **Status is never colour alone.** Every status shows its word (Plenty, Low, Out).

## 2. Design tokens

Put these in `app/static/app.css` under `:root` exactly once. Templates and CSS use the variables, never raw hex values.

### Colour

| Token | Hex | Use |
|---|---|---|
| `--color-bg` | `#F7F4EC` | Page background (oat) |
| `--color-surface` | `#FFFFFF` | Cards, inputs, bottom nav |
| `--color-border` | `#E8E2D3` | Card borders, nav top border |
| `--color-border-input` | `#DDD6C6` | Inputs, selects, unselected segment buttons |
| `--color-divider` | `#F0EBDF` | Lines between list rows |
| `--color-ink` | `#1D2A1F` | Primary text and money amounts |
| `--color-muted` | `#5F6B5E` | Secondary text, labels, inactive nav |
| `--color-primary` | `#2E6A44` | Primary buttons, selected Plenty, active nav, icons (basil green) |
| `--color-primary-text` | `#24553A` | Links and green text on light backgrounds |
| `--color-primary-hover` | `#173D29` | Link hover |
| `--color-primary-tint` | `#E4EFDF` | "Opened from tag" chip, success icon circle |
| `--color-low-bg` | `#FBEBC8` | Low badge and selected Low segment (mustard) |
| `--color-low-text` | `#7A4F00` | Low text |
| `--color-low-border` | `#E5C27A` | Selected Low segment border |
| `--color-out-bg` | `#FADDD5` | Out badge, selected Out segment, error banner (tomato) |
| `--color-out-text` | `#A3321C` | Out text, error text |
| `--color-out-border` | `#EBA592` | Selected Out segment border |
| `--color-error-border` | `#B83A22` | Invalid input border (1.5px) |
| `--color-trip-day` | `#D9622B` | Days with a shopping trip (carrot) |
| `--color-day-empty` | `#EFE9DB` | Past days with no trip |
| `--color-day-future` | `#CFC6B2` | Dashed outline for days still to come |
| `--color-dashed` | `#B9B09A` | Dashed "Add another item" button border |

Text on white must meet WCAG AA (4.5:1). All pairs above have been chosen to pass; do not lighten `--color-muted`.

### Typography

Load from Google Fonts: Bricolage Grotesque (600, 700) and Figtree (400, 500, 600, 700).

| Token / role | Font | Size | Weight | Notes |
|---|---|---|---|---|
| Display number (month spend) | Bricolage Grotesque | 42px | 700 | letter-spacing -0.03em, tabular numbers |
| Page title (Fridge) | Bricolage Grotesque | 32px | 700 | letter-spacing -0.02em |
| Greeting (Hi Voshana) | Bricolage Grotesque | 28px | 700 | |
| Trip total | Bricolage Grotesque | 30px | 700 | tabular numbers |
| Header title (New trip) | Bricolage Grotesque | 20px | 700 | centred |
| Section heading (At home) | Bricolage Grotesque | 17px | 700 | |
| Body, inputs, buttons | Figtree | 16px | 400 / 600 for buttons | Inputs must be 16px or iOS zooms in |
| List item name | Figtree | 15px | 500–600 | |
| Labels, secondary | Figtree | 14px | 400–600 | |
| Meta, badges | Figtree | 13px | 400–600 | |
| Field labels, nav labels, weekday letters | Figtree | 12px | 500–600 | |

Every money amount uses `font-variant-numeric: tabular-nums`.

### Spacing, shape, size

- 4px base unit. Page padding 20px left/right, 20–28px top. Gaps: 8, 10, 12, 16, 20px.
- Corner radius: cards 16px (summary cards 20px); primary buttons 14px; inputs and segment buttons 10–12px; badges and chips 999px.
- Card: white, 1px `--color-border`, no shadow.
- **Touch targets at least 44 × 44px.** Primary buttons 52px tall; inputs 44–48px.
- No shadows, gradients, emoji or blue anywhere.

### Icons

Inline SVG, 24px viewBox, stroke 1.75–2px, round caps and joins, colour from `currentColor` or `--color-primary`. Icons needed: plus, chevron-left, fridge, jar (pantry), bottle (cleaning), home, receipt (trips), bar chart (spending), check, NFC waves. Icon-only buttons need an `aria-label`.

## 3. Components

| Component | Spec |
|---|---|
| **Primary button** | Full width, 52px, `--color-primary` background, white 16px/600 text, radius 14px. Optional leading plus icon. |
| **Outline button** | Same size, white background, 1.5px `--color-primary` border, primary text. Used for "Add item to Fridge". |
| **Dashed add button** | 48px, transparent, 1.5px dashed `--color-dashed`, `--color-primary-text`, plus icon. "Add another item". |
| **Card** | See tokens. Padding 16–20px. |
| **List row** | Inside a card; 14px 16px padding; name (15px) over meta (13px muted) on the left, badge or control on the right; `--color-divider` between rows. |
| **Status badge** | Pill, 13px/600, 4px 10px padding. Low: low-bg/low-text. Out: out-bg/out-text. (Plenty is not badged in lists.) |
| **Status segmented control** | Three `<button>`s (Plenty, Low, Out), min 52 × 44px, gap 4px, 13px/600, radius 10px, `aria-pressed`, grouped with `role="group"` and `aria-label="Stock level for <item>"`. Unselected: white, input border, muted text. Selected Plenty: primary bg, white text. Selected Low/Out: their bg, text and border colours. One tap = one HTMX request; the row updates in place. |
| **Store picker** | 2 × 2 grid of 48px pill buttons (Woolworths, Coles, Aldi, Other) inside a `<fieldset>` with legend "Store". Selected = primary bg, white text. Backed by radio inputs so it works without JavaScript. |
| **Text input / select** | 44px (48px for date), white, 1px input border, radius 10–12px, 16px text. Label above, 12px/600 muted. |
| **Error banner** | `role="alert"`, out-bg, out-text 14px/600, radius 12px, 12px 14px padding. |
| **Inline field error** | 13px/600 out-text under the field; field border becomes 1.5px `--color-error-border`; `aria-invalid="true"`. |
| **Tag chip** | "Opened from tag" with NFC waves icon; primary-tint bg, primary-text, 13px, pill. Shown on location pages. |
| **Header** | Back link left (chevron + "Home", 44px tall) or "Cancel"; optional centred title; optional chip right. |
| **Bottom nav** | 72px, white, top border; 3 equal tabs: Home, Trips, Spending; icon 22px over 12px label; active tab primary colour and `aria-current="page"`; inactive muted. Shown on Dashboard, Trips and Spending; hidden on forms and tag pages. |
| **Week row** | 7 circles (32px) Mon–Sun with weekday letter below (12px). Trip day: trip-day fill. Past day without trip: day-empty fill. Future day: 1.5px dashed day-future outline. Today's letter is ink and 600. Caption: "Orange days had a shopping trip". |
| **Location tile** | Card link, 3 across; icon, name (15px/600), status line (13px): "2 low" in low-text, "1 out" in out-text, "All stocked" in primary. Out wins over low when both exist ("1 out · 2 low"). |
| **Empty state** | Centred in a card: short heading, one line of muted text, optional primary action. |

## 4. Screens

All screens are designed at **390 × 844** (iPhone) and must not scroll sideways. Content can scroll vertically.

### Dashboard `/`  (mockup: Dashboard)
1. Header: date in muted 14px ("Wednesday 14 October"), greeting "Hi Voshana", account button (initial in a 44px circle) linking to logout.
2. Summary card: "Spent in October so far", display number, "across N trips"; divider; "This week" with "3 trips · $96.40"; week row.
3. Primary button "Log a shopping trip".
4. "At home": three location tiles.
5. "Buy next time": list of low and out items with location and badge, out first. Empty: "Nothing running low. Nice."
6. Bottom nav (Home active).

### Location page `/t/{slug}`  (mockup: Fridge)
1. Header: back to Home; "Opened from tag" chip.
2. Title (location name); summary line "6 items · 2 running low or out" or "6 items · all stocked".
3. One card per item: name, category, segmented control.
4. Outline button "Add item to {Location}" (goes to the add form with this location pre-selected).
5. Empty: "Nothing in the {location} yet" with the add button.
6. Unknown slug: friendly 404 "This tag isn't set up" with a link Home.

### Add item `/items/new`
Header with Cancel; title "Add item"; fields: Product name (with suggestions), Category (select), Location (select, pre-selected from the tag page), Status (segmented control, default Plenty); primary button "Add item". On success return to that location page.

### Log a trip `/trips/new`  (mockup: Log a trip)
1. Header: Cancel, centred "New trip".
2. Store picker, Date (defaults to today).
3. "Items" with count; one card per row: Product (suggestions), then a 3-column row: Category, Goes in (location), Price ($).
4. Dashed "Add another item" (adds a blank row via HTMX).
5. Total card: "Trip total" and amount (updates when the form is re-rendered); primary "Save trip".
6. Errors: banner above the items plus inline errors; rows kept.

### Trip saved (after POST /trips)
Card with check icon in a primary-tint circle, "Trip saved", "3 items from Woolworths", total, "Every item is now marked Plenty at home.", primary "Back to dashboard". A secondary text link "View trip".

### Trips `/trips`
Bottom nav (Trips active). Title "Trips". Rows: store and date ("Woolworths · Thu 8 Oct"), item count, total on the right. Newest first. Empty: "No trips logged yet" with "Log a shopping trip".

### Trip detail `/trips/{id}`
Back to Trips; title store; date; list of items (name, location, price × quantity); total at the bottom.

### Spending `/spending`
Bottom nav (Spending active). Month switcher: previous arrow, "October 2026", next arrow (disabled for future months). Summary card: total and trip count. Category list: name, amount, and a simple bar (primary colour) showing its share of the month. Empty: "No trips in September" with a muted explanation.

### Login `/login`
Centred card: app name "Grocery Tracker", Username, Password, primary "Log in". Error banner on failure. No bottom nav.

## 5. Copy and formatting

- Voice: short, friendly, plain. "Buy next time", not "Inventory deficiencies".
- Money: `$4.50`, `$412.60` (always two decimals, AUD, no "AUD" label).
- Dates: list rows "Thu 8 Oct"; headers "Wednesday 14 October"; month "October 2026".
- Sentence case for all buttons and headings.
- Errors say how to fix it: "Add a price for this item".

## 6. Accessibility checklist

- Real `<button>`, `<a href>`, `<input>` with `<label>`; never click handlers on `<div>`.
- `lang="en-AU"` on `<html>`; every page has a unique `<title>`.
- Inputs at least 16px (prevents iOS zoom); targets at least 44px.
- Status always has its word, not just colour; `aria-pressed` on segment buttons.
- Visible focus ring: 2px `--color-primary` outline, 2px offset.
- Respect `prefers-reduced-motion` (no animations needed in iteration 1 anyway).

## 7. Out of scope for design in iteration 1

Dark mode, product photos, illustrations, animations, onboarding screens, desktop layouts (pages simply centre at max-width 480px on larger screens).
