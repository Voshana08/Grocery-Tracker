import { cloneElement, useEffect, useState } from 'react'
import { Link, useNavigate, useSearchParams } from 'react-router'
import { api } from '../api/client.js'
import StatusControl from '../components/StatusControl.jsx'

export default function AddItemPage() {
  const [params] = useSearchParams()
  const from = params.get('location') ?? '' // the tag page that opened this form
  const navigate = useNavigate()

  // What the dropdowns and suggestions offer.
  const [categories, setCategories] = useState(null)
  const [locations, setLocations] = useState([])
  const [products, setProducts] = useState([])
  const [loadError, setLoadError] = useState(null)

  // What the user has typed and picked. Kept when saving fails, so nothing is lost.
  const [name, setName] = useState('')
  const [categoryId, setCategoryId] = useState('')
  const [locationSlug, setLocationSlug] = useState(from)
  const [status, setStatus] = useState('plenty')

  const [fieldErrors, setFieldErrors] = useState({})
  const [saveError, setSaveError] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    let ignore = false
    Promise.all([api('/categories'), api('/locations'), api('/products')])
      .then(([categoryList, locationList, productList]) => {
        if (ignore) return
        setCategories(categoryList)
        setLocations(locationList)
        setProducts(productList)
        const other = categoryList.find((c) => c.name === 'Other') ?? categoryList[0]
        setCategoryId((current) => current || String(other?.id ?? ''))
        setLocationSlug((current) =>
          locationList.some((l) => l.slug === current) ? current : (locationList[0]?.slug ?? ''),
        )
      })
      .catch((err) => !ignore && setLoadError(err))
    return () => {
      ignore = true
    }
  }, [])

  function changeName(value) {
    setName(value)
    setFieldErrors((errors) => ({ ...errors, product_name: undefined }))
    // Choosing a product you've added before fills in its category.
    const known = products.find((p) => p.name.toLowerCase() === value.trim().toLowerCase())
    if (known) setCategoryId(String(known.category_id))
  }

  function submit(event) {
    event.preventDefault()
    if (!name.trim()) {
      setFieldErrors({ product_name: 'Add a name for this item' })
      return
    }
    setSaving(true)
    setSaveError(null)
    api('/items', {
      method: 'POST',
      body: JSON.stringify({
        product_name: name,
        category_id: Number(categoryId),
        location_slug: locationSlug,
        status,
      }),
    })
      .then(() => navigate(`/t/${locationSlug}`, { state: { fromApp: true } }))
      .catch((err) => {
        setSaving(false)
        setFieldErrors(err.fields ?? {})
        setSaveError(err.message)
      })
  }

  const back = from ? `/t/${from}` : '/'

  return (
    <main className="page">
      <title>Add item | Grocery Tracker</title>
      <div className="form-header">
        <Link to={back} state={{ fromApp: true }}>
          Cancel
        </Link>
        <h1>Add item</h1>
      </div>

      {(loadError || saveError) && (
        <p className="error-banner" role="alert">
          {saveError ?? loadError.message}
        </p>
      )}
      {!categories && !loadError && <p className="muted">Loading…</p>}

      {categories && (
        <form className="form" onSubmit={submit} noValidate>
          <datalist id="product-suggestions">
            {products.map((p) => (
              <option key={p.id} value={p.name} />
            ))}
          </datalist>

          <Field label="Product name" error={fieldErrors.product_name} id="product-name">
            <input
              type="text"
              list="product-suggestions"
              placeholder="Start typing a product"
              autoComplete="off"
              value={name}
              onChange={(e) => changeName(e.target.value)}
            />
          </Field>

          <Field label="Category" error={fieldErrors.category_id} id="category">
            <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </Field>

          <Field label="Location" error={fieldErrors.location_slug} id="location">
            <select value={locationSlug} onChange={(e) => setLocationSlug(e.target.value)}>
              {locations.map((l) => (
                <option key={l.slug} value={l.slug}>
                  {l.name}
                </option>
              ))}
            </select>
          </Field>

          <fieldset className="field">
            <legend>Status</legend>
            <StatusControl status={status} onChange={setStatus} wide />
          </fieldset>

          <button type="submit" className="button-primary" disabled={saving}>
            {saving ? 'Adding…' : 'Add item'}
          </button>
        </form>
      )}
    </main>
  )
}

// A label above one input or select, with its error underneath when there is one.
function Field({ label, error, id, children }) {
  const errorId = `${id}-error`
  return (
    <div className="field">
      <label htmlFor={id}>{label}</label>
      {cloneElement(children, {
        id,
        'aria-invalid': error ? true : undefined,
        'aria-describedby': error ? errorId : undefined,
      })}
      {error && (
        <span id={errorId} className="field-error">
          {error}
        </span>
      )}
    </div>
  )
}
