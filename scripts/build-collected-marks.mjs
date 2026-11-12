// Build the small gallery index from the complete acquisition records.
// Assets are local source files, including raster specimens; no remote hotlink is needed.
//
// The acquisition inventory, vector search and historical follow-up registers feed it.
// They add original artwork to bodies and to the one-off programs on the gallery's timelines.
// Every file is checked against the checksum its record gives.
import { readFileSync, writeFileSync } from 'node:fs'
import { basename } from 'node:path'
import { fileURLToPath } from 'node:url'
import { createHash } from 'node:crypto'

const root = new URL('../', import.meta.url)
const read = (path) => JSON.parse(readFileSync(new URL(path, root), 'utf8'))
const inventory = read('research/identity/collection-2026-10-22/inventory.json')
const register = read('research/identity/vector-search-2026-10-30/source-register.json')
const ticorp = read('research/identity/ticorp-vector-2026-11-08/source-register.json')
const followup = read('research/identity/vector-followup-2026-11-08/source-register.json')
const historical = read('research/identity/historical-vector-followup-2026-10-30/source-register.json')
const innovate = read('research/identity/innovate-bc-vector-2026-11-12/source-register.json')
const railSightings = read('research/identity/bc-rail-sightings-2026-11-12/source-register.json')
const bceid = read('research/identity/bceid-2026-11-12/source-register.json')
const sharedServices = read('research/identity/shared-services-bc-2026-11-12/source-register.json')
const bcCancerNow = read('research/identity/bc-cancer-current-2026-11-12/source-register.json')
// Programs' marks held as supplied reconstructions, with no body of their own in the inventory.
const PROGRAM_PACKAGES = ['bc-travel-industry-2026-11-12', 'justice-institute-2026-11-12', 'auditor-general-2026-11-12', 'bc-online-2026-11-12', 'bc-cancer-agency-2026-11-12', 'solutions-bc-vector-2026-11-12', 'healthlink-bc-2026-11-12', 'bc-cancer-modern-2026-11-12']
  .map((search) => ({ search, register: read(`research/identity/${search}/source-register.json`) }))
// Supplied packages that add a vector to a body, each read with the search it came from.
const PACKAGES = ['bc-assessment-vector-2026-11-12', 'bc-power-commission-vector-2026-11-12', 'bc-place-vector-2026-11-12', 'bc-railway-vector-2026-11-12', 'bc-railway-dogwood-vector-2026-11-12', 'bc-systems-vector-2026-11-12', 'bc-housing-1978-vector-2026-11-12', 'bc-petroleum-vector-2026-11-12', 'bc-housing-houses-vector-2026-11-12', 'fvhr-vector-2026-11-12']
  .map((search) => ({ search, register: read(`research/identity/${search}/source-register.json`) }))
const railway = read('research/identity/railway-history-2026-11-12/source-register.json')
const railwayHistory = read('research/identity/railway-history-2026-11-12/history.json')

const checked = (asset) => {
  if (!/^identity-collected\/[a-z0-9._/-]+$/i.test(asset.file) || asset.file.includes('..')) {
    throw new Error(`Invalid asset path: ${asset.file}`)
  }
  const data = readFileSync(new URL(`public/${asset.file}`, root))
  if (createHash('sha256').update(data).digest('hex') !== asset.sha256) {
    throw new Error(`Source checksum differs: ${asset.file}`)
  }
  if (asset.preview) {
    if (!/^identity-collected\/[a-z0-9._/-]+$/.test(asset.preview) || asset.preview.includes('..')) {
      throw new Error(`Invalid preview path: ${asset.preview}`)
    }
    const preview = readFileSync(new URL(`public/${asset.preview}`, root))
    if (asset.previewSha256 && createHash('sha256').update(preview).digest('hex') !== asset.previewSha256) {
      throw new Error(`Preview checksum differs: ${asset.preview}`)
    }
  }
  return asset
}

