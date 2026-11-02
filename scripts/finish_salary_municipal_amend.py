#!/usr/bin/env python3
"""Preserve first-pass files and add the source-confirmed Blaschuk correction."""
import copy
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AREA = ROOT/'research/salaries/queue-completion-2026-11-01/municipal'
COLLECTION = ROOT/'research/salaries/queue-completion-municipal'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        assert path.read_bytes() == data, str(path)
    else:
        path.write_bytes(data)


def run():
    old = COLLECTION/'mission-2023-employee-remuneration.json.gzip'
    assert sha(old) == '24ac7b07cf0c1f7e3e391dffb52d0de98c66b129a758ae1fb180dfa613ba504b'
    rows = json.loads(gzip.decompress(old.read_bytes()))
    assert rows[10] == ['city-of-mission','Blaschuk, S','Building Inspector 2',93274,1718,6]
    corrected = copy.deepcopy(rows)
    corrected[10][3] = 93271
    assert sum(r[3] for r in corrected) == 16445762
    assert sum(r[4] or 0 for r in corrected) == 318887
    out = COLLECTION/'mission-2023-employee-remuneration-v2.json.gzip'
    freeze(out, gzip.compress(json.dumps(corrected,ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
    crop = Path('/tmp/queue-completion-municipal/mission-2023-blaschuk-author-actual1200.png')
    assert sha(crop) == '8ee1a633a90586c90b4d4a0498c6bbae033033defdc3a25688c235b169b35f0a'
    pinned = AREA/'source-review/mission-2023-blaschuk-pay-actual1200.png'
    freeze(pinned,crop.read_bytes())
    original = AREA/'mission-2023-original-review.json.gzip'
    assert sha(original) == '5ffbfb2cf61dd1ece941c3407a14d42e95d899d9cf32b84be72832a5ef390201'
    amendment = {
        'date':'2026-11-01', 'sourceKey':'mission-2023', 'sourceSha256':'82e0ab886a7e8a1e464e3afa25127be7176de79881b93b7602c5a101c8f4d6ac',
        'priorFrozenPayload':{'path':str(old.relative_to(ROOT)),'sha256':sha(old)},
        'priorFrozenOriginalReview':{'path':str(original.relative_to(ROOT)),'sha256':sha(original)},
        'candidate':{'path':str(out.relative_to(ROOT)),'sha256':sha(out),'rows':148},
        'corrections':[{'sectionIndex':1,'sectionRow':11,'name':'Blaschuk, S','physicalPage':6,'field':'remuneration','firstPass':93274,'finalLiteral':93271,'reason':'Independent image-first peer transcribed93,271. Author independently rerendered the original physical6 cell at1200dpi and confirms the final glyph1. Both OCR engines read4; the first author source review missed that shared error. No balancing or outside-name inference.'}],
        'actualOriginalReviewCrop':{'path':str(pinned.relative_to(ROOT)),'sha256':sha(pinned),'render':'PyMuPDF page.get_pixmap(dpi=1200,clip=Rect(360,363.6,432,376.8),alpha=False), original physical6; actual PDF-painted source','boxIn300DpiCoordinates':[1500,1515,1800,1570]},
        'unchangedFieldsExceptOnePayCell':True,
        'literalControlDiscrepancies':{
            'namedEmployeeRows':{'remuneration':16445762,'expenses':318887},
            'printedNamedEmployees':{'remuneration':16445765,'expenses':318887},
            'namedRowSumMinusPrinted':{'remuneration':-3,'expenses':0},
            'page6EmployeeRows':{'remuneration':4050146,'expenses':97830,'printedTotalColumnSum':4147979},
            'printedPage6EmployeeSubtotal':{'remuneration':4050149,'expenses':97830,'total':4147979},
            'specificRow':{'literalRemuneration':93271,'literalExpenses':1718,'sum':94989,'printedExpenseInclusiveTotal':94992,'printedTotalMinusLiteralPayAndExpenses':3}
        },
        'firstPassFilesRemainImmutable':True,'unrelatedRowsChanged':False,'noBalancing':True
    }
    receipt=AREA/'mission-2023-post-peer-source-amendment.json'
    freeze(receipt,(json.dumps(amendment,ensure_ascii=False,indent=2)+'\n').encode())
    context=json.loads((AREA/'mission-2023-context-review.json').read_text())
    context['supersedesContextForAcceptance']='research/salaries/queue-completion-2026-11-01/municipal/mission-2023-context-review.json'
    context['allNamedAndPageControlsAgreeExactlyAfterCompleteSourceRowReview']=False
    context['originalImageAmendment']={'path':str(receipt.relative_to(ROOT)),'sha256':sha(receipt)}
    context['literalControlDiscrepancies']=amendment['literalControlDiscrepancies']
    context['publicWarning']='The148 named employee rows total CAD16,445,762 remuneration and318,887 known expenses. The printed named-employee remuneration subtotal is16,445,765,3 higher; its expense subtotal agrees. Physical6 employee rows total4,050,146 remuneration versus printed page subtotal4,050,149, also3 higher. Blaschuk, S visibly prints93,271 remuneration and1,718 expenses (sum94,989), while its separate printed expense-inclusive Total is94,992,3 higher. Every individual cell is retained as visibly printed; no cause is inferred and no amount is balanced.'
    contextout=AREA/'mission-2023-context-review-v2.json'
    freeze(contextout,(json.dumps(context,ensure_ascii=False,indent=2)+'\n').encode())
    print(json.dumps({'candidate':str(out.relative_to(ROOT)),'sha256':sha(out),'amendment':str(receipt.relative_to(ROOT)),'amendmentSha256':sha(receipt)},indent=2))


if __name__=='__main__':
    run()
