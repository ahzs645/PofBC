import { useEffect, useState } from 'react'
import { assetUrl } from './healthStoryData.js'

const BASE = import.meta.env?.BASE_URL || '/'
const INITIAL = { phase: 'idle', comparison: null, collections: {}, error: null }

export function useBoundaryData(enabled) {
  const [state, setState] = useState(INITIAL)
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    if (!enabled || state.phase === 'ready') return undefined
    const controller = new AbortController()
    const load = async (file) => {
      const response = await fetch(assetUrl(file, BASE), { signal: controller.signal })
      if (!response.ok) throw new Error('The boundary files could not be loaded. Please try again.')
      return response.json()
    }
    setState((previous) => ({ ...previous, phase: 'loading', error: null }))
    load('boundary-comparison.json').then(async (comparison) => {
      const datasets = Object.entries(comparison.datasets ?? {}).filter(([, dataset]) => dataset.file)
      const collections = Object.fromEntries(await Promise.all(datasets.map(async ([id, dataset]) => {
        const collection = await load(dataset.file)
        if (collection.type !== 'FeatureCollection' || !Array.isArray(collection.features)) {
          throw new Error('A boundary file has an unexpected format.')
        }
        return [id, collection]
      })))
      if (!controller.signal.aborted) setState({ phase: 'ready', comparison, collections, error: null })
    }).catch((error) => {
      if (!controller.signal.aborted) setState({ ...INITIAL, phase: 'error', error: error.message })
    })
    return () => controller.abort()
  }, [enabled, attempt])
  return { ...state, retry: () => { setState(INITIAL); setAttempt((value) => value + 1) } }
}

export default useBoundaryData
