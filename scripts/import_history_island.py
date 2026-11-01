#!/usr/bin/env python3
"""Reproduce reviewed island/coast municipal histories without changing prior collections."""
import argparse
from collections import defaultdict
from decimal import Decimal
import gzip
import hashlib
import json
from pathlib import Path
import re
import subprocess
import urllib.request
import fitz

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'research/salaries/municipal-history-island'
AUDIT=ROOT/'research/salaries/municipal-history-pass/island'
CACHE=Path('/tmp/pofbc-history-island')
NUM=r'-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{2})?'
MONEY=re.compile(r'\$?(?:'+NUM+r'|\('+NUM+r'\)|-)')


def pack(raw):
    # A fixed portable OS header keeps gzip bytes identical across Python hosts.
    out=bytearray(gzip.compress(raw,mtime=0));out[9]=255;return bytes(out)

def sha(raw):return hashlib.sha256(raw).hexdigest()
def money(raw):
    raw=raw.replace('$','').strip()
    if raw in ['', '-']:return None
    if raw.startswith('(') and raw.endswith(')'):raw='-'+raw[1:-1]
    if not MONEY.fullmatch(raw):raise ValueError(f'Invalid amount {raw!r}')
    n=Decimal(raw.replace(',',''));return int(n) if n==n.to_integral_value() else float(n)
def summed(rows,i):return sum((Decimal(str(r[i])) for r in rows if r[i] is not None),Decimal())


def profiles():
    out=[]
    def add(slug,y,kind,pages,index,nameright,mode='separate',end='Total'):
        out.append(dict(slug=slug,year=str(y),kind=kind,pages=pages,headerIndex=index,nameRight=nameright,mode=mode,end=end))
    for y in range(2021,2025):
        add('city-of-courtenay',y,'employees',[32,33] if y==2021 else [32,33,34],0,{2021:120,2022:149,2023:150,2024:134}[y])
        add('city-of-courtenay',y,'council',[31],0,200)
        n={2021:32,2022:31,2023:32,2024:31}[y]
        add('village-of-cumberland',y,'employees',[n],1,250,end='Consolidated')
        add('village-of-cumberland',y,'council',[n],0,240)
        if y==2024:
            add('town-of-gibsons',y,'employees',[10],0,145,end='Remuneration:')
            add('town-of-gibsons',y,'council',[9],0,190)
        else:
            n={2021:32,2022:33,2023:38}[y]
            add('town-of-gibsons',y,'employees',[n],1,350,mode='comma-role',end='Consolidated')
            add('town-of-gibsons',y,'council',[n],0,220)
    for y,n in [(2021,27),(2022,25),(2023,26)]:
        add('village-of-tahsis',y,'employees',[n],1,265 if y!=2021 else 265,mode='separate',end='Consolidated')
        add('village-of-tahsis',y,'council',[n],0,265)
    for y,first in [(2023,29),(2024,27)]:
        add('district-of-ucluelet',y,'employees',[first+1],0,190 if y==2023 else 205,mode='printed-name',end='Aggregate')
        add('district-of-ucluelet',y,'council',[first],0,210,mode='printed-name',end='numeric-subtotal')
    for y in [2021,2022]:
        add('village-of-sayward',y,'employees',[2],1,410,mode='dash-role',end='Consolidated' if y==2021 else 'numeric-subtotal')
        add('village-of-sayward',y,'council',[2],0,410,mode='prefix-role' if y==2021 else 'dash-role',end='Total' if y==2021 else 'numeric-subtotal')
    add('town-of-port-mcneill',2021,'employees',[28],0,200)
    add('town-of-port-mcneill',2021,'council',[27],0,200)
    add('city-of-courtenay',2020,'employees',[32,33,34],0,120)
    add('city-of-courtenay',2020,'council',[31],0,200)
    for y,n in [(2014,27),(2015,28),(2016,29),(2017,29),(2018,30),(2019,29),(2020,32)]:
        edge={2014:210,2015:210,2016:210,2017:218,2018:240,2019:280,2020:240}[y]
        add('village-of-cumberland',y,'employees',[n],1,edge,end='Consolidated')
        add('village-of-cumberland',y,'council',[n],0,edge)
    for y in [2018,2019,2020]:
        add('district-of-lantzville',y,'employees',[4],1,160,end='Employees')
        add('district-of-lantzville',y,'council',[4],0,170)
    for y,n in [(2019,25),(2020,27)]:
        add('village-of-tahsis',y,'employees',[n],1,265,end='Consolidated')
        add('village-of-tahsis',y,'council',[n],0,265)
    for y in [2012,2013]:
        add('district-of-tofino',y,'employees',[5],1,160,mode='separate' if y==2012 else 'separate-given',end='Consolidated')
        add('district-of-tofino',y,'council',[5],0,190,mode='separate-given')
    add('district-of-tofino',2021,'employees',[5],1,160,mode='separate-given',end='Consolidated')
    add('district-of-tofino',2021,'council',[5],0,190,mode='separate-given')
    return out


