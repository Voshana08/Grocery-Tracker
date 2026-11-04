// Icons used on more than one page: 24px viewBox, 2px round strokes, colour from the text.

export function Plus({ size = 20 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" aria-hidden="true">
      <path d="M12 5v14M5 12h14" />
    </svg>
  )
}

export function ChevronLeft() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M15 5l-7 7 7 7" />
    </svg>
  )
}

function LocationIcon({ children }) {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      {children}
    </svg>
  )
}

export function Fridge() {
  return (
    <LocationIcon>
      <rect x="6" y="2.5" width="12" height="19" rx="2.5" />
      <path d="M6 10h12M9 5.5v2M9 13v3" />
    </LocationIcon>
  )
}

export function Jar() {
  return (
    <LocationIcon>
      <rect x="6" y="7" width="12" height="14" rx="2.5" />
      <path d="M8 3.5h8V7H8zM6 12h12" />
    </LocationIcon>
  )
}

export function Bottle() {
  return (
    <LocationIcon>
      <path d="M10 3h4v3h-4zM9 6h6l1.5 4v9.5A1.5 1.5 0 0 1 15 21H9a1.5 1.5 0 0 1-1.5-1.5V10z" />
      <path d="M14 4.5h3.5" />
    </LocationIcon>
  )
}

export function Check() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor"
      strokeWidth="2.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
      <path d="M5 12.5l4.5 4.5L19 7.5" />
    </svg>
  )
}
