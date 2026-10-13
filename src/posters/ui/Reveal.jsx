// Shared entrance choreography for panel content: children arrive in order, a beat apart.

import { motion } from 'motion/react'

export const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.055, delayChildren: 0.12 } }
}

export const item = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { duration: 0.5, ease: [0.2, 0.7, 0.2, 1] } }
}

export const Reveal = ({ children, className }) => (
  <motion.div className={className} variants={container} initial="hidden" animate="show">
    {children}
  </motion.div>
)

export const Item = ({ as = 'div', children, ...rest }) => {
  const Tag = motion[as]
  return <Tag variants={item} {...rest}>{children}</Tag>
}

/** Label / value rows. `rows` is [[label, value], …]. */
export const Facts = ({ rows }) => (
  <Item as="dl" className="pv-facts">
    {rows.map(([k, v]) => [<dt key={`${k}-k`}>{k}</dt>, <dd key={`${k}-v`}>{v}</dd>])}
  </Item>
)
