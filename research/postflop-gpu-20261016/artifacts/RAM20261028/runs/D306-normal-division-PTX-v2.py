"""All RN-FTZ guards with local CFG and identical clamp-expression aliases."""
import bisect, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D306-normal-division-PTX'
R = ROOT / 'runs/E124-resource'

def inspect(text):
    items = [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith('//')]
    labels = {line[:-1]: index for index, line in enumerate(items) if re.fullmatch(r'\$L[\w$]+:', line)}
    writes = {}
    for index, line in enumerate(items):
        match = re.match(r'\S+\s+(%f\d+),', line)
        if match:
            writes.setdefault(match[1], []).append(index)
    def canonical(operand, at, depth=0):
        assert depth < 12
        if operand.startswith('0f'):
            return ('literal', operand)
        positions = writes.get(operand, [])
        which = bisect.bisect_left(positions, at) - 1
        definition = positions[which] if which >= 0 else -1
        if definition >= 0:
            line = items[definition]
            clamp = re.fullmatch(r'max\.f32\s+%f\d+,\s*(%f\d+),\s*(0f00000000);', line)
            if clamp:
                return ('max.f32', canonical(clamp[1], definition, depth + 1), ('literal', clamp[2]))
            move = re.fullmatch(r'mov\.f32\s+%f\d+,\s*(%f\d+|0f[0-9A-F]+);', line)
            if move:
                return canonical(move[1], definition, depth + 1)
        return ('opaque_register_value', operand, definition)
    definitions, branches = {}, []
    for index, line in enumerate(items):
        leaf = re.fullmatch(r'setp\.(le|ge|gtu|ltu)\.f32\s+(%p\d+),\s*(%f\d+),\s*(%f\d+|0f[0-9A-F]+);', line)
        if leaf:
            op, pred, one, two = leaf.groups()
            definitions[pred] = ('leaf', op, canonical(one, index), canonical(two, index))
        boolean = re.fullmatch(r'(and|or)\.pred\s+(%p\d+),\s*(%p\d+),\s*(%p\d+);', line)
        if boolean:
            op, dest, one, two = boolean.groups()
            definitions[dest] = (op, definitions.get(one), definitions.get(two))
        branch = re.fullmatch(r'@(%p\d+) bra\s+(\S+);', line)
        if branch and branch[1] in definitions:
            branches.append((index, branch[2], definitions[branch[1]]))
    def leaves(expr, boolean):
        assert expr is not None
        if expr[0] == 'leaf':
            return [expr[1:]]
        assert expr[0] == boolean
        return leaves(expr[1], boolean) + leaves(expr[2], boolean)
    def division(index):
        match = re.fullmatch(r'div\.rn(\.ftz)?\.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);', items[index])
        assert match
        return bool(match[1]), match[2], canonical(match[3], index), canonical(match[4], index)
    def walk_to_division(start):
        visited = set()
        index = start
        for _ in range(12):
            assert index not in visited and 0 <= index < len(items)
            visited.add(index)
            line = items[index]
            if line.startswith('div.'):
                return index
            jump = re.fullmatch(r'bra\.uni\s+(\S+);', line)
            if jump:
                index = labels[jump[1]]
                continue
            assert line.endswith(':') or re.match(r'(?:max|mov)\.f32\b', line), line
            index += 1
        raise AssertionError('local path exceeds fixed12instruction bound')
    def joins_after(index):
        result, visited = [], set()
        index += 1
        for _ in range(12):
            if index in visited or index >= len(items):
                break
            visited.add(index)
            line = items[index]
            if line in [label + ':' for label in labels]:
                result.append(line[:-1])
                index += 1
                continue
            jump = re.fullmatch(r'bra\.uni\s+(\S+);', line)
            if jump:
                index = labels[jump[1]]
                continue
            # Stop on the first following computation; do not conflate an
            # unrelated later program join with this division's immediate join.
            break
        return result
    witnesses = []
    for index, line in enumerate(items):
        if 'div.rn.ftz.f32' not in line:
            continue
        ftz, dest, n, d = division(index)
        assert ftz
        expected_good = [('ge', n, ('literal', '0f20000000')), ('le', d, ('literal', '0f5F000000')), ('le', n, d)]
        expected_bad = [('ltu', n, ('literal', '0f20000000')), ('gtu', d, ('literal', '0f5F000000')), ('gtu', n, d)]
        matches = []
        for branch_index, target, expr in branches:
            if not 0 < index - branch_index <= 40:
                continue
            for form, boolean, expected in [('ordered_good_guard', 'and', expected_good), ('unordered_bad_guard_fallback', 'or', expected_bad)]:
                try:
                    atoms = leaves(expr, boolean)
                    if sorted(atoms, key=repr) != sorted(expected, key=repr):
                        continue
                    taken = walk_to_division(labels[target])
                    not_taken = walk_to_division(branch_index + 1)
                    fast, slow = (taken, not_taken) if boolean == 'and' else (not_taken, taken)
                    assert fast == index
                    sf, sd, sn, sden = division(slow)
                    assert not sf and (sd, sn, sden) == (dest, n, d)
                    common = set(joins_after(fast)) & set(joins_after(slow))
                    assert common
                    matches.append({'guard_form': form, 'branch_item': branch_index, 'fallback_division_item': slow,
                                    'guard_atoms': atoms, 'immediate_shared_join': sorted(common)})
                except (AssertionError, KeyError):
                    continue
        assert len(matches) == 1, (index, line, len(matches))
        witnesses.append({'item_index': index, 'instruction': line, 'destination': dest, 'numerator_expression': n,
                          'denominator_expression': d, **matches[0]})
    assert witnesses and len(witnesses) == text.count('div.rn.ftz.f32')
    assert text.count('.ftz.') == len(witnesses)
    assert not re.search(r'\b(?:div|rcp)\.approx', text)
    return witnesses

