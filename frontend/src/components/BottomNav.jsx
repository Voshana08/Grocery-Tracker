import { NavLink } from 'react-router'

// Home / Trips / Spending tabs (DESIGN.md section 3). NavLink sets aria-current="page"
// on the tab for the current URL, and the CSS colours that one.
const TABS = [
  { to: '/', label: 'Home', icon: <path d="M4 11l8-6.5 8 6.5V20h-5v-5H9v5H4z" /> },
  { to: '/trips', label: 'Trips', icon: <path d="M6 3h12v18l-3-2-3 2-3-2-3 2zM9 8h6M9 12h6" /> },
  { to: '/spending', label: 'Spending', icon: <path d="M5 20V11M12 20V4M19 20v-7" /> },
]

export default function BottomNav() {
  return (
    <nav className="bottom-nav" aria-label="Main">
      {TABS.map((tab) => (
        <NavLink key={tab.to} to={tab.to} end>
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor"
            strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            {tab.icon}
          </svg>
          {tab.label}
        </NavLink>
      ))}
    </nav>
  )
}