def split_name_title(name,title,mode):
    if mode=='comma-role':
        a=name.split(',',2);assert len(a)==3,('Missing printed name/title delimiter',name)
        return ','.join(a[:2]).strip(),' '.join(x for x in [a[2].strip(),title] if x)
    if mode=='dash-role':
        a=name.split(' - ',1);assert len(a)==2,('Missing printed role delimiter',name)
        return a[0],' '.join(x for x in [a[1],title] if x)
    if mode=='prefix-role':
        m=re.fullmatch(r'(Mayor|Councillor) (.+)',name);assert m,name
        return m[2],m[1]
    return name,title


def positioned(page,cfg):
    area=page.rect.get_area();large=[x for x in page.get_image_info() if fitz.Rect(x['bbox']).get_area()/area>.8]
    assert not large,('OCR overlay is not native independent text',cfg['slug'],cfg['year'],page.number+1)
    words=page.get_text('words');mode=cfg['mode'];pairs=[]
    for w in words:
        if w[4].casefold() not in ['remuneration','renumeration']:continue
        tolerance=15 if cfg['slug']=='village-of-tahsis' and cfg['year']=='2019' else 3
        ex=[x for x in words if x[4].casefold()in ['expenses','expense'] and abs(x[1]-w[1])<tolerance and x[0]>w[0]]
        pos=[x for x in words if x[4].casefold()=='position' and abs(x[1]-w[1])<3]
        if len(ex)==1 and (pos or (mode in ['comma-role','dash-role','prefix-role'] and w[0]>300) or (cfg['slug']=='town-of-gibsons' and cfg['year']=='2024' and w[1]>150)):
            pairs.append((w,ex[0]))
    pairs.sort(key=lambda z:z[0][1]);ph,eh=pairs[cfg['headerIndex']];hy=ph[1]
    th=[w for w in words if w[4].casefold()=='total' and abs(w[1]-hy)<3 and w[0]>eh[0]]
    bh=[w for w in words if w[4]=='Benefits' and abs(w[1]-hy)<3 and ph[0]<w[0]<eh[0]]
    heads=[ph]+bh+[eh]+th
    end=cfg['end'];cut=min([w[1] for w in words if w[1]>hy+3 and (w[4].casefold().rstrip(':')==end.casefold().rstrip(':') or w[4]=='Prepared' or (w[4]=='Statement' and any(z[4]=='Financial' and abs(z[1]-w[1])<2 for z in words)))]+[page.rect.height-42])
    if end=='numeric-subtotal':
        for w in words:
            if w[1]<=hy+3 or not MONEY.fullmatch(w[4]) or not cfg['nameRight']<w[0]<eh[0]-4:continue
            same=[z for z in words if z[0]<cfg['nameRight'] and abs(z[1]-w[1])<2 and re.search('[A-Za-z]',z[4])]
            if not same:cut=min(cut,w[1])
    body=[w for w in words if hy+3<w[1]<cut-1]
    ng=[]
    for w in sorted([w for w in body if w[0]<cfg['nameRight']],key=lambda w:(round(w[1]),w[0])):
        if not ng or abs(ng[-1][0]-w[1])>1.4:ng.append([w[1],[]])
        ng[-1][1].append(w)
    ng=[g for g in ng if not ' '.join(w[4] for w in g[1]).startswith(('Remuneration over','Remuneration Over'))]
    if mode=='comma-role':
        grouped=[]
        for y,line in ng:
            text=' '.join(w[4] for w in line)
            if text.count(',')>=2:grouped.append([y,line])
            else:
                assert grouped,('Unexpected role continuation',text)
                grouped[-1][1].extend(line)
        ng=grouped
    out=[];evidence=[];word_indices={id(w):i for i,w in enumerate(words)};body_ids={id(w) for w in body}
    for i,(y,nw) in enumerate(ng):
        nxt=ng[i+1][0] if i+1<len(ng) else cut
        start=min(word_indices[id(w)] for w in nw)
        stop=min(word_indices[id(w)] for w in ng[i+1][1]) if i+1<len(ng) else len(words)
        # Native cell content order preserves titles which begin visually above
        # a bottom-aligned employee name. Coordinates still define the monetary
        # columns, and the independent reader uses page layout rather than this
        # PDF cell sequence.
        rw=[w for w in words[start:stop] if id(w) in body_ids]
        name=' '.join(w[4] for w in sorted(nw,key=lambda w:(round(w[1]),w[0])))
        if not re.search('[A-Za-z]',name):raise ValueError(('Invalid name',name))
        values=[];used=set()
        for j,h in enumerate(heads):
            left=h[0]-12;right=heads[j+1][0]-4 if j+1<len(heads) else page.rect.width
            if cfg['slug']=='district-of-tofino':
                split=480 if cfg['year']=='2021' else 475
                if bh:left,right=[(330,430),(430,490),(490,page.rect.width)][j]
                else:left,right=(380,split) if j==0 else (split,page.rect.width)
            nums=[(k,w) for k,w in enumerate(rw) if left<w[0]<right and MONEY.fullmatch(w[4])]
            assert len(nums)<=1,('Ambiguous monetary cell',name,j,nums)
            values.append(money(nums[0][1][4]) if nums else None);used.update(k for k,w in nums)
        malformed=[(k,w) for k,w in enumerate(rw) if w[0]>=eh[0]-12 and re.search(r'\d',w[4]) and not MONEY.fullmatch(w[4])]
        if malformed:
            assert cfg['slug']=='district-of-ucluelet' and cfg['year']=='2023' and name=='Fortune Abigail' and [w[4]for k,w in malformed]==['3,3463.64'],('Unexpected nonnumeric monetary cell',name,malformed)
            used.update(k for k,w in malformed)
        assert values[0] is not None,('Missing pay',cfg['slug'],cfg['year'],name,rw)
        title=' '.join(w[4] for k,w in sorted(enumerate(rw),key=lambda z:(round(z[1][1]),z[1][0])) if k not in used and w[0]>=cfg['nameRight'] and w[4]!='$') or None
        name,title=split_name_title(name,title,mode)
        assert not any(z in (title or '') for z in ['Consolidated','STATEMENT','Schedule 1','Remuneration Expenses']),('Table boundary leaked into title',name,title)
        expense=values[2] if bh else values[1]
        out.append([name,title,values[0],expense,page.number+1]);evidence.append(dict(row=out[-1],printedAdditionalTotal=values[-1] if th else None,printedBenefits=values[1] if bh else None,unusableExpenseLiteral='3,3463.64' if malformed else None,words=[list(w[:5]) for w in rw]))
    return out,evidence