// The register's labels are its file names; these say what each file shows.
const LABELS = {
  'ticorp-2025-colour-source-vector': 'Full colour, Summer 2025 project update',
  'ticorp-2020-reversed-source-vector': 'White, Spring 2020 project overview',
  'pavco-2025-26-colour-source-vector': 'Full colour, FY2025/26 year in review',
  'pavco-2023-reversed-source-vector': 'White, 2023–2026 accessibility plan',
  'forest-renewal-bc-2000-colour-source-vector': 'Full colour, December 2000 funded-project report',
  'forest-renewal-bc-1999-black-source-vector': 'Black, March 1999 woodlot inventory manual',
  'worksafe-2003-serif-source-vector': 'Distressed WorkSafe wordmark and board name, 2003 annual report',
  'worksafebc-2004-tagline-source-vector': 'Black and orange with tagline, 2004 annual report',
  'worksafebc-2024-colour-source-vector': 'Black and orange, 2024 annual report',
  'bclc-2009-colour-tagline-source-vector': 'Older palette with tagline, 2009 service plan update',
  'bclc-2009-reversed-source-vector': 'White with coloured dots, 2009 service plan update',
  'bclc-2011-reversed-tagline-source-vector': 'White with coloured dots and tagline, 2010/11 annual report',
  'bccie-2022-source-vector': 'Full colour, 2022–2025 strategic plan',
  'bcfma-2021-source-vector': 'Teal emblem and wordmark, 2020/21 report',
  'bc-housing-corporate-component-source-vector': 'Emblem and wordmark',
  'bc-housing-research-centre-source-vector': 'Research Centre lockup',
  'bcib-2022-horizontal-reversed-source-vector': 'Full name, reversed, 2021/22 report',
  'bcib-2025-tagline-reversed-source-vector': '“Building Opportunity Here”, reversed, 2024/25 report',
  'columbia-power-2024-reversed-source-vector': 'Reversed, 2024 history book',
  'community-living-bc-2014-reversed-source-vector': 'Reversed, 2013/14 annual report',
  'community-living-bc-2023-colour-source-vector': 'Full colour, 2023 report',
  'infrastructure-bc-2026-colour-source-vector': 'Full colour, Spring 2026 brochure',
  'infrastructure-bc-2026-reversed-source-vector': 'Reversed, Spring 2026 brochure',
  'fnha-icon': 'Symbol',
  'fnha-logo-colour': 'Full colour',
  'fnha-logo-white': 'White lettering',
  'interior-health-blue-horizontal-source-extraction': 'Blue, horizontal, 2023 roadmap',
  'phsa-black-source-extraction': 'Black',
  'phsa-white-source-extraction': 'White',
  'bc-oil-gas-commission-2014': 'Full colour, 2014 report',
  'bc-transmission-2009': 'Short name, 2009 service plan',
  'partnerships-bc-2012': 'Full colour, 2012/13 report',
  'bc-public-service-where-ideas-work-2023-reverse': '“Where ideas work”, reversed, 2023 corporate plan',
  'canada-starts-here-2012': '“Canada Starts Here”, 2012',
  'canada-starts-here-bc-jobs-plan-2012': '“Canada Starts Here” with the BC Jobs Plan, 2012',
  BCID_StrongerBC_RGB_pos: 'Endorsed, full colour',
  BCID_StrongerBC_RGB_rev: 'Endorsed, full colour, reversed',
  BCID_StrongerBC_Solid_pos: 'Endorsed, solid colour',
  BCID_StrongerBC_Solid_rev: 'Endorsed, solid colour, reversed',
  StrongerBC_RGB_pos: 'Wordmark, full colour',
  StrongerBC_RGB_rev: 'Wordmark, full colour, reversed',
  StrongerBC_Solid_pos: 'Wordmark, solid colour',
  StrongerBC_Solid_rev: 'Wordmark, solid colour, reversed',
  'welcomebc-2016': 'The flat mark with a gold rule, 2016',
  'welcomebc-current': 'Endorsed, with a gold rule, current',
  'workbc-2016': 'The flat mark with a gold rule, 2016',
  'workbc-current': 'The flat mark with a grey rule, current'
}

