const pressImages = 'https://cdn.sanity.io/images/p3hjnjl0/production/'
const playbook = pressImages + '136100d9d4083a0cbd50a1a9e195e4f74e13b0c0-3300x2550.jpg'
const applications = pressImages + '35e19662170538b93da26155419b9754574225b7-3300x2550.jpg'
const wildlife = pressImages + 'e9d17957cde330fcbd70dbe28f10b6ee013b800f-1640x924.png'
const specimens = 'https://optimo.ch/uploads/0423/'
export const baselClassicSpecimen = specimens + '91137346e49b25429d7ec666b1437e4236a35dae1554c253b710eb8a9420a3f2/Optimo-BaselClassic-Specimen.pdf#page=3'
export const baselGroteskSpecimen = specimens + 'df0e2e5bebacc61e61b17bc3969e16ae956619440784c24688abac596d164fec/Optimo-BaselGrotesk-Specimen.pdf#page=2'
const directory = 'identity-collected/bc-parks-foundation/playbook'

const groups = [
  {
    label: 'Playbook', source: playbook, reference: 'Published playbook spread',
    studies: [
      ['type-specimen', 'The three type styles', 'The capital A and lowercase a share a baseline and scale. Their paths come from Optimo’s printed specimens. Compare the stroke contrast of Classic Black with the two Grotesk weights.'],
      ['type-hierarchy', 'Typesetting hierarchy', 'The playbook uses Classic Black for headings and quotes. Grotesk Medium sets tags, subheadings, introductory text and buttons. Grotesk Regular sets standard body and reference text. The heading is outlined. The other samples are editable text that uses locally installed Basel Grotesk, with Arial as a fallback.'],
      ['glass-panel', 'Digital glass panel', 'The playbook uses slightly rounded glass panels over photographs on websites and in newsletters. This demonstration places a PaRx panel over the launch’s aurora photograph. A clipped, blurred copy of the same image supplies the glass texture.'],
      ['section-divider', 'Chapter divider', 'The Logo Guidelines divider centres a two-line Moss heading on Charcoal. The reconstruction preserves the title’s letter shapes and condenses the paragraph and footer.'],
      ['signature-pairings', 'Signature colour pairings', 'Each pair reverses foreground and background. Charcoal and Moss are the primary pair. The other pairs combine Umber with Sunset and Midnight with Mist. All six placements use the Foundation’s original signature paths.']
    ]
  },
  {
    label: 'Campaign', source: applications, reference: 'Published campaign and stationery board',
    studies: [
      ['poster-protect', 'Paddling poster', 'The two-line headline sits between the small signature and the website pill. The reconstructed SVG separates the traced lettering, signature and button from the aerial photograph.'],
      ['poster-parks', 'Eagle poster', 'The eagle sits to the left of the signature. A four-line headline occupies the middle of the composition. Its original line breaks and letter shapes are preserved.']
    ]
  },
  {
    label: 'Stationery', source: applications, reference: 'Published campaign and stationery board',
    studies: [
      ['card-contact', 'Business card · contact side', 'The signature sits at the upper right. The name, role and two contact lines share a left edge, and the website aligns to the opposite edge. The sample details from the mockup are fixed vector outlines.'],
      ['card-inlet', 'Business card · coast', 'A centred Moss signature spans the water and shoreline. The file includes the native signature paths and a photographic layer taken from repeated views of this card on the board.'],
      ['card-valley', 'Business card · valley', 'The same signature placement appears against a low sun and a mountain valley. Repeated views on the board supply the corners of the photograph.']
    ]
  },
  {
    label: 'Photography', source: pressImages + '316790053ad6883866cf135177f05221c132ee06-1640x924.png', reference: 'Original aurora photograph',
    studies: [
      ['aurora-landscape', 'Aurora and campsite', 'PofBC’s vector study follows the original framing. Broad gradients describe the northern lights, and traced shapes preserve the mountain ridge and the lit tent. The photographic reference opens at full resolution.']
    ]
  },
  {
    label: 'Infographics', source: wildlife, reference: 'Published wildlife graphic',
    studies: [
      ['wildlife-graphic', 'Wildlife statistics', 'Four glass panels and a thin polygon frame the bear. The numerals preserve the shapes printed in the September 2025 graphic. The captions paraphrase the figures as published.'],
      ['wildlife-overlay', 'Transparent infographic overlay', 'The rounded panels, polygon, outlined numerals and editable captions can be placed over another photograph. The panel fills approximate the glass treatment shown in the playbook.']
    ]
  }
]