def layout(text,cfg):
    lines=text.splitlines();headers=[]
    for i,line in enumerate(lines):
        if re.search(r'(?i)(?:Name|Employee|Elected Official).*?(?:Remuneration|Renumeration)\s*(?:\(\$\))?\s*(?:Benefits\s*)?Expenses?',line):headers.append(i)
        elif cfg['slug']=='village-of-tahsis' and cfg['year']=='2019' and re.search(r'Name\s+Position\s+Remuneration',line):headers.append(i)
        elif cfg['slug']=='town-of-gibsons' and cfg['year']=='2024' and re.fullmatch(r'\s*(?:Remuneration|Renumeration)\s+Expenses\s+Total\s*',line):headers.append(i)
    assert len(headers)>cfg['headerIndex'],('Missing layout header',cfg,headers)
    headerline=lines[headers[cfg['headerIndex']]]
    name_indent=max(8,len(headerline)-len(headerline.lstrip())+5)
    current=None;records=[];pending_title=[]
    for line in lines[headers[cfg['headerIndex']]+1:]:
        st=line.strip()
        if not st:continue
        if current is None and st in ['($)','$']:continue
        if current is None and cfg['slug']=='village-of-tahsis' and st=='(Note 1)':continue
        if cfg['end']=='Remuneration:' and st.startswith('Remuneration:'):break
        if cfg['end']=='Employees' and st.startswith('Employees less than'):break
        if re.match(r'(?i)^(Total|Consolidated|Aggregate|3\. Reconciliation|Statement of|Prepared under|THE CORPORATION)',st):break
        if st.startswith(('Remuneration over','Remuneration Over')):continue
        parts=re.split(r'\s{2,}',st)
        onlynums=all(all(MONEY.fullmatch(t) for t in x.replace('$','').split()) for x in parts)
        if onlynums and current is not None and current[2]:break
        mode=cfg['mode']
        if mode=='printed-name':starts=len(parts)>2 and not MONEY.fullmatch(parts[0])
        elif cfg['slug']=='village-of-tahsis' or mode=='separate-given':starts=len(line)-len(line.lstrip())<name_indent
        elif mode=='prefix-role':starts=st.startswith(('Mayor ','Councillor '))
        else:starts=',' in parts[0] and not MONEY.fullmatch(parts[0].replace('$','').strip()) and len(line)-len(line.lstrip())<name_indent
        bottom_aligned=cfg['slug']=='city-of-courtenay' or (cfg['slug']=='village-of-cumberland' and int(cfg['year'])<=2017) or (cfg['slug']=='district-of-tofino' and cfg['year']=='2012')
        if bottom_aligned and not starts and not any(MONEY.fullmatch(x.replace('$','').strip()) for x in parts):
            pending_title.extend(parts);continue
        if starts:
            if current is not None:records.append(current)
            if mode=='printed-name':name=' '.join(parts[:2]);parts=parts[2:]
            else:name=parts.pop(0)
            current=[name,pending_title,[]];pending_title=[]
        assert current is not None,('Unexpected pre-row text',cfg,line)
        for p in parts:
            clean=p.replace('$','').strip()
            if clean=='3,3463.64':
                assert cfg['slug']=='district-of-ucluelet' and cfg['year']=='2023' and current[0]=='Fortune Abigail'
                current[2].append(None);continue
            tokens=clean.split()
            if tokens and all(MONEY.fullmatch(t) for t in tokens):current[2].extend(money(t) for t in tokens)
            elif clean:
                if ((cfg['slug']=='city-of-courtenay' and cfg['year']=='2020') or (cfg['slug']=='village-of-cumberland' and int(cfg['year'])<=2017)) and p.endswith(' $'):p=p[:-2]
                current[1].append(p)
    if current is not None:records.append(current)
    result=[]
    totalcol=cfg['slug']=='town-of-port-mcneill' or (cfg['slug']=='town-of-gibsons' and cfg['year']=='2024')
    for name,title,nums in records:
        assert 1<=len(nums)<=3,(cfg,name,title,nums)
        if totalcol and len(nums)==2:nums.insert(1,None)
        if len(nums)==1:nums.append(None)
        if cfg['slug']=='district-of-tofino' and cfg['year']=='2021' and cfg['kind']=='council':
            assert len(nums)==3;nums=[nums[0],nums[2]]
        name,title=split_name_title(name,' '.join(title) or None,cfg['mode'])
        result.append([name,title,nums[0],nums[1]])
    return result



