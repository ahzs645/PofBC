// The Province's 1977 artwork, read straight from PofBC's own reconstruction: the Provincial
// Symbol (crest and ring) from src/assets/markup.js and every ministry of 1976–1986 from the
// ministry history. brandkit used to receive this as artwork.json, copied out of a PofBC checkout
// (its old scripts/import-pofbc.mjs); now that the generator lives here, it reads the source.

import { pofbc } from './paths.mjs'

export const provinceArtwork = async ({ from = 1976, to = 1986 } = {}) => {
  const { PROVINCIAL_MARK } = await pofbc('src/assets/markup.js')
  const { MINISTRY_EPISODES } = await pofbc('src/ministries/ministryHistory.js')
  const ministries = MINISTRY_EPISODES
    .filter((episode) => episode.from <= to && (episode.to == null || episode.to >= from))
    .sort((a, b) => a.name.localeCompare(b.name) || a.from - b.from)
    .map((episode) => ({ name: episode.name, from: episode.from, to: episode.to ?? null }))
  return {
    source: 'PofBC src/assets/markup.js (the Provincial Symbol, crest and ring) and src/ministries (ministry history)',
    symbol: { viewBox: [0, 0, PROVINCIAL_MARK.viewBox.width, PROVINCIAL_MARK.viewBox.height], markup: PROVINCIAL_MARK.inner },
    ministries
  }
}
