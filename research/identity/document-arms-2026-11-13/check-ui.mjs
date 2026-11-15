import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { mkdir, writeFile } from 'node:fs/promises';
import { pathToFileURL, fileURLToPath } from 'node:url';
// Optional test dependencies stay outside the application; see validation.md.
const project=fileURLToPath(new URL('../../../', import.meta.url)).replace(/\/$/, '');
const require=createRequire(`${project}/package.json`);
const testRequire=process.env.POFBC_TEST_DEPS ? createRequire(process.env.POFBC_TEST_DEPS) : require;
const {build}=testRequire('esbuild');
const {JSDOM}=testRequire('jsdom');
const React=require('react');
const {createRoot}=require('react-dom/client');
const {act}=React;
const out=`${project}/tmp/identity-review`;
await mkdir(out,{recursive:true});
await build({
 entryPoints:[`${project}/src/site/App.jsx`],outfile:`${out}/App.mjs`,bundle:true,platform:'node',format:'esm',packages:'external',jsx:'automatic',
 loader:{'.png':'dataurl','.jpg':'dataurl'},define:{'import.meta.env.BASE_URL':'"/PofBC/"'},logLevel:'error',
 plugins:[{name:'leave-unopened-views-deferred',setup(b){b.onResolve({filter:/^\.\.\/(gallery|government|internal|posters|signs|patches|plates|guides|stationery|salaries|health)\/.*View\.jsx$/},args=>({path:args.path,external:true}));}}]
});
const dom=new JSDOM('<!doctype html><html><head></head><body><div id="app"></div></body></html>',{url:'https://example.test/PofBC/',pretendToBeVisual:true});
const w=dom.window;
for(const key of ['window','document','navigator','location','history','localStorage','HTMLElement','SVGElement','Element','Event','MouseEvent','DOMParser']) Object.defineProperty(globalThis,key,{value:key==='window'?w:w[key],configurable:true,writable:true});
globalThis.IS_REACT_ACT_ENVIRONMENT=true;
globalThis.addEventListener=w.addEventListener.bind(w);globalThis.removeEventListener=w.removeEventListener.bind(w);globalThis.scrollTo=()=>{};
globalThis.matchMedia=()=>({matches:false,addEventListener(){},removeEventListener(){}});
w.HTMLCanvasElement.prototype.toDataURL=function(type){return `data:${type};base64,AA==`};
const blobs=new Map();let blobId=0;let saved;
URL.createObjectURL=(blob)=>{const url=`blob:identity-${++blobId}`;blobs.set(url,blob);return url;};
URL.revokeObjectURL=(url)=>blobs.delete(url);
document.addEventListener('click',event=>{const link=event.target.closest?.('a[download]');if(link){event.preventDefault();saved={name:link.download,blob:blobs.get(link.href)};}});
const {App}=await import(pathToFileURL(`${out}/App.mjs`));
const container=document.getElementById('app');let root=createRoot(container);
const click=async(label)=>{const button=[...document.querySelectorAll('button')].find(b=>b.textContent.trim()===label);assert.ok(button,`button ${label}`);await act(async()=>{button.click();await new Promise(resolve=>setTimeout(resolve,10));});};
const colourPanel=()=>[...document.querySelectorAll('section.panel')].find(el=>el.querySelector('h2')?.textContent==='Colour');
const colourField=(label)=>[...colourPanel().querySelectorAll('.field')].find(el=>el.querySelector('.field__label')?.textContent===label);
const swatch=async(label,name)=>{const button=colourField(label)?.querySelector(`button[aria-label="${name}"]`);assert.ok(button,`${label} ${name} swatch`);await act(async()=>button.click());};
const setLinked=async(linked)=>{const input=colourPanel().querySelector('input[type="checkbox"]');assert.ok(input,'colour link checkbox');if(input.checked!==linked)await act(async()=>input.click());};
const sourceRecord=()=>document.querySelector('.document-arms-source__record');
const sourceImage=()=>sourceRecord().querySelector('img');
const chooseReference=async(value)=>{const select=document.querySelector('.document-arms-source select');assert.ok([...select.options].some(option=>option.value===value),`reference option ${value}`);await act(async()=>{select.value=value;select.dispatchEvent(new Event('change',{bubbles:true}));});};
let checks=0;
const assertCase=(name,fn)=>{fn();checks++;console.log(`PASS ${name}`)};
await act(async()=>root.render(React.createElement(App)));
await click('Historic');
assertCase('historical option renders actual lazy preview and hides ministry inputs',()=>{assert.ok(document.querySelector('svg[data-identity="document-arms"]'));assert.equal([...document.querySelectorAll('h2')].some(e=>e.textContent==='Wording'),false);assert.match(document.body.textContent,/Reconstruction study/);});
for(const [label,layout,specimen] of [['Arms alone','emblem','mining-1954-title'],['Split serif','split-serif','supplied-split-serif'],['Government heading','government','oic-1121-heading'],['Crown grant heading','split-blackletter','oic-1121-grant']]){
 await click(label);
 assertCase(`actual React heading ${layout} selects its relevant source`,()=>{assert.equal(document.querySelector('svg[data-identity]').dataset.layout,layout);assert.equal(document.querySelectorAll('.document-arms-reference img').length,1);assert.equal(sourceRecord().dataset.specimen,specimen);assert.equal(document.querySelectorAll('svg[data-identity] text, svg[data-identity] image').length,0);});
}

