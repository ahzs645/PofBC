// Small glyphs shared by the site's views: the sun that heads every breadcrumb, and the icons of
// the light and dark toggle. Drawn in currentColor unless told otherwise, so each view colours them
// from its own palette.

/** The seal at the centre of the government diagram, small: the site's favicon, in effect. */
const SUN_PATH = (() => {
  const points = Array.from({ length: 64 }, (_, index) => {
    const theta = (index / 64) * Math.PI * 2
    const r = 7.6 + Math.sin(theta * 12) * 1.1
    return `${(10 + Math.cos(theta) * r).toFixed(2)},${(10 + Math.sin(theta) * r).toFixed(2)}`
  })
  return `M${points.join('L')}Z`
})()

export const SunGlyph = ({ fill = 'currentColor', className }) => (
  <svg className={className} viewBox="0 0 20 20" width="20" height="20" aria-hidden="true">
    <path d={SUN_PATH} fill={fill} />
  </svg>
)

export const MoonIcon = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
    <path d="M13.5 9.6A5.8 5.8 0 0 1 6.4 2.5a5.8 5.8 0 1 0 7.1 7.1Z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
  </svg>
)

export const SunIcon = () => (
  <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
    <circle cx="8" cy="8" r="3" stroke="currentColor" strokeWidth="1.4" />
    <path d="M8 1v1.6M8 13.4V15M1 8h1.6M13.4 8H15M3.05 3.05l1.13 1.13M11.82 11.82l1.13 1.13M3.05 12.95l1.13-1.13M11.82 4.18l1.13-1.13" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
  </svg>
)

/** The toggle's icon shows where it goes, not where the page is: a moon on light, a sun on dark. */
export const ThemeIcon = ({ name }) => (name === 'dark' ? <SunIcon /> : <MoonIcon />)
