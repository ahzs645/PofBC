const project = 'https://www.behance.net/gallery/31832877/Destination-British-Columbia-Rebranding'
const sourceId = 'ethos-destination-bc-portfolio-2016'
const creditsId = 'applied-arts-destination-bc-2016'
const date = '2016-02-11'

export const tourismRebrandingSources = [
  { id: sourceId, title: 'Destination British Columbia Rebranding', shortTitle: 'Original design portfolio',
    publisher: 'Gabriel Lefebvre and Rachel Lecompte, Behance', date, url: project,
    description: 'Lefebvre and Lecompte published their account of the identity on February 11, 2016. The date identifies the portfolio publication.' },
  { id: creditsId, title: 'Super, Natural British Columbia, Complete Design Program', shortTitle: 'Design credits',
    publisher: 'Applied Arts', date: '2016', url: 'https://www.appliedartsmag.com/winners/design/super-natural-british-columbia-w348/?year=2016',
    description: 'The award entry credits ethos, Gabriel Lefebvre for creative direction, graphic design and typography, Rachel Lecompte for copywriting, and Gae Wakabayashi for account direction.' }
]

// Module links open the individual image in the creators’ portfolio. The local renditions
// retain the full composition, resized to fit 1100 × 1350 and encoded as WebP for display.
const specimen = (name, label, caption, module, sourceImageUrl, width, height) => ({
  file: 'tourism/rebranding-2016/' + name + '.webp', label, caption, alt: caption,
  width, height, date, dateLabel: 'Portfolio publication', sourceId,
  sourceUrl: project + '/modules/' + module, sourceLocator: 'Portfolio image · ' + label,
  sourceImageUrl, evidenceType: 'portfolio-preview', downloadLabel: 'portfolio preview'
})

