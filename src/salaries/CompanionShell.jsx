// The frame every salary section shares: the search field, a heading with its figures in tiles, the
// browse bar (Employers · People · Positions · Council pay · Workforce) with the cards/table switch,
// then the section's own chips and content. Council pay and Workforce use it so they read, and are
// worked, the same way as Employers and People.

import { Segmented } from '../site/Segmented.jsx'
import { SalarySearchField } from './MobileFilters.jsx'
import { LAYOUTS } from './common.jsx'

export const BROWSE = [
  { value: 'employers', label: 'Employers' },
  { value: 'people', label: 'People' },
  { value: 'positions', label: 'Positions' },
  { value: 'council', label: 'Council pay' },
  { value: 'workforce', label: 'Workforce' }
]

/**
 * @param {object} props
 * @param {Array<{ label: string, value: string, note?: string }>} props.tiles  Up to four headline figures.
 */
export const CompanionShell = ({ browse, onBrowse, layout, onLayout, query, onSearch, searchLabel, placeholder, searchHelp, heading, tiles = [], intro = null, children }) => (
  <div className="salaries salaries-companion">
    {onSearch && (
      <div className="salaries__search salaries__global-search">
        <SalarySearchField labelled label={searchLabel} ariaLabel={searchLabel} placeholder={placeholder} help={searchHelp} value={query} onChange={onSearch} />
      </div>
    )}
    <section className="salaries__intro" aria-labelledby={`salaries-${browse}-intro`}>
      <h2 id={`salaries-${browse}-intro`} className="salaries__heading">{heading}</h2>
      {intro}
      {browse !== 'about' && onBrowse && <p className="salaries__about-link"><button type="button" className="salaries__link" onClick={() => onBrowse('about')}>About these records, privacy and corrections</button></p>}
      {tiles.length > 0 && (
        <dl className="salaries__tiles">
          {tiles.map((tile) => (
            <div key={tile.label}><dt>{tile.label}</dt><dd>{tile.value}</dd>{tile.note && <dd className="salaries__line">{tile.note}</dd>}</div>
          ))}
        </dl>
      )}
    </section>
    <div className="salaries__browse-bar">
      <Segmented ariaLabel="Browse" value={browse} onChange={onBrowse} options={BROWSE} />
      {onLayout && <Segmented compact ariaLabel="Layout" value={layout} onChange={onLayout} options={LAYOUTS} />}
    </div>
    {children}
  </div>
)

/** A row of chips like the sector chips: one pressed at a time, each with an optional count. */
export const Chips = ({ label, options, value, onChange, all = null }) => (
  <div className="salaries__chips" role="group" aria-label={label}>
    {all && <button type="button" aria-pressed={value === 'all'} onClick={() => onChange('all')}>{all}</button>}
    {options.map((option) => (
      <button key={option.value} type="button" aria-pressed={value === option.value} title={option.title}
        onClick={() => onChange(all && value === option.value ? 'all' : option.value)}>
        {option.label}{option.count !== undefined && <> <span>{option.count.toLocaleString('en-CA')}</span></>}
      </button>
    ))}
  </div>
)
