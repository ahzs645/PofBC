import { motion } from 'motion/react'
import { MINISTRY_NAMES, SOURCES } from '../history.jsx'
import { LogoStudio } from '../logo/LogoStudio.jsx'
import { Item, Reveal, item } from '../../ui/Reveal.jsx'

export function Logo({ config, onConfig, live, onLive, onExport }) {
  const crest = config.era === 'crest'
  return (
    <Reveal>
      <Item as="p" className="pv-eyebrow">Part 4 of 5 · The logo</Item>
      <Item as="h2">The crest the Province <em>used before the sun</em></Item>
      <Item as="p" className="pv-lede">A rounded square holding the arms of British Columbia, then "Province of British Columbia" in bold Helvetica, then the ministry in regular. This is the identity the Province ran on its signage, letterhead and posters through the 1970s and 80s. Change anything below and the poster follows.</Item>

      <Item as="div">
        <LogoStudio config={config} onChange={onConfig} live={live} onLive={onLive} onExport={onExport} />
      </Item>

      {crest ? (
        <>
          <Item as="h3">What is in the crest</Item>
          <Item as="p">The whole coat of arms, simplified to one weight of line. A wapiti stag for Vancouver Island and a bighorn sheep for the mainland hold the shield, recalling the union of the two colonies in 1866. Above it a lion stands on a crown wearing a garland of Pacific dogwood. Underneath, the motto <i>Splendor sine occasu</i>: splendour without diminishment.</Item>
          <Item as="p">Canon Arthur Beanlands of Christ Church Cathedral in Victoria designed the arms in the 1890s. The shield was granted by Edward VII in 1906, but the crest, supporters and motto you see here were used for decades before Elizabeth II formally granted the complete arms in 1987. On this poster they are still, strictly, unofficial.</Item>

          <Item as="h3">Dating the poster from the wording</Item>
          <Item as="p">The ministry has been renamed many times, and the lockup says exactly <b>Ministry of Environment</b>, with no "the" and no "and Parks". Only one span of years fits.</Item>
          <motion.ol className="pv-timeline" variants={item}>
            {MINISTRY_NAMES.map(({ year, text, here }) => (
              <motion.li key={year} className={here ? 'pv-here' : undefined} variants={item}>
                <time>{year}</time><span>{text}</span>
              </motion.li>
            ))}
          </motion.ol>

          <Item as="h3">The four lockups</Item>
          <Item as="p">The identity came as a kit. Three of the arrangements survive as Illustrator files, each set slightly differently by hand, and the generator keeps those differences rather than averaging them. The side-by-side one on this poster does not survive as a file: it was reconstructed from a photograph of signage, borrowing its type size from the horizontal lockup.</Item>
          <Item as="p">The type is real Helvetica, verified from the advance widths in the source files. Here it is drawn as outlines from the generator's own glyph table, so nothing on this page depends on the font being installed.</Item>
        </>
      ) : (
        <>
          <Item as="h3">The rising sun</Item>
          <Item as="p">In 2005 the Province replaced the crest identity with a mark of a gold sun rising over blue mountains, with the tagline "The Best Place on Earth" underneath. The 2011 version dropped the tagline and is the one in use now; a compact "BC" form followed for social media in 2017.</Item>
          <Item as="p">The ministry name beside it is set in a Garamond. The Province's guidelines ask that the artwork be used exactly as published, so the mark itself is the published drawing, unchanged; only the wording beside it is set live, from the alphabet those published names were lettered with.</Item>
          <Item as="h3">Four official colourways</Item>
          <Item as="p"><b>Colour</b> is the mark as drawn, for white and light grounds. <b>Reverse</b> lightens the mountains to a 60 percent blue and turns the type white, for BC Blue and black. The two <b>solid</b> versions drop the sun's rays entirely so the background shows through them; painting the rays white would ring the mark with a halo on anything but a white page.</Item>
        </>
      )}

      <Item as="div" className="pv-sources">
        Sources for the dates:
        <ul>
          {SOURCES.map((s) => <li key={s.href}><a href={s.href} target="_blank" rel="noopener">{s.label}</a> ({s.note})</li>)}
          <li>Lockups and current marks are rendered live by the PofBC generator.</li>
        </ul>
      </Item>
    </Reveal>
  )
}
