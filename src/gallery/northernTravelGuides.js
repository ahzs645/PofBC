import artwork from './northernTravelGuideArtwork.json' with { type: 'json' }

export const NORTHERN_TRAVEL_GUIDE_ARTWORK = artwork

const records = [
  {
    id: 'destination-brand',
    name: 'Super, Natural British Columbia',
    kind: 'tourism-initiative',
    aliases: ['HelloBC', 'Explore BC', 'British Columbia Canada sunrise'],
    description: 'Provincial destination marketing as printed in the 2012–15 Northern British Columbia Travel Guides.',
    history: 'The 2012 and 2013 guides carry the shaded provincial sunrise and the white Super, Natural lettering. The 2015 guide uses the newer stacked wordmark and maple leaf in two colourways.',
    cover: 'snbc-canada-stacked-positive-2015',
    initiativeId: 'tourism',
    // destinationbc.ca: “promoting our Super, Natural British Columbia® brand”, a trade-mark of Destination BC Corp.
    relations: [{ subject: 'destination-bc', type: 'service-of', label: 'Destination BC’s trade-marked provincial brand' }],
    extraSources: [{ title: 'Destination BC', url: 'https://www.destinationbc.ca/' }]
  },
  {
    id: 'visitor-centre',
    name: 'BC Visitor Centre network',
    kind: 'tourism-initiative',
    aliases: ['Visitor Centre', 'Visitor Information Centre'],
    description: 'The Visitor Centre signs printed in the guides pair the yellow information symbol and blue panel with the Super, Natural oval.',
    cover: 'visitor-centre-super-natural-oval-pdf',
    initiativeId: 'tourism',
    // The centres are community-owned; the network is Destination BC's Visitor Services Network Program.
    relations: [{ subject: 'destination-bc', type: 'service-of', label: 'Community-owned centres in Destination BC’s Visitor Services Network Program' }],
    extraSources: [{ title: 'Destination BC, Visitor Services', url: 'https://www.destinationbc.ca/what-we-do/destination-management/visitor-services/' }]
  },
  {
    id: 'chances-gaming',
    name: 'Chances gaming venues',
    kind: 'gaming-centre',
    aliases: ['Chances', 'Chances community gaming centres'],
    description: 'Chances community gaming centres in Terrace, Dawson Creek and Fort St. John carried separate venue signatures in the guides’ advertisements. ' +
      'Each Chances venue has its own owner: Chances Prince Rupert is owned by Gitxaała Enterprises Corporation, and Snuneymuxw First Nation’s Petroglyph Development Group bought Chances Maple Ridge from Great Canadian in April 2026. ' +
      'All of them operate under BCLC, which conducts and manages gaming in the province through service agreements with each facility’s private owner-operator. ' +
      'The owners of the Terrace and Fort St. John venues have not been confirmed; Great Canadian is reported to have kept its Dawson Creek centre when it sold its other B.C. properties.',
    cover: 'chances-dawson-creek-2015',
    // BCLC conducts and manages the gaming; each venue's owner-operator runs it under a service agreement.
    relations: [{ subject: 'bclc', type: 'service-of', label: 'Gaming centres run by separate owner-operators under BCLC service agreements' }],
    extraSources: [
      { title: 'Chances Prince Rupert, About (“governed and abide by BCLC policies, procedures, and standards”)', url: 'https://www.chancespr.ca/about/' },
      { title: 'Great Canadian Entertainment, sale of Chances Maple Ridge, April 2026', url: 'https://greatcanadian.com/news/cmr-sale-2026/' },
      { title: 'British Columbia Lottery Corporation (Wikipedia): facilities run by private owner-operators under service agreements', url: 'https://en.wikipedia.org/wiki/British_Columbia_Lottery_Corporation' },
      { title: 'Province of B.C., Gambling and fundraising', url: 'https://www2.gov.bc.ca/gov/content/sports-culture/gambling-fundraising' }
    ]
  },
  {
    id: 'bc-ferries-travel',
    name: 'BC Ferries Vacations',
    kind: 'tourism-initiative',
    description: 'The travel-package signature appeared in BC Ferries advertisements in all three northern guides. The 2015 example also shows the Canadian Signature Experiences endorsement.',
    cover: 'bc-ferries-vacations-guide'
  },
  {
    id: 'small-town-love',
    name: 'Small Town Love',
    kind: 'tourism-initiative',
    historical: true,
    aliases: ['Love Northern BC'],
    description: 'The shop-local campaign promoted independent businesses in Northern Development’s service area. The 2015 guide has its orange heart and the Trust’s sponsor signature.',
    cover: 'small-town-love-heart-2015',
    relations: [{ subject: 'northern-development-initiative-trust', type: 'related-to', label: 'Regional program partner' }]
  },
  {
    id: 'bc-fishing-resorts-and-outfitters-association',
    name: 'BC Fishing Resorts & Outfitters Association',
    shortName: 'BC Fishing Resorts and Outfitters',
    kind: 'tourism-association',
    aliases: ['BCFROA', 'Where to Fish in BC'],
    description: 'The association used red lettering with a fish worked into the initials in its fishing directory ads.',
    cover: 'bcfroa-red-2013',
    relations: [{ subject: 'fishing-bc', type: 'related-to', label: 'Named partner in the 2017 Fishing BC launch' }]
  },
  {
    id: 'visit-terrace',
    name: 'Visit Terrace',
    kind: 'tourism-initiative',
    description: 'Terrace’s visitor advertising used a green bear and dark script in 2012, a white bear and script in 2013, and larger white destination lettering in 2015.',
    cover: 'visit-terrace-bear-script-2013',
    relations: [{ subject: 'municipality-terrace', type: 'related-to', label: 'Community destination branding' }]
  },
  {
    id: 'tourism-prince-george',
    name: 'Tourism Prince George',
    kind: 'tourism-association',
    aliases: ['Tourism Prince George Society', 'TourismPG', 'Tour the City', 'Get Out!', 'takeonPG'],
    description: 'Tourism Prince George used a text-only sponsor signature and several moose-and-skyline treatments between 2012 and 2015. The guides record the Tour the City, Get Out! and takeonPG campaigns.',
    cover: 'tourism-prince-george-moose-guide-2012',
    relations: [{ subject: 'municipality-prince-george', type: 'related-to', label: 'Community destination branding' }]
  },
  {
    id: 'tourism-prince-rupert',
    name: 'Tourism Prince Rupert',
    kind: 'tourism-initiative',
    aliases: ['Discover Our Nature'],
    description: 'The 2015 visitor ad pairs a white bird-shaped emblem with Prince Rupert and Discover Our Nature.',
    cover: 'prince-rupert-discover-our-nature-2015',
    relations: [{ subject: 'municipality-prince-rupert', type: 'related-to', label: 'Community destination branding' }]
  },
  {
    id: 'haida-gwaii-tourism',
    name: 'Haida Gwaii tourism',
    kind: 'tourism-initiative',
    aliases: ['Go Haida Gwaii'],
    description: 'The name and wave appeared together in the 2015 guide’s Haida Gwaii destination ad.',
    cover: 'haida-gwaii-wave-2015'
  },
  {
    id: 'alaska-highway',
    name: 'Alaska Highway tourism',
    kind: 'tourism-initiative',
    aliases: ['The World Famous Alaska Highway'],
    description: 'The guide includes this sign-shaped lettering in a notice for the highway’s 75th anniversary.',
    cover: 'world-famous-alaska-highway-2015'
  },
  {
    id: 'tourism-northern-rockies',
    name: 'Tourism Northern Rockies',
    kind: 'tourism-initiative',
    description: 'The blue-and-green Northern Rockies destination signature appears in the 2013 and 2015 guides.',
    cover: 'tourism-northern-rockies-2015',
    relations: [{ subject: 'municipality-northern-rockies', type: 'related-to', label: 'Regional destination branding' }]
  },
  ...[
    ['canada-winter-games-2015', 'Prince George 2015 Canada Winter Games', 'canada-winter-games-pg-full-colour-2013', 'Bilingual host-event marks and the official community partner artwork for the Prince George Games.'],
    ['lheidli-tenneh', 'Lheidli T’enneh', 'lheidli-tenneh-2015', 'The red and black emblem appears beside the City of Prince George and centennial marks in the 2015 guide.'],
    ['golden-raven-experience', 'A Golden Raven Experience', 'golden-raven-stacked-2015', 'The central Interior cultural attractions campaign used a gold raven with single-line and stacked signatures.'],
    ['huble-homestead', 'Huble Homestead Historic Site', 'huble-homestead-official-brochure', 'The historic site’s house and green banner appear in all three editions.'],
    ['friends-of-fort-st-james', 'Friends of Fort St. James National Historic Site', 'friends-fort-st-james-badge-2012', 'The Friends’ circular badge appears in the 2012 historic site advertisement.'],
    ['chetwynd-chainsaw-carving', 'International Chainsaw Carving Championship', 'chetwynd-carving-11th-2015', 'The Chetwynd advertisement records the eleventh annual competition in June 2015.'],
    ['tourism-dawson-creek', 'Tourism Dawson Creek', 'tourism-dawson-creek-red-white-2015', 'Dawson Creek used separate destination lettering and an illustrated tourism wordmark.'],
    ['alaska-highway-house', 'Alaska Highway House', 'alaska-highway-house-blue-2015', 'The Dawson Creek attraction used a gold medallion and a later blue signature in the guides.'],
    ['dawson-creek-art-gallery', 'Dawson Creek Art Gallery', 'dawson-creek-art-gallery-title-2015', 'The 2015 advertisement carries the gallery’s title and the Grainery shop signature.'],
    ['fort-st-john-north-peace-museum', 'Fort St. John North Peace Museum', 'north-peace-museum-2015', 'The 2015 advertisement shows the museum and its historical association badge.'],
    ['fort-nelson-heritage-museum', 'Fort Nelson Heritage Museum', 'fort-nelson-heritage-museum-2015', 'The 2015 advertisement shows the museum’s title and heritage collection.'],
    ['visit-bulkley-nechako', 'Visit Bulkley-Nechako', 'bulkley-nechako-picture-it-2015', 'The 2015 Picture It! campaign paired its title with a map pin and route artwork.'],
    ['tourism-smithers', 'Tourism Smithers', 'tourism-smithers-orange-figure-2015', 'The guide advertisements pair a serif wordmark with a small orange figure.'],
    ['hazeltons-tourism', 'The Hazeltons tourism', 'hazeltons-visitor-title-2015', 'The Hazeltons visitor centre used the Historic Heartland of Northern British Columbia signature.'],
    ['ksan-historical-village', '’Ksan Historical Village & Museum', 'ksan-museum-2012', 'The 2012 advertisement pairs the stylized red name with the museum line and a mask detail.'],
    ['stewart-bear-arts-festival', 'Stewart Bear Arts Festival', 'stewart-bear-arts-2015', 'The 2013 and 2015 event advertisements use a stacked serif title.'],
    ['stewart-cassiar-highway', 'Stewart–Cassiar Highway tourism', 'stewart-cassiar-red-2015', 'The Highway 37 route advertisements used two different stacked names.'],
    ['terrace-riverboat-days', 'Terrace Riverboat Days', 'riverboat-days-2015', 'The annual event badges carry a boat emblem and dated lettering.'],
    ['terrace-heritage-park-museum', 'Terrace Heritage Park Museum', 'heritage-park-museum-2015', 'The advertisement shows the museum’s building silhouette and stacked name.'],
    ['kitimat-museum-archives', 'Kitimat Museum & Archives', 'kitimat-museum-archives-2012', 'The five-colour museum mark appears in the 2012 Kitimat advertising spread.'],
    ['prince-rupert-seafest', 'Prince Rupert Seafest', 'seafest-harbour-2015', 'The 37th annual event advertisement pairs the Seafest script with an illustrated tugboat.'],
    ['gwaii-haanas', 'Gwaii Haanas', 'gwaii-haanas-blue-panel-2012', 'The bilingual site signatures appear with the conserved area’s circular emblem.'],
    ['haida-nation', 'Haida Nation', 'haida-nation-colour-2012', 'Red and white treatments of the Haida Nation signature appear in the Gwaii Haanas advertisements.'],
    ['via-rail', 'VIA Rail Canada', 'via-rail-upper-2015', 'The guide back covers show VIA Rail’s signature, its A Green Choice badge and The Canadian campaign.'],
    ['hawkair', 'Hawkair', 'hawkair-script-2015', 'Hawkair’s script wordmark appeared in the 2015 Visit Terrace advertisement.'],
    ['helijet', 'Helijet', 'helijet-blue-charters-2015', 'The guides carry the blue Helijet panel in the North Coast charter advertisement.'],
    ['robson-valley-tourism', 'Visit the Robson Valley', 'visit-robson-valley-2015', 'McBride promoted the Robson Valley with a postcard-style advertisement.'],
    ['cassiar-cannery', 'Cassiar Cannery', 'cassiar-cannery-historic-resort-2015', 'The 2015 advertisement shows the historic resort and nature retreat wordmark.']
  ].map(([id, name, cover, description]) => ({ id, name, cover, description, kind: 'tourism-initiative' }))
]

export const NORTHERN_TRAVEL_GUIDE_RECORDS = records.map(({ extraSources = [], ...record }) => ({
  ...record,
  sources: [...[...new Map(artwork[record.id].map(({ sourceUrl, sourceFile }) => [
    sourceUrl, { title: sourceFile, url: sourceUrl }
  ])).values()], ...extraSources]
}))