def numeric_tail(line,n):
    nums=[]
    for tok in line.replace(' $ ',' ').split():
        if tok.casefold()=='n/a':nums.append(None)
        elif MONEY.fullmatch(tok):nums.append(money(tok))
    return nums[-n:] if len(nums)>=n else None


def controls(doc,pdf,cfg):
    slug=cfg['slug'];kind=cfg['kind'];year=cfg['year'];page_n=cfg['pages'][-1]
    patterns=[]
    if kind=='council':
        if slug=='district-of-ucluelet' or (slug=='village-of-sayward' and year=='2022'):
            patterns=[('named',r'^\s*[\d,.]+\s+[\d,.]+\s*$',2,0)]
        elif slug=='district-of-tofino':patterns=[('named',r'^ Total: Elected officials',3 if year=='2021' else 2,0)]
        else:patterns=[('named',r'^\s*Total(?::|\s|$)',3 if slug=='town-of-port-mcneill' or(slug=='town-of-gibsons'and year=='2024')else 2,0)]
    elif slug=='city-of-courtenay':patterns=[('named',r'^Total for employees where',2,0),('under',r'^Consolidated total',2,0)]
    elif slug=='town-of-port-mcneill':patterns=[('named',r'^Total\s',3,0)]
    elif slug=='district-of-ucluelet':patterns=[('named',r'^Aggregate over',2,0),('under',r'^Aggregate under',2,0),('all',r'^Totals',2,0)]
    elif slug=='village-of-sayward' and year=='2022':patterns=[('named',r'^\s*[\d,.]+\s+[\d,.]+\s*$',2,1),('under',r'^Consolidated total',2,0)]
    elif slug=='district-of-lantzville':patterns=[('under',r'^\s*Employees less than',2,0),('all',r'^\s*Total.*Employees',2,0)]
    else:
        allpat={'village-of-cumberland':r'^Total: Other Employees','town-of-gibsons':r'^\s*Total Other Employees' if year!='2024' else r'^ Total\s','village-of-tahsis':r'^Total Employees','village-of-sayward':r'^Total Employees','district-of-tofino':r'^ Total: Other employees'}[slug]
        if slug=='town-of-gibsons' and year=='2024':patterns=[('named',r'^ Remuneration:.*Above',3,0),('under',r'^ Remuneration:.*Up to',3,0),('all',allpat,3,0)]
        else:patterns=[('under',r'^\s*Consolidated [Tt]otal',2,0),('all',allpat,2,0)]
    txt=subprocess.check_output(['pdftotext','-f',str(page_n),'-l',str(page_n),'-layout',str(pdf),'-'],text=True)
    lines=txt.splitlines();out=[]
    for scope,pat,n,occurrence in patterns:
        hits=[i for i,l in enumerate(lines)if re.search(pat,l,re.I)]
        assert len(hits)>occurrence,('Missing control label',cfg,scope,pat)
        start=hits[occurrence];line=None;values=None
        for j in range(start,min(start+5,len(lines))):
            values=numeric_tail(lines[j],n)
            if values is not None:line=lines[j];break
        assert values is not None,('Missing control amounts',cfg,scope)
        # Locate the same complete monetary cells in independent positioned text.
        wordlines=[]
        for w in sorted(doc[page_n-1].get_text('words'),key=lambda w:(round(w[1]),w[0])):
            if not wordlines or abs(wordlines[-1][0]-w[1])>1.6:wordlines.append([w[1],[]])
            wordlines[-1][1].append(w)
        matches=[]
        for yy,ww in wordlines:
            ww.sort(key=lambda w:w[0])
            joined=' '.join(w[4]for w in ww)
            if numeric_tail(joined,n)==values:matches.append((yy,ww))
        assert matches,('Control readers disagree',cfg,scope,values,line)
        # Repeated monetary controls in reconciliation sections remain separate
        # evidence; the first printed schedule occurrence is retained here.
        yy,ww=matches[0]
        out.append(dict(scope=scope,labelRegex=pat,printedValues=values,physicalPdfPage=page_n,popplerLayoutLine=line,positionedWords=[list(w[:5])for w in ww],bothReadersAgree=True))
    return out


def expected_named(control,cfg):
    by={x['scope']:x['printedValues']for x in control}
    if 'named'in by:
        v=by['named'];return [v[0],v[2]if cfg['slug']=='district-of-tofino'and cfg['year']=='2021'and cfg['kind']=='council' else v[1]]
    a,b=by['all'],by['under']
    # An unavailable below-threshold expense total cannot be subtracted as zero.
    # The broader all-employee control does not establish a named comparator.
    def difference(x,y):
        v=Decimal(str(x))-Decimal(str(y));return int(v)if v==v.to_integral_value()else float(v)
    return [difference(a[0],b[0]), None if a[1]is None or b[1]is None else difference(a[1],b[1])]


def normalize_json(obj):return (json.dumps(obj,ensure_ascii=False,separators=(',',':'))+'\n').encode()