const photographic = new Set(['glass-panel', 'poster-protect', 'poster-parks', 'card-inlet', 'card-valley', 'wildlife-graphic'])

const digests = {
  'type-specimen': '67788e30ec6998f25c7390afc4b5e63c5728d2a8cbade933959a217252776c4d',
  'type-hierarchy': 'd72774a3f54d20c9894a9b5912cea14df991dc90ce2373ad01beef3a0e0e6592',
  'glass-panel': 'fbbd703172ef29d82f5bdd557410fb7213f0b198588251e981b18e818011e84c',
  'section-divider': 'ee5c5a42b422c3d535d1d8aa82f25a127b3926f0a28815679abb68dc21a0e9d1',
  'signature-pairings': 'db9fe809c461abd6a86e8934c1497088612ed6406a535c0690272dc14ffcc8d8',
  'poster-protect': 'c57f6c7496858215c497b7f7df9f60b339e3482ac3ce63de71372bcb28a9006d',
  'poster-parks': '4ef9a20d6ac0854ba1f30342ba8d3b24123ac4be640ca306a4b16cc77530aa35',
  'card-contact': '8d62033658c0ae740ea11e353a1cf0b2da6f45e6cf6652ab9d955a8bd57cc2ba',
  'card-inlet': '4cbe884d2cc31da291ebf498fdd2c98884ca20e7bfd5e2b8e7825acc5be0b59f',
  'card-valley': '42252edf852a573387fe7504646f3bbac4284fc1a11d26be419d25549dd82160',
  'aurora-landscape': '894702daba0c27bca4738c6da1cc31310570a46713a4b89dcd0b421d2cd4f881',
  'wildlife-graphic': '6021005c42100428ba07ec7663fbe4240e55ea6738dc4e9aeadb6c8adac58393',
  'wildlife-overlay': '1c403e6a49e97ff647cda3cad87604005c915d75bfc4f1b9c3cf1a3df338cae1'
}

export const foundationStudySections = groups.map(({ label, studies }) => ({
  id: label === 'Playbook' ? 'foundation-studies' : 'foundation-' + label.toLowerCase(),
  label, marks: studies.map(([id]) => 'bcpf-study-' + id)
}))

export const foundationStudyAssets = groups.flatMap(({ source, reference, studies }) =>
  studies.map(([id, label, notes]) => ({
    id: 'bcpf-study-' + id, label, notes, file: directory + '/' + id + '.svg', sha256: digests[id],
    format: 'svg', isVector: !photographic.has(id), reconstruction: true, evidenceType: 'vector-reconstruction',
    publisher: 'BC Parks Foundation', creator: 'PofBC reconstruction', observedDate: '2026-11-25',
    specimenDate: '2025-09-18', dateNote: 'The date identifies the published launch reference.',
    sourcePage: 'https://bcparksfoundation.ca/updates/bc-parks-foundation-launches-a-bold-new-visual-identity/',
    sourceUrl: source, sourceFile: reference, sourceLocator: label,
    referenceDetail: source === playbook || source === applications
      ? { file: directory + '/references/' + id + '.webp' }
      : { url: source + '?w=1000&auto=format' },
    fidelityNote: photographic.has(id)
      ? 'The SVG combines photographic material with reconstructed shapes and lettering.'
      : 'The reconstruction retains a full vector canvas.',
    ...(id === 'type-specimen' ? { alsoSeen: [
      { label: 'Optimo, Basel Classic specimen, page 3', source: baselClassicSpecimen },
      { label: 'Optimo, Basel Grotesk specimen, page 2', source: baselGroteskSpecimen }
    ] } : {})
  }))
)
