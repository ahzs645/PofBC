// Minimal sfnt (TrueType/OpenType) surgery: enough to get one usable face out of macOS's Helvetica.
//
// Two things need doing that no library on npm does for us:
//
//   extractFace()    macOS ships Helvetica as a .ttc — several faces sharing one file and, where
//                    the bytes are identical, sharing table data between them. Neither harfbuzz
//                    nor a browser @font-face will take a face out of a collection.
//
//   withNames()      harfbuzz's subsetter discards all but one `name` record. jsPDF's TrueType
//                    parser reads the PostScript name (ID 6) and dereferences the result without
//                    checking, so a subset font makes it throw before it ever writes a glyph.
//
// Both are the same underlying operation — rebuild the file from a set of tables — so they share
// buildFont() below.

const TTC_TAG = 0x74746366 // 'ttcf'

const tag = (buffer, offset) => buffer.toString('latin1', offset, offset + 4)

/** Byte offsets of each face's table directory, or [0] for a plain (non-collection) font. */
export const collectionOffsets = (buffer) => {
  if (buffer.readUInt32BE(0) !== TTC_TAG) return [0]

  const count = buffer.readUInt32BE(8)
  return Array.from({ length: count }, (_, i) => buffer.readUInt32BE(12 + i * 4))
}

/** `{ postscriptName }` for each face, so callers can select by name rather than index. */
export const collectionFaceNames = (buffer) => collectionOffsets(buffer)
  .map((offset) => ({ offset, postscriptName: readPostscriptName(buffer, offset) }))

// Table directory entries are fixed-width records of tag/checksum/offset/length.
const readTableRecords = (buffer, directoryOffset) => {
  const numTables = buffer.readUInt16BE(directoryOffset + 4)
  const records = []

  for (let i = 0; i < numTables; i += 1) {
    const at = directoryOffset + 12 + i * 16
    records.push({
      tag: tag(buffer, at),
      checksum: buffer.readUInt32BE(at + 4),
      offset: buffer.readUInt32BE(at + 8),
      length: buffer.readUInt32BE(at + 12)
    })
  }

  return records
}

// The PostScript name (name ID 6) is the only identifier that reliably distinguishes
// "Helvetica" from "Helvetica-Bold" across platforms, so face selection keys off it.
const readPostscriptName = (buffer, directoryOffset) => {
  const record = readTableRecords(buffer, directoryOffset).find((entry) => entry.tag === 'name')
  if (!record) return null

  const base = record.offset
  const count = buffer.readUInt16BE(base + 2)
  const storage = base + buffer.readUInt16BE(base + 4)

  for (let i = 0; i < count; i += 1) {
    const at = base + 6 + i * 12
    if (buffer.readUInt16BE(at + 6) !== 6) continue // nameID 6 = PostScript name

    const platformId = buffer.readUInt16BE(at)
    const length = buffer.readUInt16BE(at + 8)
    const offset = storage + buffer.readUInt16BE(at + 10)
    // Platform 3 (Windows) stores UTF-16BE; platform 1 (Macintosh) stores single bytes.
    const encoding = platformId === 3 ? 'utf16le' : 'latin1'
    const slice = buffer.subarray(offset, offset + length)

    return encoding === 'utf16le' ? swap16(slice).toString('utf16le') : slice.toString('latin1')
  }

  return null
}

const swap16 = (slice) => {
  const copy = Buffer.from(slice)
  copy.swap16()
  return copy
}

/** Every table of a face, as `{ tag: Buffer }`. */
const readTables = (buffer, directoryOffset) => Object.fromEntries(
  readTableRecords(buffer, directoryOffset)
    .map((record) => [record.tag, buffer.subarray(record.offset, record.offset + record.length)])
)

const align4 = (value) => (value + 3) & ~3

/**
 * Writes a set of tables out as a standalone font file.
 *
 * Table checksums are recomputed rather than carried over, since a rebuilt or replaced table
 * invalidates the original value. The whole-file checksum in `head` is left alone: it is advisory,
 * no rasteriser this project touches verifies it, and computing it correctly requires a second
 * pass to patch a field that is itself part of the sum.
 */
const buildFont = (sfntVersion, tables) => {
  const tags = Object.keys(tables).sort()
  const headerSize = 12 + tags.length * 16

  // Every table must start on a 4-byte boundary, so they are laid out with padding between.
  let cursor = headerSize
  const placed = tags.map((tag) => {
    const entry = { tag, data: tables[tag], offset: cursor }
    cursor += align4(entry.data.length)
    return entry
  })

  const output = Buffer.alloc(cursor)
  output.writeUInt32BE(sfntVersion, 0)
  output.writeUInt16BE(placed.length, 4)
  // The binary-search hints the spec requires. Readers rarely use them, but validators and some
  // rasterisers do check that they are self-consistent.
  const entrySelector = Math.floor(Math.log2(placed.length))
  const searchRange = 2 ** entrySelector * 16
  output.writeUInt16BE(searchRange, 6)
  output.writeUInt16BE(entrySelector, 8)
  output.writeUInt16BE(placed.length * 16 - searchRange, 10)

  placed.forEach((entry, index) => {
    const at = 12 + index * 16
    output.write(entry.tag, at, 4, 'latin1')
    output.writeUInt32BE(checksum(entry.data), at + 4)
    output.writeUInt32BE(entry.offset, at + 8)
    output.writeUInt32BE(entry.data.length, at + 12)
    entry.data.copy(output, entry.offset)
  })

  return output
}

