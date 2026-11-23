// Where the rest of the site links into the Parties view.
//
// Kept apart from the catalogue so the government view can link a premier's or a candidate's party
// without loading every party's artwork records. The labels are the ones the site's own data uses:
// the premiers' timeline ("NDP", "Social Credit", …) and Elections BC's party names ("BC NDP",
// "Conservative Party", …).

const PARTY_LABELS = {
  'Non-partisan': 'pre-1903',
  Conservative: 'bc-conservative',
  'Progressive Conservative': 'bc-conservative',
  'Conservative Party': 'bc-conservative',
  'Conservative Party of BC': 'bc-conservative',
  'Conservative Party of British Columbia': 'bc-conservative',
  Liberal: 'bc-liberal',
  'BC Liberal': 'bc-liberal',
  'BC Liberal Party': 'bc-liberal',
  'BC United': 'bc-united',
  Coalition: 'coalition',
  'Social Credit': 'social-credit',
  CCF: 'bc-ccf',
  NDP: 'bc-ndp',
  'BC NDP': 'bc-ndp',
  'New Democratic': 'bc-ndp',
  'New Democratic Party': 'bc-ndp',
  Green: 'bc-green',
  'BC Green Party': 'bc-green',
  'BC Greens': 'bc-green',
  Provincial: 'provincial-party',
  Reform: 'bc-reform',
  Labour: 'labour-historical',
  Socialist: 'socialist-party-bc',
  OneBC: 'onebc',
  CentreBC: 'centrebc'
}

/** The Parties view's id for a party as the site's other data names it, or null. */
export const partyIdFor = (label) => PARTY_LABELS[label] ?? null

/** The address of the Parties view, or of one party in it. */
export const partyPlace = (party, extra = {}) => ({ view: 'parties', ...(party ? { party: typeof party === 'object' ? party.id : party } : {}), ...extra })

/** The address of a party named the way the site's other data names it, or null. */
export const partyPlaceFor = (label) => {
  const id = partyIdFor(label)
  return id ? partyPlace(id) : null
}
