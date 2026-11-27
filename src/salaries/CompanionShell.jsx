// The frame every salary section shares: the search field, a heading with its figures in tiles, the
// browse bar with the cards/table switch, then the section's own chips and content. Council pay and
// Workforce use it so they read, and are worked, the same way as Employers and People.

import { Segmented } from '../site/Segmented.jsx'
import { SalarySearchField } from './MobileFilters.jsx'
import { LAYOUTS } from './common.jsx'
import { Breadcrumbs } from '../site/Breadcrumbs.jsx'

// The bar holds two kinds of thing. Employers, People and Positions are three ways through the same
// payment records, and keep the period and sector chosen: a segmented control. Council pay, Workforce
// and About are other collections, with their own figures and sources: plainer links beside it.
export const RECORD_BROWSE = [
  { value: 'employers', label: 'Employers' },
  { value: 'people', label: 'People' },
  { value: 'positions', label: 'Positions' }
]
export const OTHER_BROWSE = [
  { value: 'council', label: 'Council pay' },
  { value: 'workforce', label: 'Workforce' },
  { value: 'about', label: 'About' }
]
/** Every section with a tab of its own (About is a page of notes, not a section). */
export const BROWSE = [...RECORD_BROWSE, ...OTHER_BROWSE.filter(({ value }) => value !== 'about')]

/**
 * The sections, drawn the same on every page: SalariesView's settleBrowse finds the bar by its
 * `salaries__browse-bar--sections` class, to keep it under the reader's finger as the section
 * changes. On a collection of its own (Council pay, Workforce, About) none of the three records
 * tabs is pressed.
 */
export const BrowseBar = ({ browse, onBrowse, layout, onLayout }) => (
  <div className="salaries__browse-bar salaries__browse-bar--sections">
    <div className="salaries__sections">
      <Segmented ariaLabel="Browse the payment records" value={browse} onChange={onBrowse} options={RECORD_BROWSE} />
      <div className="salaries__other-sections" role="group" aria-label="Other collections">
        {OTHER_BROWSE.map((option) => (
          <button key={option.value} type="button" className="salaries__section-link" aria-pressed={browse === option.value} onClick={() => onBrowse(option.value)}>
            {option.label}
          </button>
        ))}
      </div>
    </div>
    {onLayout && <Segmented compact ariaLabel="Layout" value={layout} onChange={onLayout} options={LAYOUTS} />}
  </div>
)

/**
 * @param {object} props
 * @param {Array<{ label: string, value: string, note?: string }>} props.tiles  Up to four headline figures.
 */
export const CompanionShell = ({ browse, onBrowse, layout, onLayout, query, onSearch, searchLabel, placeholder, searchHelp, heading, back = null, tiles = [], intro = null, children }) => (
  <div className="salaries salaries-companion">
    {onSearch && (
      <div className="salaries__search salaries__global-search">
        <SalarySearchField labelled label={searchLabel} ariaLabel={searchLabel} placeholder={placeholder} help={searchHelp} value={query} onChange={onSearch} />
      </div>
    )}
    <section className={`salaries__intro salaries__intro--${browse}`} aria-labelledby={`salaries-${browse}-intro`}>
      {back?.length > 0 && <Breadcrumbs label="Salaries" steps={[...back, { label: heading }]} />}
      <div className="salaries__page-heading">
        <h2 id={`salaries-${browse}-intro`} className="salaries__heading">{heading}</h2>
      </div>
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
    {onBrowse && <BrowseBar browse={browse} onBrowse={onBrowse} layout={layout} onLayout={onLayout} />}
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
