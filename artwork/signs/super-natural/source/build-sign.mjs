import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { FLAG } from '../../../../src/assets/flagMark.js';
import { GLYPHS, KERNING } from '../../../../src/hydro/serif.js';
import { setRun, runMarkup } from '../../../../src/hydro/hydroType.js';

const root=path.dirname(fileURLToPath(import.meta.url));
const design=JSON.parse(fs.readFileSync(path.join(root,'design.json'),'utf8'));
const out=path.join(root,'output');
fs.mkdirSync(out,{recursive:true});
fs.mkdirSync(path.join(out,'components'),{recursive:true});
const {canvas:c,flag:f,palette:p}=design;
const n=v=>Number(v.toFixed(5));
const xml=s=>s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/"/g,'&quot;');
const flagShapes=FLAG.shapes.map((shape,i)=>`<path id="flag-shape-${i+1}" d="${shape.d}" fill="${shape.fill}"/>`).join('\n');
const flag=`<g id="existing-spirit-of-bc-flag" inkscape:label="Existing PofBC flag — 12 original paths" transform="translate(${f.x} ${f.y}) scale(${f.scale})" data-source="src/assets/flagMark.js" data-geometry="unchanged">${flagShapes}</g>`;

// These straight bands terminate on the EXISTING shapes' left-edge vertices.
// A 4-source-unit overlap prevents antialias seams without changing source paths.
const L=(design.stripeLeft-f.x)/f.scale;
const stripeDefs=[
 {id:'red-band',fill:p.red,d:`M${L} 367.34H49.14L42.71 420.3L35.71 466.34H${L}Z`},
 {id:'upper-navy-band',fill:p.navy,d:`M${L} 488.37H33.23L19.14 596.34H${L}Z`},
 {id:'lower-navy-band',fill:p.navy,d:`M${L} 613.68H16.86L4.03 721.59H${L}Z`}
];
const stripes=`<g id="geometric-stripe-extensions" inkscape:label="Three geometric stripe extensions" transform="translate(${f.x} ${f.y}) scale(${f.scale})">${stripeDefs.map(a=>`<path id="${a.id}" fill="${a.fill}" d="${a.d}"/>`).join('\n')}</g>`;
const header=`<g id="flag-and-stripe-header" inkscape:groupmode="layer" inkscape:label="Flag and three stripes">${stripes}\n${flag}</g>`;

