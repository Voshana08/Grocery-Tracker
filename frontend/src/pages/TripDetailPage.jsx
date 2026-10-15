import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router'
import { api } from '../api/client.js'
import { ChevronLeft } from '../components/Icons.jsx'
import { formatLongDate, formatMoney } from '../lib/format.js'

export default function TripDetailPage() {
  const { id } = useParams()
  const [trip, setTrip] = useState(null)
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    api(`/trips/${encodeURIComponent(id)}`)
      .then((data) => !ignore && setTrip(data))
      .catch((err) => !ignore && setError(err))
    return () => {
      ignore = true
    }
  }, [id])

  return (
    <main className="page">
      <title>{`${trip ? trip.store : 'Trip'} | Grocery Tracker`}</title>
      <div className="page-header">
        <Link to="/trips" className="back-link">
          <ChevronLeft />
          Trips
        </Link>
      </div>

      {error?.status === 404 && (
        <div className="card empty-state">
          <h1>Trip not found</h1>
          <Link to="/trips">See all trips</Link>
        </div>
      )}
      {error && error.status !== 404 && (
        <p className="error-banner" role="alert">
          {error.message}
        </p>
      )}
      {!trip && !error && <p className="muted">Loading…</p>}

      {trip && (
        <>
          <div className="page-title">
            <h1>{trip.store}</h1>
            <span className="summary muted">{formatLongDate(trip.trip_date)}</span>
          </div>

          <ul className="card list">
            {trip.items.map((item) => (
              <li key={item.id} className="list-row">
                <span className="list-text">
                  <span className="list-name">{item.name}</span>
                  <span className="list-meta muted">{item.location}</span>
                </span>
                <span className="list-amounts">
                  <span className="list-amount">
                    {formatMoney(item.price_cents * item.quantity_bought)}
                  </span>
                  {item.quantity_bought > 1 && (
                    <span className="list-meta muted">
                      {item.quantity_bought} × {formatMoney(item.price_cents)}
                    </span>
                  )}
                </span>
              </li>
            ))}
          </ul>

          <section className="card trip-total trip-total-line">
            <span className="muted">Trip total</span>
            <span className="trip-total-amount">{formatMoney(trip.total_cents)}</span>
          </section>
        </>
      )}
    </main>
  )
}
