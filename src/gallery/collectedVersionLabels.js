// What each version's button says on a design's page, for the files whose own records name none.
//
// A design with more than one file shows a button per file; a file without a version label left its
// button blank. Each label says how the file differs from the others in its design and where it was
// taken from, in the words its sibling files already use. A record that names its own label keeps it.
export const COLLECTED_VERSION_LABELS = {
  // Ministry of Environment, the flag-years mark.
  'bc-environment-flag-years': 'Dark ink · upright',
  'bc-environment-flag-years-cream': 'Cream · for a dark ground',
  'bc-environment-flag-years-cover-band': 'Cream on the cover’s green band',
  // Ministry of Tourism, Recreation and Culture.
  'tourism-recreation-culture-1986': 'Blue-violet, as printed',
  'tourism-recreation-culture-1986-black': 'Black',
  // SuperHost, as the newspaper and the trademark specimen arrange it.
  'superhost-1986': 'Black · newspaper',
  'superhost-1986-colour': 'Flag in colour · newspaper',
  'superhost-1986-cipo': 'Black · trademark specimen',
  'superhost-1986-cipo-colour': 'Flag in colour · trademark specimen',
  'bc-place-1983-rebuilt': 'Vector reconstruction · 1983 gala programme',
  'islands-trust-2006': 'Colour · 2005–06 annual report',
  'yxs-airport-2012': 'Image · 2012 travel guide',
  'source-expanded-translink-website-logo': 'Colour · website SVG',
  'source-expanded-skytrain-toolkit-wordmark': 'Colour · 2026 toolkit',
  'source-expanded-coast-mountain-bus-company-route-map-logo': 'Image · 2017 route map',
  'municipal-chilliwack-climate-actions-summary-stacked': 'Stacked · 2022 climate actions summary',
  'municipal-coquitlam-treasury-report-2025': 'Blue · 2025 Treasury Report',
  'municipal-quesnel-brand-guidelines-2016-compact': 'Compact · 2016 brand guidelines',
  'municipal-smithers-new-residents-guide-2026': 'Stacked · 2026 resident guide',
  'municipal-smithers-new-residents-guide-2026-tagline-white': 'White with tagline · 2026 resident guide',
  'source-municipal-vanderhoof-website-logo': 'Full colour · website SVG',
  'source-municipal-vanderhoof-website-logo-white': 'White · website SVG',
  'sd46-primary-black': 'Black · brand-guide SVG',
  'sd46-tagline-black': 'Black · brand-guide SVG',
  'sd46-simplified-black': 'Black · brand-guide SVG',
  'school-district-57-logo-current': 'Current logo · image',
  'school-district-64-logo-current': 'Website image · PNG',
  'sd64-wordmark-2023-native': 'Colour · brand-guide SVG',
  'school-district-82-logo-current': 'Website icon · PNG',
  'school-district-83-logo-current': 'Website logo · PNG'
}

/** A file with the version label its button shows, where its own record names none. */
export const withVersionLabel = (asset) => asset.versionLabel || !COLLECTED_VERSION_LABELS[asset.id]
  ? asset
  : { ...asset, versionLabel: COLLECTED_VERSION_LABELS[asset.id] }
