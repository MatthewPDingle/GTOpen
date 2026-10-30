"""Check selector removal and every native rank-conditioned accumulator pair."""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D301-predicated-correction-native'

def parse(text):
    return {int(match[1], 16): match[2] for match in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*', text)}

def inspect(text, baseline):
    rows = parse(text)
    old = parse(baseline)
    def inventory(mapping):
        result = collections.Counter()
        for op in mapping.values():
            name = re.sub(r'^@!?U?P\d+ ', '', op).split()[0]
            if name in ['FADD', 'FSEL', 'FMUL', 'FFMA']:
                result[('predicated:' if op.startswith('@') else 'unpredicated:') + name] += 1
        return dict(result)
    before, after = inventory(old), inventory(rows)
    assert before['predicated:FSEL'] == 30
    assert not any('FSEL' in key for key in after)
    assert after['predicated:FADD'] == 60
    assert before['unpredicated:FMUL'] == after['unpredicated:FMUL'] == 1
    assert before['unpredicated:FFMA'] == after['unpredicated:FFMA'] == 2
    barriers = [op for op in rows.values() if op.startswith('BAR.')]
    assert len(barriers) == 5 and barriers == [op for op in old.values() if op.startswith('BAR.')]
    versions = collections.defaultdict(lambda: -1)
    predicates = {}
    groups = collections.defaultdict(list)
    witnesses = []
    for pc, original_op in rows.items():
        op = re.sub(r'\.reuse\b', '', original_op)
        compare = re.fullmatch(r'ISETP.GE.U32.AND (P\d+), PT, (R\d+), (R\d+), (PT|P\d+)', op)
        if compare:
            destination, pos, bound, parent = compare.groups()
            source = True if parent == 'PT' else predicates.get(parent)
            predicates[destination] = (pos + '@' + hex(versions[pos]), bound, source, pc)
        add = re.fullmatch(r'@(!?)(P\d+) FADD (R\d+), (R\d+), (R\d+)', op)
        if add:
            negated, predicate, destination, one, two = add.groups()
            assert (one == destination) != (two == destination)
            reach = two if one == destination else one
            condition = predicates.get(predicate)
            assert condition is not None
            pos, bound, parent, compare_pc = condition
            if negated:
                assert bound == 'R26' and parent is True
                role = 'lower'
            else:
                assert bound == 'R8' and isinstance(parent, tuple)
                assert parent[0] == pos and parent[1] == 'R26' and parent[2] is True
                role = 'higher'
            key = (pos, reach + '@' + hex(versions[reach]))
            groups[key].append(role)
            witnesses.append({'PC': hex(pc), 'instruction': original_op, 'role': role,
                              'position_value_version': pos, 'reach_value_version': key[1],
                              'predicate_compare_PC': hex(compare_pc), 'accumulator': destination})
        # Track register writes so a later reused register name is not confused
        # with the earlier position or reach value stored in a predicate.
        plain = re.sub(r'^@!?U?P\d+ ', '', op)
        write = re.match(r'(?!ST|BRA|BAR|BSSY|BSYNC)\S+ (R\d+)(?:,|\.)', plain)
        if write:
            versions[write[1]] = pc
    assert len(witnesses) == 60 and len(groups) == 30
    assert all(sorted(roles) == ['higher', 'lower'] for roles in groups.values())
    assert sum(row['role'] == 'lower' for row in witnesses) == 30
    assert sum(row['role'] == 'higher' for row in witnesses) == 30
    return {'baseline_static_inventory': before, 'candidate_static_inventory': after,
            'all30_native_conditional_pairs': witnesses,
            'same_position_and_reach_value_version_in_each_pair': True,
            'bounds': {'lower': 'R26', 'upper': 'R8'},
            'predicates': 'lower=!GE(pos,lb); higher=GE(pos,ub)&GE(pos,lb); original if/else priority',
            'original5barriers': barriers,
            'limits': 'Fixed-driver static instruction and linear-current-definition/value-version witness, not a complete native CFG/pointer/IEEE interpreter. R26/R8 roles agree with D300 parameter-bound PTX; their full native address ancestry is not re-proved here. No dynamic lane frequency/instruction throughput/counter/speed attribution. Full raw original GPU and engine/canonical/broad/material/speed gates remain mandatory.'}

if len(sys.argv) == 1:
    h.custody()
    capture = h.read(H / 'capture-report.json')
    files = [Path(__file__), H / 'protocol.json', H / 'capture-report.json', ROOT / 'runs/D300-predicated-correction-PTX/report.json']
    files += [Path(capture['entry_sections'][arm]['up_show']['path']) for arm in ['baseline', 'candidate']]
    h.save(H / 'reader-protocol-v2.json', {'at': h.now(), 'status': 'FROZEN_PRE_NATIVE_CORRECTION_READER',
        'input_sha256': {str(path): h.sha(path) for path in files},
        'requirements': 'Original30nativepredicatedFSEL->0;60predicatedFADD mapto30lower/higherpairs sharingposition/reachvalueversions with exactunsignedelsepriority. Original5barriers/fullpayoutmul/2FMA inventory. Negative wrongpriority/operand/selector/barrier fixtures. No new module/compiler/applicationkernel/solver/speed.'})
    print(h.sha(H / 'reader-protocol-v2.json'), flush=True)
    sys.exit(0)

assert len(sys.argv) == 2
h.pin(H / 'reader-protocol-v2.json', sys.argv[1])
P = h.read(H / 'reader-protocol-v2.json')
h.custody()
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
capture = h.read(H / 'capture-report.json')
text = Path(capture['entry_sections']['candidate']['up_show']['path']).read_text()
baseline = Path(capture['entry_sections']['baseline']['up_show']['path']).read_text()
witness = inspect(text, baseline)
negative = []
first = witness['all30_native_conditional_pairs'][0]
load = first['instruction']
changed = load.replace('R37', 'R36', 1)
assert load != changed
cases = [
    ('wrong_reach_word', re.sub(r'(/\*1ea0\*/\s*)' + re.escape(load), lambda match: match[1] + changed, text, count=1)),
    ('wrong_else_bound', text.replace('R31, R8, P2', 'R31, R26, P2', 1)),
    ('unexpected_selector', text.replace(load, load.replace('FADD', 'FSEL'), 1)),
    ('missing_barrier', text.replace('BAR.SYNC.DEFER_BLOCKING', 'NOP', 1))
]
for label, bad in cases:
    assert bad != text
    try:
        inspect(bad, baseline)
    except AssertionError:
        negative.append(label)
    else:
        raise AssertionError('negative fixture accepted: ' + label)
h.save(H / 'report.json', {'id': 'D301', 'at': h.now(),
    'status': 'pass_scoped_native_selector_removal_and_all30_original_priority_pairs',
    'protocol_sha256': sys.argv[1], 'witness': witness, 'negative_reader_fixtures': negative,
    'all_owned_capture_disassembly_children_terminal': True,
    'new_application_kernel_solver_or_speed_samples': 0, 'candidate_adopted': False})
h.custody()
print('D301 selector removal andall30nativecorrectionpairs passed.', flush=True)
