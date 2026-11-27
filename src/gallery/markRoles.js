// What each collected design is to its body: the body's identity, or a secondary mark made for an
// anniversary, a campaign, an event, a partner's co-brand, or a publication's decoration.
//
// A collection leads with its body's identity. Its cover and its first entries are identity designs
// whenever it holds one, and its secondary marks follow in a section of their own for each kind. A
// collection holding only secondary marks keeps one as its cover, labelled as what it is.
//
// The role is presentation only: design IDs, files and provenance are unchanged. A record can carry
// its own `markRole`; the map below covers records whose packages carry none. Each entry gives the
// words of its record (label, notes, source locator or file name) that show what the mark is. A
// design is classified only when its record says so plainly; a tagline that is part of a body's
// signature, a festival's own annual title, or a campaign's own mark is that body's identity.

export const MARK_ROLES = {
  // ── Anniversary and commemorative marks ────────────────────────────────────────────────────────
  'source-forest-enhancement-society-fesbc-10th-anniversary-svg': { role: 'commemorative',
    evidence: 'Source file logo-10yrs-full.svg; the record notes “Anniversary variant is explicitly identified”, beside the standard horizontal and vertical logo-kit artwork.' },
  'tiabc-website': { role: 'commemorative', evidence: 'Label “TIABC 50th anniversary signature”; notes “A commemorative fifty-year lockup in the association’s masthead.”' },
  'bcirpu-anniversary-2024': { role: 'commemorative', evidence: 'Label “BCIRPU 25th-anniversary silver seal”.' },
  'asi-anniversary-web': { role: 'commemorative', evidence: 'Label “ASI 15th anniversary, 1986–2001”: the outlined 15 surrounds the initials and the years.' },
  'asi-fifteen-years': { role: 'commemorative', evidence: 'Label “ASI fifteenth anniversary signature”, with “Fifteen years building BC’s high technology sector.”' },
  'iaf-25-years': { role: 'commemorative', evidence: 'Label “IAF 25th anniversary”; the lockup adds “25 YEARS 1996–2021”.' },
  'bcgs-centennial-1995': { role: 'commemorative', evidence: 'Label “100 years of geological surveying”: the centennial signature, 1895–1995.' },
  'bcgs-anniversary-2020': { role: 'commemorative', evidence: 'Label “125th anniversary seal”.' },
  'source-expanded-etsi-bc-annual-report-2026-20th-anniversary': { role: 'commemorative', evidence: 'Label “20th anniversary logo”: a gold 20 Years badge above the horizontal logo.' },
  'prince-george-centennial-2015': { role: 'commemorative', evidence: 'Label “Prince George centennial · 1915–2015”, with “Prince George Celebrates” below the 100.' },
  'recovered-north-cowichan-150-anniversary-2023': { role: 'commemorative', evidence: 'Label “North Cowichan · 150 anniversary mark, 2023”; notes “commemorative150 mark”.' },
  'source-recovered-forest-practices-board-30th': { role: 'commemorative', evidence: 'Label “Forest Practices Board — 30th anniversary lockup”.' },
  'ufv-40-years-2014': { role: 'commemorative', evidence: 'Label “University of the Fraser Valley · 40 years”: “40 YEARS” set above the signature.' },
  'ufv-cascades-30-years-2013': { role: 'commemorative', evidence: 'Label “UFV Cascades athletics · 30 years”, with a 1983–2013 ribbon.' },
  'bc-150-years': { role: 'commemorative', evidence: 'Label “BC 150 Years”; notes “The 2008 anniversary mark”.' },

  // ── Campaign and promotional marks ─────────────────────────────────────────────────────────────
  'tourism-prince-george-tour-the-city-2012': { role: 'campaign', evidence: 'Notes “The brown campaign lettering … followed by the bracketed tagline.”' },
  'pg-get-out-2013': { role: 'campaign', evidence: 'Notes “The campaign headline contains image effects”.' },
  'take-on-pg-2015': { role: 'campaign', evidence: 'Label “takeonPG.com · centennial campaign”.' },
  'alaska-highway-house-journey-2015': { role: 'campaign', evidence: 'Label “Start your Alaska Highway journey here · campaign”.' },
  'smithers-im-there-2014': { role: 'campaign', evidence: 'Notes “The I’m there. campaign”.' },
  'fort-st-john-compass-2013': { role: 'campaign', evidence: 'Label “… · visitor campaign”; notes “a visitor campaign design with a compass rose and its own slogan”.' },
  'taylor-district-script-2015': { role: 'campaign', evidence: 'Label “District of Taylor · visitor campaign script”.' },
  'municipal-clinton-walking-tour-2021-slogan': { role: 'campaign', evidence: 'Notes “the stacked Clinton promotional slogan” (“Where History Meets Adventure”).' },
  'explore-bc-photo-collage-2015': { role: 'campaign', evidence: 'Notes “The tourism campaign’s white #EXPLOREBC headline crosses a collage of visitor photographs.”' },
  'recovered-ucc-fact-book-campaign-2003': { role: 'campaign', evidence: 'Label “UCC campaign lockup”; notes “campaign use”.' },

  // ── Event, sponsor and partner marks ───────────────────────────────────────────────────────────
  'firesmart-bc-training-summit': { role: 'event', evidence: 'Label “Wildfire Resiliency and Training Summit”: one of the guide’s event identities, beside the provincial signature.' },
  'pg-moose-winter-games-partner-2015': { role: 'partner', evidence: 'Label “Tourism Prince George × 2015 Canada Winter Games · community partner”.' },
  'nbcta-snbc-smithers-reverse-2015': { role: 'partner', evidence: 'Label “Northern British Columbia Region × Super, Natural BC · Smithers co-brand”.' },
  'nbcta-region-snbc-red': { role: 'partner', evidence: 'Notes “The red Northern British Columbia Region panel is paired with the oval Super, Natural British Columbia Canada mark.”' },

  // ── Decorative and editorial graphics ──────────────────────────────────────────────────────────
  'nbcta-northeast-guide-2012': { role: 'decorative', evidence: 'Label “… section graphic”; notes “on a red editorial panel”.' },
  'nbcta-northwest-guide-2012': { role: 'decorative', evidence: 'Label “… section graphic”; notes “on a green editorial panel”.' },
  'nbcta-haida-gwaii-guide-2012': { role: 'decorative', evidence: 'Label “… section graphic”; notes “on a yellow editorial panel”.' },
  'nbcta-choices-ahead-2015': { role: 'decorative', evidence: 'Label “Choices Ahead · 2015 guide route icon”.' }
}

