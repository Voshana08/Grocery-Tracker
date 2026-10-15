# Grocery Tracker: design brief

The visual source of truth for iteration 1. The approved mockups are the **"v1 with your palette"** row (Dashboard, Fridge, Log a trip; palette approved 15 Oct 2026) in Claude Design: https://claude.ai/artifact/XUgFLZMWLRoR8wQFFahy2a. Where this file and a mockup disagree, this file wins.

## 1. Who it is for and how it should feel

- **User:** a budget-conscious young adult in Melbourne who shops at Woolworths, Coles and Aldi up to five times a week and wants to stop wasting money and trips.
- **Where it is used:** standing at the fridge after tapping an NFC tag, or in the kitchen after unpacking the shopping. One hand, often in a hurry.
- **Feel:** fresh food and a paper shopping bag, not a bank. Calm, warm, practical. Palette chosen by the owner: plum, blue, sage, butter and coral.

### Principles

1. **One glance, one tap.** The tag page must answer "what's low?" without scrolling and change a status in a single tap.
2. **Honest about money.** Spending is shown in plum ink, never in a status colour. Blue means action; sage means "stocked"; neither means "you spent".
3. **Trips are the enemy.** Shopping days are highlighted in coral so a busy week is impossible to miss.
4. **Never lose typing.** A validation error keeps everything the user entered.
5. **Status is never colour alone.** Every status shows its word (Plenty, Low, Out).

## 2. Design tokens

Put these in `frontend/src/styles/tokens.css` under `:root` exactly once. Components and CSS use the variables, never raw hex values.

### Colour

| Token | Hex | Use |
|---|---|---|
| `--color-bg` | `#FFFFFF` | Page background: white, as in the owner's mockups (changed 15 Oct 2026). Cards stand out by their border |
| `--color-surface` | `#FFFFFF` | Cards, inputs, bottom nav, dashboard content area |
| `--color-border` | `#E6DFC2` | Card borders, nav top border |
| `--color-border-input` | `#8E7D86` | Inputs and selects (3.9:1 on white, so the field edge is visible) |
| `--color-border-control` | `#E0D8BE` | Unselected segment and store buttons, account button |
| `--color-divider` | `#EFE9D0` | Lines between list rows |
| `--color-ink` | `#381D2A` | Primary text and money amounts (plum) |
| `--color-muted` | `#6B5762` | Secondary text, labels, inactive nav (derived from plum) |
| `--color-primary` | `#3E6990` | Primary buttons, links, active nav, selected store, icons (blue) |
| `--color-primary-hover` | `#335A7D` | Link and button hover |
| `--color-plenty` | `#AABD8C` | Selected Plenty segment (sage), with ink text |
| `--color-plenty-border` | `#8FA472` | Selected Plenty segment border |
| `--color-stocked-text` | `#58703F` | "All stocked" text (sage, darkened to pass contrast) |
| `--color-stocked-tint` | `#E6ECDB` | "Opened from tag" chip, success icon circle |
| `--color-stocked-tint-text` | `#3F5530` | Text on the stocked tint |
| `--color-low-bg` | `#E9E3B4` | Low badge, selected Low segment, past days without a trip (butter) |
| `--color-low-text` | `#381D2A` | Low text (ink) |
| `--color-low-border` | `#CFC68A` | Selected Low segment border |
| `--color-out-bg` | `#381D2A` | Out badge and selected Out segment (solid plum: the darkest status is the most urgent) |
| `--color-out-text` | `#FFFFFF` | Text on Out |
| `--color-error-bg` | `#FCE4D7` | Error banner |
| `--color-error-text` | `#A3461C` | Error banner text, inline field errors |
| `--color-error-border` | `#A3461C` | Invalid input border (1.5px) |
| `--color-trip-day` | `#EE6C4D` | Days with a shopping trip (coral) |
| `--color-day-future` | `#B8A9AE` | Dashed outline for days still to come |
| `--color-dashed` | `#8E7D86` | Dashed "Add another item" button border |

