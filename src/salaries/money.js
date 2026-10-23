// Retain the published cent precision while keeping whole-dollar disclosures uncluttered.
const wholeDollars = new Intl.NumberFormat('en-CA', {
  style: 'currency', currency: 'CAD', minimumFractionDigits: 0, maximumFractionDigits: 0
})
const dollarsAndCents = new Intl.NumberFormat('en-CA', {
  style: 'currency', currency: 'CAD', minimumFractionDigits: 2, maximumFractionDigits: 2
})

export const formatMoney = (value, missing = '—') => {
  if (value === null || value === undefined || !Number.isFinite(value)) return missing
  return (Number.isInteger(value) ? wholeDollars : dollarsAndCents).format(value)
}

/** Median of monetary observations, rounded to the nearest cent only when the midpoint needs it. */
export const medianMoney = (values) => {
  if (!values.length) return null
  const sorted = [...values].sort((a, b) => a - b)
  const middle = Math.floor(sorted.length / 2)
  if (sorted.length % 2) return sorted[middle]
  const lowerCents = Math.round(sorted[middle - 1] * 100)
  const upperCents = Math.round(sorted[middle] * 100)
  return Math.round((lowerCents + upperCents) / 2) / 100
}
