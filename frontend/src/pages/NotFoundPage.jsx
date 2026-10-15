import { Link } from 'react-router'

export default function NotFoundPage() {
  return (
    <main className="page">
      <title>Page not found | Grocery Tracker</title>
      <div className="card empty-state">
        <h1>Page not found</h1>
        <p className="muted">This page doesn't exist yet.</p>
        <Link to="/">Go to Home</Link>
      </div>
    </main>
  )
}
