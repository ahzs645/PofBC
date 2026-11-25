// Explicit identity subjects complement the Crown/health acquisition queue.
//
// Eligibility for a visual collection is independent of an organization's legal kind.
// A subject/source/relation is not proof that artwork is held or that a distinct mark existed.
// Keep adoption, publication, observation and legal-name dates on their actual evidence; no
// artwork dates are inferred here. Runtime asset coverage is calculated by the coverage module.
//
// graphNode references a real atlas node. collectionIds identify only directly relevant
// shelves; parent collections must never be assigned to a child merely to make it look held.
// salaryEmployers are links to existing source employer records, never merge instructions.
// graphYear is navigation only: a year in the existing atlas lifespan, normally the year
// before an exclusive end or the last documented sighting of an untraced body. It never
// dates a logo. Values are static to keep the atlas history out of the gallery runtime.

import { HEALTH_COUNCIL_SUBJECTS } from './healthCouncilHistory.js'
import { ADDITIONAL_COUNCIL_SUBJECTS } from './additionalCouncilSubjects.js'
import { YOUTH_SUBJECTS } from './bcYouth.js'
import { FAMILY_COUNCIL_SUBJECT } from './councilForTheFamily.js'
import { ALCOHOL_AND_DRUG_COMMISSION_SUBJECT } from './alcoholAndDrugCommission.js'
import { RECONCILED_FAMILIES, RECONCILED_SUBJECTS } from './reconciledSubjects.js'
import { MUNICIPAL_FAMILIES, MUNICIPAL_KIND_LABELS, MUNICIPAL_SUBJECTS } from './municipalSubjects.js'
import { RECOVERED_IDENTITY_BODIES } from './recoveredIdentityData.js'
import { SCHOOL_IDENTITY_SUBJECTS } from '../schools/integration.js'
import { SCHOOL_FAMILY } from '../schools/districts.js'

import { POSTSECONDARY_FAMILY, POSTSECONDARY_SUBJECTS } from './postsecondarySubjects.js'
import { postsecondaryArtworkOf } from './postsecondaryArtwork.js'

import { SURVEY_AND_LIBRARY_SUBJECTS } from './geologicalSurveyAndLibrary.js'

export const IDENTITY_KIND_LABELS = {
  'legislative-institution': 'Legislative institution',
  'advisory-council': 'Advisory council',
  'public-college': 'Public college',
  'nonprofit-society': 'Nonprofit society',
  'education-predecessor': 'Educational predecessor or operation',
  'education-campus': 'Campus',
  'school-district': 'School district',
  'francophone-school-district': 'Francophone school district',
  ...MUNICIPAL_KIND_LABELS,
  "campaign": "Campaign or slogan",
  "regional-authority": "Regional authority",
  "public-subsidiary": "Public subsidiary",
  "corporate-subsidiary": "Corporate subsidiary",
  "police-service": "Police service",
  "service-brand": "Service or program brand",
  "municipal-service": "Municipal service",
  "crown-corporation": "Crown corporation",
  "regional-government": "Regional government",
  "government-branch": "Government branch",
  "agency": "Agency",
  "nonprofit-agency": "Nonprofit agency",
  "public-safety-organization": "Public-safety organization",
  "statutory-corporation": "Statutory corporation",
  "independent-regulator": "Independent regulator",
  "development-trust": "Development trust",
  "development-society": "Development society",
  "public-corporation": "Public corporation",
  "independent-board": "Independent board",
  "health-authority": "Health authority",
  "health-agency": "Health agency",
  "health-service": "Health service",
  "venue": "Public venue",
  "independent-officer": "Independent officer",
  "court": "Court",
  "central-agency": "Central agency",
  "public-university": "Public university",
  "advocacy-society": "Advocacy society",
  "public-institute": "Public institute",
  "charitable-institution": "Charitable institution"
}

export const IDENTITY_RELATION_LABELS = {
  'renamed-from': 'Renamed from',
  'renamed-to': 'Renamed to',
  'amalgamated-with': 'Amalgamated with',
  'amalgamated-into': 'Amalgamated into',
  'split-from': 'Split from',
  'split-off': 'Separated into',
  'split-into': 'Split into',
  'absorbed': 'Absorbed',
  'received-operations-from': 'Received operations from',
  'transferred-operations-to': 'Operations transferred to',
  'succeeded-at-site': 'Succeeded at site of',
  'site-succeeded-by': 'Site succeeded by',
  'successor-of': 'Successor of',
  "related-to": "Related to",
  "part-of": "Part of",
  "service-of": "Service of",
  "owned-by": "Owned by",
  "shareholder-of": "Holds the voting share of",
  "operated-by": "Operated by",
  "used-by": "Used by",
  "predecessor-of": "Predecessor of",
  "campaigned-for": "Campaigned for",
  "shares-identity-with": "Shares identity with"
}

const CURATED_FAMILIES = [
  {
    "id": "transit",
    "label": "Transit and fare systems",
    "description": "Regional operators, passenger services, network symbols and historical transit programs."
  },
  {
    "id": "regional-government",
    "label": "Regional government",
    "description": "Metro Vancouver and its service identities, with historical GVRD evidence kept distinct."
  },
  {
    "id": "liquor-distribution",
    "label": "Liquor and cannabis distribution",
    "description": "The Liquor Distribution Branch, its retail and wholesale brands, and earlier identities."
  },
  {
    "id": "creative-culture",
    "label": "Creative industries and arts",
    "description": "Creative BC, film-industry predecessors and the BC Arts Council."
  },
  {
    "id": "public-safety",
    "label": "Public safety",
    "description": "Emergency communications identities, separate from police services and health services."
  },
  {
    "id": "ferries",
    "label": "Ferries and governance",
    "description": "Ferry operators, historical authorities, the modern shareholder and independent regulator."
  },
  {
    "id": "regional-development",
    "label": "Regional development trusts",
    "description": "Regional trusts and development funds with their own public identities."
  },
  {
    "id": "regulators-administration",
    "label": "Regulators and public administration",
    "description": "Independent regulators, land records, pensions and delegated public-service bodies."
  },
  {
    "id": "specialist-health",
    "label": "Specialist health services",
    "description": "PHSA, emergency health services, hospitals and specialist public-health identities."
  },
  {
    "id": "hydro",
    "label": "BC Hydro and related identities",
    "description": "BC Hydro, its subsidiary, energy-conservation brands and historical utility evidence."
  },
  {
    "id": "gaming",
    "label": "BCLC and its programs",
    "description": "BCLC corporate identities, PlayNow and GameSense."
  },
  {
    "id": "venues",
    "label": "PavCo and venues",
    "description": "PavCo, BC Place, Vancouver Convention Centre and separately dated historical company artwork."
  },
  {
    "id": "museum-archives",
    "label": "Museum and archives",
    "description": "Royal BC Museum and BC Archives identities."
  },
  {
    "id": "innovation-training",
    "label": "Innovation and trades training",
    "description": "Current innovation and training bodies and their historical predecessors."
  },
  {
    "id": "independent-offices",
    "label": "Independent offices",
    "description": "Legislative officers and their own public identities."
  },
  {
    "id": "courts",
    "label": "Courts",
    "description": "Court seals, arms and publication signatures requiring source-specific review."
  },
  {
    "id": "provincial-administration",
    "label": "Provincial administration",
    "description": "Offices where a shared provincial signature may be appropriate and needs evidence."
  },
  {
    "id": "institutions",
    "label": "Universities and public institutions",
    "description": "Named institutions in the wider collection scope; academic, heraldic, athletics and uniform assets remain distinct."
  },
  {
    "id": "historical-research",
    "label": "Existing historical research",
    "description": "Unresolved corporate artwork and established families that should not be mistaken for new gaps."
  }
]

