#!/usr/bin/env node
/**
 * Rebuild the documentary source contact sheet from the held PNG crops.
 * Run from any directory: node path/to/build-evidence-review.mjs
 * Images are embedded byte-for-byte, shown whole with contain scaling, and are
 * never traced, recoloured or redrawn. Labels use the project's pinned Noto Sans
 * font outlines so both SVG and PNG render without system-font dependencies.
 */
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { createRequire } from 'node:module';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { openSync } from 'fontkit';
import { Resvg } from '@resvg/resvg-js';

const require = createRequire(import.meta.url);
const dir = dirname(fileURLToPath(import.meta.url));
const width = 1400;
const height = 1100;
const colours = {
  paper: '#F5F4EF', card: '#FFFEFC', navy: '#162A49', ink: '#30383E',
  muted: '#526273', line: '#D5DAD9', accent: '#A5743B',
};
const fontFiles = {
  regular: require.resolve('@fontsource/noto-sans/files/noto-sans-latin-400-normal.woff'),
  bold: require.resolve('@fontsource/noto-sans/files/noto-sans-latin-700-normal.woff'),
};
const fonts = Object.fromEntries(Object.entries(fontFiles).map(([key, path]) => [key, openSync(path)]));
const esc = (value) => String(value).replace(/[&<>"']/g, (c) => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&apos;',
}[c]));
const sha256 = (bytes) => createHash('sha256').update(bytes).digest('hex');
const parts = [];
function label(text, x, baseline, size, options = {}) {
  const font = fonts[options.bold ? 'bold' : 'regular'];
  const run = font.layout(text);
  if (run.glyphs.some((glyph) => glyph.id === 0)) throw new Error(`Missing label glyph: ${text}`);
  const scale = size / font.unitsPerEm;
  const advance = run.positions.reduce((sum, p) => sum + p.xAdvance, 0) * scale;
  if (options.maxWidth && advance > options.maxWidth) {
    throw new Error(`Label exceeds available width: ${text} (${advance} > ${options.maxWidth})`);
  }
  let penX = 0;
  let penY = 0;
  const paths = run.glyphs.map((glyph, i) => {
    const position = run.positions[i];
    const glyphX = penX + position.xOffset;
    const glyphY = penY + position.yOffset;
    if (![glyphX, glyphY, position.xAdvance, position.yAdvance].every(Number.isFinite)) {
      throw new Error(`Invalid glyph position: ${text}`);
    }
    // Read raw outlines without transforming fontkit's cached glyph paths. All
    // placement stays in SVG transforms, so reuse of a letter cannot alter it.
    const path = glyph.path.toSVG();
    if (/NaN|Infinity/.test(path)) throw new Error(`Invalid raw glyph outline: ${text}`);
    penX += position.xAdvance;
    penY += position.yAdvance;
    return `<path transform="translate(${glyphX} ${glyphY})" d="${path}"/>`;
  }).join('');
  parts.push(`<g aria-label="${esc(text)}"><title>${esc(text)}</title><g fill="${options.fill ?? colours.ink}" transform="translate(${x} ${baseline}) scale(${scale} ${-scale})">${paths}</g></g>`);
}

const cards = [
  {
    number: '01', title: 'Government caption',
    subtitle: 'OIC 1121/1978 · approved 4 May 1978 · PDF page 1',
    caption: 'Exact match to the supplied order heading.',
    file: 'oic-1121-heading-detail.png',
    source: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978',
    page: 1,
  },
  {
    number: '02', title: 'Blackletter map heading',
    subtitle: 'OIC 1121/1978 · map attachment · PDF page 4',
    caption: 'Same order file; map creation date unknown.',
    file: 'oic-1121-grant-detail.png',
    source: 'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978',
    page: 4,
  },
  {
    number: '03', title: '1954 cover engraving',
    subtitle: 'Mining in British Columbia · PDF page 1',
    caption: '1954 imprint: Don McDiarmid, Queen’s Printer.',
    file: 'mining-1954-cover-detail.png',
    source: 'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf',
    page: 1,
  },
  {
    number: '04', title: '1954 title-page engraving',
    subtitle: 'Same publication · PDF page 2',
    caption: 'Different drawing within the same dated publication.',
    file: 'mining-1954-title-detail.png',
    source: 'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf',
    page: 2,
  },
];

