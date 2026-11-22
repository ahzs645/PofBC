// usage: node render.cjs in.svg out.png [width] [bg]
const {Resvg}=require(require('path').resolve(__dirname, '../../../../node_modules/@resvg/resvg-js'));
const fs=require('fs');
const [,,i,o,w,bg]=process.argv;
const r=new Resvg(fs.readFileSync(i),{fitTo:{mode:'width',value:+(w||600)},background:bg||'rgba(0,0,0,0)'});
fs.writeFileSync(o,r.render().asPng());
