// The history around each of the Province's one-off marks.
//
// A one-off is one mark, but the body or campaign it names seldom had only one. WorkBC was a
// wordmark beside the Best Place on Earth mark, then two flat marks of its own; BC Stats had a web
// logo in the flag years and has none of its own today. So each one-off sits on a timeline of the
// eras its body has had, oldest first, the way BC Hydro's three identities do — and an era whose
// mark the gallery does not hold is still on it, as a gap, not left out (QA_CASES 19: an
// uncatalogued logo is not "no logo").
//
// An era is one of four things:
//   held      — the gallery has its mark (`marks` names the one-offs, by id);
//   generator — the generator draws its mark, and `generator` is the patch that opens it there;
//   sought    — the body had a mark of its own then, which the gallery has not obtained;
//   none      — the body used the Province's or its ministry's marks, and had none of its own.
//
// Every date says what it rests on (the gallery's APPLICABILITY vocabulary) and cites where it came
// from. Most rest on the Wayback Machine: a capture shows a mark was in use on that day, not when it
// was adopted, so those are "first seen" and never promoted to adoption. Where a mark was archived
// but nobody has looked at it yet, the era says that too, rather than describing it from its
// filename. The research behind this is in research/identity/ (2026-09-26).

const wayback = (stamp, url) => `https://web.archive.org/web/${stamp}/${url}`

/** A source: what it is, where it is, and where in it the claim is. */
const source = (title, url, locator) => ({ title, url, ...(locator ? { locator } : {}) })

// ── Sources shared by more than one timeline ─────────────────────────────────────────────────────

const TYEE_2011 = source(
  'The Tyee, “What happened to the Best Place on Earth?”, 4 Oct 2011',
  'https://thetyee.ca/Mediacheck/2011/10/04/BC-Best-Place-On-Earth/',
  '“launched in 2005 and registered with [CIPO] the following year”; since March 2011 it has “slowly and quietly disappeared”'
)

const GLOBAL_2011 = source(
  'Global News (Postmedia), 7 Oct 2011',
  'https://globalnews.ca/news/163800/',
  'the slogan dropped “a few months ago”; “the logo of a rising sun and mountain … will live on”'
)

const WILDFIRE_NAMES = source(
  'Forest fire management in British Columbia (PMC8938580), note 2',
  'https://pmc.ncbi.nlm.nih.gov/articles/PMC8938580/',
  '“the Forest Protection Division (1912), then the Protection Branch (1978), then the Wildfire Management Branch (2010)”'
)

/** The oval ministry crest, shared by BC Timber Sales' plans of 2017–2022 and a Wildfire Service logo. */
const OVAL_CREST_NOTE = 'An oval ministry crest — British Columbia and Forests, Lands and Natural Resource ' +
  'Operations around an eagle, two conifers, a deer and a fish over water'

/** The tagline's years, which bound any mark that carries it. */
const TAGLINE_YEARS = 'The Best Place on Earth tagline was launched in 2005 and dropped from government use in 2011.'

// ── The timelines ────────────────────────────────────────────────────────────────────────────────

