// The Noxious Weeds pieces: the Ministry of Forests' Forest Practices Branch campaign against
// invasive plants, as three supplied PDFs — a screen leaflet (its file made in 1999) and two posters
// (theirs in 2000). Those are the files' creation dates, not publication dates. Their
// parts, what the panels say, and the stories. Data only; the drawings are attached in ./index.js.
//
// The drawings are built from the PDFs by artwork/posters/noxious-weeds/build.py, which also
// measures where each part was found (the *.parts.js beside this file): a part's frame and its
// hotspots come from there, not from numbers typed here. A part's layer is every element the build
// gave its name (`data-part`); a plant that is part of a photograph has a highlight, a masked copy
// of the photograph, that the spotlight keeps bright.
//
// Panels are blocks, as in ../forest-service/posters.js; `story` is what the part says in story mode.

import { POSTERS } from '../catalogue.js'
import BEWARE_FOUND from './beware-these-alien-invaders.parts.js'
import SHATTERING_FOUND from './shattering-the-environment.parts.js'
import EXPLOSION_FOUND from './explosion-in-slow-motion.parts.js'

const BEWARE = 'beware-these-alien-invaders'
const SHATTERING = 'shattering-the-environment'
const EXPLOSION = 'explosion-in-slow-motion'

// ── Shared context ──────────────────────────────────────────────────────────────────────────────

const ministry = (year) => ({
  label: `Ministry of Forests, in ${year}`,
  note: `Government · ${year}: the ministry that signs the campaign, and its lockup in the identity of the day`,
  to: { view: 'government', year, node: 'ministry-of-forests-1988' }
})
const WILDLIFE_TREES_SIGNATURE = {
  label: 'The same signature on Wildlife Trees',
  note: 'Posters · the Forest Practices Branch’s poster of a habitat tree',
  to: { view: 'posters', poster: 'wildlife-trees', part: 'ministry' }
}
const on = (poster, part, note) => ({ label: POSTERS[poster].title, note, to: { view: 'posters', poster, part } })

const SUBSTITUTE_TYPE = 'The copy is set in substitutes. The PDF names Univers and Eurostile but does not carry them, so every copy of the file has always been set in whatever the viewer had; here it is set deliberately, in TeX Gyre Heros, TeX Gyre Heros Cn, Saira Condensed and Michroma, at the positions the PDF gives each letter.'
const SOURCE_NOTE = 'Rebuilt from the supplied PDF: its photographs are the PDF’s own JPEG images, unaltered; its lettering is redrawn as outlines.'

/** A part as the viewer takes it, its frame and hotspots from what the build measured. */
const parts = (found, defs) => Object.fromEntries(Object.entries(defs).map(([id, def]) => {
  if (id === 'overview') return [id, { ...def, box: found.view }]
  const measured = found.parts[id]
  if (!measured) throw new Error(`No measurements for the part ${id}`)
  return [id, { pad: 0.08, ...def, box: measured.box, boxes: measured.boxes, layer: `[data-part="${id}"]` }]
}))

// ── Beware These Alien Invaders: the screen leaflet ─────────────────────────────────────────────

