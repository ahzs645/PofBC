"""Summarize each Budget's "Supplement to the Estimates" (BC Data Catalogue, Treasury Board Staff) to
one row per ministry, sub-vote and appropriation type for the Budget's first fiscal year.

Usage (from the repository root):

    python3 -I research/finance/scripts/summarize_supplement.py \
        research/finance/cache/supplement  research/finance/estimates

Each Budget's CSV is fetched into the cache directory if it is not there. The catalogue files carry
the chart-of-accounts segments: segment 03 level 1 is the ministry or special office, level 3 the
sub-vote, level 4 says whether it is a voted or a statutory appropriation; segment 04 level 2 is
operating expense or capital expenditure. Only operating expense for the first year is kept, because
that is what the Estimates vote and the Public Accounts compare. Amounts are whole dollars as
published; brackets are negative.

Writes supplement.csv: budget, fiscal_year, ministry_code, ministry, subvote_code, subvote,
appropriation (voted / statutory), amount, source_url.
"""

import csv
import io
import os
import re
import sys
import urllib.request
from collections import defaultdict

CSVS = {
    # Budget 2013 was re-tabled after the May 2013 election; the Estimates voted that year are the
    # June update's. Budget 2017 was also updated in September 2017, but no catalogue file of that
    # update's Supplement was found, so 2017-18 is checked against the February Budget and differs.
    2013: 'https://catalogue.data.gov.bc.ca/dataset/c37f2874-e9f2-4d3b-8679-c27ed8d1d979/resource/cc1062f9-6467-40e3-9ef1-e189bae50e8a/download/bcfinjune2013supplementestimates.csv',
    2014: 'https://catalogue.data.gov.bc.ca/dataset/6f616d57-b18f-4de9-a8bb-5ad68740909e/resource/04d91153-9441-4086-9b6f-bb274ff93e33/download/bcfin2014supplementestimates.csv',
    2015: 'https://catalogue.data.gov.bc.ca/dataset/a9e7e680-9e8a-4555-add3-4a8922823ec6/resource/dbe70107-03d2-4ce2-9171-72c14f14e498/download/bcfin2015supplementestimates.csv',
    2016: 'https://catalogue.data.gov.bc.ca/dataset/6cc9174a-259d-45d6-a7f5-9af0589f052e/resource/8298881b-3b36-4f2a-b04f-54f5606ce888/download/bcfin2016supplementestimates.csv',
    2017: 'https://catalogue.data.gov.bc.ca/dataset/91049159-0dc0-4480-9c73-8e61150d167d/resource/3b1668fc-976e-402f-aab0-801a9049c436/download/bcfin2017supplementestimates.csv',
    2018: 'https://catalogue.data.gov.bc.ca/dataset/2013c544-62e8-4485-ad4b-6e5ba5e373b9/resource/2db8ef59-7f61-4a13-a189-53be4729842b/download/bc_fin_2018_supplement_estimates.csv',
    2019: 'https://catalogue.data.gov.bc.ca/dataset/4cbb92ee-16ba-466b-87f0-643903053cb6/resource/fceddadd-da8d-41a4-819a-e30b4607f9e4/download/bc_fin_2019_supplement_estimates.csv',
    2020: 'https://catalogue.data.gov.bc.ca/dataset/3f26d4b1-ad22-4278-a553-e969a9c7ad26/resource/5b4d8393-635c-4060-8d71-550c61097c78/download/bc_fin_2020_supplement_estimates.csv',
    2021: 'https://catalogue.data.gov.bc.ca/dataset/a96153e2-21a5-4e70-8625-cca770f01fbd/resource/bc2ec14f-b445-47e9-9a86-cf0bd819c434/download/bc_fin_2021_supplement_estimates.csv',
    2022: 'https://catalogue.data.gov.bc.ca/dataset/1d57ea3c-1fa7-49f5-a203-eac188a385d4/resource/c142b196-8f43-45ef-b1db-03498eb12dcf/download/bc_fin_2022_supplement_estimates.csv',
    2023: 'https://catalogue.data.gov.bc.ca/dataset/2f40fb8f-a9e7-4f5b-94e9-04fbfaa10676/resource/d41c315a-9efb-4b86-a193-c06a9addeeff/download/bc_fin_2023_supplement-estimates.csv',
    2024: 'https://catalogue.data.gov.bc.ca/dataset/824d7d12-7fff-4ba6-83f7-24ce2fdab17a/resource/c33ec0f8-6506-4147-8f1b-adffff71b407/download/bc_fin_2024_supplement_estimates.csv',
    2025: 'https://catalogue.data.gov.bc.ca/dataset/aa46e2ad-042f-4044-b869-e2ab4b814609/resource/34a70c70-c711-42da-bdb7-8453aac23b42/download/bc_fin_2025_supplement_estimates.csv',
    2026: 'https://catalogue.data.gov.bc.ca/dataset/dd093de1-11eb-4d34-92e1-781de5222bd7/resource/2bd288c9-c9b0-4f74-b487-ef5e1f5e0310/download/bc_fin_2026_supplement_estimates.csv',
}


