from pathlib import Path
import json,re
A=Path(__file__).parent;j=json.loads((A/'full-source-coverage-and-guard-audit.json').read_text());classified=[]
for district in j:
 for item in district['outsideSelectedPayAnchors']:
  text=item['wholePageHorizontalText'];plain=re.sub(r'\s+','',text).upper().lstrip('|');kind=None
  if '4690ROGERSTREET'in plain and ('723-3565'in plain or '723-0318'in plain):kind='printed-letterhead-address-and-phone-numbers'
  elif plain.startswith('STATEMENTOFFINANCIALINFORMATION(SOFI)|FISCALYEARENDEDJUNE30,2025'):kind='printed-fiscal-year-footer'
  elif plain.startswith(('TOTALELECTEDOFFICIALS','TOTALFORELECTEDOFFICIALS')):kind='printed-trustee-control'
  elif plain.startswith('TOTALDETAILEDEMPLOYEES'):kind='printed-named-employee-control'
  elif plain.startswith(('TOTALEMPLOYEES<=','PAIDTOEACHEMPLOYEEWAS$75,000.00ORLESS')):kind='printed-unnamed-employee-aggregate'
  elif plain.startswith(('TOTALEMPLOYEESOTHERTHANELECTED','CONSOLIDATEDTOTAL'))or plain.startswith('TOTAL45,053,062.35'):kind='printed-combined-control'
  elif plain.startswith('TOTALEMPLOYERPREMIUMFORCPP/EI'):kind='printed-employer-CPP-EI-aggregate'
  elif plain.startswith('C.REMUNERATIONFORELECTEDOFFICIALS'):kind='printed-repeated-trustee-control'
  assert kind,(district['district'],item);classified.append({'district':district['district'],**item,'sourceDisposition':kind,'notAnIndividualObservation':True})
(A/'broad-outside-payment-anchor-classifications.json').write_text(json.dumps({'allBroadOutsideAnchors':len(classified),'unexplained':0,'classifications':classified,'basis':'Actual first/last salary context pages were personally viewed; exact repeated letterhead/fiscal footer source labels are retained. Independent census used any-digit pay-column anchors before applying names/number parsing and no table Y window. This supplements source-specific parser census and guards correlated row exclusions.'},ensure_ascii=False,indent=2)+'\n');print('Classified',len(classified),'broad outside source anchors; no unexplained observations')
