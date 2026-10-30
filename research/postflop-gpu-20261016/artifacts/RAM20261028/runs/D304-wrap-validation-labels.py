"""Keep long validation labels inside the research ledger's last column."""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
H = ROOT / 'runs/D304-tracker-display-metadata'
page = h.ar.DASHBOARD / 'index.html'
before = page.read_bytes()
assert before.count(b'\n') == before.count(b'\r\n')
anchor = b'  </style>'
rule = b'    #experiments td:last-child .badge{display:inline-block;max-width:100%;white-space:normal;overflow-wrap:anywhere}\r\n'
assert before.count(anchor) == 1 and rule not in before
after = before.replace(anchor, rule + anchor, 1)
assert after.replace(rule, b'', 1) == before
(H / 'index-before.html').write_bytes(before)
(H / 'index-after.html').write_bytes(after)
page.write_bytes(after)
h.save(H / 'layout-fix.json', {'at': h.now(), 'scope': 'One scoped CSS rule wraps long validation badges in research table; no solver/raw/status/quality/data changes.',
    'path': str(page), 'before_sha256': h.sha(H / 'index-before.html'), 'after_sha256': h.sha(page),
    'entire_preexisting_HTML_recovered_by_removing_one_rule': True,
    'reason': 'Actual browser screenshot showed long correctness descriptions in nowrap badges stretching the ledger beyond the viewport. Other badges retain existing style.',
    'browser_after_check_required': True})
h.custody()
print('One CSS rule applied; all preexisting HTML bytes preserved.', flush=True)
