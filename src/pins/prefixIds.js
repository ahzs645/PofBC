// The Interior University Society's drawings are served as they were supplied (public/unbc-origins/),
// with generic ids such as "title" and "artwork". On the stage each is given a prefix, so it can sit
// on a page beside another drawing without a collision, and its title loses the " - " separator.

/** `raw` with every id, and every reference to one, prefixed. */
export const prefixIds = (raw, prefix) => raw
  .replace(/ id="([^"]+)"/g, (_, id) => ` id="${prefix}${id}"`)
  .replace(/ aria-labelledby="([^"]+)"/g, (_, ids) => ` aria-labelledby="${ids.split(/\s+/).map((id) => prefix + id).join(' ')}"`)
  .replace(/url\(#([^)]+)\)/g, (_, id) => `url(#${prefix}${id})`)
  .replace(/ (xlink:)?href="#([^"]+)"/g, (_, xlink = '', id) => ` ${xlink}href="#${prefix}${id}"`)
  .replace(/(<title[^>]*>[^<]*?) - /, '$1: ')
