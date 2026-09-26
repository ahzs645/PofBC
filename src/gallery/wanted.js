// Marks the gallery does not have yet, shown so that their absence is not mistaken for anything else.
//
// A gallery that simply leaves a body out reads as though the body had no mark, or as though its
// mark did not matter. These are the Crown corporations and agencies whose artwork has been looked
// for and not obtained: each says what has been verified about the route to it, and what would
// have to happen next. None has artwork, and none is drawn — a card for one of these that showed a
// logo would be exactly the unverified asset the research warns against.
//
// Copied by hand from the research companion package (tmp/research/package/logo_acquisition.json,
// "British Columbia government atlas — research companion", as of 2026-09-25), with its source ids
// kept so each can be traced back to sources.json there. Nothing is fetched: the contact routes are
// the package's, recorded as text, not links this site follows.

/**
 * What the package found about each body's artwork. Every status here means the same thing on the
 * card — no original artwork has been obtained — and differs only in how far the route to it goes.
 */
export const ASSET_STATUS = {
  no_vector_master_verified: 'No master artwork verified',
  request_route_verified: 'A route to request it is verified',
  chronology_verified_artwork_pending: 'Its dates are verified; the artwork is pending'
}

export const WANTED_AS_OF = '2026-09-25'

export const WANTED = [
  {
    id: 'icbc',
    source: 'L01',
    label: 'ICBC',
    body: 'Crown corporation',
    graphNode: 'icbc',
    sourceIds: ['S17', 'S18', 'S19'],
    verified: 'Official newsroom and editorial gallery',
    assetStatus: 'no_vector_master_verified',
    contact: 'Use the newsroom’s media contacts',
    nextAction: 'Request current corporate master and earlier wordmarks, brand guidelines, first-use ' +
      'evidence and historical-display permission.',
    warning: 'Approved photographs are not a confirmed SVG logo pack.'
  },
  {
    id: 'bclc',
    source: 'L02',
    label: 'BCLC',
    body: 'Crown corporation',
    graphNode: 'bclc',
    sourceIds: ['S20', 'S21'],
    verified: 'Official media centre and media terms',
    assetStatus: 'no_vector_master_verified',
    contact: 'mediarelations@bclc.com',
    nextAction: 'Request BCLC corporate and earlier identity masters, with documented era dates; separate ' +
      'corporate and lottery/game brands.',
    warning: 'The photo gallery is not evidence of a logo asset or unrestricted reuse rights.'
  },
  {
    id: 'bc-ferries',
    source: 'L03',
    label: 'BC Ferries',
    body: 'Crown corporation until 2003',
    // The diagram has the Crown corporation, which ended in 2003; the company that followed it is not
    // a public body, so the link goes to the years it was one.
    graphNode: 'bc-ferry-corporation',
    sourceIds: ['S22'],
    verified: 'Official media library and media contact',
    assetStatus: 'no_vector_master_verified',
    contact: 'media@bcferries.com',
    nextAction: 'Request current corporate and historical marks; distinguish the corporation, vessel ' +
      'liveries and government-era identity.',
    warning: 'A current logo does not establish historical legal status or date of adoption.'
  },
  {
    id: 'bc-transit',
    source: 'L04',
    label: 'BC Transit',
    body: 'Crown corporation',
    graphNode: 'bc-transit',
    sourceIds: ['S16'],
    verified: 'Explicit instructions to request the corporate logo for media use',
    assetStatus: 'request_route_verified',
    contact: 'media@bctransit.com',
    nextAction: 'Request original vector and brand guide, including historical versions and permission ' +
      'appropriate to this atlas.',
    warning: 'No logo file or project-specific permission was obtained in this pass.'
  },
  {
    id: 'worksafebc',
    source: 'L05',
    label: 'WorkSafeBC',
    body: 'Workers’ Compensation Board · agency',
    graphNode: 'workers-compensation-board',
    sourceIds: ['S13', 'S14', 'S15'],
    verified: 'Official 1968 and 1983 logo dates, 1974 legal-name and 2005 operating-name milestones',
    assetStatus: 'chronology_verified_artwork_pending',
    contact: 'Use the organization’s official Contact Us route',
    nextAction: 'Request original artwork for the 1968, 1983 and WorkSafeBC eras; retain ' +
      'legal-name/operating-name separation.',
    warning: 'Year-level chronology is not equivalent to a verified vector master or exact rollout interval.'
  }
]
