const organization = 'tourism-association'
const program = 'tourism-initiative'
const coOp = 'destination-bc-co-op-marketing'
export const SECTOR_GUIDELINES = 'https://www.destinationbc.ca/content/uploads/2023/11/DBC-CoOp-Application-Guidelines-2024-25-FINAL5.pdf'

const source = (title, url) => ({ title, url })
const relation = (subject, label, type = 'related-to') => ({ subject, label, type })
const operator = (subject, label) => relation(subject, label, 'operated-by')
const appendix = (page) => source(
  `Destination BC 2024–25 Co-op Guidelines, Appendix 3, printed p. ${page}`,
  `${SECTOR_GUIDELINES}#page=${page + 2}`
)
const funding2020 = source('Destination BC’s May 2020 roster and funding announcement',
  'https://www.destinationbc.ca/news/bcs-tourism-sectors-dbc-funding/')
const paddleLaunch = source('Destination BC’s April 2023 Paddle BC announcement',
  'https://www.destinationbc.ca/news/paddle-bc-news-release-explore-the-best-paddling-in-canada-right-here-in-british-columbia/')
const birdLaunch = source('Destination BC’s November 2020 launch account',
  'https://www.destinationbc.ca/news/the-bc-bird-trail-takes-flight/')
const fishingAbout = source('Fishing BC’s project and partner description', 'https://fishingbc.com/about-fishing-bc/')
const golfAbout = source('Allied Golf Association’s account of the marketing alliance', 'https://aga-bc.org/bcgma/')
const oceanProject = source('Island Coastal Economic Trust ocean boating brand project',
  'https://islandcoastaltrust.ca/project/ocean-boating-marine-tourism-marketing/')
const bikeAbout = source('Mountain Biking BC’s project history', 'https://mountainbikingbc.ca/about/')
const wineRename = source('Wine Growers British Columbia’s name-change announcement',
  'https://winebc.com/industry/media_releases/british-columbia-wine-institute-excited-to-announce-new-name/')