if len(sys.argv) == 1:
    h.custody()
    files = [Path(__file__), H / 'protocol.json', H / 'reader-v1-failure.json', ROOT / 'runs/D306-normal-division-PTX.py',
             R / 'protocol.json', R / 'report.json', ROOT / 'runs/E124-source/manifest.json', ROOT / 'runs/D305-normal-division-scout/range-contract.json']
    files += [R / 'execution' / ('candidate-' + arch + '-' + name + '.ptx.txt') for arch in ['compute_120', 'compute_75'] for name in ['down_action', 'up_action']]
    h.save(H / 'protocol-v2.json', {'at': h.now(), 'status': 'FROZEN_PRE_ADDITIVE_LOCAL_CFG_GUARD_READER',
        'input_sha256': {str(path): h.sha(path) for path in files},
        'repair': 'Original120sections passed;75 uses explicit fallback branch and duplicated identical max.f32 clamps. V2 tracks only identical max/mov expression aliases and fixed local control paths, retains every FTZsite/4sections/operands/guard/bounds/fallback/join and4negativefixtures. Original script/protocol/error retained; source/compiler/module/GPU unchanged, no repeats.',
        'limits': 'Local40instruction guard window,12step path/join walk,max/mov alias only; no fullCFG/address/FP interpreter. Unknown structure fails closed, no sites omitted.'})
    print(h.sha(H / 'protocol-v2.json'), flush=True)
    sys.exit(0)
assert len(sys.argv) == 2
h.pin(H / 'protocol-v2.json', sys.argv[1])
P = h.read(H / 'protocol-v2.json')
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
h.custody()
sections = {}
for arch in ['compute_120', 'compute_75']:
    for name in ['down_action', 'up_action']:
        path = R / 'execution' / ('candidate-' + arch + '-' + name + '.ptx.txt')
        sections[arch + ':' + name] = inspect(path.read_text(encoding='utf-8'))
text = (R / 'execution/candidate-compute_120-down_action.ptx.txt').read_text(encoding='utf-8')
first = sections['compute_120:down_action'][0]['instruction']
parts = re.fullmatch(r'div.rn.ftz.f32\s+(%f\d+),\s*(%f\d+),\s*(%f\d+);', first)
mutations = [
    ('wrong_denominator', text.replace(first, first.replace(', ' + parts[3] + ';', ', ' + parts[2] + ';'), 1)),
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
    'protocol_sha256': sys.argv[1], 'site_counts': {key: len(value) for key, value in sections.items()}, 'all_sites': sections,
    'negative_fixtures_rejected': rejected, 'new_compiler_GPU_module_kernel_solver_or_speed_samples': 0,
    'limits': P['limits'] + ' No original completeclamp/sum/globalFP-DAG/pointer ancestry/native/IEEE-output or speed claim; full raw controls stillmandatory.'})
h.custody()
print(json.dumps({'status': 'pass', 'site_counts': {key: len(value) for key, value in sections.items()}, 'negative_fixtures': rejected}), flush=True)