// Files dropped because the same design is held as vector artwork (colour aside: a body's colours
// are its standard ones, so a recoloured copy is not another design). The gallery keeps the vector;
// the dropped file's source stays recorded in its acquisition record, and its date, if it has one,
// is kept on the vector as a further sighting.
const SUPERSEDED = {
  'source-transportation-investment-corporation-transportation-investment-corporation-png': 'vector-ticorp-2025-colour-source-vector',
  'source-bc-housing-bc-housing-png': 'vector-bc-housing-corporate-component-source-vector',
  'source-bc-assessment-bc-assessment-jpg': 'bc-assessment-svg',
  // The official EPS stays as the SVG's original download.
  'source-bc-assessment-bc-assessment-eps': 'bc-assessment-svg',
  'source-columbia-power-columbia-power-png': 'vector-columbia-power-2024-reversed-source-vector',
  'source-infrastructure-bc-infrastructure-bc-png': 'vector-infrastructure-bc-2026-colour-source-vector',
  'source-community-living-bc-community-living-bc-png': 'vector-community-living-bc-2023-colour-source-vector',
  'source-knowledge-network-knowledge-network-colour-png': 'source-knowledge-network-knowledge-network-colour-eps',
  'source-bc-pavilion-corporation-pavco-png': 'vector-pavco-2025-26-colour-source-vector',
  'source-forest-enhancement-society-fesbc-horizontal-png': 'source-forest-enhancement-society-fesbc-horizontal-eps',
  'source-forest-enhancement-society-fesbc-vertical-png': 'source-forest-enhancement-society-fesbc-vertical-eps',
  'source-innovate-bc-innovate-bc-teal-png': 'innovate-bc-2024-colour',
  // The wordmark alone, twice; the logo's vector carries it.
  'source-innovate-bc-innovate-bc-logo-png': 'innovate-bc-2024-colour',
  'source-innovate-bc-innovate-bc-wordmark-png': 'innovate-bc-2024-colour',
  'source-bc-family-maintenance-agency-bc-family-maintenance-agency-png': 'vector-bcfma-2021-source-vector',
  'source-inbc-inbc-print-png': 'source-inbc-inbc-svg',
  'source-bc-council-for-international-education-bccie-png': 'vector-bccie-2022-source-vector',
  'source-interior-health-interior-health-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-white-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-horizontal-jpg': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-interior-health-interior-health-2004-letterhead-png': 'vector-interior-health-blue-horizontal-source-extraction',
  'source-provincial-health-services-authority-phsa-png': 'vector-phsa-black-source-extraction',
  'source-bc-heritage-trust-bc-heritage-trust-1989-logo-png': 'historical-bc-heritage-trust-2002',
  'source-forest-renewal-bc-forest-renewal-bc-1999-original-png': 'vector-forest-renewal-bc-1999-black-source-vector',
  // A third-party vector of the design the Corporation's own reports give as original paths.
  'source-forest-renewal-bc-forest-renewal-bc-supplied-vector-svg': 'vector-forest-renewal-bc-2000-colour-source-vector',
  'source-oil-and-gas-commission-bc-oil-gas-commission-2021-jpeg': 'vector-bc-oil-gas-commission-2014',
  'source-oil-and-gas-commission-bc-oil-gas-commission-2019-jpeg': 'vector-bc-oil-gas-commission-2014',
  'source-partnerships-bc-partnerships-bc-2006-logo-crop-png': 'vector-partnerships-bc-2012',
  'source-pacific-carbon-trust-pacific-carbon-trust-2013-png': 'source-pacific-carbon-trust-pacific-carbon-trust-2013-svg',
  'source-capital-health-region-capital-health-region-2000-letterhead-png': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-2000-original-colour': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-2000-original-greyscale': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-1999-january-newspaper-raster': 'historical-capital-health-region-2000-dark-grey',
  'historical-capital-health-region-1999-october-letterhead-raster': 'historical-capital-health-region-2000-dark-grey',
  'source-central-vancouver-island-health-region-central-vancouver-island-health-region-1999-png': 'source-central-vancouver-island-health-region-central-vancouver-island-health-region-1999-svg',
  // The hybrid SVG wraps the same low-resolution wordmark as the complete image, which is kept.
  'source-north-okanagan-health-region-north-okanagan-health-region-2000-hybrid-svg': 'source-north-okanagan-health-region-north-okanagan-health-region-2000-png',
  'source-northern-interior-regional-health-board-northern-interior-regional-health-board-2001-png': 'historical-northern-interior-regional-health-board-blue-2001',
  // The reconstruction keeps the Power Pioneers image as its source download.
  'source-bc-power-commission-bc-power-commission-original-logo-jpg': 'bc-power-commission-rebuilt',
  'source-bc-place-ltd-bc-place-1983-logo-png': 'bc-place-1983-rebuilt',
  'source-bc-systems-corporation-bc-systems-1983-logo-png': 'bcsc-1983-white',
  'shared-services-bc-2010-letterhead': 'shared-services-bc-2006-07',
  // The two scans are kept as the logos' downloads.
  'source-bc-petroleum-corporation-bc-petroleum-1983-logo-png': 'bcpc-stacked-white',
  'historical-bc-petroleum-1992-symbol-raster': 'bcpc-emblem-black',
  // The report's 78-pixel image is kept as the emblem's download.
  'source-fraser-valley-health-region-fraser-valley-health-region-2000-jpg': 'fvhr-emblem-colour',
  // The 2003 document's image is kept as the vector's download.
  'solutions-bc-2003': 'solutions-bc-2003-vector',
  // The website's PNG, without the PHSA line, is kept as the vector's download.
  'bc-cancer-logo': 'bc-cancer-phsa'
}

