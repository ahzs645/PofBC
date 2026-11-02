"""Immutable personally read original source rows, independent of producer values."""
from pathlib import Path
import argparse,hashlib,json,sys
R=Path(__file__).resolve().parents[1];B=R/'research/salaries/gap-fill-2026-11-02/school_north/reviews/phsa-history'
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--key',required=True);ap.add_argument('--batch',type=int,required=True);ap.add_argument('--revision',default='v4');a=ap.parse_args();p=R/'research/salaries/gap-fill-2026-11-02/phsa_history/source-only-packets'/f'{a.key}-{a.revision}'/'packet.json';packet=json.loads(p.read_text());by={r['sequence']:r for r in packet['targets']};rows=[]
 for line in sys.stdin.read().strip().splitlines():
  seq,name,pay,expenses=line.split('|');seq=int(seq);target=by[seq];rows.append(dict(sequence=seq,name=name,remuneration=int(pay.replace(',','')),expenses=None if expenses=='-' else int(expenses.replace(',','')),literalExpense=expenses,position=None,physicalPage=target['physicalPage'],rowOnPage=target['rowOnPage'],sourceCropSha256=target['sourceCropSha256']))
 d=B/'producer-packet-first-readings';d.mkdir(exist_ok=True);dest=d/f'{a.key}-{a.revision}-batch{a.batch:03d}.json';assert not dest.exists();dest.write_text(json.dumps(dict(key=a.key,candidateValuesOpened=False,producerRawReadersOpened=False,sourceOnlyPacketSha256=hashlib.sha256(p.read_bytes()).hexdigest(),method='Personal original-pixel first reading of every listed full-row contact before candidate or raw OCR access; exact source reading, not a selected OCR answer.',rows=rows,noOutreach=True),indent=2,ensure_ascii=False)+'\n');print(len(rows),hashlib.sha256(dest.read_bytes()).hexdigest())
if __name__=='__main__':main()