const BEWARE_PARTS = {
  overview: {
    label: 'Whole leaflet',
    pad: 0.02,
    panel: {
      eyebrow: 'Ministry of Forests · Noxious Weeds',
      heading: 'Beware These Alien Invaders',
      lede: 'A five-screen leaflet made to be read on a computer: a cover, and one screen each for four weeds, joined by buttons. Here its screens are laid out one under another.',
      blocks: [
        'It is a PDF with links in it, a file made in March 1999, a year before the posters’ files: the cover’s red button opens the first weed, and the arrows and HOME under each weed step on or go back.',
        { facts: [
          ['Issued by', 'Ministry of Forests, from the cover; the file names its author as MOF'],
          ['File made', '25 March 1999 (QuarkXPress, Acrobat Distiller 3.01)'],
          ['Published', 'not established; the file’s date is not a publication date'],
          ['Screens', 'five, each 684 × 468 points'],
          ['Its subject', 'Vegetation Management, from the file']
        ] },
        { note: `${SOURCE_NOTE} ${SUBSTITUTE_TYPE} The weed headings and the cover’s text use the faces embedded in the file, and are their own.` },
        'Its strongest story is its format: an early interactive PDF, a cover and four pages joined by buttons, read on a screen years before that was ordinary for a government leaflet.'
      ]
    },
    story: [
      'The Ministry of Forests made a leaflet for the screen about weeds: five pages of a PDF, linked like a small website. Its file is dated March 1999, the earliest of the three pieces here under the name Noxious Weeds.',
      'Read it as it was meant to be clicked through: the cover, then four weeds.'
    ]
  },
  headline: {
    label: 'Headline',
    hint: 'BEWARE THESE ALIEN INVADERS',
    pad: 0.6,
    panel: {
      eyebrow: 'The cover · its headline',
      heading: 'Beware these alien invaders',
      lede: 'One line of widely spaced capitals, half of it in white across the photograph and half in black on the paper beside it.',
      blocks: [
        'The campaign’s word for the weeds is invaders, and it calls them alien: plants from elsewhere. Both posters a year later open the same way, “These Alien Invaders are destroying our natural ecosystems” and “Alien Invaders are threatening to shatter our precious resources”.',
        { facts: [['Face', 'Eurostile Bold Extended in the PDF; Michroma here']] }
      ]
    },
    story: ['Its headline names the enemy: alien invaders, plants that came from somewhere else.']
  },
  intro: {
    label: 'Cover photograph',
    hint: 'a mossy creek, and the wordmark',
    pad: 0.06,
    panel: {
      eyebrow: 'The cover · its picture',
      heading: 'A creek under moss',
      lede: 'A photograph of a stream running through moss-hung trees, fading out at its edges, with the BRITISH COLUMBIA mark, “Ministry of Forests” and the green NOXIOUS WEEDS wordmark laid over it.',
      blocks: [
        'The marks are part of the picture here, not separate drawings: the whole cover image is one 431 × 301 pixel photograph.',
        { facts: [['Image', 'one JPEG, 431 × 301 pixels, as in the PDF']] },
        { h: 'The wordmark on the posters' },
        { links: [on(SHATTERING, 'wordmark', 'NOXIOUS WEEDS under the landscape'), on(EXPLOSION, 'wordmark', 'NOXIOUS WEEDS among the specimens')] }
      ]
    },
    story: ['On the cover, a forest creek, the government’s mark, and the campaign’s green wordmark, NOXIOUS WEEDS, its O and X run together.']
  },
  invaders: {
    label: 'The warning',
    hint: 'beautiful but deadly',
    pad: 0.1,
    panel: {
      eyebrow: 'The cover · its copy',
      heading: 'Beautiful but deadly',
      lede: 'One paragraph, opening with a large green B: what the weeds do, how they spread, and how many there are.',
      blocks: [
        '“Capable of producing thousands of seeds per plant which may lie dormant for many years, they pose a very real threat to the continued existence and biodiversity of our environment.”',
        'It blames people first: weeds are carried “mainly by humans carrying seeds, burs or root pieces on machinery and vehicles, but also on footwear or clothing”, and then by water, wind and wildlife. And it counts them: “more than 20 species of weeds presently threatening B.C.’s plant communities.”',
        { facts: [['Text', 'as printed, including “of of weeds” across a line break']] }
      ]
    },
    story: [
      'Beautiful but deadly, it says. They make thick stands, they can make a site impossible to get into, and their seeds wait in the ground for years.',
      'And it is mostly us who move them: on machinery, vehicles, boots and clothes.'
    ]
  },
  start: {
    label: 'Click here',
    hint: 'the way in',
    pad: 0.4,
    panel: {
      eyebrow: 'The cover · its button',
      heading: 'Click here',
      lede: 'A small red glass button and, under it, “click here to learn about four noxious weeds”, in a typewriter face.',
      blocks: [
        'In the PDF this is a link to the first weed. Here the leaflet is laid out flat, so the next screen is simply below it; the button is kept as it was drawn.',
        { facts: [['Face', 'Courier, as the file names it']] }
      ]
    },
    story: ['A red button says click here. Below, the four weeds.']
  },
  thistle: {
    label: 'Bull thistle',
    hint: 'screen 2',
    pad: 0.06,
    panel: {
      eyebrow: 'Screen 2 of 5',
      heading: 'Bull Thistle',
      lede: 'A thistle in flower on black, and four facts: a biennial up to 1.5 metres, spiny-winged, its seeds alive for up to 36 years.',
      blocks: [
        '“Can be spread long distances by wind-borne seeds, of which it can produce up to 4000 per plant.”',
        'Bull thistle is the one weed of these four that neither poster shows; the landscape poster has a different thistle, marsh plume thistle.',
        { links: [on(SHATTERING, 'thistle', 'Marsh plume thistle, in the landscape')] }
      ]
    },
    story: ['First, bull thistle: spiny, up to a metre and a half, and up to 4,000 seeds a plant that can stay alive in the ground for 36 years.']
  },
  gorse: {
    label: 'Gorse',
    hint: 'screen 3',
    pad: 0.06,
    panel: {
      eyebrow: 'Screen 3 of 5',
      heading: 'Gorse',
      lede: 'A spiny evergreen shrub with yellow flowers, over two metres; up to 8,000 seeds a year, dormant for up to 40.',
      blocks: [
        '“Fairly flammable, creating potential fire hazard in drier areas.” The specimen poster says the same, and adds that it was then limited to coastal areas.',
        { links: [on(EXPLOSION, 'gorse', 'Gorse, among the specimens')] }
      ]
    },
    story: ['Then gorse, a thorny shrub that seeds for decades, and burns.']
  },
  toadflax: {
    label: 'Dalmatian toadflax',
    hint: 'screen 4',
    pad: 0.06,
    panel: {
      eyebrow: 'Screen 4 of 5',
      heading: 'Dalmatian Toadflax',
      lede: 'Snapdragon-like yellow flowers on waxy, heart-shaped leaves; roots that run deep and wide.',
      blocks: [
        'Its roots win by “intense competition for limited soil and water”, and it “contains toxic alkaloids that can cause liver damage in grazing animals”.',
        'It is the one weed on all three pieces of the campaign.',
        { links: [on(SHATTERING, 'toadflax', 'In the landscape, as “Dalmation Toadflax”'), on(EXPLOSION, 'toadflax', 'Among the specimens')] }
      ]
    },
    story: ['Dalmatian toadflax: pretty, yellow, and poisonous to the animals that graze it. It is the one weed on every piece of this campaign.']
  },
  houndstongue: {
    label: 'Hound’s tongue',
    hint: 'screen 5',
    pad: 0.06,
    panel: {
      eyebrow: 'Screen 5 of 5',
      heading: 'Hound’s Tongue',
      lede: 'Soft, hairy leaves shaped like a dog’s tongue, dull purple flowers, and burs: 4,000 to 6,000 seeds covered with hooked prickles.',
      blocks: [
        'It travels by “burs attachment to clothing, cattle and wildlife”, and, like toadflax, carries alkaloids that damage the livers of grazing animals.',
        { links: [on(EXPLOSION, 'houndstongue', 'Hound’s-tongue, its seeds and the weevil that eats it')] }
      ]
    },
    story: ['Last, hound’s tongue, whose burs catch on anything that passes: socks, cattle, deer.']
  },
  navigation: {
    label: 'Buttons',
    hint: 'back, home, next',
    pad: 0.04,
    panel: {
      eyebrow: 'The leaflet · its links',
      heading: 'Back, home, next',
      lede: 'Under every weed, the same three red glass buttons between two copper arrows, and HOME in red.',
      blocks: [
        'They were the leaflet’s links: step back, go to the cover, step on. Laid out flat they lead nowhere, and are kept as they were drawn, a reminder that this was made for a screen.'
      ]
    },
    story: ['Under each weed, the same buttons: back, home, next. It was made to be clicked through on a screen, like a small website.']
  }
}