// Another colourway of the same design: shown inside the design's entry as a version to switch
// to, rather than as a separate mark.
const VARIANT_OF = {
  'vector-ticorp-2020-reversed-source-vector': 'vector-ticorp-2025-colour-source-vector',
  'vector-infrastructure-bc-2026-reversed-source-vector': 'vector-infrastructure-bc-2026-colour-source-vector',
  'vector-community-living-bc-2014-reversed-source-vector': 'vector-community-living-bc-2023-colour-source-vector',
  'source-knowledge-network-knowledge-network-svg': 'source-knowledge-network-knowledge-network-colour-eps',
  'vector-pavco-2023-reversed-source-vector': 'vector-pavco-2025-26-colour-source-vector',
  'vector-phsa-white-source-extraction': 'vector-phsa-black-source-extraction',
  'vector-fnha-logo-white': 'vector-fnha-logo-colour',
  'source-first-nations-health-authority-fnha-white-png': 'source-first-nations-health-authority-fnha-horizontal-png',
  'vector-forest-renewal-bc-1999-black-source-vector': 'vector-forest-renewal-bc-2000-colour-source-vector',
  'historical-capital-health-region-2000-dark-white': 'historical-capital-health-region-2000-dark-grey',
  'source-innovate-bc-innovate-bc-white-eps': 'innovate-bc-2024-colour',
  'bcr-dogwood-dark': 'bcr-dogwood-white',
  'bcsc-1983-black': 'bcsc-1983-white',
  'jibc-logo-reversed': 'jibc-logo',
  'bcpc-stacked-black': 'bcpc-stacked-white',
  'bcpc-emblem-white': 'bcpc-emblem-black',
  'bc-housing-houses-white': 'bc-housing-houses',
  'fvhr-emblem-black': 'fvhr-emblem-colour',
  'solutions-bc-2003-black': 'solutions-bc-2003-vector',
  'bc-cancer-research-white': 'bc-cancer-research',
  'bc-cancer-foundation-2018-white': 'bc-cancer-foundation-2018',
  'bc-cancer-foundation-2026-white': 'bc-cancer-foundation-2026'
}

// What each version is called inside its design's entry.
const VERSION_LABELS = {
  'vector-ticorp-2025-colour-source-vector': 'Full colour',
  'vector-ticorp-2020-reversed-source-vector': 'White',
  'vector-infrastructure-bc-2026-colour-source-vector': 'Full colour',
  'vector-infrastructure-bc-2026-reversed-source-vector': 'Reversed',
  'vector-community-living-bc-2023-colour-source-vector': 'Full colour',
  'vector-community-living-bc-2014-reversed-source-vector': 'Reversed',
  'source-knowledge-network-knowledge-network-colour-eps': 'Full colour',
  'source-knowledge-network-knowledge-network-svg': 'White lettering',
  'vector-pavco-2025-26-colour-source-vector': 'Full colour',
  'vector-pavco-2023-reversed-source-vector': 'White',
  'vector-phsa-black-source-extraction': 'Black',
  'vector-phsa-white-source-extraction': 'White',
  'vector-fnha-logo-colour': 'Full colour',
  'vector-fnha-logo-white': 'White lettering',
  'source-first-nations-health-authority-fnha-horizontal-png': 'Full colour',
  'source-first-nations-health-authority-fnha-white-png': 'White',
  'vector-forest-renewal-bc-2000-colour-source-vector': 'Full colour',
  'vector-forest-renewal-bc-1999-black-source-vector': 'Black',
  'historical-capital-health-region-2000-dark-grey': 'Dark and grey',
  'historical-capital-health-region-2000-dark-white': 'Dark and white',
  'innovate-bc-2024-colour': 'Full colour',
  'source-innovate-bc-innovate-bc-white-eps': 'White',
  'bcr-dogwood-white': 'White lettering',
  'bcr-dogwood-dark': 'Dark lettering',
  'bcsc-1983-white': 'White (as printed)',
  'bcsc-1983-black': 'Black',
  'jibc-logo': 'On white',
  'jibc-logo-reversed': 'Reversed (as supplied)',
  'bcpc-stacked-white': 'White (as printed)',
  'bcpc-stacked-black': 'Black',
  'bcpc-emblem-black': 'Black (as printed)',
  'bcpc-emblem-white': 'White',
  'bc-housing-houses': 'Black',
  'bc-housing-houses-white': 'White',
  'fvhr-emblem-colour': 'Colour',
  'fvhr-emblem-black': 'Black',
  'solutions-bc-2003-vector': 'On teal (as printed)',
  'solutions-bc-2003-black': 'Black',
  'bc-cancer-research': 'Colour',
  'bc-cancer-research-white': 'White and purple',
  'bc-cancer-foundation-2018': 'Colour',
  'bc-cancer-foundation-2018-white': 'White and purple',
  'bc-cancer-foundation-2026': 'Navy and purple',
  'bc-cancer-foundation-2026-white': 'White and purple'
}

