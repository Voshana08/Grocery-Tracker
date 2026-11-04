const LABELS = { low: 'Low', out: 'Out' }

// The pill on Buy next time rows. Plenty isn't badged in lists (DESIGN.md section 3).
export default function StatusBadge({ status }) {
  return (
    <span className="status-badge" data-status={status}>
      {LABELS[status]}
    </span>
  )
}
