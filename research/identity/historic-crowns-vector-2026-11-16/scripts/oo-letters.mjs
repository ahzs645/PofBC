import { ONE_OFF_MARKS } from '/home/user/PofBC/src/assets/oneOffMarks.js'
import { lettersOf } from '/home/user/PofBC/scripts/glyphs.mjs'
const [id, role] = process.argv.slice(2)
const shape = ONE_OFF_MARKS[id].shapes.find((s) => s.role === role)
lettersOf(shape.d).forEach((l, i) => console.log(i, ['left', 'top', 'right', 'bottom'].map((k) => l.box[k].toFixed(2)).join(' '), 'w', (l.box.right - l.box.left).toFixed(2), 'h', (l.box.bottom - l.box.top).toFixed(2), 'n', l.subpaths.length))