const CURATED_SUBJECTS = [
  {
    "id": "translink",
    "label": "TransLink",
    "name": "TransLink",
    "kind": "regional-authority",
    "family": "transit",
    "graphNode": "translink",
    "aliases": [
      "South Coast British Columbia Transportation Authority",
      "Greater Vancouver Transportation Authority",
      "GVTA",
      "SCBCTA"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "translink"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink operating companies",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies"
      },
      {
        "title": "TransLink logo history",
        "url": "https://buzzer.translink.ca/?p=27339",
        "note": "The history distinguishes the original GVTA wording from the simplified identity."
      },
      {
        "title": "TransLink active transportation toolkit",
        "url": "https://www.translink.ca/-/media/translink/documents/cycling/regional-cycling-strategy/active-transportation-promotion-and-education-toolkit.pdf#page=43",
        "note": "Appendix D distinguishes the Leaper and T marker; source guidance is not a claim that every variant is held."
      }
    ],
    "nextAction": "Review the original GVTA lockup and dated variants alongside the current corporate artwork.",
    "note": "The corporate Leaper and passenger-facing T marker are separate identities. Legal-name changes are not artwork-adoption dates.",
    "relations": []
  },
  {
    "id": "translink-t-marker",
    "label": "TransLink T marker",
    "name": "TransLink T marker",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "T marker",
      "Transit T",
      "network marker"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink active transportation toolkit",
        "url": "https://www.translink.ca/-/media/translink/documents/cycling/regional-cycling-strategy/active-transportation-promotion-and-education-toolkit.pdf#page=43",
        "note": "Appendix D distinguishes the Leaper and T marker; source guidance is not a claim that every variant is held."
      }
    ],
    "nextAction": "Find dated earlier applications while retaining the source’s supported colourway and use restrictions.",
    "note": "Appendix D describes a customer-facing network identifier with no inverse or monochrome version; do not generate those as official variants.",
    "relations": [
      {
        "subject": "translink",
        "type": "part-of",
        "note": "TransLink's own wayfinding mark, not a separate service."
      }
    ]
  },
  {
    "id": "coast-mountain-bus-company",
    "label": "Coast Mountain Bus Company",
    "name": "Coast Mountain Bus Company",
    "kind": "public-subsidiary",
    "family": "transit",
    "graphNode": "coast-mountain-bus-company",
    "aliases": [
      "CMBC",
      "Coast Mountain BusLink"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "coast-mountain-bus-company"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "Coast Mountain Bus Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/coast-mountain-bus-company"
      }
    ],
    "nextAction": "Seek source-native corporate artwork and separately date any Coast Mountain BusLink specimen.",
    "note": "Bus operations, SeaBus and Transit Security belong in the relationship record; their marks do not become interchangeable.",
    "relations": [
      {
        "subject": "translink",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "british-columbia-rapid-transit-company",
    "label": "BCRTC",
    "name": "British Columbia Rapid Transit Company",
    "kind": "public-subsidiary",
    "family": "transit",
    "graphNode": "british-columbia-rapid-transit-company",
    "aliases": [
      "BC Rapid Transit Company"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "british-columbia-rapid-transit-company"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Acquire the company mark and source-specific historical variants.",
    "note": "The company operates Expo and Millennium lines and West Coast Express; management of the Canada Line operating agreement is a different relationship.",
    "relations": [
      {
        "subject": "translink",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "west-coast-express",
    "label": "West Coast Express",
    "name": "West Coast Express",
    "kind": "public-subsidiary",
    "family": "transit",
    "graphNode": "west-coast-express",
    "aliases": [
      "WCE",
      "West Coast Express Limited"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "west-coast-express"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "West Coast Express name and logo announcement",
        "url": "https://www.translink.ca/-/media/translink/documents/rider-guide/buzzer-archives/1990s/1995/buzzer_1995_02_24.pdf#page=2",
        "note": "A dated publication specimen; announcement and service-launch dates are separate."
      },
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Seek original files for the 1995 purple-and-gold identity and compare dated later versions.",
    "note": "This identity family includes company and commuter-service uses; label each specimen with its use rather than inferring a legal change from a logo.",
    "relations": [
      {
        "subject": "translink",
        "type": "part-of"
      },
      {
        "subject": "british-columbia-rapid-transit-company",
        "type": "operated-by",
        "label": "Commuter service operated by BCRTC"
      }
    ]
  },
  {
    "id": "metro-vancouver-transit-police",
    "label": "Transit Police",
    "name": "Transit Police",
    "kind": "police-service",
    "family": "transit",
    "graphNode": "metro-vancouver-transit-police",
    "aliases": [
      "Metro Vancouver Transit Police",
      "South Coast British Columbia Transportation Authority Police Service",
      "Greater Vancouver Transportation Authority Police Service",
      "GVTA Police"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "metro-vancouver-transit-police",
      "transit-police"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "Transit Police heraldic register",
        "url": "https://www.gg.ca/en/heraldry/public-register/project/1363",
        "note": "Arms, flag and badge are separate from a corporate wordmark or uniform rendering."
      },
      {
        "title": "TransLink operating companies",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies"
      }
    ],
    "nextAction": "Seek source-native corporate artwork and separately documented heraldic emblems; link verified uniform specimens without treating them as the corporate logo.",
    "note": "The heraldic registration, corporate logo and a sewn badge are different evidence. Two salary employer labels remain separate source records.",
    "relations": [
      {
        "subject": "translink",
        "type": "part-of",
        "note": "One of TransLink's operating companies, within the TransLink enterprise."
      }
    ]
  },
  {
    "id": "transit-security",
    "label": "Transit Security",
    "name": "Transit Security",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "CMBC Transit Security",
      "BC Transit Security"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Coast Mountain Bus Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/coast-mountain-bus-company"
      }
    ],
    "nextAction": "Acquire dated CMBC Transit Security identifiers and keep them separate from police insignia.",
    "note": "Transit Security is described by CMBC and must not be attributed to Transit Police.",
    "relations": [
      {
        "subject": "coast-mountain-bus-company",
        "type": "service-of"
      },
      {
        "subject": "metro-vancouver-transit-police",
        "type": "related-to",
        "label": "Separate security and police roles"
      }
    ]
  },
  {
    "id": "skytrain",
    "label": "SkyTrain",
    "name": "SkyTrain",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Sky Train"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      },
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Seek standalone approved master files, historical wordmarks and separately attributed line identifiers.",
    "note": "A Surrey Langley SkyTrain project logo does not establish coverage of the network identity.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of"
      },
      {
        "subject": "british-columbia-rapid-transit-company",
        "type": "operated-by",
        "label": "Expo and Millennium line operations"
      }
    ]
  },
  {
    "id": "expo-line",
    "label": "Expo Line",
    "name": "Expo Line",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      },
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Acquire the line identifier from inspected official wayfinding artwork.",
    "note": "Line names, symbols and colours are passenger information, not independent corporate identities.",
    "relations": [
      {
        "subject": "skytrain",
        "type": "part-of"
      },
      {
        "subject": "british-columbia-rapid-transit-company",
        "type": "operated-by"
      }
    ]
  },
  {
    "id": "millennium-line",
    "label": "Millennium Line",
    "name": "Millennium Line",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      },
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Acquire the line identifier from inspected official wayfinding artwork.",
    "note": "Line names, symbols and colours are passenger information, not independent corporate identities.",
    "relations": [
      {
        "subject": "skytrain",
        "type": "part-of"
      },
      {
        "subject": "british-columbia-rapid-transit-company",
        "type": "operated-by"
      }
    ]
  },
  {
    "id": "canada-line",
    "label": "Canada Line",
    "name": "Canada Line",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      },
      {
        "title": "British Columbia Rapid Transit Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/british-columbia-rapid-transit-company"
      }
    ],
    "nextAction": "Collect the line identity and document its operating context separately.",
    "note": "BCRTC manages the Canada Line operating agreement; that does not mean it directly operates this line.",
    "relations": [
      {
        "subject": "skytrain",
        "type": "part-of"
      },
      {
        "subject": "british-columbia-rapid-transit-company",
        "type": "related-to",
        "label": "Manages the operating agreement"
      }
    ]
  },
  {
    "id": "seabus",
    "label": "SeaBus",
    "name": "SeaBus",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Sea-Bus",
      "Sea Bus"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "SeaBus anniversary history",
        "url": "https://buzzer.translink.ca/2022/06/45-facts-about-seabus-at-its-45th-anniversary/"
      },
      {
        "title": "Coast Mountain Bus Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/coast-mountain-bus-company"
      }
    ],
    "nextAction": "Collect dated Sea-Bus and SeaBus identities with the BC Hydro, BC Transit or CMBC era stated.",
    "note": "Historical livery and service marks need dated attribution; the current operator alone does not identify older artwork.",
    "relations": [
      {
        "subject": "coast-mountain-bus-company",
        "type": "operated-by"
      },
      {
        "subject": "translink",
        "type": "service-of"
      },
      {
        "subject": "bc-hydro",
        "type": "related-to",
        "label": "Historical service context"
      },
      {
        "subject": "bc-transit",
        "type": "related-to",
        "label": "Historical service context"
      }
    ]
  },
  {
    "id": "handydart",
    "label": "HandyDART / handyDART",
    "name": "HandyDART / handyDART",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "HandyDART",
      "Handy Dart"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink media resources",
        "url": "https://www.translink.ca/news/media-resources"
      },
      {
        "title": "BC Transit corporate identity policy",
        "url": "https://www.bctransit.com/wp-content/uploads/541/716/SPA5.03-Corporate-Identity.pdf"
      }
    ],
    "nextAction": "Compare TransLink and BC Transit applications, acquiring missing variants with each network and operator stated.",
    "note": "The name crosses networks; geography and operator context remain on each specimen.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of",
        "label": "Metro Vancouver service"
      },
      {
        "subject": "bc-transit",
        "type": "service-of",
        "label": "Service in BC Transit systems"
      }
    ]
  },
  {
    "id": "rapidbus",
    "label": "RapidBus",
    "name": "RapidBus",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Rapid Bus"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "RapidBus introduction",
        "url": "https://buzzer.translink.ca/2019/07/introducing-a-new-member-to-the-translink-fleet-say-hello-to-rapidbus/"
      }
    ],
    "nextAction": "Collect the service identity and dated launch/livery specimens.",
    "note": "Keep the TransLink RapidBus identity separate from other operators using rapid-bus language.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of"
      },
      {
        "subject": "b-line",
        "type": "related-to",
        "label": "Related bus-service identity"
      }
    ]
  },
  {
    "id": "b-line",
    "label": "B-Line",
    "name": "B-Line",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "B Line",
      "BLine"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "RapidBus introduction",
        "url": "https://buzzer.translink.ca/2019/07/introducing-a-new-member-to-the-translink-fleet-say-hello-to-rapidbus/"
      },
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      }
    ],
    "nextAction": "Acquire dated B-Line marks and preserve evidence of continuing as well as historical uses.",
    "note": "A RapidBus launch does not by itself establish that every B-Line use ended.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "compass",
    "label": "Compass",
    "name": "Compass",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Compass Card",
      "Compass fare card"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Compass naming announcement",
        "url": "https://buzzer.translink.ca/2011/03/compass-the-winning-name-of-our-electronic-fare-card/"
      }
    ],
    "nextAction": "Seek source-native fare-card artwork and compare dated card and system specimens.",
    "note": "The naming announcement and fare-system launch are distinct events.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "nightbus",
    "label": "NightBus",
    "name": "NightBus",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Night Bus",
      "NightBus District"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink wayfinding standards manual",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/freedom-of-information/wayfinding-standards-manual.pdf",
        "note": "Acquisition reference; acceptance of individual artwork requires file inspection."
      },
      {
        "title": "TransLink media resources",
        "url": "https://www.translink.ca/news/media-resources"
      }
    ],
    "nextAction": "Inspect the service identifier and NightBus District signage in official publications.",
    "note": "Standalone master artwork remains a source-specific acquisition question.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "west-vancouver-blue-bus",
    "label": "West Vancouver Blue Bus",
    "name": "West Vancouver Blue Bus",
    "kind": "municipal-service",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Blue Bus",
      "West Vancouver Municipal Transit"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Coast Mountain Bus Company",
        "url": "https://www.translink.ca/about-us/about-translink/operating-companies/coast-mountain-bus-company"
      }
    ],
    "nextAction": "Collect municipal transit identity history and dated Blue Bus artwork.",
    "note": "An associated municipal operator is not a TransLink subsidiary.",
    "relations": [
      {
        "subject": "translink",
        "type": "related-to",
        "label": "Regional service partnership"
      }
    ]
  },
  {
    "id": "aircare",
    "label": "AirCare",
    "name": "AirCare",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Air Care"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink 2012 annual report",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/corporate-reports/translink_annual_report/tl_annual_report_2012.pdf",
        "note": "Historical relationship evidence; does not imply a program is still operating."
      }
    ],
    "nextAction": "Collect historical program artwork and keep evidence dates with each specimen.",
    "note": "Historical emissions-testing program; an old annual report does not imply current operation.",
    "relations": [
      {
        "subject": "pacific-vehicle-testing-technologies",
        "type": "operated-by"
      },
      {
        "subject": "translink",
        "type": "service-of",
        "note": "A TransLink program, run by its subsidiary Pacific Vehicle Testing Technologies; ended 31 December 2014."
      }
    ]
  },
  {
    "id": "pacific-vehicle-testing-technologies",
    "label": "Pacific Vehicle Testing Technologies",
    "name": "Pacific Vehicle Testing Technologies",
    "kind": "public-subsidiary",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "PVTT",
      "Pacific Vehicle Testing Technologies Ltd."
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "TransLink 2012 annual report",
        "url": "https://www.translink.ca/-/media/translink/documents/about-translink/corporate-reports/translink_annual_report/tl_annual_report_2012.pdf",
        "note": "Historical relationship evidence; does not imply a program is still operating."
      }
    ],
    "nextAction": "Verify a distinct corporate mark independently of the AirCare program logo.",
    "note": "The program name and the historical operating company are separate subjects.",
    "relations": [
      {
        "subject": "translink",
        "type": "owned-by",
        "note": "TransLink's subsidiary that ran AirCare until the program ended at the close of 2014."
      }
    ]
  },
  {
    "id": "quickpass",
    "label": "QuickPass",
    "name": "QuickPass",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Quick Pass",
      "Golden Ears Bridge QuickPass"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "QuickPass 2009 media handout",
        "url": "https://buzzer.translink.ca/wp-content/uploads/2009/11/2009-11-19-quickpass-geb-media-tour-handout.pdf"
      }
    ],
    "nextAction": "Collect the dated Golden Ears Bridge tolling identity and source context.",
    "note": "Historical tolling-service identity; preserve the publication date without implying present operation.",
    "relations": [
      {
        "subject": "translink",
        "type": "service-of",
        "note": "Golden Ears Bridge tolling accounts, administered by TransLink, 2009–2017."
      }
    ]
  },
  {
    "id": "bc-transit",
    "label": "BC Transit",
    "name": "BC Transit",
    "kind": "crown-corporation",
    "family": "transit",
    "graphNode": "bc-transit",
    "aliases": [
      "British Columbia Transit"
    ],
    "collectionIds": [
      "bc-transit"
    ],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Transit history",
        "url": "https://www.bctransit.com/about/history/"
      },
      {
        "title": "BC Transit corporate identity policy",
        "url": "https://www.bctransit.com/wp-content/uploads/541/716/SPA5.03-Corporate-Identity.pdf"
      }
    ],
    "nextAction": "Extend the established collection only for demonstrated service or era gaps.",
    "note": "UTA, flag and loop-era corporate artwork already exists; service brands require their own attributed evidence.",
    "relations": [
      {
        "subject": "urban-transit-authority",
        "type": "related-to",
        "label": "Historical authority identity"
      }
    ]
  },
  {
    "id": "umo",
    "label": "Umo",
    "name": "Umo",
    "kind": "service-brand",
    "family": "transit",
    "graphNode": null,
    "aliases": [
      "Umo Mobility",
      "Umo Pass"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Umo at BC Transit",
        "url": "https://www.bctransit.com/umo/"
      },
      {
        "title": "BC Transit terms for Umo",
        "url": "https://www.bctransit.com/wp-content/uploads/2025/06/BC-Transit-Terms-and-Conditions-for-Use-of-Umo-20250617.pdf",
        "note": "Defines Umo as technology owned by Cubic Transportation Systems and licensed by BC Transit."
      }
    ],
    "nextAction": "Collect the BC Transit application of Umo and retain the vendor ownership context.",
    "note": "Umo is owned by Cubic Transportation Systems and licensed by BC Transit; it is not a BC-owned corporation.",
    "relations": [
      {
        "subject": "bc-transit",
        "type": "used-by"
      }
    ]
  },
  {
    "id": "urban-transit-authority",
    "label": "Urban Transit Authority",
    "name": "Urban Transit Authority",
    "kind": "crown-corporation",
    "family": "transit",
    "graphNode": "urban-transit-authority",
    "graphYear": 1981,
    "aliases": [
      "UTA"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Transit history",
        "url": "https://www.bctransit.com/about/history/"
      }
    ],
    "nextAction": "Improve dated source artwork without duplicating the established transit history.",
    "note": "Held historical specimens are represented in the BC Transit family; file quality and legal succession are separate questions.",
    "relations": [
      {
        "subject": "bc-transit",
        "type": "predecessor-of",
        "note": "The same corporation, renamed BC Transit in 1982."
      }
    ]
  },
  {
    "id": "metro-transit-operating-company",
    "label": "Metro Transit Operating Company",
    "name": "Metro Transit Operating Company",
    "kind": "crown-corporation",
    "family": "transit",
    "graphNode": "metro-transit-operating-company",
    "graphYear": 1991,
    "aliases": [
      "MTOC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Transit history",
        "url": "https://www.bctransit.com/about/history/"
      }
    ],
    "nextAction": "Seek a dated corporate specimen; retain an unconfirmed distinct-identity outcome if evidence remains inconclusive.",
    "note": "UTA arrows and The Buzzer masthead were not accepted as an MTOC corporate logo.",
    "relations": [
      {
        "subject": "bc-transit",
        "type": "related-to",
        "label": "Historical operations relationship"
      }
    ],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "metro-vancouver",
    "label": "Metro Vancouver",
    "name": "Metro Vancouver",
    "kind": "regional-government",
    "family": "regional-government",
    "graphNode": "metro-vancouver",
    "aliases": [
      "Greater Vancouver Regional District",
      "GVRD",
      "Metro Vancouver Regional District",
      "MVRD"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "metro-vancouver"
    ],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "Metro Vancouver brand portal",
        "url": "https://metrovancouver.org/media-room/metro-vancouver-brand"
      },
      {
        "title": "Metro Vancouver brand book",
        "url": "https://metrovancouver.org/media-room/Documents/metro-vancouver-brand-book.pdf",
        "note": "Brand-name adoption is distinct from the regional district legal-name change."
      }
    ],
    "nextAction": "Document approved current variants and acquire separately sourced GVRD-era specimens.",
    "note": "Brand adoption and the legal regional-district renaming are separate chronology fields.",
    "relations": []
  },
  {
    "id": "metro-vancouver-regional-parks",
    "label": "Metro Vancouver Regional Parks",
    "name": "Metro Vancouver Regional Parks",
    "kind": "service-brand",
    "family": "regional-government",
    "graphNode": null,
    "aliases": [
      "Regional Parks",
      "GVRD Parks"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Metro Vancouver Regional Parks brand book",
        "url": "https://metrovancouver.org/media-room/Documents/mv-regional-parks-brand-book.pdf"
      }
    ],
    "nextAction": "Acquire supported park-system identifiers from the dedicated brand book.",
    "note": "A Metro Vancouver service identity; generic corporate artwork alone does not cover it.",
    "relations": [
      {
        "subject": "metro-vancouver",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "liquor-distribution-branch",
    "label": "Liquor Distribution Branch",
    "name": "Liquor Distribution Branch",
    "kind": "government-branch",
    "family": "liquor-distribution",
    "graphNode": "liquor-distribution-branch",
    "aliases": [
      "LDB",
      "BCLDB",
      "BC Liquor Distribution Branch"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "LDB annual reports",
        "url": "https://www.bcldb.com/publications/annual-report"
      }
    ],
    "nextAction": "Find source-native branch signatures and dated historical specimens, with retail and wholesale identities attributed separately.",
    "note": "The atlas already knows the branch; its retail and wholesale identities are separate subjects.",
    "relations": [
      {
        "subject": "liquor-control-board",
        "type": "related-to",
        "label": "Historical liquor-administration context"
      }
    ]
  },
  {
    "id": "sub-bcliquor",
    "label": "BCLIQUOR",
    "name": "BCLIQUOR",
    "kind": "service-brand",
    "family": "liquor-distribution",
    "graphNode": "sub-bcliquor",
    "aliases": [
      "BC Liquor Stores",
      "BC Liquor",
      "BCL"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "LDB retail customers",
        "url": "https://www.bcldb.com/doing-business-ldb/retail-customers"
      },
      {
        "title": "LDB annual reports",
        "url": "https://www.bcldb.com/publications/annual-report"
      }
    ],
    "nextAction": "Establish the BC Liquor Stores and BCLIQUOR chronology through dated reports and signage; seek original artwork for earlier eras.",
    "note": "A retail identity of LDB, not a separate Crown corporation.",
    "relations": [
      {
        "subject": "liquor-distribution-branch",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "sub-bc-cannabis-stores",
    "label": "BC Cannabis Stores",
    "name": "BC Cannabis Stores",
    "kind": "service-brand",
    "family": "liquor-distribution",
    "graphNode": "sub-bc-cannabis-stores",
    "aliases": [
      "BCCS",
      "BC Cannabis"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "BC Cannabis Stores brand announcement",
        "url": "https://news.gov.bc.ca/releases/2018AG0027-000740",
        "note": "Brand announcement establishes the retail identity; it is not a separate Crown corporation."
      },
      {
        "title": "LDB annual reports",
        "url": "https://www.bcldb.com/publications/annual-report"
      }
    ],
    "nextAction": "Seek a source-native retail original and dated applications, distinguishing the brand announcement from later use.",
    "note": "Retail and wholesale marks should not be substituted for one another.",
    "relations": [
      {
        "subject": "liquor-distribution-branch",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "bc-cannabis-wholesale",
    "label": "BC Cannabis Wholesale",
    "name": "BC Cannabis Wholesale",
    "kind": "service-brand",
    "family": "liquor-distribution",
    "graphNode": null,
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Cannabis Wholesale quarterly report",
        "url": "https://www.bcldb.com/files/BC_Cannabis_Wholesale_Quarterly_Sales_Report_Q3_2024_LR_0.pdf"
      },
      {
        "title": "LDB annual reports",
        "url": "https://www.bcldb.com/publications/annual-report"
      }
    ],
    "nextAction": "Seek a source-native wholesale original and date its use through reports or other attributable specimens.",
    "note": "Wholesale identity under LDB, separate from BC Cannabis Stores.",
    "relations": [
      {
        "subject": "liquor-distribution-branch",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "ldb-wholesale",
    "label": "LDB Wholesale Operations",
    "name": "LDB Wholesale Operations",
    "kind": "service-brand",
    "family": "liquor-distribution",
    "graphNode": null,
    "aliases": [
      "BC Liquor Wholesale",
      "LDB Wholesale"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "LDB Wholesale Operations",
        "url": "https://wholesale.bcldb.com/"
      },
      {
        "title": "LDB annual reports",
        "url": "https://www.bcldb.com/publications/annual-report"
      }
    ],
    "nextAction": "Document the wholesale mark’s approved variants and establish its use chronology through dated specimens.",
    "note": "The corporate branch and retail identities do not establish wholesale-mark coverage.",
    "relations": [
      {
        "subject": "liquor-distribution-branch",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "liquor-control-board",
    "label": "Liquor Control Board",
    "name": "Liquor Control Board",
    "kind": "agency",
    "family": "liquor-distribution",
    "graphNode": "liquor-control-board",
    "graphYear": 1972,
    "aliases": [
      "BC Liquor Control Board"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Archives: Liquor Control Board",
        "url": "https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-liquor-board"
      }
    ],
    "nextAction": "Locate a dated original signature or seal before claiming a distinct historical logo.",
    "note": "Historical agency evidence is separate from current LDB branding.",
    "relations": []
  },
  {
    "id": "creative-bc",
    "label": "Creative BC",
    "name": "Creative BC",
    "kind": "nonprofit-agency",
    "family": "creative-culture",
    "graphNode": "creative-bc",
    "aliases": [
      "Creative BC Society"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "Creative BC logos and brand",
        "url": "https://creativebc.com/about/logos-and-brand/",
        "note": "The page offers joint-logo JPG/EPS downloads; linked packs do not imply that every master has been inspected."
      },
      {
        "title": "Creative BC media room and history",
        "url": "https://creativebc.com/about/media-room/",
        "note": "Describes the Film Commission and BC Film and Media merger."
      }
    ],
    "nextAction": "Compare the corporate artwork with approved joint-logo originals and date earlier variants, keeping funding lockups explicit.",
    "note": "The Film Commission and BC Film and Media merger informs the history; predecessor artwork needs its own evidence.",
    "relations": []
  },
  {
    "id": "bc-film-commission",
    "label": "BC Film Commission",
    "name": "BC Film Commission",
    "kind": "agency",
    "family": "creative-culture",
    "graphNode": "bc-film-commission",
    "graphYear": 2012,
    "aliases": [
      "British Columbia Film Commission"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Creative BC media room and history",
        "url": "https://creativebc.com/about/media-room/",
        "note": "Describes the Film Commission and BC Film and Media merger."
      },
      {
        "title": "Creative BC logos and brand",
        "url": "https://creativebc.com/about/logos-and-brand/",
        "note": "The page offers joint-logo JPG/EPS downloads; linked packs do not imply that every master has been inspected."
      }
    ],
    "nextAction": "Collect historic Commission artwork and current Creative BC program applications separately.",
    "note": "A predecessor organization and a continuing program name can share words without representing the same dated specimen.",
    "relations": [
      {
        "subject": "creative-bc",
        "type": "predecessor-of",
        "note": "Creative BC was formed on 1 April 2013 from the BC Film Commission and BC Film + Media."
      }
    ]
  },
  {
    "id": "bc-film-and-media",
    "label": "BC Film / BC Film + Media",
    "name": "BC Film / BC Film + Media",
    "kind": "nonprofit-agency",
    "family": "creative-culture",
    "graphNode": null,
    "aliases": [
      "BC Film",
      "BC Film and Media",
      "BC Film + Media",
      "British Columbia Film"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Creative BC media room and history",
        "url": "https://creativebc.com/about/media-room/",
        "note": "Describes the Film Commission and BC Film and Media merger."
      }
    ],
    "nextAction": "Acquire dated BC Film and Film + Media identities and verify their chronology.",
    "note": "The official Creative BC history identifies this side of the merger; current Creative BC artwork does not cover it.",
    "relations": [
      {
        "subject": "creative-bc",
        "type": "predecessor-of"
      }
    ]
  },
  {
    "id": "bc-arts-council",
    "label": "BC Arts Council",
    "name": "BC Arts Council",
    "kind": "agency",
    "family": "creative-culture",
    "graphNode": "bc-arts-council",
    "aliases": [
      "British Columbia Arts Council",
      "BCAC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 1,
    "scope": "core",
    "sources": [
      {
        "title": "BC Arts Council logos and acknowledgement",
        "url": "https://www.bcartscouncil.ca/funding/logo-and-acknowledgement/"
      }
    ],
    "nextAction": "Compare the Council identifier and joint Province/Council lockups, acquiring missing originals as separately described variants.",
    "note": "The atlas agency record already exists; a joint download is not evidence that every colourway is held.",
    "relations": []
  },
  {
    "id": "e-comm",
    "label": "E-Comm 9-1-1",
    "name": "E-Comm 9-1-1",
    "kind": "public-safety-organization",
    "family": "public-safety",
    "graphNode": "e-comm",
    "aliases": [
      "E-Comm",
      "EComm",
      "E-Comm 911",
      "Emergency Communications for British Columbia"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "E-Comm governance",
        "url": "https://www.ecomm911.ca/transformation/governance/"
      },
      {
        "title": "E-Comm reports",
        "url": "https://www.ecomm911.ca/about-e-comm/updates/"
      }
    ],
    "nextAction": "Collect source-native corporate artwork and dated historical variants.",
    "note": "Emergency communications governance is distinct from provincial Crown status and from individual police agencies.",
    "relations": []
  },
  {
    "id": "bc-ferry-corporation",
    "label": "BC Ferries operator history",
    "name": "British Columbia Ferry Corporation (historical operator)",
    "kind": "crown-corporation",
    "family": "ferries",
    "graphNode": "bc-ferry-corporation",
    "graphYear": 2002,
    "aliases": [
      "BC Ferries",
      "British Columbia Ferry Corporation"
    ],
    "collectionIds": [
      "bc-ferries"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Ferries brand-guideline disclosure",
        "url": "https://www.bcferries.com/our-company/freedom-of-information/23-016",
        "note": "The disclosure page lists a 325-page responsive file. A source lead does not establish that all its contents have been reviewed."
      }
    ],
    "nextAction": "Enrich the existing multi-era collection from inspected guideline records.",
    "note": "The historical BC Ferry Corporation and modern operator have a multi-era collection; this does not cover the modern Ferry Authority or the regulator.",
    "relations": []
  },
  {
    "id": "bc-ferry-authority",
    "label": "BC Ferry Authority, 1964–1977",
    "name": "British Columbia Ferry Authority (1964–1977)",
    "kind": "crown-corporation",
    "family": "ferries",
    "graphNode": "bc-ferry-authority",
    "graphYear": 1976,
    "aliases": [
      "Historical British Columbia Ferry Authority"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Archives: historical Ferry Authority",
        "url": "https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-ferry-authority-2"
      }
    ],
    "nextAction": "Improve the existing dated historical specimens without replacing them with modern Authority artwork.",
    "note": "This historical Authority is different from the governance body created under the 2003 model.",
    "relations": [
      {
        "subject": "bc-ferry-authority-2003",
        "type": "related-to",
        "label": "Different body with a similar name"
      },
      {
        "subject": "bc-ferry-corporation",
        "type": "predecessor-of",
        "note": "Continued as the British Columbia Ferry Corporation in 1977."
      }
    ]
  },
  {
    "id": "bc-ferry-authority-2003",
    "label": "B.C. Ferry Authority",
    "name": "B.C. Ferry Authority",
    "kind": "statutory-corporation",
    "family": "ferries",
    "graphNode": "bc-ferry-authority-2003",
    "aliases": [
      "BC Ferry Authority 2003",
      "Modern BC Ferry Authority"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "B.C. Ferry Authority governance",
        "url": "https://www.bcferryauthority.com/about-us/",
        "note": "The modern 2003 governance body is different from the 1964–1977 historical Authority."
      }
    ],
    "nextAction": "Seek source-native shareholder artwork and dated earlier specimens, keeping the modern authority separate from the ferry operator and historical authority.",
    "note": "A corporation without share capital holding BC Ferries’ voting share; do not overwrite the 1964–1977 Authority.",
    "relations": [
      {
        "subject": "bc-ferry-corporation",
        "type": "shareholder-of",
        "note": "Under the Coastal Ferry Act of 2003 the Authority holds the single voting share of BC Ferry Services Inc., the operator that succeeded the British Columbia Ferry Corporation; the Province holds its preferred shares."
      }
    ]
  },
  {
    "id": "sub-bc-ferry-commission",
    "label": "BC Ferry Commission",
    "name": "BC Ferry Commission",
    "kind": "independent-regulator",
    "family": "ferries",
    "graphNode": "sub-bc-ferry-commission",
    "aliases": [
      "Office of the BC Ferries Commissioner",
      "BC Ferries Commissioner",
      "British Columbia Ferry Commission"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Ferry Commission role",
        "url": "https://www.bcferrycommission.ca/about/"
      },
      {
        "title": "BC Ferry Commission annual reports",
        "url": "https://www.bcferrycommission.ca/about/annual-reports/"
      }
    ],
    "nextAction": "Seek source-native regulator artwork and compare dated reports to establish earlier identifiers.",
    "note": "Regulator, shareholder, ferry operator and provincial procurer are distinct roles.",
    "relations": [
      {
        "subject": "bc-ferry-authority-2003",
        "type": "related-to",
        "label": "Separate regulator and shareholder roles"
      }
    ]
  },
  {
    "id": "northern-development-initiative-trust",
    "label": "Northern Development",
    "name": "Northern Development",
    "kind": "development-trust",
    "family": "regional-development",
    "graphNode": "northern-development-initiative-trust",
    "aliases": [
      "Northern Development Initiative Trust",
      "NDIT"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Northern Development annual report",
        "url": "https://www.northerndevelopment.bc.ca/wp-content/uploads/2025/05/NDIT_2024-AR_Web.pdf"
      }
    ],
    "nextAction": "Seek source-native trust artwork and dated earlier specimens to establish the identity’s chronology.",
    "note": "Already an atlas agency; a background-image download is not an established master-logo kit.",
    "relations": []
  },
  {
    "id": "island-coastal-economic-trust",
    "label": "Island Coastal Economic Trust",
    "name": "Island Coastal Economic Trust",
    "kind": "development-trust",
    "family": "regional-development",
    "graphNode": "island-coastal-economic-trust",
    "aliases": [
      "ICET",
      "Island Coastal Trust"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Island Coastal Economic Trust identity story",
        "url": "https://islandcoastaltrust.ca/news/moving-forward-together/",
        "note": "The October 2025 story documents a new identity; earlier artwork remains a separate era."
      }
    ],
    "nextAction": "Seek original files for the five-paddle identity and recover earlier artwork with dated evidence.",
    "note": "Preserve each era’s source; the story documents design authorship but is not a complete master package.",
    "relations": []
  },
  {
    "id": "etsi-bc",
    "label": "ETSI-BC",
    "name": "Economic Trust of the Southern Interior",
    "kind": "development-trust",
    "family": "regional-development",
    "graphNode": "etsi-bc",
    "aliases": [
      "Southern Interior Development Initiative Trust",
      "SIDIT"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "ETSI-BC logo downloads",
        "url": "https://www.etsi-bc.ca/logos/",
        "note": "The source links to a folder of full-name, short and stacked versions."
      }
    ],
    "nextAction": "Inspect the downloadable variants and source the earlier SIDIT identity.",
    "note": "Former and current names require their own dated artwork; short and stacked variants are not new organizations.",
    "relations": []
  },
  {
    "id": "nechako-kitamaat-development-fund",
    "label": "Nechako-Kitamaat Development Fund",
    "name": "Nechako-Kitamaat Development Fund",
    "kind": "development-society",
    "family": "regional-development",
    "graphNode": "nechako-kitamaat-development-fund",
    "aliases": [
      "Nechako-Kitamaat Development Fund Society",
      "NKDF",
      "NKDFS"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Nechako-Kitamaat Development Fund history",
        "url": "https://nkdf.org/how-to-apply/how-to-apply/program-guidelines"
      },
      {
        "title": "Nechako-Kitamaat Development Fund annual report",
        "url": "https://nkdf.org/uploads/files/annualReports/NKDF_Annual_Report_2024-2025.pdf"
      }
    ],
    "nextAction": "Collect the dated report identity and inspect any available original artwork.",
    "note": "A regional development fund society, not another name for Northern Development Initiative Trust.",
    "relations": []
  },
  {
    "id": "bc-pension-corporation",
    "label": "BC Pension Corporation",
    "name": "BC Pension Corporation",
    "kind": "public-corporation",
    "family": "regulators-administration",
    "graphNode": "bc-pension-corporation",
    "aliases": [
      "British Columbia Pension Corporation",
      "Pension Corporation"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Pension Corporation publications",
        "url": "https://www.bcpensioncorp.ca/publications"
      }
    ],
    "nextAction": "Seek source-native corporate artwork and separately dated historical variants.",
    "note": "Pension administration is distinct from BCI investment management, which already has gallery coverage.",
    "relations": []
  },
  {
    "id": "bc-safety-authority",
    "label": "BC Safety Authority",
    "name": "BC Safety Authority",
    "kind": "independent-regulator",
    "family": "regulators-administration",
    "graphNode": "bc-safety-authority",
    "graphYear": 2016,
    "aliases": [
      "BCSA",
      "British Columbia Safety Authority"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Technical Safety BC 2017 bulletin",
        "url": "https://files.technicalsafetybc.ca/v3/assets/bltdec2ded849740f4d/blt3568bd886f6ae5ce/63326ed2f4d6a4451a8c9406/ib-pr_2017-01_rev.1_12-2017.pdf",
        "note": "Documents the BC Safety Authority name change; current artwork is not evidence of the older mark."
      }
    ],
    "nextAction": "Find dated original BCSA artwork independently of the current TSBC identity.",
    "note": "The renaming bulletin establishes a relationship, not visual equivalence of historical and current marks.",
    "relations": [
      {
        "subject": "technical-safety-bc",
        "type": "predecessor-of",
        "label": "Earlier operating name"
      }
    ]
  },
  {
    "id": "technical-safety-bc",
    "label": "Technical Safety BC",
    "name": "Technical Safety BC",
    "kind": "independent-regulator",
    "family": "regulators-administration",
    "graphNode": "technical-safety-bc",
    "aliases": [
      "TSBC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Technical Safety BC",
        "url": "https://www.technicalsafetybc.ca/"
      },
      {
        "title": "Technical Safety BC 2017 bulletin",
        "url": "https://files.technicalsafetybc.ca/v3/assets/bltdec2ded849740f4d/blt3568bd886f6ae5ce/63326ed2f4d6a4451a8c9406/ib-pr_2017-01_rev.1_12-2017.pdf",
        "note": "Documents the BC Safety Authority name change; current artwork is not evidence of the older mark."
      }
    ],
    "nextAction": "Date the current identity through published specimens and collect the earlier BCSA era separately.",
    "note": "Already represented in the atlas; it is eligible for identity collection without being reclassified as a Crown.",
    "relations": []
  },
  {
    "id": "land-title-and-survey-authority",
    "label": "Land Title and Survey Authority",
    "name": "Land Title and Survey Authority",
    "kind": "statutory-corporation",
    "family": "regulators-administration",
    "graphNode": "land-title-and-survey-authority",
    "aliases": [
      "LTSA",
      "Land Title and Survey Authority of British Columbia",
      "BC Land Title and Survey"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "LTSA organization and subsidiary",
        "url": "https://ltsa.ca/about-ltsa/",
        "note": "LTSA describes its non-governmental statutory structure and wholly owned LandSure subsidiary."
      }
    ],
    "nextAction": "Date LTSA’s corporate variants and separately acquire subsidiary and service brands with their own attribution.",
    "note": "LTSA describes itself as a non-governmental, self-funded statutory corporation.",
    "relations": []
  },
  {
    "id": "landsure-systems",
    "label": "LandSure Systems",
    "name": "LandSure Systems",
    "kind": "corporate-subsidiary",
    "family": "regulators-administration",
    "graphNode": "landsure-systems",
    "aliases": [
      "LandSure",
      "LandSure Systems Ltd."
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "LTSA organization and subsidiary",
        "url": "https://ltsa.ca/about-ltsa/",
        "note": "LTSA describes its non-governmental statutory structure and wholly owned LandSure subsidiary."
      }
    ],
    "nextAction": "Collect LandSure’s own identity with its subsidiary relationship retained.",
    "note": "A wholly owned LTSA subsidiary; generic LTSA artwork alone does not establish its coverage.",
    "relations": [
      {
        "subject": "land-title-and-survey-authority",
        "type": "owned-by"
      }
    ]
  },
  {
    "id": "consumer-protection-bc",
    "label": "Consumer Protection BC",
    "name": "Consumer Protection BC",
    "kind": "independent-regulator",
    "family": "regulators-administration",
    "graphNode": "consumer-protection-bc",
    "aliases": [
      "Business Practices and Consumer Protection Authority",
      "BPCPA"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Consumer Protection BC",
        "url": "https://www.consumerprotectionbc.ca/about-us/"
      },
      {
        "title": "Consumer Protection BC media room",
        "url": "https://www.consumerprotectionbc.ca/media-centre/media-room/",
        "note": "Offers logo versions by request; a public master pack was not established by the audit."
      }
    ],
    "nextAction": "Seek a corporate master through the media-request route and date the identity through published specimens.",
    "note": "A public master pack was not verified by the audit; the organization exercises delegated regulatory authority.",
    "relations": []
  },
  {
    "id": "forest-practices-board",
    "label": "Forest Practices Board",
    "name": "Forest Practices Board",
    "kind": "independent-board",
    "family": "regulators-administration",
    "graphNode": "forest-practices-board",
    "aliases": [
      "FPB",
      "BC Forest Practices Board"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Forest Practices Board",
        "url": "https://www.bcfpb.ca/"
      }
    ],
    "nextAction": "Inspect official reports and artwork before identifying distinct marks or shared signatures.",
    "note": "An existing atlas body does not imply a standalone corporate mark has already been accepted.",
    "relations": []
  },
  {
    "id": "provincial-health-services-authority",
    "label": "PHSA",
    "name": "Provincial Health Services Authority",
    "kind": "health-authority",
    "family": "specialist-health",
    "graphNode": "provincial-health-services-authority",
    "aliases": [],
    "collectionIds": [
      "collected-provincial-health-services-authority"
    ],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "PHSA programs and services",
        "url": "https://www.phsa.ca/our-services/programs-services"
      }
    ],
    "nextAction": "Preserve existing PHSA corporate artwork while adding separately evidenced service identities.",
    "note": "A parent mark does not establish coverage for specialist health programs or hospitals.",
    "relations": []
  },
  {
    "id": "bc-emergency-health-services",
    "label": "BC Emergency Health Services",
    "name": "BC Emergency Health Services",
    "kind": "health-agency",
    "family": "specialist-health",
    "graphNode": "bc-emergency-health-services",
    "aliases": [
      "BCEHS"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Emergency Health Services",
        "url": "https://www.bcehs.ca/about/who-we-are"
      },
      {
        "title": "BCEHS anniversary identity story",
        "url": "https://www.bcehs.ca/about/news-stories/stories/50th-anniversary-logo-meaning"
      }
    ],
    "nextAction": "Seek source-native corporate artwork and separately dated anniversary designs with each use stated.",
    "note": "BC Ambulance Service and BCEHS identities are related but are not interchangeable.",
    "relations": [
      {
        "subject": "provincial-health-services-authority",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "bc-ambulance-service",
    "label": "BC Ambulance Service",
    "name": "BC Ambulance Service",
    "kind": "health-service",
    "family": "specialist-health",
    "graphNode": null,
    "aliases": [
      "BCAS",
      "British Columbia Ambulance Service"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Ambulance Service",
        "url": "https://www.bcehs.ca/about/who-we-are/bc-ambulance-service"
      },
      {
        "title": "BCEHS anniversary identity story",
        "url": "https://www.bcehs.ca/about/news-stories/stories/50th-anniversary-logo-meaning"
      }
    ],
    "nextAction": "Collect service marks, heraldic/uniform emblems and anniversary designs as distinct asset types.",
    "note": "An accepted patch does not by itself establish corporate-logo coverage.",
    "relations": [
      {
        "subject": "bc-emergency-health-services",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "emergency-health-services-commission",
    "label": "Emergency Health Services Commission",
    "name": "Emergency Health Services Commission",
    "kind": "agency",
    "family": "specialist-health",
    "graphNode": "emergency-health-services-commission",
    "graphYear": 2012,
    "aliases": [
      "EHSC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Archives: Emergency Health Services Commission",
        "url": "https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-emergency-health-services-commission"
      },
      {
        "title": "BC Ambulance Service",
        "url": "https://www.bcehs.ca/about/who-we-are/bc-ambulance-service"
      }
    ],
    "nextAction": "Seek dated original Commission artwork and keep its historical context.",
    "note": "Do not substitute a current BCEHS or BCAS logo for an unverified Commission mark.",
    "relations": [
      {
        "subject": "bc-emergency-health-services",
        "type": "predecessor-of"
      }
    ],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "sub-bc-centre-for-disease-control",
    "label": "BC Centre for Disease Control",
    "name": "BC Centre for Disease Control",
    "kind": "health-agency",
    "family": "specialist-health",
    "graphNode": "sub-bc-centre-for-disease-control",
    "aliases": [
      "BCCDC",
      "BC Center for Disease Control"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BCCDC media enquiries",
        "url": "https://www.bccdc.ca/about/news-stories/media-enquiries"
      }
    ],
    "nextAction": "Collect a verified BCCDC original and dated historical specimens.",
    "note": "The official media page is a logo-request route; PHSA coverage alone does not supply the BCCDC identity.",
    "relations": [
      {
        "subject": "provincial-health-services-authority",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "sub-bc-childrens-hospital",
    "label": "BC Children’s Hospital",
    "name": "BC Children’s Hospital",
    "kind": "health-service",
    "family": "specialist-health",
    "graphNode": "sub-bc-childrens-hospital",
    "aliases": [
      "BC Children's Hospital",
      "BCCH",
      "Sunny Hill Health Centre"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "PHSA: BC Children’s Hospital and Sunny Hill",
        "url": "https://www.phsa.ca/our-services/programs-services/bc-childrens-hospital-and-sunny-hill-health-centre-for-children"
      }
    ],
    "nextAction": "Collect the hospital identity and attribute Sunny Hill and foundation artwork separately.",
    "note": "The atlas node includes Sunny Hill; do not attribute every related charity or facility mark to the hospital.",
    "relations": [
      {
        "subject": "provincial-health-services-authority",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "sub-bc-womens-hospital",
    "label": "BC Women’s Hospital + Health Centre",
    "name": "BC Women’s Hospital + Health Centre",
    "kind": "health-service",
    "family": "specialist-health",
    "graphNode": "sub-bc-womens-hospital",
    "aliases": [
      "BC Women's Hospital",
      "BC Women’s Hospital",
      "BCWH"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "PHSA: BC Women’s Hospital",
        "url": "https://www.phsa.ca/our-services/programs-services/bc-womens-hospital-health-centre"
      }
    ],
    "nextAction": "Seek source-native hospital artwork and dated earlier variants, retaining independent foundation attribution where applicable.",
    "note": "A PHSA or fundraising-foundation mark is not automatically the hospital’s own identity.",
    "relations": [
      {
        "subject": "provincial-health-services-authority",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "sub-bc-cancer",
    "label": "BC Cancer",
    "name": "BC Cancer",
    "kind": "health-agency",
    "family": "specialist-health",
    "graphNode": "sub-bc-cancer",
    "aliases": [
      "BC Cancer Agency",
      "BCCA"
    ],
    "collectionIds": [
      "collected-sub-bc-cancer"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "PHSA: BC Cancer",
        "url": "https://www.phsa.ca/our-services/programs-services/bc-cancer-agency"
      }
    ],
    "nextAction": "Preserve the established history and only add a demonstrated missing design or version.",
    "note": "BC Cancer already has multiple accepted identities; foundation-owned assets remain separately attributed.",
    "relations": [
      {
        "subject": "provincial-health-services-authority",
        "type": "part-of"
      }
    ]
  },
  {
    "id": "bc-hydro",
    "label": "BC Hydro",
    "name": "BC Hydro",
    "kind": "crown-corporation",
    "family": "hydro",
    "graphNode": "bc-hydro",
    "aliases": [
      "British Columbia Hydro and Power Authority"
    ],
    "collectionIds": [
      "bc-hydro"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Hydro",
        "url": "https://www.bchydro.com/"
      }
    ],
    "nextAction": "Preserve the existing multi-era family and inspect specific missing subsidiary or program artwork.",
    "note": "The current corporate identity already includes a Power smart tagline.",
    "relations": []
  },
  {
    "id": "sub-powerex",
    "label": "Powerex",
    "name": "Powerex",
    "kind": "public-subsidiary",
    "family": "hydro",
    "graphNode": "sub-powerex",
    "aliases": [
      "Powerex Corp.",
      "Powerex Corporation"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Powerex",
        "url": "https://powerex.com/"
      }
    ],
    "nextAction": "Date Powerex’s corporate variants through attributable publications and seek earlier original artwork.",
    "note": "Powerex is a separate subsidiary identity; the BC Hydro gallery does not cover it.",
    "relations": [
      {
        "subject": "bc-hydro",
        "type": "owned-by"
      }
    ]
  },
  {
    "id": "power-smart",
    "label": "Power Smart",
    "name": "Power Smart",
    "kind": "service-brand",
    "family": "hydro",
    "graphNode": null,
    "aliases": [
      "PowerSmart"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Hydro",
        "url": "https://www.bchydro.com/"
      }
    ],
    "nextAction": "Verify standalone and historical Power Smart artwork separately from the corporate tagline.",
    "note": "Presence of the tagline in a BC Hydro logo does not establish a separate standalone mark.",
    "relations": [
      {
        "subject": "bc-hydro",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "bclc",
    "label": "BCLC",
    "name": "BCLC",
    "kind": "crown-corporation",
    "family": "gaming",
    "graphNode": "bclc",
    "aliases": [
      "British Columbia Lottery Corporation"
    ],
    "collectionIds": [
      "bclc"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BCLC",
        "url": "https://corporate.bclc.com/"
      }
    ],
    "nextAction": "Preserve corporate history and add only source-specific program or design gaps.",
    "note": "The established corporate collection is distinct from PlayNow and GameSense.",
    "relations": []
  },
  {
    "id": "sub-playnow",
    "label": "PlayNow",
    "name": "PlayNow",
    "kind": "service-brand",
    "family": "gaming",
    "graphNode": "sub-playnow",
    "aliases": [
      "PlayNow.com",
      "Play Now"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "PlayNow",
        "url": "https://www.playnow.com/"
      },
      {
        "title": "BCLC",
        "url": "https://corporate.bclc.com/"
      }
    ],
    "nextAction": "Date the service identity’s variants and record the jurisdiction of each application.",
    "note": "A BCLC corporate mark does not establish PlayNow brand coverage.",
    "relations": [
      {
        "subject": "bclc",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "gamesense",
    "label": "GameSense",
    "name": "GameSense",
    "kind": "service-brand",
    "family": "gaming",
    "graphNode": null,
    "aliases": [
      "Game Sense"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BCLC GameSense",
        "url": "https://corporate.bclc.com/player-health/gamesense.html"
      }
    ],
    "nextAction": "Collect the program identity and distinguish BCLC originals from other licensed applications.",
    "note": "GameSense is a program identity; licensed use elsewhere does not create another BC organization.",
    "relations": [
      {
        "subject": "bclc",
        "type": "service-of"
      }
    ]
  },
  {
    "id": "bc-pavilion-corporation",
    "label": "PavCo",
    "name": "PavCo",
    "kind": "crown-corporation",
    "family": "venues",
    "graphNode": "bc-pavilion-corporation",
    "aliases": [
      "BC Pavilion Corporation",
      "British Columbia Pavilion Corporation"
    ],
    "collectionIds": [
      "collected-bc-pavilion-corporation"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "PavCo",
        "url": "https://www.bcpavco.com/"
      }
    ],
    "nextAction": "Preserve corporate artwork while adding each venue’s separately sourced identity.",
    "note": "PavCo corporate and venue brands are different subjects.",
    "relations": []
  },
  {
    "id": "sub-bc-place",
    "label": "BC Place",
    "name": "BC Place",
    "kind": "venue",
    "family": "venues",
    "graphNode": "sub-bc-place",
    "aliases": [
      "BC Place Stadium"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Place",
        "url": "https://www.bcplace.com/"
      },
      {
        "title": "PavCo",
        "url": "https://www.bcpavco.com/"
      }
    ],
    "nextAction": "Date the current venue identity and acquire separately sourced earlier venue specimens.",
    "note": "The 1983 British Columbia Place Ltd. reconstruction is a different historical company record.",
    "relations": [
      {
        "subject": "bc-pavilion-corporation",
        "type": "operated-by"
      },
      {
        "subject": "bc-place-ltd",
        "type": "related-to",
        "label": "Historical company artwork"
      }
    ]
  },
  {
    "id": "sub-vancouver-convention-centre",
    "label": "Vancouver Convention Centre",
    "name": "Vancouver Convention Centre",
    "kind": "venue",
    "family": "venues",
    "graphNode": "sub-vancouver-convention-centre",
    "aliases": [
      "VCC",
      "Vancouver Convention and Exhibition Centre"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Vancouver Convention Centre",
        "url": "https://www.vancouverconventioncentre.com/"
      },
      {
        "title": "PavCo",
        "url": "https://www.bcpavco.com/"
      }
    ],
    "nextAction": "Seek source-native venue artwork and dated historical versions with the venue clearly identified.",
    "note": "PavCo’s corporate mark alone does not establish the convention centre’s identity coverage.",
    "relations": [
      {
        "subject": "bc-pavilion-corporation",
        "type": "operated-by"
      }
    ]
  },
  {
    "id": "bc-place-ltd",
    "label": "British Columbia Place Ltd.",
    "name": "British Columbia Place Ltd.",
    "kind": "crown-corporation",
    "family": "venues",
    "graphNode": "bc-place-ltd",
    "graphYear": 1986,
    "aliases": [
      "BC Place Ltd."
    ],
    "collectionIds": [
      "collected-bc-place-ltd"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "PavCo",
        "url": "https://www.bcpavco.com/"
      }
    ],
    "nextAction": "Preserve the accepted 1983 reconstruction and compare only against identified historical sources.",
    "note": "Historical company artwork is not a substitute for the current stadium brand.",
    "relations": [
      {
        "subject": "sub-bc-place",
        "type": "related-to",
        "label": "Distinct historical company and venue subjects"
      }
    ]
  },
  {
    "id": "royal-bc-museum",
    "label": "Royal BC Museum",
    "name": "Royal BC Museum",
    "kind": "crown-corporation",
    "family": "museum-archives",
    "graphNode": "royal-bc-museum",
    "aliases": [
      "Royal British Columbia Museum",
      "RBCM"
    ],
    "collectionIds": [
      "royal-bc-museum"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Royal BC Museum",
        "url": "https://royalbcmuseum.bc.ca/"
      }
    ],
    "nextAction": "Preserve existing museum artwork and review specific missing historical variants.",
    "note": "Museum coverage does not by itself establish a distinct BC Archives service identity.",
    "relations": []
  },
  {
    "id": "sub-bc-archives",
    "label": "BC Archives",
    "name": "BC Archives",
    "kind": "service-brand",
    "family": "museum-archives",
    "graphNode": "sub-bc-archives",
    "aliases": [
      "British Columbia Archives"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Archives",
        "url": "https://royalbcmuseum.bc.ca/bc-archives"
      }
    ],
    "nextAction": "Verify distinct Archives artwork or document a shared signature with an actual specimen.",
    "note": "A departmental name typeset beside provincial arms is not automatically a unique logo.",
    "relations": [
      {
        "subject": "royal-bc-museum",
        "type": "part-of"
      }
    ],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "innovate-bc",
    "label": "Innovate BC",
    "name": "Innovate BC",
    "kind": "crown-corporation",
    "family": "innovation-training",
    "graphNode": "innovate-bc",
    "aliases": [],
    "collectionIds": [
      "collected-innovate-bc"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Innovate BC",
        "url": "https://www.innovatebc.ca/"
      }
    ],
    "nextAction": "Preserve current artwork while adding separately dated predecessor identities.",
    "note": "Current artwork cannot establish historical Science Council or Innovation Council marks.",
    "relations": []
  },
  {
    "id": "bc-innovation-council",
    "label": "BC Innovation Council",
    "name": "BC Innovation Council",
    "kind": "agency",
    "family": "innovation-training",
    "graphNode": "bc-innovation-council",
    "graphYear": 2017,
    "aliases": [
      "BCIC",
      "British Columbia Innovation Council"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Innovate BC",
        "url": "https://www.innovatebc.ca/"
      }
    ],
    "nextAction": "Find dated BCIC original artwork and record the supported identity period.",
    "note": "A historical atlas record exists; successor artwork is not evidence of its mark.",
    "relations": [
      {
        "subject": "innovate-bc",
        "type": "predecessor-of"
      },
      {
        "subject": "science-council-of-bc",
        "type": "related-to",
        "label": "Earlier institutional history"
      }
    ]
  },
  {
    "id": "science-council-of-bc",
    "label": "Science Council of BC",
    "name": "Science Council of BC",
    "kind": "agency",
    "family": "innovation-training",
    "graphNode": "science-council-of-bc",
    "graphYear": 2003,
    "aliases": [
      "Science Council of British Columbia",
      "SCBC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Science Council of BC service plan",
        "url": "https://www.bcbudget.gov.bc.ca/2003/sp/crowncorps/scbc.pdf"
      }
    ],
    "nextAction": "Inspect dated official publications for a corporate specimen.",
    "note": "Do not confuse this historical council with Science World.",
    "relations": [
      {
        "subject": "bc-innovation-council",
        "type": "predecessor-of"
      }
    ]
  },
  {
    "id": "skilledtradesbc",
    "label": "SkilledTradesBC",
    "name": "SkilledTradesBC",
    "kind": "crown-corporation",
    "family": "innovation-training",
    "graphNode": "skilledtradesbc",
    "aliases": [
      "Skilled Trades BC"
    ],
    "collectionIds": [
      "collected-skilledtradesbc"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "SkilledTradesBC",
        "url": "https://skilledtradesbc.ca/"
      }
    ],
    "nextAction": "Preserve current artwork and review historical training-agency designs separately.",
    "note": "Current SVG coverage does not settle predecessor identity chronology.",
    "relations": []
  },
  {
    "id": "industry-training-authority",
    "label": "Industry Training Authority",
    "name": "Industry Training Authority",
    "kind": "agency",
    "family": "innovation-training",
    "graphNode": "industry-training-authority",
    "graphYear": 2021,
    "aliases": [
      "ITA",
      "Industry Training Authority BC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "SkilledTradesBC",
        "url": "https://skilledtradesbc.ca/"
      }
    ],
    "nextAction": "Collect dated ITA artwork and distinguish legal and operating-name history.",
    "note": "Current SkilledTradesBC artwork is not a substitute for the ITA identity.",
    "relations": [
      {
        "subject": "skilledtradesbc",
        "type": "predecessor-of"
      }
    ]
  },
  {
    "id": "industry-training-and-apprenticeship-commission",
    "label": "Industry Training and Apprenticeship Commission",
    "name": "Industry Training and Apprenticeship Commission",
    "kind": "agency",
    "family": "innovation-training",
    "graphNode": "industry-training-and-apprenticeship-commission",
    "graphYear": 2002,
    "aliases": [
      "ITAC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Industry Training and Apprenticeship Commission announcement",
        "url": "https://archive.news.gov.bc.ca/releases/archive/pre2001/1997/0614.asp"
      }
    ],
    "nextAction": "Find a dated Commission specimen before asserting a distinct logo.",
    "note": "Keep the unresolved artwork question separate from the existing historical organization record.",
    "relations": [
      {
        "subject": "industry-training-authority",
        "type": "predecessor-of"
      }
    ],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "chief-electoral-officer",
    "label": "Elections BC",
    "name": "Elections BC",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "chief-electoral-officer",
    "aliases": [
      "Chief Electoral Officer"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Elections BC official website",
        "url": "https://elections.bc.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "ombudsperson",
    "label": "BC Ombudsperson",
    "name": "BC Ombudsperson",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "ombudsperson",
    "aliases": [
      "Ombudsperson",
      "Ombudsman"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Ombudsperson official website",
        "url": "https://bcombudsperson.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "information-and-privacy-commissioner",
    "label": "Information and Privacy Commissioner",
    "name": "Information and Privacy Commissioner",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "information-and-privacy-commissioner",
    "aliases": [
      "OIPC",
      "Office of the Information and Privacy Commissioner"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Information and Privacy Commissioner official website",
        "url": "https://www.oipc.bc.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "conflict-of-interest-commissioner",
    "label": "Conflict of Interest Commissioner",
    "name": "Conflict of Interest Commissioner",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "conflict-of-interest-commissioner",
    "aliases": [
      "COIBC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Conflict of Interest Commissioner official website",
        "url": "https://coibc.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "representative-for-children-and-youth",
    "label": "Representative for Children and Youth",
    "name": "Representative for Children and Youth",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "representative-for-children-and-youth",
    "aliases": [
      "RCY",
      "RCYBC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Representative for Children and Youth official website",
        "url": "https://rcybc.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "human-rights-commissioner",
    "label": "BC Human Rights Commissioner",
    "name": "BC Human Rights Commissioner",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "human-rights-commissioner",
    "aliases": [
      "BCOHRC",
      "Office of the Human Rights Commissioner"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "BC Human Rights Commissioner official website",
        "url": "https://bchumanrights.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "police-complaint-commissioner",
    "label": "Police Complaint Commissioner",
    "name": "Police Complaint Commissioner",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "police-complaint-commissioner",
    "aliases": [
      "OPCC",
      "Office of the Police Complaint Commissioner"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "core",
    "sources": [
      {
        "title": "Police Complaint Commissioner official website",
        "url": "https://opcc.bc.ca"
      }
    ],
    "nextAction": "Inspect official artwork and dated reports; distinguish office identity, heraldry and shared provincial signatures.",
    "note": "The office is eligible for identity collection without being treated as a Crown corporation.",
    "relations": []
  },
  {
    "id": "auditor-general",
    "label": "Auditor General of British Columbia",
    "name": "Auditor General of British Columbia",
    "kind": "independent-officer",
    "family": "independent-offices",
    "graphNode": "auditor-general",
    "aliases": [
      "OAG",
      "Auditor General"
    ],
    "collectionIds": [
      "collected-auditor-general"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Auditor General of British Columbia official website",
        "url": "https://www.oag.bc.ca"
      }
    ],
    "nextAction": "Preserve the accepted office identity and inspect only specific missing eras.",
    "note": "An existing collection already covers the Auditor General.",
    "relations": []
  },
  {
    "id": "court-of-appeal",
    "label": "Court of Appeal for British Columbia",
    "name": "Court of Appeal for British Columbia",
    "kind": "court",
    "family": "courts",
    "graphNode": "court-of-appeal",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Court of Appeal for British Columbia official website",
        "url": "https://www.bccourts.ca/Court_of_Appeal/"
      }
    ],
    "nextAction": "Review dated seals, arms and publication signatures before classifying a distinct emblem.",
    "note": "Lack of a dedicated gallery collection does not prove that a separate logo exists.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "supreme-court",
    "label": "Supreme Court of British Columbia",
    "name": "Supreme Court of British Columbia",
    "kind": "court",
    "family": "courts",
    "graphNode": "supreme-court",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Supreme Court of British Columbia official website",
        "url": "https://www.bccourts.ca/supreme_court/"
      }
    ],
    "nextAction": "Review dated seals, arms and publication signatures before classifying a distinct emblem.",
    "note": "Lack of a dedicated gallery collection does not prove that a separate logo exists.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "provincial-court",
    "label": "Provincial Court of British Columbia",
    "name": "Provincial Court of British Columbia",
    "kind": "court",
    "family": "courts",
    "graphNode": "provincial-court",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Provincial Court of British Columbia official website",
        "url": "https://www.provincialcourt.bc.ca"
      }
    ],
    "nextAction": "Review dated seals, arms and publication signatures before classifying a distinct emblem.",
    "note": "Lack of a dedicated gallery collection does not prove that a separate logo exists.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "office-of-the-premier",
    "label": "Office of the Premier",
    "name": "Office of the Premier",
    "kind": "central-agency",
    "family": "provincial-administration",
    "graphNode": "office-of-the-premier",
    "aliases": [
      "Premier’s Office"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Office of the Premier official website",
        "url": "https://www2.gov.bc.ca/gov/content/governments/organizational-structure/office-of-the-premier"
      }
    ],
    "nextAction": "Compare a dated official signature to determine whether shared provincial identity is the correct record.",
    "note": "No distinct corporate logo is asserted. Shared-identity status requires an actual supporting specimen.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "government-communications-and-public-engagement",
    "label": "Government Communications and Public Engagement",
    "name": "Government Communications and Public Engagement",
    "kind": "central-agency",
    "family": "provincial-administration",
    "graphNode": "government-communications-and-public-engagement",
    "aliases": [
      "GCPE"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Government Communications and Public Engagement official website",
        "url": "https://news.gov.bc.ca"
      }
    ],
    "nextAction": "Compare a dated official signature to determine whether shared provincial identity is the correct record.",
    "note": "No distinct corporate logo is asserted. Shared-identity status requires an actual supporting specimen.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "interior-university-society",
    "label": "Interior University Society",
    "name": "Interior University Society",
    "kind": "advocacy-society",
    "family": "institutions",
    "graphNode": null,
    "aliases": [
      "IUS",
      "Interior University",
      "Northern U"
    ],
    "collectionIds": [
      "collected-interior-university-society"
    ],
    "salaryEmployers": [],
    "priority": 2,
    "scope": "institution",
    "sources": [
      {
        "title": "UNBC — History: the 1987 origins and 1988 campaign",
        "url": "https://www.unbc.ca/about-unbc/history",
        "note": "Records the society’s incorporation on 1 December 1987 and its advocacy for a northern university."
      },
      {
        "title": "Interior University Society vector brand kit, version 1.2",
        "citation": "User-supplied historical identity reconstruction, IUS_Vector_Brand_Kit(1).zip; README, asset manifest and original-artifact photograph inventory.",
        "note": "The supplied vectors are modern reconstructions. The invitation specimen is dated 8 June 1988; that observed use does not date the identity’s creation."
      }
    ],
    "nextAction": "Locate original campaign artwork and dated adoption records; the reconstructed fonts, proportions and colours remain approximate.",
    "note": "Incorporated on 1 December 1987, the Interior University Society organised the campaign for a university in northern BC. Its campaign helped establish UNBC; the society was a separate advocacy organisation, not an earlier operating university or a former legal name of UNBC.",
    "relations": [
      {
        "type": "campaigned-for",
        "subject": "university-of-northern-bc",
        "label": "Regional campaign that helped establish UNBC",
        "sourceUrl": "https://www.unbc.ca/about-unbc/history"
      }
    ]
  },
  {
    "id": "university-of-northern-bc",
    "label": "UNBC",
    "name": "University of Northern British Columbia",
    "kind": "public-university",
    "family": "institutions",
    "graphNode": "university-of-northern-bc",
    "aliases": [
      "University of Northern BC"
    ],
    "collectionIds": [],
    "salaryEmployers": [
      "university-of-northern-bc"
    ],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "UNBC logos and graphic standards",
        "url": "https://www.unbc.ca/communications-and-marketing/logos-and-graphic-standards",
        "note": "Academic logo, athletics mark and heraldic symbols have different purposes."
      },
      {
        "title": "UNBC — History",
        "url": "https://www.unbc.ca/about-unbc/history",
        "note": "Connects the Interior University Society campaign to UNBC’s establishment in 1990 and official opening in 1994."
      },
      {
        "title": "University of Northern British Columbia Act, SBC 1990, c.28",
        "url": "https://www.bclaws.gov.bc.ca/civix/document/id/94consol18/94consol18/90028",
        "note": "Section 2 establishes UNBC as a corporation. Assented to 6 July 1990; effective 20 July 1990."
      }
    ],
    "nextAction": "Date earlier academic identity variants; inspect additional approved arrangements and keep heraldic, athletics and uniform material as separate asset types.",
    "note": "UNBC grew from a regional campaign led by the Interior University Society. The university was established by statute in 1990 and officially opened in 1994. Its academic, heraldic and athletics identities are distinct from the society’s earlier campaign artwork.",
    "relations": []
  },
  {
    "id": "university-of-british-columbia",
    "label": "UBC",
    "name": "University of British Columbia",
    "kind": "public-university",
    "family": "institutions",
    "graphNode": "university-of-british-columbia",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [
      "university-of-bc"
    ],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "UBC brand",
        "url": "https://brand.ubc.ca/"
      }
    ],
    "nextAction": "Date earlier academic identity variants; inspect additional approved arrangements and keep heraldic, athletics and uniform material as separate asset types.",
    "note": "Existing security patches, where present, do not establish academic-logo coverage.",
    "relations": []
  },
  {
    "id": "simon-fraser-university",
    "label": "SFU",
    "name": "Simon Fraser University",
    "kind": "public-university",
    "family": "institutions",
    "graphNode": "simon-fraser-university",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [
      "simon-fraser-university"
    ],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "SFU brand toolkit",
        "url": "https://www.sfu.ca/communicators-toolkit/brand.html"
      }
    ],
    "nextAction": "Collect academic identity originals and date earlier variants; link heraldic, athletics and uniform material as separate asset types.",
    "note": "Existing security patches, where present, do not establish academic-logo coverage.",
    "relations": []
  },
  {
    "id": "university-of-victoria",
    "label": "UVic",
    "name": "University of Victoria",
    "kind": "public-university",
    "family": "institutions",
    "graphNode": "university-of-victoria",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [
      "university-of-victoria"
    ],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "University of Victoria logos",
        "url": "https://www.uvic.ca/brand/brand-guidelines/logos/index.php"
      }
    ],
    "nextAction": "Date earlier academic identity variants; inspect additional approved arrangements and keep heraldic, athletics and uniform material as separate asset types.",
    "note": "Existing security patches, where present, do not establish academic-logo coverage.",
    "relations": []
  },
  {
    "id": "bcit",
    "label": "BCIT",
    "name": "British Columbia Institute of Technology",
    "artworkReview": postsecondaryArtworkOf('bcit'),
    "kind": "public-institute",
    "family": "institutions",
    "graphNode": "bcit",
    "aliases": [],
    "collectionIds": [],
    "salaryEmployers": [
      "bcit"
    ],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "BCIT building signage guidelines",
        "url": "https://www.bcit.ca/files/facilities/campusdev/pdf/240530_bcit_building_signage_guidelines.pdf",
        "note": "Dated signage/brand evidence; does not imply every institutional master is held."
      }
    ],
    "nextAction": "Confirm reuse permission before adding any historical artwork. The source links document the marks without adding copies to the gallery.",
    "note": "The gallery’s existing website logo is separate from the historical logo sources, anniversary artwork and heraldic grant below.",
    "relations": []
  },
  {
    "id": "science-world",
    "label": "Science World",
    "name": "Science World",
    "kind": "charitable-institution",
    "family": "institutions",
    "graphNode": "science-world",
    "aliases": [
      "ASTC Science World Society",
      "Science World British Columbia"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "institution",
    "sources": [
      {
        "title": "Science World brand assets",
        "url": "https://www.scienceworld.ca/brand/",
        "note": "ASTC Science World Society is a registered charity; keep its institution and heraldic/uniform assets distinct."
      }
    ],
    "nextAction": "Date the current approved variants and acquire separately sourced historical identities.",
    "note": "ASTC Science World Society is a registered charity, not a provincial Crown corporation.",
    "relations": []
  },
  {
    "id": "bc-housing",
    "label": "BC Housing",
    "name": "BC Housing",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "bc-housing",
    "aliases": [
      "British Columbia Housing Management Commission"
    ],
    "collectionIds": [
      "collected-bc-housing"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Housing",
        "url": "https://www.bchousing.org/"
      }
    ],
    "nextAction": "Preserve accepted corporate artwork and source any shared-identity claims separately.",
    "note": "The housing family already has accepted historical and current designs.",
    "relations": []
  },
  {
    "id": "provincial-rental-housing-corporation",
    "label": "Provincial Rental Housing Corporation",
    "name": "Provincial Rental Housing Corporation",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "provincial-rental-housing-corporation",
    "aliases": [
      "PRHC"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "PRHC letter in 100 Mile House council agenda",
        "url": "https://www.100milehouse.com/sites/default/files/2025-11/2025_Nov_12_Special_Agenda_PKG.pdf#page=7",
        "note": "Letter dated 6 November 2025 uses BC Housing’s emblem and wordmark. The repository’s source audit visually checked this page; evidence is limited to this document."
      },
      {
        "title": "BC Housing",
        "url": "https://www.bchousing.org/"
      }
    ],
    "nextAction": "Extend the documented shared-identity evidence with other dated specimens, and continue any distinct-mark research.",
    "note": "The inspected 6 November 2025 letter uses BC Housing’s identity. This establishes shared use in that document, not a universal rule for every PRHC publication.",
    "relations": [
      {
        "subject": "bc-housing",
        "type": "shares-identity-with",
        "label": "BC Housing identity on the 6 November 2025 letter"
      }
    ],
    "identityStatus": "shared-identity"
  },
  {
    "id": "bc-electric-company-crown",
    "label": "BC Electric, Crown period",
    "name": "BC Electric, Crown period",
    "kind": "crown-corporation",
    "family": "hydro",
    "graphNode": "bc-electric-company-crown",
    "graphYear": 1964,
    "aliases": [
      "British Columbia Electric Company",
      "BC Electric Company"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Hydro",
        "url": "https://www.bchydro.com/"
      }
    ],
    "nextAction": "Find a clean contemporary mark demonstrably used during provincial ownership.",
    "note": "Earlier private BC Electric Railway artwork and later BC Hydro marks are not automatically evidence of this period.",
    "relations": [
      {
        "subject": "bc-hydro",
        "type": "predecessor-of"
      }
    ]
  },
  {
    "id": "wlc-developments",
    "label": "W.L.C. Developments",
    "name": "W.L.C. Developments",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "wlc-developments",
    "graphYear": 1997,
    "aliases": [
      "WLC Developments",
      "W.L.C. Developments Ltd."
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Archives: Assets and Land Corporation and predecessors",
        "url": "https://search-bcarchives.royalbcmuseum.bc.ca/british-columbia-assets-and-land-corporation"
      }
    ],
    "nextAction": "Seek original company documents and property records for an attributable mark or seal.",
    "note": "Existing acquisition record remains unresolved; a distinct identity is not assumed.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "bc-harbours-board",
    "label": "BC Harbours Board",
    "name": "BC Harbours Board",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "bc-harbours-board",
    "graphYear": 1984,
    "aliases": [
      "British Columbia Harbours Board"
    ],
    "collectionIds": [],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "Order in Council 1061/1985, BC Harbours Board",
        "url": "https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1061_1985",
        "note": "Establishes the historical body, not a verified corporate graphic."
      }
    ],
    "nextAction": "Seek a dated corporate specimen and retain an unconfirmed-identity outcome where appropriate.",
    "note": "Absence of accepted artwork is not proof that a distinct logo existed.",
    "relations": [],
    "identityStatus": "distinct-unconfirmed"
  },
  {
    "id": "bc-railway-company",
    "label": "BC Rail",
    "name": "BC Rail",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "bc-railway-company",
    "aliases": [
      "British Columbia Railway Company",
      "BCRC"
    ],
    "collectionIds": [
      "collected-bc-railway-company"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Crown agency service plans",
        "url": "https://www.bcbudget.gov.bc.ca/2026/crownserviceplans/"
      }
    ],
    "nextAction": "Preserve the established multi-era railway collection and add only demonstrated gaps.",
    "note": "An existing substantial collection; it should not be counted as an absent identity family.",
    "relations": []
  },
  {
    "id": "icbc",
    "label": "ICBC",
    "name": "ICBC",
    "kind": "crown-corporation",
    "family": "historical-research",
    "graphNode": "icbc",
    "aliases": [
      "Insurance Corporation of British Columbia"
    ],
    "collectionIds": [
      "icbc"
    ],
    "salaryEmployers": [],
    "priority": 3,
    "scope": "core",
    "sources": [
      {
        "title": "BC Crown agency service plans",
        "url": "https://www.bcbudget.gov.bc.ca/2026/crownserviceplans/"
      }
    ],
    "nextAction": "Preserve existing corporate history and source-specific variants.",
    "note": "An existing substantial collection; the expansion does not replace accepted artwork.",
    "relations": []
  }
]

