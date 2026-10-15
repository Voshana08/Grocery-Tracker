// The only place the app calls fetch (CLAUDE.md section 4).

export class ApiError extends Error {
  constructor(message, status, fields = {}) {
    super(message)
    this.status = status // 0 means the server could not be reached
    this.fields = fields // 422 only: { product_name: "...", "items.2.price_cents": "..." }
  }
}

// FastAPI's 422 detail is a list like [{ loc: ["body", "items", 2, "price_cents"], msg: "..." }].
// Keyed by path without "body": "category_id", or "items.2.price_cents" for row 3 of a trip.
function fieldErrors(detail) {
  if (!Array.isArray(detail)) return {}
  return Object.fromEntries(detail.map((error) => [error.loc.slice(1).join('.'), error.msg]))
}

export async function api(path, options = {}) {
  const headers = options.body ? { 'Content-Type': 'application/json' } : {}
  let response
  try {
    response = await fetch(`/api${path}`, { credentials: 'include', headers, ...options })
  } catch {
    throw new ApiError("Can't reach Grocery Tracker. Check your connection and try again.", 0)
  }

  // Not logged in: go to the login page, then come back here. The auth calls
  // themselves get the 401 instead, so the login form can show its error.
  if (response.status === 401 && !path.startsWith('/auth/')) {
    const here = window.location.pathname + window.location.search
    window.location.assign(`/login?next=${encodeURIComponent(here)}`)
    throw new ApiError('Please log in.', 401)
  }

  const data = await response.json().catch(() => null)
  if (!response.ok) {
    const fields = fieldErrors(data?.detail)
    const message =
      typeof data?.detail === 'string'
        ? data.detail
        : (Object.values(fields)[0] ?? 'Something went wrong.')
    throw new ApiError(message, response.status, fields)
  }
  return data
}