// The sum of a table's contents as big-endian uint32s, with the tail zero-padded.
const checksum = (data) => {
  let sum = 0
  for (let i = 0; i < data.length; i += 4) {
    sum = (sum + ((data[i] << 24) | (data[i + 1] << 16) | (data[i + 2] << 8) | (data[i + 3] || 0))) >>> 0
  }
  return sum
}

/**
 * Extracts one face from a collection as a standalone sfnt buffer.
 *
 * @param {Buffer} buffer          The .ttc (or plain .ttf/.otf) file.
 * @param {string} postscriptName  e.g. 'Helvetica-Bold'.
 * @returns {Buffer} A self-contained font file.
 */
export const extractFace = (buffer, postscriptName) => {
  const faces = collectionFaceNames(buffer)
  const face = faces.find((entry) => entry.postscriptName === postscriptName)

  if (!face) {
    const available = faces.map((entry) => entry.postscriptName).join(', ')
    throw new Error(`No face named "${postscriptName}" in this font. Available: ${available}`)
  }

  return buildFont(buffer.readUInt32BE(face.offset), readTables(buffer, face.offset))
}

/** Reads one name record out of a font, or null. */
export const readName = (buffer, nameId) => {
  const tables = readTables(buffer, 0)
  const name = tables.name
  if (!name) return null

  const count = name.readUInt16BE(2)
  const storage = name.readUInt16BE(4)

  for (let i = 0; i < count; i += 1) {
    const at = 6 + i * 12
    if (name.readUInt16BE(at + 6) !== nameId) continue

    const platformId = name.readUInt16BE(at)
    const length = name.readUInt16BE(at + 8)
    const offset = storage + name.readUInt16BE(at + 10)
    const slice = name.subarray(offset, offset + length)

    if (platformId === 3) {
      const copy = Buffer.from(slice)
      copy.swap16()
      return copy.toString('utf16le')
    }
    return slice.toString('latin1')
  }

  return null
}

// Name records are emitted for both the Macintosh and Windows platforms. Readers are inconsistent
// about which they consult — jsPDF walks whatever it finds first — and between them these two
// cover everything that will open these files.
const NAME_PLATFORMS = [
  { platformId: 1, encodingId: 0, languageId: 0, encode: (value) => Buffer.from(value, 'latin1') },
  {
    platformId: 3,
    encodingId: 1,
    languageId: 0x0409,
    encode: (value) => {
      const buffer = Buffer.from(value, 'utf16le')
      buffer.swap16()
      return buffer
    }
  }
]

/**
 * Replaces a font's `name` table with one built from `names`, a map of name ID to string.
 *
 * Subsetting leaves the font with a single name record, which is both useless to a human opening
 * the file and fatal to jsPDF. This puts back a complete, minimal set under a family of our own
 * choosing, so the embedded face identifies itself rather than impersonating the system Helvetica.
 */
export const withNames = (buffer, names) => {
  const entries = []

  for (const platform of NAME_PLATFORMS) {
    for (const [nameId, value] of Object.entries(names)) {
      if (value == null) continue
      entries.push({ ...platform, nameId: Number(nameId), data: platform.encode(String(value)) })
    }
  }

  // The spec requires records sorted by platform, encoding, language, then name ID.
  entries.sort((a, b) => (
    a.platformId - b.platformId || a.encodingId - b.encodingId ||
    a.languageId - b.languageId || a.nameId - b.nameId
  ))

  const storageOffset = 6 + entries.length * 12
  const storage = Buffer.concat(entries.map((entry) => entry.data))
  const table = Buffer.alloc(storageOffset + storage.length)

  table.writeUInt16BE(0, 0) // format 0
  table.writeUInt16BE(entries.length, 2)
  table.writeUInt16BE(storageOffset, 4)

  let cursor = 0
  entries.forEach((entry, index) => {
    const at = 6 + index * 12
    table.writeUInt16BE(entry.platformId, at)
    table.writeUInt16BE(entry.encodingId, at + 2)
    table.writeUInt16BE(entry.languageId, at + 4)
    table.writeUInt16BE(entry.nameId, at + 6)
    table.writeUInt16BE(entry.data.length, at + 8)
    table.writeUInt16BE(cursor, at + 10)
    entry.data.copy(table, storageOffset + cursor)
    cursor += entry.data.length
  })

  return buildFont(buffer.readUInt32BE(0), { ...readTables(buffer, 0), name: table })
}
