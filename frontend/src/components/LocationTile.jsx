import { Link } from 'react-router'
import { Bottle, Fridge, Jar } from './Icons.jsx'

const ICONS = { fridge: Fridge, pantry: Jar, cleaning: Bottle }

// "1 out · 2 low", "2 low" or "All stocked". Out comes first because it's the most urgent.
function statusLine({ low_count: low, out_count: out }) {
  if (out > 0 && low > 0) return `${out} out · ${low} low`
  if (out > 0) return `${out} out`
  if (low > 0) return `${low} low`
  return 'All stocked'
}

export default function LocationTile({ location }) {
  const Icon = ICONS[location.slug] ?? Jar
  const needed = location.low_count + location.out_count
  return (
    // fromApp: arriving from here isn't a tag tap, so the location page hides its chip.
    <Link to={`/t/${location.slug}`} state={{ fromApp: true }} className="card location-tile">
      <Icon />
      <span className="location-tile-name">{location.name}</span>
      <span className={needed > 0 ? 'location-tile-status' : 'location-tile-status stocked'}>
        {statusLine(location)}
      </span>
    </Link>
  )
}
