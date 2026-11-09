import { useEffect, useState } from 'react'
import { assetUrl } from './healthStoryData.js'

const BASE = import.meta.env?.BASE_URL || '/'
const cache = new Map()

function load(path) {
  if (!cache.has(path)) {
    cache.set(path, fetch(assetUrl(path, BASE)).then((response) => {
      if (!response.ok) throw new Error('The map data could not be loaded.')
      return response.json()
    }).then((collection) => {
      if (collection.type !== 'FeatureCollection') throw new Error('A map file has an unexpected format.')
      return collection
    }).catch((error) => { cache.delete(path); throw error }))
  }
  return cache.get(path)
}

// Loads one framework's boundaries plus the province base layer, and the
// georectified printed map only when the overlay is switched on.
export function useHealthGeography(framework, overlayMapId) {
  const [state, setState] = useState({ phase: 'loading', base: null, regions: null, overlay: null, error: null })
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    let live = true
    setState((previous) => ({ ...previous, phase: previous.regions ? 'updating' : 'loading', error: null }))
    Promise.all([
      load('boundaries/authorities-2001.geojson'),
      load(`boundaries/${framework}.geojson`),
      overlayMapId ? load(`rectified/${overlayMapId}.geojson`) : Promise.resolve(null),
    ]).then(([base, regions, overlay]) => {
      if (live) setState({ phase: 'ready', base, regions, overlay, error: null })
    }).catch((error) => {
      if (live) setState({ phase: 'error', base: null, regions: null, overlay: null, error: error.message })
    })
    return () => { live = false }
  }, [framework, overlayMapId, attempt])
  return { ...state, retry: () => setAttempt((value) => value + 1) }
}

export default useHealthGeography