Text on white must meet WCAG AA (4.5:1), and an input's border, when it is the only sign of the field, needs 3:1. All pairs above pass; do not lighten `--color-muted` or `--color-border-input`.

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
| **Dashed add button** | 48px, transparent, 1.5px dashed `--color-dashed`, `--color-primary`, plus icon. "Add another item". |
| **Card** | See tokens. Padding 16–20px. |
| **List row** | Inside a card; 14px 16px padding; name (15px) over meta (13px muted) on the left, badge or control on the right; `--color-divider` between rows. |
| **Status badge** | Pill, 13px/600, 4px 10px padding. Low: low-bg/low-text. Out: out-bg/out-text (white on plum). (Plenty is not badged in lists.) |
| **Status segmented control** | Three `<button>`s (Plenty, Low, Out), min 52 × 44px, gap 4px, 13px/600, radius 10px, `aria-pressed`, grouped with `role="group"` and `aria-label="Stock level for <item>"`. Unselected: white, control border, muted text. Selected Plenty: plenty bg, ink text, plenty border. Selected Low/Out: their bg, text and border colours. One tap updates the screen at once and sends the PATCH; if it fails, the old status comes back and the error banner shows. |
| **Store picker** | 2 × 2 grid of 48px pill buttons (Woolworths, Coles, Aldi, Other) inside a `<fieldset>` with legend "Store". Selected = primary bg, white text. Backed by radio inputs (VoiceOver reads them as a choice of four). |
| **Text input / select** | 44px (48px for date), white, 1px input border, radius 10–12px, 16px text. Label above, 12px/600 muted. |
| **Error banner** | `role="alert"`, error-bg, error-text 14px/600, radius 12px, 12px 14px padding. |
| **Inline field error** | 13px/600 error-text under the field; field border becomes 1.5px `--color-error-border`; `aria-invalid="true"`. |
| **Tag chip** | "Opened from tag" with NFC waves icon; stocked-tint bg, stocked-tint-text, 13px, pill. Shown on location pages. |
| **Header** | Back link left (chevron + "Home", 44px tall) or "Cancel"; optional centred title; optional chip right. |
| **Bottom nav** | 72px, white, top border; 3 equal tabs: Home, Trips, Spending; icon 22px over 12px label; active tab primary colour and `aria-current="page"`; inactive muted. Shown on Dashboard, Trips and Spending; hidden on forms and tag pages. |
| **Week row** | 7 circles (32px) Mon–Sun with weekday letter below (12px). Trip day: trip-day fill with a white check icon inside, so the meaning never rests on colour alone. Past day without trip: low-bg fill. Future day: 1.5px dashed day-future outline. Today's letter is ink and 600. Each day has an `aria-label` ("Monday, 1 trip", "Tuesday, no trip"). Caption: "Days with a shopping trip are ticked". |
| **Location tile** | Card link, 3 across; icon, name (15px/600), status line (13px): "2 low" in low-text, "1 out" in ink 600, "All stocked" in stocked-text. Out wins over low when both exist ("1 out · 2 low"). |
| **Empty state** | Centred in a card: short heading, one line of muted text, optional primary action. |

## 4. Screens

All screens are designed at **390 × 844** (iPhone) and must not scroll sideways. Content can scroll vertically.

