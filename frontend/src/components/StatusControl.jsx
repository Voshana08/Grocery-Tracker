const OPTIONS = [
  { value: 'plenty', label: 'Plenty' },
  { value: 'low', label: 'Low' },
  { value: 'out', label: 'Out' },
]

// Plenty / Low / Out buttons. onChange(newStatus) runs on each tap.
// wide: full-width version used in forms (Add item); the compact one sits on item rows.
export default function StatusControl({ itemName, status, onChange, wide = false }) {
  const label = itemName ? `Stock level for ${itemName}` : 'Stock level'
  return (
    <div className={wide ? 'status-control wide' : 'status-control'} role="group" aria-label={label}>
      {OPTIONS.map((option) => (
        <button
          key={option.value}
          type="button"
          data-status={option.value}
          aria-pressed={status === option.value}
          onClick={onChange ? () => onChange(option.value) : undefined}
        >
          {option.label}
        </button>
      ))}
    </div>
  )
}
