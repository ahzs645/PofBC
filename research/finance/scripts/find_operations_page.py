"""Print the PDF page number of the statement of operations in a statement's text, for
transcribe_statement.py: the first page that names the statement and carries a revenue heading
and figures. Usage: python3 -I research/finance/scripts/find_operations_page.py <pdf url>"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statement_text import pages_of  # noqa: E402

pages = pages_of(sys.argv[1])
for number, page in enumerate(pages, 1):
    head = '\n'.join(page.strip().split('\n')[:8])
    if re.search(r'statements? of (operations|revenue and expense|changes in net assets)|statement of comprehensive', head, re.I) \
            and re.search(r'^\s*revenues?\b', page, re.I | re.M) and len(re.findall(r'\d{1,3}(?:,\d{3})+', page)) > 8:
        print(number)
        break
else:
    print(0)
