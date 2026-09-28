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
// All five of its bodies — ICBC (L01), BCLC (L02), BC Ferries (L03), BC Transit (L04) and WorkSafeBC
// (L05) — have since had their logo histories researched (research/identity/, 2026-09-27) and are
// collections in the gallery, so the list is empty and the gallery shows no shelf for it. It is kept
// for the next body found missing. No package is an official master, so the routes the companion
// recorded still stand: ICBC through its newsroom's media contacts, BCLC through
// mediarelations@bclc.com, BC Ferries through media@bcferries.com, BC Transit through
// media@bctransit.com, and WorkSafeBC through its Contact Us route.

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

/**
 * @type {Array<{id: string, source: string, label: string, body: string, graphNode: string,
 *   sourceIds: string[], verified: string, assetStatus: keyof ASSET_STATUS, contact: string,
 *   nextAction: string, warning: string}>}
 */
export const WANTED = []
