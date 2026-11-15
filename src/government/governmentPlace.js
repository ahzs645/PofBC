import { canonicalId } from './episodes.js'
import { instrumentById } from './instruments.js'
import { relatedBodyById } from './relatedBodies.js'
import { FIRST_YEAR, PRESENT_YEAR } from './snapshot.js'

const validYear = (value) => Number.isInteger(value) && value >= FIRST_YEAR && value <= PRESENT_YEAR

/** Read a shared government link, including older gallery/salary links that only specify a node. */
export const readGovernmentPlace = (search = '') => {
  const params = new URLSearchParams(search)
  const year = Number(params.get('year'))
  const compare = Number(params.get('compare'))
  const mode = params.get('mode')
  const related = mode === 'related' || Boolean(relatedBodyById(params.get('node')))
  return {
    // The related catalogue describes current governance, even when a salary disclosure link
    // supplies its reporting year. It does not project that description into the historical graph.
    year: related ? PRESENT_YEAR : validYear(year) ? year : PRESENT_YEAR,
    // Preserve links made before an episode's name was corrected.
    node: params.get('node') ? canonicalId(params.get('node')) : null,
    mode: related ? 'related' : ['graph', 'list', 'compare'].includes(mode) ? mode : 'graph',
    compare: validYear(compare) ? compare : null,
    undated: params.get('undated') !== '0',
    local: params.get('local') === '1',
    instrument: instrumentById(params.get('instrument') ?? '') ? params.get('instrument') : null
  }
}
