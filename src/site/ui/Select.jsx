// The site's dropdown, in place of the browser's own <select>.
//
// A native select draws its list in the operating system's style — a grey Windows menu, a macOS
// checklist — whatever the page around it looks like, and none of that list can be styled. This one
// draws the list itself, so it takes the palette of whichever view it sits in: ink on stone here, the
// posters' dark glass, the government view's own surfaces.
//
// It is written to be dropped in where a <select> was. The options are still <option> and
// <optgroup> elements, read as a description of the list rather than rendered; `onChange` receives
// the chosen option's value as a string, exactly what `event.target.value` gave before.
//
// Accessibility follows the WAI-ARIA "select-only combobox" pattern: focus stays on the button, the
// list is a listbox it controls, and the option under the keyboard is its active descendant. Arrow
// keys, Home and End, Page Up and Down, Enter, Space, Escape and typing a name all work as they do in
// a native select. Long lists also get a filter box.
//
// The list opens in the top layer (the Popover API) where the browser has it, so a panel's overflow,
// a transformed ancestor or a modal cannot clip it; without it, the list is fixed to the viewport.
// Either way it stays a DOM child of the control, so it inherits the view's custom properties. It is
// built from <span>s, so it is valid wherever a <select> was: inside a <p>, a <label>, a button row.

import { Children, Fragment, isValidElement, useCallback, useEffect, useId, useLayoutEffect, useMemo, useRef, useState } from 'react'
import './ui.css'

const SUPPORTS_POPOVER = typeof HTMLElement !== 'undefined' && 'showPopover' in HTMLElement.prototype
// A list this long is easier to filter than to scroll.
const SEARCH_FROM = 15
const PAGE = 8
const GAP = 4
const EDGE = 8

const textOf = (node) => {
  if (node == null || typeof node === 'boolean') return ''
  if (typeof node === 'string' || typeof node === 'number') return String(node)
  if (Array.isArray(node)) return node.map(textOf).join('')
  if (isValidElement(node)) return textOf(node.props.children)
  return ''
}

/** Reads <option> and <optgroup> children into a flat list of options, each knowing its group. */
const readOptions = (children, group = null, into = []) => {
  Children.forEach(children, (child) => {
    if (!isValidElement(child)) return
    if (child.type === Fragment) { readOptions(child.props.children, group, into); return }
    if (child.type === 'optgroup') {
      readOptions(child.props.children, { label: child.props.label, disabled: Boolean(child.props.disabled) }, into)
      return
    }
    if (child.type !== 'option') return
    const text = textOf(child.props.children)
    into.push({
      value: child.props.value !== undefined ? child.props.value : text,
      label: child.props.children,
      text,
      title: child.props.title,
      disabled: Boolean(child.props.disabled || group?.disabled),
      group
    })
  })
  return into
}

/** Options given as data rather than children: values, or { value, label, disabled, title, group }. */
const fromData = (options) => {
  const groups = new Map()
  return options.map((option) => {
    const entry = typeof option === 'object' && option !== null ? option : { value: option, label: String(option) }
    let group = null
    if (entry.group) {
      if (!groups.has(entry.group)) groups.set(entry.group, { label: entry.group, disabled: false })
      group = groups.get(entry.group)
    }
    return { value: entry.value, label: entry.label ?? String(entry.value), text: textOf(entry.label ?? entry.value), title: entry.title, disabled: Boolean(entry.disabled), group }
  })
}

const same = (a, b) => String(a ?? '') === String(b ?? '')
const fold = (text) => text.normalize('NFD').replace(/[̀-ͯ]/g, '').toLowerCase()
const cx = (...names) => names.filter(Boolean).join(' ')

