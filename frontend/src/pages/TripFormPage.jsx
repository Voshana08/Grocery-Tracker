import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router'
import { api } from '../api/client.js'
import { Plus } from '../components/Icons.jsx'
import { dollarsToCents, formatMoney, todayInMelbourne } from '../lib/format.js'

const STORES = ['Woolworths', 'Coles', 'Aldi', 'Other']

// API field names -> the row's own field names (for errors the server sends back).
const ROW_FIELD = {
  product_name: 'product',
  category_id: 'categoryId',
  location_slug: 'locationSlug',
  price_cents: 'price',
}

let nextKey = 1 // gives every row a stable React key, even after rows are removed

function isBlank(row) {
  return !row.product.trim() && !row.price.trim()
}

// Checks the form the same way the API will, so mistakes show before sending.
// Completely blank rows are ignored (owner's choice), so a stray "Add another item" is harmless.
function validate(store, date, rows) {
  const errors = { rows: {} }
  if (!store) errors.store = 'Choose a store'
  if (!date) errors.date = 'Choose the date'
  const filled = rows.filter((row) => !isBlank(row))
  if (filled.length === 0) errors.items = 'Add at least one item'
  for (const row of filled) {
    const rowErrors = {}
    if (!row.product.trim()) rowErrors.product = 'Add a product name'
    if (dollarsToCents(row.price) === null) {
      rowErrors.price = row.price.trim() ? 'Use a price like 4.50' : 'Add a price for this item'
    }
    if (Object.keys(rowErrors).length) errors.rows[row.key] = rowErrors
  }
  return errors
}

// Rows that still have at least one error (a row whose errors were all fixed has an empty {}).
function rowsWithErrors(errors) {
  return Object.values(errors.rows).filter((rowErrors) => Object.keys(rowErrors).length > 0)
}

function hasErrors(errors) {
  return Boolean(errors.store || errors.date || errors.items || rowsWithErrors(errors).length)
}

// "1 item needs a price before saving" (DESIGN.md), or a general line for other mistakes.
function bannerText(errors) {
  const rowErrors = rowsWithErrors(errors)
  const n = rowErrors.length
  if (n > 0) {
    const onlyPrices = rowErrors.every((e) => e.price && Object.keys(e).length === 1)
    const items = n === 1 ? '1 item needs' : `${n} items need`
    return `${items} ${onlyPrices ? 'a price' : 'fixing'} before saving`
  }
  return errors.items ?? errors.store ?? errors.date ?? errors.server
}