// ── Shattering the Environment: the landscape poster ────────────────────────────────────────────

const SHATTERING_PARTS = {
  overview: {
    label: 'Whole poster',
    pad: 0.02,
    panel: {
      eyebrow: 'Ministry of Forests · Noxious Weeds',
      heading: 'Shattering the Environment',
      lede: 'A mountain valley, river and forest, cracked across like a pane of glass, with four weeds composited into it, standing taller than the trees.',
      blocks: [
        'The landscape and the weeds are one photographic composite; the cracks are part of it. The weeds are photographed separately and set into the scene at a scale no real weed reaches, the poster’s point.',
        { facts: [
          ['Issued by', 'Ministry of Forests, Forest Practices Branch'],
          ['File made', '31 March 2000 (Acrobat Distiller 4.0)'],
          ['Printed', 'not established; the file’s date is not a printing date'],
          ['Sheet', '36 × 27 inches'],
          ['Photograph', 'one JPEG, 2106 × 1592 pixels, as in the PDF']
        ] },
        { note: `${SOURCE_NOTE} ${SUBSTITUTE_TYPE}` },
        'The management advice on the sheet is the campaign’s own, of its time; it is kept as printed, and is not current guidance.'
      ]
    },
    story: [
      'The posters’ files are dated a year after the leaflet’s. This one puts four weeds into a mountain valley and breaks the picture like glass.',
      'Read it left to right, the way the weeds stand in it.'
    ]
  },
  landscape: {
    label: 'The landscape',
    hint: 'cracked like glass',
    pad: 0.02,
    panel: {
      eyebrow: 'The picture',
      heading: 'A valley, shattered',
      lede: 'Snow-capped peaks, a forested slope, a gravel bar on a river and a meadow in front, with white cracks running across all of it.',
      blocks: [
        'The cracks turn the photograph into something breakable, and the title says what is breaking it. The edges of the picture are broken too: the left side is cut ragged, and a toadflax stem leaves the frame on the right.',
        { facts: [['Credits', 'background photograph, Gunter Marx Photography; compositing and film, Watermark Lithography']] }
      ]
    },
    story: ['The landscape is the kind of place the ministry looks after: mountains, forest, river, meadow. And it is cracked.']
  },
  title: {
    label: 'Title',
    hint: 'SHATTERING THE ENVIRONMENT',
    pad: 0.1,
    panel: {
      eyebrow: 'The title',
      heading: 'Shattering the environment',
      lede: 'Pale blue extended capitals spaced right out across the top of the picture, and a rush skeletonweed seedhead standing up through the gap after THE.',
      blocks: [
        'The weed is not stopped by the title: its stem runs up out of the photograph and between the words.',
        { facts: [['Face', 'Eurostile Bold Extended in the PDF; Michroma here']] }
      ]
    },
    story: ['The title is spaced across the top, and a weed has grown right through it.']
  },
  thistle: {
    label: 'Marsh plume thistle',
    hint: 'the tall thistle, left',
    pad: 0.04,
    panel: {
      eyebrow: 'Weed 1 of 4',
      heading: 'Marsh Plume Thistle',
      em: 'Cirsium palustre',
      lede: 'A spiny stem with pink-purple flowerheads, standing over the trees on the left of the valley.',
      blocks: [
        '“A biennial that may reach 1.5 metres in height, whose stem, leaves, and flowerhead are covered with large spines. It spreads by seed through disturbed and undisturbed areas.”',
        'The specimen poster gives it more height, 1.2 to 2.4 metres.',
        { links: [on(EXPLOSION, 'marsh', 'Marsh plume thistle, among the specimens'), on(BEWARE, 'thistle', 'Bull thistle, on the leaflet')] }
      ]
    },
    story: ['On the left, marsh plume thistle, spines on every part of it, taller here than the spruce behind.']
  },
  skeletonweed: {
    label: 'Rush skeletonweed',
    hint: 'the bare stems',
    pad: 0.04,
    panel: {
      eyebrow: 'Weed 2 of 4',
      heading: 'Rush Skeletonweed',
      em: 'Chondrilla juncea',
      lede: 'Thin, nearly leafless stems rising the whole height of the picture, one of them up through the title.',
      blocks: [
        '“A perennial that spreads by wind-borne seed and by aggressive shoot buds produced on lateral roots that extend from the taproot.”',
        { links: [on(EXPLOSION, 'skeletonweed', 'Rush skeletonweed, among the specimens')] }
      ]
    },
    story: ['Then rush skeletonweed, almost all stem, hard to see and spreading by seed and by root.']
  },
  knapweed: {
    label: 'Spotted knapweed',
    hint: 'pink flowers, centre',
    pad: 0.05,
    panel: {
      eyebrow: 'Weed 3 of 4',
      heading: 'Spotted Knapweed',
      em: 'Centaurea maculosa',
      lede: 'A branching plant with pale pink-purple flowers, standing in the middle of the river flats.',
      blocks: [
        '“A biennial to short-lived perennial, with a long fibrous taproot, that spreads by wind-borne feathery seed from July to September.”',
        'The specimen poster calls it a perennial and explains the name: black-tipped bracts, hence “spotted”.',
        { links: [on(EXPLOSION, 'spotted', 'Spotted knapweed, and the moth whose larvae eat its roots')] }
      ]
    },
    story: ['In the middle, spotted knapweed, seeding on the wind from July to September.']
  },
  toadflax: {
    label: 'Dalmatian toadflax',
    hint: 'yellow, right',
    pad: 0.04,
    panel: {
      eyebrow: 'Weed 4 of 4',
      heading: 'Dalmation Toadflax',
      em: 'Linaria dalmatica',
      lede: 'Yellow snapdragon flowers on long stems, so big they break out of the right edge of the picture.',
      blocks: [
        '“A perennial that spreads by seed from its snapdragon-like flowers and by its creeping roots. Its deeply penetrating taproot and lateral roots suppress other vegetation by intense competition for limited soil and water.”',
        'The caption spells it “Dalmation”, as printed; the leaflet and the other poster have Dalmatian.',
        { links: [on(BEWARE, 'toadflax', 'On the leaflet'), on(EXPLOSION, 'toadflax', 'Among the specimens')] }
      ]
    },
    story: ['And on the right, Dalmatian toadflax, too big for the frame.']
  },
  message: {
    label: 'The message',
    hint: 'alien invaders',
    pad: 0.1,
    panel: {
      eyebrow: 'The copy',
      heading: 'Alien invaders are threatening to shatter our precious resources',
      lede: 'A narrow column down the right of the picture: weeds as an ecological and an economic problem, and whose job they are.',
      blocks: [
        '“The resulting monocultures reduce crop and recreational values, decrease native vegetation (and therefore forage for wildlife and livestock), ruin biodiversity, and damage the ecosystem as a whole.”',
        'It ends on responsibility: “It is our responsibility to learn about and to identify these weeds and to properly manage our resources.”',
        { facts: [['Face', 'Eurostile Condensed in the PDF; Saira Condensed here']] }
      ]
    },
    story: ['The copy down the side gives the charge: weeds crowd out crops and native plants, starve wildlife and livestock, and it is our job to know them.']
  },
  website: {
    label: 'Website',
    hint: 'for more information',
    pad: 0.3,
    panel: {
      eyebrow: 'The copy · its address',
      heading: 'For more information',
      lede: '“For more information on noxious weeds, you can check our website at: http://www.for.gov.bc.ca/hfp/noxweeds”, the address in green.',
      blocks: [
        'The address is the Forest Practices Branch’s part of the Ministry of Forests website (hfp). The screen leaflet may well have lived there; that is not established.',
        { sources: [{ label: 'The address, in the Wayback Machine', href: 'https://web.archive.org/web/*/www.for.gov.bc.ca/hfp/noxweeds*' }] }
      ]
    },
    story: ['For more, it sends you to a website: in 2000, a poster with a web address.']
  },
  credits: {
    label: 'Credits',
    hint: 'who made it',
    pad: 0.4,
    panel: {
      eyebrow: 'The small print',
      heading: 'Credits',
      lede: 'Six lines of tiny capitals under the address.',
      blocks: [
        { facts: [
          ['Copy', 'Susan Turner & Dwaine Brooke'],
          ['Art direction', 'Paul Nystedt & Denton Pendergast'],
          ['Design', 'Rocket Science Design'],
          ['Weed photography', 'Dion Manastyrski'],
          ['Compositing & film', 'Watermark Lithography'],
          ['Background photo', 'Gunter Marx Photography']
        ] },
        'The specimen poster credits the same writers, art directors, photographer and lithographer, with Denton Pendergast for design and Soren Henrich for illustration.'
      ]
    },
    story: ['The small print names the team: the same writers, art directors and photographer made the second poster.']
  },
  signature: {
    label: 'Ministry signature',
    hint: 'Ministry of Forests, Forest Practices Branch',
    pad: 0.3,
    panel: {
      eyebrow: 'The signature',
      heading: 'Ministry of Forests',
      em: 'Forest Practices Branch',
      lede: 'The coat of arms and BRITISH COLUMBIA, with the ministry and the branch in two lines beside them.',
      blocks: [
        'This is the coat-of-arms signature, here printed in black beside the campaign’s green wordmark. The Forest Practices Branch signs the Wildlife Trees poster the same way, in green.',
        { links: [ministry(2000), WILDLIFE_TREES_SIGNATURE] }
      ]
    },
    story: ['It is signed by the Ministry of Forests’ Forest Practices Branch, the branch that would sign Wildlife Trees a year or so later.']
  },
  wordmark: {
    label: 'Wordmark',
    hint: 'NOXIOUS WEEDS',
    pad: 0.3,
    panel: {
      eyebrow: 'The campaign',
      heading: 'NOXIOUS WEEDS',
      lede: 'The campaign’s mark in yellow-green: NOXIOUS in thin, tall letters with the O and X crossed into one another, and WEEDS in bold italic capitals underneath.',
      blocks: [
        'The same mark is on all three pieces.',
        { links: [on(BEWARE, 'intro', 'On the leaflet’s cover, laid over the photograph'), on(EXPLOSION, 'wordmark', 'Among the specimens')] }
      ]
    },
    story: ['And by the campaign: NOXIOUS WEEDS, in green.']
  }
}

