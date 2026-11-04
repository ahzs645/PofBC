/** Page changes get a Back/Forward entry; edits to the current page replace its entry. */
export const writeHistory = (url, { replace = false, state } = {}) => {
  if (!globalThis.history?.pushState) return false
  const href = String(url)
  if (!replace && href === globalThis.location.href) return false
  globalThis.history[replace ? 'replaceState' : 'pushState'](
    state === undefined ? (replace ? globalThis.history.state : null) : state,
    '', href
  )
  return true
}