export default function TripFormPage() {
  const navigate = useNavigate()
  const [options, setOptions] = useState(null) // { categories, locations, products }
  const [loadError, setLoadError] = useState(null)

  const [store, setStore] = useState('')
  const [date, setDate] = useState(todayInMelbourne())
  const [rows, setRows] = useState([])
  const [errors, setErrors] = useState({ rows: {} })
  const [saving, setSaving] = useState(false)
  const [confirmingDiscard, setConfirmingDiscard] = useState(false)

  useEffect(() => {
    let ignore = false
    Promise.all([api('/categories'), api('/locations'), api('/products')])
      .then(([categories, locations, products]) => {
        if (ignore) return
        setOptions({ categories, locations, products })
        setRows([blankRow(categories, locations)])
      })
      .catch((err) => !ignore && setLoadError(err))
    return () => {
      ignore = true
    }
  }, [])

  function blankRow(categories = options.categories, locations = options.locations) {
    const other = categories.find((c) => c.name === 'Other') ?? categories[0]
    return {
      key: nextKey++,
      product: '',
      categoryId: String(other?.id ?? ''),
      locationSlug: locations[0]?.slug ?? '',
      price: '',
    }
  }

  function updateRow(key, changes) {
    setRows((current) => current.map((row) => (row.key === key ? { ...row, ...changes } : row)))
    // Clear the errors for whatever was just edited.
    setErrors((current) => {
      const rowErrors = { ...current.rows[key] }
      for (const field of Object.keys(changes)) delete rowErrors[field]
      return { ...current, rows: { ...current.rows, [key]: rowErrors } }
    })
  }

  function changeProduct(key, value) {
    // Choosing a product you've bought before fills in its category.
    const known = options.products.find((p) => p.name.toLowerCase() === value.trim().toLowerCase())
    updateRow(key, known ? { product: value, categoryId: String(known.category_id) } : { product: value })
  }

  function cancel() {
    const typedSomething = store || rows.some((row) => !isBlank(row))
    if (typedSomething) setConfirmingDiscard(true)
    else navigate('/')
  }

  function submit(event) {
    event.preventDefault()
    const found = validate(store, date, rows)
    setErrors(found)
    if (hasErrors(found)) return

    const filled = rows.filter((row) => !isBlank(row))
    setSaving(true)
    api('/trips', {
      method: 'POST',
      body: JSON.stringify({
        store,
        trip_date: date,
        items: filled.map((row) => ({
          product_name: row.product,
          category_id: Number(row.categoryId),
          location_slug: row.locationSlug,
          price_cents: dollarsToCents(row.price),
        })),
      }),
    })
      .then((trip) => navigate(`/trips/${trip.id}/saved`, { state: { trip }, replace: true }))
      .catch((err) => {
        setSaving(false)
        setErrors(serverErrors(err, filled))
      })
  }

  const totalCents = rows.reduce((sum, row) => sum + (dollarsToCents(row.price) ?? 0), 0)
  const banner = hasErrors(errors) || errors.server ? bannerText(errors) : null

  return (
    <main className="page">
      <title>New trip | Grocery Tracker</title>
      <div className="form-header">
        <button type="button" className="link-button" onClick={cancel}>
          Cancel
        </button>
        <h1>New trip</h1>
      </div>

      {confirmingDiscard && (
        <div className="card confirm" role="alert" aria-labelledby="discard-title">
          <h2 id="discard-title">Discard this trip?</h2>
          <p className="muted">The items you've typed will be lost.</p>
          <div className="confirm-actions">
            <button type="button" className="button-danger" onClick={() => navigate('/')}>
              Discard
            </button>
            <button
              type="button"
              className="button-outline"
              onClick={() => setConfirmingDiscard(false)}
            >
              Keep editing
            </button>
          </div>
        </div>
      )}

      {loadError && (
        <p className="error-banner" role="alert">
          {loadError.message}
        </p>
      )}
      {!options && !loadError && <p className="muted">Loading…</p>}

      {options && (
        <form className="form" onSubmit={submit} noValidate>
          <fieldset className="field">
            <legend>Store</legend>
            <div className="store-picker">
              {STORES.map((name) => (
                <label key={name}>
                  <input
                    type="radio"
                    name="store"
                    value={name}
                    checked={store === name}
                    onChange={() => {
                      setStore(name)
                      setErrors((current) => ({ ...current, store: undefined }))
                    }}
                  />
                  {name}
                </label>
              ))}
            </div>
            {errors.store && <span className="field-error">{errors.store}</span>}
          </fieldset>

          <div className="field">
            <label htmlFor="trip-date">Date</label>
            <input
              id="trip-date"
              type="date"
              value={date}
              max={todayInMelbourne()}
              aria-invalid={errors.date ? true : undefined}
              onChange={(e) => setDate(e.target.value)}
            />
            {errors.date && <span className="field-error">{errors.date}</span>}
          </div>

          <section className="trip-items" aria-labelledby="items-title">
            <div className="section-heading">
              <h2 id="items-title">Items</h2>
              <span className="muted">{rows.length === 1 ? '1 item' : `${rows.length} items`}</span>
            </div>

            {banner && (
              <p className="error-banner" role="alert">
                {banner}
              </p>
            )}

            <datalist id="product-suggestions">
              {options.products.map((p) => (
                <option key={p.id} value={p.name} />
              ))}
            </datalist>

            {rows.map((row, index) => (
              <TripRow
                key={row.key}
                row={row}
                number={index + 1}
                errors={errors.rows[row.key] ?? {}}
                options={options}
                canRemove={rows.length > 1}
                onChange={(changes) => updateRow(row.key, changes)}
                onProduct={(value) => changeProduct(row.key, value)}
                onRemove={() => setRows((current) => current.filter((r) => r.key !== row.key))}
              />
            ))}

            <button
              type="button"
              className="button-dashed"
              onClick={() => setRows((current) => [...current, blankRow()])}
            >
              <Plus size={18} />
              Add another item
            </button>
          </section>

          <section className="card trip-total">
            <div className="trip-total-line">
              <span className="muted">Trip total</span>
              <span className="trip-total-amount" aria-live="polite">
                {formatMoney(totalCents)}
              </span>
            </div>
            <button type="submit" className="button-primary" disabled={saving}>
              {saving ? 'Saving…' : 'Save trip'}
            </button>
          </section>
        </form>
      )}
    </main>
  )
}

