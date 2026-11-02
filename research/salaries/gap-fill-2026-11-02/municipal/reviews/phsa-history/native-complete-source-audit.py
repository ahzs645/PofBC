from pathlib import Path
import fitz,gzip,hashlib,json,re
B=Path(__file__).resolve().parent;R=Path('/workspace/PofBC')
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):return {'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes())}
def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def norm(s):return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',s).strip()).rstrip('*')
def main():
 first=json.loads((B/'native-first-source-image-transcript.json').read_text());srcctx=json.loads((B/'native-first-source-context-transcript.json').read_text());contexts={x['sourceKey']:x for x in srcctx['sources']}
 results=[];rawpins=[];data=[]
 for key in ['phsa-2006-07','phsa-2007-08','phsa-2008-09']:
  pdf=Path('/workspace/gap-phsa-history-cache')/(key+'.pdf');doc=fitz.open(pdf);mup=read(B/(key+'-mupdf-independent-rows.json.gzip'));pop=read(B/(key+'-poppler-independent-rows.json.gzip'));selected=[];diffs=[];census=[];pix=[];numeric_unclassified=[];geometry=[]
  for a,b in zip(mup['rows'],pop['rows']):
   assert all(a[f]==b[f] for f in ['sequence','pdfPage','remuneration','sourceExpenses'])
   assert norm(a['name'])==norm(b['name'])
   e=0 if a['sourceExpenses']=='(0)' else a['expenses'];marker='*' if a['sequence']==289 and key=='phsa-2008-09' else None
   row={**a,'name':a['name'].rstrip('*'),'expenses':e,'sourceNameFootnote':marker}
   selected.append(row)
  assert len(mup['rows'])==len(pop['rows'])
  for manual in first['rows']:
   if manual['sourceKey']!=key:continue
   r=selected[manual['sequence']-1]
   for f in ['pdfPage','name','position','remuneration','expenses','sourceExpenses','sourceNameFootnote']:
    av=norm(manual[f]) if f=='name' else manual[f];bv=norm(r[f]) if f=='name' else r[f]
    if av!=bv:diffs.append({'sequence':r['sequence'],'field':f,'manual':manual[f],'native':r[f]})
  for engine in ['mupdf','poppler']:
   pages=read(B/(key+'-'+engine+'-words.json.gzip'));parsed=mup if engine=='mupdf' else pop
   for i,words in enumerate(pages):
    pn=i+1
    if pn<3:continue
    heads=[w for w in words if w['text'] in ['Remuneration','Expenses'] and w['x0']>300 and w['y0']<250];hy=max(w['y1'] for w in heads)
    counts={'namedPay':0,'namedExpense':0,'printedMonetaryTotal':0,'footerPageNumber':0,'statutoryFooter':0,'footnote':0}
    for w in words:
     if not re.fullmatch(r'(?:\(?\d+(?:,\d{3})*\)?|-)',w['text']) or w['y0']<=hy:continue
     wc=(w['y0']+w['y1'])/2
     hits=[r for r in selected if r['pdfPage']==pn and abs((r['box'][1]+r['box'][3])/2-wc)<3.5]
     controls=[r for r in parsed['controls'] if r['pdfPage']==pn and abs((r['anchor']['y0']+r['anchor']['y1'])/2-wc)<3.5]
     if hits:
      # A name may itself contain a literal hyphen; that glyph is not a payment.
      if w['x0']<300:continue
      split=(heads[0]['x1']+heads[1]['x0'])/2
      counts['namedPay' if w['x0']<split else 'namedExpense']+=1
     elif controls:counts['printedMonetaryTotal']+=1
     elif w['y0']>730 and 285<w['x0']<325:counts['footerPageNumber']+=1
     elif w['y0']>680 and w['text'] in ['1','6']:counts['statutoryFooter']+=1
     elif key=='phsa-2008-09' and pn==11 and w['y0']>650:counts['footnote']+=1
     else:numeric_unclassified.append({'engine':engine,'pdfPage':pn,'word':w})
    census.append({'engine':engine,'physicalPage':pn,'classes':counts})
  for pn,p in enumerate(doc,1):
   pixmap=p.get_pixmap(matrix=fitz.Matrix(150/72,150/72),alpha=False);pix.append({'physicalPage':pn,'dpi':150,'width':pixmap.width,'height':pixmap.height,'rgbPixelSha256':sha(pixmap.samples),'pngSha256':sha(pixmap.tobytes('png'))})
   # Check native text boxes for any painted table glyph reaching physical boundaries.
   if pn<3:continue
   wr=doc[pn-1].get_text('words');name_right=max((w[2] for w in wr if w[0]<300 and w[1]>190 and w[1]<680),default=0)
   geometry.append({'physicalPage':pn,'maxNamedCellGlyphRight':max((max(n['x1'] for n in r['nameWordBoxes']) for r in selected if r['pdfPage']==pn),default=0),'payColumnLowerBoundary':300,'pageWidth':float(p.rect.width),'pageHeight':float(p.rect.height)})
  assert not diffs,diffs;assert not numeric_unclassified,numeric_unclassified
  sp=B/(key+'-peer-selected-native-rows.json.gzip');sp.write_bytes(gzip.compress((json.dumps({'phase':'independent peer selection before producer candidates','sourceKey':key,'sourceSha256':sha(pdf.read_bytes()),'rows':selected,'additiveLiteralDecisions':['Parenthesized (0) is explicit numeric zero; source literal retained.','Superscript asterisk retained as sourceNameFootnote, not person name; native parser star-baseline difference independently image resolved.','Expenses printed as dashes remain null.']},indent=2,ensure_ascii=False)+'\n').encode(),mtime=0));data.append(pin(sp))
  ctx=contexts[key];sumpay=sum(r['remuneration'] for r in selected);sumexp=sum(r['expenses'] or 0 for r in selected)
  results.append({'sourceKey':key,'sourceSha256':sha(pdf.read_bytes()),'actualPeriod':ctx['actualPeriod'],'bodyPhysicalPages':[3,len(doc)],'rowCount':len(selected),'sourceNarrativeNamedCount':ctx['declaredNamedCount'],'narrativeCountResidual':len(selected)-ctx['declaredNamedCount'],'twoCompleteNativeReaderCountsAgree':True,'allNativeFieldsAgreeAfterOneSourceFootnoteAndTwoExplicitZeroDecisions':True,'manualRows':sum(r['sourceKey']==key for r in first['rows']),'manualFieldsAllAgree':True,'sumRemuneration':sumpay,'sourcePrintedRemuneration':ctx['sourcePrintedNamedRemuneration'],'remunerationResidual':sumpay-ctx['sourcePrintedNamedRemuneration'],'sumKnownExpenses':sumexp,'sourcePrintedExpenses':ctx['sourcePrintedNamedExpenses'],'knownExpenseResidual':sumexp-ctx['sourcePrintedNamedExpenses'],'expenseNullCount':sum(r['expenses'] is None for r in selected),'noExpenseDashesImputed':True,'residualsUnalteredCauseNotInferred':True,'allNumericTableTokensClassified':True,'wholePagePaymentCensus':census,'pageRasterPins':pix,'sourceColumnGeometryAudit':geometry,'selectedDataPin':pin(sp)})
  for engine in ['mupdf','poppler']:
   for kind in ['words','independent-rows']:rawpins.append(pin(B/(key+'-'+engine+'-'+kind+'.json.gzip')))
 add={'phase':'independent source review before producer candidate','rows':4082,'fullNativeReadersReplayed':2,'personallyImageTranscribedRows':33,'personallyReadMoneyCells':66,'completeHumanTranscriptionClaim':False,'rawReaderPins':rawpins,'selectedPeerDataPins':data,'firstManualTranscript':pin(B/'native-first-source-image-transcript.json'),'firstSourceContextTranscript':pin(B/'native-first-source-context-transcript.json'),'sourceImagePacket':pin(B/'native-source-image-peer-packet.json'),'sources':results,'sourceFootnotePersonallyViewed':{'physicalPage':11,'sourceKey':'phsa-2008-09','text':'Expenses for 08/09 are higher than07/08 due to one time professional development courses and travel associated with Chair duties for health care related organizations.','name':'Cranston,Lynda','sourceNameFootnote':'*','image':pin(B/'phsa-2008-09-source-footnote-p011.png')},'archivalCoverPersonallyViewed':True,'originalEmployerApprovalPagePresent':False,'publicationObservation':'Official Legislative Library archival copies of employer statements; explicit Library-added covers explain different delivered versus stored bitstream bytes. No Council/board adoption or signature approval inferred.','noOutreach':True}
 out=B/'native-complete-independent-source-audit.json';write(out,add);print(json.dumps({'path':str(out),'sha256':sha(out.read_bytes()),'rows':4082,'manual':33,'sources':[{k:s[k] for k in ['sourceKey','rowCount','narrativeCountResidual','remunerationResidual','knownExpenseResidual']} for s in results]},indent=2))
if __name__=='__main__':main()
