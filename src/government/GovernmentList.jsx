// The year's government as a list: the diagram's second view.
//
// Everything the diagram draws, in the order a reader would look for it — the Legislature and its
// officers, the Crown and the Premier, each ministry with its minister and the bodies that answer
// to it, the courts, and whatever answers to no ministry the sources name. It is the view that
// works on a phone, and the one a screen reader can walk without learning the diagram's geometry.

import { useLayoutEffect, useMemo, useRef, useState } from 'react'
import { KINDS } from './GovernmentGraph.jsx'

const Item = ({ node, selected, onSelect, nested }) => (
  <li>
    <button
      type="button"
      className="gov-list__item"
      data-nested={nested || undefined}
      aria-current={selected ? 'true' : undefined}
      onClick={() => onSelect(node.id)}
    >
      <span className="gov-kind-dot" data-branch={node.branch ?? 'people'} />
      <span className="gov-list__name">
        {node.shortName ?? node.name}
        <span className="gov-list__meta">{KINDS[node.kind]?.one ?? ''}</span>
      </span>
      {node.head?.person && <span className="gov-list__head">{node.head.person}</span>}
    </button>
  </li>
)

export const GovernmentList = ({ government, selectedId, onSelect, hiddenKinds, compact = false }) => {
  const sections = useMemo(() => {
    const visible = government.nodes.filter((node) => node.kind !== 'people' && !hiddenKinds.has(node.kind))
    const by = (test) => visible.filter(test)
    const ministries = by((node) => node.kind === 'ministry')
    const answering = (id) => by((node) => node.group === id && node.kind !== 'ministry')
    const grouped = new Set(ministries.map((node) => node.id).concat('premier'))
    return [
      { title: 'Legislative', items: by((node) => node.branch === 'legislative').map((node) => ({ node })) },
      {
        title: 'Executive',
        items: [
          ...by((node) => node.kind === 'crown' || node.kind === 'premier').flatMap((node) => [
            { node },
            ...(node.kind === 'premier' ? answering('premier').map((child) => ({ node: child, nested: true })) : [])
          ]),
          ...ministries.flatMap((node) => [{ node }, ...answering(node.id).map((child) => ({ node: child, nested: true }))])
        ]
      },
      {
        title: 'Answering to no ministry named in the sources',
        items: by((node) => node.branch === 'executive' && node.ring === 'outer' && !grouped.has(node.group)).map((node) => ({ node }))
      },
      { title: 'Judicial', items: by((node) => node.branch === 'judicial').map((node) => ({ node })) }
    ].filter((section) => section.items.length)
  }, [government, hiddenKinds])

  // The body chosen when the list opened; its group starts unfolded, and is not folded again under the
  // reader as the choice moves.
  const [chosenAtStart] = useState(selectedId)

  // The list scrolls in the diagram's frame, and its scrollbar sits in the page's margin beside it,
  // so the cards line up with the timeline under them whether the system's scrollbars take room or not.
  const frame = useRef(null)
  useLayoutEffect(() => {
    const element = frame.current
    if (element) element.style.setProperty('--gov-list-gutter', `${element.offsetWidth - element.clientWidth}px`)
  }, [compact])

  return (
    <div className="gov-list" ref={frame} aria-label={`The Government of British Columbia in ${government.year}, as a list`}>
      {sections.map((section) => {
        const title = <h2 className="gov-list__title">{section.title} <span className="gov-muted">{section.items.length}</span></h2>
        const items = (
          <ul>
            {section.items.map(({ node, nested }) => (
              <Item key={node.id} node={node} nested={nested} selected={node.id === selectedId} onSelect={onSelect} />
            ))}
          </ul>
        )
        // On a phone the list is part of the page rather than a frame of its own, so its groups are
        // folded — the one holding the chosen body open — so the timeline stays near.
        return compact
          ? (
            <details key={section.title} className="gov-list__section" open={section.items.some(({ node }) => node.id === chosenAtStart) || undefined}>
              <summary>{title}</summary>
              {items}
            </details>
            )
          : <section key={section.title} className="gov-list__section">{title}{items}</section>
      })}
    </div>
  )
}
