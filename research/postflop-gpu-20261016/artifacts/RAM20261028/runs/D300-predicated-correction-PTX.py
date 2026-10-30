"""Bound original reach words and rank predicates to all explicit additions."""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D300-predicated-correction-PTX'
R = ROOT / 'runs/E122-resource'

def definitions(text):
    out = collections.defaultdict(list)
    for line in text.splitlines():
        match = re.match(r'^\s*(?:@!?[%\w]+\s+)?([a-z][\w.]*)\s+([^;]+);\s*$', line)
        if not match:
            continue
        op = match[1]
        args = [word.strip() for word in match[2].split(',')]
        if not op.startswith(('st.', 'bar.', 'bra')) and re.fullmatch(r'%[rf]\w*\d+', args[0]):
            out[args[0]].append((op, args[1:]))
    return out

def ancestry(reg, defs, seen=None):
    seen = set() if seen is None else seen
    if reg in seen:
        return set()
    seen.add(reg)
    out = set()
    for op, args in defs.get(reg, []):
        if op.startswith('ld.param.'):
            for word in args:
                match = re.search(r'up_show_param_(\d+)', word)
                if match:
                    out.add(int(match[1]))
        else:
            for word in args:
                for parent in re.findall(r'%[rf]\w*\d+', word):
                    out |= ancestry(parent, defs, seen)
    return out

def inspect(text, baseline):
    defs = definitions(text)
    blocks = list(re.finditer(r'\{\s*\.reg \.pred p_lo, p_hi, p_not_lo;.*?\}', text, re.S))
    assert len(blocks) == 30
    assert 'selp.f32' not in text and '.ftz' not in text
    bars = re.findall(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;', text)
    assert len(bars) == 5 and bars == re.findall(r'\bbar\.(?:sync|red)(?:\.[\w]+)*[^;]*;', baseline)
    rows = []
    pattern = (r'\{\s*\.reg \.pred p_lo, p_hi, p_not_lo;\s*'
               r'setp\.lt\.u32 p_lo,\s*(%r\d+),\s*(%r\d+);\s*'
               r'setp\.ge\.u32 p_hi,\s*\1,\s*(%r\d+);\s*'
               r'not\.pred p_not_lo, p_lo;\s*and\.pred p_hi, p_hi, p_not_lo;\s*'
               r'@p_lo add\.rn\.f32\s+(%f\d+),\s*\4,\s*(%f\d+);\s*'
               r'@p_hi add\.rn\.f32\s+(%f\d+),\s*\6,\s*\5;\s*\}')
    for block in blocks:
        match = re.fullmatch(pattern, block[0])
        assert match, block[0]
        pos, lower, upper, lo_acc, reach, hi_acc = match.groups()
        assert lo_acc != hi_acc
        assert ancestry(lower, defs) & {12, 13} == {12}
        assert ancestry(upper, defs) & {12, 13} == {13}
        reach_loads = [(op, args) for op, args in defs[reach] if op == 'ld.shared.f32']
        assert len(reach_loads) == 1
        address = reach_loads[0][1][0].strip('[]')
        address_defs = [args for op, args in defs[address] if op == 'add.s64']
        products = []
        for operands in address_defs:
            for operand in operands:
                products += [args for op, args in defs[operand] if op == 'mul.wide.u32' and args == [pos, '4']]
        assert products
        assert any(op == 'ld.shared.u32' for op, args in defs[pos])
        rows.append({'position': pos, 'lower_bound': lower, 'upper_bound': upper,
                     'lower_accumulator': lo_acc, 'higher_accumulator': hi_acc,
                     'same_original_reach_word': reach, 'reach_address': address, 'PTX': block[0]})
    return {'all30_rank_correction_sites': rows, 'lower_bound_param': 12, 'upper_bound_param': 13,
            'original_position_to_same_reach_word_addressing': True, 'readwrite_self_adds': True,
            'priority': 'lower iff pos<lb; higher iff pos>=ub AND NOT pos<lb, including malformed bound ordering',
            'all5barriers_unchanged': bars, 'unconditional_total_and_all_prefix_payout_source_unchanged': True,
            'limits': 'Bounded actual PTX operand/rank-address/predicate witness plus source inverse/Boolean contract; not a full PTX memory/FP interpreter. Readwrite chain/caller integration, native JIT form, full raw original controls and full qualification remain required.'}

if len(sys.argv) == 1:
    h.custody()
    H.mkdir(exist_ok=False)
    assert all(h.read(R / 'report.json')['gates'].values())
    files = [Path(__file__), ROOT / 'epoch/common.py', R / 'protocol.json', R / 'report.json',
             ROOT / 'runs/E122-source/manifest.json', ROOT / 'runs/D299-predicated-correction-scout/predicate-contract.json']
    files += [R / 'execution' / (arm + '-compute_120-up_show.ptx.txt') for arm in ['baseline', 'candidate']]
    h.save(H / 'protocol.json', {'id': 'D300', 'at': h.now(), 'status': 'FROZEN_PRE_EMITTED_PTX_READER',
        'input_sha256': {str(path): h.sha(path) for path in files},
        'requirements': 'All30explicitasm sites: original sharedcardposition ->samef32reachword, lower/upper sourceparam12/13, originalself-add accumulators, exactunsigned if/elsepriority withANDnotlower; noFTZ/selp.f32, original5barriers. Wrongcomparison/priority/operand/precision/barrier negativefixtures. No compiler/module/applicationkernel/solver/speed.'})
    print(h.sha(H / 'protocol.json'), flush=True)
    sys.exit(0)

assert len(sys.argv) == 2
h.pin(H / 'protocol.json', sys.argv[1])
P = h.read(H / 'protocol.json')
h.custody()
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
text = (R / 'execution/candidate-compute_120-up_show.ptx.txt').read_text()
baseline = (R / 'execution/baseline-compute_120-up_show.ptx.txt').read_text()
witness = inspect(text, baseline)
first = witness['all30_rank_correction_sites'][0]['PTX']
negative = []
for label, bad_block in [
    ('wrong_lower_comparison', first.replace('setp.lt.u32', 'setp.le.u32', 1)),
    ('wrong_else_priority', first.replace('and.pred p_hi, p_hi, p_not_lo', 'and.pred p_hi, p_hi, p_lo', 1)),
    ('wrong_reach_operand', first.replace(witness['all30_rank_correction_sites'][0]['same_original_reach_word'], '%f999999', 1)),
    ('wrong_precision', first.replace('add.rn.f32', 'add.rz.f32', 1))
]:
    bad = text.replace(first, bad_block, 1)
    assert bad != text
    try:
        inspect(bad, baseline)
    except AssertionError:
        negative.append(label)
    else:
        raise AssertionError('negative fixture accepted: ' + label)
bad = text.replace('bar.sync', 'bar.arrive', 1)
try:
    inspect(bad, baseline)
except AssertionError:
    negative.append('missing_original_barrier')
else:
    raise AssertionError('negative barrier fixture accepted')
h.save(H / 'report.json', {'id': 'D300', 'at': h.now(),
    'status': 'pass_scoped_predicated_correction_PTX_original_words_priority_and_barriers',
    'protocol_sha256': sys.argv[1], 'witness': witness, 'negative_reader_fixtures': negative,
    'new_compiler_GPU_kernel_solver_or_speed_samples': 0, 'candidate_adopted': False})
h.custody()
print('D300 all30word/predicate/self-add sites and5negativefixtures passed.', flush=True)