def make_source(cfg,receipt,rows,control):
    slug=cfg['slug'];year=cfg['year'];employee=cfg['kind']=='employees';expected=expected_named(control,cfg)
    pay=summed(rows,3);exp=summed(rows,4);delta=[float(pay-Decimal(str(expected[0]))),None if expected[1]is None else float(exp-Decimal(str(expected[1])))]
    warnings=[]
    if any(delta):
        expense_text=f"known disclosed expenses ${delta[1]:+.2f}"if delta[1]is not None else'named expense comparator unavailable'
        warnings.append(f"Published named rows differ from the printed named control (or all employees minus the below-threshold aggregate): remuneration ${delta[0]:+.2f}; {expense_text}. The cause is unresolved; published cells are retained unchanged.")
    broader_expense=None
    if employee and expected[1]is None:
        by={x['scope']:x['printedValues']for x in control};all_expense=by['all'][1]
        broader_expense=dict(knownNamedEmployeeExpenses=float(exp),printedAllEmployeeExpenses=all_expense,printedBelowThresholdExpense=None,printedBelowThresholdExpenseLiteral='n/a',knownNamedMinusAllEmployeeExpenses=None if all_expense is None else float(exp-Decimal(str(all_expense))),comparisonScope='different scopes; not a named-employee expense reconciliation',namedEmployeeExpenseComparatorAvailable=False)
        warnings.append(f"The source prints below-threshold employee expenses as n/a, which does not establish zero. A named-employee expense comparator is unavailable. Known named expenses ${float(exp):,.2f} and printed all-employee expenses ${all_expense:,.2f} cover different scopes; their difference is not a named expense reconciliation. Published row expenses are unchanged.")
    malformed=slug=='district-of-ucluelet'and year=='2023'and employee
    if malformed:
        warnings=["Abigail Fortune's expense cell is literally printed '3,3463.64' and cannot be interpreted reliably. Her unambiguous published remuneration is retained; expenses are missing, without comma removal or subtotal-based inference. The literal is retained in evidence. Full named expense reconciliation remains unresolved; the known numeric expenses total $23,514.08 against the printed $26,977.72 named control."]
    notes=["Employee and elected-official cohorts remain separate; under-threshold and grand-total aggregates are evidence only. Names, initials, source spelling and printed title abbreviations are retained. No departments are inferred.","Blank and dash expense cells remain missing; explicit numeric zeroes and negative amounts remain numeric. These payment disclosures are not annual base salary rates or complete employee rosters.","No compiled records are deleted, relabelled or inferred to belong to these periods."]
    if slug=='city-of-courtenay'and year=='2020':notes.append('The source explicitly states that calendar2020 includes an additional pay period beyond the usual26 pay periods; this affects comparisons with other years.')
    if slug=='town-of-gibsons'and year in ['2021','2022','2023']:notes.append('The source prints names and roles together; the first two comma-delimited fields retain the printed name and subsequent text retains the printed role. Its footnote includes overtime/extended-hours payments, applicable vehicle allowances and taxable benefits in remuneration.')
    if slug in ['town-of-gibsons','town-of-port-mcneill']:notes.append('Expense-inclusive additional Total cells are retained as evidence only, never remuneration. Equal salary and Total cells do not convert blank expenses to zero.')
    if slug=='district-of-ucluelet':notes.append('The source prints surname and given name in adjacent Name columns; they are joined with a space in the same printed order. The source labels its schedules unaudited and prepared on a cash basis.')
    if slug=='city-of-courtenay'and year in ['2022','2023','2024']and employee:notes.append('One title is visibly clipped at the cell edge. A source/year/name/token-guarded correction removes Poppler-only hidden suffix glyphs; the visible PyMuPDF prefix is retained without expanding the title.')
    if slug=='town-of-port-mcneill'and not employee:warnings.append('The employee-page summary additionally reports council expenses of $2,426, differing by $1,048 from the named council schedule subtotal $1,378. The named published expense cells are retained; the cause is unresolved.')
    benefits=slug=='district-of-tofino'and year=='2021'and not employee
    if slug=='district-of-tofino'and year=='2021':warnings.append('The official posted report is not marked draft, but its approval page10 is an unsigned, undated template with highlighted names. Signed approval or adoption has not been established; published source fields are retained with this qualification.')
    if benefits:warnings.append('This measure uses the explicitly published Remuneration column only. Separately reported Benefits are retained in source evidence and excluded; inclusive total compensation is not established.')
    source=dict(id=f"history-island-{slug}-{year}-{cfg['kind']}",employerSlug=slug,employerName=receipt['employerName'],sector='Municipalities',year=year,periodType='calendar',periodStart=f'{year}-01-01',periodEnd=f'{year}-12-31',title=f"{receipt['employerName']} {year} official {'employee'if employee else'elected-official'} remuneration and expenses",sourceUrl=receipt['sourceUrl'],sourceIndexUrl=receipt['sourceIndexUrl'],sha256=receipt['sha256'],pdfBytes=receipt['bytes'],file=f"{slug}-{year}-{cfg['kind']}.json.gzip",currency='CAD',scope='employee-remuneration'if employee else'elected-officials',category='employee-remuneration'if employee else'elected-officials',nameDisclosure='as-published',positionDisclosure='as-published',rowCount=len(rows),totalRemuneration=float(pay),totalDisclosedExpenses=float(exp),pages=cfg['pages'],status='verified',verifiedOn='2026-10-31',completeEmployeeSchedule=True if employee else None,expensesComplete=False if malformed else not any(r[4]is None for r in rows),notes=notes,validation=dict(sourceFingerprintLocked=True,completeNamedCohort=True,completeEmployeeSchedule=True if employee else None,expensesComplete=False if malformed else not any(r[4]is None for r in rows),rowsIndependentlyCompared=len(rows),independentReaders=['PyMuPDF native positioned words','Poppler native layout'],bothReadersAgreeAfterGuardedVisibleTextCorrection=True,physicalPdfPages=cfg['pages'],printedControls=control,expectedNamedControl=expected,rowSumMinusNamedControl=delta,malformedExpenseLiteral='3,3463.64'if malformed else None,reviewedRowAndPageEdges=True))
    if employee:
        source['threshold']=75000
        if slug in ['city-of-courtenay','village-of-tahsis','district-of-ucluelet','town-of-port-mcneill']or(slug=='village-of-sayward'and year=='2022')or(slug=='town-of-gibsons'and year=='2024'):source['thresholdComparison']='>'
    if broader_expense:
        source['validation']['namedEmployeeExpenseComparatorAvailable']=False
        source['validation']['broaderEmployeeExpenseComparison']=broader_expense
        source['notes'].append('Below-threshold expense n/a remains unavailable, not zero. The all-employee expense control is broader than the known named rows and cannot establish a named-employee subtotal.')
    if benefits:source['scopeDescription']='Published Remuneration only; separately reported Benefits excluded; inclusive total compensation not established.'
    if warnings:source['publicWarning']=' '.join(warnings)
    return {k:v for k,v in source.items()if v is not None}


