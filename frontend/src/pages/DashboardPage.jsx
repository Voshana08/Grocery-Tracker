import { useEffect, useState } from 'react'
import { Link } from 'react-router'
import { api } from '../api/client.js'
import BottomNav from '../components/BottomNav.jsx'
import { Plus } from '../components/Icons.jsx'
import LocationTile from '../components/LocationTile.jsx'
import StatusBadge from '../components/StatusBadge.jsx'
import WeekRow from '../components/WeekRow.jsx'
import { formatLongDate, formatMoney, formatMonthName } from '../lib/format.js'

const plural = (count, word) => `${count} ${word}${count === 1 ? '' : 's'}`

export default function DashboardPage() {
  const [data, setData] = useState(null) // { dashboard, locations }
  const [error, setError] = useState(null)

  useEffect(() => {
    let ignore = false
    Promise.all([api('/dashboard'), api('/locations')])
      .then(([dashboard, locations]) => !ignore && setData({ dashboard, locations }))
      .catch((err) => !ignore && setError(err))
    return () => {
      ignore = true
    }
  }, [])

  return (
    <>
      <main className="page has-nav">
        <title>Home | Grocery Tracker</title>
        {error && (
          <p className="error-banner" role="alert">
            {error.message}
          </p>
        )}
        {!data && !error && <p className="muted">Loading…</p>}
        {data && <Dashboard {...data} />}
      </main>
      <BottomNav />
    </>
  )
}

function Dashboard({ dashboard, locations }) {
  const { today, month, week, low_and_out: toBuy } = dashboard
  return (
    <>
      <header className="greeting">
        <span className="muted">{formatLongDate(today)}</span>
        <h1>Hi there</h1>
      </header>

      <section className="card summary-card">
        <div className="month-spend">
          <span className="muted">Spent in {formatMonthName(today)} so far</span>
          <span className="month-spend-amount">{formatMoney(month.total_cents)}</span>
          <span className="muted">across {plural(month.trip_count, 'trip')}</span>
        </div>
        <div className="summary-week">
          <div className="summary-week-heading">
            <h2>This week</h2>
            <span className="muted">
              {plural(week.trip_count, 'trip')} · {formatMoney(week.total_cents)}
            </span>
          </div>
          <WeekRow days={week.days} today={today} />
        </div>
      </section>

      <Link to="/trips/new" className="button-primary dashboard-action">
        <Plus />
        Log a shopping trip
      </Link>

      <section className="dashboard-section">
        <h2>At home</h2>
        <div className="location-tiles">
          {locations.map((location) => (
            <LocationTile key={location.slug} location={location} />
          ))}
        </div>
      </section>

      <section className="dashboard-section">
        <div className="section-heading">
          <h2>Buy next time</h2>
          {toBuy.length > 0 && <span className="muted">{plural(toBuy.length, 'item')}</span>}
        </div>
        {toBuy.length === 0 ? (
          <p className="card nothing-low">Nothing running low. Nice.</p>
        ) : (
          <ul className="card list">
            {toBuy.map((item) => (
              <li key={item.id} className="list-row">
                <span className="list-text">
                  <span className="list-name">{item.name}</span>
                  <span className="list-meta muted">{item.location}</span>
                </span>
                <StatusBadge status={item.status} />
              </li>
            ))}
          </ul>
        )}
      </section>
    </>
  )
}
