import { motion } from 'motion/react'
import { Item, item } from './Reveal.jsx'

/** Cards for glyphs lifted out of a drawing with extractGlyphs(). */
export const GlyphRow = ({ glyphs, fill = '#eee3c0' }) => (
  <Item as="div" className="pv-glyph-row">
    {glyphs.map((g, i) => (
      <motion.div key={g.key} className="pv-glyph" variants={item} whileHover={{ y: -3 }} transition={{ delay: i * 0.04 }}>
        <svg viewBox={g.viewBox} aria-hidden="true"><path d={g.d} transform={g.transform} fill={fill} /></svg>
        <b>{g.name}</b>
        <span>{g.letter} · {g.where}</span>
        <span>glyph {g.id}</span>
      </motion.div>
    ))}
  </Item>
)