def guard_layout(cfg,n,other):
    # The rendered 2022 title ends at the cell clip. Poppler exposes
    # unpainted suffix glyphs; retain the visible PyMuPDF prefix only.
    if cfg['slug']=='city-of-courtenay' and cfg['year']=='2022' and cfg['kind']=='employees' and n==32:
        old='Manager of Financial Planning, Payroll & Business Performance'
        new='Manager of Financial Planning, Payroll & Business Perfo'
        hit=[x for x in other if x[0]=='Berard, A.'];assert len(hit)==1 and hit[0][1]==old
        hit[0][1]=new
    if cfg['slug']=='city-of-courtenay' and cfg['year']=='2023' and cfg['kind']=='employees' and n==34:
        hit=[x for x in other if x[0]=='Wyka, R.'];assert len(hit)==1 and hit[0][1]=='Manager of Financial Planning, Payroll & Business Performance'
        hit[0][1]='Manager of Financial Planning, Payroll & Busine'
    if cfg['slug']=='city-of-courtenay' and cfg['year']=='2024' and cfg['kind']=='employees' and n==34:
        hit=[x for x in other if x[0]=='Wyka, R.'];assert len(hit)==1 and hit[0][1]=='Manager of Financial Planning, Payroll & Bus. Performance'
        hit[0][1]='Manager of Financial Planning, Payroll & Bus. Performa'
    return other


def period_proof(doc,cfg):
    slug=cfg['slug'];year=cfg['year']
    if slug=='district-of-ucluelet':
        heading=re.search(year+r'\s+Statement of Financial Information',' '.join(doc[cfg['pages'][0]-1].get_text().split()),re.I);assert heading
        date=re.search(r'December 31,? '+year,' '.join(doc[4].get_text().split()),re.I);assert date
        return dict(physicalPdfPage=cfg['pages'][0],printedText=heading[0],financialStatementsPeriodPage=5,financialStatementsPeriodText=date[0],calendarYear=year,uploadedFilenameNotUsedAsPeriod=True)
    n=1 if slug in ['village-of-tahsis','district-of-tofino']else 32 if slug=='town-of-port-mcneill'else cfg['pages'][0]
    text=' '.join(doc[n-1].get_text().split())
    if slug in ['village-of-tahsis','district-of-tofino','town-of-port-mcneill','village-of-cumberland','district-of-lantzville']:
        pattern=r'(?:For the Year Ended|YEAR ENDED|Fiscal Year End:).*?December 31,? '+year
    elif slug=='city-of-courtenay':pattern=r'(?:for|For) the Year '+year
    elif slug=='town-of-gibsons':pattern=r'(?:January 1.*?December 31,|Year [Ee]nded December 31,) '+year
    else:pattern=r'(?:Employees for|Expenses for) '+year
    hit=re.search(pattern,text,re.I);assert hit,('Printed period missing',cfg,n,text[:500])
    return dict(physicalPdfPage=n,printedText=hit[0],calendarYear=year,uploadedFilenameNotUsedAsPeriod=True)


