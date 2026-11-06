import { gunzipSync } from 'node:zlib'

// Compression levels, zlib versions and platform header bytes may differ.
// Accept only byte-identical decompressed content, including ordering/newlines.
export function gzipContentMatches (bytes, expected) {
  try { return gunzipSync(bytes).equals(Buffer.from(expected)) } catch { return false }
}
