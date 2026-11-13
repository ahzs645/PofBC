// Records for things the printed pieces name but the rest of the site has no entry for: a unit of
// a ministry, a ship, the people credited. Each says only what its sources support, and names the
// pieces it is read from. The connection registry (connections.js) points at them, and a piece's
// overview opens them in place.
//
// Data only. `facts` is [[label, value], …]; `seenOn` is where on the pieces it is printed;
// `sources` are pages elsewhere. `limits` says what is not established, and is always shown.

export const RECORDS = {
  'forest-practices-branch': {
    kind: 'Ministry unit',
    title: 'Forest Practices Branch',
    summary: 'A branch of the Ministry of Forests, and the unit named in the signature of three pieces here. On each it stands under the ministry’s name, beneath the Province’s arms.',
    facts: [
      ['Named on', 'Wildlife Trees; Shattering the Environment; Explosion in Slow Motion'],
      ['Parent', 'Ministry of Forests (the name the ministry held from 1988 to 2005)'],
      ['Not to be confused with', 'the Forest Practices Board, an independent watchdog created in 1995 under the Forest Practices Code. The Board has a record in the Government view; the Branch does not.']
    ],
    seenOn: [
      { poster: 'wildlife-trees', part: 'ministry', note: 'In green, beside the Forest Service tree oval' },
      { poster: 'shattering-the-environment', part: 'signature', note: 'In black, under the address' },
      { poster: 'explosion-in-slow-motion', part: 'signature', note: 'In black, at the foot of the sheet' }
    ],
    limits: 'When the Branch was formed, renamed or wound up is not established here; this record rests on the three signatures alone. It is not yet a body in the Government view.',
    sources: [
      { label: 'Forest Practices Board, about the Board', href: 'https://www.bcfpb.ca/board/' }
    ]
  },
  'queen-of-sidney-vessel': {
    kind: 'Vessel',
    title: 'Queen of Sidney',
    summary: 'The ship on the decal. She was built as Sidney, one of the first two ferries of the provincial fleet, and took the name on the ribbon three years into her service.',
    facts: [
      ['Built', 'Victoria Machinery Depot, Victoria, as yard number 85'],
      ['Laid down', '9 May 1959'],
      ['Launched', '6 October 1959'],
      ['Entered service', '15 June 1960, between Victoria and Vancouver, as Sidney'],
      ['Renamed', 'Queen of Sidney in 1963, when the fleet’s larger ships were given “Queen of” names'],
      ['Retired', 'November 2000; sold in 2002']
    ],
    seenOn: [
      { poster: 'queen-of-sidney', part: 'ferry', note: 'The ship, drawn bow-on inside the wheel' },
      { poster: 'queen-of-sidney', part: 'ribbon', note: 'Her name, in white capitals' }
    ],
    limits: 'From a secondary source, which itself disagrees in places about her last years. If the 1963 renaming holds, a sticker with this name is no earlier than that; her livery and configuration in the drawing have not yet been compared with dated photographs, so the decal stays undated.',
    sources: [
      { label: 'Wikipedia, Sidney-class ferry', href: 'https://en.wikipedia.org/wiki/Sidney-class_ferry' }
    ]
  },
  'noxious-weeds-credits': {
    kind: 'Creators, as printed',
    title: 'Who made the weed posters',
    summary: 'The two posters print their credits in small capitals, role by role. Together they show how a public campaign was put together: writers, art directors, a designer, a photographer, an illustrator and a lithographer.',
    facts: [
      ['Susan Turner', 'Copy, on both posters'],
      ['Dwaine Brooke', 'Copy, on both posters'],
      ['Paul Nystedt', 'Art direction, on both posters'],
      ['Denton Pendergast', 'Art direction on both posters; design of Explosion in Slow Motion'],
      ['Rocket Science Design', 'Design of Shattering the Environment'],
      ['Dion Manastyrski', 'Photography of the weeds, on both posters'],
      ['Gunter Marx Photography', 'The background landscape of Shattering the Environment'],
      ['Soren Henrich', 'Illustration, on Explosion in Slow Motion'],
      ['Watermark Lithography', 'Compositing and film, on both posters']
    ],
    seenOn: [
      { poster: 'shattering-the-environment', part: 'credits', note: 'Six lines under the address' },
      { poster: 'explosion-in-slow-motion', part: 'action', note: 'In small capitals above the band at the foot of the sheet' }
    ],
    limits: 'Names and roles exactly as the posters print them. None has been identified independently, and the screen leaflet credits no one.',
    sources: []
  },
  'wildlife-trees-artist': {
    kind: 'Creator, from a mark',
    title: 'd.g.',
    summary: 'The only signature on Wildlife Trees: “d.g.01”, in the grass at the foot of the tree. Probably the artist’s initials and a year.',
    facts: [
      ['Mark', '“d.g.01”'],
      ['Read as', 'initials, and 2001: an inference'],
      ['Credited elsewhere on the sheet', 'no one']
    ],
    seenOn: [
      { poster: 'wildlife-trees', part: 'signature', note: 'In the grass, right of the roots' }
    ],
    limits: 'Who d.g. was is not established. The year, if it is one, would date the drawing, not the printing.',
    sources: []
  }
}