// Shorter accounts where a body's or file's own record is about a file no longer shown.
const BODY_NOTES = {
  'fraser-valley-health-region': 'The region’s flower of blue and green petals around a white cross, from a September 2000 project report it shared with the BC Cancer Agency, and a printed header with its slogan, “Integrating Health Care”. Leads for its original artwork: recruitment advertisements in Canadian Nurse, June 1998 and May 2000 (vol. 96, no. 5, pp. 46 and 49). Amalgamated into the Fraser Health Authority in December 2001.',
  'provincial-rental-housing-corporation': 'No separate PRHC logo or readable seal has been found. Incorporated in 1961 as Pemco Holdings Ltd., renamed British Columbia Housing Corporation and then, in December 1976, Provincial Rental Housing Corporation. It holds land and has no staff; BC Housing acts for it, and its correspondence and signage carry BC Housing’s identity. Its own reports use plain name headings. Leads: BC Housing’s PRHC land files and CMHC’s British Columbia files at Library and Archives Canada.',
  'bc-petroleum-corporation': 'The Crown corporation that bought and sold the province’s natural gas from 1973. Its curled-flame emblem, alone and over its four-line name, from its 1982/83 and 1991/92 annual reports.',
  'bc-systems-corporation': 'The Province’s shared computing corporation, from 1977. Its operations moved into government in 1996 and it was dissolved in 2000; its role continues in today’s Connected Services BC.',
  'bc-railway-company': 'Its wordmark is the BCRC acrostic — British Columbia Railway Company stepped down on four lines, with the initials in red — seen in three letterings: the heavier one on its website, and the wide Eurostile of the 2024 report’s cover and the Verdana of its letterhead.',
  'bc-place-ltd': 'The Crown company that built BC Place Stadium (opened 1983) on the False Creek lands that later held Expo 86. Renamed BC Enterprise Corporation in 1987; its assets passed to PavCo in 1989.',
  'bc-power-commission': 'The public utility that brought power to communities outside BC Electric’s territory from 1945, and one of BC Hydro’s two predecessors (established 1962, amalgamated 1965). Its emblem was on the commission’s red service trucks.',
  'bc-steamship-company': 'The Crown company that ran the Princess Marguerite between Victoria and Seattle from 1975. It sold its ships in 1988 and was renamed Victoria Line Ltd. in 1994.',
  'transportation-investment-corporation': 'One design in full colour and white, both original vector artwork from Pattullo Bridge Replacement Project publications.',
  'bc-housing': 'The British Columbia Housing Management Commission, known as BC Housing, since 1967: its house-shaped BC of 1978, the illustrated houses it registered as a trademark (advertised 2010), and today’s emblem from its 2015 rebrand, with the Research Centre lockup.',
  'bc-assessment': 'The full-colour logo from the official media kit: an SVG converted from its EPS, with the EPS itself as the original download.',
  'columbia-power': 'The logo as original vector artwork, reversed, from the 2024 history book.',
  'infrastructure-bc': 'One design in full colour and reversed, both original vector artwork from the Spring 2026 brochure.',
  'community-living-bc': 'One design in full colour and reversed, both original vector artwork from its 2014 and 2023 reports.',
  'knowledge-network': 'One design, in full colour and with white lettering, as vector artwork from the official brand kit.',
  'bc-pavilion-corporation': 'One design in full colour and in white, both original vector artwork from PavCo’s own publications.',
  'forest-enhancement-society': 'The horizontal and vertical logos from the official 2026 logo kit, as vector artwork, and the 10th-anniversary logo.',
  'innovate-bc': 'One logo, the disc with its i over “innovate BC”: in full colour from the 2024/2025 Impact Report (vector, with the report’s star-trail photograph in the disc), and in white as vector artwork from the official brand kit.',
  'bc-family-maintenance-agency': 'The logo as original vector artwork from the 2020/21 annual report.',
  'inbc': 'The logo as vector artwork from the official website.',
  'bc-council-for-international-education': 'The logo as original vector artwork from the 2022–2025 strategic plan.',
  'interior-health': 'The horizontal logo as original vector artwork, seen on a June 2004 letterhead and in a 2023 roadmap, with the stacked logo and the symbol as published images.',
  'provincial-health-services-authority': 'One design in black and in white, as original vector artwork.',
  'bc-heritage-trust': 'The boxed Trust mark as original vector artwork from the 2001/02 annual report; the same mark is on its 1989 conservation publication.',
  'forest-renewal-bc': 'One design in full colour and black, both original vector artwork from the Corporation’s 1999 and 2000 publications.',
  'oil-and-gas-commission': 'The corporate mark as original vector artwork from the 2014 annual report; the same mark is on official PDFs of 2019 and 2021.',
  'partnerships-bc': 'The wordmark as original vector artwork from the 2012/13 annual report; the same wordmark is in the 2006 service plan.',
  'capital-health-region': 'Capital Health Region of Victoria. One design in two original vector versions from 2000 publications, the same mark as on its 1999 and 2000 letterheads and newspaper notices. Dates identify appearances, not adoption.',
  'central-vancouver-island-health-region': 'The March 2002 report The World Without Linen Bags reproduces authentic 1999 letterheads. The full logo uses original PDF vector paths and glyph outlines, not a new trace. A grayscale emblem is also preserved from an embedded source image. Letter dates are sightings; no adoption date is asserted.',
  'north-okanagan-health-region': 'The NOHR emblem and acronym wordmark from the June 2000 report cover. The emblem alone is original vector; the full logo survives only as an image, its wordmark very small (46 × 22 px). No font substitution or traced wordmark supplied.',
  'northern-interior-regional-health-board': 'Original blue vector emblem and full name from the July 2001 annual report; the same mark is on an April 2001 organizational chart. Dates identify source appearances, not first use.'
}
// Display labels for files whose inventory label says how they were made; that stays in the record
// (reconstruction: true), not on the page.
const ASSET_LABELS = {
  'source-urban-transit-authority-urban-transit-authority-png': 'Urban Transit Authority — signature',
  'source-expo-86-corporation-expo86-symbol-svg': 'Expo 86 — symbol',
  'source-expo-86-corporation-expo86-wordmark-svg': 'Expo 86 — wordmark',
  'source-fraser-valley-health-region-fraser-valley-health-region-2000-jpg': 'Fraser Valley Health Region — Flower and cross'
}
const ASSET_NOTES = {
  'source-urban-transit-authority-urban-transit-authority-png': 'The Urban Transit Authority’s signature, drawn in 2020 by Colin Stepney (Cjstepney); a contemporary original is still wanted.',
  'source-expo-86-corporation-expo86-symbol-svg': 'The Expo 86 symbol, as drawn for Wikimedia Commons from merchandise photographs.',
  'source-expo-86-corporation-expo86-wordmark-svg': 'The Expo 86 wordmark, as drawn for Wikipedia in 2008.',
  'source-fraser-valley-health-region-fraser-valley-health-region-2000-jpg': 'Four petals in blue and green around a white cross, from the cover of the Fraser Valley Health Centre / Eastern Fraser Valley Cancer Centre project report of September 2000. The report embeds it at only 78 pixels square.',
  'vector-ticorp-2025-colour-source-vector': 'The BC emblem, a gold divider and the name on three lines, as original vector paths from page 1 of the Pattullo Bridge Replacement Project’s Summer 2025 project update. The PDF’s print colours are converted to sRGB.',
  'vector-ticorp-2020-reversed-source-vector': 'The publication’s own white version, as original vector paths from the back cover of the Spring 2020 project overview. Its blue page is left out, so it needs a dark ground.'
}

