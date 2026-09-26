// Light or dark, for the whole site.
//
// One choice rather than one per view: the generator, the gallery and the government diagram share
// a page and a palette, and a toggle that flipped only the view it sat in would leave the next view
// in the other theme. The choice is held in a small store outside React, so every component that
// asks — the masthead's toggle, the diagram's — sees the same answer and re-renders together.
//
// Until a choice is made the system's preference decides, and changes to it are followed. The
// answer is written to <html data-theme>, which is what site.css keys its palette on.

import { useEffect, useSyncExternalStore } from 'react'

export const THEME_KEY = 'pofbc-theme'
// The diagram had its own toggle before the site did; a choice made there is carried over.
const LEGACY_KEY = 'pofbc-government-theme'

const valid = (value) => (value === 'light' || value === 'dark' ? value : null)

const readChoice = () => {
  try {
    const storage = globalThis.localStorage
    return valid(storage?.getItem(THEME_KEY)) ?? valid(storage?.getItem(LEGACY_KEY))
  } catch {
    // Storage can be refused outright (a sandboxed frame, some private modes); the system decides.
    return null
  }
}

const media = globalThis.matchMedia?.('(prefers-color-scheme: dark)') ?? null
let chosen = readChoice()
const listeners = new Set()

const current = () => chosen ?? (media?.matches ? 'dark' : 'light')
const emit = () => { for (const listener of listeners) listener() }

const apply = (name) => {
  if (globalThis.document) document.documentElement.dataset.theme = name
}

// Set as soon as this module loads, before the first render, so the page does not paint in the
// system's theme and then switch.
apply(current())

const subscribe = (listener) => {
  listeners.add(listener)
  const onSystem = () => emit()
  // Another tab choosing a theme is a choice made here too.
  const onStorage = (event) => {
    if (event.key !== THEME_KEY) return
    chosen = valid(event.newValue)
    emit()
  }
  media?.addEventListener('change', onSystem)
  globalThis.addEventListener?.('storage', onStorage)
  return () => {
    listeners.delete(listener)
    media?.removeEventListener('change', onSystem)
    globalThis.removeEventListener?.('storage', onStorage)
  }
}

const toggle = () => {
  chosen = current() === 'dark' ? 'light' : 'dark'
  try {
    globalThis.localStorage?.setItem(THEME_KEY, chosen)
  } catch {
    // Not remembered, but still applied for this visit.
  }
  emit()
}

/** @returns {{name: 'light'|'dark', toggle: () => void}} */
export const useSiteTheme = () => {
  const name = useSyncExternalStore(subscribe, current, () => 'light')
  useEffect(() => { apply(name) }, [name])
  return { name, toggle }
}