// ── Explosion in Slow Motion: the specimen poster ───────────────────────────────────────────────

const EXPLOSION_PARTS = {
  overview: {
    label: 'Whole poster',
    pad: 0.02,
    panel: {
      eyebrow: 'Ministry of Forests · Noxious Weeds',
      heading: 'Explosion in Slow Motion',
      lede: 'Ten weeds photographed and drawn like specimens on white, around a giant nodding thistle going to seed under a bursting title, with the insects that eat two of them and three ways to fight them.',
      blocks: [
        'The explosion is the weeds’ spread: slow, seed by seed, and everywhere. Seeds drift across the top of the sheet; every weed has a caption of what it looks like and how it travels.',
        { facts: [
          ['Issued by', 'Ministry of Forests, Forest Practices Branch'],
          ['File made', '31 March 2000 (Acrobat Distiller 4.0)'],
          ['Printed', 'not established; the file’s date is not a printing date'],
          ['Sheet', '22 × 36 inches'],
          ['Pictures', '20 JPEG images and one PNG, as in the PDF; the centre is one composite']
        ] },
        { note: `${SOURCE_NOTE} ${SUBSTITUTE_TYPE}` },
        'The control methods and claims on the sheet are the campaign’s own, of its time; they are kept as printed, and are not current guidance.'
      ]
    },
    story: [
      'The second poster is a field guide. Ten weeds, each with what it looks like and how it spreads, around one enormous thistle gone to seed.',
      'Read it from the top: the warning, the title, the thistle, then the weeds around it, then what to do.'
    ]
  },
  headline: {
    label: 'Warning',
    hint: 'these alien invaders',
    pad: 0.1,
    panel: {
      eyebrow: 'The headline',
      heading: 'These Alien Invaders are destroying our natural ecosystems',
      lede: '“Introduced to North America without their natural predators, these plants are displacing native vegetation and having a negative impact on biodiversity.”',
      blocks: [
        'Without their natural predators: the reason the poster can show two insects as a remedy, further down.',
        { links: [on(EXPLOSION, 'biocontrol', 'The weevil and the moth')] }
      ]
    },
    story: ['At the top, the charge: these plants arrived without the insects that keep them in check at home.']
  },
  title: {
    label: 'Title',
    hint: 'EXPLOSION in slow motion',
    pad: 0.06,
    panel: {
      eyebrow: 'The title',
      heading: 'Explosion',
      em: 'in slow motion',
      lede: 'EXPLOSION in black, heavy, flaring letters bowed over the top of the thistle, the letters thrown out from the middle and casting soft shadows; IN SLOW MOTION in a tight arc under them.',
      blocks: [
        'EXPLOSION is part of the central photographic composite, so it is kept as the PDF has it; IN SLOW MOTION is drawn as paths in the PDF, and is vector here.',
        { facts: [['Credits', 'design, Denton Pendergast; photo-compositing, Watermark Lithography']] }
      ]
    },
    story: ['The title bursts over the thistle like the seedhead it sits on: an explosion, in slow motion.']
  },
  seeds: {
    label: 'Seeds on the wind',
    hint: 'drifting across the sheet',
    pad: 0.03,
    panel: {
      eyebrow: 'The picture · its seeds',
      heading: 'Seeds on the wind',
      lede: 'Single seeds, each on its plume of fine hairs, scattered across the top half of the sheet.',
      blocks: ['Each drifting seed is its own small image in the PDF, laid on the white around the title; they are the slow explosion.']
    },
    story: ['Around it, seeds drift away on their plumes, one by one.']
  },
  nodding: {
    label: 'Nodding thistle',
    hint: 'the giant at the centre',
    pad: 0.04,
    panel: {
      eyebrow: 'The centre',
      heading: 'Nodding thistle',
      em: 'Carduus nutans',
      lede: 'The poster’s centrepiece: tall stems with heavy, drooping heads, pink in flower and white going to seed, the biggest head opening into a ball of plumes under the title.',
      blocks: [
        '“Nodding thistle seeds contain large plumes for effective wind dispersal.” Its caption is short: “This plant is considered to be under biological control.”',
        { links: [on(EXPLOSION, 'biocontrol', 'Biological control, as the poster shows it')] }
      ]
    },
    story: ['The giant is nodding thistle, and it is the one weed here the poster calls under control, by its enemies.']
  },
  spurge: {
    label: 'Leafy spurge',
    hint: 'upper left',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Leafy spurge',
      em: 'Euphorbia esula',
      lede: '“Latex-filled plant consisting of persistent creeping roots and an 0.8 m stem, crowned with yellow-green flowers lacking petals and sepals but surrounded by a pair of yellow-green bracts.”',
      blocks: ['Its picture is the one PNG among the poster’s images.']
    },
    story: ['Leafy spurge, milky inside, spreading by roots that will not die.']
  },
  skeletonweed: {
    label: 'Rush skeletonweed',
    hint: 'the thin stems, right',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Rush skeletonweed',
      em: 'Chondrilla juncea',
      lede: '“Aggressive rhizomatous roots, dandelion-like rosettes, and small, yellow flowers on tall (0.3 to 1.3 m), pale green, slender stems with few, tiny leaves, hence “skeletonweed”.”',
      blocks: [
        'It is told apart “by reddish brown, downward-pointing hairs near the bottom of the stem.”',
        { links: [on(SHATTERING, 'skeletonweed', 'In the landscape, through the title')] }
      ]
    },
    story: ['Rush skeletonweed, nearly all stem: a skeleton of a plant.']
  },
  toadflax: {
    label: 'Dalmatian toadflax',
    hint: 'yellow, right',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Dalmatian toadflax',
      em: 'Linaria dalmatica',
      lede: '“Pale green stem and waxy, heart-shaped leaves with a snapdragon-like yellow flower; outcompetes other vegetation for water with its creeping root system.”',
      blocks: [{ links: [on(BEWARE, 'toadflax', 'On the leaflet'), on(SHATTERING, 'toadflax', 'In the landscape')] }]
    },
    story: ['Dalmatian toadflax again, the campaign’s constant.']
  },
  ragwort: {
    label: 'Tansy ragwort',
    hint: 'left',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Tansy ragwort',
      em: 'Senecio jacobaea',
      lede: '“Prolific seed-producing biennial to short-lived perennial with daisy-like yellow flowers atop a 0.3 to 1.2 m stem harbouring dark green, non-uniform, and deeply lobed leaves, hence a “ragged” look.”',
      blocks: ['The caption warns it is “often confused with common tansy, which produces only small disc flowers.”']
    },
    story: ['Tansy ragwort, easy to mistake for a harmless tansy.']
  },
  houndstongue: {
    label: 'Hound’s-tongue',
    hint: 'lower left, with its seeds',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Hound’s-tongue',
      em: 'Cynoglossum officinale',
      lede: '“Large, dark green leaf shaped like a dog’s tongue with fuschia-coloured, bell-shaped flowers developing into clinging burs.”',
      blocks: [
        'Its seeds are pictured beside it: “Four burred seeds within a nutlet disperse by clinging to unsuspecting passers-by.”',
        { links: [on(BEWARE, 'houndstongue', 'On the leaflet'), on(EXPLOSION, 'biocontrol', 'The weevil that eats its roots')] }
      ]
    },
    story: ['Hound’s-tongue, and its burred seeds, made to hitch a ride.']
  },
  biocontrol: {
    label: 'Weevil and moth',
    hint: 'insects that eat weeds',
    pad: 0.15,
    panel: {
      eyebrow: 'Biological control',
      heading: 'Two insects',
      lede: 'A black-and-white weevil beside hound’s-tongue, and a yellow moth beside spotted knapweed, each pictured with what it does.',
      blocks: [
        '“Cross-bearing weevil, Mogulones cruciger: larvae feed on the roots of hound’s-tongue.” “Sulphur moth, Agapeta zoegana: larvae feed on the roots of knapweed.”',
        'They answer the headline: weeds that came without their predators can be followed by them.'
      ]
    },
    story: ['Two insects sit among the weeds: a weevil and a moth whose larvae eat the roots of hound’s-tongue and knapweed. Predators, brought to follow their prey.']
  },
  marsh: {
    label: 'Marsh plume thistle',
    hint: 'the purple stem, centre',
    pad: 0.04,
    panel: {
      eyebrow: 'Specimen',
      heading: 'Marsh plume thistle',
      em: 'Cirsium palustre',
      lede: '“Tall (1.2 to 2.4 m), spiny-winged, deep purple stems harbouring few spiny-tipped, green leaves, topped with a cluster of small, purple flowers producing wind-blown seeds; prefers wet soils.”',
      blocks: [{ links: [on(SHATTERING, 'thistle', 'In the landscape, given as up to 1.5 m')] }]
    },
    story: ['Marsh plume thistle, its stem running down the middle of the sheet.']
  },
  gorse: {
    label: 'Gorse',
    hint: 'yellow shrub, centre',
    pad: 0.04,
    panel: {
      eyebrow: 'Specimen',
      heading: 'Gorse',
      em: 'Ulex europaeus',
      lede: '“Tall (2 m), evergreen shrub with yellow, pea-like flowers giving rise to large pods, large rigid thorns hazardous to move around, and potential fire hazard; presently limited to coastal areas.”',
      blocks: [{ links: [on(BEWARE, 'gorse', 'On the leaflet')] }]
    },
    story: ['Gorse, thorny and flammable, and in 2000 still only on the coast.']
  },
  diffuse: {
    label: 'Diffuse knapweed',
    hint: 'lower left',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Diffuse knapweed',
      em: 'Centaurea diffusa',
      lede: '“0.6 to 0.9 m perennial shaped like a small tumbleweed, hence “tumble” knapweed, with white, urn-shaped flower receptacles and bracts ending in sharp spines.”',
      blocks: ['Its seeds travel with the whole plant: the knapweed caption says diffuse knapweed “spreads its seeds by the “tumbling” action of the plant”.']
    },
    story: ['Diffuse knapweed rolls like a tumbleweed, scattering seed as it goes.']
  },
  spotted: {
    label: 'Spotted knapweed',
    hint: 'lower right, with its seeds',
    panel: {
      eyebrow: 'Specimen',
      heading: 'Spotted knapweed',
      em: 'Centaurea maculosa',
      lede: '“0.5 to 1.5 m perennial with pale pink to purple, urn-shaped flower receptacles and black-tipped bracts, hence “spotted” knapweed.”',
      blocks: [
        'Its seeds are pictured beside it: knapweeds produce “between 900 and 18 000 3 mm long seeds”, and spotted knapweed’s “burst from the seedhead as it shatters.”',
        { links: [on(SHATTERING, 'knapweed', 'In the landscape'), on(EXPLOSION, 'biocontrol', 'The moth whose larvae eat its roots')] }
      ]
    },
    story: ['Spotted knapweed: up to 18,000 seeds a plant, bursting out as the head shatters. An explosion.']
  },
  control: {
    label: 'Control',
    hint: 'clipping, herbicide, seeding',
    pad: 0.04,
    panel: {
      eyebrow: 'What to do',
      heading: 'Three kinds of control',
      lede: 'Along the foot of the sheet: hands clipping a weed, a hand scattering seed, and, between them, herbicide in words alone.',
      blocks: [
        { facts: [
          ['Clipping', 'removing stems and flowers to prevent seed production and weaken plants; “an alternative to herbicidal control”'],
          ['Herbicide', 'chemicals to destroy weeds “and in some cases, seed banks”'],
          ['Seeding', 'seeds to replenish the plant community “before weeds can invade”']
        ] },
        'Herbicide is the only one of the three without a picture.'
      ]
    },
    story: ['At the bottom, the remedies: clip them, spray them, or sow something else first.']
  },
  signature: {
    label: 'Ministry signature',
    hint: 'Ministry of Forests, Forest Practices Branch',
    pad: 0.3,
    panel: {
      eyebrow: 'The signature',
      heading: 'Ministry of Forests',
      em: 'Forest Practices Branch',
      lede: 'The coat of arms and BRITISH COLUMBIA, with the ministry and the branch beside them, in black over the green wordmark.',
      blocks: [{ links: [ministry(2000), WILDLIFE_TREES_SIGNATURE] }]
    },
    story: ['Signed, as before, by the Forest Practices Branch.']
  },
  wordmark: {
    label: 'Wordmark',
    hint: 'NOXIOUS WEEDS',
    pad: 0.3,
    panel: {
      eyebrow: 'The campaign',
      heading: 'NOXIOUS WEEDS',
      lede: 'The campaign’s yellow-green mark, as on the other two pieces.',
      blocks: [{ links: [on(BEWARE, 'intro', 'On the leaflet’s cover'), on(SHATTERING, 'wordmark', 'Under the landscape')] }]
    },
    story: ['With the campaign’s green mark.']
  },
  action: {
    label: 'You can help',
    hint: 'the green band',
    pad: 0.06,
    panel: {
      eyebrow: 'The call',
      heading: 'You can help protect the environment',
      lede: '“Learn to identify these biological pollutants and if found on Crown land, please report their location to your local Ministry of Forests office.”',
      blocks: [
        'A solid yellow-green band across the foot of the sheet, in the wordmark’s colour, with the credits in small capitals above it.',
        { facts: [
          ['Copy', 'Susan Turner and Dwaine Brooke'],
          ['Art direction', 'Paul Nystedt and Denton Pendergast'],
          ['Design', 'Denton Pendergast'],
          ['Photography', 'Dion Manastyrski'],
          ['Illustration', 'Soren Henrich'],
          ['Photo-compositing', 'Watermark Lithography']
        ] }
      ]
    },
    story: [
      'And the ask, in a green band: learn them, and if you find them on Crown land, tell the ministry.',
      'Biological pollutants, it calls them. The campaign’s whole case in two words.'
    ]
  }
}