// The reconciled gallery owners and the municipal registry follow the curated subjects.
// Municipalities come before the historical-research family in the register.
export const IDENTITY_FAMILIES = [...CURATED_FAMILIES.slice(0, -1), ...RECONCILED_FAMILIES, ...MUNICIPAL_FAMILIES, SCHOOL_FAMILY, POSTSECONDARY_FAMILY, CURATED_FAMILIES.at(-1)]
const recoveredById = new Map(RECOVERED_IDENTITY_BODIES.map((body) => [body.id, body]))
export const IDENTITY_SUBJECTS = [...CURATED_SUBJECTS, ...SURVEY_AND_LIBRARY_SUBJECTS, ...YOUTH_SUBJECTS, ...HEALTH_COUNCIL_SUBJECTS, ...ADDITIONAL_COUNCIL_SUBJECTS, FAMILY_COUNCIL_SUBJECT, ALCOHOL_AND_DRUG_COMMISSION_SUBJECT, ...RECONCILED_SUBJECTS, ...MUNICIPAL_SUBJECTS, ...SCHOOL_IDENTITY_SUBJECTS, ...POSTSECONDARY_SUBJECTS]
  .map((subject) => recoveredById.get(subject.id)?.nextAction
    ? { ...subject, nextAction: recoveredById.get(subject.id).nextAction }
    : subject)
