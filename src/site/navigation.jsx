// Links between the site's views.
//
// Each view reads its place from the address bar when it opens, so a link to another view is just a
// query string: `{ view: 'internal', internal: 'forests' }` and so on. SiteLink renders it as a real
// link (so it can be copied or opened in a new tab) and, on a plain click, hands it to the App,
// which writes the address and swaps the view without a reload.

import { createContext, forwardRef, useContext } from 'react'

export const NavigationContext = createContext(null)

/** The query string for a set of view parameters, with empty ones left out. */
export const searchFor = (params) => {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    if (value !== null && value !== undefined && value !== '') search.set(key, String(value))
  }
  return `?${search}`
}

export const useNavigate = () => useContext(NavigationContext)

/** A link to another place on the site. `to` is the view's parameters. */
export const SiteLink = forwardRef(({ to, children, onClick, ...rest }, ref) => {
  const navigate = useNavigate()
  return (
    <a
      ref={ref}
      href={searchFor(to)}
      onClick={(event) => {
        onClick?.(event)
        if (!navigate || event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return
        event.preventDefault()
        navigate(to)
      }}
      {...rest}
    >
      {children}
    </a>
  )
})
SiteLink.displayName = 'SiteLink'