/** A register entry as the inventory's asset record, so both read the same in the gallery. */
const fromRegister = (entry, search = 'vector-search-2026-10-30') => {
  if (!LABELS[entry.id]) throw new Error(`No label for ${entry.id}`)
  if (!entry.genuineVectorVerified || entry.validation?.embeddedImages || entry.validation?.textElements || entry.validation?.externalResources?.length) {
    throw new Error(`Not verified as pure vector: ${entry.id}`)
  }
  const original = entry.sourceBytesUnchanged
  return checked({
    id: `vector-${entry.id}`,
    label: `${entry.organization} — ${LABELS[entry.id]}`,
    file: `identity-collected/${entry.bodyId}/${basename(entry.file)}`,
    format: 'svg',
    isVector: true,
    supplied: false,
    reconstruction: false,
    publisher: entry.publisher ?? entry.organization,
    sourcePage: entry.sourcePageUrl ?? entry.sourceUrl,
    sourceUrl: entry.sourceUrl,
    sourceLocator: entry.sourcePdfPage ? `PDF page ${entry.sourcePdfPage}` : entry.sourcePackageEntry ?? null,
    sourceFile: entry.sourceTitle ?? null,
    sourceDate: entry.sourceDate ?? null,
    dateNote: entry.dateMeaning ?? '',
    observedDate: entry.retrievedDate,
    evidenceType: original ? 'official-svg-download' : 'native-pdf-vector-extraction',
    notes: entry.notes,
    fidelityNote: original
      ? 'Published SVG retained byte for byte, checked for real geometry and no embedded images or text, and rendered. Its source is linked below.'
      : `${entry.provenance} ${entry.method ?? ''}`.trim(),
    sha256: entry.sha256,
    bytes: entry.bytes,
    darkBackground: Boolean(entry.darkBackgroundRecommended),
    ...(entry.timelineId ? { timelineEra: entry.timelineId } : {}),
    search
  })
}

