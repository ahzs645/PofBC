const {Resvg}=require('/home/user/PofBC/node_modules/@resvg/resvg-js');
const fs=require('fs');
const [,,inp,out,w,bg]=process.argv;
const r=new Resvg(fs.readFileSync(inp),{fitTo:{mode:'width',value:+(w||600)},background:bg||'white'});
fs.writeFileSync(out,r.render().asPng());