export const TIMELINES = {
  // The Province's own mark, which every one-off sets a name beside.
  'bc-mark': {
    label: 'The BC mark',
    eras: [
      {
        id: 'bc-mark-flag',
        status: 'generator',
        years: 'about 1983–2005',
        label: 'The flag logo',
        note: 'Before the sun mark, the Province’s logo was a stylised provincial flag beside “BC” — the ' +
          'generator’s Flag identity draws it.',
        generator: { era: 'flag' },
        applicability: {
          kind: 'estimated_era',
          years: 'about 1983–2005',
          note: 'The start is a flag historian’s “around 1983”; licence-plate sources give 1963 instead, so ' +
            'it is not settled. The end is the sun mark’s launch.'
        },
        sources: [
          source('Flags of the World, British Columbia (Dean McGee, 8 Oct 2007)', 'https://www.crwflags.com/fotw/flags/ca-bc.html',
            '“Around 1983, the British Columbia Government began using a stylized flag as its main logo”')
        ]
      },
      {
        id: 'bc-mark-best-place',
        status: 'held',
        marks: ['best-place-on-earth'],
        years: '2005–2011',
        label: 'The Best Place on Earth',
        note: 'The sun rising behind mountains over the sea, “British Columbia” in Garamond, a gold keyline, ' +
          'and the slogan beneath it.',
        applicability: { kind: 'documented_adoption', years: '2005–2011', note: TAGLINE_YEARS },
        sources: [TYEE_2011, GLOBAL_2011]
      },
      {
        id: 'bc-mark-alone',
        status: 'generator',
        years: '2011–present',
        label: 'The mark without its slogan',
        note: 'The slogan went and the mark stayed. Its sun has since been drawn flat, and it is the mark ' +
          'every ministry mark is set beside today — the generator’s Current identity. When the sun went ' +
          'flat has not been found.',
        generator: { era: 'current' },
        applicability: {
          kind: 'documented_adoption',
          years: '2011–present',
          note: 'The slogan’s retirement is reported for 2011, with no month; nothing dates the flat sun.'
        },
        sources: [GLOBAL_2011]
      }
    ]
  },

  'work-bc': {
    label: 'WorkBC',
    eras: [
      {
        id: 'workbc-best-place',
        status: 'held',
        marks: ['work-bc'],
        years: '2007–2011',
        label: 'Beside the Best Place on Earth mark',
        note: 'WorkBC began as the Province’s labour-market action plan as well as a website. WorkBC.ca is ' +
          'first seen in April 2007, with the Best Place on Earth mark beside a WorkBC wordmark.',
        applicability: {
          kind: 'estimated_era',
          years: '2007–2011',
          note: `Bounded by WorkBC.ca’s first capture and by the tagline this mark carries. ${TAGLINE_YEARS}`
        },
        sources: [
          source('WorkBC.ca, 29 Apr 2007 (Wayback Machine)', wayback('20070429043407', 'http://workbc.ca/'),
            'the Best Place on Earth mark and a separate WorkBC wordmark'),
          source('B.C. news release, 11 Oct 2007', 'https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2007ECD0041-001278.htm',
            '“British Columbia’s WorkBC action plan”'),
          TYEE_2011
        ]
      },
      {
        id: 'workbc-flat-rule',
        status: 'sought',
        years: '2016–2018',
        label: 'The flat mark, with a gold rule',
        note: 'The BC mark with its sun drawn flat, a thin gold rule, then “Work” in blue and “BC” in gold — ' +
          'the same template as WelcomeBC’s header of the same year. The header between 2012 and 2016 ' +
          'was archived but has not been looked at.',
        applicability: {
          kind: 'first_observation',
          years: '2016–2018',
          note: 'Its header file is first captured in January 2016 and replaced by July 2018.'
        },
        seenAt: [wayback('20160125130340', 'https://www.workbc.ca/images/workbc-header-logo.svg')],
        sources: [
          source('WorkBC.ca header logo, 25 Jan 2016 (Wayback Machine)', wayback('20160125130340', 'https://www.workbc.ca/images/workbc-header-logo.svg'))
        ]
      },
      {
        id: 'workbc-grey-rule',
        status: 'sought',
        years: '2018–present',
        label: 'The flat mark, with a grey rule',
        note: 'The flat sun at the left, a grey upright rule, and “Work” in blue with “BC” in gold, in the ' +
          'screen colours #234075 and #e3a82b. The file served today is the one first captured in July ' +
          '2018; it carried over into the 2023 redesign of WorkBC.ca unchanged.',
        applicability: {
          kind: 'first_observation',
          years: '2018–present',
          note: 'First captured 18 July 2018; the file live today is byte for byte the same.'
        },
        seenAt: ['https://www.workbc.ca/themes/custom/workbc/logo.svg'],
        sources: [
          source('WorkBC.ca logo, as served today', 'https://www.workbc.ca/themes/custom/workbc/logo.svg',
            'identical to the capture of 18 Jul 2018'),
          source('B.C. news release, 8 Feb 2023', 'https://news.gov.bc.ca/releases/2023PSFS0005-000146',
            '“a newly redesigned WorkBC.ca”')
        ]
      }
    ]
  },

  'welcome-bc': {
    label: 'WelcomeBC',
    eras: [
      {
        id: 'welcomebc-2008',
        status: 'sought',
        years: '2008–2009',
        label: '“Welcome to British Columbia”',
        note: 'WelcomeBC was announced on 13 June 2007 as the umbrella for the Province’s settlement ' +
          'programs. Its first site carried a logo titled “Welcome to British Columbia”, which the Wayback ' +
          'Machine did not keep.',
        applicability: {
          kind: 'first_observation',
          years: '2008–2009',
          note: 'The program’s announcement is documented; the logo is known only from its first site, ' +
            'first captured in April 2008.'
        },
        sources: [
          source('B.C. news release, 23 Jun 2008', 'https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2008AG0030-000974.htm',
            '“announced WelcomeBC … on June 13, 2007”'),
          source('WelcomeBC.ca, 12 Apr 2008 (Wayback Machine)', wayback('20080412015022', 'http://www.welcomebc.ca/en/index.html'))
        ]
      },
      {
        id: 'welcomebc-shaded',
        status: 'held',
        marks: ['welcome-bc'],
        years: 'before 2016',
        label: 'Beside the shaded sun',
        note: 'The mark here: the BC mark with its shaded sun, and “WelcomeBC” beside it in large Garamond. ' +
          'The site’s logos of 2010 and 2013 were archived but have not been looked at, so which years it ' +
          'is from is not settled.',
        applicability: {
          kind: 'estimated_era',
          years: 'before 2016',
          note: 'Its shaded sun puts it before the flat header WelcomeBC.ca had by March 2016.'
        },
        seenAt: [
          wayback('20100212214518', 'http://www.welcomebc.ca/shared/images/logo_welcomeBC.gif'),
          wayback('20130524172318', 'http://www.welcomebc.ca/images/logo-png.aspx')
        ],
        sources: [
          source('WelcomeBC.ca, 7 Jun 2010 (Wayback Machine)', wayback('20100607101227', 'http://www.welcomebc.ca/en/index.html'))
        ]
      },
      {
        id: 'welcomebc-flat-rule',
        status: 'sought',
        years: '2016–2025',
        label: 'The flat mark, with a gold rule',
        note: 'The BC mark with its sun drawn flat, a thin gold rule, then “Welcome” in blue and “BC” in ' +
          'gold — the same template as WorkBC’s header of the same year.',
        applicability: {
          kind: 'first_observation',
          years: '2016–2025',
          note: 'On the site from March 2016; last seen on 7 September 2025.'
        },
        seenAt: [wayback('20160413214302', 'http://www.welcomebc.ca/images/welcomebc-header-logo.svg')],
        sources: [
          source('WelcomeBC.ca header logo, 13 Apr 2016 (Wayback Machine)', wayback('20160413214302', 'http://www.welcomebc.ca/images/welcomebc-header-logo.svg'))
        ]
      },
      {
        id: 'welcomebc-2025',
        status: 'sought',
        years: '2025–present',
        label: 'Stacked, with the program named',
        note: 'Since the site’s redesign in September 2025: the flat BC mark and “WelcomeBC” stacked, with a ' +
          'gold rule, in BC blue and gold.',
        applicability: {
          kind: 'first_observation',
          years: '2025–present',
          note: 'First seen on 12 September 2025, five days after the last capture of the mark before it.'
        },
        seenAt: ['https://www.welcomebc.ca/getmedia/ce0988e3-03e0-4fed-a743-8ace3a34d1ce/WelcomeBC_cmyk_pos_Print.svg'],
        sources: [
          source('WelcomeBC.ca logo, as served today', 'https://www.welcomebc.ca/getmedia/ce0988e3-03e0-4fed-a743-8ace3a34d1ce/WelcomeBC_cmyk_pos_Print.svg')
        ]
      }
    ]
  },

  'bc-stats': {
    label: 'BC Stats',
    eras: [
      {
        id: 'bcstats-1996',
        status: 'sought',
        years: '1996–1998',
        label: 'Its first web logo',
        note: 'BC Stats, “the statistical agency of the Province of British Columbia”, had a site of its own ' +
          'by 1996, headed by an image titled “BC STATS logo”. Its filename suggests the flag identity; ' +
          'nobody has looked at it yet.',
        applicability: { kind: 'first_observation', years: '1996–1998', note: 'Seen on the site from October 1996 to January 1998.' },
        seenAt: [wayback('19961228003016', 'http://www.bcstats.gov.bc.ca/pics/flagcol2.gif')],
        sources: [source('BCStats.gov.bc.ca, 20 Oct 1996 (Wayback Machine)', wayback('19961020180542', 'http://www.bcstats.gov.bc.ca/'))]
      },
      {
        id: 'bcstats-ministry',
        status: 'none',
        years: '2000–2003',
        label: 'Under the ministry’s banner',
        note: 'The site took the Ministry of Finance’s banner, in the Province’s web template of the time, ' +
          'with no mark of BC Stats’ own.',
        applicability: { kind: 'first_observation', years: '2000–2003', note: 'Seen on the site from February 2000 to November 2003.' },
        sources: [source('BCStats.gov.bc.ca, 16 Aug 2000 (Wayback Machine)', wayback('20000816001837', 'http://www.bcstats.gov.bc.ca/'))]
      },
      {
        id: 'bcstats-2004',
        status: 'sought',
        years: '2004–2006',
        label: 'Beside the government crest',
        note: 'The government’s crest in the header, beside a BC Stats logo that was archived but has not ' +
          'been looked at.',
        applicability: { kind: 'first_observation', years: '2004–2006', note: 'Seen on the site from April 2004 to January 2006.' },
        seenAt: [wayback('20041205214534', 'http://www.bcstats.gov.bc.ca/images/bcstats_logo.gif')],
        sources: [source('BCStats.gov.bc.ca, 5 Dec 2004 (Wayback Machine)', wayback('20041205214534', 'http://www.bcstats.gov.bc.ca/'))]
      },
      {
        id: 'bcstats-shaded',
        status: 'held',
        marks: ['bc-stats'],
        years: '2007–2012',
        label: 'Beside the shaded sun',
        note: 'The mark here — “BC” in gold running into “Stats” — is most likely the one in the site’s ' +
          'header of these years, a single image linking to the government on its left and to BC Stats on ' +
          'its right. That header has not been compared with this mark.',
        applicability: {
          kind: 'estimated_era',
          years: '2007–2012',
          note: 'The header is first captured in September 2007 and on the site until January 2012.'
        },
        seenAt: [wayback('20070925235643', 'http://www.bcstats.gov.bc.ca/images/bcstats_logo.jpg')],
        sources: [source('BCStats.gov.bc.ca, 14 Jan 2010 (Wayback Machine)', wayback('20100114111109', 'http://www.bcstats.gov.bc.ca/'))]
      },
      {
        id: 'bcstats-2012',
        status: 'sought',
        years: '2012–2017',
        label: 'The last site of its own',
        note: 'A new site with a new logo, archived but not yet looked at.',
        applicability: { kind: 'first_observation', years: '2012–2017', note: 'Seen from February 2012 to January 2017.' },
        seenAt: [wayback('20120319163902', 'http://www.bcstats.gov.bc.ca/Libraries/Website_Pictures/BCStats.sflb.ashx')],
        sources: [source('BCStats.gov.bc.ca, 24 Feb 2012 (Wayback Machine)', wayback('20120224195540', 'http://www.bcstats.gov.bc.ca/Home.aspx'))]
      },
      {
        id: 'bcstats-gov',
        status: 'none',
        years: '2017–present',
        label: 'On gov.bc.ca',
        note: 'Its site now redirects into gov.bc.ca, under the government’s own header. Whether its ' +
          'publications carry a mark of their own has not been checked.',
        applicability: { kind: 'first_observation', years: '2017–present', note: 'Redirected by April 2017.' },
        sources: [source('BC Stats on gov.bc.ca', 'https://www2.gov.bc.ca/gov/content/data/about-data-management/bc-stats')]
      }
    ]
  },

  'environmental-reporting-bc': {
    label: 'Environmental Reporting BC',
    eras: [
      {
        id: 'erbc-soe',
        status: 'none',
        years: '1993–2012',
        label: 'State of Environment reporting',
        note: 'Before the program had a name, the Province published five State of Environment reports, ' +
          'from 1993 to 2007, under its ministries’ and the government’s marks.',
        applicability: { kind: 'documented_adoption', years: '1993–2012', note: 'The reports’ years are the Province’s own account of them.' },
        sources: [
          source('Environmental Reporting BC, previous reports', 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/reporting/environmental-reporting-bc/previous-reports-indicators',
            '“five State of Environment Reports for B.C. from 1993 to 2007”')
        ]
      },
      {
        id: 'erbc-shaded',
        status: 'held',
        marks: ['environmental-reporting-bc'],
        years: '2012–2016',
        label: 'Beside the shaded sun',
        note: 'The program launched in 2012. Its lockup with the shaded-sun BC mark is in the Province’s own ' +
          'report templates of 2015 and 2016, which fits the mark here.',
        applicability: {
          kind: 'estimated_era',
          years: '2012–2016',
          note: 'The launch year is documented; the mark is dated only by its templates, and the templates ' +
            'have not been compared with it.'
        },
        seenAt: ['https://github.com/bcgov/envreportutils.internal'],
        sources: [
          source('Environmental Reporting BC, previous reports', 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/reporting/environmental-reporting-bc/previous-reports-indicators',
            '“Environmental Reporting BC was launched in 2012”'),
          source('bcgov/envreportutils.internal (GitHub)', 'https://github.com/bcgov/envreportutils.internal',
            'report-template logos committed 2015–2016')
        ]
      },
      {
        id: 'erbc-gov',
        status: 'none',
        years: '2016–present',
        label: 'On gov.bc.ca',
        note: 'Its pages moved into gov.bc.ca and carry only the government’s header. Whether its reports ' +
          'still carry the program’s own mark has not been checked.',
        applicability: { kind: 'first_observation', years: '2016–present', note: 'Redirected into gov.bc.ca by August 2016.' },
        sources: [source('Environmental Reporting BC on gov.bc.ca', 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/reporting/environmental-reporting-bc')]
      }
    ]
  },

  'public-service': {
    label: 'BC Public Service',
    eras: [
      {
        id: 'wiw-2007',
        status: 'held',
        marks: ['public-service'],
        years: 'from 2007',
        label: '“Where ideas work”, beside the shaded sun',
        note: 'The BC Public Service’s employer brand, launched in 2007: “BC Public Service” under the mark ' +
          'and the slogan beside it.',
        applicability: {
          kind: 'documented_adoption',
          years: 'from 2007',
          note: 'The brand’s launch year is the Public Service’s own; when this lockup gave way to the next ' +
            'is not recorded.'
        },
        sources: [
          source('Where Ideas Work, corporate plan (2016), p. 6', wayback('20170206230813', 'http://www2.gov.bc.ca/assets/gov/careers/forms-tools/all-employees/corporate_plan_where_ideas_work.pdf'),
            '“Where Ideas Work brand launched”, under 2007')
        ]
      },
      {
        id: 'wiw-later',
        status: 'sought',
        years: 'by 2017–present',
        label: 'The later “Where ideas work” logo',
        note: 'The brand is still in use — its 2023 corporate plan carries the name — under a logo of its ' +
          'own on the Public Service’s career pages, archived but not yet looked at.',
        applicability: { kind: 'first_observation', years: 'by 2017–present', note: 'Its logo files are first seen in 2017 and 2018.' },
        seenAt: ['https://whereideaswork.gov.bc.ca/wp-content/uploads/2018/03/wiw-pos-rgb.png'],
        sources: [
          source('Where Ideas Work', 'https://whereideaswork.gov.bc.ca/', 'the logo file, uploaded March 2018, still served')
        ]
      }
    ]
  },

  'pacific-gateway': {
    label: 'Canada’s Pacific Gateway',
    eras: [
      {
        id: 'gateway-2008',
        status: 'held',
        marks: ['pacific-gateway'],
        years: '2008–2011',
        label: 'Canada’s Pacific Gateway',
        note: 'The Province’s international brand under Premier Campbell, with a site of its own launched ' +
          'in September 2008.',
        applicability: {
          kind: 'first_observation',
          years: '2008–2011',
          note: 'Its banner is first seen on gov.bc.ca in April 2008, and its site redirected elsewhere by ' +
            'August 2011. No source ties this lockup with the BC mark to a date of its own.'
        },
        sources: [
          source('B.C. news release, 1 Apr 2009', 'https://archive.news.gov.bc.ca/releases/news_releases_2005-2009/2009STED0020-000614.htm',
            '“CanadasPacificGateway.ca … was launched in September 2008”'),
          GLOBAL_2011
        ]
      },
      {
        id: 'gateway-starts-here',
        status: 'sought',
        years: 'from 2011',
        label: '“Canada Starts Here”',
        note: 'Premier Clark’s government replaced the brand with “Canada Starts Here”, revealed at Prince ' +
          'Rupert on 20 September 2011 — a logo of stacked shipping containers.',
        applicability: { kind: 'documented_adoption', years: 'from 2011', note: 'Its reveal is reported to the day.' },
        sources: [TYEE_2011, GLOBAL_2011]
      }
    ]
  },

  'stronger-bc': {
    label: 'StrongerBC',
    eras: [
      {
        id: 'strongerbc-2020',
        status: 'held',
        marks: ['stronger-bc'],
        years: '2020–2022',
        label: 'StrongerBC for everyone',
        note: 'The name of the Province’s economic recovery plan of September 2020. Its guidelines of ' +
          'January 2021 give the “StrongerBC for everyone” word mark, set with the BC mark or on its own, for ' +
          'government use.',
        applicability: {
          kind: 'documented_adoption',
          years: '2020–2022',
          note: 'The plan’s release is documented to the day; the word mark to its guidelines’ month.'
        },
        sources: [
          source('B.C. news release, 17 Sep 2020', 'https://news.gov.bc.ca/releases/2020PREM0052-001780',
            '“StrongerBC for everyone: BC’s Economic Recovery Plan”'),
          source('Use of the StrongerBC marks (Jan 2021)', 'https://www2.gov.bc.ca/assets/gov/british-columbians-our-governments/services-policies-for-government/policies-procedures-standards/corporate-identity-assets/visid-pdfs/bcid_use_of_strongerbc.pdf', 'pp. 1–2')
        ]
      },
      {
        id: 'strongerbc-2022',
        status: 'sought',
        years: '2022–present',
        label: 'StrongerBC, the core brand',
        note: 'With the StrongerBC Economic Plan of February 2022 the name became “a core brand of the ' +
          'Government of B.C.”, with guidelines and a brand package of its own by 2023, and an endorsed ' +
          'mark and a wordmark issued in 2024.',
        applicability: {
          kind: 'documented_adoption',
          years: '2022–present',
          note: 'The plan and the brand matrix are dated; the 2024 files are dated by their downloads.'
        },
        sources: [
          source('B.C. news release, 17 Feb 2022', 'https://news.gov.bc.ca/releases/2022JERI0004-000230'),
          source('Download the BC marks', 'https://www2.gov.bc.ca/gov/content/governments/services-for-government/policies-procedures/bc-visual-identity/download-marks',
            'StrongerBC endorsed mark and wordmark')
        ]
      }
    ]
  },

  'bc-wildfire-service': {
    label: 'BC Wildfire Service',
    eras: [
      {
        id: 'bcws-protection-branch',
        status: 'none',
        years: '1978–2010',
        label: 'The Protection Branch',
        note: 'The Forest Service’s fire division, from 1912, became the Protection Branch in 1978. Its site ' +
          'of 2007 to 2010 carried a photographic banner with the branch’s name beside the Province’s own ' +
          'mark, and no mark of its own.',
        applicability: {
          kind: 'documented_adoption',
          years: '1978–2010',
          note: 'The names’ years are from a published history of the service; the banner is seen from 2007.'
        },
        seenAt: [wayback('20070606083658im_', 'http://bcwildfire.ca/images/portal/FOR_FPB_long_banner.gif')],
        sources: [WILDFIRE_NAMES, source('bcwildfire.ca, 6 Jun 2007 (Wayback Machine)', wayback('20070606083658', 'http://bcwildfire.ca/'))]
      },
      {
        id: 'bcws-wildfire-management-branch',
        status: 'none',
        years: '2010–2015',
        label: 'The Wildfire Management Branch',
        note: 'Renamed in 2010, the branch went under the Province’s Best Place on Earth mark and its ' +
          'ministry’s name — on its site and on its guides.',
        applicability: {
          kind: 'first_observation',
          years: '2010–2015',
          note: 'The name’s start is from the service’s history; its last byline on a news release is 26 June 2015.'
        },
        sources: [
          WILDFIRE_NAMES,
          source('bcwildfire.ca, 10 Jan 2013 (Wayback Machine)', wayback('20130110113346', 'http://bcwildfire.ca/')),
          source('B.C. news release, 26 Jun 2015', 'https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2015FLNR0142-000961.htm',
            'the last byline reading “Wildfire Management Branch”')
        ]
      },
      {
        id: 'bcws-oval-crest',
        status: 'sought',
        years: 'from 2015',
        label: 'The oval crest, “Wildfire Service”',
        note: `The name BC Wildfire Service appears at the end of June 2015. ${OVAL_CREST_NOTE}, with a ` +
          '“Wildfire Service” scroll beneath — was published as its logo in 2021. The ministry it names ' +
          'suggests it is older, which is not established.',
        applicability: {
          kind: 'first_observation',
          years: 'from 2015',
          note: 'The name is first seen on a news release of 30 June 2015; the crest is seen as the service’s ' +
            'logo in June 2021.'
        },
        seenAt: ['https://s3.amazonaws.com/wpe-e-know.ca/eknow/wp-content/uploads/2021/06/BC-Wildfire-Service-logo.jpg'],
        sources: [
          source('B.C. news release, 30 Jun 2015', 'https://archive.news.gov.bc.ca/releases/news_releases_2013-2017/2015FLNR0152-000994.htm',
            'the first byline reading “BC Wildfire Service”'),
          source('e-know.ca, “BC Wildfire Service logo” (June 2021)', 'https://www.e-know.ca/regions/east-kootenay/wildfire-reported-southwest-of-canal-flats/attachment/bc-wildfire-service-logo/')
        ]
      },
      {
        id: 'bcws-bc-mark',
        status: 'held',
        marks: ['bc-wildfire-service', 'bc-wildfire-service-one-line'],
        years: 'by 2023–present',
        label: 'Beside the BC mark',
        note: 'The flat-sun BC mark with a gold divider and the name in Garamond, “BC” in gold — on two lines ' +
          'or on one. Both are on the wildfire situation site, and on the service’s reports and guides ' +
          'since.',
        applicability: {
          kind: 'first_observation',
          years: 'by 2023–present',
          note: 'The two-line file is first captured in May 2023 and the one-line in August 2024; it may be older.'
        },
        seenAt: [
          'https://wildfiresituation.nrs.gov.bc.ca/assets/images/logo/bcwfservice-logo.png',
          'https://wildfiresituation.nrs.gov.bc.ca/assets/images/logo/bc-wildfire-service-logo-transparent.png'
        ],
        sources: [
          source('Wildfire situation site, logo files', 'https://wildfiresituation.nrs.gov.bc.ca/assets/images/logo/bcwfservice-logo.png',
            'first captured 1 May 2023'),
          source('Cultural and Prescribed Fire annual summary report, 2025', 'https://www2.gov.bc.ca/assets/gov/public-safety-and-emergency-services/wildfire-status/prescribed-burning/annual_summary_report_crx_fire_2025.pdf', 'cover')
        ]
      }
    ]
  },

  'environmental-lab-bc': {
    label: 'Environmental Lab BC',
    eras: [
      {
        id: 'envlab-analytical',
        status: 'none',
        years: 'to 2024',
        label: 'The Analytical Laboratory',
        note: 'The Province’s environmental laboratory, in operation for over thirty years, went by ' +
          '“Analytical Laboratory” and used its ministry’s mark, with none of its own.',
        applicability: {
          kind: 'first_observation',
          years: 'to 2024',
          note: 'Seen under that name from 2017 to 2023; “Environmental Laboratory” by July 2024.'
        },
        sources: [
          source('Analytical Laboratory, gov.bc.ca, 6 Feb 2017 (Wayback Machine)', wayback('20170206232212', 'http://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/research/analytical-lab')),
          source('Analytical Laboratory, gov.bc.ca, 24 Jul 2024 (Wayback Machine)', wayback('20240724065058', 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/research/analytical-lab'))
        ]
      },
      {
        id: 'envlab-mark',
        status: 'held',
        marks: ['environmental-lab-bc'],
        years: 'by 2025–present',
        label: 'Environmental Lab BC',
        note: 'Renamed B.C. Environmental Laboratory, with a mark of its own: the flat-sun BC mark, a gold ' +
          'divider, and “Environmental Lab BC” in Garamond. The file the gallery has is the same export as ' +
          'the one on the lab’s page.',
        applicability: {
          kind: 'first_observation',
          years: 'by 2025–present',
          note: 'The mark’s file is first captured on 17 April 2025.'
        },
        seenAt: ['https://www2.gov.bc.ca/assets/gov/environment/research-monitoring-and-reporting/research/analytical-labratory/images/bc-env-lab-logo.svg'],
        sources: [
          source('B.C. Environmental Laboratory, gov.bc.ca', 'https://www2.gov.bc.ca/gov/content/environment/research-monitoring-reporting/research/bc-environmental-lab',
            '“has been in operation for over 30 years”')
        ]
      }
    ]
  }
}

/** Which timeline each one-off sits on: its own, or its body's where two marks share one. */
const TIMELINE_OF = {
  'best-place-on-earth': 'bc-mark',
  'work-bc': 'work-bc',
  'welcome-bc': 'welcome-bc',
  'bc-stats': 'bc-stats',
  'environmental-reporting-bc': 'environmental-reporting-bc',
  'public-service': 'public-service',
  'pacific-gateway': 'pacific-gateway',
  'stronger-bc': 'stronger-bc',
  'bc-wildfire-service': 'bc-wildfire-service',
  'bc-wildfire-service-one-line': 'bc-wildfire-service',
  'environmental-lab-bc': 'environmental-lab-bc'
}

export const timelineKeyOf = (entryId) => TIMELINE_OF[entryId]

// ── Eras for the bodies with collections of their own ───────────────────────────────────────────

// ICBC's and BCLC's sources, from the research packages in research/identity/icbc and
// research/identity/bclc (27 September 2026), whose source ids are kept in each title.

const cipo = (number) => `https://ised-isde.canada.ca/cipo/trademark-search/${number}`
const cipoImage = (number) => `https://ised-isde.canada.ca/cipo/trademark-search/media/${number}.png`

const ICBC_SOURCES = {
  S1: source('ICBC Service Plan 2014–2016 [S1]', 'https://www.bcbudget.gov.bc.ca/2014/sp/pdf/agency/icbc.pdf',
    'printed page 3: the corporation was established in 1973'),
  S2: source('CIPO official mark 0903609 [S2]', cipo('903609'), 'filed 12 January 1989, advertised 17 May 1989'),
  S3: source('CIPO 1326195, ICBC & Design [S3]', cipo('1326195'),
    'square-corner sans badge; filed 29 November 2006; insurance use claimed since at least March 1992'),
  S4: source('CIPO 1379948, ICBC & Design (rounded corners) [S4]', cipo('1379948'),
    '“three rounded corners”; filed 21 January 2008'),
  S5: source('CIPO 1561227, ICBC & Design (colour) [S5]', cipo('1561227'),
    'white lettering and road on blue; filed 2012, use claimed since at least January 2008'),
  S6: source('ICBC Annual Service Plan Report 2025/26 [S6]', 'https://www.icbc.com/assets/en/5zp5LxLIznBZi8nODF4yQt/ar-26.pdf',
    'cover, dated August 2026'),
  S9: source('icbc.com [S9]', 'https://icbc.com/', 'header, observed 27 September 2026'),
  S10: source('CIPO 0374886, ICBC & Design [S10]', cipo('374886'),
    'use claimed from 1 March 1974; filed 6 May 1974; registration cancelled 20 June 2023'),
  S11: source('ICBC 1992 annual report, scanned by McGill University [S11]', 'https://digital.library.mcgill.ca/images/hrcorpreports/pdfs/6/634113.pdf',
    'back cover, PDF page 28; print code “PI 151 (2 93)”'),
  S12: source('ICBC 2007–2009 Service Plan [S12]', 'https://www.bcbudget.gov.bc.ca/2007/sp/pdf/agency/icbc.pdf', 'cover, January 2007'),
  S13: source('ICBC 2008–2010 Service Plan [S13]', 'https://www.bcbudget.gov.bc.ca/2008/sp/pdf/agency/icbc.pdf', 'cover, January 2008'),
  S14: source('ICBC 2009–2011 Service Plan [S14]', 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/icbc.pdf', 'cover, January 2009')
}

const BCLC_SOURCES = {
  S1: source('BCLC 2006/07 Annual Report [1]', 'https://corporate.bclc.com/content/dam/bclccorporate/reports/annual-reports/2007/bclc-annual-report-0607.pdf', 'cover'),
  S2: source('BCLC Service Plan 2008/09–2010/11 [2]', 'https://www.bcbudget.gov.bc.ca/2008/sp/pdf/agency/bclc.pdf', 'cover, early 2008'),
  S3: source('Canadian Press, “B.C. Lottery rebrands as BCLC”, Marketing, 13 Aug 2008 [3]', 'https://marketingmag.ca/brands/b-c-lottery-rebrands-as-bclc-17155/',
    'the lowercase acronym, dots inside the b and both c’s, and the tagline “playing it right”'),
  S4: source('BCLC Service Plan 2009/10–2011/12 [4]', 'https://www.bcbudget.gov.bc.ca/2009/sp/pdf/agency/bclc.pdf', 'cover'),
  S6: source('BCLC Environmental, Social and Governance Report 2022 [6]', 'https://corporate.bclc.com/content/dam/bclccorporate/reports/corporate-citizenship/2022/environmental-social-and-governance-report-2022.pdf', 'cover'),
  S7: source('BCLC Design System: Colour [7]', 'https://corporate.bclc.com/documentation/design-system/styles/colour.html',
    'grey #414B56, red #9B1831, orange #E86A10, green #7DBC13; undated'),
  S8: source('BCLC 2025/26 Prince George Community Impact Report [8]', 'https://corporate.bclc.com/content/dam/bclccorporate/reports/community-impact-reports/2026/community-impact-report-2025-26-prince-george.pdf', 'page 1'),
  S9: source('BCLC 2008 Carbon Neutral Action Report [9]', 'https://www2.gov.bc.ca/assets/gov/environment/climate-change/cnar/2008/cc/bc_lottery_corporation.pdf',
    'page 4, 30 June 2009: new supplies replaced the old only as stock ran out')
}

// BC Ferries' sources, from the research package in research/identity/bc-ferries (27 September 2026).

const BCF_SOURCES = {
  S1: source('B.C. news release, “New BC Ferry Company to Improve Services”, 2 Apr 2003 [S1]',
    'https://archive.news.gov.bc.ca/releases/archive/2001-2005/2003tran0017-000313.htm',
    'the dogwood retired after 43 years; the outgoing logo unchanged for 25; the wave introduced, and phased in over the following year'),
  S2: source('British Columbia Toll Authority Ferry System, 1963 season brochure, via ExploreNorth [S2]',
    'https://explorenorth.com/bc/bc_ferries-1963.html', 'cover: a black-outlined dogwood on a green flag'),
  S3: source('BC Ferries, Investor Overview, September 2026 [S3]', 'https://www.bcferries.com/web_image/h7f/h2d/9106869944350.pdf', 'cover')
}

// WorkSafeBC's sources, from the research package in research/identity/worksafebc (27 September 2026).

const WCB_SOURCES = {
  S1: source('WorkSafeBC, “Our story: 1917–1941” [S1]', 'https://www.worksafebc.com/en/about-us/who-we-are/our-story/1917-1941',
    'founded on 1 January 1917 as the Workmen’s Compensation Board'),
  S2: source('WorkSafeBC, “Our story: 1967–1991” [S2]', 'https://www.worksafebc.com/en/about-us/who-we-are/our-story/1967-1991',
    'a worker-protection logo in 1968; provincial imagery added in 1983; “Workmen’s” became “Workers’” in 1974'),
  S3: source('WorkSafeBC, “Our story: 1992–2016” [S3]', 'https://www.worksafebc.com/en/about-us/who-we-are/our-story/1992-2016',
    'WorkSafeBC adopted as the operating name in 2005; the legal name is kept'),
  S4: source('WorkSafeBC clearance service, logo image [S4]', 'https://asmtclr.online.worksafebc.com/Mobile/css/images/WorkSafeBC-logo.png',
    'observed 27 September 2026'),
  S5: source('Freebie Supply, Worker’s Compensation Board logo [S5]', 'https://freebiesupply.com/logos/workers-compensation-board-logo/',
    'an undated specimen'),
  S6: source('Seeklogo, Worker’s Compensation Board logo no. 153800 [S6]', 'https://seeklogo.com/vector-logo/153800/workers-compensation-board',
    'an undated specimen')
}

/**
 * BC Parks' eras around its flag-era badge, BC Timber Sales' around its two marks, and ICBC's,
 * BCLC's, BC Ferries' and WorkSafeBC's. These are collections, not one-offs, so collections.js puts their marks into the held
 * eras itself; what is here is everything else an era says.
 */
export const COLLECTION_ERAS = {
  'bc-parks': [
    {
      id: 'parks-badge',
      status: 'held',
      years: 'by 2002',
      label: 'The flag badge',
      note: 'The flag symbol in a rounded frame, with “BC” and “Parks” set alike — on the Province’s park ' +
        'brochures beside the park’s name, with the arms and the ministry at the foot. Its sites of the ' +
        'time used plain type rather than the badge.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2002',
        note: 'Seen on brochures printed in 2002. Its start in the flag years of the 1980s is inferred from ' +
          'the identity it belongs to, not found; BC Archives’ BC Parks master files, which hold its ' +
          'logos and badges, are where to date it.'
      },
      sources: [
        source('Alice Lake Provincial Park brochure (03/2002)', wayback('20030625043855', 'http://wlapwww.gov.bc.ca:80/bcparks/explore/parkpgs/alice_lk/alicelk_brochure.pdf'), 'cover'),
        source('BC Archives, GR-3888, BC Parks in-house materials master files', 'https://search-bcarchives.royalbcmuseum.bc.ca/bc-parks-in-house-materials-master-files',
          '“logos, badges, stickers”, 1937–2008')
      ]
    },
    {
      id: 'parks-shaded-banner',
      status: 'sought',
      years: '2005–2007',
      label: '“BCParks” beside the shaded sun',
      note: 'The shaded sun and mountains, then “BCParks” set solid in white serif, on the ministry’s web ' +
        'banner — without the Best Place on Earth line.',
      applicability: { kind: 'first_observation', years: '2005–2007', note: 'Seen on its site from November 2005 to February 2007.' },
      seenAt: [wayback('20070208041812im_', 'http://www.env.gov.bc.ca/bcparks/images/images_ban/bn_enviro_esd_2005.jpg')],
      sources: [source('BC Parks, 10 Nov 2005 (Wayback Machine)', wayback('20051110020339', 'http://wlapwww.gov.bc.ca/bcparks/index.htm'))]
    },
    {
      id: 'parks-best-place',
      status: 'sought',
      years: '2010–2016',
      label: 'Beside the Best Place on Earth mark',
      note: 'The shaded-sun BC mark with its tagline, a thin gold rule, and “BCParks” in dark blue serif — ' +
        'the arrangement of WorkBC’s and WelcomeBC’s marks.',
      applicability: {
        kind: 'first_observation',
        years: '2010–2016',
        note: 'Seen on its site from January 2010 to 22 November 2016, a mark that outlived the tagline’s ' +
          'retirement from government use in 2011.'
      },
      seenAt: [wayback('20100108165242im_', 'http://www.env.gov.bc.ca/bcparks/_bcparks_templates/images/logo-bcparks.gif')],
      sources: [source('BC Parks, 8 Jan 2010 (Wayback Machine)', wayback('20100108165242', 'http://www.env.gov.bc.ca/bcparks/'))]
    },
    {
      id: 'parks-flat-text',
      status: 'none',
      years: '2016–2023',
      label: 'The flat BC mark, and its name in type',
      note: 'The Province’s flat-sun mark reversed in white, with “BC Parks” as a separate line of type ' +
        'beside it rather than a lockup of its own.',
      applicability: {
        kind: 'first_observation',
        years: '2016–2023',
        note: 'Its site changed between 22 November and 2 December 2016, and again at the start of 2023.'
      },
      sources: [source('BC Parks, 2 Dec 2016 (Wayback Machine)', wayback('20161202140303', 'http://www.env.gov.bc.ca/bcparks/'))]
    },
    {
      id: 'parks-current',
      status: 'sought',
      years: '2023–present',
      label: 'The BC Parks logo',
      note: 'One lockup: the flat sun and mountains with “British Columbia”, a gold upright bar, and “BC ' +
        'Parks” in serif, with a stacked version beside it. Its colours have shifted between versions of ' +
        'the file.',
      applicability: { kind: 'first_observation', years: '2023–present', note: 'On bcparks.ca from 2 February 2023; not there on 28 January.' },
      seenAt: [
        'https://bcparks.ca/static/BCParks_Primary_Reversed-cropped-0080416cb5f347c8e7c33f32739f17ca.svg',
        'https://bcparks.ca/static/BCParks_Primary_Reversed_Vertical-9873b7442479cf33ebc73121675114fa.svg'
      ],
      sources: [
        source('bcparks.ca, 2 Feb 2023 (Wayback Machine)', wayback('20230202082950', 'https://bcparks.ca/')),
        source('bcparks.ca', 'https://bcparks.ca/')
      ]
    }
  ],

  bcts: [
    {
      id: 'bcts-banner',
      status: 'none',
      years: '2003–2005',
      label: 'A banner, not a mark',
      note: 'BC Timber Sales was established on 20 June 2003. Its first site had its name in white type on ' +
        'a green banner, and no mark.',
      applicability: {
        kind: 'first_observation',
        years: '2003–2005',
        note: 'Its establishment is documented to the day; the banner is seen from May 2003 to February 2005.'
      },
      sources: [
        source('B.C. news release, 2013', 'https://news.gov.bc.ca/releases/2013FLNR0194-001483', '“established on June 20, 2003”'),
        source('BC Timber Sales, 11 May 2003 (Wayback Machine)', wayback('20030511171328', 'http://www.for.gov.bc.ca/bcts/'))
      ]
    },
    {
      id: 'bcts-earlier',
      status: 'held',
      years: '2005–2017',
      label: 'The wordmark on its own',
      note: '“BCTS” in green over “BC Timber Sales” in a slab serif, with no BC mark beside it. On its site ' +
        'it was paired with a round Forest Service tree badge.',
      applicability: {
        kind: 'first_observation',
        years: '2005–2017',
        note: 'On its site from May 2005 until the site moved into gov.bc.ca after November 2017.'
      },
      seenAt: [wayback('20070105182942im_', 'http://www.for.gov.bc.ca/bcts/images/bctslogo_right.gif')],
      sources: [
        source('BC Timber Sales, 12 May 2005 (Wayback Machine)', wayback('20050512075023', 'http://www.for.gov.bc.ca/bcts/')),
        source('BC Timber Sales, 23 Nov 2017 (Wayback Machine)', wayback('20171123201642', 'https://www.for.gov.bc.ca/bcts/'))
      ]
    },
    {
      id: 'bcts-oval-crest',
      status: 'sought',
      years: '2017–2022',
      label: 'Beside the oval crest',
      note: `${OVAL_CREST_NOTE} — then “BCTS” in a heavy green sans over “BC Timber Sales”: a sans redrawing ` +
        'of the wordmark, on the covers of its business plans.',
      applicability: {
        kind: 'first_observation',
        years: '2017–2022',
        note: 'On its plans for 2017/18 to 2021/22; the plan of 2016/17 carries only the Province’s mark.'
      },
      seenAt: ['https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bp-201718-201920.pdf'],
      sources: [
        source('BC Timber Sales business plan 2017/18–2019/20', 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bp-201718-201920.pdf', 'cover'),
        source('BC Timber Sales business plan 2021/22–2023/24', 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bcts-business-plan_2021-22-to-2023-24.pdf', 'cover')
      ]
    },
    {
      id: 'bcts-current',
      status: 'held',
      years: 'by 2023–present',
      label: 'Beside the BC mark',
      note: 'The initials over the name in a sans, beside the BC mark with a grey divider.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2023–present',
        note: 'On its business plan of August 2023 and its reports since.'
      },
      sources: [
        source('BC Timber Sales business plan 2023/24–2025/26', 'https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/bc-timber-sales/business-plans-performance-reports/bcts_business_plan_2023-2024_to_2025-2026_final.pdf', 'cover')
      ]
    }
  ],

  // ICBC's eras are the package's evidence groups, and like it they do not claim to be exclusive:
  // a filing, a use claimed in one and a dated cover answer different questions, and the early
  // arrangements may have overlapped. No adoption or retirement date is known for any of them.
  icbc: [
    {
      id: 'icbc-1974',
      status: 'held',
      years: '1974',
      label: 'The registry emblem',
      note: 'An early vertical emblem: a half-disc facing left in a tall frame, under a separate upper ' +
        'component of paired curved shapes. Known from the drawing in its trademark record, which is ' +
        'hatched for colour without saying which colours; it is drawn here as outlines for that reason.',
      applicability: {
        kind: 'first_observation',
        years: 'from 1974',
        note: 'Its trademark record claims use from 1 March 1974, and was filed on 6 May. The corporation ' +
          'was established in 1973, but no example from that year has been found. The record was cancelled ' +
          'in 2023, which says nothing about when the emblem stopped being used.'
      },
      seenAt: [cipoImage('374886')],
      sources: [ICBC_SOURCES.S10, ICBC_SOURCES.S1]
    },
    {
      id: 'icbc-half-disc',
      status: 'held',
      years: 'by 1989',
      label: 'The half-disc and the name',
      note: 'A solid half-disc beside “ICBC”, and beside the full name on three lines. The half-disc ' +
        'arrangement is in an official-mark record; the full name is known only from a picture supplied ' +
        'to the research, filed under 1989. How either relates to the 1974 emblem is not known.',
      applicability: {
        kind: 'first_observation',
        years: 'by 1989',
        note: 'The half-disc arrangement was filed as an official mark on 12 January 1989 and advertised on ' +
          '17 May. A filing is not a launch, and the full-name version is not dated by it.'
      },
      seenAt: [cipoImage('903609')],
      sources: [ICBC_SOURCES.S2]
    },
    {
      id: 'icbc-serif-road',
      status: 'held',
      years: 'about 1992',
      label: 'The road badge, in a serif',
      note: 'The square badge with a road curving through it, and “ICBC” reversed out in a narrow serif — ' +
        'the start of the road family every later mark belongs to.',
      applicability: {
        kind: 'first_observation',
        years: 'about 1992',
        note: 'On the back cover of the 1992 annual report, printed in February 1993 by its print code; a ' +
          'later record of the road badge claims use from March 1992. Together they date the road family, ' +
          'not this serif drawing.'
      },
      sources: [ICBC_SOURCES.S11, ICBC_SOURCES.S3]
    },
    {
      id: 'icbc-square-sans',
      status: 'held',
      years: 'by 2007–2008',
      label: 'The square badge, in a heavier sans',
      note: 'The same square-cornered badge, with “ICBC” in a heavy sans. The serif-to-sans change has not ' +
        'been dated, nor shown to have happened everywhere at once.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2007–2008',
        note: 'On the covers of the service plans of January 2007 and January 2008, and in a trademark ' +
          'filed in November 2006. The supplied file was filed under 2005, which nothing independent confirms.'
      },
      seenAt: [cipoImage('1326195')],
      sources: [ICBC_SOURCES.S12, ICBC_SOURCES.S13, ICBC_SOURCES.S3]
    },
    {
      id: 'icbc-rounded',
      status: 'held',
      years: '2008–present',
      label: 'The rounded badge',
      note: 'Three corners rounded, and the badge in blue with the lettering and road reversed out in ' +
        'white. The same drawing is on icbc.com today in orange, a colour variant rather than a new ' +
        'mark: why, and for how long, is not known.',
      applicability: {
        kind: 'estimated_era',
        years: '2008–present',
        note: 'A rollout in 2008 is inferred: the rounded drawing was filed on 21 January 2008, the blue ' +
          'version claims use from that month, and the service plan of January 2008 still has the square ' +
          'badge where January 2009’s has this one. It is on the report of August 2026.'
      },
      seenAt: [cipoImage('1379948'), cipoImage('1561227')],
      sources: [ICBC_SOURCES.S4, ICBC_SOURCES.S5, ICBC_SOURCES.S13, ICBC_SOURCES.S14, ICBC_SOURCES.S6, ICBC_SOURCES.S9]
    }
  ],

  bclc: [
    {
      id: 'bclc-legacy',
      status: 'held',
      years: 'by 2007–2008',
      label: 'The sun and waves',
      note: 'A sun rising over waves, beside “British Columbia Lottery Corporation” in a heavy italic. ' +
        'Only one colour of it has been supplied, so it is drawn in one ink; what colours it was printed ' +
        'in is not established.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2007–2008',
        note: 'On the 2006/07 annual report and the service plan of early 2008. BCLC has operated since ' +
          '1985, but that does not date this mark.'
      },
      sources: [BCLC_SOURCES.S1, BCLC_SOURCES.S2]
    },
    {
      id: 'bclc-2008',
      status: 'held',
      years: '2008–by 2022',
      label: 'Lowercase, in red, orange and green',
      note: 'The corporation’s initials in lowercase, with a dot of colour inside the b and each c, launched ' +
        'with the tagline “playing it right”. New stationery replaced the old only as stock ran out.',
      applicability: {
        kind: 'documented_adoption',
        years: '2008–by 2022',
        note: 'The new identity was reported on 13 August 2008, and is on the next year’s service plan. ' +
          'The older palette is still on a report of 2022, which is not an end date.'
      },
      sources: [BCLC_SOURCES.S3, BCLC_SOURCES.S4, BCLC_SOURCES.S9, BCLC_SOURCES.S6, BCLC_SOURCES.S7]
    },
    {
      id: 'bclc-contemporary',
      status: 'held',
      years: 'by 2025/26–present',
      label: 'Purple, coral and yellow',
      note: 'The same lowercase letters, darker, with the dots in purple, coral and yellow. When the colours ' +
        'changed has not been found; it is a new palette, not a new drawing.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2025/26',
        note: 'On page 1 of a community impact report for 2025/26. The report’s year is not a launch date.'
      },
      sources: [BCLC_SOURCES.S8]
    }
  ],

  // Two symbol families — the dogwood, then the wave — with the dogwood split where the package
  // splits it: a dated 1963 example, and the drawing the 2003 announcement retired.
  'bc-ferries': [
    {
      id: 'bcf-early-dogwood',
      status: 'held',
      years: '1960s',
      label: 'The early dogwood',
      note: 'A white dogwood with a yellow centre, its petals outlined in black, on a green waving flag — ' +
        'as the ferry system’s 1963 brochure draws it. One illustration does not say what every drawing of ' +
        'the time looked like.',
      applicability: {
        kind: 'first_observation',
        years: 'by 1963',
        note: 'On the cover of the 1963 season brochure. The dogwood itself goes back to 1960: the 2003 ' +
          'announcement retires it after 43 years.'
      },
      seenAt: ['https://explorenorth.com/bc/images/bc_ferries-1963a.jpg'],
      sources: [BCF_SOURCES.S2, BCF_SOURCES.S1]
    },
    {
      id: 'bcf-geometric-dogwood',
      status: 'held',
      years: 'about 1978–2003',
      label: 'The geometric dogwood',
      note: 'The flower redrawn in flat geometric petals, white on a green flag, beside “BC FERRIES” in a ' +
        'heavy squared capital. Retired with the dogwood on 2 April 2003.',
      applicability: {
        kind: 'estimated_era',
        years: 'about 1978–2003',
        note: 'The 2003 announcement says the outgoing logo had not changed in 25 years, which points to ' +
          'about 1978; no record of its introduction has been found, nor whether the flower and the lettering ' +
          'changed together. Its retirement is documented.'
      },
      sources: [BCF_SOURCES.S1]
    },
    {
      id: 'bcf-wave',
      status: 'held',
      years: '2003–present',
      label: 'The wave',
      note: 'A stylised wave running into “BCFerries” in a slanted sans, in blue — introduced with BC Ferry ' +
        'Services Inc., the company that took over from the Crown corporation, and phased onto the fleet ' +
        'over the following year.',
      applicability: {
        kind: 'documented_adoption',
        years: '2003–present',
        note: 'Announced on 2 April 2003, and on the cover of BC Ferries’ investor overview of September 2026.'
      },
      sources: [BCF_SOURCES.S1, BCF_SOURCES.S3]
    }
  ],

  // The board's own history dates two redesigns, 1968 and 1983; a name change (1974) and an
  // operating name (2005) are kept apart from them. What came before 1968 is not known, so no era
  // stands for it — the intro says so rather than a slot claiming a mark that may not have existed.
  worksafebc: [
    {
      id: 'wcb-1968',
      status: 'sought',
      years: '1968–1983',
      label: 'The worker-protection emblem',
      note: 'The board’s history describes a new design in 1968 built on protecting the worker. No ' +
        'picture of it has been found, so it is not drawn.',
      applicability: {
        kind: 'documented_adoption',
        years: '1968–1983',
        note: 'The board’s own history dates the design to 1968 and the next one to 1983; when this one ' +
          'actually went out of use, or whether the two overlapped, is not recorded.'
      },
      sources: [WCB_SOURCES.S2]
    },
    {
      id: 'wcb-1983',
      status: 'held',
      years: 'from 1983',
      label: 'The province and the worker',
      note: 'The outline of British Columbia with the coast’s islands, shaped into a hand sheltering a ' +
        'worker’s head, beside the Workers’ Compensation Board’s name — the board, renamed from ' +
        '“Workmen’s” in 1974, added the province to its mark in 1983.',
      applicability: {
        kind: 'documented_adoption',
        years: 'from 1983',
        note: 'The board’s history dates the redesign to 1983. The lockup drawn here comes from undated ' +
          'specimens and belongs to it by likeness, not by a dated example; when it was retired is not known, ' +
          'and 2005 is not taken as its end.'
      },
      seenAt: ['https://seeklogo.com/vector-logo/153800/workers-compensation-board'],
      sources: [WCB_SOURCES.S2, WCB_SOURCES.S5, WCB_SOURCES.S6]
    },
    {
      id: 'worksafebc-orange',
      status: 'held',
      years: 'by 2026',
      label: 'WorkSafeBC, in black and orange',
      note: '“Work” and “Safe” reversed out of black blocks and “BC” out of an orange one. The board took ' +
        'WorkSafeBC as its everyday name in 2005 and kept its legal name; when this wordmark first ' +
        'appeared has not been found.',
      applicability: {
        kind: 'first_observation',
        years: 'by 2026',
        note: 'On an official WorkSafeBC service on 27 September 2026. The name dates from 2005, which ' +
          'does not date this drawing of it.'
      },
      seenAt: ['https://asmtclr.online.worksafebc.com/Mobile/css/images/WorkSafeBC-logo.png'],
      sources: [WCB_SOURCES.S4, WCB_SOURCES.S3]
    }
  ]
}