const additions = new Map()
for (const entry of register.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry))
}
for (const entry of ticorp.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry, 'ticorp-vector-2026-11-08'))
}
for (const entry of followup.assets) {
  if (!additions.has(entry.bodyId)) additions.set(entry.bodyId, [])
  additions.get(entry.bodyId).push(fromRegister(entry, 'vector-followup-2026-11-08'))
}

// The Department of Travel Industry's, on the Province's own timeline (gallery collection "bc-mark"),
// and the Justice Institute's, a public body outside the inventory's Crown corporations.
for (const { search, register: packaged } of PROGRAM_PACKAGES) for (const { verification, ...asset } of packaged.assets) {
  if (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  if (!additions.has(packaged.program)) additions.set(packaged.program, [])
  additions.get(packaged.program).push(checked({ ...asset, search }))
}

// Historical specimens use inventory-shaped records; detailed extraction evidence stays in
// their source register rather than in the gallery bundle. They must name an inventory body.
const bodyIds = new Set(inventory.bodies.map((body) => body.id))
// Supplied images of marks with no vector: kept as images, and said to be.
for (const { bodyId, ...asset } of railSightings.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown body: ${bodyId}`)
  if (asset.isVector || !asset.supplied) throw new Error(`Expected a supplied image: ${asset.id}`)
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search: 'bc-rail-sightings-2026-11-12' }))
}
// A program's published image, kept as published.
for (const [search, register] of [['bceid-2026-11-12', bceid], ['shared-services-bc-2026-11-12', sharedServices], ['bc-cancer-current-2026-11-12', bcCancerNow]]) for (const asset of register.assets) {
  if (asset.isVector) throw new Error(`Expected an image: ${asset.id}`)
  if (!additions.has(register.program)) additions.set(register.program, [])
  additions.get(register.program).push(SUPERSEDED[asset.id] ? asset : checked({ ...asset, search }))
}
for (const { bodyId, verification, ...asset } of innovate.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown body: ${bodyId}`)
  // Vector paths over the report's own photograph, so not pure vector, and recorded as such.
  if (asset.isVector || verification?.textElements !== 0 || verification.externalResources?.length !== 0) {
    throw new Error(`Unexpected record for ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search: 'innovate-bc-vector-2026-11-12' }))
}
for (const { search, register: packaged } of PACKAGES) for (const { bodyId, verification, ...asset } of packaged.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown body: ${bodyId}`)
  if (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  for (const extra of asset.downloads ?? []) checked({ file: extra.file, sha256: extra.sha256 })
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  additions.get(bodyId).push(checked({ ...asset, search }))
}
for (const { bodyId, verification, ...asset } of historical.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body: ${bodyId}`)
  if (asset.isVector && (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0)) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  // A superseded file is not shown, so its file need not be held.
  const record = { ...asset, search: 'historical-vector-followup-2026-10-30' }
  additions.get(bodyId).push(SUPERSEDED[asset.id] ? record : checked(record))
}
for (const bodyId of Object.keys(historical.bodyUpdates)) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown historical body update: ${bodyId}`)
}
// The railway history's acquisitions (PGE and BC Rail source crops), read as the historical ones are.
for (const { bodyId, verification, ...asset } of railway.assets) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown railway body: ${bodyId}`)
  if (asset.isVector && (!verification?.genuineVectorVerified || verification.embeddedImages !== 0 || verification.textElements !== 0 || verification.externalResources?.length !== 0)) {
    throw new Error(`Not verified as pure vector: ${asset.id}`)
  }
  if (!additions.has(bodyId)) additions.set(bodyId, [])
  const record = { ...asset, search: 'railway-history-2026-11-12' }
  additions.get(bodyId).push(SUPERSEDED[asset.id] ? record : checked(record))
}
for (const bodyId of Object.keys(railway.bodyUpdates)) {
  if (!bodyIds.has(bodyId)) throw new Error(`Unknown railway body update: ${bodyId}`)
}

// Dates of the files each kept file stands for, as further sightings of its design.
const alsoSeenOf = (all, id) => all.filter((asset) => SUPERSEDED[asset.id] === id && asset.sourceDate)
  .map((asset) => ({ date: asset.sourceDate, source: asset.sourcePage || asset.sourceUrl || null }))
const kept = (assets) => assets.filter((asset) => !SUPERSEDED[asset.id])
  .map((asset) => {
    const alsoSeen = alsoSeenOf(assets, asset.id)
    return alsoSeen.length ? { ...asset, alsoSeen } : asset
  })
const finished = (asset) => ({
  ...asset,
  ...(ASSET_NOTES[asset.id] ? { notes: ASSET_NOTES[asset.id] } : {}),
  ...(ASSET_LABELS[asset.id] ? { label: ASSET_LABELS[asset.id] } : {}),
  ...(VERSION_LABELS[asset.id] ? { versionLabel: VERSION_LABELS[asset.id] } : {}),
  ...(VARIANT_OF[asset.id] ? { variantOf: VARIANT_OF[asset.id] } : {})
})

// Where later research changed a body's years: the Steamship Company was renamed in 1994, not
// dissolved in 1992, and its legal end is untraced.
const BODY_DATES = {
  'bc-steamship-company': { to: null },
  // Operations passed to government in 1996; the corporation was dissolved on 30 April 2000.
  'bc-systems-corporation': { to: 2000 }
}

const bodies = inventory.bodies.map((body) => {
  const { queries, researchSources, ...display } = body
  for (const asset of kept(display.assets)) checked(asset)
  const added = additions.get(body.id) ?? []
  additions.delete(body.id)
  const record = added.length ? {
    ...display,
    ...historical.bodyUpdates[body.id],
    ...railway.bodyUpdates[body.id],
    status: 'asset-collected',
    assets: [...display.assets, ...added]
  } : display
  return {
    ...record,
    ...(BODY_NOTES[body.id] ? { notes: BODY_NOTES[body.id] } : {}),
    ...BODY_DATES[body.id],
    assets: kept(record.assets).map(finished)
  }
})
// What is left belongs to the one-off programs, which are timelines rather than inventory bodies.
const specimens = [...additions].map(([program, assets]) => ({ program, assets: kept(assets).map(finished) }))

for (const [id, keeper] of Object.entries({ ...SUPERSEDED, ...VARIANT_OF })) {
  const ids = new Set([...bodies, ...specimens].flatMap((each) => each.assets.map((asset) => asset.id)))
  if (!ids.has(keeper) || (VARIANT_OF[id] && !ids.has(id))) throw new Error(`Unknown consolidation: ${id} → ${keeper}`)
}

const seenIds = new Set()
const seenFiles = new Set()
for (const { assets } of [...bodies, ...specimens]) for (const asset of assets) {
  if (seenIds.has(asset.id) || seenFiles.has(asset.file)) throw new Error(`Duplicate collected asset: ${asset.id} (${asset.file})`)
  seenIds.add(asset.id)
  seenFiles.add(asset.file)
}

// Decorative scenes, liveries and application photos have provenance and checksums too,
// but never become adopted-logo entries merely because they were cropped from a source.
const contextByFile = new Map(railway.contextAssets.map((asset) => [asset.file, checked(asset)]))
for (const item of railwayHistory.evidence) {
  if (!contextByFile.has(item.file) || seenFiles.has(item.file)) {
    throw new Error(`Railway context is missing or counted as a logo: ${item.file}`)
  }
  contextByFile.delete(item.file)
}
if (contextByFile.size) throw new Error('Unassigned railway supporting images')
const railwayIds = new Set(bodies.filter((body) => ['pacific-great-eastern-railway', 'bc-railway-company'].includes(body.id))
  .flatMap((body) => body.assets.map((asset) => asset.id)))
const railwayVersions = bodies.flatMap((body) => body.assets).filter((asset) => asset.variantOf)
for (const era of railwayHistory.eras) for (const id of era.assetIds ?? []) {
  if (!railwayIds.delete(id)) throw new Error(`Missing or repeated railway logo: ${id}`)
  // A design's other colourways go with it.
  for (const version of railwayVersions) if (version.variantOf === id) railwayIds.delete(version.id)
}
if (railwayIds.size) throw new Error(`Railway logos without a design group: ${[...railwayIds].join(', ')}`)

writeFileSync(new URL('src/gallery/railwayHistoryData.js', root),
  '// Generated by scripts/build-collected-marks.mjs from the sourced railway history.\n' +
  '// Design dates, reproduction dates and corporate events remain separate.\n' +
  `export const RAILWAY_HISTORY = ${JSON.stringify(railwayHistory, null, 2)}\n`)

writeFileSync(new URL('src/gallery/collectedData.js', root),
  '// Generated by scripts/build-collected-marks.mjs from the source-linked acquisition inventory.\n' +
  '// Logo dates are recorded separately from organization dates.\n' +
  `export const COLLECTED_BODIES = ${JSON.stringify(bodies, null, 2)}\n` +
  '// Published vector specimens of the one-off programs, by the timeline each belongs to.\n' +
  `export const COLLECTED_SPECIMENS = ${JSON.stringify(specimens, null, 2)}\n`)
console.log(`Wrote ${bodies.length} research records, ${bodies.reduce((sum, body) => sum + body.assets.length, 0)} body assets and ${specimens.reduce((sum, each) => sum + each.assets.length, 0)} program specimens to ${fileURLToPath(new URL('src/gallery/collectedData.js', root))}`)
