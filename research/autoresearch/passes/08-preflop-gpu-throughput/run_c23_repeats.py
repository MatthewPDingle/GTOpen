"""Registered C23 retention pairs, after the successful first large screen.

Large pair 2 is already complete (control then candidate). Alternate order for
pairs 3 and 4. Small pairs 1-3 start control/candidate and alternate. Preserve
every output and yield to user work through the existing per-process guard.
"""
import json
import sys
from run_c23 import HERE, RAW, read, run, compare, run07


def main():
    assert read(RAW/'c23-first-pair-verified.json')['admitted']
    fixture = sys.argv[1]
    schedule = {'large': [(3, ['candidate', 'control']), (4, ['control', 'candidate'])],
                'small': [(1, ['control', 'candidate']), (2, ['candidate', 'control']), (3, ['control', 'candidate'])]}[fixture]
    for pair, roles in schedule:
        values = {}
        for role in roles:
            run07.idle()
            values[role] = run(fixture, role, pair=pair)
        ratio = compare(values['control'], values['candidate'])
        print(json.dumps({'fixture': fixture, 'pair': pair, 'ratio': ratio, 'exact': True}), flush=True)


if __name__ == '__main__':
    main()