export const NOXIOUS_WEEDS_POSTERS = {
  [BEWARE]: {
    id: BEWARE,
    spotlight: { keep: BEWARE_FOUND.papers },
    regions: ['intro', 'headline', 'invaders', 'start', 'thistle', 'gorse', 'toadflax', 'houndstongue', 'navigation'],
    parts: parts(BEWARE_FOUND, BEWARE_PARTS),
    order: ['overview', 'headline', 'intro', 'invaders', 'start', 'thistle', 'gorse', 'toadflax', 'houndstongue', 'navigation']
  },
  [SHATTERING]: {
    id: SHATTERING,
    spotlight: { keep: SHATTERING_FOUND.papers },
    // The landscape first, so that every part drawn over it is found before it.
    regions: ['landscape', 'title', 'thistle', 'skeletonweed', 'knapweed', 'toadflax', 'message', 'website', 'credits', 'signature', 'wordmark'],
    parts: parts(SHATTERING_FOUND, SHATTERING_PARTS),
    order: ['overview', 'landscape', 'title', 'thistle', 'skeletonweed', 'knapweed', 'toadflax', 'message', 'website', 'credits', 'signature', 'wordmark']
  },
  [EXPLOSION]: {
    id: EXPLOSION,
    spotlight: { keep: EXPLOSION_FOUND.papers },
    // The broad regions of the central composite first, the specimens over them.
    regions: ['nodding', 'title', 'seeds', 'headline', 'spurge', 'skeletonweed', 'toadflax', 'ragwort', 'houndstongue', 'biocontrol', 'marsh', 'gorse', 'diffuse', 'spotted', 'control', 'signature', 'wordmark', 'action'],
    parts: parts(EXPLOSION_FOUND, EXPLOSION_PARTS),
    order: ['overview', 'headline', 'title', 'seeds', 'nodding', 'spurge', 'skeletonweed', 'toadflax', 'ragwort', 'houndstongue', 'biocontrol', 'marsh', 'gorse', 'diffuse', 'spotted', 'control', 'signature', 'wordmark', 'action']
  }
}
