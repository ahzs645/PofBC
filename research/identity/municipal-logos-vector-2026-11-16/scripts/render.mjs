// Render an SVG to PNG with resvg. usage: node render.mjs in.svg out.png [height]
import { readFileSync, writeFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(new URL('../../../../package.json', import.meta.url));
const { Resvg } = require('@resvg/resvg-js');
const [svg, out, h] = process.argv.slice(2);
writeFileSync(out, new Resvg(readFileSync(svg), { fitTo: { mode: 'height', value: Number(h || 300) } }).render().asPng());