// Server 422s point at items by position among the rows that were sent; map them back to rows.
function serverErrors(err, sentRows) {
  const errors = { rows: {}, server: err.message }
  for (const [path, message] of Object.entries(err.fields ?? {})) {
    const [first, index, field] = path.split('.')
    if (first === 'items' && sentRows[index] && ROW_FIELD[field]) {
      const key = sentRows[index].key
      errors.rows[key] = { ...errors.rows[key], [ROW_FIELD[field]]: message }
    } else if (first === 'store') errors.store = message
    else if (first === 'trip_date') errors.date = message
  }
  return errors
}

function TripRow({ row, number, errors, options, canRemove, onChange, onProduct, onRemove }) {
  const id = (field) => `row-${row.key}-${field}`
  const invalid = (field) =>
    errors[field] ? { 'aria-invalid': true, 'aria-describedby': id(`${field}-error`) } : {}

  return (
    <div className="card trip-row" role="group" aria-label={`Item ${number}`}>
      <div className="trip-row-top">
        <label htmlFor={id('product')}>Product</label>
        {canRemove && (
          <button
            type="button"
            className="link-button muted"
            aria-label={`Remove item ${number}${row.product ? `, ${row.product}` : ''}`}
            onClick={onRemove}
          >
            Remove
          </button>
        )}
      </div>
      <input
        id={id('product')}
        type="text"
        list="product-suggestions"
        placeholder="Start typing a product"
        autoComplete="off"
        value={row.product}
        onChange={(e) => onProduct(e.target.value)}
        {...invalid('product')}
      />
      {errors.product && (
        <span id={id('product-error')} className="field-error">
          {errors.product}
        </span>
      )}

      <div className="trip-row-grid">
        <div className="small-field">
          <label htmlFor={id('category')}>Category</label>
          <select
            id={id('category')}
            value={row.categoryId}
            onChange={(e) => onChange({ categoryId: e.target.value })}
            {...invalid('categoryId')}
          >
            {options.categories.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="small-field">
          <label htmlFor={id('location')}>Goes in</label>
          <select
            id={id('location')}
            value={row.locationSlug}
            onChange={(e) => onChange({ locationSlug: e.target.value })}
            {...invalid('locationSlug')}
          >
            {options.locations.map((l) => (
              <option key={l.slug} value={l.slug}>
                {l.name}
              </option>
            ))}
          </select>
        </div>
        <div className="small-field">
          <label htmlFor={id('price')}>Price ($)</label>
          <input
            id={id('price')}
            type="text"
            inputMode="decimal"
            placeholder="0.00"
            value={row.price}
            onChange={(e) => onChange({ price: e.target.value })}
            {...invalid('price')}
          />
        </div>
      </div>
      {['price', 'categoryId', 'locationSlug'].map(
        (field) =>
          errors[field] && (
            <span key={field} id={id(`${field}-error`)} className="field-error">
              {errors[field]}
            </span>
          ),
      )}
    </div>
  )
}
