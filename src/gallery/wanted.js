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
//
// ICBC (L01), BCLC (L02) and BC Ferries (L03) were on this list until their logo histories arrived
// (research/identity/, 2026-09-27); they are collections in the gallery now. No package is an
// official master, so the routes the companion recorded for them still stand: ICBC through its
// newsroom's media contacts, BCLC through mediarelations@bclc.com, BC Ferries through
// media@bcferries.com.

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
