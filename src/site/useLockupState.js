// The generator's single piece of state, plus the small amount of logic that keeps it coherent.

import { useCallback, useEffect, useMemo, useState } from 'react'
import { clearSpaceFactor, clearSpacePadding } from '../logo/layouts.js'
import { BRAND_COLORS, TRANSPARENT, describeContrast, isLightColor, resolveColor } from '../logo/logoColors.js'
import { DEFAULTS } from './lockupDefaults.js'
import { applyShare, applyUpdate, swapColours } from './lockupReducer.js'
import { codeForName } from './ministryLink.js'
import { readConfigParam } from './configFormat.js'
import { decodeShare, readShareToken } from './shareLink.js'

/** The viewing surface and contrast of the parts actually present in the selected artwork. */
export const getPreviewAppearance = (state) => {
  const background = state.era === 'document'
    ? state.documentBackground
    : state.era === 'current'
      ? state.currentBackground
      : state.era === 'flag'
        ? state.flagBackground
        : state.era === 'crest'
          ? state.crestBackground
          : state.background
  const isTransparent = resolveColor(background, TRANSPARENT) === TRANSPARENT
  const ink = state.era === 'document'
    ? { mark: state.documentMarkColor, text: state.linkColors ? state.documentMarkColor : state.documentTextColor }
    : state.era === 'flag'
      ? { mark: state.flagMarkColor, text: state.linkColors ? state.flagMarkColor : state.flagTextColor }
      : state.era === 'crest'
        ? { mark: state.crestMarkColor, text: state.linkColors ? state.crestMarkColor : state.crestTextColor }
        : { mark: state.markColor, text: state.textColor }
  const hasText = state.era !== 'document' || state.documentLayout !== 'emblem'

  const against = (surface) => {
    const mark = describeContrast(ink.mark, surface)
    // Arms alone retains the lettering settings for the next heading, but that absent lettering
    // must not trigger a contrast warning or choose a dark surface for otherwise black arms.
    if (!hasText) return { ...mark, part: 'mark', differs: false }
    const text = describeContrast(ink.text, surface)
    const worst = (mark.ratio ?? Infinity) <= (text.ratio ?? Infinity) ? mark : text
    return { ...worst, part: worst === mark ? 'mark' : 'text', differs: mark.ratio !== text.ratio }
  }
  const contrast = isTransparent
    ? [
        { surface: 'On white', ...against(BRAND_COLORS.white) },
        { surface: 'On black', ...against(BRAND_COLORS.black) }
      ]
    : [{ surface: 'Against the background', ...against(background) }]

  // The current identity takes its ink from the published colourway. Other identities use their
  // visible colours; Auto has no effect on exported artwork or its requested background.
  const inkIsLight = state.era === 'current'
    ? ['reverse', 'white'].includes(state.currentVariant)
    : isLightColor(ink.mark) || (hasText && isLightColor(ink.text))
  const backdrop = state.backdrop !== 'auto'
    ? state.backdrop
    : isTransparent && inkIsLight ? 'dark' : 'light'
  return { background, isTransparent, contrast, backdrop }
}

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
  // What the historical renderer draws. Kept apart from `lockup` below because BcLockup forwards
  // anything it does not recognise to the <svg> element, and the current era's fields are not
  // drawing options — handing it the whole object put them in the DOM.
  const artwork = useMemo(() => ({
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

  // Everything an export needs, for each identity.
  // Each era draws on its own background, so everything downstream — preview, export, backdrop,
  // contrast — reads it from here rather than reaching for state.background directly.
  const { background, isTransparent, contrast, backdrop } = useMemo(
    () => getPreviewAppearance(state), [state]
  )

  const lockup = useMemo(() => ({
    era: state.era,
    documentLayout: state.documentLayout,
    documentMarkColor: state.documentMarkColor,
    documentTextColor: state.linkColors ? state.documentMarkColor : state.documentTextColor,
    documentBackground: state.documentBackground,
    language: state.language,
    // Only while the chosen name is still one of the published marks. A name typed by hand has no
    // code, and an export named after a stale one would be a lie about what is inside it.
    currentMinistry: codeForName(state.source === 'manual' ? state.manualMinistry : state.ministry)
      ? state.currentMinistry
      : '',
    // The wording the mark is set with. It was missing here, so every current-era download came
    // out as the mark alone while the preview beside it showed the name.
    currentName: state.currentName,
    currentVariant: state.currentVariant,
    currentBackground: state.currentBackground,
    // The key rather than a distance: the two eras measure their marks in different units, so each
    // turns it into a margin against its own artwork.
    clearSpace: state.clearSpace,
    clearSpaceFactor: clearSpaceFactor(state.clearSpace),
    layout: state.layout,
    wordmark: state.wordmark,
    ministry: (state.source === 'manual' ? state.manualMinistry : state.ministry).trim(),
    program: state.program.trim(),
    markColor: state.markColor,
    textColor: state.textColor,
    flagPalette: state.flagPalette,
    flagBackground: state.flagBackground,
    flagMarkColor: state.flagMarkColor,
    flagTextColor: state.linkColors ? state.flagMarkColor : state.flagTextColor,
    crestArrangement: state.crestArrangement,
    crestPlacement: state.crestPlacement,
    crestBold: state.crestBold,
    crestAlign: state.crestAlign,
    crestMinistrySize: state.crestMinistrySize,
    crestExtraStep: state.crestExtraStep,
    crestExtra: state.crestExtra.trim(),
    crestMarkColor: state.crestMarkColor,
    crestTextColor: state.linkColors ? state.crestMarkColor : state.crestTextColor,
    crestBackground: state.crestBackground,
    flagSymbol: state.flagSymbol,
    flagPlacement: state.flagPlacement,
    flagProvince: state.flagProvince,
    flagExtra: state.flagExtra.trim(),
    background,
    padding: clearSpacePadding(state.clearSpace),
    markAlign: state.markAlign
  }), [state, background])

  const swapColors = useCallback(() => setState(swapColours), [])

  return { state, update, reset, lockup, artwork, background, contrast, backdrop, isTransparent, swapColors }
}

export { DEFAULTS }
