// Marks that are not arrangements of anything.
//
// The generator is built on patterns: an identity, a lockup, a ministry, a colourway. Most of the
// Province's marks are one of those, which is why it can draw them. Some are not — they were drawn
// once, for one body, and follow no rule that generalises. BC Parks is the plain case: the flag
// symbol inside a frame, both words set alike, which is nothing the standards page describes and
// nothing any other ministry got.
//
// They are collected here rather than bent into the generator, because adding "Badge" beside
// "Horizontal" in a list of arrangements would say that any ministry can be set that way, and
// none can.

export const ONE_OFFS = [
  {
    id: 'bc-parks',
    label: 'BC Parks',
    body: 'BC Parks',
    years: 'from the 1980s',
    note: 'The flag symbol inside a rounded frame, with “Parks” set at the same size as “BC” — ' +
      'both words are the wordmark, not a ministry line under a symbol. The frame is a ' +
      'superellipse, which is what gives it sides that bow where a rounded rectangle’s run ' +
      'straight.',
    caveat: 'Proportions are read off a picture of the mark, not measured from artwork.',
    draw: { symbol: 'badge', ministry: 'Parks' },
    // Starting points, not separate marks. A mark gets one card in the gallery; these are offered
    // inside it, and every colour is editable from there anyway.
    presets: [
      { id: 'colour', label: 'Colour', ink: '#10069f', palette: 'official', background: '#ffffff' },
      { id: 'mono', label: 'One ink', ink: '#000000', palette: 'ink', background: '#ffffff' },
      { id: 'reverse', label: 'Reversed', ink: '#ffffff', palette: 'ink', background: '#10069f' }
    ]
  }
]

export const findOneOff = (id) => ONE_OFFS.find((entry) => entry.id === id)
