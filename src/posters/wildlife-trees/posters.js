// Wildlife Trees: its parts, where each sits in the drawing, what the panel says about it, and the
// story told down the tree. Data only — the drawing is attached in ./index.js — so the boxes can be
// checked without a browser.
//
// Boxes are in the drawing's own units (1000 wide, as the package measured them from the scan). The
// tree's are taken from the package's measured region masks (source/tree-*-regions.json), not from
// the groups' bounds: the tree is drawn in clipped horizontal tiles, and a tile's paths run past the
// edge it is clipped to.
//
// Panels are blocks, as in ../forest-service/posters.js. `story` is what the part says in story
// mode, read in `order`: the poster is read the way it is drawn, from the broken top of the tree to
// its roots, and then down the sheet.

import { POSTERS } from '../catalogue.js'

const ID = 'wildlife-trees'
const INK = '#326C59'

// ── Shared context ──────────────────────────────────────────────────────────────────────────────

const MINISTRY_LINK = {
  label: 'Ministry of Forests, in 2001',
  note: 'Government · 2001: the ministry this poster is signed by, and its lockup in the identity of the day',
  to: { view: 'government', year: 2001, node: 'ministry-of-forests-1988' }
}
const OVAL_LINK = {
  label: 'The Forest Service tree oval',
  note: 'Internal Logos · Forests: the oval on this poster, its variants and history',
  to: { view: 'internal', internal: 'forests', 'internal-logo': 'forest-service' }
}
const FORESTS_LINK = {
  label: 'The Forest Service’s other marks',
  note: 'Internal Logos · Forests: from the Lands Department seal to the wildlife ovals',
  to: { view: 'internal', internal: 'forests' }
}
const EARLIER_EMBLEM_LINK = {
  label: 'The service’s earlier mark, on REWARD',
  note: 'Posters · the evergreen emblem it used before the ovals',
  to: { view: 'posters', poster: 'reward-living-forest', part: 'emblem' }
}

const part = (id) => ({ view: 'posters', poster: ID, part: id })
const back = (id, label, note) => ({ label, note, to: part(id) })

// The animals: the frame around each, its caption, and what the package records of how it was
// rebuilt (source/animal-source-notes/vector-manifest.json).
const animal = ({ key, caption, box, label, hint, panel, story }) => ({
  label,
  hint,
  box,
  pad: 0.12,
  layer: `#${key}, #${caption}`,
  panel,
  story
})

const ANIMAL_NOTE = 'Each animal is its own layer, rebuilt separately and put back at the exact place it was cut from in the scan; its surroundings inside the frame (branches, trunk, ground) are a second layer behind it.'

// ── The parts ───────────────────────────────────────────────────────────────────────────────────

