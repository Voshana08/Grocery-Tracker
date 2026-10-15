const OPTIONS = [
  { value: 'plenty', label: 'Plenty' },
  { value: 'low', label: 'Low' },
  { value: 'out', label: 'Out' },
]

// Plenty / Low / Out buttons for one item. onChange(newStatus) runs on each tap.
export default function StatusControl({ itemName, status, onChange }) {
  return (
    <div className="status-control" role="group" aria-label={`Stock level for ${itemName}`}>
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
