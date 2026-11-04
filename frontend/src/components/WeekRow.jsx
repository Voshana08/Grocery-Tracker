import { formatWeekday } from '../lib/format.js'
import { Check } from './Icons.jsx'

function dayState(day, today) {
  if (day.trip_count > 0) return 'trip'
  return day.day < today ? 'past' : 'future' // ISO dates sort like text
}

// "Monday, 1 trip", "Monday, 2 trips", "Tuesday, no trip"
function dayLabel(day) {
  const count = day.trip_count
  const trips = count === 0 ? 'no trip' : `${count} ${count === 1 ? 'trip' : 'trips'}`
  return `${formatWeekday(day.day)}, ${trips}`
}

// Seven circles, Monday to Sunday. Trip days also get a tick, so colour isn't the only signal.
export default function WeekRow({ days, today }) {
  return (
    <>
      <ol className="week-row">
        {days.map((day) => (
          <li key={day.day} className="week-day">
            <span className="week-circle" data-state={dayState(day, today)} role="img"
              aria-label={dayLabel(day)}>
              {day.trip_count > 0 && <Check />}
            </span>
            <span className={day.day === today ? 'week-letter today' : 'week-letter'}
              aria-hidden="true">
              {formatWeekday(day.day)[0]}
            </span>
          </li>
        ))}
      </ol>
      <p className="week-caption muted">Days with a shopping trip are ticked</p>
    </>
  )
}
