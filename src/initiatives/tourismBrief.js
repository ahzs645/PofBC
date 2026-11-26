const libraryRecord = 'https://digitalcollections.llbc.leg.bc.ca/handle/123456789/55920'
const libraryPdf = 'https://digitalcollectionsrepository.llbc.leg.bc.ca/server/api/core/bitstreams/c1cd638e-4d7e-4bba-8911-f10d5f19af93/content'
const dbc = 'https://www.destinationbc.ca/'
const go2 = 'https://www.go2hr.ca/'

const source = (id, title, publisher, url, date) => ({ id, title, publisher, url, date })
const link = (label, url) => ({ label, url })
const cite = (sourceId, locator) => ({ sourceId, locator })
const brief = (page) => ({ sourceId: 'tourism-brief-2009-05', page, url: `${libraryPdf}#page=${page}` })
const tourismRecord = (label, record) => link(label, `?view=initiatives&initiative=tourism&record=${record}`)
const gallery = (label, logos) => link(label, `?view=gallery&logos=${logos}`)

export const tourismBriefSources = [
  source('tourism-brief-2009-05', 'The Tourism Brief, May 2009', 'Tourism British Columbia · Legislative Library of BC digital collections', libraryRecord, 'May 2009'),
  source('tbc-service-plan-2009', 'Tourism British Columbia 2009/10–2011/12 Service Plan', 'Tourism British Columbia', 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/tbc.pdf', '2009'),
  source('tbc-employees-first-2011', 'Employees First, second edition', 'Ministry of Jobs, Tourism and Innovation and go2 Tourism HR Society', dbc + 'content/uploads/2018/08/EmployeesFirstTBEGuide2011_July07.pdf', '2011'),
  source('tourism-education-2013', 'BC Tourism and Hospitality Education: 2013 Status Report', 'BC Council on Admissions and Transfer', 'https://www.bccat.ca/pubs/Reports/TourismEdReport2013.pdf', '2013'),
  source('dbc-industry-partners', 'Industry Partners', 'Destination BC', dbc + 'who-we-are/regional-community-industry-partner/industry-partners/'),
  source('go2hr-current', 'About go2HR', 'go2HR Tourism Society', go2 + 'about-us'),
  source('go2hr-superhost', 'SuperHost customer service training', 'go2HR', go2 + 'training/customer-service'),
  source('ita-2006-07', 'Industry Training Authority 2006/07 Annual Service Plan Report', 'Industry Training Authority', 'https://skilledtradesbc.ca/media/940/download', '2007'),
  source('ita-2014-15', 'Industry Training Authority 2014/15 Annual Service Plan Report', 'Industry Training Authority', 'https://www.bcbudget.gov.bc.ca/Annual_Reports/2014_2015/pdf/agency/ita.pdf', '2015'),
  source('skilledtradesbc-cook', 'Cook (Professional Cook 3) and the progressive trade levels', 'SkilledTradesBC', 'https://skilledtradesbc.ca/cook-professional-cook-3-red-seal'),
  source('skilledtradesbc-food-trades', 'Food and service trades', 'SkilledTradesBC', 'https://skilledtradesbc.ca/find-your-trade?f%5B0%5D=skills_taxonomy_term_name%3AExpressive'),
  source('thrc-propel', 'Propel Student Work Placement Program', 'Tourism HR Canada', 'https://tourismhr.ca/program-and-service/propel-student-work-placement-program/'),
  source('linkbc-closure', 'It’s my last day at BCIT', 'Morgan Westcott · former LinkBC general manager', 'https://tourismnerd.wordpress.com/2018/02/27/its-my-last-day-at-bcit/', 'February 2018'),
  source('linkbc-textbook', 'Introduction to Tourism and Hospitality in BC, second edition', 'BCcampus Open Education', 'https://opentextbc.ca/introtourism2e/', '2021'),
  source('linkbc-website-2015', 'Archived LinkBC homepage', 'LinkBC · Internet Archive', 'https://web.archive.org/web/20150903000608/http://linkbc.ca:80/', 'September 3, 2015'),
  source('linkbc-study-website-2015', 'Archived Study Tourism in BC homepage', 'LinkBC · Internet Archive', 'https://web.archive.org/web/20150903001448/http://studytourisminbc.com:80/', 'September 3, 2015'),
  source('linkbc-torc-2013', 'Archived Tourism Online Resource Centre', 'LinkBC · Internet Archive', 'https://web.archive.org/web/20130118070153/http://torc.linkbc.ca:80/main/index.php?torc_show&wid=6', 'January 18, 2013'),
  source('go2hr-capilano-2018', 'President’s Report to the Board, March 2018', 'Capilano University', 'https://www.capilanou.ca/media/capilanouca/about-capu/governance/presidentx27s-office/reports-amp-initiatives/presidentx27s-report-to-the-board/Presidents-Report-to-the-Board-March-2018-Final.pdf', 'March 2018'),
  source('tec-capilano-2017', 'Business and Tourism Educators Articulation and Conference', 'Capilano University', 'https://beac-tec2017.capilanou.ca/accommodation/', '2017'),
  source('vcc-linkbc', 'VCC Hospitality students win LinkBC competition', 'Vancouver Community College', 'https://www.vcc.ca/international/about/news-and-events/news/article/vcc-hospitality-students-win-linkbc-competition.html', 'November 2013'),
  source('dbc-winning-pitch-2018', 'Directions, April 2018', 'Destination BC', dbc + 'content/uploads/2018/07/DBC-Directions-April-62c-2018.pdf', 'April 2018'),
  source('bccat-articulation-2021', 'Joint Tourism and Hospitality Management articulation meeting minutes', 'BC Council on Admissions and Transfer', 'https://www.bccat.ca/minutes/2021Tourism.pdf', 'April 2021'),
  source('dbc-visitor-services', 'Visitor Services', 'Destination BC', dbc + 'what-we-do/destination-management/visitor-services/'),
  source('dbc-annual-report-2014-15', 'Destination BC 2014/15 Annual Service Plan Report', 'Destination BC', dbc + 'content/uploads/2018/07/DBC_AnnServicePlanReport_FINAL.pdf', '2015'),
  source('dbc-industry-performance', 'Industry Performance', 'Destination BC', dbc + 'research-insights/type/industry-performance/'),
  source('dbc-travel-media', 'Travel Media', 'Destination BC', dbc + 'what-we-do/marketing/travel-media/'),
  source('dbc-learning-centre', 'Learning Centre', 'Destination BC', dbc + 'learning-centre/'),
  source('dbc-listings-portal', 'Tourism Business Listings Portal', 'Destination BC', 'https://listingsportal.destinationbc.ca/s/'),
  source('dbc-marketing-strategy-2026', '2026 Marketing Plan and 2026–2028 Marketing Strategy announcement', 'Destination BC', dbc + 'newsletters/2026/03/destination-bc-directions-march-12-2026.html', 'March 2026'),
  source('surrey-sport-tourism', 'Surrey Sport Tourism Plan', 'City of Surrey', 'https://www.surrey.ca/sites/default/files/corporate-reports/RPT_2010_R262.pdf', '2010'),
  source('sport-tourism-guide-2011', 'Sport Tourism: A Guide to the Industry', 'Ministry of Jobs, Tourism and Innovation', dbc + 'content/uploads/2018/08/SportTourismTBEGuide2011_July07.pdf', '2011'),
  source('sport-marketplace-archive', 'Archived BC Sport Tourism Events Marketplace website', 'BC Sport Tourism Events Marketplace · Internet Archive', 'https://web.archive.org/web/20090412055505/http://www.bcsporttourismmarketplace.com:80/', 'April 12, 2009'),
  source('hosting-bc-archive', 'Archived Hosting BC homepage', 'Hosting BC · Internet Archive', 'https://web.archive.org/web/20090414184047/http://www.hostingbc.ca:80/', 'April 14, 2009'),
  source('viasport-hosting-bc', 'Hosting BC grant program', 'viaSport BC', 'https://viasport.ca/grants/hosting-bc/'),
  source('province-hosting-bc-2012', 'Provincial funding announcement for Hosting BC', 'Province of British Columbia', 'https://news.gov.bc.ca/releases/2012CSCD0088-001467', 'September 2012'),
  source('lift-2011', 'LIFT Philanthropy Partners’ pre-budget submission', 'LIFT Philanthropy Partners', 'https://www.ourcommons.ca/Content/Committee/411/FINA/WebDoc/WD5138047/411_FINA_PBC2011_Briefs/LIFT%20Philanthropy%20Partners%20E.pdf', '2011'),
  source('lift-current', 'Our Organization', 'LIFT Impact Partners', 'https://www.liftpartners.ca/organization'),
  source('vanoc-windup', 'Vancouver 2010 Games officially wrap up', 'Canadian Olympic Committee', 'https://olympic.ca/press/release-vancouver-2010-games-officially-wrap-up/', '2014'),
  source('tourism-2010-resource-citation', 'Demand Analysis Study for Cultural Performance/Events Spaces', 'City of Vancouver', 'https://vancouver.ca/files/cov/demand-analysis-study-cultural-performance-event-spaces-northeast-false-creek-hastings-park.pdf', 'December 2010'),
  source('tourism-2010-resource-archive', 'Archived Tourism 2010 Resource Centre', 'Tourism British Columbia · Internet Archive', 'https://web.archive.org/web/20090402233315/http://www.tourism2010.com:80/CMS/', 'April 2, 2009'),
  source('tota-history', 'About TOTA', 'Thompson Okanagan Tourism Association', 'https://www.totabc.org/about'),
  source('destination-osoyoos-plan', 'Five Year Business Plan 2024–2029', 'Destination Osoyoos', 'https://www.destinationosoyoos.com/wp-content/uploads/2023/10/5-Year-Strategy-2024-2029.pdf'),
  source('itbc-history', 'Who We Are', 'Indigenous Tourism BC', 'https://www.indigenousbc.com/corporate/who-we-are/')
]

export const tourismBriefPublication = {
  id: 'tourism-brief-may-2009', title: 'The Tourism Brief · May 2009', kind: 'stakeholder newsletter',
  description: 'Tourism British Columbia’s May 2009 issue reports on Olympic marketing, workforce training, research, visitor services and tourism partners. The Legislative Library’s copy preserves the newsletter and its individual articles.',
  sourceRefs: [cite('tourism-brief-2009-05', 'Catalogue record 55920'), brief(2)],
  links: [link('Explore the programs and partners', '?view=initiatives&initiative=tourism&section=programs')]
}

export const tourismProgramsSection = {
  id: 'programs', label: 'Programs & partners', type: 'records', layout: 'text', searchable: true, searchPlaceholder: 'Search programs or organizations',
  title: 'Tourism programs and partners',
  description: 'Follow the organizations, services and campaigns in Tourism BC’s May 2009 Tourism Brief. Current status reviewed November 2026.',
  records: [
    {
      id: 'go2hr', title: 'go2HR', kind: 'independent industry association', statusLabel: 'Active',
      searchTerms: ['go2 Tourism HR Society', 'Hospitality Industry Education Advisory Committee', 'HIEAC'],
      description: 'The Hospitality Industry Education Advisory Committee dates to 1979. In 2003 the industry broadened its workforce mandate and rebranded it as go2. The 2009 newsletter reported on its Propel training division.',
      current: 'Destination BC lists go2HR as an industry partner. The independent society serves BC tourism and hospitality employers and workers with HR and workplace safety advice, training, labour-market research and a job board. It took over WorldHost in 2017 and relaunched the courses under the SuperHost name.',
      sourceRefs: [brief(9), cite('tbc-employees-first-2011', 'Foreword'), cite('tourism-education-2013', 'Printed p. 17'), cite('dbc-industry-partners'), cite('go2hr-current'), cite('go2hr-superhost')],
      links: [link('Visit go2HR', go2), tourismRecord('Propel and Professional Cook', 'propel-cook-apprenticeship'), tourismRecord('SuperHost and WorldHost artwork and websites', 'worldhost')]
    },
    {
      id: 'propel-cook-apprenticeship', title: 'Propel and Professional Cook', kind: 'go2 division and apprenticeship', statusLabel: 'Credentials continue',
      searchTerms: ['cook baker meatcutter', 'Professional Cook 1 2 3', 'Industry Training Organization', 'Red Seal'],
      description: 'By 2006/07 go2 had been sanctioned as an Industry Training Organization. Its Propel division oversaw Cook, Baker and Meatcutter and led the 2008 review behind the three-tier Professional Cook program targeted for September 2009.',
      current: 'The Industry Training Authority brought Industry Training Organization functions in-house by October 31, 2014. SkilledTradesBC now lists Professional Cook 1 and 2 and Cook (Professional Cook 3), the Red Seal level, alongside Baker and Meatcutter. Tourism HR Canada runs a separate national student placement program also called Propel.',
      sourceRefs: [brief(9), cite('ita-2006-07', 'Printed p. 35'), cite('ita-2014-15', 'Enhance ITA Capability'), cite('skilledtradesbc-cook'), cite('skilledtradesbc-food-trades'), cite('thrc-propel')],
      links: [link('Current Professional Cook pathway', 'https://skilledtradesbc.ca/cook-professional-cook-3-red-seal'), tourismRecord('go2HR', 'go2hr')]
    },
    {
      id: 'linkbc', title: 'LinkBC', kind: 'post-secondary education network', statusLabel: 'Historical network',
      searchTerms: ['Link BC', 'Capilano University', 'Vancouver Community College', 'Study Tourism in BC', 'Hire BC’s BEST', 'Tourism Educators Conference'],
      description: 'Two provincially supported leadership and innovation centres for tourism and hospitality merged in 2007 to form LinkBC. The May 2009 issue records 20 public post-secondary partners and staff hosted by Capilano University and Vancouver Community College. LinkBC ran Study Tourism in BC, Hire BC’s BEST, industry networking, educator support and an online library. The issue also announced plans for a Games education portal.',
      current: 'Former general manager Morgan Westcott documents the network’s wind-down in the mid-2010s. Its precise closure date remains unverified. LinkBC helped coordinate the original open textbook, which BCcampus still hosts in a revised edition.',
      sourceRefs: [brief(10), cite('tourism-education-2013', 'Printed p. 7 and LinkBC network sections'), cite('linkbc-website-2015'), cite('linkbc-closure'), cite('linkbc-textbook')],
      links: [link('Open BCcampus tourism textbook', 'https://opentextbc.ca/introtourism2e/'), tourismRecord('Tourism Online Resource Centre', 'tourism-online-resource-centre'), tourismRecord('Study Tourism in BC', 'study-tourism-in-bc'), tourismRecord('Hire BC’s BEST and Student-Industry Rendezvous', 'linkbc-student-recruitment'), tourismRecord('Tourism Educators Conference', 'tourism-educators-conference'), tourismRecord('Student Case Competition', 'tourism-student-case-competition')]
    },
    {
      id: 'tourism-online-resource-centre', title: 'Tourism Online Resource Centre', kind: 'LinkBC online library', statusLabel: 'Historical website',
      searchTerms: ['TORC', 'bctorc.ca', 'torc.linkbc.ca'],
      description: 'LinkBC’s free online library gathered tourism research and resources for students, instructors and industry. The newsletter lists bctorc.ca as its address in May 2009.',
      current: 'The Internet Archive preserves the library’s 2013 landing page at torc.linkbc.ca. A current official repository carrying forward TORC’s catalogue remains unverified. LinkBC’s open tourism textbook is still available through BCcampus.',
      sourceRefs: [brief(10), cite('linkbc-torc-2013'), cite('linkbc-textbook')],
      links: [tourismRecord('LinkBC', 'linkbc')]
    },
    {
      id: 'study-tourism-in-bc', title: 'Study Tourism in BC', kind: 'LinkBC education campaign', statusLabel: 'Historical website',
      searchTerms: ['studytourisminbc.ca', 'studytourisminbc.com', 'Games education portal'],
      description: 'LinkBC piloted tourism and hospitality education marketing abroad in 2008 and promoted the Study Tourism in BC website in 2009. Its later marketing plan addressed prospective students, current students and alumni. The 2015 website let readers browse programs by discipline.',
      current: 'The Internet Archive preserves the portal. A current official successor and the launch of the separately announced 2009 Games education portal remain unverified.',
      sourceRefs: [brief(10), cite('tourism-education-2013', 'Study Tourism in BC Marketing Plan'), cite('linkbc-study-website-2015')],
      links: [tourismRecord('LinkBC', 'linkbc')]
    },
    {
      id: 'linkbc-student-recruitment', title: 'Hire BC’s BEST and Student-Industry Rendezvous', kind: 'LinkBC student recruitment', statusLabel: 'Historical initiatives',
      description: 'In 2009 LinkBC promoted a hiring guide for employers and speed-networking events connecting students with tourism and hospitality employers.',
      current: 'Capilano University reports a go2HR Student Rendezvous with hotels and tour companies in 2018. go2HR currently operates a tourism and hospitality job board. A current edition of the LinkBC hiring guide remains unverified.',
      sourceRefs: [brief(10), cite('go2hr-capilano-2018'), cite('go2hr-current')],
      links: [tourismRecord('LinkBC', 'linkbc'), tourismRecord('go2HR', 'go2hr')]
    },
    {
      id: 'tourism-educators-conference', title: 'Tourism Educators Conference', kind: 'professional development event', statusLabel: 'Later editions documented',
      description: 'BC’s tourism educators began holding the conference in 1991. LinkBC helped coordinate the 2009 edition, which focused on cruise tourism and hospitality education.',
      current: 'Capilano University records a joint business and tourism educators event in 2017. BC Council on Admissions and Transfer minutes document separate ongoing articulation work in 2021. A current edition of the original conference remains unverified.',
      sourceRefs: [brief(10), cite('tourism-education-2013', 'Tourism Educators Conference and Appendix C'), cite('tec-capilano-2017'), cite('bccat-articulation-2021')],
      links: [tourismRecord('LinkBC', 'linkbc')]
    },
    {
      id: 'tourism-student-case-competition', title: 'Tourism and Hospitality Student Case Competition', kind: 'student event', statusLabel: 'Historical event',
      searchTerms: ['LinkBC Student Case Competition', 'The Winning Pitch', 'Perfect Pitch', 'Student-Industry Rendezvous'],
      description: 'LinkBC ran an annual student case competition reported in 2009 and documented by Vancouver Community College in 2013. Destination BC records go2HR running a comparable provincial student competition, The Winning Pitch, in 2018.',
      current: 'A 2021 articulation committee recorded a proposal to revive The Winning Pitch as The Perfect Pitch. The full transfer history from LinkBC and an ongoing provincial series remain unverified.',
      sourceRefs: [brief(10), cite('vcc-linkbc'), cite('dbc-winning-pitch-2018'), cite('bccat-articulation-2021')],
      links: [tourismRecord('LinkBC', 'linkbc'), tourismRecord('go2HR', 'go2hr')]
    },
    {
      id: 'welcome-the-world', title: 'Welcome the World', kind: 'Tourism BC consumer campaign', statusLabel: 'Historical campaign',
      searchTerms: ['DiscoverOurBC.com', 'BC Field Reporters', 'HelloBC videos', 'British Columbia Insider’s Guide'],
      description: 'Tourism BC launched this consumer campaign ahead of Vancouver 2010. The 2009 rollout used resident recommendations, BC Field Reporters, TV spots, short online films, social media, contests and a new Insider’s Guide. Advertisements pointed to DiscoverOurBC.com.',
      current: 'This was a Games-era campaign. Its original site and any later reuse of the name remain archival leads. Destination BC’s current marketing strategy and travel site run under the Super, Natural British Columbia brand.',
      sourceRefs: [brief(3), cite('tbc-service-plan-2009', 'Welcome the World Initiative'), cite('dbc-marketing-strategy-2026')],
      links: [tourismRecord('British Columbia Insider’s Guide', 'insiders-guide'), tourismRecord('HelloBC and SupernaturalBC.com', 'hellobc'), link('Spirit of 2010 provincial campaign', '?view=initiatives&initiative=spirit-of-2010')]
    },
    {
      id: 'team-2010', title: 'Team 2010 and the Ambassador Workshop', kind: 'Games volunteer training', statusLabel: 'Historical programs',
      searchTerms: ['WorldHost Training Services', 'Vancouver Organizing Committee', 'VANOC', 'YVR', 'CBSA', 'TransLink', 'RCMP'],
      description: 'VANOC created Team 2010 to explain the Games to volunteers. WorldHost delivered train-the-trainer workshops to organizations including YVR Airport Authority, the Canada Border Services Agency and TransLink. WorldHost also promoted its separate Ambassador Workshop and reported related work with 2010 Legacies Now, the RCMP and the provincial visitor centre network.',
      current: 'These workshops document Games-era activity. VANOC was dissolved in 2014. The broader visitor-service training program continues as go2HR’s SuperHost.',
      sourceRefs: [brief(5), cite('vanoc-windup'), cite('go2hr-superhost')],
      links: [tourismRecord('SuperHost and WorldHost', 'worldhost'), tourismRecord('2010 Legacies Now', '2010-legacies-now')]
    },
    {
      id: '2010-legacies-now', title: '2010 Legacies Now', kind: 'Games legacy organization', statusLabel: 'Continues as LIFT Impact Partners',
      description: 'Established in 2000, 2010 Legacies Now used the Olympic bid and Games to support community programs. It partnered with Tourism BC on sport tourism and contributed to Games-related training initiatives.',
      current: 'LIFT Philanthropy Partners launched its new venture-philanthropy mission in February 2011 and became LIFT Impact Partners in 2021. It now helps Canadian social purpose organizations build capacity. viaSport administers the provincial Hosting BC grant.',
      sourceRefs: [brief(5), brief(11), cite('lift-2011'), cite('lift-current'), cite('viasport-hosting-bc')],
      links: [link('LIFT Impact Partners', 'https://www.liftpartners.ca/organization'), tourismRecord('Hosting BC', 'hosting-bc')]
    },
    {
      id: 'bc-sport-tourism-events-marketplace', title: 'BC Sport Tourism Events Marketplace', kind: 'sport tourism event', statusLabel: 'Historical event',
      description: 'Started in 2005 as a partnership between 2010 Legacies Now, Tourism BC and the Province. Its fifth edition, on April 1, 2009 at the Richmond Olympic Oval, brought together sport organizations and tourism representatives and marked the relaunch of the Hosting BC website.',
      current: 'The City of Surrey still lists the marketplace in its 2010 sport tourism plan. The final edition and a direct successor remain unverified. Hosting BC’s grant continues separately.',
      sourceRefs: [brief(11), cite('sport-marketplace-archive', 'Archived page includes Flash elements'), cite('surrey-sport-tourism', 'Tourism BC and 2010 Legacies Now Sport Tourism Partnership'), cite('viasport-hosting-bc')],
      links: [tourismRecord('Hosting BC', 'hosting-bc'), tourismRecord('2010 Legacies Now', '2010-legacies-now')]
    },
    {
      id: 'hosting-bc', title: 'Hosting BC', kind: 'venue directory and sport grant', statusLabel: 'Grant continues',
      searchTerms: ['hostingbc.ca', 'viaSport'],
      description: 'The 2009 issue records a relaunch of the Hosting BC venue directory. A 2011 sport tourism guide still describes the site for event organizers. The partnership also ran a separate funding stream for sport events under the Hosting BC name.',
      current: 'The Province confirmed viaSport as grant administrator in 2012. viaSport still publishes the Hosting BC grant and its intake dates. A current successor to the original venue directory remains unverified.',
      sourceRefs: [brief(11), cite('hosting-bc-archive'), cite('surrey-sport-tourism'), cite('sport-tourism-guide-2011', 'HostingBC.ca'), cite('province-hosting-bc-2012'), cite('viasport-hosting-bc')],
      links: [link('Hosting BC grant and intake dates', 'https://viasport.ca/grants/hosting-bc/')]
    },
    {
      id: 'tourism-2010-resource-centre', title: 'Tourism 2010 Resource Centre', kind: 'Tourism BC information website', statusLabel: 'Historical website',
      searchTerms: ['tourism2010.com'],
      description: 'The newsletter links to tourism2010.com. Its archived April 2009 homepage includes Games news, regional updates and a library of downloadable resources. A City of Vancouver study cites consulting it in August 2010.',
      current: 'The Games-era site survives through the Internet Archive. Its closing date and a direct successor remain unverified.',
      sourceRefs: [brief(2), cite('tourism-2010-resource-archive'), cite('tourism-2010-resource-citation', 'References')]
    },
    {
      id: 'tourism-visitor-services', title: 'Visitor Services and Visitor Centres', kind: 'Tourism BC operating function', statusLabel: 'Community network continues',
      searchTerms: ['Provincial Gateway Visitor Centres', 'Community Network Visitor Centres', 'Ninette Ollgaard', 'Margaret McCormick', 'Tourism Product Management'],
      description: 'In 2009 Tourism BC’s Visitor Services team covered the call centre, visitor information and product sales. The issue distinguishes Provincial Gateway Visitor Centres from the Community Network and records the appointment of Ninette Ollgaard as director.',
      current: 'Destination BC transferred airport visitor services to the Vancouver Airport Authority in 2014/15. It supports the Visitor Services Network Program of community-owned visitor centres and runs the network’s statistics program.',
      sourceRefs: [brief(7), cite('dbc-annual-report-2014-15', 'Message from the Board Chair and CEO'), cite('dbc-visitor-services')],
      links: [link('Current Visitor Services Network', dbc + 'what-we-do/destination-management/visitor-services/'), tourismRecord('HelloBC and SupernaturalBC.com', 'hellobc')]
    },
    {
      id: 'tourism-research-planning', title: 'Research & Planning', kind: 'Tourism BC operating function', statusLabel: 'Core reports continue',
      searchTerms: ['BC Tourism Indicators', 'International Visitor Arrivals', 'International Market Research', 'Value of the Visitor Centre Reports', 'Travel Activities and Motivations Survey', 'TAMS', 'Sunshine Coast Visitor Study', 'BC Nordic Ski Facility Client Report'],
      description: 'The 2009 team published Tourism Indicators, International Visitor Arrivals, international market profiles and visitor centre, travel motivation, sector and regional studies.',
      current: 'Destination BC’s Research & Insights publishes Tourism Indicators, International Visitor Arrivals and Value of Tourism. The Visitor Services Network has its own statistics portal. The newsletter’s one-off studies and the North American Travel Activities and Motivations Survey are historical evidence.',
      sourceRefs: [brief(6), cite('dbc-industry-performance'), cite('dbc-visitor-services')],
      links: [link('Current industry performance reports', dbc + 'research-insights/type/industry-performance/')]
    },
    {
      id: 'tourism-travel-media', title: 'Travel Media Relations', kind: 'Tourism BC operating function', statusLabel: 'Media visits continue',
      searchTerms: ['Japan', 'Japanese media', 'Vancouver', 'Whistler', 'press trips', 'FAMs', 'www2.hellobc.com/travelmedia'],
      description: 'Tourism BC hosted Japanese media in Vancouver and Whistler ahead of the Games and reported more than 26 online stories within a few weeks. The article describes the visit as one of a series of international trips dating to the bid phase.',
      current: 'Destination BC still organizes familiarization trips with regional and local partners and runs a Visiting Journalist Program. The 2009 Japan trip is a dated example of that function.',
      sourceRefs: [brief(8), cite('dbc-travel-media')],
      links: [link('Current Travel Media program', dbc + 'what-we-do/marketing/travel-media/')]
    },
    {
      id: 'tourism-industry-programs', title: 'Tourism BC Industry Programs', kind: 'industry services', statusLabel: 'Services continue at Destination BC',
      description: 'The 2009 issue linked to Tourism BC Industry Programs for operators. The service plan describes industry work spanning consumer marketing, partnerships, training and visitor services.',
      current: 'Destination BC offers resources through its Learning Centre and Tourism Business Listings Portal. Its current marketing strategy includes co-operative marketing and travel trade and media opportunities.',
      sourceRefs: [brief(2), cite('tbc-service-plan-2009'), cite('dbc-learning-centre'), cite('dbc-listings-portal'), cite('dbc-marketing-strategy-2026')],
      links: [link('Destination BC Learning Centre', dbc + 'learning-centre/'), link('Tourism Business Listings Portal', 'https://listingsportal.destinationbc.ca/s/')]
    },
    {
      id: 'thompson-okanagan-tourism', title: 'Thompson Okanagan Tourism Association', kind: 'regional nonprofit society', statusLabel: 'Active',
      searchTerms: ['TOTA', 'Okanagan Valley Tourist Association', 'Okanagan Similkameen Tourist Association', 'Glenn Mandziuk'],
      description: 'Founded in 1957 and incorporated in 1963, the association adopted its current name in 1997. The May 2009 issue reports that it appointed Glenn Mandziuk, previously CEO of Destination Osoyoos.',
      current: 'TOTA is an industry-led nonprofit and one of Destination BC’s six regional destination management organizations. It lists Symphony Tourism Services and the Thompson Okanagan Tourism Foundation as subsidiaries.',
      sourceRefs: [brief(12), cite('tota-history')],
      links: [link('TOTA history and subsidiaries', 'https://www.totabc.org/about'), gallery('TOTA in the logo gallery', 'collected-thompson-okanagan-tourism'), tourismRecord('Destination Osoyoos', 'destination-osoyoos')]
    },
    {
      id: 'destination-osoyoos', title: 'Destination Osoyoos', kind: 'local nonprofit society', statusLabel: 'Active',
      description: 'Destination Osoyoos Development Society began operating in 1996. The issue describes its tourism and community economic development role when Glenn Mandziuk left to lead TOTA.',
      current: 'Its 2024–2029 business plan identifies the society as the destination management organization and designated recipient of the Town’s accommodation tax. It works with local government, TOTA, Destination BC and other tourism stakeholders.',
      sourceRefs: [brief(12), cite('destination-osoyoos-plan', 'Management, Governance & Administration')],
      links: [link('Visit Destination Osoyoos', 'https://www.destinationosoyoos.com/'), tourismRecord('Thompson Okanagan Tourism Association', 'thompson-okanagan-tourism')]
    },
    {
      id: 'indigenous-tourism-bc', title: 'Indigenous Tourism BC', kind: 'Indigenous-led nonprofit', statusLabel: 'Active',
      searchTerms: ['Aboriginal Tourism BC', 'Aboriginal Tourism Association of BC', 'AtBC', 'ITBC'],
      description: 'The organization dates to 1996. In 2009 the Tourism Brief refers to Aboriginal Tourism BC in connection with an industry partner award.',
      current: 'Indigenous Tourism BC works with Indigenous tourism businesses, First Nations and community partners to develop Indigenous tourism across the province.',
      sourceRefs: [brief(12), cite('itbc-history')],
      links: [link('Indigenous Tourism BC', 'https://www.indigenousbc.com/corporate/who-we-are/'), gallery('Indigenous Tourism BC in the logo gallery', 'collected-indigenous-tourism-bc')]
    }
  ]
}

export const addTourismBriefContext = (record) => {
  if (record.id !== 'worldhost') return record
  return {
    ...record,
    description: 'SuperHost launched in 1985 for Expo 86. Tourism BC announced the WorldHost Training Services rebrand in May 2009, and the program and its assets passed to Destination BC in 2013. go2HR took over delivery in 2017 and revived the SuperHost name with updated classroom and online courses.',
    sourceRefs: [...record.sourceRefs, brief(5), cite('go2hr-superhost', 'WorldHost and SuperHost FAQ')],
    links: [...record.links, link('Current SuperHost courses at go2HR', go2 + 'training/customer-service'), tourismRecord('go2HR', 'go2hr'), tourismRecord('Team 2010 and the Ambassador Workshop', 'team-2010')]
  }
}