// These are user journeys through the actual source viewer, not a separate evidence mock.
await click('Arms alone');
assertCase('arms-only controls omit absent lettering without hiding the source comparison',()=>{
 assert.ok(colourField('Arms'));
 assert.equal(colourField('Text'),undefined);
 assert.equal(colourPanel().querySelector('input[type="checkbox"]'),null);
 assert.match(sourceRecord().textContent,/Published 1954/);
 assert.equal(sourceRecord().querySelector('a:not([aria-label])').href,'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf#page=2');
});
const armsBeforeSourceChange=document.querySelector('svg[data-identity]').outerHTML;
await chooseReference('mining-1954-cover');
const coverDetail=sourceImage().src;
await click('Whole page');
assertCase('whole-page control shows the original page without altering the rendered study',()=>{
 assert.notEqual(sourceImage().src,coverDetail);
 assert.equal(sourceRecord().querySelector('figure').dataset.wholePage,'true');
 assert.match(sourceImage().alt,/Complete grey cover/);
 assert.equal(document.querySelector('svg[data-identity]').outerHTML,armsBeforeSourceChange);
 assert.equal(sourceRecord().querySelector('a:not([aria-label])').href,'https://cmscontent.nrs.gov.bc.ca/geoscience/publicationcatalogue/Miscellaneous/BCGS_MP-46.pdf#page=1');
});
await click('Detail');
assertCase('detail returns to the same source crop',()=>{
 assert.equal(sourceImage().src,coverDetail);
 assert.equal(sourceRecord().querySelector('figure').hasAttribute('data-whole-page'),false);
});
await click('Whole page');
await chooseReference('official-1906');
assertCase('low-resolution official illustration has its own status and no invented whole-page view',()=>{
 assert.equal(sourceRecord().dataset.specimen,'official-1906');
 assert.match(sourceRecord().textContent,/Official historical illustration/);
 assert.match(sourceRecord().textContent,/illustration date not established/);
 assert.match(sourceRecord().textContent,/200 × 186 pixels/);
 assert.equal(document.querySelector('[aria-label="Reference view"]'),null);
 assert.equal(document.querySelector('svg[data-identity]').outerHTML,armsBeforeSourceChange);
});
await click('Government heading');
assertCase('government heading opens the independently identified order and approval date',()=>{
 assert.equal(sourceRecord().dataset.specimen,'oic-1121-heading');
 assert.match(sourceRecord().textContent,/Approved 4 May 1978 · PDF page 1/);
 assert.equal(sourceRecord().querySelector('a:not([aria-label])').href,'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978#page=1');
});
await chooseReference('oic-832-heading');
assertCase('the second dated order stays separate from the supplied order',()=>{
 assert.match(sourceRecord().textContent,/Approved 6 April 1978/);
 assert.match(sourceRecord().textContent,/separate order/);
 assert.equal(sourceRecord().querySelector('a:not([aria-label])').href,'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/0832_1978#page=1');
});
await chooseReference('supplied-government');
assertCase('original supplied crop remains available with its matched source',()=>{
 assert.match(sourceRecord().textContent,/Supplied crop · original identified/);
 assert.equal(document.querySelector('[aria-label="Reference view"]'),null);
 assert.match(sourceRecord().querySelector('a:not([aria-label])').href,/1121_1978#page=1$/);
});
await click('Crown grant heading');
assertCase('Crown-grant source identifies page four without misdating the map or grant',()=>{
 assert.equal(sourceRecord().dataset.specimen,'oic-1121-grant');
 assert.match(sourceRecord().textContent,/Attached to the order approved 4 May 1978 · PDF page 4/);
 assert.match(sourceRecord().textContent,/Crown Grant No\. 8498/);
 assert.match(sourceRecord().textContent,/map sheet’s creation date and the grant’s issue date are not established/);
 assert.equal(sourceRecord().querySelector('a:not([aria-label])').href,'https://www.bclaws.gov.bc.ca/civix/document/id/oic/arc_oic/1121_1978#page=4');
});

// Reproduce the two palette bugs through visible controls, including a return from another era.
await setLinked(false);
await swatch('Mark','black');
await swatch('Text','red');
const historicRed=document.querySelector('svg[data-identity] [data-part="heading"]').getAttribute('fill');
await click('Arms');
await setLinked(false);
await setLinked(true);
await click('Historic');
assertCase('relinking another identity preserves Historic independent lettering and link choice',()=>{
 assert.equal(colourPanel().querySelector('input[type="checkbox"]').checked,false);
 assert.equal(document.querySelector('svg[data-identity] [data-part="heading"]').getAttribute('fill'),historicRed);
 assert.equal(document.querySelector('svg[data-identity] [data-part="arms"]').getAttribute('fill'),'#000000');
});
await swatch('Text','white');
await swatch('Background','Transparent');
await click('Arms alone');
assertCase('black arms ignore hidden white lettering when choosing the automatic preview surface',()=>{
 assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'light');
 assert.equal(document.querySelector('svg[data-identity] [data-part="heading"]'),null);
 assert.equal(colourField('Text'),undefined);
 assert.equal(colourPanel().querySelector('input[type="checkbox"]'),null);
 assert.match(colourPanel().querySelector('.contrast-list').textContent,/On white21:1/);
});
await click('Crown grant heading');
assertCase('returning to a heading restores its saved independent white lettering',()=>{
 assert.equal(document.querySelector('svg[data-identity] [data-part="heading"]').getAttribute('fill'),'#ffffff');
 assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'dark');
 assert.equal(colourPanel().querySelector('input[type="checkbox"]').checked,false);
});
await setLinked(true);
const colorPanel=[...document.querySelectorAll('section.panel')].find(el=>el.querySelector('h2')?.textContent==='Colour');
await act(async()=>colorPanel.querySelector('button[aria-label="Transparent"]').click());
await act(async()=>colorPanel.querySelectorAll('button[aria-label="white"]')[0].click());
assertCase('white transparent preview chooses dark auto backdrop and exports no background',()=>{assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'dark');assert.equal(document.querySelector('svg[data-identity] [data-part="arms"]').getAttribute('fill'),'#ffffff');assert.equal(document.querySelector('svg[data-identity] [data-part="background"]'),null);});
await click('Light');
assertCase('manual backdrop changes only the viewing surface',()=>{assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'light');assert.equal(document.querySelector('svg[data-identity] [data-part="background"]'),null);});
await click('Auto');
await click('Crest');
assert.equal(document.querySelector('svg[data-identity="document-arms"]'),null);
await click('Historic');
assertCase('returning from another identity retains the historic palette and layout',()=>{assert.equal(document.querySelector('svg[data-identity]').dataset.layout,'split-blackletter');assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'dark');});
await click('Download SVG');
assert.ok(saved?.blob);
const exported=await saved.blob.text();
assertCase('actual download action creates outlined SVG with study filename and metadata',()=>{assert.equal(saved.name,'bc-historic-arms-split-blackletter-study.svg');assert.match(exported,/data-layout="split-blackletter"/);assert.match(exported,/not a verified historical or official drawing/);assert.doesNotMatch(exported,/<image\b|<text\b|@font-face/);assert.match(exported,/fill="#ffffff"/);});
await click('Copy link');
const shareUrl=document.querySelector('[aria-label="Shareable link"]').value;
assert.ok(new URL(shareUrl).searchParams.get('s'));
await act(async()=>root.unmount());
history.replaceState(null,'',shareUrl);
root=createRoot(container);
await act(async()=>{root.render(React.createElement(App));await new Promise(resolve=>setTimeout(resolve,30));});
assertCase('actual component reload restores compressed layout, linked colours and transparency',()=>{assert.equal(document.querySelector('svg[data-identity]').dataset.layout,'split-blackletter');assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'dark');assert.equal(JSON.parse(document.getElementById('configuration').value).linkColors,true);});
await click('Government heading');
await click('Copy readable link');
const readable=document.querySelector('[aria-label="Shareable link"]').value;
assertCase('readable copy after compressed reload removes stale token',()=>{const url=new URL(readable);assert.equal(url.searchParams.has('s'),false);assert.equal(JSON.parse(url.searchParams.get('c')).documentLayout,'government');});
assertCase('related 1919 and manuals links preserve specific records',()=>{const links=[...document.querySelectorAll('.document-arms-panel a')].map(a=>a.getAttribute('href'));assert.ok(links.includes('?view=plates&plate=1919-cardboard'));assert.ok(links.includes('?view=guides'));});
await writeFile(`${out}/dom.html`,document.documentElement.outerHTML);
await act(async()=>root.unmount());
dom.window.close();
console.log(`${checks} actual React/JSDOM interaction checks passed. Browser layout and raster/PDF codecs are not exercised.`);