// Backing contour derives from the source flag's upper silhouette, with a modest
// white allowance. It is an interpreted panel edge, not a traced photograph edge.
const cap=`<path id="white-flag-backing" transform="translate(${f.x} ${f.y}) scale(${f.scale})" d="M48 395L66 132L146 81C219 48 315 10 365 36C394 51 386 88 380 114C376 129 374 139 383 140C398 141 425 110 452 105L479 87C504 68 548 41 595 16L612 14C649 -3 687 -17 707 10C721 28 704 69 705 83C718 80 764 59 804 38L817 45L861 20L951 -1L924 242L902 430L60 745Z" fill="${p.paper}"/>`;
const panel=`<g id="panel" inkscape:groupmode="layer" inkscape:label="White sign panel and flag backing">${cap}<rect id="rectangular-sign-face" x="0" y="${c.panelTop}" width="${c.width}" height="${c.height-c.panelTop}" fill="${p.paper}"/></g>`;
const runCharacters=text=>Array.from(text);
const rows=[];
const rowMetrics=[];
for(const row of design.rows){
  const measured=setRun(row.text,{x:0,y:0,size:1000});
  const sx=row.width/(measured.box.right-measured.box.x);
  const dsFor=ch=>ch===',' ? design.lettering.commaDescenderScale : (row.descenderScale??design.lettering.descenderScale);
  const descent=Math.max(...runCharacters(row.text).map(ch=>{const b=GLYPHS[ch]?.box?.[3]??0;return b>100?b*dsFor(ch):b;}));
  const sy=row.height/(descent-measured.box.y);
  const run=setRun(row.text,{x:row.x-measured.box.x*sx,y:row.y-measured.box.y*sy,size:1000,sx,sy,id:row.id});
  const letters=run.chars.map((ch,i)=>{
    const glyph=GLYPHS[ch];
    if(!glyph?.d)return '';
    const shape=`<path d="${glyph.d}"/>`;
    const body=glyph.box[3]>100 ? `<g clip-path="url(#above-baseline)">${shape}</g><g transform="scale(1 ${dsFor(ch)})" clip-path="url(#below-baseline)">${shape}</g>` : shape;
    return `<g data-letter="${xml(ch)}" data-glyph-index="${i}" transform="translate(${n(run.positions[i])} 0)">${body}</g>`;
  }).join('\n');
  const markup=`<g id="${row.id}" data-text="${xml(row.text)}" transform="matrix(${n(sx)} 0 0 ${n(sy)} ${n(run.x)} ${n(run.y)})" fill="${p.navy}" stroke="${p.navy}" stroke-width="${design.lettering.opticalStroke}" stroke-linejoin="round" paint-order="stroke fill">${letters}</g>`;
  run.box.bottom=row.y+row.height;
  rows.push(markup);
  rowMetrics.push({id:row.id,text:row.text,sx,sy,horizontalCondensation:sx/sy,baseline:run.y,box:run.box,glyphs:run.chars.filter(a=>GLYPHS[a]?.d).length});
}
const wording=`<g id="three-line-lettering" inkscape:groupmode="layer" inkscape:label="Existing Termes outlines — three fitted lines" data-source="src/hydro/serif.js" data-typeface-status="reconstruction substitute, original unidentified; reversible optical weight and descender adjustment">${rows.join('\n')}</g>`;
const desc='Reconstructed from reusable PofBC elements: twelve unaltered Spirit of BC flag paths, committed TeX Gyre Termes Regular glyph outlines with reversible weight and descender adjustments, three new geometric stripe extensions and a white panel. Layout estimated from Bennett-06(1).jpg. The original sign font and paint specification are unverified. No photographic tracing, raster image or font dependency in the master.';
function svg(body,title=design.title,viewBox=`0 0 ${c.width} ${c.height}`){const [vx,vy,vw,vh]=viewBox.split(/\s+/).map(Number);return `<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape" width="${vw}" height="${vh}" viewBox="${viewBox}" role="img" aria-labelledby="title desc">\n<title id="title">${xml(title)}</title>\n<desc id="desc">${xml(desc)}</desc>\n<metadata>${xml(JSON.stringify({sourceCommit:design.sourceCommit,sourceRepo:'https://github.com/ahzs645/PofBC',method:'component assembly; no tracing',paletteStatus:'existing supplied-artwork palette; not sign-specific verification',font:'Existing TeX Gyre Termes Regular outlined glyphs',design}))}</metadata>\n<defs><clipPath id="above-baseline"><rect x="-1000" y="-2000" width="20000" height="2000"/></clipPath><clipPath id="below-baseline"><rect x="-1000" y="0" width="20000" height="2000"/></clipPath></defs>\n${body}\n</svg>\n`;}
fs.writeFileSync(path.join(out,'BC_Super_Natural_Welcome_Sign.svg'),svg(panel+'\n'+header+'\n'+wording));
fs.writeFileSync(path.join(out,'BC_Super_Natural_Artwork_Only.svg'),svg(header+'\n'+wording,design.title+' — artwork only, transparent'));
fs.writeFileSync(path.join(out,'components','Flag_and_Stripes.svg'),svg(header,'Existing BC flag with geometric stripe extensions',`0 0 ${c.width} 400`));
fs.writeFileSync(path.join(out,'components','Lettering.svg'),svg(wording,'Existing Termes lettering for the welcome sign'));
fs.writeFileSync(path.join(out,'components','Panel_Silhouette.svg'),svg(panel,'Interpreted sign panel silhouette'));
fs.writeFileSync(path.join(out,'construction.json'),JSON.stringify({design,rowMetrics,counts:{sourceFlagPaths:FLAG.shapes.length,stripePaths:stripeDefs.length,letterPaths:rowMetrics.reduce((a,b)=>a+b.glyphs,0)}},null,2)+'\n');
console.log(JSON.stringify({output:out,rowMetrics},null,2));
