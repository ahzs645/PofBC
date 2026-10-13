// Coastal Forest: the drawing, its parts, and what the viewer needs beyond a data panel per part —
// the live logo studio, the glyph highlights, and zooming the copy section by section.

import { useEffect, useMemo, useState } from 'react'
import posterRaw from './poster.svg?raw'
import forestPhoto from './forest.jpg'
import { useLayerSwap } from '../stage/useLayerSwap.js'
import { useGlyphReveal } from '../stage/useGlyphReveal.js'
import { useLayerDim } from '../stage/useLayerDim.js'
import { unionBox } from '../stage/zoom.js'
import { extractGlyphs } from '../stage/glyphs.js'
import { getGlyphOutlines } from '../../export/fontOutlines.js'
import { DEFAULT_LOGO, isOriginalLogo, logoTag, renderLogo, setLogoOutlines } from './logo/renderLogo.js'
import { logoTarget } from './targets.js'
import { COPY_GROUPS, CREDIT_LAYER, GLYPH_NOTES, LOGO_SLOT, ORDER, PARTS, REGIONS, SECTIONS } from './parts.js'
import { Overview } from './panels/Overview.jsx'
import { Photograph } from './panels/Photograph.jsx'
import { Title } from './panels/Title.jsx'
import { Copy } from './panels/Copy.jsx'
import { Logo } from './panels/Logo.jsx'
import { Slogan } from './panels/Slogan.jsx'

// The drawing refers to its photograph by a bare file name; the bundle gives it a hashed one.
const prepare = (raw) => raw.replace('href="forest.jpg"', `href="${forestPhoto}"`)

function useCoastal({ svg, part, select, openExport, tour }) {
  const [sectionFocus, setSectionFocus] = useState(null)
  const [sectionZoom, setSectionZoom] = useState(null)
  const [hlTitle, setHlTitle] = useState(true)
  const [hlSlogan, setHlSlogan] = useState(true)
  const [logo, setLogo] = useState(DEFAULT_LOGO)
  const [logoLive, setLogoLive] = useState(true)

  // Leaving the copy lets go of its section.
  useEffect(() => { setSectionZoom(null); setSectionFocus(null) }, [part])

  // Layer effects on the poster itself.
  const logoSvg = useMemo(() => renderLogo(logo), [logo])
  const posterLogo = logoLive && !isOriginalLogo(logo) ? logoSvg : null
  useLayerSwap(svg, '#ministry', posterLogo, LOGO_SLOT)
  useGlyphReveal(svg, '#title path', part === 'title')
  useGlyphReveal(svg, '#slogan path', part === 'slogan')
  useGlyphReveal(svg, `${CREDIT_LAYER} use`, part === 'photograph', { each: 0.012, startDelay: 0.6 })
  useLayerDim(svg, COPY_GROUPS, sectionFocus ? SECTIONS[sectionFocus].matches : null)

  const glyphs = useMemo(() => svg ? {
    title: extractGlyphs(svg, '#title path[data-glyph$=".swsh"]', { unique: true, notes: GLYPH_NOTES }),
    slogan: extractGlyphs(svg, '#slogan path[data-glyph$=".swsh"], #slogan path[data-glyph="tilde"]', { notes: GLYPH_NOTES })
  } : { title: [], slogan: [] }, [svg])

  // The copy can be framed one section at a time.
  const frame = useMemo(() => {
    if (part === 'copy' && sectionZoom && svg) {
      const groups = [...svg.querySelectorAll(COPY_GROUPS)].filter(SECTIONS[sectionZoom].matches)
      return { box: unionBox(groups), pad: 0.08 }
    }
    return undefined
  }, [part, sectionZoom, svg])

  const className = (part === 'title' && hlTitle ? 'pv-hl-title ' : '') + (part === 'slogan' && hlSlogan ? 'pv-hl-slogan' : '')

  const content = {
    overview: <Overview onSelect={select} onTour={tour.toggle} touring={tour.playing} />,
    photograph: <Photograph />,
    title: <Title glyphs={glyphs.title} highlight={hlTitle} onHighlight={setHlTitle} />,
    copy: <Copy focus={sectionFocus} zoom={sectionZoom} onFocus={setSectionFocus} onZoom={setSectionZoom} />,
    logo: <Logo config={logo} onConfig={setLogo} live={logoLive} onLive={setLogoLive} onExport={() => openExport('logo')} />,
    slogan: <Slogan glyphs={glyphs.slogan} highlight={hlSlogan} onHighlight={setHlSlogan} />
  }[part]

  return {
    frame,
    className,
    content,
    posterTag: posterLogo ? logoTag(logo) : null,
    targets: [
      logoTarget({ getSvg: ({ background }) => renderLogo(logo, { background: background || 'none', clearSpace: background ? 0.25 : 0 }), tag: logoTag(logo) })
    ]
  }
}

const regionIds = REGIONS.map(({ id }) => id)

/** Resolves once the generator's glyph outlines are in hand, so the studio draws outlined type. */
export const load = async () => {
  setLogoOutlines(await getGlyphOutlines())
  return {
    svgRaw: posterRaw,
    prepare,
    parts: PARTS,
    order: ORDER,
    regions: regionIds,
    spotlight: { keep: ['background'] },
    useExtras: useCoastal
  }
}
