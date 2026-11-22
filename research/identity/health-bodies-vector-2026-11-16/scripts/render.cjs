// node render.cjs in.svg out.png width [background]
const fs = require('fs');
const { Resvg } = require(process.env.RESVG || '/home/user/PofBC/node_modules/@resvg/resvg-js');
const [, , inp, out, w, bg] = process.argv;
const r = new Resvg(fs.readFileSync(inp), { fitTo: { mode: 'width', value: +w }, background: bg || 'rgba(0,0,0,0)' });
fs.writeFileSync(out, r.render().asPng());