const images = {
  "maple-leaf": specimen("maple-leaf", "BC maple leaf",
    "A small black maple leaf encloses the letters BC. The portfolio displays this emblem at 49 × 48 pixels.",
    "214263724", "https://mir-s3-cdn-cf.behance.net/project_modules/max_632_webp/d67f6431832877.56bce7641c549.jpg", 49, 48),
  "logo-block": specimen("logo-block", "Carved logo block",
    "The four lines of the wordmark sit closely together on the face of the wood block.",
    "202901901", "https://mir-s3-cdn-cf.behance.net/project_modules/1400_webp/90a6ed31832877.5663026c858d6.jpg", 1100, 659),
  "alphabet-block": specimen("alphabet-block", "Carved alphabet detail",
    "A close view of the carved alphabet shows the cut edges of letters, numbers and punctuation.",
    "202901903", "https://mir-s3-cdn-cf.behance.net/project_modules/1400_webp/a77d8e31832877.5663026c871f3.jpg", 1100, 722),
  "printed-logo": specimen("printed-logo", "Wordmark impression",
    "The narrow black letters stack into a single shape on an unprinted ground.",
    "202961911", "https://mir-s3-cdn-cf.behance.net/project_modules/1400_webp/dab4fa31832877.5663a9e740f84.jpg", 1100, 659),
  "type-introduction": specimen("type-introduction", "Type in the forest",
    "White display lettering introduces Great Forest against a dense stand of trees. Photograph by Spencer Robertson.",
    "202986739", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/2b751431832877.56642177afb93.jpg", 1100, 743),
  "type-specimen": specimen("type-specimen", "Great Forest character set",
    "The specimen compares the regular letters, small capitals, special glyphs and overscore and underscore forms.",
    "202988677", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/fffb3f31832877.5664285e4916e.jpg", 1100, 845),
  "palette": specimen("palette", "Landscape colour references",
    "Two rows of natural surfaces pair colour names with leaves, rock, water, bark and snow.",
    "205099123", "https://mir-s3-cdn-cf.behance.net/project_modules/max_632_webp/e6ade731832877.5676bc661de30.jpg", 1100, 441),
  "headlines": specimen("headlines", "Voice and lettering",
    "Six short phrases show how the typeface’s widths and strokes change the shape of a headline.",
    "202962231", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/01591a31832877.5663ac0ae1785.jpg", 1100, 845),
  "icons": specimen("icons", "Landscape pictograms",
    "Five line drawings depict a settlement, a wave, a stand of trees, mountains and a low sun.",
    "203496491", "https://mir-s3-cdn-cf.behance.net/project_modules/max_632_webp/921c8e31832877.566838463de68.jpg", 1100, 303),
  "photography": specimen("photography", "Photography board",
    "Coast, forest, rock, water and people appear together on the photographic board. The project credits Garrett Grove, Paul Colangelo, Duiken Redactie, Adam Gibbs, Anthony Taylor, Camila Massu and Eric Berger.",
    "214231134", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/607cc831832877.56bcc4817c513.jpg", 1100, 551),
  "newspaper": specimen("newspaper", "Newspaper advertisement",
    "A vertical newspaper advertisement pairs a forest photograph with the destination signature. Photograph credited to quixotically-insane.",
    "202961161", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/24068431832877.5663a60731fcd.jpg", 900, 1350),
  "brochures": specimen("brochures", "Regional brochures",
    "Three white covers crop oversized black place names at their edges.",
    "202901907", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/52714931832877.5663026c89d73.jpg", 1100, 733),
  "magazine": specimen("magazine", "Magazine spread",
    "An open magazine places a full-page landscape opposite columns of editorial copy.",
    "202901909", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/cdc13a31832877.5663026c8b58e.jpg", 1100, 739),
  "outdoor": specimen("outdoor", "Outdoor advertisement",
    "A framed outdoor placement sets a small headline and the provincial signature over a blue-green photograph. Photograph by Garrett Grove.",
    "203496489", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/2b2d0231832877.566838463c98c.jpg", 1100, 733),
  "van": specimen("van", "Vehicle decal",
    "A maple leaf appears on the side panel of a blue camper van, just behind the windows. Photograph by William Woodward.",
    "202901913", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/34b8e931832877.5663026c8e41d.jpg", 1100, 660),
  "office": specimen("office", "Office lettering",
    "Overlapping lines of place names turn the office wall into a field of black lettering.",
    "202901915", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/311eb531832877.5663026c8ffbc.jpg", 1100, 699),
  "map": specimen("map", "Typographic map",
    "A framed poster arranges names horizontally and vertically to suggest provincial geography.",
    "230681465", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/665f8e31832877.572f9b02aa54c.jpg", 1100, 734),
  "stationery": specimen("stationery", "Office stationery",
    "Letterhead, an envelope and cards pair the small wordmark with densely printed reverses.",
    "202901917", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/026de331832877.5663026c91aa3.jpg", 1100, 733),
  "field-objects": specimen("field-objects", "Bottle and knife sheath",
    "The identity appears on a metal bottle and a leather sheath photographed outdoors.",
    "214259798", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/14c91831832877.56bce2a61fc7c.jpg", 1100, 770),
  "tote": specimen("tote", "Produce tote",
    "A canvas bag carries a two-line message about locally grown produce.",
    "202901921", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/36e21d31832877.5663026c94af4.jpg", 1100, 733),
  "statement-shirt": specimen("statement-shirt", "Lettered shirt",
    "A short environmental message appears in loose green lettering across the back of the shirt.",
    "202901923", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/08901c31832877.5663026c9657c.jpg", 1100, 816),
  "notebook-outside": specimen("notebook-outside", "Notebook cover",
    "A leather wrap and cord hold the travel notebook closed.",
    "202960329", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/46291431832877.5663a273c38aa.jpg", 1100, 733),
  "notebook-inside": specimen("notebook-inside", "Notebook interior",
    "A narrow stack of letters appears on the first page inside the leather cover.",
    "202960331", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/10aee131832877.5663a273c50b0.jpg", 1100, 733),
  "leaf-shirt": specimen("leaf-shirt", "Maple leaf shirt",
    "A small red maple leaf sits on the chest of a white shirt.",
    "202960907", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/be52fd31832877.5663a5015b808.jpg", 1100, 660),
  "trade-show": specimen("trade-show", "Exhibition banners",
    "Whistler and Tofino photographs flank a banner filled with place names. Photographs by Reuben Krabbe and Sarah Lee.",
    "202988785", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/2f1d5d31832877.566428d036627.jpg", 1100, 827),
  "logo-history": specimen("logo-history", "Two generations of the wordmark",
    "The portfolio pairs the earlier oval landscape emblem with the compact carved wordmark.",
    "202990087", "https://mir-s3-cdn-cf.behance.net/project_modules/fs_webp/747a6d31832877.56642c7c9e565.jpg", 1100, 659)
}

const guidePage = (page) => '?view=initiatives&initiative=tourism&section=brand-guide&page=' + page

export const tourismRebrandingSection = {
  id: 'rebranding', label: '2016 design portfolio', type: 'records',
  title: 'The wood-carved tourism identity', eyebrow: 'Design portfolio · February 2016',
  description: 'Gabriel Lefebvre and Rachel Lecompte show how ethos used carved lettering across print, objects and public spaces. Lefebvre led creative direction, design and typography. Lecompte wrote the copy, and Gae Wakabayashi directed the account.',
  featuredId: 'rebrand-carved-wordmark',
  records: [
    { id: 'rebrand-carved-wordmark', title: 'From wood block to wordmark', kind: 'identity design',
      description: 'A carved block and its impression show the construction of the stacked signature. A comparison with the older oval emblem records the change in design. The small maple leaf carries the letters BC.',
      images: [images['logo-block'], images['alphabet-block'], images['printed-logo'], images['logo-history'], images['maple-leaf']],
      links: [
        { label: 'The welcome sign and its earlier lettering', url: '?view=signs&sign=super-natural' },
        { label: 'Watch the brand launch film linked by the designers', url: 'https://www.youtube.com/watch?v=dNFrZNjs2ng' }
      ] },
    { id: 'rebrand-great-forest', title: 'Great Forest in wood and type', kind: 'typography',
      description: 'The designers took the width of a carving tool as their unit for spacing letters and lines. The character sheet shows how alternate forms and ligatures let words nest together.',
      images: [images['type-specimen'], images['type-introduction']],
      links: [
        { label: 'Watch the ethos Great Forest tutorial', url: 'https://vimeo.com/155026531' },
        { label: 'Great Forest in the 2021 guide', url: guidePage(59) }
      ] },
    { id: 'rebrand-landscape', title: 'Landscape, colour and photography', kind: 'art direction',
      description: 'The palette begins with objects and surfaces. Photographs of water, foliage, earth and rock show what a colour looks like in the landscape. A second board sets those colours in scenes from across the province.',
      images: [images.palette, images.photography],
      links: [{ label: 'The colour specifications in the 2021 guide', url: guidePage(64) }] },
    { id: 'rebrand-language', title: 'Short copy and pictograms', kind: 'brand language',
      description: 'Short phrases let the display lettering act as both text and image. A set of five pictograms uses a few strokes to suggest places and landscapes.',
      images: [images.headlines, images.icons],
      links: [{ label: 'Tone of voice in the 2021 guide', url: guidePage(66) }] },
    { id: 'rebrand-print', title: 'Brochures, newspapers and advertising', kind: 'print design',
      description: 'Regional brochure covers enlarge place names until the letters run off the edge. Newspaper, magazine and outdoor layouts show how the lettering sits beside or over a photograph.',
      images: [images.brochures, images.newspaper, images.magazine, images.outdoor] },
    { id: 'rebrand-place-names', title: 'Maps, walls and stationery', kind: 'environmental and print design',
      description: 'Place names form a map on paper and a pattern across an office wall. The same lettering fills the backs of stationery while the wordmark sits alone on the front.',
      images: [images.map, images.office, images.stationery] },
    { id: 'rebrand-objects', title: 'Objects for the journey', kind: 'applied identity',
      description: 'A notebook, tote and shirts give the lettering different scales. The compact symbol fits surfaces as small as a chest emblem and a vehicle decal.',
      images: [images.tote, images['statement-shirt'], images['leaf-shirt'], images['notebook-outside'], images['notebook-inside'], images['field-objects'], images.van] },
    { id: 'rebrand-exhibition', title: 'Whistler and Tofino on the exhibition floor', kind: 'exhibition design',
      description: 'Two photographic banners place a person within mountain and coastal landscapes. A third panel between them names places across the province in stacked type.',
      images: [images['trade-show']] }
  ].map((record) => ({ ...record, sourceRefs: [{ sourceId }, { sourceId: creditsId }] }))
}
