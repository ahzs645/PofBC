// Which disclosure of pay a body's panel shows (Salaries.jsx).

import { SALARY_INDEX } from './salaryIndex.js'

export const PUBLIC_SERVICE = 'public-service'

/**
 * Whose disclosure a body's panel shows: its own, or, for a ministry and the agency that employs the
 * public service, the public service's — which the Province discloses as one employer, not by ministry.
 */
export const salaryKeyOf = (node) => {
  if (SALARY_INDEX[node.id]) return node.id
  if (node.kind === 'ministry' || node.id === 'bc-public-service-agency') return PUBLIC_SERVICE
  return null
}
