// What a part's panel shows before "Read more" is pressed (DataPanel.jsx).
//
// A panel's blocks are prose, caveats and sources mixed with things that can be taken in at a look:
// a table of facts, the colours, a picture, links. At a glance the panel keeps the second kind and
// holds the first back. Nothing is reordered, so the full reading is the blocks exactly as written.

const scannable = (block) => typeof block !== 'string' && Boolean(block.facts || block.palette || block.figure || block.links)

/**
 * The blocks shown at a glance, and how many are held back. Only the first table of facts is kept;
 * a heading is kept when the block it heads is.
 */
export const glance = (blocks) => {
  let facts = 0
  const keeps = blocks.map((block) => {
    if (typeof block === 'string' || !scannable(block)) return false
    if (block.facts) return facts++ === 0
    return true
  })
  const kept = blocks.filter((block, i) => (typeof block !== 'string' && block.h ? keeps[i + 1] === true : keeps[i]))
  return { kept, held: blocks.length - kept.length }
}
