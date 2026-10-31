// The sovereign of Canada, and so of British Columbia, on a day since the Province joined
// Confederation in 1871. A reign is counted from the day of accession, so a year read at its last
// day takes whoever then reigned: 1901 is Edward VII's, 1936 George VI's, 2022 Charles III's.
// Accession dates as the Government of Canada gives them (canada.ca, "Previous Sovereigns of Canada").

export const MONARCHS = [
  { name: 'Victoria', title: 'Queen', from: '1837-06-20' },
  { name: 'Edward VII', title: 'King', from: '1901-01-22' },
  { name: 'George V', title: 'King', from: '1910-05-06' },
  { name: 'Edward VIII', title: 'King', from: '1936-01-20' },
  { name: 'George VI', title: 'King', from: '1936-12-11' },
  { name: 'Elizabeth II', title: 'Queen', from: '1952-02-06' },
  { name: 'Charles III', title: 'King', from: '2022-09-08' }
]

/** The monarch reigning on `day` (YYYY-MM-DD), or the first in the list before it. */
export const monarchOn = (day) => MONARCHS.findLast((monarch) => monarch.from <= day) ?? MONARCHS[0]
