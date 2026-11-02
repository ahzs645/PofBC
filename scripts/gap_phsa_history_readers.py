#!/usr/bin/env python3
"""Source-profile geometry and separate literal readers for PHSA scan evidence."""
import csv
import io
import re
import statistics


def name_comparison(value):
    return re.sub(r'\s*,\s*',',',re.sub(r'\s+',' ',value).strip())


def money(raw):
    token=re.sub(r'\s+','',raw)
    if token in ['-','–','—']:return {'kind':'explicit-dash','value':None,'raw':raw}
    if not token:return {'kind':'not-recognized','value':None,'raw':raw}
    if re.fullmatch(r'(?:\d{1,3}(?:,\d{3})+|\d+)',token):
        return {'kind':'number','value':int(token.replace(',','')),'raw':raw}
    if re.fullmatch(r'\((?:\d{1,3}(?:,\d{3})+|\d+)\)',token):
        return {'kind':'number','value':-int(token[1:-1].replace(',','')),'raw':raw}
    if re.fullmatch(r'-(?:\d{1,3}(?:,\d{3})+|\d+)',token):
        return {'kind':'number','value':int(token.replace(',','')),'raw':raw}
    return {'kind':'unparsed','value':None,'raw':raw}


def tess_words(tsv):
    result=[]
    # Tesseract text may itself begin with a literal quote. It is not CSV quoting.
    for w in csv.DictReader(io.StringIO(tsv),delimiter='\t',quoting=csv.QUOTE_NONE):
        if w['level']!='5' or not w.get('text','').strip():continue
        x,y,width,height=[int(w[k]) for k in ['left','top','width','height']]
        result.append({'text':w['text'],'box':[x,y,x+width,y+height],
                       'x':x+width/2,'y':y+height/2,'confidence':float(w['conf']),
                       'line':tuple(w[k] for k in ['page_num','block_num','par_num','line_num'])})
    return result


def source_profile(raw,fixture):
    words=tess_words(raw['tesseractRawTsv'])
    width,height=raw['renderer']['imageDimensions']
    name_headers=[w for w in words if w['text'].lower()=='name' and w['x']<width*.5 and w['y']<height*.4]
    if len(name_headers)!=1:raise ValueError('Source table Name header needs a literal image profile')
    headers={}
    for label in ['Name','Remuneration','Expenses']:
        hits=[w for w in words if w['text'].lower()==label.lower() and abs(w['y']-name_headers[0]['y'])<30]
        if len(hits)!=1:raise ValueError('Source table header needs literal image profile: '+label)
        headers[label]=hits[0]
    name_lines={}
    for w in words:
        if headers['Name']['box'][3]<w['y']<height*.94 and w['x']<headers['Remuneration']['box'][0]-30:
            name_lines.setdefault(w['line'],[]).append(w['y'])
    centers=sorted(statistics.mean(v) for v in name_lines.values())
    pitch=statistics.median(b-a for a,b in zip(centers,centers[1:]))
    legal_footer=[w for w in words if w['text'].lower() in ['this','statement'] and w['y']>height*.90]
    if not legal_footer:raise ValueError('Source legal footer boundary needs explicit image profile')
    return {'sourceId':raw['sourceId'],'sourceSha256':raw['sourceSha256'],'year':raw['yearFromInventory'],
            'imageDimensions':[width,height],'firstSalaryPhysicalPage':int(fixture[0]['physicalPage']),
            'firstSalaryRowCount':len(fixture),'firstTableHeaders':headers,
            'namePayBoundary':headers['Remuneration']['box'][0]-30,
            'payExpenseBoundary':headers['Expenses']['box'][0]-30,
            'sourceFirstTableRowPitchPixels':pitch,
            'sourceLegalFooterTop':min(w['box'][1] for w in legal_footer),
            'sourceFirstTableLegalFooterWords':legal_footer,
            'tableBodyBottomFraction':.94,'tableHeaderSearchBottomFraction':.4,
            'initialUncalibratedConfidenceRules':{'rapidName':.98,'tesseractName':85,
                                                  'rapidMoney':.98,'tesseractMoney':90},
            'geometryDefinition':'Original per-source printed columns anchored by the independently image-transcribed first table. Each page header and final Total are located separately. No universal row count, footer count or dash template.'}


