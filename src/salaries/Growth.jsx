// How pay moved, as the salary pages show it: the two measures (growth.js) as tiles, a tip saying
// what each is, and a table column for either.

import { formatRate, MAX_GAP, MIN_RECORDS, MIN_SPAN } from './growth.js'
import { count } from './common.jsx'

/** What the two measures are, behind an "i" beside a heading. */
export const GrowthTip = ({ id }) => (
  <span className="salaries__tip salaries__tip--inline">
    <button type="button" className="salaries__tip-button" aria-label="How pay growth is measured" aria-describedby={id}>i</button>
    <span role="tooltip" id={id} className="salaries__tip-text">
      <strong>Average growth</strong> compares the average in the first and last years with {MIN_RECORDS} or more records, at least {MIN_SPAN} years
      apart, as a rate a year; across employers, each employer’s own change is taken, weighed by its records. It moves when who is
      on the list changes, not only when pay does. <strong>Typical raise</strong> is the median yearly change for the same name between two
      disclosures up to {MAX_GAP} years apart: closer to what people kept in a job were paid more, though a shared name is not proof of one
      person, and a part year shows as a jump.
    </span>
  </span>
)

/**
 * The two measures as tiles: `growth` from seriesGrowth or pooledGrowth, `raise` from typicalRaise,
 * either null (`raiseNote` then says why). Nothing is drawn when neither could be measured.
 */
export const GrowthTiles = ({ growth, raise, years, id, extra, raiseNote = 'no name in two disclosures' }) => {
  if (!growth && !raise) return null
  return (
    <div className="salaries__growth">
      <h3 className="salaries__title">How pay moved <GrowthTip id={id} /></h3>
      <dl className="salaries__tiles salaries__tiles--three">
        <div>
          <dt>Average growth</dt>
          <dd>{formatRate(growth?.rate, '')}</dd>
          <dd className="salaries__line">{growth ? `a year, ${years[growth.from?.year ?? growth.from]}–${years[growth.to?.year ?? growth.to]}` : `needs ${MIN_RECORDS}+ records ${MIN_SPAN}+ years apart`}</dd>
        </div>
        <div>
          <dt>Typical raise</dt>
          <dd>{formatRate(raise?.rate, '')}</dd>
          <dd className="salaries__line">{raise ? `a year, from ${count(raise.pairs, 'raise', 'raises')}` : raiseNote}</dd>
        </div>
        {extra}
      </dl>
    </div>
  )
}

/** A table column of a rate a year, in percent so its filter reads "at least 3" as 3%. */
export const rateColumn = (id, header, rateOf) => ({
  id,
  header,
  accessorFn: (row) => {
    const rate = rateOf(row)
    return rate === null || rate === undefined ? undefined : Math.round(rate * 1000) / 10
  },
  sortUndefined: 'last',
  meta: { kind: 'number' },
  cell: ({ getValue }) => formatRate(getValue() === undefined ? null : getValue() / 100, '')
})