const sectors = [
  {
    id: 'backcountry-lodges-of-bc', name: 'Backcountry Lodges of British Columbia Association', shortName: 'Backcountry Lodges of BC',
    kind: organization, from: 2004, page: 38, aliases: ['BLBCA', 'Backcountry Lodges'],
    officialUrl: 'https://backcountrylodgesofbc.com/',
    description: 'A member-directed association of independent backcountry lodges.',
    history: 'Lodge operators formed the association in 2004 after a 2003 liability-insurance crisis. Joint operating protocols reopened access to insurance. The association later developed shared marketing with Destination BC.',
    sources: [source('BLBCA’s account of its formation', 'https://backcountrylodgesofbc.com/blog/backcountry-lodges-of-bc/'),
      source('BLBCA media resources', 'https://backcountrylodgesofbc.com/media/')]
  },
  {
    id: 'bc-ale-trail', name: 'The BC Ale Trail', kind: program, from: 2016, page: 38,
    aliases: ['BC Ale Trail', 'Ale Trail'], officialUrl: 'https://bcaletrail.ca/',
    description: 'A visitor marketing program built around itineraries linking BC craft breweries and their communities.',
    history: 'The first seven regional trails launched in October 2016. Eight more followed in 2017. The Number Creative documents developing the identity guidelines with the project team and stakeholders.',
    relations: [operator('bc-craft-brewers-guild', 'Program delivered with')],
    sources: [source('The BC Ale Trail’s launch and expansion account', 'https://bcaletrail.ca/update-from-the-bc-ale-trail/'),
      source('Ale Trail delivery team and Co-op partnership', 'https://bcaletrail.ca/about-team/'),
      source('The Number Creative’s project and identity case study', 'https://thenumber.ca/work/bc-ale-trail/')]
  },
  {
    id: 'bc-bird-trail', name: 'The BC Bird Trail', kind: program, from: 2020, page: 38,
    aliases: ['BC Bird Trail', 'Birding'], officialUrl: 'https://bcbirdtrail.ca/',
    description: 'A collaboration that promotes birdwatching in BC through visitor itineraries and travel information.',
    history: 'The trail launched in September 2020 with Richmond and Delta, the Fraser Valley, and central Vancouver Island itineraries. Destination BC’s 2024–25 guidelines identify Tourism Richmond as the sector lead.',
    relations: [operator('tourism-richmond', '2024–25 sector lead'),
      relation('tourism-chilliwack', 'Fraser Valley launch partner'),
      relation('indigenous-tourism-bc', 'Launch partner')],
    sources: [birdLaunch, source('The BC Bird Trail’s production partners', 'https://bcbirdtrail.ca/partners/')]
  },
  {
    id: 'camping-rving-bc-coalition', name: 'Camping and RVing BC Coalition', shortName: 'Camping & RV in BC',
    kind: organization, page: 38, aliases: ['Camping & RVing BC Coalition', 'Camping and RV in BC', 'Camping and RVing British Columbia Coalition'],
    officialUrl: 'https://www.campingrvbc.com/about/',
    description: 'A nonprofit marketing collective for camping and recreational vehicle travel across BC.',
    history: 'The coalition traces its origins to the Experiences BC sector marketing program. Its 2014 newsletter shows the Camping & RV in BC signature. Destination BC identifies the BC Lodging and Campgrounds Association as the sector lead in 2020.',
    relations: [operator('bc-lodging-campgrounds-association', 'Coalition managed by')],
    sources: [source('Coalition origins and membership', 'https://www.campingrvbc.com/about/'),
      source('Coalition March 2014 newsletter', 'https://www.campingrvbc.com/wp-content/uploads/2014/10/Newsletter-March-2014.pdf'), funding2020]
  },
  {
    id: 'bc-farmers-market-trail', name: 'The BC Farmers’ Market Trail', kind: program, from: 2018, page: 38,
    aliases: ["BC Farmers' Market Trail", 'BC Farmers Market Trail', 'Farmers’ Markets'],
    officialUrl: 'https://bcfarmersmarkettrail.com/',
    description: 'A consumer directory and travel campaign for member farmers’ markets throughout BC.',
    history: 'The BC Association of Farmers’ Markets launched the website in 2018 with support from Destination BC, Columbia Basin Trust and Kootenay Rockies Tourism.',
    relations: [operator('bc-association-farmers-markets', 'Campaign operated by'),
      relation('kootenay-rockies-tourism', 'Launch supporter')],
    sources: [source('BCAFM’s 2018 annual report', 'https://bcfarmersmarket.org/app/uploads/2019/03/2018BCAFMAnnualReport.pdf'),
      source('Destination BC’s account of the trail partnership', 'https://www.destinationbc.ca/news/bc-farmers-markets-association-on-pivoting-member-operations/')]
  },
  {
    id: 'fishing-bc', name: 'Fishing BC', kind: program, from: 2016, page: 38,
    aliases: ['FishingBC'], officialUrl: 'https://fishingbc.com/',
    description: 'A joint marketing initiative for freshwater and saltwater fishing tourism.',
    history: 'The Freshwater Fisheries Society of BC dates the partnership to 2016. Destination BC announced the new branded website and video in May 2017, naming the BC Fishing Resorts and Outfitters Association, Freshwater Fisheries Society of BC and Sport Fishing Institute of BC. The campaign’s partner page and the 2024–25 guidelines use BC Fishing Tourism Association. Two 2021 magazine ads show the white framed signature in use; they do not establish when it was adopted.',
    relations: [relation('bc-fishing-tourism-association', '2024–25 sector lead')],
    sources: [
      source('Freshwater Fisheries Society of BC, 2025–26 annual report, PDF p. 8', 'https://www.gofishbc.com/wp-content/uploads/2026/08/2025-26-FFSBC-Annual-Report-digital.pdf#page=8'),
      source('Destination BC’s May 2017 branded site and video announcement', 'https://www.destinationbc.ca/content/uploads/2018/07/2990_Corporate_24May2017_Newsletter.pdf'),
      fishingAbout,
      source('SOAR, September/October 2021, p. 7: white framed logo in a raster ad', 'https://www.pacificcoastal.com/wp-content/uploads/2021/09/SOARMagazine_Sept_Oct_2021.pdf#page=7'),
      source('SOAR, November/December 2021, p. 21: white framed logo in a raster ad', 'https://www.pacificcoastal.com/wp-content/uploads/2021/11/SOAR_Nov_Dec_2021.pdf#page=21')
    ]
  },
  {
    id: 'gardens-bc', name: 'Gardens British Columbia', shortName: 'Gardens BC', kind: organization, from: 2008, page: 38,
    aliases: ['Gardens BC', 'British Columbia Garden Tourism Coalition Society'], officialUrl: 'https://gardensbc.com/',
    description: 'A coalition of public gardens promoting garden tourism, registered as the British Columbia Garden Tourism Coalition Society.',
    history: 'The coalition dates its formation to 2008 and credits a group of garden marketers led by Dave Cowen of The Butchart Gardens. It appears in Destination BC’s 2020 sector roster.',
    sources: [source('Gardens BC’s origin and registered name', 'https://gardensbc.com/about/'),
      source('Gardens BC membership flyer, formation date and orange signature', 'https://gardensbc.com/app/uploads/2022/03/Gardens-BC-Join-Now-flyer.pdf#page=1'), funding2020]
  },
  {
    id: 'golf-in-british-columbia', name: 'Golf in British Columbia', kind: program, page: 38,
    aliases: ['Golf in BC', 'Golf in British Columbia.com'], officialUrl: 'https://golfinbritishcolumbia.com/',
    description: 'The visitor-facing campaign of the BC Golf Marketing Alliance.',
    history: 'Destination BC documents the alliance website and Co-op marketing activity in 2020. The alliance’s 2025 contest rules pair the promotional wordmark with its own name.',
    relations: [operator('bc-golf-marketing-alliance', 'Campaign operated by')],
    sources: [golfAbout, source('Destination BC’s 2020 golf marketing account', 'https://www.destinationbc.ca/news/bc-golf-sector-pivots-during-covid-19-pandemic/'),
      source('Alliance 2025 contest rules', 'https://golfinbritishcolumbia.com/assets/documents/BCGMA-Contest-Rules-2025-BC-Golf-Adventure-to-Vancouver-Island_250319.pdf')]
  },
  {
    id: 'bc-guest-ranchers-association', name: 'BC Guest Ranchers Association', kind: organization, page: 39,
    aliases: ['BC Guest Ranches', 'Guest Ranches'], officialUrl: 'https://bcguestranches.com/',
    description: 'A member organization that promotes guest ranches and sets standards for inclusion in its directory.',
    history: 'The association’s white ranch signature carries the date 1985. Destination BC lists the association as sector lead in 2020 and reproduces the signature in its 2024–25 guidelines.',
    sources: [source('Association membership requirements', 'https://bcguestranches.com/membership/requirements/'), funding2020]
  },
  {
    id: 'guide-outfitters-association-bc', name: 'Guide Outfitters Association of British Columbia', shortName: 'Guide Outfitters Association of BC',
    kind: organization, from: 1966, page: 39, aliases: ['GOABC', 'Guide Outfitters Association of BC'],
    officialUrl: 'https://www.goabc.org/',
    description: 'An association representing British Columbia’s guide outfitting industry.',
    history: 'The association dates its formation to 1966 and identifies its original incorporated name as the Western Guides and Outfitters Association. The 2024–25 guidelines show the wildlife badge with the “Wildlife First” line.',
    sources: [source('GOABC history of guide outfitting and its formation', 'https://www.goabc.org/working-in-guide-outfitting/guide-outfitting-history/'),
      source('GOABC’s Conservation at Work, earlier legal name', 'https://www.goabc.org/wp-content/uploads/2017/04/conservationatwork-web-opt.pdf'), funding2020]
  },
  {
    id: 'mountain-biking-bc', name: 'Mountain Biking BC', kind: program, from: 2010, page: 39,
    aliases: ['Mountain Bike BC', 'Mountain Biking'], officialUrl: 'https://mountainbikingbc.ca/',
    description: 'A provincial mountain biking destination marketing program.',
    history: 'The Western Canada Mountain Bike Tourism Association launched Mountain Biking BC in 2010 to coordinate sector promotion. The appendix shows the stacked lettering beside the trail symbol and a small tagline underneath.',
    relations: [operator('western-canada-mountain-bike-tourism-association', 'Program launched by')],
    sources: [bikeAbout, funding2020, source('March 2023 Outdoor Adventure & Travel Show guide, BC Bike Show sponsor artwork', 'https://outdooradventureshow.ca/wp-content/uploads/2023/03/OAS_Vancouver_ShowGuide_2023_web.pdf#page=20')]
  },
  {
    id: 'paddle-bc', name: 'Paddle BC', kind: program, from: 2022, page: 39,
    aliases: ['PaddleBC', 'Wild and Wonderful Waterways'], officialUrl: 'https://paddlebc.ca/',
    description: 'A provincial collaboration promoting paddling experiences and destinations.',
    history: 'Paddle BC announced its launch in September 2022. The 2024–25 guidelines identify Destination Castlegar as the sector lead.',
    relations: [operator('destination-castlegar', '2024–25 sector lead'),
      relation('fishing-bc', 'Paddle BC project partner'), relation('indigenous-tourism-bc', 'Paddle BC project partner'),
      relation('cariboo-chilcotin-coast-tourism', 'Paddle BC project partner'),
      relation('sunshine-coast-tourism', 'Paddle BC project partner')],
    sources: [source('Paddle BC’s September 2022 launch announcement', 'https://paddlebc.ca/kayak-fishing-in-british-columbia/'), paddleLaunch]
  },
  {
    id: 'ahoy-british-columbia', name: 'AHOY British Columbia', shortName: 'AHOY BC', kind: program, page: 39,
    aliases: ['AHOY BC', 'Ocean Boating', 'Power and Sail Cruising'], officialUrl: 'https://ahoybc.com/',
    description: 'The coastal boating destination brand of the BC Ocean Boating Tourism Association.',
    history: 'The Island Coastal Economic Trust documented the association’s branding project in 2015. AHOY BC’s planner describes three coastal regions and eleven sub-regions.',
    relations: [operator('bc-ocean-boating-tourism-association', 'Campaign operated by')],
    sources: [oceanProject, source('2015 ocean boating project announcement', 'https://islandcoastaltrust.ca/wp-content/uploads/2023/01/NR_BCOBTA_2015_12May2015.pdf'),
      source('The association’s description of AHOY BC', 'https://ahoybc.com/about-bcobta/')]
  },
  {
    id: 'bc-snowmobile-federation', name: 'British Columbia Snowmobile Federation', shortName: 'BC Snowmobile Federation',
    kind: organization, from: 1965, page: 39, aliases: ['BCSF', 'BC Snowmobile Federation'],
    officialUrl: 'https://bcsf.org/',
    description: 'The nonprofit federation for organized snowmobiling and snowmobile clubs across BC.',
    history: 'The federation dates its formation to 1965. The 2024–25 guidelines identify it by its shield while directing visitors to the Let’s Ride BC campaign website.',
    sources: [source('BC Snowmobile Federation’s history and mandate', 'https://bcsf.org/about'),
      source('Let’s Ride BC visitor website', 'https://letsridebc.com/'), funding2020]
  },
  {
    id: 'wines-of-british-columbia', name: 'Wines of British Columbia', kind: program, page: 39,
    aliases: ['Wine BC', 'Wines of BC'], officialUrl: 'https://winebc.com/',
    description: 'A collective consumer brand for BC wine and wine tourism.',
    history: 'The BC Wine Institute’s fiscal 2021 strategic plan carries the grape-cluster signature. The institute became Wine Growers British Columbia in February 2021 and retained Wines of British Columbia as the consumer brand.',
    relations: [operator('wine-growers-british-columbia', 'Consumer brand promoted by')],
    sources: [source('BC Wine Institute fiscal 2021 strategic plan', 'https://winebc.com/industry/wp-content/uploads/sites/2/2020/05/F2021-Strategic-Plan-FINAL.pdf'),
      wineRename, source('Official Wines of British Columbia brand assets', 'https://winebc.com/industry/resources/image-brand-assets/')]
  }
]

