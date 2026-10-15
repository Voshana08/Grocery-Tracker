import { useEffect, useState } from 'react'
import { Link, useLocation, useParams } from 'react-router'
import { api } from '../api/client.js'
import { formatMoney } from '../lib/format.js'

export default function TripSavedPage() {
  const { id } = useParams()
  const { state } = useLocation()
  // Arriving from the form, the trip comes along; after a reload, fetch it.
  const [trip, setTrip] = useState(state?.trip ?? null)
  const [error, setError] = useState(null)

  useEffect(() => {
    if (trip) return
    let ignore = false
    api(`/trips/${id}`)
      .then((data) => !ignore && setTrip(data))
      .catch((err) => !ignore && setError(err))
    return () => {
      ignore = true
    }
  }, [id, trip])

  const count = trip?.items.length

  return (
    <main className="page">
      <title>Trip saved | Grocery Tracker</title>
      {error && (
        <p className="error-banner" role="alert">
          {error.message}
        </p>
      )}
      {!trip && !error && <p className="muted">Loading…</p>}
      {trip && (
        <section className="card saved">
          <div className="saved-check">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor"
              strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
              <path d="M5 12.5l4.5 4.5L19 7.5" />
            </svg>
          </div>
          <h1>Trip saved</h1>
          <p className="muted">
            {count === 1 ? '1 item' : `${count} items`} from {trip.store}
          </p>
          <p className="saved-total">{formatMoney(trip.total_cents)}</p>
          <p className="muted">Every item is now marked Plenty at home.</p>
          <Link to="/" className="button-primary">
            Back to dashboard
          </Link>
          <Link to={`/trips/${trip.id}`} className="saved-view">
            View trip
          </Link>
        </section>
      )}
    </main>
  )
}
