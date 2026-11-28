"""Fetch a financial statement PDF, keep its text page by page, and print the page(s) that hold the
statement of operations, so its lines can be transcribed and checked by hand.

Usage (from the repository root; needs poppler's pdftotext):

    python3 -I research/finance/scripts/statement_text.py <pdf url> [<search phrase>]

The PDF is fetched into research/finance/cache/statements/, turned into text with
`pdftotext -layout` (one form feed per page), and then deleted to save disk: the text keeps every
page, and the URL is in research/finance/statements/index.csv. Pages are counted from 1, from the
first page of the file, as a PDF viewer counts them.

With --draft <year column> it also prints a draft CSV of the page's lines: each label and the figure
in the given numeric column (1 for the first figure on the line). A draft is not a transcription:
every line is checked against the page and categorized by hand.
"""

import os
import re
import subprocess
import sys

CACHE = os.path.join('research', 'finance', 'cache', 'statements')
NUMBER = re.compile(r'^\(\$?\d[\d,]*\)$|^-?\$?\d[\d,]*$|^-$|^—$')


def text_path(url):
    return os.path.join(CACHE, re.sub(r'[^A-Za-z0-9._-]+', '_', url.split('//', 1)[-1]) + '.txt')


def pages_of(url):
    path = text_path(url)
    if not os.path.exists(path):
        os.makedirs(CACHE, exist_ok=True)
        pdf = path[:-4] + '.pdf'
        # curl, with a time limit: a stalled download fails rather than hangs.
        try:
            subprocess.run(['curl', '-sSfL', '--max-time', '90', '-A', 'Mozilla/5.0 (research script)', '-o', pdf, url], check=True)
        except subprocess.CalledProcessError:
            if os.path.exists(pdf):
                os.remove(pdf)
            raise
        subprocess.run(['pdftotext', '-layout', pdf, path], check=True)
        os.remove(pdf)
    return open(path, encoding='utf-8', errors='replace').read().split('\f')


def figures(line):
    words = line.split()
    out = []
    while words and NUMBER.match(words[-1].replace('$', '')):
        out.insert(0, words.pop())
    return ' '.join(words), out


def amount(text):
    t = text.replace('$', '').replace(',', '').strip()
    if t in ('-', '—', ''):
        return 0
    neg = t.startswith('(') or t.startswith('-')
    value = int(t.strip('()-'))
    return -value if neg else value


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    url = args[0]
    phrase = args[1] if len(args) > 1 else r'statements? of operations'
    pages = pages_of(url)
    draft = None
    if '--draft' in sys.argv:
        draft = int(sys.argv[sys.argv.index('--draft') + 1])
    show = [int(p) for p in sys.argv[sys.argv.index('--page') + 1].split(',')] if '--page' in sys.argv else None
    hits = show or [i + 1 for i, page in enumerate(pages) if re.search(phrase, page, re.I) and len(re.findall(r'\d{1,3}(?:,\d{3})+', page)) > 8]
    print(f'{len(pages)} pages; showing {hits}')
    for number in hits[:3]:
        page = pages[number - 1]
        print(f'===== PDF page {number} =====')
        print(page)
        if draft:
            print('----- draft -----')
            for line in page.split('\n'):
                label, nums = figures(line)
                if len(nums) >= draft and label:
                    print(f'"{label}",{amount(nums[draft - 1])}')


if __name__ == '__main__':
    main()
