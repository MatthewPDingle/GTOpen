"""Scoped guard/operand/fallback witness for every RN-FTZ PTX site."""
import collections, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D306-normal-division-PTX'
R = ROOT / 'runs/E124-resource'

def inspect(text):
    items = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('//')]
    definitions = {}
    snapshots = {}
    for index, line in enumerate(items):
        match = re.fullmatch(r'setp\.(le|ge|gtu|ltu)\.f32\s+(%p\d+),\s*(%f\d+),\s*(%f\d+|0f[0-9A-F]+);', line)
        if match:
            op, pred, one, two = match.groups()
            definitions[pred] = ('leaf', op, one, two)
        match = re.fullmatch(r'(and|or)\.pred\s+(%p\d+),\s*(%p\d+),\s*(%p\d+);', line)
        if match:
            op, dest, one, two = match.groups()
            assert one in definitions and two in definitions
            definitions[dest] = (op, definitions[one], definitions[two])
        if re.fullmatch(r'@%p\d+ bra\s+\S+;', line):
            pred = line.split()[0][1:]
            if pred in definitions:
                snapshots[index] = definitions[pred]
    def leafset(expr, boolean):
        if expr[0] == 'leaf':
            return [expr[1:]]
        assert expr[0] == boolean
        return leafset(expr[1], boolean) + leafset(expr[2], boolean)
    def division(line, ftz):
        op = 'div.rn.ftz.f32' if ftz else 'div.rn.f32'
        match = re.fullmatch(re.escape(op) + r'\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);', line)
        assert match, line
        return match.groups()
    witnesses = []
    for index, line in enumerate(items):
        if 'div.rn.ftz.f32' not in line:
            continue
        dest, numerator, denominator = division(line, True)
        if items[index - 1].endswith(':'):
            # Ordered positive guard jumps over original fallback to FTZ.
            fast = items[index - 1][:-1]
            branch_index = index - 4
            branch = re.fullmatch(r'@(%p\d+) bra\s+(\S+);', items[branch_index])
            assert branch and branch[2] == fast
            assert division(items[index - 3], False) == (dest, numerator, denominator)
            join = re.fullmatch(r'bra\.uni\s+(\S+);', items[index - 2])
            assert join and items[index + 1] == join[1] + ':'
            atoms = sorted(leafset(snapshots[branch_index], 'and'))
            assert atoms == sorted([('le', denominator, '0f5F000000'), ('ge', numerator, '0f20000000'), ('le', numerator, denominator)])
            form = 'ordered_good_guard'
        else:
            # Unordered bad tests branch to original fallback; FTZ fallthrough.
            branch_index = index - 1
            branch = re.fullmatch(r'@(%p\d+) bra\s+(\S+);', items[branch_index])
            assert branch
            join = re.fullmatch(r'bra\.uni\s+(\S+);', items[index + 1])
            assert join and items[index + 2] == branch[2] + ':'
            assert division(items[index + 3], False) == (dest, numerator, denominator)
            assert items[index + 4] == join[1] + ':'
            atoms = sorted(leafset(snapshots[branch_index], 'or'))
            assert atoms == sorted([('gtu', denominator, '0f5F000000'), ('ltu', numerator, '0f20000000'), ('gtu', numerator, denominator)])
            form = 'unordered_bad_guard_fallback'
        witnesses.append({'item_index': index, 'instruction': line, 'destination': dest, 'numerator': numerator,
                          'denominator': denominator, 'guard_form': form, 'guard_atoms': atoms,
                          'same_original_division_fallback_operands_and_join': True})
    assert witnesses
    assert len(witnesses) == text.count('div.rn.ftz.f32')
    assert text.count('.ftz.') == len(witnesses)
    assert not re.search(r'\b(?:div|rcp)\.approx', text)
    return witnesses

if len(sys.argv) == 1:
    h.custody()
    assert all(h.read(R / 'report.json')['gates'].values())
    H.mkdir(exist_ok=False)
    files = [Path(__file__), R / 'protocol.json', R / 'report.json', ROOT / 'runs/E124-source/manifest.json', ROOT / 'runs/D305-normal-division-scout/range-contract.json']
    files += [R / 'execution' / ('candidate-' + arch + '-' + name + '.ptx.txt') for arch in ['compute_120', 'compute_75'] for name in ['down_action', 'up_action']]
    h.save(H / 'protocol.json', {'at': h.now(), 'status': 'FROZEN_PRE_GUARD_PTX_READER', 'input_sha256': {str(path): h.sha(path) for path in files},
        'requirements': 'Every RNFTZsite in4targetsections mustcarry exactpositiveordered conjunction or unorderedbad-disjunction bounds2^-63/2^63/n<=d, correct branch direction and originalRNfallback with identicaln/d/destination andjoin. No otherFTZ/approxprimitive.4negativefixtures. This is a bounded guard/operand parser, not completeFP/CFG/address/IEEEsimulator or speed proof.'})
    print(h.sha(H / 'protocol.json'), flush=True)
    sys.exit(0)
assert len(sys.argv) == 2
h.pin(H / 'protocol.json', sys.argv[1])
P = h.read(H / 'protocol.json')
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
h.custody()
sections = {}
for arch in ['compute_120', 'compute_75']:
    for name in ['down_action', 'up_action']:
        path = R / 'execution' / ('candidate-' + arch + '-' + name + '.ptx.txt')
        sections[arch + ':' + name] = inspect(path.read_text(encoding='utf-8'))
text = (R / 'execution/candidate-compute_120-down_action.ptx.txt').read_text(encoding='utf-8')
first = sections['compute_120:down_action'][0]
instruction = first['instruction']
mutations = [
    ('wrong_denominator', text.replace(instruction, instruction.replace(', ' + first['denominator'] + ';', ', ' + first['numerator'] + ';'), 1)),
    ('weaken_numerator_bound', text.replace('0f20000000', '0f1FFFFFFE', 1)),
    ('invert_branch', re.sub(r'(@)(%p\d+ bra\s+\S+;)(\s*// begin inline asm\s*div\.rn\.ftz\.f32)', r'\1!\2\3', text, count=1)),
    ('wrong_fallback_rounding', text.replace('div.rn.f32', 'div.rz.f32', 1))
]
rejected = []
for label, bad in mutations:
    assert bad != text
    try:
        inspect(bad)
    except (AssertionError, KeyError):
        rejected.append(label)
    else:
        raise AssertionError('Negative fixture accepted: ' + label)
h.save(H / 'report.json', {'id': 'D306', 'at': h.now(), 'status': 'pass_scoped_all_RNFTZ_guard_operands_fallback_and_join',
    'protocol_sha256': sys.argv[1], 'site_counts': {key: len(value) for key, value in sections.items()},
    'all_sites': sections, 'negative_fixtures_rejected': rejected, 'new_compiler_GPU_module_kernel_solver_or_speed_samples': 0,
    'limits': 'Scopeexactguard/fallback/typedoperand/joins only; original fullclamp/sum/address/globalFP-DAG andnative/lifecycle/actualIEEE-output controls remain. No universal interpreter, dynamic branch frequency, native shorterpath or speed claim.'})
h.custody()
print(json.dumps({'status': 'pass', 'site_counts': {key: len(value) for key, value in sections.items()}, 'negative_fixtures': rejected}), flush=True)
