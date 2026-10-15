import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../api/client.js'
import BottomNav from '../components/BottomNav.jsx'
import { Plus } from '../components/Icons.jsx'
import { formatMoney, formatShortDate } from '../lib/format.js'

export default function TripsPage() {
  const [trips, setTrips] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    api('/trips')
      .then((data) => !ignore && setTrips(data))
      .catch((err) => !ignore && setError(err))
    return () => {
      ignore = true
    }
  }, [])

  return (
    <>
      <main className="page has-nav">
        <title>Trips | Grocery Tracker</title>
        <h1 className="screen-title">Trips</h1>

        {error && (
          <p className="error-banner" role="alert">
            {error.message}
          </p>
        )}
        {!trips && !error && <p className="muted">Loading…</p>}

        {trips?.length === 0 && (
          <div className="card empty-state">
            <h2>No trips logged yet</h2>
            <Link to="/trips/new" className="button-primary">
              <Plus />
              Log a shopping trip
            </Link>
          </div>
        )}

        {trips?.length > 0 && (
          <ul className="card list">
            {trips.map((trip) => (
              <li key={trip.id}>
                <Link to={`/trips/${trip.id}`} className="list-row">
                  <span className="list-text">
                    <span className="list-name">
                      {trip.store} · {formatShortDate(trip.trip_date)}
                    </span>
                    <span className="list-meta muted">
                      {trip.item_count === 1 ? '1 item' : `${trip.item_count} items`}
                    </span>
                  </span>
                  <span className="list-amount">{formatMoney(trip.total_cents)}</span>
                </Link>
              </li>
            ))}
          </ul>
        )}
      </main>
      <BottomNav />
    </>
  )
}
