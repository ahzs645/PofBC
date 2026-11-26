// Each title corresponds to one printed page. Chapter boundaries also drive the reader's contents.
const chapter = (title, description, pages) => ({ title, description, pages })
const ourBrandChapters = [
  chapter('Introduction', 'The December 2021 edition introduces the province’s destination brand and identifies the changes in version 5.0.', [
    'Cover', 'Welcome to the destination brand', 'Contents and edition notes']),
  chapter('Brand strategy', 'Visitor research grounds the brand in wilderness. The guide pairs the province’s raw landscape with its cultivated side and explains how the Super, Natural British Columbia tagline carries both.', [
    'Redefining our brand', 'The changing tourism industry', 'Research and consultation', 'Reasons to visit BC', 'Five attributes of British Columbia', 'Wild at Heart', 'Super, Natural British Columbia', 'Aligning with the brand', 'Cultured and raw']),
  chapter('The brand toolbox', 'Destination BC brings photography, type, colour, voice and the web tile together as the tools of the destination identity.', ['Brand toolbox']),
  chapter('Photography and video', 'Signature images introduce the province, experience images show what visitors can do, and moments bring everyday details into view.', [
    'Photography and videography', 'Setting a visual direction', 'Mood and place', 'Choosing images', 'Building an image collection', 'Three visual tiers', 'Signature images', 'Experience images', 'Moments']),
  chapter('Image techniques', 'The examples show how light, framing and colour change the feel of a scene, from a backlit subject to a city seen against the wilderness.', [
    'Techniques', 'Earth tones', 'Muted primary colours', 'Shadows and blacks', 'Monochromatic colour', 'Desaturation', 'Morning and late afternoon light', 'Dappled light', 'Shallow depth of field', 'Backlighting and veiling', 'Cropping and perspective', 'Minimalism', 'Photojournalism', 'Cities in wilderness']),
  chapter('Mood boards', 'Six regional photo boards show how the same art direction travels across BC. The remaining boards look at cities, winter and moving images.', [
    'Vancouver Island', 'Vancouver, Coast & Mountains', 'Thompson Okanagan', 'Kootenay Rockies', 'Cariboo Chilcotin Coast', 'Northern BC', 'Cities', 'Winter', 'Video mood board']),
  chapter('Image comparisons', 'Paired examples explain why a photograph fits the brand. The final two pages collect the working criteria for filmmakers and photographers.', [
    'Expressions and colour', 'Tourism clichés', 'Staged composition', 'Image processing', 'Exposure and lens effects', 'Comparisons I', 'Comparisons II', 'Comparisons III', 'Comparisons IV', 'Video quick reference', 'Photography quick reference']),
  chapter('Typography', 'Great Forest is a custom wood-print display face. Brandon Grotesque carries longer passages, captions and utility text. The final specimen shows how the two faces work together.', [
    'Typography', 'The two typefaces', 'Great Forest', 'Brandon Grotesque', 'Pairing the typefaces']),
  chapter('Colour', 'Spirit Bear White and Orca Black anchor the identity. Salmon Red picks out the maple leaf. The secondary neutrals and seven accent colours draw on the province’s landscapes.', [
    'Colour', 'The natural spectrum', 'Palette specifications']),
  chapter('Tone of voice', 'The Helpful Guide speaks differently to a stranger, an acquaintance and a friend. The writing examples move from creating an emotional connection to helping someone plan a trip.', [
    'Tone of voice', 'The Helpful Guide', 'Voice attributes', 'Tone and the traveller', 'Tone framework', 'Language principles', 'Writing examples', 'Voice summary']),
  chapter('Logo web tile', 'The framed Explore tile was made for partner websites. The guide shows both colourways and specifies 100 × 140 and 150 × 211 pixel versions.', [
    'Logo web tile', 'Sizes, colourways and placement']),
  chapter('Contact and updates', 'The final page identifies Destination BC as the contact for this edition of the brand guidelines.', ['Contact and updates'])
]

const rainforestChapters = [
  chapter('Introduction', 'The cover identifies Rainforest to Rockies as part of the Super, Natural British Columbia family. The contents distinguish the route’s strategy from its visual identity.', [
    'Cover', 'Contents']),
  chapter('Family of brands', 'Invest in Iconics connects local tourism experiences under the provincial destination brand. The guide places Rainforest to Rockies alongside The Great Wilderness and explains how tourism operators participate.', [
    'Building the family', 'The provincial destination brand', 'Introducing the brand family', 'The role of tourism businesses']),
  chapter('Route and traveller', 'The route map traces several ways to travel from the Pacific to the Rockies. The traveller profile describes people who value both well-known destinations and discoveries along the way.', [
    'Brand strategy', 'Route map', 'The ideal traveller', 'Curious Wanderers', 'The spirit of the route', 'Place and traveller insights']),
  chapter('Essence, promise and pillars', '“Unfold Wonder” describes the experience of seeing the landscape change along the journey. Five pillars connect its ocean and mountain endpoints with local cultures, independent travel and care for the land.', [
    'Unfold Wonder', 'The brand promise', 'Five brand pillars', 'Strategy at a glance']),
  chapter('Logos and partner use', 'The Wander Mark combines a tree, peak and arrow. For partners, the guide adds the British Columbia, Canada line, sets clear space to the width of the F in Rainforest, and specifies a minimum height of 25 mm in print or 80 pixels on screen.', [
    'Brand identity', 'Logo', 'The Wander Mark', 'The third-party lockup', 'Clear space', 'Minimum size', 'Examples of incorrect use']),
  chapter('Tone of voice', 'Playfulness distinguishes the route’s voice within the parent brand. Examples use sensory details, questions and everyday language to evoke a moment on the road.', [
    'Tone of voice', 'The route’s voice within the family', 'Playfulness in practice']),
  chapter('Key messages', 'The messages describe the coast-to-mountains journey, shifts in scenery and the freedom to choose a pace and route.', [
    'Key messaging', 'Messages for visitors']),
  chapter('Experience and storytelling', 'The guide translates each brand pillar into experiences that operators can feature, including cultural encounters, local detours and ways to care for the land.', [
    'Experience and storytelling themes', 'Pillars and experience themes']),
  chapter('Colour and contrast', 'Three greens distinguish the route. White and black come from the provincial brand. The final page illustrates the guide’s text and background pairings for digital media.', [
    'Colour', 'Primary palette', 'Supporting palette', 'Web content accessibility']),
  chapter('Photography and video', 'The guide looks for play, movement, surprise and cultural context. Its image boards follow the route through coast and city, rainforest, dry interior hills and mountain ranges.', [
    'Visual style', 'Photography and video criteria', 'Four kinds of landscape']),
  chapter('Contact', 'Destination BC lists where partners can ask about the brand and its use.', ['Partner enquiries'])
]

