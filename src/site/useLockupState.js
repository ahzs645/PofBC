// The generator's single piece of state, plus the small amount of logic that keeps it coherent.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { clearSpacePadding } from '../logo/layouts.js'
import { BRAND_COLORS, TRANSPARENT, describeContrast, isLightColor, resolveColor } from '../logo/logoColors.js'
import { DEFAULTS } from './lockupDefaults.js'
import { applyShare, applyUpdate, swapColours } from './lockupReducer.js'
import { readConfigParam } from './configFormat.js'
import { decodeShare, readShareToken } from './shareLink.js'

export const useLockupState = () => {
  const [state, setState] = useState(DEFAULTS)

  // A shared link restores its configuration on arrival. Decoding is asynchronous, so the page
  // paints the defaults for a frame first; the alternative is holding the whole UI back behind a
  // decompression, which is worse for the overwhelmingly common case of no link at all.
  useEffect(() => {
    // A plain-JSON configuration is applied immediately — it needs no decompression, and it is the
    // form an agent can write by hand into a link.
    const config = readConfigParam()
    if (config) setState((current) => applyShare(current, config))

    const token = readShareToken()
    if (!token) return

    let cancelled = false
    decodeShare(token).then((patch) => {
      if (!cancelled && patch) setState((current) => applyShare(current, patch))
    })

    return () => { cancelled = true }
  }, [])

  const update = useCallback((patch) => {
    setState((current) => applyUpdate(current, patch))
  }, [])

  const reset = useCallback(() => setState(DEFAULTS), [])

  // What the renderer is handed, as opposed to what the form is holding.
  const lockup = useMemo(() => ({
    layout: state.layout,
    wordmark: state.wordmark,
    ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
    program: state.program.trim(),
    markColor: state.markColor,
    textColor: state.textColor,
    background: state.background,
    padding: clearSpacePadding(state.clearSpace),
    markAlign: state.markAlign
  }), [state])

  const isTransparent = resolveColor(state.background, TRANSPARENT) === TRANSPARENT

  /**
   * How the lockup reads.
   *
   * A transparent export has no background of its own, so the honest answer is not one number but
   * two: it is going to land on something, and light and dark surfaces give opposite results. The
   * worse of the mark and the type is reported for each, since a lockup is only as legible as its
   * least legible half.
   */
  const contrast = useMemo(() => {
    const against = (surface) => {
      const mark = describeContrast(state.markColor, surface)
      const text = describeContrast(state.textColor, surface)
      const worst = (mark.ratio ?? Infinity) <= (text.ratio ?? Infinity) ? mark : text
      return { ...worst, part: worst === mark ? 'mark' : 'text', differs: mark.ratio !== text.ratio }
    }

    return isTransparent
      ? [
          { surface: 'On white', ...against(BRAND_COLORS.white) },
          { surface: 'On black', ...against(BRAND_COLORS.black) }
        ]
      : [{ surface: 'Against the background', ...against(state.background) }]
  }, [state.markColor, state.textColor, state.background, isTransparent])

  /**
   * The preview surface.
   *
   * On 'auto' this follows the artwork: a white lockup on a transparent background is invisible on
   * a light page, which is the one case where the preview actively misleads. Flipping the surface
   * dark is the fix, and it is the answer to "what happens if this lands on white" too — the
   * contrast readout above says so in numbers, this shows it.
   */
  const backdrop = useMemo(() => {
    if (state.backdrop !== 'auto') return state.backdrop
    const inkIsLight = isLightColor(state.markColor) || isLightColor(state.textColor)
    return isTransparent && inkIsLight ? 'dark' : 'light'
  }, [state.backdrop, state.markColor, state.textColor, isTransparent])

  const swapColors = useCallback(() => setState(swapColours), [])

  return { state, update, reset, lockup, contrast, backdrop, isTransparent, swapColors }
}

export { DEFAULTS }
