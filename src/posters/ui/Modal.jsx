import { useLayoutEffect, useRef } from 'react'

// At a dialog boundary Chromium may otherwise send Tab to the browser chrome.
function keepTabInside(event) {
  const dialog = event.currentTarget
  if (event.key !== 'Tab' || event.target.closest('dialog') !== dialog) return
  const controls = [...dialog.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]')]
    .filter((node) => node.tabIndex >= 0 && !node.matches(':disabled') && node.getClientRects().length
      && !node.closest('[hidden], [inert]') && getComputedStyle(node).visibility === 'visible')
  const first = controls[0]
  const last = controls.at(-1)
  if (!first || (event.shiftKey ? event.target === first : event.target === last)) {
    event.preventDefault()
    const next = event.shiftKey ? last : first
    next?.focus()
  }
}

/** Native modal dialogs make the rest of the page inert, including when the export is nested. */
export function Modal({ onDismiss, children, ...props }) {
  const ref = useRef(null)
  useLayoutEffect(() => {
    const dialog = ref.current
    dialog.showModal()
    dialog.querySelector('[data-initial-focus]')?.focus({ preventScroll: true })
    return () => dialog.close()
  }, [])

  return (
    <dialog {...props} ref={ref} onKeyDown={keepTabInside} onCancel={(event) => {
      if (event.target !== ref.current) return
      event.preventDefault()
      onDismiss()
    }}>
      {children}
    </dialog>
  )
}
