import { useEffect, useRef, useState } from 'react'
import { writeHistory } from '../site/browserHistory.js'
import { readSalaryPlace, salaryPlaceUrl } from './viewState.js'

const readLocation = () => ({
  place: readSalaryPlace(globalThis.location?.search ?? ''),
  trail: globalThis.history?.state?.salaryTrail ?? []
})

/** Keep the address, browser history and salary Back link on the same navigation path. */
export const useSalaryPlace = () => {
  const [location, setLocation] = useState(readLocation)
  const current = useRef(location)

  useEffect(() => {
    const restore = () => {
      current.current = readLocation()
      setLocation(current.current)
    }
    globalThis.addEventListener('popstate', restore)
    return () => globalThis.removeEventListener('popstate', restore)
  }, [])

  const commit = (place, trail, replace) => {
    const url = salaryPlaceUrl(globalThis.location.href, place)
    if (!writeHistory(url, { replace, state: { ...globalThis.history.state, salaryTrail: trail } })) return
    current.current = { place, trail }
    setLocation(current.current)
  }

  // Typing and filters update one entry, so Back never walks through individual keystrokes.
  const setPlace = (update) => {
    const { place, trail } = current.current
    commit(typeof update === 'function' ? update(place) : update, trail, true)
  }
  const go = (place, label) => commit(place, [...current.current.trail, { label }], false)
  const goBack = (fallback) => {
    if (current.current.trail.length) globalThis.history.back()
    // A shared link has no local history. Its Back link opens the employer or searchable root.
    else commit(fallback, [], true)
  }

  return { ...location, setPlace, go, goBack }
}
