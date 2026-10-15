import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import { api } from '../api/client.js'
import StatusControl from '../components/StatusControl.jsx'

const NEEDS_BUYING_FIRST = { out: 0, low: 1, plenty: 2 }

// Out first, then low, then plenty. The API already sorts by name, and sort() keeps
// that order inside each group. Done once on load so cards never jump under a thumb.
function sortForGlance(items) {
  return [...items].sort((a, b) => NEEDS_BUYING_FIRST[a.status] - NEEDS_BUYING_FIRST[b.status])
}

function summaryLine(items) {
  const needed = items.filter((item) => item.status !== 'plenty').length
  const count = `${items.length} ${items.length === 1 ? 'item' : 'items'}`
  return needed === 0 ? `${count} · all stocked` : `${count} · ${needed} running low or out`
}

// key={slug}: going from /t/fridge to /t/pantry gives a fresh page with empty state.
export default function LocationRoute() {
  const { slug } = useParams()
  return <LocationPage key={slug} slug={slug} />
}

function LocationPage({ slug }) {
  const { state } = useLocation()
  const [location, setLocation] = useState(null)
  const [error, setError] = useState(null)
  const [saveError, setSaveError] = useState(null)

  useEffect(() => {
    let ignore = false // if the page closes mid-request, drop the late answer
    api(`/locations/${encodeURIComponent(slug)}`)
      .then((data) => !ignore && setLocation({ ...data, items: sortForGlance(data.items) }))
      .catch((err) => !ignore && setError(err))
    return () => {
      ignore = true
    }
  }, [slug])

  function setItemStatus(itemId, status, onlyIf) {
    setLocation((current) => ({
      ...current,
      items: current.items.map((item) =>
        item.id === itemId && (!onlyIf || item.status === onlyIf) ? { ...item, status } : item,
      ),
    }))
  }

  // Show the new status at once, then save it. If saving fails, put the old one back.
  function changeStatus(item, newStatus) {
    if (newStatus === item.status) return
    const oldStatus = item.status
    setItemStatus(item.id, newStatus)
    setSaveError(null)
    api(`/inventory/${item.id}`, {
      method: 'PATCH',
      body: JSON.stringify({ status: newStatus }),
    }).catch(() => {
      // onlyIf: if another tap changed this item meanwhile, keep that newer choice.
      setItemStatus(item.id, oldStatus, newStatus)
      setSaveError(`Couldn't save ${item.name}. Try again.`)
    })
  }

  if (error?.status === 404) {
    return (
      <main className="page">
        <title>Tag not set up | Grocery Tracker</title>
        <div className="card empty-state">
          <h1>This tag isn't set up</h1>
          <Link to="/">Go to Home</Link>
        </div>
      </main>
    )
  }

  return (
    <main className="page">
      <title>{`${location?.name ?? 'Loading'} | Grocery Tracker`}</title>
      <div className="page-header">
        <Link to="/" className="back-link">
          <ChevronLeft />
          Home
        </Link>
        {/* Tiles on the dashboard pass fromApp, so the chip only shows after a real tag tap. */}
        {!state?.fromApp && (
          <span className="tag-chip">
            <NfcWaves />
            Opened from tag
          </span>
        )}
      </div>

      {(error || saveError) && (
        <p className="error-banner" role="alert">
          {saveError ?? error.message}
        </p>
      )}
      {!location && !error && <p className="muted">Loading…</p>}

      {location && (
        <>
          <div className="page-title">
            <h1>{location.name}</h1>
            {location.items.length > 0 && (
              <span className="summary muted">{summaryLine(location.items)}</span>
            )}
          </div>

          {location.items.length === 0 ? (
            <div className="card empty-state">
              <h2>Nothing in the {location.name.toLowerCase()} yet</h2>
            </div>
          ) : (
            <ul className="item-list">
              {location.items.map((item) => (
                <li key={item.id} className="card item">
                  <div className="item-text">
                    <span className="item-name">{item.name}</span>
                    <span className="item-category muted">{item.category}</span>
                  </div>
                  <StatusControl
                    itemName={item.name}
                    status={item.status}
                    onChange={(newStatus) => changeStatus(item, newStatus)}
                  />
                </li>
              ))}
            </ul>
          )}

          <Link to={`/items/new?location=${location.slug}`} className="button-outline">
            <Plus />
            Add item to {location.name}
          </Link>
        </>
      )}
    </main>
  )
}

function ChevronLeft() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 5l-7 7 7 7" />
    </svg>
  )
}

function NfcWaves() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <path d="M6 8.5a8 8 0 0 1 0 7M9.5 6a12 12 0 0 1 0 12M13 4a16 16 0 0 1 0 16" />
    </svg>
  )
}

function Plus() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}