parts.push(`<rect width="${width}" height="${height}" fill="${colours.paper}"/>`);
parts.push(`<rect x="64" y="38" width="38" height="4" fill="${colours.accent}"/>`);
label('PofBC / HISTORICAL DOCUMENT ARMS', 116, 44, 13, { bold: true, fill: colours.muted, maxWidth: 1000 });
label('Historic arms: the source evidence', 64, 99, 38, { bold: true, fill: colours.navy, maxWidth: 1272 });
label('Source excerpts matched to the supplied references, with two additional period specimens.', 64, 135, 18, { fill: colours.muted, maxWidth: 1272 });

const provenance = [];
cards.forEach((card, i) => {
  const x = 64 + (i % 2) * 650;
  const y = 176 + Math.floor(i / 2) * 388;
  const imageBytes = readFileSync(join(dir, 'reference', card.file));
  if (imageBytes.subarray(0, 8).toString('hex') !== '89504e470d0a1a0a') {
    throw new Error(`Expected original PNG source: ${card.file}`);
  }
  const sourceWidth = imageBytes.readUInt32BE(16);
  const sourceHeight = imageBytes.readUInt32BE(20);
  provenance.push({ source: card.source, pdfPage: card.page, file: `reference/${card.file}`, sourceWidth, sourceHeight, sha256: sha256(imageBytes) });
  parts.push(`<g><title>${esc(`${card.title} — ${card.subtitle}`)}</title>`);
  parts.push(`<rect x="${x}" y="${y}" width="622" height="360" rx="12" fill="${colours.card}" stroke="${colours.line}"/>`);
  label(card.number, x + 24, y + 37, 13, { bold: true, fill: colours.accent, maxWidth: 40 });
  label(card.title, x + 64, y + 39, 22, { bold: true, fill: colours.navy, maxWidth: 534 });
  label(card.subtitle, x + 24, y + 70, 15, { fill: colours.muted, maxWidth: 574 });
  parts.push(`<rect x="${x + 24}" y="${y + 91}" width="574" height="228" rx="3" fill="#FFFFFF" stroke="#E9EAE5"/>`);
  parts.push(`<image x="${x + 25}" y="${y + 92}" width="572" height="226" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,${imageBytes.toString('base64')}"><title>${esc(`Unaltered held source crop: ${card.file}; ${sourceWidth} × ${sourceHeight} pixels`)}</title></image>`);
  label(card.caption, x + 24, y + 342, 14, { fill: colours.muted, maxWidth: 574 });
  parts.push('</g>');
});

parts.push(`<path d="M64 955H1336" stroke="${colours.line}"/>`);
label('How to read this sheet', 64, 989, 17, { bold: true, fill: colours.navy, maxWidth: 1272 });
label('These are document scans, not the exported vector study. Map creation date remains unknown.', 64, 1019, 16, { maxWidth: 1272 });
label('Different drawings are documented; no prescribed historical master or typeface has been established.', 64, 1046, 16, { maxWidth: 1272 });
label('Reviewed 14 November 2026 · Original crop bytes embedded · Full excerpts shown without further cropping', 64, 1081, 12, { fill: colours.muted, maxWidth: 1272 });

const metadata = {
  reviewed: '2026-11-14',
  purpose: 'Documentary comparison; original source crops only; no reconstruction or tracing.',
  sources: provenance,
  fonts: Object.fromEntries(Object.entries(fontFiles).map(([key, path]) => [key, { package: '@fontsource/noto-sans', weight: key === 'bold' ? 700 : 400, sha256: sha256(readFileSync(path)) }])),
};
const svg = `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" role="img" aria-labelledby="title desc">\n<title id="title">Historic arms: the source evidence</title>\n<desc id="desc">Four unaltered document excerpts: OIC 1121/1978 page 1 government caption, page 4 blackletter map heading, and two different arms drawings from the cover and title page of a 1954 provincial mining pamphlet. These are scans, not the exported vector study. The map creation date, historical master and exact typefaces remain unknown.</desc>\n<metadata>${esc(JSON.stringify(metadata, null, 2))}</metadata>\n${parts.join('\n')}\n</svg>\n`;
const svgPath = join(dir, 'source-evidence-review.svg');
const pngPath = join(dir, 'source-evidence-review.png');
writeFileSync(svgPath, svg);
const png = new Resvg(svg, { font: { loadSystemFonts: false }, fitTo: { mode: 'original' } }).render().asPng();
writeFileSync(pngPath, png);
console.log(`Wrote ${svgPath}\nWrote ${pngPath}\n${width} × ${height}; ${provenance.length} original source crops; all label widths checked.`);