### Dashboard `/`  (mockup: Dashboard)
1. Header: date in muted 14px ("Wednesday 14 October"), greeting "Hi {display_name}" ("Hi there" until login exists in #16), account button (first letter of the display name in a 44px circle). Tapping the account button shows a small "Log out" button below it; logging out takes two taps, so it never happens by accident.
2. Summary card: "Spent in October so far", display number, "across N trips"; divider; "This week" with "3 trips · $96.40"; week row.
3. Primary button "Log a shopping trip".
4. "At home": three location tiles.
5. "Buy next time": list of low and out items with location and badge, out first. Empty: "Nothing running low. Nice."
6. Bottom nav (Home active).

### Location page `/t/{slug}`  (mockup: Fridge)
1. Header: back to Home; "Opened from tag" chip, shown only when the page was opened directly (tag tap or typed URL). Dashboard tiles pass a flag when they link here, so the chip stays truthful.
2. Title (location name); summary line "6 items · 2 running low or out" or "6 items · all stocked".
3. One card per item: name, category, segmented control. Sorted out first, then low, then plenty, each group by name, so "what's low?" is answered without scrolling. The order is set when the page loads; tapping a status does **not** move the card (it would jump from under the thumb). The new order shows on the next visit.
4. Outline button "Add item to {Location}" (goes to the add form with this location pre-selected).
5. Empty: "Nothing in the {location} yet" with the add button.
6. Unknown slug: friendly 404 "This tag isn't set up" with a link Home.

### Add item `/items/new`
Mockup: "Add item (v1, your palette)" on the canvas (approved 15 Oct 2026). Header with Cancel (back to the tag page it came from); centred title "Add item". Fields, each with a 14px/600 ink label above and a 48px input: Product name (with suggestions; choosing a known product fills in its Category), Category (select), Location (select, pre-selected from the tag page), Status (Plenty / Low / Out buttons across the full width, 48px, default Plenty). Primary button "Add item" at the bottom ("Adding…" while saving). Empty name: inline error "Add a name for this item". Adding a product that is already in that location updates its status. On success return to that location page.

### Log a trip `/trips/new`  (mockup: Log a trip)
1. Header: Cancel, centred "New trip". Cancel with anything typed shows an inline card "Discard this trip?" ("The items you've typed will be lost.") with a **Discard** button (error-text fill, white text) and an outline **Keep editing** button; with nothing typed it leaves at once. A reload still loses the trip (owner's choice: no saved draft).
2. Store picker (no store chosen at first; "Choose a store" if missing), Date (defaults to today in Melbourne, no future dates).
3. "Items" with count; one card per row: Product (suggestions; a known product fills in its category), then a 3-column row: Category, Goes in (location), Price ($). All fields 16px so iOS doesn't zoom; long options such as "Cleaning cupboard" are cut off in the narrow selects (owner's choice). A muted "Remove" text button sits top-right of each card (44px tall), hidden when there is only one row. Completely blank rows are ignored when saving.
4. Dashed "Add another item" (adds a blank row in React state, no server call).
5. Total card: "Trip total" and amount, updated live as prices are typed (display only; the API calculates the saved total); primary "Save trip".
6. Errors: banner above the items ("1 item needs a price before saving", or "2 items need fixing before saving" for other mistakes) plus inline errors under the row ("Add a product name", "Add a price for this item", "Use a price like 4.50"); rows kept.

### Trip saved `/trips/{id}/saved`
Card with check icon in a stocked-tint circle, "Trip saved", "3 items from Woolworths", total, "Every item is now marked Plenty at home." (added in #12, once restocking exists), primary "Back to dashboard". A secondary text link "View trip". Built in #11; survives a reload by fetching the trip.

### Trips `/trips`
Bottom nav (Trips active). Title "Trips". Rows: store and date ("Woolworths · Thu 8 Oct"), item count, total on the right. Newest first. Empty: "No trips logged yet" with "Log a shopping trip".

### Trip detail `/trips/{id}`
Back to Trips; title store; date; list of items (name, location, price × quantity); total at the bottom.

### Spending `/spending`
Bottom nav (Spending active). Month switcher: previous arrow, "October 2026", next arrow (disabled for future months). Summary card: total and trip count. Category list: name, amount, and a simple bar (primary colour) showing its share of the month. Empty: "No trips in September" with a muted explanation.

### Login `/login`
Built like the app's own pages, not a generic login template: no centred card, no logo icon, no slogan.
1. Top-aligned (about 56px from the top), so the button stays above the iPhone keyboard. Left-aligned.
2. "Grocery Tracker" as the page title (Bricolage 32px/700, same place as "Fridge" on the location page); under it one muted line, "Log in to see what's at home."
3. Fields straight on the page background: Username, Password, then a full-width primary "Log in". A real `<form>` with a submit button, so iPhone (iCloud Keychain) and Android (Google Password Manager) offer to save and autofill the password.
4. Username: `autocomplete="username"`, `autocapitalize="none"`, `autocorrect="off"`, `spellcheck="false"`. Password: `autocomplete="current-password"`. No show/hide password button.
5. Empty field: inline error ("Enter your username", "Enter your password"). Wrong details: error banner "Username or password is incorrect" above the fields; the username is kept, the password is cleared and focused. While waiting: the button reads "Logging in…" and is disabled.
6. Already logged in: go straight to `?next=` or `/`. No bottom nav.

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
