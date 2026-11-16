// usage: node render.js in.svg out.png [width] [bg]
const {Resvg}=require('/home/user/PofBC/node_modules/@resvg/resvg-js');
const fs=require('fs');
const [,,i,o,w,bg]=process.argv;
const r=new Resvg(fs.readFileSync(i),{fitTo:{mode:'width',value:+(w||800)},background:bg||'white'});
fs.writeFileSync(o,r.render().asPng());
