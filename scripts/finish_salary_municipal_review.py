#!/usr/bin/env python3
"""Create bounded actual-PDF review packets from immutable raw-reader staging."""
import gzip,hashlib,json,math
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parents[1];AREA=ROOT/"research/salaries/queue-completion-2026-11-01/municipal";CACHE=Path("/tmp/queue-completion-municipal")
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run():
 draft=AREA/"reader-draft-v2.json.gzip";sections=json.loads(gzip.decompress(draft.read_bytes()))["sections"];out=CACHE/"review";out.mkdir(exist_ok=True);packets=[]
 for si,section in enumerate(sections):
  cfg=section["layout"]
  if cfg["sourceKey"]=="creston-2024":continue
  assert section["equalRowCounts"]
  image=Image.open(CACHE/"images"/f'{cfg["sourceKey"]}-p{cfg["physicalPage"]:02d}.png').convert("RGB")
  edata=json.loads(gzip.decompress((ROOT/section["evidenceFile"]).read_bytes()));assert sha(CACHE/"images"/f'{cfg["sourceKey"]}-p{cfg["physicalPage"]:02d}.png')==edata["render"]["imageSha256"]
  left=math.floor(cfg["name"][0]-15);right=math.ceil(max(cfg[f][1] for f in ("name","position","remuneration","expenses","total") if f in cfg)+15)
  rows=section["tesseractRows"]
  for start in range(0,len(rows),18):
   group=rows[start:start+18];pieces=[];record=[]
   for j,row in enumerate(group,start=start):
    y=row["anchorY"];lower=max(cfg["top"],row["rowBand"][0],y-50);upper=min(cfg["bottom"],row["rowBand"][1],y+50)
    box=[left,math.floor(lower),right,math.ceil(upper)];crop=image.crop(box);pieces.append((j+1,crop))
    record.append({"sectionRow":j+1,"sourceCropBox300Dpi":box,"tesseract":{k:v["raw"] for k,v in row["fields"].items()},"paddle":{k:v["raw"] for k,v in section["paddleRows"][j]["fields"].items()},"tesseractParsedMoney":{k:v for k,v in ((field,row["fields"][field].get("value")) for field in ("remuneration","expenses","total") if field in row["fields"])},"fieldDisagreements":[d for d in section["disagreements"] if d["row"]==j+1]})
   height=sum(im.height+24 for _,im in pieces);sheet=Image.new("RGB",(right-left,height),"white");draw=ImageDraw.Draw(sheet);top=0
   for rowNumber,im in pieces:
    draw.text((2,top+2),f'ACTUAL PDF300dpi | section{si} {cfg["sourceKey"]} p{cfg["physicalPage"]} {cfg["scope"]} row{rowNumber}',fill="black");sheet.paste(im,(0,top+24));top+=24+im.height
   stem=f's{si:02d}-{cfg["sourceKey"]}-p{cfg["physicalPage"]:02d}-r{start+1:02d}-{start+len(group):02d}';path=out/(stem+".png");sheet.save(path)
   packet={"packetId":stem,"sectionIndex":si,"sourceKey":cfg["sourceKey"],"physicalPage":cfg["physicalPage"],"scope":cfg["scope"],"sourceSha256":edata["sourceSha256"],"originalPageImageSha256":edata["render"]["imageSha256"],"imagePath":str(path),"imageSha256":sha(path),"rows":record};(out/(stem+".json")).write_text(json.dumps(packet,indent=2)+"\n");packets.append({k:packet[k] for k in ("packetId","sectionIndex","sourceKey","physicalPage","scope","imagePath","imageSha256")})
 manifest={"date":"2026-11-01","immutableReaderDraftSha256":sha(draft),"reviewTargetRows":sum(len(s["tesseractRows"]) for s in sections if s["layout"]["sourceKey"]!="creston-2024"),"packets":packets,"note":"Author checks every original name/title/amount, not just machine disagreements. Crops from actual PDF-painted source, no embedded tile stitching. Complete original page context remains available in /tmp, and both raw-engine streams remain separate."};(AREA/"manual-review-packets.json").write_text(json.dumps(manifest,indent=2)+"\n");print(json.dumps({"packets":len(packets),"rows":manifest["reviewTargetRows"],"manifest":str(AREA/"manual-review-packets.json")}))
if __name__=="__main__":run()