const Chevron = () => (
  <svg className="ui-select__chevron" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true" focusable="false">
    <path d="M2.5 4.5 6 8l3.5-3.5" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

const Tick = () => (
  <svg className="ui-select__tick" viewBox="0 0 12 12" width="12" height="12" aria-hidden="true" focusable="false">
    <path d="M2.5 6.2 5 8.6l4.5-5" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
)

/**
 * @param {object} props
 * @param {*} props.value The chosen option's value. Compared as a string, as a native select does.
 * @param {(value: string) => void} props.onChange Called with the chosen option's value, as a string.
 * @param {React.ReactNode} [props.children] <option> and <optgroup> elements.
 * @param {Array} [props.options] Or the options as data, in place of children.
 * @param {React.ReactNode} [props.display] Drawn in the button in place of the chosen option's label.
 * @param {string} [props.placeholder] Shown when no option has the value.
 * @param {boolean} [props.searchable] Whether the list has a filter box; by default, from 15 options.
 * @param {string} [props.className] Classes for the button.
 * @param {string} [props.menuClassName] Classes for the list.
 */
export const Select = ({
  value,
  onChange,
  children,
  options: data,
  display,
  placeholder,
  searchable,
  disabled = false,
  className,
  menuClassName,
  id,
  title,
  style,
  'aria-label': ariaLabel,
  'aria-labelledby': ariaLabelledby,
  'aria-describedby': ariaDescribedby
}) => {
  const ownId = useId()
  const buttonId = id ?? `${ownId}-button`
  const listId = `${ownId}-list`
  const optionId = (index) => `${ownId}-option-${index}`

  const options = useMemo(() => (data ? fromData(data) : readOptions(children)), [data, children])
  const chosenIndex = options.findIndex((option) => same(option.value, value))
  // A native select with no matching option shows its first; a placeholder says so instead.
  const shown = chosenIndex >= 0 ? options[chosenIndex] : placeholder == null ? options[0] : null

  const [open, setOpen] = useState(false)
  // The option under the keyboard, as last set. What is shown as active is derived from it below, so
  // that filtering can never leave it pointing at an option that is no longer in the list.
  const [wanted, setActive] = useState(-1)
  const [query, setQuery] = useState('')
  const [above, setAbove] = useState(false)
  const button = useRef(null)
  const list = useRef(null)
  const search = useRef(null)
  const typed = useRef({ text: '', at: 0 })
  // Where the pointer last was. Chrome sends a pointermove when the list moves under a resting
  // pointer (as it does while filtering); only a real move should take the highlight.
  const pointer = useRef(null)

  const filterable = searchable ?? options.length >= SEARCH_FROM
  const visible = useMemo(() => {
    const words = fold(query.trim()).split(/\s+/).filter(Boolean)
    return options
      .map((option, index) => ({ option, index }))
      .filter(({ option }) => !words.length || words.every((word) => fold(option.text).includes(word)))
  }, [options, query])

  const enabled = useCallback((index) => index >= 0 && options[index] && !options[index].disabled, [options])
  const active = visible.some(({ index }) => index === wanted) ? wanted : visible.find(({ index }) => enabled(index))?.index ?? -1

  /** The next enabled visible option from `from`, `step` at a time; stops at the ends. */
  const move = (from, step) => {
    const order = visible.map(({ index }) => index)
    if (!order.length) return -1
    let at = order.indexOf(from)
    if (at < 0) at = step > 0 ? -1 : order.length
    let target = Math.max(0, Math.min(order.length - 1, at + step))
    const direction = step > 0 ? 1 : -1
    while (target >= 0 && target < order.length && !enabled(order[target])) target += direction
    if (target < 0 || target >= order.length) {
      // Nothing enabled that way: stay where we are, or settle on the nearest enabled one.
      return enabled(from) ? from : order.find(enabled) ?? -1
    }
    return order[target]
  }
  const edge = (last) => {
    const order = visible.map(({ index }) => index).filter(enabled)
    return (last ? order.at(-1) : order[0]) ?? -1
  }

  const openList = (startAt = chosenIndex) => {
    if (disabled || !options.length) return
    setQuery('')
    setActive(enabled(startAt) ? startAt : options.findIndex((_, i) => enabled(i)))
    setOpen(true)
  }

  const close = useCallback((refocus = true) => {
    setOpen(false)
    setQuery('')
    if (refocus) button.current?.focus({ preventScroll: true })
  }, [])

  const choose = (index) => {
    if (!enabled(index)) return
    close()
    if (!same(options[index].value, value)) onChange?.(String(options[index].value ?? ''))
  }

  // Typing a name moves to the first option that starts with it, as a native select does. Letters
  // typed in quick succession build up one search; the same letter again cycles through matches.
  const typeahead = (key) => {
    const now = Date.now()
    const state = typed.current
    state.text = now - state.at > 700 ? key : state.text + key
    state.at = now
    const cycling = state.text.length > 1 && [...state.text].every((letter) => letter === state.text[0])
    const needle = fold(cycling ? state.text[0] : state.text)
    // A fresh letter starts after the current option, so pressing it again moves on.
    const current = open ? active : chosenIndex
    const first = current < 0 ? 0 : current + (cycling || state.text.length === 1 ? 1 : 0)
    for (let i = 0; i < options.length; i += 1) {
      const index = (first + i) % options.length
      if (enabled(index) && fold(options[index].text).trimStart().startsWith(needle)) return index
    }
    return -1
  }

  const onKeyDown = (event) => {
    const { key } = event
    // Every key but Tab stays here, as it would in a native select: the views' own shortcuts
    // (arrows to step, Escape to leave) skip form fields, and this is one.
    if (key !== 'Tab') event.stopPropagation()
    if (!open) {
      if (key === 'ArrowDown' || key === 'ArrowUp' || key === 'Enter' || key === ' ') {
        event.preventDefault()
        openList()
      } else if (key.length === 1 && !event.metaKey && !event.ctrlKey && !event.altKey && key !== ' ') {
        const found = typeahead(key)
        if (found >= 0) openList(found)
      }
      return
    }
    const inSearch = event.target === search.current
    switch (key) {
      case 'ArrowDown': event.preventDefault(); if (!event.altKey) setActive(move(active, 1)); break
      case 'ArrowUp':
        event.preventDefault()
        if (event.altKey) choose(active)
        else setActive(move(active, -1))
        break
      case 'PageDown': event.preventDefault(); setActive(move(active, PAGE)); break
      case 'PageUp': event.preventDefault(); setActive(move(active, -PAGE)); break
      case 'Home': if (!inSearch) { event.preventDefault(); setActive(edge(false)) } break
      case 'End': if (!inSearch) { event.preventDefault(); setActive(edge(true)) } break
      case 'Enter': event.preventDefault(); choose(active); break
      case 'Escape': event.preventDefault(); close(); break
      case 'Tab': close(false); break
      case ' ':
        if (!inSearch) { event.preventDefault(); choose(active) }
        break
      default:
        if (!inSearch && key.length === 1 && !event.metaKey && !event.ctrlKey && !event.altKey) {
          const found = typeahead(key)
          if (found >= 0) setActive(found)
        }
    }
  }

  // Opening: lift the list into the top layer, place it, and hand the keyboard to the filter.
  useLayoutEffect(() => {
    const element = list.current
    if (!open || !element) return undefined
    if (SUPPORTS_POPOVER) { try { element.showPopover() } catch { /* already open */ } }

    const place = () => {
      const anchor = button.current
      if (!anchor) return
      const box = anchor.getBoundingClientRect()
      const viewport = window.visualViewport
      const width = viewport?.width ?? window.innerWidth
      const height = viewport?.height ?? window.innerHeight
      element.style.minWidth = `${Math.round(box.width)}px`
      element.style.maxWidth = `${Math.max(box.width, Math.min(width - EDGE * 2, 480))}px`
      element.style.maxHeight = ''
      const natural = Math.min(element.scrollHeight, 360)
      const below = height - box.bottom - GAP - EDGE
      const over = box.top - GAP - EDGE
      const flip = below < Math.min(natural, 200) && over > below
      const room = Math.max(120, flip ? over : below)
      element.style.maxHeight = `${Math.min(360, room)}px`
      const listHeight = Math.min(natural, room)
      const listWidth = element.offsetWidth
      const left = Math.min(Math.max(EDGE, box.left), Math.max(EDGE, width - listWidth - EDGE))
      element.style.left = `${Math.round(left)}px`
      element.style.top = `${Math.round(flip ? box.top - GAP - listHeight : box.bottom + GAP)}px`
      setAbove(flip)
    }
    place()

    let frame = 0
    const later = () => { cancelAnimationFrame(frame); frame = requestAnimationFrame(place) }
    window.addEventListener('resize', later)
    window.addEventListener('scroll', later, true)
    window.visualViewport?.addEventListener('resize', later)
    return () => {
      cancelAnimationFrame(frame)
      window.removeEventListener('resize', later)
      window.removeEventListener('scroll', later, true)
      window.visualViewport?.removeEventListener('resize', later)
      if (SUPPORTS_POPOVER) { try { element.hidePopover() } catch { /* already closed */ } }
    }
  }, [open, visible.length])

  // A phone's keyboard would cover half the list, so the filter takes focus only with a mouse.
  useEffect(() => {
    if (open && filterable && window.matchMedia?.('(pointer: fine)').matches) search.current?.focus({ preventScroll: true })
  }, [open, filterable])

  // Keep the active option in view as the keyboard moves through a long list.
  useEffect(() => {
    if (!open || active < 0) return
    document.getElementById(optionId(active))?.scrollIntoView({ block: 'nearest' })
  }, [open, active]) // eslint-disable-line react-hooks/exhaustive-deps

  // A press anywhere else closes the list, without taking the focus back from wherever it went.
  useEffect(() => {
    if (!open) return undefined
    const outside = (event) => {
      if (button.current?.contains(event.target) || list.current?.contains(event.target)) return
      // A press on the control's own <label> becomes a click on the button, which closes the list.
      if ([...(button.current?.labels ?? [])].some((label) => label.contains(event.target))) return
      close(false)
    }
    document.addEventListener('pointerdown', outside, true)
    return () => document.removeEventListener('pointerdown', outside, true)
  }, [open, close])

  // If the control disappears (or is disabled) while open, the list goes with it.
  useEffect(() => { if (disabled && open) close(false) }, [disabled, open, close])

  const groups = []
  for (const entry of visible) {
    const last = groups.at(-1)
    if (last && last.group === entry.option.group) last.entries.push(entry)
    else groups.push({ group: entry.option.group, entries: [entry] })
  }

  const renderOption = ({ option, index }) => {
    const chosen = index === chosenIndex
    return (
      <span
        key={index}
        id={optionId(index)}
        role="option"
        className="ui-select__option"
        aria-selected={chosen}
        aria-disabled={option.disabled || undefined}
        data-active={index === active || undefined}
        title={option.title}
        onPointerMove={(event) => {
          const last = pointer.current
          if (last && last.x === event.clientX && last.y === event.clientY) return
          pointer.current = { x: event.clientX, y: event.clientY }
          if (!option.disabled && index !== active) setActive(index)
        }}
        onClick={(event) => { event.preventDefault(); choose(index) }}
      >
        <span className="ui-select__option-label">{option.label}</span>
        {chosen && <Tick />}
      </span>
    )
  }

  const describedActive = open && active >= 0 ? optionId(active) : undefined

  return (
    <>
      <button
        ref={button}
        type="button"
        id={buttonId}
        role="combobox"
        className={cx('ui-select', className)}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={open ? listId : undefined}
        aria-activedescendant={describedActive}
        aria-label={ariaLabel}
        aria-labelledby={ariaLabelledby}
        aria-describedby={ariaDescribedby}
        data-open={open || undefined}
        data-placeholder={!shown || undefined}
        disabled={disabled}
        title={title}
        style={style}
        onClick={(event) => {
          pointer.current = { x: event.clientX, y: event.clientY }
          if (open) close()
          else openList()
        }}
        onKeyDown={onKeyDown}
      >
        <span className="ui-select__value">{display ?? (shown ? shown.label : placeholder)}</span>
        <Chevron />
      </button>
      {open && (
        <span
          ref={list}
          className={cx('ui-select__menu', menuClassName)}
          popover={SUPPORTS_POPOVER ? 'manual' : undefined}
          data-fallback={SUPPORTS_POPOVER ? undefined : true}
          data-above={above || undefined}
          // Clicks in the list stay in the list: a surrounding <label> would otherwise pass them on to
          // the button and open the list again.
          onClick={(event) => event.preventDefault()}
          onPointerDown={(event) => { if (event.target !== search.current) event.preventDefault() }}
          onKeyDown={onKeyDown}
        >
          {filterable && (
            <span className="ui-select__search">
              <input
                ref={search}
                type="search"
                role="combobox"
                aria-label="Filter the list"
                aria-expanded="true"
                aria-controls={listId}
                aria-autocomplete="list"
                aria-activedescendant={describedActive}
                placeholder="Type to filter…"
                autoComplete="off"
                spellCheck={false}
                value={query}
                onChange={(event) => setQuery(event.target.value)}
              />
            </span>
          )}
          <span
            id={listId}
            role="listbox"
            className="ui-select__list"
            aria-labelledby={ariaLabelledby ?? (ariaLabel ? undefined : buttonId)}
            aria-label={ariaLabel}
            tabIndex={-1}
          >
            {groups.map(({ group, entries }, at) => (group ? (
              <span key={`${group.label}-${at}`} role="group" aria-label={group.label} className="ui-select__group">
                <span className="ui-select__group-label" aria-hidden="true">{group.label}</span>
                {entries.map(renderOption)}
              </span>
            ) : <Fragment key={`loose-${at}`}>{entries.map(renderOption)}</Fragment>))}
            {!visible.length && <span className="ui-select__empty">Nothing matches “{query.trim()}”.</span>}
          </span>
        </span>
      )}
    </>
  )
}
