// Where the era brands are read from and written to.
//
//   brandkit/sources/<id>/   what an era's generator starts from (fonts, licences, artwork, notes),
//                            committed
//   brandkit/shared/fonts/   TeX Gyre Heros and Cursor, copied into every era's fonts/
//   <out>/<id>/              the brand folder the generator writes: brand.json and every file it
//                            lists. <out> is brandkit/out/brands unless BRANDKIT_OUT says otherwise.
//
// The engine is brandkit itself, the submodule at vendor/brandkit.

import { resolve } from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

export const ROOT = fileURLToPath(new URL('../../../', import.meta.url))
export const BRANDKIT = resolve(ROOT, 'vendor/brandkit')
export const SOURCES = resolve(ROOT, 'brandkit/sources')
export const SHARED = resolve(ROOT, 'brandkit/shared')
export const OUT = resolve(ROOT, process.env.BRANDKIT_OUT ?? 'brandkit/out/brands')

/** The output folder for a brand, as a file: URL ending in a slash (what the generators expect). */
export const brandFolder = (id) => pathToFileURL(`${resolve(OUT, id)}/`)
/** A module in PofBC, by its path from the repository root. */
export const pofbc = (path) => import(pathToFileURL(resolve(ROOT, path)).href)
