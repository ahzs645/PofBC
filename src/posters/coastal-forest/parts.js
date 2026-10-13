// What this poster is made of, in the drawing's own units (viewBox 0 0 2400 3600).

export const PARTS = {
  overview: { label: 'Whole poster', box: { x: 0, y: 0, w: 2400, h: 3600 }, pad: 0.015 },
  photograph: { label: 'Photograph', hint: 'the supplied image, and the credit under it', box: { x: 154, y: 161, w: 2085, h: 2490 }, pad: 0.03, layer: '#photograph' },
  title: { label: 'Title', hint: 'Bookman JF Pro with chosen swashes', box: { x: 160, y: 2699, w: 808, h: 129 }, pad: 0.12, layer: '#title' },
  copy: { label: 'Copy', hint: 'four columns of transcribed text', box: { x: 162, y: 2731, w: 2074, h: 560 }, pad: 0.05, layer: '#copy' },
  logo: { label: 'Logo', hint: 'the crest identity, and a live studio', box: { x: 1844, y: 3160, w: 425, h: 102 }, pad: 0.35, layer: '#ministry' },
  slogan: { label: 'Slogan', hint: 'and the story of one tilde', box: { x: 164, y: 3313, w: 2074, h: 105 }, pad: 0.08, layer: '#slogan' }
}

export const ORDER = ['overview', 'photograph', 'title', 'copy', 'logo', 'slogan']
export const STEPS = ORDER.filter((id) => id !== 'overview').map((id) => ({ id, label: PARTS[id].label }))

// Hotspot regions, ordered so the smaller ones sit on top of the copy block.
export const REGIONS = ['photograph', 'copy', 'title', 'logo', 'slogan'].map((id) => ({ id, ...PARTS[id] }))

// The photo credit's own layer, reset from the supplied close-up: right-aligned in the black
// margin under the picture. It is framed with the photograph rather than being a part of its own.
export const CREDIT_LAYER = '#photo-credit'

// Where a swapped-in logo goes: the free area under the fourth column, above the slogan.
export const LOGO_SLOT = { x: 1844, y: 3060, w: 425, h: 232 }

// The copy layer's sections, found by the ids and accessible labels the builder wrote. Headings
// carry the section's own label, so they dim and zoom together with the columns beneath them.
export const SECTIONS = {
  intro: { label: 'Introduction', matches: (g) => g.id === 'introduction' },
  habitat: { label: 'Exceptional Habitat', matches: (g) => g.id.startsWith('habitat') || g.getAttribute('aria-label') === 'Exceptional Habitat' },
  early: { label: 'Early Exploitation', matches: (g) => g.id === 'early-exploitation' || g.getAttribute('aria-label') === 'Early Exploitation' },
  integrated: { label: 'Integrated Management', matches: (g) => g.id.startsWith('integrated') || g.getAttribute('aria-label') === 'Integrated Management' }
}
export const COPY_GROUPS = '#copy > g'

export const GLYPH_NOTES = {
  'F.swsh': ['F', 'Forest'],
  'r2.swsh': ['r', 'Forest'],
  's.swsh': ['s', 'Coastal, Forest'],
  'E.swsh': ['E', 'Environment'],
  'H.swsh': ['H', 'Home'],
  tilde: ['~', 'separator']
}

export const TOUR_SECONDS = 12
