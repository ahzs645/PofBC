"""Print the first lines of each page of a statement's text, to find the statement of operations by
eye where find_operations_page.py does not. Usage: page_heads.py <pdf url> [max pages]"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from statement_text import pages_of  # noqa: E402

pages = pages_of(sys.argv[1])
for number, page in enumerate(pages[: int(sys.argv[2]) if len(sys.argv) > 2 else 14], 1):
    lines = [line.strip() for line in page.strip().split('\n') if line.strip()][:4]
    print(number, len(page), ' / '.join(lines)[:160])
