// The ministries and central agencies of the Government of British Columbia.
//
// This is a convenience list, not an authority. Ministries are created, merged and renamed at
// every cabinet shuffle, so the generator always allows a typed-in name as well — a list that has
// gone stale should never be the reason someone cannot make the logo they need.
//
// Last reviewed: 2025-09. When updating, check the current list at
// https://www2.gov.bc.ca/gov/content/governments/organizational-structure/ministries-organizations

/** The date the list below was last checked, surfaced in the UI so its age is visible. */
export const MINISTRY_LIST_REVIEWED = '2025-09'

export const MINISTRY_GROUPS = [
  {
    label: 'Ministries',
    options: [
      'Ministry of Agriculture and Food',
      'Ministry of Attorney General',
      'Ministry of Children and Family Development',
      'Ministry of Citizens’ Services',
      'Ministry of Education and Child Care',
      'Ministry of Emergency Management and Climate Readiness',
      'Ministry of Energy and Climate Solutions',
      'Ministry of Environment and Parks',
      'Ministry of Finance',
      'Ministry of Forests',
      'Ministry of Health',
      'Ministry of Housing and Municipal Affairs',
      'Ministry of Indigenous Relations and Reconciliation',
      'Ministry of Infrastructure',
      'Ministry of Jobs, Economic Development and Innovation',
      'Ministry of Labour',
      'Ministry of Mining and Critical Minerals',
      'Ministry of Post-Secondary Education and Future Skills',
      'Ministry of Public Safety and Solicitor General',
      'Ministry of Social Development and Poverty Reduction',
      'Ministry of Tourism, Arts, Culture and Sport',
      'Ministry of Transportation and Transit',
      'Ministry of Water, Land and Resource Stewardship'
    ]
  },
  {
    label: 'Central agencies',
    options: [
      'Office of the Premier',
      'BC Public Service Agency',
      'Government Communications and Public Engagement',
      'Intergovernmental Relations Secretariat'
    ]
  }
]

/** Every name in one flat list, in the order the groups declare them. */
export const MINISTRIES = MINISTRY_GROUPS.flatMap((group) => group.options)

/** Case- and punctuation-insensitive search, for the picker's filter box. */
export const searchMinistries = (query) => {
  const needle = normalize(query)
  if (!needle) return MINISTRY_GROUPS

  return MINISTRY_GROUPS
    .map((group) => ({ ...group, options: group.options.filter((name) => normalize(name).includes(needle)) }))
    .filter((group) => group.options.length > 0)
}

// Everything but letters and digits is folded away, so a filter box matches on the words rather
// than on the punctuation. Nobody types the curly apostrophe in "Citizens’ Services" from memory,
// and "post secondary", "post-secondary" and "postsecondary" should all find the same ministry.
const normalize = (value) => String(value ?? '').toLowerCase().replace(/[^a-z0-9]+/g, '')

export const isKnownMinistry = (name) => MINISTRIES.some((entry) => normalize(entry) === normalize(name))
