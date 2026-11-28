"""Reading the Province's "CRF Detailed Schedules of Payments – Government Transfers" files.

The catalogue dataset (https://catalogue.data.gov.bc.ca/dataset/903c41c4-09c7-4af9-a43c-af3b6ff5c705,
Open Government Licence – British Columbia) holds one CSV per fiscal year, FYE 2007 to FYE 2026: the
payee, the paying ministry and the amount of every transfer of $25,000 or more from the Consolidated
Revenue Fund. The files differ in small ways: title lines before the header, header spellings
("Name", "NAME", "Reported Supplier Name"), amounts as text with commas and stray spaces, and two
encodings (UTF-8, with or without a byte-order mark, and Windows-1252).

Thousands of payees are individuals (foster and care providers, for example). Nothing here writes a
payee that is not matched to a site body: the raw files stay in the cache, which is not committed.
"""

import csv
import io
import os
import re
import urllib.request

DATASET = 'https://catalogue.data.gov.bc.ca/dataset/903c41c4-09c7-4af9-a43c-af3b6ff5c705'
FILES = {
    2007: 'resource/41f78459-4eda-49fd-8690-42f1dbfc6796/download/fye-07-government-transfers.csv',
    2008: 'resource/37a145ec-b94d-4288-ad3a-ab03e346a685/download/fye-08-government-transfers.csv',
    2009: 'resource/1c05a4f8-9fc7-4c55-8896-631bafee8033/download/fye-09-government-transfers.csv',
    2010: 'resource/2f8e671c-980e-42c9-ba03-cc997301003a/download/fye-10-government-transfers.csv',
    2011: 'resource/aa13c4ef-b0c5-4086-bd98-7af48ee89a79/download/fye-11-government-transfers.csv',
    2012: 'resource/44693861-3914-413b-abf7-afd27c847d82/download/fye-12-government-transfers.csv',
    2013: 'resource/44a9ac16-1213-46ad-9ca9-b3658d0bf49b/download/fye-13-government-transfers.csv',
    2014: 'resource/28a20b90-b1ee-462d-9b05-a47517ade8fb/download/fye-14-government-transfers.csv',
    2015: 'resource/4d02ccc0-f64f-45f7-9e2f-eb2be4723ada/download/fye-15-government-transfers.csv',
    2016: 'resource/d5cf9b3a-8eeb-4ee4-94e2-2742d00f137e/download/fye-16-government-transfers.csv',
    2017: 'resource/219a718d-0e68-44ea-aec5-690975a78d50/download/fye17-govt-transfers.csv',
    2018: 'resource/7a8132e0-26ae-4caa-bcd1-09cac45a128b/download/fye18-govt-transfers.csv',
    2019: 'resource/86fd4751-788c-4417-9fd7-b76893d35b72/download/fye19-govt-transfers.csv',
    2020: 'resource/debb18e3-3b99-4ad7-b0c2-fa5d2e968a41/download/fye20-govt-transfers.csv',
    2021: 'resource/aef706f0-1cfa-45b1-ac22-4dd262619690/download/fye21-govt-transfers.csv',
    2022: 'resource/69ed1057-fb1b-4bcc-ab21-d1b6953aff67/download/fye22-gov-transfers.csv',
    2023: 'resource/356b01e0-9972-4760-82d9-689c85d71e51/download/fye23-gov-transfers.csv',
    2024: 'resource/ad965b50-5f87-4442-b753-d45d33656917/download/fye24-govt-transfer.csv',
    2025: 'resource/bb8595a9-6a6f-4265-821e-30b36d60b628/download/fye25-govt-transfers.csv',
    2026: 'resource/c5eecccf-3f4f-4144-8d8d-de3a51e65a54/download/fye26-govt-transfers.csv',
}


def url_of(fye):
    return f'{DATASET}/{FILES[fye]}'


def fetch(cache, fye):
    path = os.path.join(cache, os.path.basename(FILES[fye]))
    if not os.path.exists(path):
        os.makedirs(cache, exist_ok=True)
        urllib.request.urlretrieve(url_of(fye), path)
    return path


def text_of(path):
    raw = open(path, 'rb').read()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252', errors='replace')


def amount(text):
    """Whole dollars from "1,234 ", " 1,234.00", "(1,234)"; a lone dash is nil; None when blank."""
    t = text.replace(',', '').replace('$', '').strip()
    if t == '-':
        return 0
    if not t:
        return None
    neg = t.startswith('(') or t.startswith('-')
    value = round(float(t.strip('()-').strip()))
    return -value if neg else value


def rows_of(cache, fye):
    """Every payment row of a year's file: (payee as printed, ministry as printed, whole dollars)."""
    rows = list(csv.reader(io.StringIO(text_of(fetch(cache, fye)))))
    start = next(i for i, row in enumerate(rows) if row and re.fullmatch(r'(name|reported supplier name)', row[0].strip(), re.I))
    out = []
    for row in rows[start + 1:]:
        if len(row) < 3 or not row[0].strip():
            continue
        value = amount(row[2])
        if value is None:
            continue
        out.append((re.sub(r'\s+', ' ', row[0]).strip(), re.sub(r'\s+', ' ', row[1]).strip(), value))
    return out


def payee_key(name):
    """A payee spelling reduced to its words, so "B.C." and "BC", "&" and "AND" meet."""
    t = name.upper().replace('’', "'").replace('`', "'")
    t = re.sub(r"[.'\"]", '', t)
    t = t.replace('&', ' AND ')
    t = re.sub(r'\bBRITISH COLUMBIA\b', 'BC', t)
    t = re.sub(r'\bB C\b', 'BC', t)
    t = re.sub(r'[^A-Z0-9]+', ' ', t)
    t = re.sub(r'^THE |\sTHE$', '', t.strip())  # "CANADIAN BLOOD SERVICES, THE"
    return re.sub(r'\s+', ' ', t).strip()
