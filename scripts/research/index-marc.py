"""Index ISO2709 catalogue metadata; source discovery only, never accepted historical claims.
python scripts/research/index-marc.py ZIP OUTPUT_JSON
MARC-8 bytes are preserved as Latin-1 plus an explicit decoding warning, not guessed Unicode.
"""
import json,sys,zipfile,hashlib,re
from pathlib import Path
source='https://www.llbc.leg.bc.ca/public/pubdocs/bcdocsMARCBatchFiles/1990s_records/1995-1999.zip'
records=[];files=[]
with zipfile.ZipFile(sys.argv[1]) as archive:
 for name in sorted(archive.namelist()):
  data=archive.read(name);offset=0;count=0
  while offset<len(data):
   if not data[offset:].strip():break
   length=int(data[offset:offset+5]);record=data[offset:offset+length]
   if len(record)!=length or record[-1:]!=b'\x1d':raise ValueError(f'Invalid record: {name}@{offset}')
   base=int(record[12:17]);directory=record[24:base-1]
   if len(directory)%12:raise ValueError(f'Invalid directory: {name}@{offset}')
   fields={};encoding='utf-8' if record[9:10]==b'a' else 'latin-1'
   for p in range(0,len(directory),12):
    entry=directory[p:p+12];tag=entry[:3].decode('ascii');size=int(entry[3:7]);start=int(entry[7:12]);raw=record[base+start:base+start+size-1]
    if tag<'010':value=raw.decode(encoding)
    else:value=' '.join(part[1:].decode(encoding) for part in raw[2:].split(b'\x1f')[1:])
    fields.setdefault(tag,[]).append(value)
   metadata={tag:fields.get(tag,[]) for tag in ['001','008','110','245','260','264','610','710','856','901']}
   records.append({'archive_member':name,'record_index':count,'byte_offset':offset,'leader':record[:24].decode('ascii'),'metadata':metadata,'decoding':'UTF-8' if encoding=='utf-8' else 'MARC-8 not decoded; byte-preserving Latin-1 view','status':'candidate_source_unreviewed'})
   offset+=length;count+=1
  files.append({'name':name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),'records':count,'status':'indexed' if count else 'empty_source_member'})
result={'schema':'source-discovery/1','source_url':source,'archive_sha256':hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest(),'retrieved_on':'2026-09-30','files':files,'records':records,'warning':'Dates and printed corporate names describe publications/catalogue records, not founding or legal responsibility.'}
Path(sys.argv[2]).parent.mkdir(parents=True,exist_ok=True);Path(sys.argv[2]).write_text(json.dumps(result,indent=2)+'\n')
print(len(files),'archive members;',len(records),'catalogue records;',sum(not f['records'] for f in files),'empty members')