def read_tesseract(raw,profile):
    words=tess_words(raw['tesseractRawTsv']);height=profile['imageDimensions'][1]
    headers=[w for w in words if w['text'].lower()=='name' and w['x']<profile['namePayBoundary'] and w['y']<height*.4]
    if len(headers)!=1:return [],[],['tesseract-table-header-count-'+str(len(headers))]
    top=headers[0]['box'][3];bottom=min(height*profile['tableBodyBottomFraction'],profile['sourceLegalFooterTop']-5)
    totals=[w for w in words if w['text'].lower() in ['total','totals'] and w['x']<profile['namePayBoundary'] and top<w['y']<bottom]
    if totals:bottom=min(w['box'][1] for w in totals)
    grouped={}
    for w in words:
        if top<w['y']<bottom:grouped.setdefault(w['line'],[]).append(w)
    rows=[]
    for group in grouped.values():
        group=sorted(group,key=lambda w:w['x'])
        name=[w for w in group if w['x']<profile['namePayBoundary']]
        if not name:continue
        pay=[w for w in group if profile['namePayBoundary']<=w['x']<profile['payExpenseBoundary']]
        expense=[w for w in group if w['x']>=profile['payExpenseBoundary']]
        rows.append({'name':' '.join(w['text'] for w in name),'y':statistics.mean(w['y'] for w in name),
                     'nameBox':[min(w['box'][0] for w in name),min(w['box'][1] for w in name),
                                max(w['box'][2] for w in name),max(w['box'][3] for w in name)],
                     'nameConfidence':min(w['confidence'] for w in name),
                     'pay':money(' '.join(w['text'] for w in pay)),
                     'expense':money(' '.join(w['text'] for w in expense)),
                     'payConfidence':min([w['confidence'] for w in pay],default=None),
                     'expenseConfidence':min([w['confidence'] for w in expense],default=None),
                     'rawWords':group})
    return sorted(rows,key=lambda r:r['y']),totals,[]


def read_rapid(raw,profile,alternative=None):
    entries=[]
    for box,text,confidence in raw['rapidocrRaw'] if alternative is None else alternative:
        entries.append({'text':text,'confidence':confidence,'box':box,
                        'x':sum(p[0] for p in box)/4,'y':sum(p[1] for p in box)/4})
    height=profile['imageDimensions'][1]
    headers=[r for r in entries if r['text'].strip().lower()=='name' and r['x']<profile['namePayBoundary'] and r['y']<height*.4]
    if len(headers)!=1:return [],[],['rapid-table-header-count-'+str(len(headers))]
    top=max(p[1] for p in headers[0]['box']);bottom=min(height*profile['tableBodyBottomFraction'],profile['sourceLegalFooterTop']-5)
    totals=[r for r in entries if r['text'].strip().lower() in ['total','totals'] and r['x']<profile['namePayBoundary'] and top<r['y']<bottom]
    if totals:bottom=min(min(p[1] for p in r['box']) for r in totals)
    body=[r for r in entries if top<r['y']<bottom]
    name_boxes=sorted([r for r in body if r['x']<profile['namePayBoundary']],key=lambda r:r['y'])
    pitch=profile['sourceFirstTableRowPitchPixels']
    groups=[]
    for entry in name_boxes:
        if groups and abs(entry['y']-statistics.mean(r['y'] for r in groups[-1]))<pitch*.35:
            groups[-1].append(entry)
        else:groups.append([entry])
    names=[]
    for group in groups:
        group.sort(key=lambda r:r['x'])
        names.append({'text':' '.join(r['text'] for r in group),'confidence':min(r['confidence'] for r in group),
                      'box':[p for r in group for p in r['box']],
                      'y':statistics.mean(r['y'] for r in group),'pieces':group})
    rows=[]
    for name in names:
        pay=[r for r in body if profile['namePayBoundary']<=r['x']<profile['payExpenseBoundary'] and abs(r['y']-name['y'])<pitch*.35]
        expense=[r for r in body if r['x']>=profile['payExpenseBoundary'] and abs(r['y']-name['y'])<pitch*.35]
        rows.append({'name':name['text'],'nameConfidence':name['confidence'],'nameBox':name['box'],'y':name['y'],
                     'namePieces':name['pieces'],
                     'pay':money(pay[0]['text']) if len(pay)==1 else money(''),
                     'expense':money(expense[0]['text']) if len(expense)==1 else money(''),
                     'payConfidence':pay[0]['confidence'] if len(pay)==1 else None,
                     'expenseConfidence':expense[0]['confidence'] if len(expense)==1 else None,
                     'rawPayMatches':pay,'rawExpenseMatches':expense})
    return rows,totals,[]
