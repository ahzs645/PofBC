// Loads the BC Laws ministers' responsibilities data (amr.js, about 160 KB compressed) only when a
// card that shows it opens, so the rest of the government view does not carry it.
import { useEffect, useState } from 'react'

let loaded = null
let loading = null

export const useAmr = () => {
  const [amr, setAmr] = useState(loaded)
  useEffect(() => {
    if (loaded) return undefined
    let live = true
    loading ??= import('./amr.js').then((module) => { loaded = module; return module })
    loading.then((module) => { if (live) setAmr(module) })
    return () => { live = false }
  }, [])
  return amr
}
