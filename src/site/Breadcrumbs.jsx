// The trail at the top of a page below a section's first page: "← Section / Parent / This page".
//
// Every page that is not a section's first page opens with it, so the way back is always in the
// same place and looks the same: the section's first page as the back button, each page between as
// a link, and this page last, named but not a link. A step is a SiteLink when it has a place (`to`),
// so it has a real address to open in a new tab; an `href` with an `onClick` when the view handles a
// plain click itself (a transition) but the step still has an address; or a button when the view
// keeps its own state (`onClick` alone).
import { Fragment } from 'react'
import { SiteLink } from './navigation.jsx'

const Step = ({ step, className, stepRef, children }) => step.to
  ? <SiteLink ref={stepRef} className={className} to={step.to} title={step.title} onClick={step.onClick}>{children}</SiteLink>
  : step.href
    ? <a ref={stepRef} className={className} href={step.href} title={step.title} onClick={step.onClick}>{children}</a>
    : step.onClick
      ? <button ref={stepRef} type="button" className={className} title={step.title} onClick={step.onClick}>{children}</button>
      // A step with no page of its own (an organization a viewer groups by) is named, not linked.
      : <span className={`${className} gallery__crumb--plain`} title={step.title}>{children}</span>

/**
 * @param {object} props
 * @param {string} props.label What the trail is named for a screen reader: the section.
 * @param {{ label: string, to?: object, href?: string, onClick?: Function, title?: string }[]} props.steps The section's
 *   first page, then each page between, oldest first; the last is this page.
 * @param {import('react').Ref} [props.currentRef] Focused when the page opens, so a screen reader
 *   starts at the page's name.
 * @param {import('react').Ref} [props.backRef] The first step, for a view that focuses its way back.
 * @param {import('react').ReactNode} [props.after] Shown after the trail on the same line (a count).
 */
export const Breadcrumbs = ({ label, steps, currentRef, backRef, after }) => {
  const [root, ...rest] = steps
  const current = rest.at(-1)
  const between = rest.slice(0, -1)
  return (
    <nav className="gallery__crumbs" aria-label={label}>
      <Step step={root} className="gallery__back" stepRef={backRef}><span aria-hidden="true">←</span> {root.label}</Step>
      {between.map((step) => (
        <Fragment key={step.label}>
          <span aria-hidden="true">/</span>
          <Step step={step} className="gallery__crumb">{step.label}</Step>
        </Fragment>
      ))}
      {current && <>
        <span aria-hidden="true">/</span>
        <span aria-current="page" title={current.label} ref={currentRef} tabIndex={currentRef ? -1 : undefined}>{current.label}</span>
      </>}
      {after}
    </nav>
  )
}