const designCase = { label: 'The designers’ rebranding case study', to: { view: 'initiatives', initiative: 'tourism', section: 'rebranding' } }
const welcomeSign = { label: 'The earlier Super, Natural welcome sign', to: { view: 'signs', sign: 'super-natural', part: 'slogan' } }
const tourismRecord = (label, record) => ({ label, to: { view: 'initiatives', initiative: 'tourism', section: 'marks', record } })
const routeRecord = (label, record) => ({ label, to: { view: 'initiatives', initiative: 'rainforest-to-rockies', section: 'marks', record } })
const parentPage = (label, page) => ({ label, to: { view: 'initiatives', initiative: 'tourism', section: 'brand-guide', page } })
const routePage = (label, page) => ({ label, to: { view: 'initiatives', initiative: 'rainforest-to-rockies', section: 'publications', page } })

export const ourBrandGuide = {
  folder: 'our-brand-2021', sourceId: 'destination-bc-our-brand-2021', chapters: ourBrandChapters,
  pageHeight: 1299, palettePage: 64,
  printOnly: ['Spirit Bear White', 'Orca Black'],
  related: {
    Introduction: [tourismRecord('Cover wordmark', 'super-natural-stacked-2021'), designCase, welcomeSign],
    'Brand strategy': [welcomeSign, routePage('How Rainforest to Rockies fits the brand family', 5)],
    'Logo web tile': [tourismRecord('Both downloadable web tiles', 'super-natural-web-tile-2021')],
    Typography: [designCase],
    Colour: [routePage('Rainforest to Rockies colour palette', 32)]
  },
  colours: [
    ['Primary', 'Spirit Bear White', '#FFFFFF', '0 / 0 / 0 / 0'],
    ['Primary', 'Orca Black', '#000000', '0 / 0 / 0 / 100'],
    ['Primary', 'Salmon Red', '#A8483D', '20 / 80 / 75 / 20', '7608'], ['Secondary', 'Warm Sand', '#BCB49E', '15 / 15 / 30 / 15', '7535'],
    ['Secondary', 'Granite Grey', '#687767', '50 / 30 / 40 / 30', '7538'], ['Secondary', 'Summit Grey', '#939598', '0 / 0 / 0 / 50', '422'], ['Secondary', 'Winter Night Grey', '#4D4D4F', '0 / 0 / 0 / 85', '425'],
    ['Tertiary', 'Warm Dusk', '#61504D', '50 / 55 / 50 / 35', '411'], ['Tertiary', 'Shore Blue', '#76ACA9', '50 / 10 / 29 / 10', '563'], ['Tertiary', 'Deep Blue', '#004B55', '100 / 50 / 50 / 40', '316'],
    ['Tertiary', 'Lichen Green', '#8EA366', '50 / 25 / 75 / 0', '2276'], ['Tertiary', 'Forest Green', '#475536', '70 / 50 / 85 / 35', '5743'], ['Tertiary', 'Peat Brown', '#927149', '35 / 49 / 75 / 20', '7559'], ['Tertiary', 'Soil Brown', '#4D4532', '50 / 50 / 70 / 55', '7533']
  ]
}

export const rainforestGuide = {
  folder: 'rainforest-to-rockies-2024', sourceId: 'industry-guidelines-2024', chapters: rainforestChapters,
  pageHeight: 945, palettePage: 32,
  related: {
    Introduction: [parentPage('Super, Natural British Columbia brand guide', 1), welcomeSign],
    'Family of brands': [parentPage('The provincial destination tagline', 10), welcomeSign],
    'Logos and partner use': [routeRecord('Primary logo', 'primary-logo'), routeRecord('Partner colourways', 'partner-lockup')],
    'Colour and contrast': [parentPage('Province-wide destination palette', 64)],
    'Photography and video': [parentPage('Provincial photography and video standards', 14)]
  },
  colours: [
    ['Primary', 'Lush Moss', '#B0BD36', '36 / 12 / 100 / 0', '7744 C'], ['Primary', 'Alpine Emerald', '#1A7667', '100 / 0 / 61 / 28', '3295 C'], ['Primary', 'Canopy Green', '#00392F', '88 / 24 / 66 / 74', '567 C'],
    ['Supporting', 'Spirit Bear White', '#FFFFFF', '0 / 0 / 0 / 0'], ['Supporting', 'Orca Black', '#333333', '0 / 0 / 0 / 100']
  ]
}
