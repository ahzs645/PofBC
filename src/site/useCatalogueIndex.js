import { useCallback, useLayoutEffect, useRef, useState } from 'react'
import { writeHistory } from './browserHistory.js'

/** An index and its detail pages share one return target, including the search and focused card. */
export const useCatalogueIndex = (view) => {
  const cards = useRef({})
  const saved = globalThis.history?.state?.catalogueIndex
  const [query, updateQuery] = useState(() => saved?.view === view ? saved.query : '')
  const returnCard = useRef(saved?.view === view ? saved.card : null)

  useLayoutEffect(() => {
    if (returnCard.current) cards.current[returnCard.current]?.focus()
  }, [])

  const setQuery = (next) => {
    updateQuery(next)
    // If this index was restored with Back, keep its saved search current for the next visit.
    if (history.state?.catalogueIndex?.view === view) {
      writeHistory(location.href, { replace: true, state: {
        ...history.state, catalogueIndex: { view, query: next, card: null }
      } })
    }
  }

  const openCard = useCallback((url, card, indexState) => {
    writeHistory(location.href, { replace: true, state: {
      ...history.state, catalogueIndex: { ...indexState, view, query, card }
    } })
    writeHistory(url, { state: { catalogueFrom: view } })
  }, [query, view])

  const closeCard = useCallback((card, fallback) => {
    if (history.state?.catalogueFrom === view) {
      history.back()
      return
    }
    // A shared detail URL can have an unrelated site in the preceding history entry.
    fallback()
    requestAnimationFrame(() => cards.current[card]?.focus())
  }, [view])

  return { cards, query, setQuery, openCard, closeCard }
}
