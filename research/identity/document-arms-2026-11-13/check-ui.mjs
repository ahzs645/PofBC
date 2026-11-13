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
 loader:{'.png':'dataurl'},define:{'import.meta.env.BASE_URL':'"/PofBC/"'},logLevel:'error',
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
let checks=0;
const assertCase=(name,fn)=>{fn();checks++;console.log(`PASS ${name}`)};
await act(async()=>root.render(React.createElement(App)));
await click('Historic arms');
assertCase('historical option renders actual lazy preview and hides ministry inputs',()=>{assert.ok(document.querySelector('svg[data-identity="document-arms"]'));assert.equal([...document.querySelectorAll('h2')].some(e=>e.textContent==='Wording'),false);assert.match(document.body.textContent,/Reconstruction study/);});
for(const [label,layout] of [['Arms alone','emblem'],['Split serif','split-serif'],['Government heading','government'],['Crown grant heading','split-blackletter']]){
 await click(label);
 assertCase(`actual React heading ${layout}`,()=>{assert.equal(document.querySelector('svg[data-identity]').dataset.layout,layout);assert.equal(document.querySelectorAll('.document-arms-reference img').length,layout==='emblem'?0:1);assert.equal(document.querySelectorAll('svg[data-identity] text, svg[data-identity] image').length,0);});
}
const colorPanel=[...document.querySelectorAll('section.panel')].find(el=>el.querySelector('h2')?.textContent==='Colour');
await act(async()=>colorPanel.querySelector('button[aria-label="Transparent"]').click());
await act(async()=>colorPanel.querySelectorAll('button[aria-label="white"]')[0].click());
assertCase('white transparent preview chooses dark auto backdrop and exports no background',()=>{assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'dark');assert.equal(document.querySelector('svg[data-identity] [data-part="arms"]').getAttribute('fill'),'#ffffff');assert.equal(document.querySelector('svg[data-identity] [data-part="background"]'),null);});
await click('Light');
assertCase('manual backdrop changes only the viewing surface',()=>{assert.equal(document.querySelector('.stage__frame').dataset.backdrop,'light');assert.equal(document.querySelector('svg[data-identity] [data-part="background"]'),null);});
await click('Auto');
await click('Crest');
assert.equal(document.querySelector('svg[data-identity="document-arms"]'),null);
await click('Historic arms');
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