const related = [
  {
    id: 'bc-craft-brewers-guild', name: 'BC Craft Brewers Guild', kind: organization, aliases: ['British Columbia Craft Brewers Guild'],
    officialUrl: 'https://bccraftbeer.com/',
    description: 'The provincial trade organization for craft brewers and a delivery partner for The BC Ale Trail.',
    history: 'Its 2018 constitution records its industry development mandate. Destination BC lists the guild as Ale Trail sector lead in 2020 and 2024–25.',
    sources: [source('2018 guild constitution', 'https://bccraftbeer.com/app/uploads/2018/10/BC-Craft-Brewers-Guild-Updated-2018-Constitution.pdf'), funding2020, appendix(38)]
  },
  {
    id: 'tourism-richmond', name: 'Tourism Richmond', kind: organization,
    officialUrl: 'https://www.visitrichmondbc.com/',
    description: 'Richmond’s destination marketing organization and the lead named for the provincial birding sector in the 2024–25 Co-op guidelines.',
    history: 'Tourism Richmond was a launch partner for the Richmond Delta Trail in 2020, alongside Tourism Delta.',
    relations: [relation('vancouver-coast-mountains', 'Community destination partner in the VCM region')],
    sources: [birdLaunch, appendix(38)]
  },
  {
    id: 'bc-lodging-campgrounds-association', name: 'BC Lodging and Campgrounds Association', kind: organization,
    aliases: ['BCLCA', 'BC Lodging & Campgrounds Association'], officialUrl: 'https://bclca.com/',
    description: 'The trade association representing privately owned and managed campgrounds, RV parks and lodging businesses.',
    history: 'Destination BC lists the association as the camping sector lead in 2020. The coalition identifies the association as its management company.',
    sources: [funding2020, source('Coalition management and mailing list', 'https://www.campingrvbc.com/enewsletter/')]
  },
  {
    id: 'bc-association-farmers-markets', name: 'BC Association of Farmers’ Markets', kind: organization, from: 2000,
    aliases: ['BCAFM', "BC Association of Farmers' Markets", 'BC Farmers Market Association'], officialUrl: 'https://bcfarmersmarket.org/',
    description: 'A nonprofit provincial association for farmers’ markets and the operator of The BC Farmers’ Market Trail.',
    history: 'Founded in 2000, the association records the consumer trail launch in its 2018 annual report, alongside a distinct refresh of the association’s own logo.',
    sources: [source('BCAFM’s account of its formation', 'https://bcfarmersmarket.org/2020-conference/get-involved/'),
      source('BCAFM 2018 annual report and brand refresh', 'https://bcfarmersmarket.org/app/uploads/2019/03/2018BCAFMAnnualReport.pdf'), appendix(38)]
  },
  {
    id: 'bc-fishing-tourism-association', name: 'BC Fishing Tourism Association', kind: organization, aliases: ['BCFTA'],
    officialUrl: 'https://bcfishingtourism.com/',
    description: 'The association named as the provincial fishing sector lead in the 2024–25 guidelines and as a partner by Fishing BC.',
    history: 'Destination BC’s 2017 launch account names the BC Fishing Resorts and Outfitters Association in the partnership. The formal relationship between the two association names remains open.',
    sources: [fishingAbout, appendix(38)]
  },
  {
    id: 'bc-golf-marketing-alliance', name: 'BC Golf Marketing Alliance', kind: organization,
    aliases: ['BCGMA', 'British Columbia Golf Marketing Alliance'], officialUrl: 'https://aga-bc.org/bcgma/',
    description: 'A strategic partnership of golf courses, regional golf marketing consortia, Destination BC and British Columbia Golf.',
    history: 'Destination BC documents the alliance’s Co-op partnership and consumer website in 2020.',
    sources: [golfAbout, appendix(38)]
  },
  {
    id: 'western-canada-mountain-bike-tourism-association', name: 'Western Canada Mountain Bike Tourism Association',
    shortName: 'Mountain Bike Tourism Association', kind: organization, aliases: ['MBTA', 'Western Mountain Bike Tourism Association'],
    officialUrl: 'https://www.mbta.ca/',
    description: 'The industry association behind the Mountain Biking BC program.',
    history: 'The association published Sea to Sky research in 2006 and announced a partnership with Tourism British Columbia in 2009. Its Mountain Biking BC initiative began in 2010.',
    sources: [source('MBTA announcements from 2006 and 2009', 'https://www.mbta.ca/news/mbta-initiatives/page/3/'), bikeAbout, appendix(39)]
  },
  {
    id: 'destination-castlegar', name: 'Destination Castlegar', kind: organization, officialUrl: 'https://www.destinationcastlegar.com/',
    description: 'The destination management organization for Castlegar and the lead named for paddling in the 2024–25 guidelines.',
    history: 'Its marketing director launched Paddle BC in 2022. Destination BC identifies Destination Castlegar as a Paddle BC partner in 2023.',
    relations: [relation('kootenay-rockies-tourism', 'Community destination partner listed by Kootenay Rockies Tourism')],
    sources: [source('Kootenay Rockies Tourism’s community partner listing', 'https://www.kootenayrockies.com/partner/destination-castlegar/'), paddleLaunch, appendix(39)]
  },
  {
    id: 'bc-ocean-boating-tourism-association', name: 'BC Ocean Boating Tourism Association', kind: organization,
    aliases: ['BCOBTA', 'British Columbia Ocean Boating Tourism Association'], officialUrl: 'https://ahoybc.com/about-bcobta/',
    description: 'A nonprofit society with board representation from coastal regions and marine tourism sectors.',
    history: 'In 2015 the Island Coastal Economic Trust identified the association as lead for a project to develop a marine tourism brand and marketing strategy.',
    sources: [oceanProject, source('BCOBTA’s governance and mandate', 'https://ahoybc.com/about-bcobta/'), appendix(39)]
  },
  {
    id: 'wine-growers-british-columbia', name: 'Wine Growers British Columbia', kind: organization, from: 1990,
    aliases: ['WGBC', 'British Columbia Wine Institute', 'BC Wine Institute', 'BCWI'], officialUrl: 'https://winebc.com/industry/',
    description: 'The industry organization that promotes Wines of British Columbia.',
    history: 'The British Columbia Wine Institute was established in 1990 alongside the BC VQA program. It adopted the Wine Growers British Columbia name in February 2021.',
    sources: [source('Wine BC’s account of the 1990 founding', 'https://winebc.com/industry/media_releases/bc-vqa-founders-toast-25-years-of-building-an-industry/'), wineRename, appendix(39)]
  },
  {
    id: 'lets-ride-bc', name: 'Let’s Ride BC', kind: program, aliases: ['LetsRideBC', "Let's Ride BC"],
    officialUrl: 'https://letsridebc.com/',
    description: 'The BC Snowmobile Federation’s visitor program for snowmobiling destinations and trip planning.',
    history: 'Destination BC’s 2024–25 guidelines give the campaign’s website in the snowmobile sector row beside the federation’s shield. The campaign publishes its own visitor guide and identity.',
    relations: [operator('bc-snowmobile-federation', 'Tourism program of')],
    sources: [source('Let’s Ride BC campaign and federation attribution', 'https://letsridebc.com/'),
      source('BC Snowmobile Visitor Guide', 'https://letsridebc.com/visitor-guide'), appendix(39)]
  }
]