def verify_offline():
    manifest=json.loads((OUT/'sources.json').read_text());evidence=json.loads(gzip.decompress((OUT/'extraction-evidence.json.gzip').read_bytes()));sources={s['id']:s for s in manifest['sources']};receipts={r['sha256']for r in json.loads((AUDIT/'retrieval-receipts.json').read_text())if 'sha256'in r}
    assert len(sources)==len(evidence)
    class SavedPage:
        def __init__(self,reading):self.reading=reading;self.number=reading['physicalPdfPage']-1;self.rect=fitz.Rect(0,0,reading['pageWidth'],reading['pageHeight'])
        def get_image_info(self):return []
        def get_text(self,mode):assert mode=='words';return [tuple(w)for w in self.reading['pymupdfWords']]
    count=0
    for envelope in evidence:
        source=sources[envelope['sourceId']];assert source['sha256']==envelope['sourceSha256']and source['sha256']in receipts
        raw=(OUT/source['file']).read_bytes();decoded=gzip.decompress(raw);assert sha(raw)==source['dataSha256']and sha(decoded)==source['normalizedSha256'];rows=json.loads(decoded)
        if 'profile'in envelope:
            cfg=envelope['profile'];reproduced=[]
            assert expected_named(envelope['controls'],cfg)==source['validation']['expectedNamedControl']
            if 'controlInterpretation'in envelope:
                interpretation=envelope['controlInterpretation']
                for field in ['expectedNamedControl','rowSumMinusNamedControl','broaderEmployeeExpenseComparison']:
                    assert interpretation[field]==source['validation'][field]
            for reading in envelope['readings']:
                assert reading['largeSalaryPageImage']is False
                one,_=positioned(SavedPage(reading),cfg);two=guard_layout(cfg,reading['physicalPdfPage'],layout(reading['popplerLayoutText'],cfg));assert[x[:4]for x in one]==two
                reproduced.extend([[cfg['slug']]+r for r in one])
            assert reproduced==rows,source['id']
            for control in envelope['controls']:
                n=len(control['printedValues']);assert numeric_tail(control['popplerLayoutLine'],n)==control['printedValues'];assert numeric_tail(' '.join(w[4]for w in control['positionedWords']),n)==control['printedValues']
        else:
            manual=envelope['manual'];peer=envelope['independentReview'];assert manual['rows']==peer['rows']and peer['status']=='pass-final-fields-controls-and-documentation'
            kind='employees'if source['category']=='employee-remuneration'else'council';assert rows==[[source['employerSlug']]+r[1:]for r in manual['rows']if r[0]==kind]
        assert len(rows)==source['rowCount'];assert float(summed(rows,3))==source['totalRemuneration'];assert float(summed(rows,4))==source['totalDisclosedExpenses'];count+=len(rows)
    print(f'Offline evidence replay passed: {len(sources)} cohorts, {count} rows; original PDFs require --verify.')

