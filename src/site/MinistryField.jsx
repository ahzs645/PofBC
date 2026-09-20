// Choosing the ministry: pick one from the list, or type anything.
//
// The list is a convenience and is dated in the hint beneath it — ministries are renamed at every
// cabinet shuffle, and a stale list must never be the reason someone cannot make their logo. The
// two modes keep separate values, so switching between them is non-destructive.

import { useId, useMemo } from 'react'
import { MINISTRY_GROUPS, MINISTRY_LIST_REVIEWED } from '../ministries/ministries.js'
import { describeMinistry, historicalGroups } from '../ministries/ministryHistory.js'

/**
 * Today's ministries, then every ministry there has been.
 *
 * Three of the four identities here are historical, and a list of the ministries that exist now
 * could not name any of them: there was no way to put the right name on a 1986 lockup. The older
 * names carry the years they ran, which is what says which lockup they belong on.
 */
const ALL_GROUPS = [
  ...MINISTRY_GROUPS,
  ...historicalGroups(MINISTRY_GROUPS.flatMap((group) => group.options))
]

/** What is known about a chosen name: when it ran, and what it became. */
const History = ({ name }) => {
  const known = useMemo(() => describeMinistry(name), [name])
  if (!known) return null

  return (
    <p className="field__note">
      {known.ended ? `Ran ${known.years}.` : `In use since ${known.years.replace('–', '')}.`}
      {known.earlier.length > 0 && ` The name was also used ${known.earlier.join(' and ')}.`}
      {known.became.length > 0 && ` It became ${known.became.join(', and ')}.`}
    </p>
  )
}

export const MinistryField = ({ source, ministry, manualMinistry, program, onChange }) => {
  const selectId = useId()
  const manualId = `${selectId}-manual`
  const programId = `${selectId}-program`

  return (
    <>
      <div className="field">
        <span className="field__label" id={`${selectId}-mode`}>Ministry</span>
        <div className="segmented" role="group" aria-labelledby={`${selectId}-mode`}>
          <button type="button" aria-pressed={source === 'list'} onClick={() => onChange({ source: 'list' })}>
            From the list
          </button>
          <button type="button" aria-pressed={source === 'manual'} onClick={() => onChange({ source: 'manual' })}>
            Type it in
          </button>
        </div>
      </div>

      {source === 'list' ? (
        <div className="field">
          <label htmlFor={selectId}>Ministry or agency</label>
          <select
            id={selectId}
            value={ministry}
            onChange={(event) => onChange({ ministry: event.target.value })}
          >
            {ALL_GROUPS.map((group) => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map((option) => (typeof option === 'string'
                  ? <option key={option} value={option}>{option}</option>
                  : <option key={option.value} value={option.value}>{option.label}</option>))}
              </optgroup>
            ))}
          </select>
          <History name={ministry} />
          <p className="field__note">
            Today’s list last reviewed {MINISTRY_LIST_REVIEWED}; the dated ones are every ministry
            since 1976. Not there? Switch to “Type it in”.
          </p>
        </div>
      ) : (
        <div className="field">
          <label htmlFor={manualId}>Ministry, agency or office</label>
          {/* A textarea rather than an input: the renderer honours explicit newlines, so someone
              who wants a particular line break can just press Enter and take it. */}
          <textarea
            id={manualId}
            rows={2}
            value={manualMinistry}
            placeholder="Ministry of Forests"
            autoComplete="off"
            onChange={(event) => onChange({ manualMinistry: event.target.value })}
          />
          <History name={manualMinistry} />
          <p className="field__note">Long names wrap to the lockup’s measure on their own. Press Enter to force a break.</p>
        </div>
      )}

      <div className="field">
        <label htmlFor={programId}>Second line <span className="field__note" style={{ display: 'inline' }}>(optional)</span></label>
        <input
          id={programId}
          type="text"
          value={program}
          placeholder="Research Program"
          autoComplete="off"
          onChange={(event) => onChange({ program: event.target.value })}
        />
      </div>
    </>
  )
}
