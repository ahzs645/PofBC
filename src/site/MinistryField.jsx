// Choosing the ministry: pick one from the list, or type anything.
//
// The list is a convenience and is dated in the hint beneath it — ministries are renamed at every
// cabinet shuffle, and a stale list must never be the reason someone cannot make their logo. The
// two modes keep separate values, so switching between them is non-destructive.

import { useId } from 'react'
import { MINISTRY_GROUPS, MINISTRY_LIST_REVIEWED } from '../ministries/ministries.js'

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
            {MINISTRY_GROUPS.map((group) => (
              <optgroup key={group.label} label={group.label}>
                {group.options.map((name) => <option key={name} value={name}>{name}</option>)}
              </optgroup>
            ))}
          </select>
          <p className="field__note">List last reviewed {MINISTRY_LIST_REVIEWED}. Not there? Switch to “Type it in”.</p>
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