export const WILDLIFE_TREES = {
  id: ID,
  spotlight: { keep: ['paper'] },
  // Hotspots: the whole tree first, so that every smaller part drawn over it is found before it.
  regions: [
    'tree', 'crown', 'nest', 'fungi', 'cavities', 'roots', 'signature',
    'hawk', 'owl', 'squirrel', 'chickadee', 'bear', 'toad',
    'heading', 'traits', 'users', 'patches', 'ministry', 'oval'
  ],
  parts: {
    overview: {
      label: 'Whole poster',
      box: POSTERS[ID].view,
      pad: 0.02,
      panel: {
        eyebrow: 'Ministry of Forests · Forest Practices Branch',
        heading: 'Wildlife Trees',
        lede: 'One dead tree, drawn in one green ink from its broken top to its roots, with six of the animals that live in it framed up its side, and below it the lesson: which trees to leave standing, and why.',
        blocks: [
          'The sheet is long and narrow, a third as wide as it is tall, so the tree can be drawn whole. It reads from the top down: the hawk on its perch, the nest, the owl, the cavities and the conks of rot on the trunk, the bear and the toad at its foot, then the title and the copy.',
          { facts: [
            ['Issued by', 'Ministry of Forests, Forest Practices Branch, from its signature'],
            ['Date', 'about 2001, from the artist’s mark “d.g.01”; not printed'],
            ['Sheet', '290.6 × 870.9 mm'],
            ['Rebuilt from', 'one scan of a printed copy, 4576 × 13,715 pixels'],
            ['Drawing', '1000 × 2997 units, no images; the master’s 104,787 paths are 1,960 here']
          ] },
          { palette: [{ name: 'The one ink', value: INK }, { name: 'Paper', value: '#FFFFFF' }] },
          { note: 'A reconstruction. The penwork is rebuilt as filled Bézier outlines fitted to the scan, the lettering is set again in a substitute face, and the two logos are this site’s own drawings placed where the printed ones are. The site shows a lighter copy of the master. Each part’s panel says what was repaired and what was left as found.' },
          { h: 'Read it as a story' },
          'The Story button (or S) reads the poster from top to bottom: scroll, and the drawing follows.',
          { h: 'Its marks elsewhere on the site' },
          { links: [MINISTRY_LINK, OVAL_LINK] }
        ]
      },
      story: [
        'A wildlife tree is a dead or live tree that provides valuable and sometimes critical habitat for wildlife. That is the poster’s own definition, and the whole sheet is built to show it: one tree, drawn whole, and six of the animals that need it.',
        'It was printed by the Ministry of Forests’ Forest Practices Branch, for the people who decide which trees are left standing when a forest is cut. Read it as it is drawn, from the top down.'
      ]
    },
    tree: {
      label: 'The tree',
      hint: 'a dead tree, drawn whole',
      box: { x: 45, y: 130, w: 930, h: 1830 },
      pad: 0.03,
      layer: '#habitat-tree',
      panel: {
        eyebrow: 'The drawing',
        heading: 'The habitat tree',
        em: 'from crown to roots',
        lede: 'A tall snag: the top broken off, bare limbs hung with lichen, bark peeling from a trunk scarred with cavities and conks, standing in fallen wood.',
        blocks: [
          'The tree is rebuilt from the scan as the pen drew it. The visible ink was traced along its middle and given back its measured width as smooth Bézier outlines, mark by mark, so the hatching on the bark is the original hatching rather than a texture laid over a shape.',
          'Where the animals’ frames cover the tree, the drawing has a gap: no branch or wood hidden by a portrait has been invented.',
          { facts: [
            ['Named parts', '56, from the broken crown to the pebbles'],
            ['Method', 'variable-width Bézier outlines fitted to the scan; no generated hatching'],
            ['Drawn in', 'ten horizontal tiles, overlapped and clipped'],
            ['White base', 'a removable layer under the solid wood']
          ] },
          { note: 'Some dark patches on the trunk are labelled cautiously as scars or cavities: the drawing alone does not say what every one of them is.' }
        ]
      },
      story: [
        'This is the tree the poster is about, and it is not a healthy one. Its top has snapped, its limbs are bare, and its trunk is split and peeling. A forester planning a cutblock might once have seen a hazard and a tree worth nothing. The poster sees habitat.'
      ]
    },
    crown: {
      label: 'Broken top',
      hint: 'the splintered crown',
      box: { x: 565, y: 132, w: 125, h: 120 },
      pad: 0.25,
      layer: '#habitat-upper-crown-splinters',
      panel: {
        eyebrow: 'The tree · its crown',
        heading: 'A broken top',
        lede: 'The crown has snapped off, leaving a ragged column of splinters standing at the top of the trunk.',
        blocks: [
          'The splinters are rebuilt as narrow standing shards with their gaps left open, as drawn; they are not filled to make a cleaner top.',
          { facts: [['Layer', 'habitat-upper-crown-splinters']] }
        ]
      },
      story: [
        'Start at the top, where the tree has already broken. A tree does not have to be alive to be a wildlife tree: the poster says dead or live, and its first picture is of one past saving.',
        'A broken top is also high ground. On a tree this tall, the highest limbs are a perch with a view over everything around it.'
      ]
    },
    hawk: animal({
      key: 'red-tailed-hawk',
      caption: 'caption-0',
      box: { x: 250, y: 94, w: 240, h: 226 },
      label: 'Red-tailed hawk',
      hint: 'on its perch, breaking its frame',
      panel: {
        eyebrow: 'Portrait 1 of 6',
        heading: 'Red-tailed hawk',
        lede: 'A hawk gripping a diagonal branch, tail fanned, head turned. It is the only animal on the poster that breaks out of its frame: its tail and feet cross the rule.',
        blocks: [
          'On the poster’s list it is an open nester: “birds that build large heavy nests: Great Blue Heron, Osprey, Bald Eagle, large hawks and owls.” Nests that size need big, strong limbs, which is one reason a tree’s structure is on the list of what makes it valuable.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '5,178 fitted outlines'],
            ['Repairs', 'two faint contours at the head and cere, measured from the scan'],
            ['Left as found', 'the gap where the perch crosses the body']
          ] }
        ]
      },
      story: [
        'The first portrait: a red-tailed hawk, and the only animal on the sheet too big for its box. Its tail and talons spill over the frame.',
        'The poster calls it an open nester, one of the birds that build large, heavy nests. They need the strongest limbs in the forest, and a tall tree with a clear view to hunt from.'
      ]
    }),
    nest: {
      label: 'Stick nest',
      hint: 'woven twigs in the crown',
      box: { x: 330, y: 325, w: 295, h: 175 },
      pad: 0.12,
      layer: '#habitat-nest-woven-twigs, #habitat-left-nest-level-upward-twigs, #habitat-nest-support-left-branch',
      panel: {
        eyebrow: 'The tree · the nest',
        heading: 'A large nest',
        lede: 'A bowl of woven sticks wedged on a limb below the broken top, loose twigs sticking out of its rim.',
        blocks: [
          '“Large nest” is one of the uses the poster lists under a tree’s structure; a nest, along with holes, pellets and fresh chips, is also the sign of “active or recent wildlife use”.',
          'The nest is rebuilt with its open weave: the gaps between the sticks are left as paper.',
          { facts: [['Layers', 'the woven nest, its upward twigs, the branch it sits on']] }
        ]
      },
      story: [
        'Below the top, a nest. It is the kind of thing the poster asks you to look for: “active or recent wildlife use: e.g., woodpecker holes, nests, owl pellets, discarded tree cones, fresh wood chips”.',
        'A nest like this one is used for years, and not always by the bird that built it.'
      ]
    },
    owl: animal({
      key: 'great-horned-owl',
      caption: 'caption-1',
      box: { x: 128, y: 389, w: 212, h: 228 },
      label: 'Great horned owl',
      hint: 'ear tufts and a hard stare',
      panel: {
        eyebrow: 'Portrait 2 of 6',
        heading: 'Great horned owl',
        lede: 'A head-and-shoulders portrait, face on: ear tufts up, the facial discs ringed, the eyes looking straight out of the frame.',
        blocks: [
          'The poster names owls twice: among the secondary cavity users, which move into holes others have made, and among the open nesters. A great horned owl builds no nest of its own; it takes over one another bird has left.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '7,660 fitted outlines'],
            ['Cropped', 'by its frame on the right and below, as printed']
          ] }
        ]
      },
      story: [
        'The great horned owl does not build. It moves in, to a stick nest a hawk has left or to a hollow in a broken trunk, which is why the poster lists owls with both the open nesters and the cavity users.',
        'Its portrait is the most direct on the sheet: the only animal looking straight back at you.'
      ]
    }),
    squirrel: animal({
      key: 'northern-flying-squirrel',
      caption: 'caption-2',
      box: { x: 219, y: 670, w: 212, h: 232 },
      label: 'Northern flying squirrel',
      hint: 'clinging to the trunk',
      panel: {
        eyebrow: 'Portrait 3 of 6',
        heading: 'Northern flying squirrel',
        lede: 'A squirrel flattened against a trunk, the fold of its gliding membrane along its side, its tail running out of the frame to the left.',
        blocks: [
          'Squirrels are on the poster’s list of secondary cavity users, “animals that don’t make their own holes but move into existing ones”. A flying squirrel dens in an old woodpecker hole.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '3,970 fitted outlines'],
            ['Repairs', 'a short rim of the rear ear, measured from the scan'],
            ['Left as found', 'the tail, cut by the frame']
          ] }
        ]
      },
      story: [
        'The poster sorts the animals by what they do with a tree. The flying squirrel is a secondary cavity user: it cannot dig a hole, so it needs a tree where something else already has.',
        'Which is why the next thing on the trunk matters.'
      ]
    }),
    fungi: {
      label: 'Conks',
      hint: 'bracket fungi on the trunk',
      box: { x: 440, y: 810, w: 295, h: 765 },
      boxes: [
        { x: 680, y: 812, w: 52, h: 98 },
        { x: 677, y: 1191, w: 56, h: 55 },
        { x: 440, y: 1373, w: 72, h: 56 },
        { x: 460, y: 1523, w: 77, h: 49 }
      ],
      pad: 0.08,
      layer: '#habitat-upper-right-bracket-fungus, #habitat-second-right-bracket-fungus, #habitat-right-bracket-fungus-1228, #habitat-left-bracket-fungus-1402, #habitat-left-bracket-fungus-1549',
      panel: {
        eyebrow: 'The tree · its decay',
        heading: 'Conks',
        em: 'the outside of the rot',
        lede: 'Five shelf fungi stand out from the trunk, two high on the right and three lower down.',
        blocks: [
          'A bracket fungus on a trunk is the fruiting body of a rot working inside it. That is the first characteristic on the poster’s list: “Internal decay — heart rot or cavities present”.',
          'Each conk is drawn with its own edge as the pen left it; the lowest keeps its stepped rim rather than being smoothed into an oval.',
          { facts: [['Conks', 'five, each its own layer']] }
        ]
      },
      story: [
        'Halfway down, shelves of fungus stand out from the bark. They are the outward sign of heart rot, and heart rot is the first thing on the poster’s list of what makes a tree valuable to wildlife.',
        'Rot softens the wood inside a standing tree. Soft wood is what a woodpecker, a primary cavity excavator, can dig into, and every hole it leaves is a home for the squirrel, the owl and the rest.'
      ]
    },
    chickadee: animal({
      key: 'black-capped-chickadee',
      caption: 'caption-3',
      box: { x: 134, y: 981, w: 220, h: 238 },
      label: 'Black-capped chickadee',
      hint: 'gripping the bark',
      panel: {
        eyebrow: 'Portrait 4 of 6',
        heading: 'Black-capped chickadee',
        lede: 'A small bird clinging sideways to a trunk beside an opening, black cap and bib, both feet gripping the bark.',
        blocks: [
          'Chickadees nest in holes. They can dig one only where rot has made the wood soft enough, and otherwise use one that is already there: the same decay the conks show.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '2,124 fitted outlines'],
            ['Kept', 'both legs and gripping feet, and a small mark under the beak, as drawn']
          ] }
        ]
      },
      story: [
        'The chickadee is small enough to use the smallest holes, and can make one of its own only where the wood has gone soft. Rot, again.',
        'Look at what it clings to: not a branch, but the side of a trunk, beside an opening.'
      ]
    }),
    cavities: {
      label: 'Cavities and bark',
      hint: 'scars, hollows and loose bark',
      box: { x: 560, y: 925, w: 130, h: 780 },
      pad: 0.06,
      layer: '#habitat-dark-scar-947, #habitat-cavity-or-dark-scar-1104, #habitat-dark-scar-1450-1577, #habitat-long-narrow-scar-1590-1671, #habitat-detached-bark-flap-1570-1620, #habitat-detached-bark-flap-1630-1700',
      panel: {
        eyebrow: 'The tree · its trunk',
        heading: 'Cavities, scars and loose bark',
        lede: 'Dark openings run down the trunk, and two curled slabs of bark have come away from it on the right.',
        blocks: [
          'Two more of the poster’s characteristics are here: cavities (part of “internal decay”), and “crevices present — loose bark or cracks suitable for bats”. Bats, the copy says, “roost and rear young under bark and in cavities”.',
          'The package names these cautiously, as scars or cavities: from the drawing alone it is not possible to say which dark patch is a hollow and which a wound.',
          { facts: [
            ['Openings', 'four, from the upper trunk to the base'],
            ['Bark flaps', 'two, with the gap to the trunk left open']
          ] }
        ]
      },
      story: [
        'Down the trunk, the tree is opening up: hollows, long scars, and bark peeling away in slabs. Each is on the poster’s list. The gap behind loose bark is where bats roost and raise their young.',
        'A tree like this is not finished. It is just becoming useful.'
      ]
    },
    bear: animal({
      key: 'black-bear',
      caption: 'caption-4',
      box: { x: 97, y: 1262, w: 265, h: 283 },
      label: 'Black bear',
      hint: 'the largest portrait',
      panel: {
        eyebrow: 'Portrait 5 of 6',
        heading: 'Black bear',
        lede: 'The largest frame on the sheet holds only a head and neck in profile, the mane drawn in dense strokes, the muzzle pointing out to the right.',
        blocks: [
          'The poster’s mammals: “Bats roost and rear young under bark and in cavities, caribou feed on lichens which grow on old or dying trees, bears use large hollows to hibernate in.” A “bear den” is also on its list of what a tree’s structure can offer.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '6,489 fitted outlines'],
            ['Repairs', 'the ink core of the near ear and its white flecks, measured from the scan'],
            ['Left as found', 'a pale seam across the neck, which is in the scan']
          ] }
        ]
      },
      story: [
        'Near the base the hollows get bigger, and so do the animals. A large hollow tree is a den: the poster says bears use them to hibernate in.',
        'The bear gets the biggest frame on the sheet, and fills it with a head alone.'
      ]
    }),
    toad: animal({
      key: 'northwestern-toad',
      caption: 'caption-5',
      box: { x: 186, y: 1561, w: 225, h: 234 },
      label: 'Northwestern toad',
      hint: 'at the foot of the tree',
      panel: {
        eyebrow: 'Portrait 6 of 6',
        heading: 'Northwestern toad',
        lede: 'A toad crouched low on the ground, hind leg folded, toes spread, its near foot crossing the bottom of the frame.',
        blocks: [
          'The poster’s amphibians: “Salamanders and toads use wildlife trees for shelter, food, and as safe, moist sites to lay their eggs.” Not only standing trees: the rotting wood on the ground, too.',
          ANIMAL_NOTE,
          { facts: [
            ['Ink strokes', '7,033 fitted outlines'],
            ['Repairs', 'the pupil and one highlight of the near eye, measured from the scan'],
            ['Recovered', 'the outer hind foot, by widening the cut 51 scan pixels to the left']
          ] }
        ]
      },
      story: [
        'The last portrait is on the ground. A toad needs a wildlife tree as much as the hawk does, for shelter, food and a moist place to lay its eggs, and it uses the tree even after it has fallen.'
      ]
    }),
    roots: {
      label: 'Roots and fallen wood',
      hint: 'the forest floor',
      box: { x: 50, y: 1690, w: 900, h: 270 },
      pad: 0.05,
      layer: '#habitat-left-buttress-root, #habitat-right-forward-basal-slab, #habitat-front-central-basal-wood, #habitat-root-flare-and-basal-bark, #habitat-forest-floor-and-fallen-wood, #habitat-foreground-fallen-branch-left, #habitat-ground-stump-left, #habitat-ground-stump-fork-behind-roots, #habitat-ground-grass-tuft-left, #habitat-ground-grass-tuft-centre-left, #habitat-ground-grass-tuft-right, #habitat-foreground-pebbles, #habitat-basal-sapling-central-right, #habitat-basal-sapling-far-right',
      panel: {
        eyebrow: 'The tree · its foot',
        heading: 'Roots and fallen wood',
        lede: 'The trunk flares into buttress roots and broken slabs, among logs, stumps, grass and pebbles.',
        blocks: [
          'The last of the poster’s uses happens here: “Insects — ants and termites chew up wood and add nutrients to the soil” (the copy has no full stop after it).',
          'No white base was put under the ground, so the gaps between the bits of wood and twigs stay open, as drawn.',
          { facts: [['Layers', 'roots and basal wood, fallen wood, two stumps, saplings, grass and pebbles']] }
        ]
      },
      story: [
        'At the bottom the tree is already returning to the ground: fallen limbs, old stumps, slabs of wood broken off the base. Ants and termites, the poster says, chew it up and add nutrients to the soil.',
        'The story of a wildlife tree does not end when it falls.'
      ]
    },
    signature: {
      label: 'Artist’s mark',
      hint: '“d.g.01”',
      box: { x: 762, y: 1914, w: 49, h: 21 },
      pad: 1.2,
      layer: '#habitat-original-illustrator-mark',
      panel: {
        eyebrow: 'The drawing · its signature',
        heading: 'd.g.01',
        lede: 'A small hand-written mark in the grass at the right of the roots.',
        blocks: [
          'It reads “d.g.01”: most likely the artist’s initials and the year, 2001. That fits the signature below it, since the Ministry of Forests held that name from 1988 to 2005. Who d.g. was is not established, and the poster credits no one else.',
          'The mark is kept as the pen left it. It was not redrawn or neatened, and no new signature was added.',
          { links: [MINISTRY_LINK] }
        ]
      },
      story: [
        'In the grass, a signature: d.g.01. The artist’s initials, it seems, and the year: 2001. Nothing else on the sheet says who drew it.'
      ]
    },
    heading: {
      label: 'Title',
      hint: 'Wildlife Trees, and what one is',
      box: { x: 90, y: 2008, w: 812, h: 206 },
      pad: 0.08,
      layer: '#poster-heading',
      panel: {
        eyebrow: 'The copy · its heading',
        heading: 'Wildlife Trees',
        lede: 'The title reversed out of a solid green block, and under it a centred, three-line definition.',
        blocks: [
          '“A wildlife tree is a dead or live tree that provides valuable and sometimes critical habitat for wildlife. Over 80 species of animals in BC are known to be dependent on wildlife trees.” The count is the poster’s.',
          'The original typeface has not been identified. The title and the definition are set again in Nimbus Sans, each line fitted to the measured box of the printed one; the spacing matches, the letter shapes need not.',
          { facts: [
            ['Title block', '646.6 × 92.9 units, solid ink'],
            ['Substitute face', 'Nimbus Sans Bold and Regular, outlined']
          ] }
        ]
      },
      story: [
        'Below the tree, the title, and the definition the whole drawing has been illustrating: a dead or live tree that provides valuable and sometimes critical habitat. Over 80 species of animals in BC, the poster says, depend on them.'
      ]
    },
    traits: {
      label: 'What makes one valuable',
      hint: 'at least two of eight',
      box: { x: 55, y: 2243, w: 404, h: 364 },
      pad: 0.08,
      layer: Array.from({ length: 15 }, (_, i) => `#left-copy-${i}`).join(', '),
      panel: {
        eyebrow: 'The copy · the first column',
        heading: 'A High Value Wildlife Tree',
        em: 'has at least 2 of these',
        lede: 'Eight characteristics, as bullets: internal decay, crevices, large brooms, wildlife use, insects, structure, size, and species.',
        blocks: [
          'Most of them have already appeared in the drawing above: the conks and hollows are internal decay, the peeling bark is crevices, the nest is wildlife use, the broken top and the big limbs are structure.',
          'The wording is kept exactly, including the space in “and /or veterans”.',
          { links: [back('fungi', 'Internal decay, in the drawing', 'The conks on the trunk'), back('cavities', 'Crevices and cavities, in the drawing', 'Scars, hollows and loose bark'), back('nest', 'Wildlife use, in the drawing', 'The stick nest')] }
        ]
      },
      story: [
        'Then the test. A high value wildlife tree has at least two of eight characteristics, and the drawing has shown most of them already: internal decay, crevices, wildlife use, a structure animals can use.',
        'The tree above is not an example of one of them. It is an example of nearly all.'
      ]
    },
    users: {
      label: 'Who uses them',
      hint: 'excavators, cavity users, nesters…',
      box: { x: 55, y: 2248, w: 838, h: 666 },
      boxes: [
        { x: 55, y: 2624, w: 427, h: 290 },
        { x: 530, y: 2248, w: 363, h: 106 }
      ],
      pad: 0.04,
      layer: [...Array.from({ length: 13 }, (_, i) => `#left-copy-${15 + i}`), ...Array.from({ length: 5 }, (_, i) => `#right-copy-${i}`)].join(', '),
      panel: {
        eyebrow: 'The copy · across both columns',
        heading: 'Who Uses Wildlife Trees?',
        lede: 'Six kinds of user, from the woodpeckers that dig the holes to the insects that break the wood down. The list starts at the foot of the first column and finishes at the top of the second.',
        blocks: [
          'Every portrait is one of them: the hawk and the owl are open nesters, the owl and the squirrel secondary cavity users, the bear a mammal, the toad an amphibian.',
          { links: [
            back('hawk', 'Red-tailed hawk', 'An open nester'),
            back('squirrel', 'Northern flying squirrel', 'A secondary cavity user'),
            back('bear', 'Black bear', 'A mammal that hibernates in hollows'),
            back('toad', 'Northwestern toad', 'An amphibian')
          ] }
        ]
      },
      story: [
        'Who uses them? The poster’s answer runs across both columns: primary cavity excavators (the woodpeckers that dig), secondary cavity users (owls, swallows, ducks, raccoons, marten, squirrels, mice), open nesters, mammals, amphibians and insects.',
        'Every animal up the tree is one of these.'
      ]
    },
    patches: {
      label: 'Wildlife tree patches',
      hint: 'leaving trees in a cutblock',
      box: { x: 527, y: 2374, w: 407, h: 328 },
      pad: 0.08,
      layer: Array.from({ length: 13 }, (_, i) => `#right-copy-${5 + i}`).join(', '),
      panel: {
        eyebrow: 'The copy · the second column',
        heading: 'Wildlife Tree Patches',
        lede: 'A paragraph and a list about leaving trees in groups: larger patches, spread through the cutblock, windfirm, with food, water and an undisturbed forest floor.',
        blocks: [
          'This is the part addressed to the people planning a harvest. A cutblock is the area of a forest to be logged; a wildlife tree patch is a group of trees left standing in it.',
          'The list asks for patches that contain high value wildlife trees, sit in areas with surrounding forest cover, have good access to food and water sources, are windfirm, include diverse plant communities and have an undisturbed forest floor.'
        ]
      },
      story: [
        'The last column turns the lesson into practice. One tree is not enough: leave patches, larger rather than smaller, and spread them through the cutblock. Patches that will stand up to the wind, near food and water, on a forest floor left alone.',
        'This is who the poster is for: the people who decide, block by block, what is cut and what is left.'
      ]
    },
    ministry: {
      label: 'Ministry signature',
      hint: 'Ministry of Forests, Forest Practices Branch',
      box: { x: 606, y: 2765, w: 135, h: 121 },
      pad: 0.35,
      layer: '#ministry-mark',
      panel: {
        eyebrow: 'The signature',
        heading: 'Ministry of Forests',
        em: 'Forest Practices Branch',
        lede: 'The Province’s coat of arms over BRITISH COLUMBIA, with the ministry and the branch in two small lines beneath.',
        blocks: [
          'This is the coat-of-arms signature, the generator’s Arms identity. The arms and the BRITISH COLUMBIA wordmark are this site’s own drawings of them, placed where the printed mark sits and coloured in the poster’s green; they were not traced from the scan.',
          'The two support lines are outlined Nimbus Sans, a substitute: the printed face has not been identified.',
          { facts: [
            ['Ministry', 'Ministry of Forests (the name held from 1988 to 2005)'],
            ['Branch', 'Forest Practices Branch'],
            ['Arms and wordmark', 'this site’s vectors, unchanged'],
            ['Ink', INK]
          ] },
          { h: 'The lockup on the site' },
          { links: [MINISTRY_LINK] }
        ]
      },
      story: [
        'It is signed twice. First by the government: the coat of arms over BRITISH COLUMBIA, and the Ministry of Forests’ Forest Practices Branch.'
      ]
    },
    oval: {
      label: 'Forest Service oval',
      hint: 'the tree oval',
      box: { x: 756, y: 2775, w: 73, h: 91 },
      pad: 0.45,
      layer: '#forest-service-mark',
      panel: {
        eyebrow: 'The second mark',
        heading: 'The Forest Service tree oval',
        lede: 'FOREST SERVICE over the top and BRITISH COLUMBIA under it, around a single conifer in front of mountains, with a diamond on each side.',
        blocks: [
          'The ministry signs the poster, and its Forest Service signs it again: the service kept a mark of its own inside the ministry, as it had since its evergreen emblem.',
          'The oval is drawn from the same Forest Oval artwork as the tree oval in Internal Logos (its frame, tree and mountains), with its lettering built from the Kabel reconstruction and its separators measured. It is coloured in the poster’s one green.',
          { facts: [
            ['Lettering', 'Kabel Black reconstruction, outlined'],
            ['Separators', 'two diamonds'],
            ['Ink', INK]
          ] },
          { h: 'See it as a logo' },
          { links: [OVAL_LINK, EARLIER_EMBLEM_LINK, FORESTS_LINK] }
        ]
      },
      story: [
        'And then by the Forest Service, in its tree oval. The service kept its own name and its own mark inside the ministry.',
        'That is the poster, top to bottom: a tree, the animals that need it, and the rule for keeping it.'
      ]
    }
  },
  order: [
    'overview', 'tree', 'crown', 'hawk', 'nest', 'owl', 'squirrel', 'fungi', 'chickadee', 'cavities',
    'bear', 'toad', 'roots', 'signature', 'heading', 'traits', 'users', 'patches', 'ministry', 'oval'
  ]
}
