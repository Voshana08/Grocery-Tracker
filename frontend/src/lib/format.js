// Money and dates (CLAUDE.md section 4): no other file formats or parses them.

// "4.50" -> 450, "4.5" -> 450, "4" -> 400. Anything else ("4.555", "abc", "-1", "") -> null.
// Splits on the dot instead of using floating-point maths, which can turn 4.35 into 434.99...
export function dollarsToCents(text) {
  const trimmed = text.trim()
  if (!/^\d+(\.\d{1,2})?$/.test(trimmed)) return null
  const [dollars, cents = ''] = trimmed.split('.')
  return Number(dollars) * 100 + Number(cents.padEnd(2, '0'))
}

// 450 -> "$4.50", 41260 -> "$412.60"
export function formatMoney(cents) {
  return new Intl.NumberFormat('en-AU', { style: 'currency', currency: 'AUD' }).format(cents / 100)
}

// Today's date in Melbourne as "2026-10-15", whatever time zone the phone is set to.
export function todayInMelbourne() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'Australia/Melbourne' }).format(new Date())
}
