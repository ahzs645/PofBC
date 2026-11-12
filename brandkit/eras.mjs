// The Province of British Columbia's visual identities, oldest first: one brandkit brand each.
//
// `id` is the brand's id (and its pack's file name); `script` writes its brand.json into
// <out>/<id>/ after brandkit/sources/<id>/ has been copied there. `years` are working dates,
// qualified where no source fixes them.

export const ERAS = [
  {
    id: 'bc-province-engraved-arms',
    label: 'Engraved arms',
    years: 'before 1977',
    script: './scripts/eras/engraved-arms.mjs',
    summary: 'The full coat of arms, engraved, over formal script: the Province before the 1977 Visual Identity Program. Starts with Grace M. McCarthy’s calling card.'
  },
  {
    id: 'bc-province-1977',
    label: 'Visual Identity Program (crest and ring)',
    years: '1977 – about 1983',
    script: './scripts/eras/province-1977.mjs',
    summary: 'The Provincial Symbol, crest and ring, with Helvetica signatures for every ministry: the four manuals of 1977.'
  },
  {
    id: 'bc-province-flag',
    label: 'The flag logo',
    years: 'about 1983 – 2005',
    script: './scripts/eras/flag.mjs',
    summary: 'BC beside the waving provincial flag, with a ministry set beside or below it.'
  },
  {
    id: 'bc-province-arms',
    label: 'Coat of arms and BRITISH COLUMBIA wordmark',
    years: 'after the flag logo (dates unconfirmed)',
    script: './scripts/eras/arms.mjs',
    summary: 'The full achievement of arms with the outlined BRITISH COLUMBIA wordmark, and a ministry set in Helvetica against it.'
  },
  {
    id: 'bc-province-current',
    label: 'The BC mark',
    years: '2011 – present',
    script: './scripts/eras/current.mjs',
    summary: 'The Province’s published BC mark (sun, mountains and sea) with each ministry set in its Garamond alphabet.'
  }
]

export const eraById = (id) => ERAS.find((era) => era.id === id)