export const TOURISM_SECTOR_RECORDS = [
  {
    id: coOp, name: 'Co-operative Marketing Partnerships Program', shortName: 'Co-op Marketing',
    kind: program, from: 2015, aliases: ['Destination BC Co-op Program', 'Provincial Sector Organizations', 'Sector tourism marketing'],
    officialUrl: 'https://www.destinationbc.ca/what-we-do/funding-sources/co-op-marketing/',
    description: 'Destination BC’s application-based marketing partnership program for community consortia and provincial tourism sectors.',
    history: 'Destination BC developed the program in 2015. Appendix 3 of the 2024–25 guidelines is a dated roster of 15 sectors, their named contacts and their published signatures.',
    relations: [operator('destination-bc', 'Program administered by')],
    sources: [source('Destination BC program development and intake', 'https://www.destinationbc.ca/news/applications-for-the-co-op-program-are-now-open/'), appendix(38), appendix(39)],
    identityStatus: 'distinct-unconfirmed',
    nextAction: 'Check program publications for a standalone program mark.'
  },
  ...sectors.map(({ page, ...record }) => ({
    ...record,
    cover: `${record.id}-appendix-2024`,
    relations: [...(record.relations ?? []), relation(coOp, 'Listed in the 2024–25 sector roster for', 'listed-by')],
    sources: [...record.sources, appendix(page)]
  })),
  ...related
]