def text_of(path):
    raw = open(path, 'rb').read()
    try:
        return raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        return raw.decode('cp1252', errors='replace')


def amount(text):
    t = text.replace(',', '').replace('$', '').strip()
    if t in ('', '-'):
        return 0
    neg = t.startswith('(') or t.startswith('-')
    value = round(float(t.strip('()-')))
    return -value if neg else value


def split_code(text):
    m = re.match(r'^(\S+)\s+(.*)$', text.strip())
    return (m.group(1), m.group(2).strip()) if m else ('', text.strip())


def column(head, *patterns):
    for name in head:
        if all(re.search(p, name, re.I) for p in patterns):
            return name
    raise SystemExit(f'no column like {patterns} in {head}')


def main():
    cache, out_dir = sys.argv[1], sys.argv[2]
    os.makedirs(cache, exist_ok=True)
    out = []
    for budget, url in sorted(CSVS.items()):
        path = os.path.join(cache, f'budget-{budget}.csv')
        if not os.path.exists(path):
            urllib.request.urlretrieve(url, path)
        rows = list(csv.DictReader(io.StringIO(text_of(path))))
        head = list(rows[0].keys())
        year_col = column(head, r'year')
        kind_col = column(head, r'segment 04 l2')
        l1, l3, l4 = column(head, r'segment 03 l1'), column(head, r'segment 03 l3'), column(head, r'segment 03 l4')
        value_col = column(head, r'(net balance|amount|budget)')
        first = min(int(r[year_col]) for r in rows if r[year_col].strip().isdigit())
        sums = defaultdict(int)
        for r in rows:
            if not r[year_col].strip().isdigit() or int(r[year_col]) != first:
                continue
            if not re.match(r'^CB0+\b', r[kind_col].strip()):
                continue
            kind = 'voted' if re.search(r'voted', r[l4], re.I) else 'statutory' if re.search(r'statutory', r[l4], re.I) else r[l4].strip()
            sums[(split_code(r[l1]), split_code(r[l3]), kind)] += amount(r[value_col])
        for ((mc, mn), (sc, sn), kind), value in sorted(sums.items()):
            out.append({'budget': budget, 'fiscal_year': f'{first - 1}-{str(first)[2:]}', 'ministry_code': mc, 'ministry': mn,
                        'subvote_code': sc, 'subvote': sn, 'appropriation': kind, 'amount': value, 'source_url': url})
        voted = sum(v for (m, s, k), v in sums.items() if k == 'voted')
        print(f'Budget {budget} (FY ending {first}): {len(sums)} sub-votes, voted operating expense ${voted:,}', file=sys.stderr)
    with open(os.path.join(out_dir, 'supplement.csv'), 'w', newline='') as f:
        w = csv.DictWriter(f, list(out[0].keys()), lineterminator='\n')
        w.writeheader()
        w.writerows(out)


if __name__ == '__main__':
    main()
