"""Compare all169 terminal f32 values for 3..9 seats, batch32/7/1."""
import json
import sys
from pathlib import Path

MARKER = 'PREFLOP_MW_TERMINAL_BITS '
EXPECTED = {(n, batch) for n in range(3, 10) for batch in (32, 7, 1)}

def read(path):
    raw = Path(path).read_bytes()
    text = raw.decode('utf-16') if raw[:2] in (b'\xff\xfe', b'\xfe\xff') else raw.decode('utf-8-sig')
    rows = {}
    for line in text.splitlines():
        at = line.find(MARKER)
        if at < 0:
            continue
        row = json.loads(line[at + len(MARKER):])
        key = (row['seats'], row['batch'])
        assert key not in rows, f'{path}: duplicate case {key}'
        assert row['model'] == 'coupled_deck_v1', (path, key, row['model'])
        assert row['opponents'] == row['seats'] - 1, (path, key)
        assert len(row['bits_by_seat']) == row['seats'], (path, key)
        assert all(len(values) == 169 for values in row['bits_by_seat']), (path, key)
        assert all(isinstance(x, int) and 0 <= x < 2**32 for values in row['bits_by_seat'] for x in values), (path, key)
        rows[key] = row
    assert set(rows) == EXPECTED, f'{path}: missing {EXPECTED-set(rows)}, extra {set(rows)-EXPECTED}'
    return rows

if len(sys.argv) != 3:
    raise SystemExit('Usage: python compare_terminal_bits.py CONTROL.log CANDIDATE.log')
control, candidate = map(read, sys.argv[1:])
mismatches = []
checked = 0
for (n, batch), row in sorted(control.items()):
    other = candidate[n, batch]
    for p, (left, right) in enumerate(zip(row['bits_by_seat'], other['bits_by_seat'])):
        for h, (a, b) in enumerate(zip(left, right)):
            checked += 1
            if a != b and len(mismatches) < 20:
                mismatches.append({'seats': n, 'batch': batch, 'seat': p, 'hand': h,
                                   'control_bits': f'{a:08x}', 'candidate_bits': f'{b:08x}'})
print(json.dumps({'cases': len(EXPECTED), 'f32_values_checked': checked,
                  'exact': not mismatches, 'first_mismatches': mismatches}, indent=2))
raise SystemExit(1 if mismatches else 0)