def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--cache',type=Path,default=CACHE);ap.add_argument('--inspect',action='store_true');ap.add_argument('--offline-verify',action='store_true');ap.add_argument('--download-missing',action='store_true');ap.add_argument('--write',action='store_true');ap.add_argument('--verify',action='store_true');args=ap.parse_args();sources=[];evidence=[]
    if args.offline_verify:
        verify_offline();return
    args.cache.mkdir(parents=True,exist_ok=True)
    receipts={(r['employerSlug'],r['linkYear']):r for r in json.loads((AUDIT/'retrieval-receipts.json').read_text())}
    baseline={r['employerSlug']:r for r in json.loads((AUDIT.parent/'baseline.json').read_text())['municipalities']}
    for cfg in profiles():
        years=baseline[cfg['slug']]['officialEmployeeYears'if cfg['kind']=='employees'else'officialCouncilYears']
        assert cfg['year']not in years,('Already accepted in baseline',cfg)
        r=receipts[(cfg['slug'],cfg['year'])];pdf=args.cache/(cfg['slug']+'-'+cfg['year']+'.pdf');
        if not pdf.exists()and args.download_missing:pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(r['sourceUrl'],headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read())
        raw=pdf.read_bytes();assert sha(raw)==r['sha256']
        doc=fitz.open(pdf);rows=[];ev=[];readings=[];period=period_proof(doc,cfg)
        for n in cfg['pages']:
            primary,words=positioned(doc[n-1],cfg)
            text=subprocess.check_output(['pdftotext','-f',str(n),'-l',str(n),'-layout',str(pdf),'-'],text=True)
            other=layout(text,cfg)
            other=guard_layout(cfg,n,other)
            assert [x[:4] for x in primary]==other,(cfg['slug'],cfg['year'],cfg['kind'],n,'reader mismatch',[(a,b) for a,b in zip(primary,other) if a[:4]!=b][:2],len(primary),len(other))
            rows.extend([[cfg['slug']]+x for x in primary]);ev.extend(words);readings.append(dict(physicalPdfPage=n,popplerLayoutText=text,pymupdfWords=[list(w)for w in doc[n-1].get_text('words')],pageWidth=doc[n-1].rect.width,pageHeight=doc[n-1].rect.height,largeSalaryPageImage=False))
        dest=args.cache/(cfg['slug']+'-'+cfg['year']+'-'+cfg['kind']+'-candidate.json');dest.write_text(json.dumps(dict(profile=cfg,rows=rows,evidence=ev,readings=readings),ensure_ascii=False,indent=2))
        control=controls(doc,pdf,cfg);source=make_source(cfg,r,rows,control);source['validation']['periodProof']=period;encoded=normalize_json(rows);compressed=pack(encoded);source.update(dataSha256=sha(compressed),normalizedSha256=sha(encoded))
        envelope=dict(sourceId=source['id'],profile=cfg,sourceSha256=r['sha256'],rows=ev,readings=readings,controls=control,periodProof=period)
        if 'broaderEmployeeExpenseComparison'in source['validation']:
            envelope['controlInterpretation']=dict(expectedNamedControl=source['validation']['expectedNamedControl'],rowSumMinusNamedControl=source['validation']['rowSumMinusNamedControl'],broaderEmployeeExpenseComparison=source['validation']['broaderEmployeeExpenseComparison'])
        if cfg['slug']=='village-of-tahsis'and cfg['year']=='2019'and cfg['kind']=='council':
            source['validation']['independentFullImageReview']='research/salaries/municipal-history-pass/reviews/island-native.md'
            source['validation']['signedApprovalPhysicalPage']=28
            review=dict(status='qualified-accepted-with-unresolved-source-residual',reason='All five individual published fields independently image-verified. Pay sum $29,124 differs from printed $28,125 by +$999; cause unresolved. No cells adjusted.',candidateSource=source,extraction=envelope,normalizedCandidateRows=rows)
            if args.write:
                (AUDIT/'tahsis-2019-council-review-evidence.json.gzip').write_bytes(pack(normalize_json(review)))
                (AUDIT/'held-tahsis-2019-council.json.gzip').unlink(missing_ok=True)
            if args.verify:assert json.loads(gzip.decompress((AUDIT/'tahsis-2019-council-review-evidence.json.gzip').read_bytes()))==review
        sources.append(source);evidence.append(envelope)
        if args.write:(OUT/source['file']).write_bytes(compressed)
        if args.verify:assert (OUT/source['file']).read_bytes()==compressed,source['file']
        print(json.dumps(dict(slug=cfg['slug'],year=cfg['year'],kind=cfg['kind'],rows=len(rows),pay=str(summed(rows,3)),expenses=str(summed(rows,4)),first=rows[0],last=rows[-1]),ensure_ascii=False))

    ocr_pdf=args.cache/'district-of-lantzville-2025.pdf'
    if not ocr_pdf.exists()and args.download_missing:ocr_pdf.write_bytes(urllib.request.urlopen(urllib.request.Request(receipts[('district-of-lantzville','2025')]['sourceUrl'],headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read())
    manual=json.loads((AUDIT/'lantzville-2025-manual-transcription.json').read_text())
    peer_path=AUDIT.parent/'reviews/lantzville-2025-ocr.json';peer=json.loads(peer_path.read_text())
    assert manual['rows']==peer['rows'] and peer['status']=='pass-final-fields-controls-and-documentation'
    assert peer['sourceSha256']==manual['sourceSha256']==sha((args.cache/'district-of-lantzville-2025.pdf').read_bytes())
    ocr=(AUDIT/'lantzville-2025-fresh-ocr.txt').read_text();assert sha(ocr.encode())==peer['supportingFingerprints']['freshOcrTextSha256']
    for kind in ['employees','council']:
        cfg=dict(slug='district-of-lantzville',year='2025',kind=kind,pages=[4],mode='manual-image-transcription')
        assert '2025'not in baseline[cfg['slug']]['officialEmployeeYears'if kind=='employees'else'officialCouncilYears']
        rows=[[cfg['slug']]+r[1:]for r in manual['rows']if r[0]==kind]
        keys=['employeeUnder','employeeAll']if kind=='employees'else['councilNamed']
        control=[dict(scope={'employeeUnder':'under','employeeAll':'all','councilNamed':'named'}[key],printedValues=manual['controls'][key],physicalPdfPage=4,verification='Both full-image human transcriptions and fresh OCR; not native PDF-reader independence.')for key in keys]
        source=make_source(cfg,receipts[(cfg['slug'],'2025')],rows,control)
        source['notes'].append('Scanned salary page with embedded OCR. Every field was fully manually transcribed and independently compared with a second complete human image transcription; fresh Tesseract OCR supports the review. OCR I/l and Roman-numeral errors are adjudicated from the image, not inferred identities.')
        if kind=='council':source['publicWarning']='The named council rows and named subtotal agree at $93,290; the lower reconciliation prints $93,289. The $1 source discrepancy remains unresolved. Individual cells remain unchanged, including the published negative expense −$256.'
        source['validation'].update(independentReaders=['author complete rendered-image transcription','independent second complete rendered-image transcription'],secondHumanReview='research/salaries/municipal-history-pass/reviews/lantzville-2025-ocr.md',supportingOcr='Tesseract fresh300dpi psm6; embeddedOCR is not independent native text',bothFullImageTranscriptionsAgree=True,embeddedOcrNameMisread='Savage, lan → visually Savage, Ian')
        encoded=normalize_json(rows);compressed=pack(encoded);source.update(dataSha256=sha(compressed),normalizedSha256=sha(encoded));sources.append(source)
        evidence.append(dict(sourceId=source['id'],sourceSha256=manual['sourceSha256'],manual=manual,independentReview=peer,supportingFreshOcr=ocr,controls=control))
        if args.write:(OUT/source['file']).write_bytes(compressed)
        if args.verify:assert(OUT/source['file']).read_bytes()==compressed
    manifest=dict(version=1,rowSchema=['employerSlug','name','position','remuneration','expenses','pdfPage'],sources=sources)
    if args.write:
        (OUT/'sources.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n');(OUT/'extraction-evidence.json.gzip').write_bytes(pack(normalize_json(evidence)))
    if args.verify:assert json.loads((OUT/'sources.json').read_text())==manifest,'Manifest differs'


if __name__=='__main__':main()
