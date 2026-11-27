// Reviewed versions of one drawing. Keep every published file and its own evidence.
// Each first ID is the existing design page. Subsequent IDs still open their named version.
const groups = [
  {
    title: 'Pouce Coupe landscape and wheat signature',
    versions: {
      'source-recovered-municipal-pouce-coupe-website-logo': 'Municipal website',
      'pouce-coupe-guide-2015': '2015 travel guide'
    }
  },
  {
    title: 'BC Parks Foundation business card back',
    versions: {
      'bcpf-study-card-inlet': 'Coast',
      'bcpf-study-card-valley': 'Valley'
    }
  },
  {
    title: 'Island Health signature',
    darkVariant: 'source-island-health-island-health-white-svg',
    versions: {
      'source-island-health-island-health-svg': 'Full colour',
      'source-island-health-island-health-white-svg': 'White'
    }
  },
  {
    title: 'Legal Aid BC horizontal logo',
    versions: {
      'source-legal-aid-bc-legal-aid-bc-horizontal-svg': 'Logo kit',
      'source-legal-aid-bc-legal-aid-bc-svg': 'Website'
    }
  },
  {
    title: 'Port Hardy community logo',
    versions: {
      'source-recovered-municipal-port-hardy-website-monochrome-logo': 'Monochrome SVG',
      'source-recovered-municipal-port-hardy-website-logo': 'Full-colour PNG'
    }
  },
  {
    title: 'BCLC with “playing it right”',
    darkVariant: 'vector-bclc-2011-reversed-tagline-source-vector',
    versions: {
      'vector-bclc-2009-colour-tagline-source-vector': 'Colour · 2009',
      'vector-bclc-2011-reversed-tagline-source-vector': 'Reverse · 2010/11'
    }
  },
  {
    title: 'Pacific Carbon Trust stacked mark',
    versions: {
      'pacific-carbon-trust-2011-vector': '2011 service plan',
      'source-pacific-carbon-trust-pacific-carbon-trust-2013-svg': '2013 service plan',
      'source-pacific-carbon-trust-pacific-carbon-trust-2009-jpeg': '2009 report'
    }
  },
  {
    title: 'Power Smart wordmark',
    versions: {
      'source-recovered-power-smart-reversed-wordmark': 'Forum brochure SVG',
      'source-recovered-power-smart-cipo-specimen': 'Official mark specimen'
    }
  },
  {
    title: 'Interior University Society print mark',
    darkVariant: 'ius-ius-print-white',
    versions: {
      'ius-ius-print-colour': 'Colour',
      'ius-ius-print-black': 'Black',
      'ius-ius-print-white': 'White',
      'ius-ius-print-reversed-panel': 'White on dark panel'
    }
  },
  {
    title: 'North Shore Health Region boxed signature',
    versions: {
      'north-shore-health-region-annual-report-2000': 'Green · annual report SVG',
      'source-north-shore-health-region-north-shore-health-region-1999-png': 'Green · published image',
      'north-shore-health-region-reversed-rebuilt': 'Reverse · reconstruction',
      'historical-north-shore-health-region-trail-reversed-raster': 'Reverse · published image'
    }
  },
  {
    title: 'Simon Fraser Health Region signature',
    versions: {
      'simon-fraser-health-region-colour-rebuilt': 'Colour · reconstruction',
      'simon-fraser-health-region-monochrome-rebuilt': 'Monochrome · reconstruction',
      'historical-simon-fraser-health-region-original-web-colour-2001': '2001 website',
      'historical-simon-fraser-health-region-continuum-2001-monochrome': '2001 monochrome specimen',
      'source-simon-fraser-health-region-simon-fraser-health-region-board-letterhead-1997-png': '1997 letterhead',
      'source-simon-fraser-health-region-simon-fraser-health-region-2003-png': '2003 recruitment ad'
    }
  },
  {
    title: 'Vancouver/Richmond Health Board signature',
    versions: {
      'vancouver-richmond-health-board-original-colour-lockup': 'Full-colour signature',
      'source-vancouver-richmond-health-board-vancouver-richmond-health-board-2001-png': 'June 2001 report cover',
      'historical-vancouver-richmond-health-board-tmj-2001': '2001 official mark',
      'historical-vancouver-richmond-health-board-2001-visions-raster': 'Fall/Winter 2001 print'
    }
  },
  {
    title: 'Campbell River/Nootka council emblem',
    versions: {
      'campbell-river-nootka-chc-rebuilt': 'Vector reconstruction',
      'source-campbell-river-nootka-community-health-council-campbell-river-nootka-health-council-2002-png': '2002 festival programme'
    }
  }
]

const reviewed = new Map()
for (const { title, versions, darkVariant } of groups) {
  const [designId] = Object.keys(versions)
  for (const [id, versionLabel] of Object.entries(versions)) {
    reviewed.set(id, id === designId
      ? { designLabel: title, versionLabel, ...(darkVariant && { darkVariant }) }
      : { variantOf: designId, versionLabel })
  }
}

const publishedReverses = {
  'innovate-bc-2024-colour': 'source-innovate-bc-innovate-bc-white-eps',
  'source-expanded-coast-mountain-bus-company-route-map-logo': 'source-vector-coast-mountain-bus-company-2022-white',
  'school-district-84-logo-current': 'school-district-84-strategic-plan-reverse',
  'school-district-93-sd093-observed-2010-2011': 'school-district-93-illustrated-book-annual-report-reverse'
}
for (const [id, darkVariant] of Object.entries(publishedReverses)) {
  reviewed.set(id, { ...reviewed.get(id), darkVariant })
}

export const groupSpecimen = (asset) => reviewed.has(asset.id) ? { ...asset, ...reviewed.get(asset.id) } : asset
