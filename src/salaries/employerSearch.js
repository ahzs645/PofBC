import { nameSearchTokens } from './nameSearch.js'

// Discovery aliases only: never replace disclosed employer names, slugs or source attribution.
// Keep additions explicit and sourced instead of inferring identities from matching initials.
const SEARCH_ALIASES = {
  'university-of-northern-bc': {
    names: ['UNBC'],
    source: 'https://www.unbc.ca/',
  },
  'university-of-victoria': {
    names: ['UVic'],
    source: 'https://www.uvic.ca/about-uvic/about-the-university/index.php',
  },
}

/**
 * Every query word must begin a word of an employer's disclosed names or explicit search aliases:
 * "lady" and "ladysmith" find the Town of Ladysmith, but "smith" does not.
 */
export const employerMatcher = (query) => {
  const words = nameSearchTokens(query)
  return (entry) => {
    if (!words.length) return false
    const labels = [...entry.names, entry.slug, ...(SEARCH_ALIASES[entry.slug]?.names ?? [])]
    const text = nameSearchTokens(labels.join(' '))
    return words.every((word) => text.some((each) => each.startsWith(word)))
  }
}
