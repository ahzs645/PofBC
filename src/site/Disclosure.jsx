// The site's one fold, for long secondary material: a full source list, research notes, a raw
// roster, an advanced setting. Short or primary text is not folded; it is simply written out.
//
// A native <details> underneath, so the keyboard, the find-in-page reveal and screen readers treat
// it as a disclosure; the browser's triangle is hidden and a small chevron, drawn like the site's
// pickers' (ui/Select.jsx), turns when it opens. The summary is a plain line of text: never a
// heading, since a heading inside a summary is lost to assistive technology. A section that needs
// a heading keeps it outside, above the fold.

import { useState } from 'react'

const Chevron = () => (
  <svg className="disclosure__chevron" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true" focusable="false">
    <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

/**
 * @param {object} props
 * @param {import('react').ReactNode} props.summary What is folded, said plainly ("All 24 sources").
 * @param {import('react').ReactNode} [props.hint] A quieter second line: a count, what it holds.
 * @param {boolean} [props.defaultOpen] Open at first; it follows the prop when the prop changes.
 * @param {(open: boolean) => void} [props.onToggle]
 * @param {import('react').ReactNode | (() => import('react').ReactNode)} props.children As a function,
 *   built only when first opened: for folds of hundreds of links that most visits never open.
 */
export const Disclosure = ({ summary, hint, className, defaultOpen = false, id, onToggle, children }) => {
  const [opened, setOpened] = useState(defaultOpen)
  const lazy = typeof children === 'function'
  return (
    <details
      id={id}
      className={className ? `disclosure ${className}` : 'disclosure'}
      open={defaultOpen || undefined}
      onToggle={(event) => {
        const open = event.currentTarget.open
        if (open) setOpened(true)
        onToggle?.(open)
      }}
    >
      <summary className="disclosure__summary">
        <span className="disclosure__label">{summary}</span>
        <Chevron />
        {hint && <span className="disclosure__hint">{hint}</span>}
      </summary>
      <div className="disclosure__body">{lazy ? ((opened || defaultOpen) && children()) : children}</div>
    </details>
  )
}