/** The roles a design can have. Anything not named here, or named nowhere, is the body's identity. */
export const MARK_ROLE_LABELS = {
  identity: 'Identity',
  commemorative: 'Anniversary mark',
  campaign: 'Campaign mark',
  event: 'Event mark',
  partner: 'Partner co-brand',
  decorative: 'Editorial graphic'
}

/** Where each kind of secondary mark is shown on its collection's page, in this order. */
export const SECONDARY_SECTIONS = [
  { id: 'secondary-commemorative', label: 'Anniversary and commemorative marks', roles: ['commemorative'] },
  { id: 'secondary-campaign', label: 'Campaign and promotional marks', roles: ['campaign'] },
  { id: 'secondary-event', label: 'Event, sponsor and partner marks', roles: ['event', 'partner'] },
  { id: 'secondary-decorative', label: 'Decorative and editorial graphics', roles: ['decorative'] }
]

const knownRole = (role) => (role && Object.hasOwn(MARK_ROLE_LABELS, role) ? role : undefined)

/** A gallery entry's role: its own, its files' records', or the map's, else identity. */
export const markRoleOf = (entry) => {
  if (!entry) return 'identity'
  const ids = [entry.id, entry.asset?.id, ...(entry.versions ?? []).map((version) => version.id)]
  return knownRole(entry.markRole) ?? knownRole(entry.asset?.markRole) ??
    (entry.versions ?? []).map((version) => knownRole(version.markRole)).find(Boolean) ??
    ids.map((id) => MARK_ROLES[id]?.role).find(Boolean) ?? 'identity'
}

export const isIdentityMark = (entry) => markRoleOf(entry) === 'identity'

/** The identity designs first, then the secondary marks, each keeping its own order. */
export const identityFirst = (entries = []) => [
  ...entries.filter(isIdentityMark),
  ...entries.filter((entry) => !isIdentityMark(entry))
]

/** The designs a cover can be chosen from: the identity designs, or every design when none is one. */
export const coverCandidates = (entries = []) => entries.some(isIdentityMark) ? entries.filter(isIdentityMark) : entries

/**
 * A gallery collection with its secondary marks after its identity: each entry carries its role, the
 * cover and shelf specimen are identity designs when the collection holds one, and a collection laid
 * out as a list gains a section for each kind of secondary mark it holds. A mark its body's record
 * already places in a section stays there; a collection laid out by eras keeps its eras, each with
 * its identity designs first.
 */
export const withMarkRoles = (collection) => {
  const all = collection.eras ? collection.eras.flatMap((era) => era.entries) : (collection.entries ?? [])
  // An entry object can be shared by several collections; its role is its design's, so it is the same in each.
  for (const entry of all) {
    const role = markRoleOf(entry)
    if (role !== 'identity') entry.markRole = role
  }
  if (!all.some((entry) => entry.markRole)) return collection

  const candidates = coverCandidates(all)
  const inCollection = (id) => all.find((entry) => entry.id === id)
  const cover = collection.cover && !candidates.includes(inCollection(collection.cover)) && inCollection(collection.cover)
    ? candidates[0]?.id : collection.cover
  const shelfSpecimen = collection.shelfSpecimen && !candidates.includes(inCollection(collection.shelfSpecimen))
    ? undefined : collection.shelfSpecimen
  // Each list keeps its own order otherwise: a collection that leads with its cover already does.
  if (collection.eras) {
    return { ...collection, cover, shelfSpecimen, eras: collection.eras.map((era) => ({ ...era, entries: identityFirst(era.entries) })) }
  }

  const placed = new Set((collection.artworkSections ?? []).flatMap(({ entries }) => entries))
  const loose = all.filter((entry) => entry.markRole && !placed.has(entry))
  const added = SECONDARY_SECTIONS.map(({ roles, ...section }) => ({
    ...section, secondary: true, entries: loose.filter((entry) => roles.includes(entry.markRole))
  })).filter(({ entries }) => entries.length)
  return {
    ...collection, cover, shelfSpecimen,
    entries: identityFirst(collection.entries ?? []),
    ...(collection.artworkSections || added.length
      ? { artworkSections: [...(collection.artworkSections ?? []), ...added] } : {})
  }
}
