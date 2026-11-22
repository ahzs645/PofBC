// Attaches the Expo 86 posters' drawings to their parts.

import { EXPO_86_POSTERS } from './posters.js'
import review from './review.webp'

const FIGURES = { 'expo-86-davidson': { review } }

const DRAWINGS = {
  'expo-86-davidson': () => import('./expo-86-davidson.svg?raw'),
  'expo-86-fiorucci': () => import('./expo-86-fiorucci.svg?raw'),
  'our-british-columbia': () => import('./our-british-columbia.svg?raw')
}

export const loaderFor = (id) => async () => {
  const { default: svgRaw } = await DRAWINGS[id]()
  const { parts, order, regions, spotlight } = EXPO_86_POSTERS[id]
  return { svgRaw, parts, order, regions, spotlight, figures: FIGURES[id] }
}
