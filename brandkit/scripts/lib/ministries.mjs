// The ministries an era's signatures are set for, from PofBC's ministry history
// (src/ministries/ministryHistory.js): every ministry in existence at some point in [from, to].

import { pofbc } from './paths.mjs'

const slug = (value) => value.toLowerCase().replace(/^ministry of (the )?/, '').replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')

/** Department items `{ id, name, years, values: { ministry } }`, alphabetical, ids unique. */
export const ministriesBetween = async (from, to, { values = (name) => ({ ministry: name }) } = {}) => {
  const { MINISTRY_EPISODES } = await pofbc('src/ministries/ministryHistory.js')
  const seen = new Set()
  return MINISTRY_EPISODES
    .filter((episode) => episode.from <= to && (episode.to == null || episode.to >= from))
    .sort((a, b) => a.name.localeCompare(b.name) || a.from - b.from)
    .map((episode) => {
      let id = slug(episode.name) || 'ministry'
      if (seen.has(id)) id = `${id}-${episode.from}`
      seen.add(id)
      return { id, name: episode.name, years: `${episode.from}–${episode.to ?? ''}`, values: values(episode.name) }
    })
}
