import { useState } from 'react'
import { AnimatePresence, motion } from 'motion/react'
import { Swatches } from '../../ui/Swatches.jsx'
import { POSTER_BLACK, PREVIEW_BACKGROUNDS } from './renderLogo.js'

/** A logo (SVG string) on a switchable background, cross-fading whenever it changes. */
export const LogoPreview = ({ svg, contrastFor, backgrounds = PREVIEW_BACKGROUNDS, initial = POSTER_BLACK, minRatio = 3 }) => {
  const [background, setBackground] = useState(initial)
  const ratio = contrastFor?.(background)
  return (
    <>
      <div className="pv-preview" style={{ background }}>
        <AnimatePresence mode="popLayout" initial={false}>
          <motion.div
            key={svg}
            className="pv-preview-art"
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 1.02 }}
            transition={{ duration: 0.28 }}
            dangerouslySetInnerHTML={{ __html: svg }}
          />
        </AnimatePresence>
        <div className="pv-preview-bgs">
          <Swatches value={background} onChange={setBackground} swatches={backgrounds} hex={false} small />
        </div>
      </div>
      {ratio != null && ratio < minRatio && (
        <p className="pv-contrast-warn">Contrast on this background is {ratio.toFixed(1)}:1. The Province's guidance wants at least {minRatio}:1 for a mark.</p>
      )}
    </>
  )
}
