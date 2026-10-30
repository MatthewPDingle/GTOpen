"""Local native division-core witnesses; reject absent intended work removal."""
import collections, json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D307-normal-division-native'

def parse(text):
    return [(int(m[1], 16), re.sub(r'\.reuse\b', '', m[2])) for m in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*', text)]

def calls(rows, ftz):
    name = 'div_rn_ftz_f32_slowpath' if ftz else 'div_rn_noftz_f32_slowpath'
    return [i for i, (_, op) in enumerate(rows) if 'CALL' in op and name in op]

def core(rows, call):
    checks = [(i, re.fullmatch(r'FCHK (P\d+), (R\d+), (R\d+)', rows[i][1])) for i in range(max(0, call - 30), call)]
    checks = [(i, m) for i, m in checks if m]
    assert checks
    check, match = checks[-1]
    pred, n, d = match.groups()
    reciprocal = [(i, re.fullmatch(r'MUFU.RCP (R\d+), ' + d, rows[i][1])) for i in range(max(0, check - 30), check + 1)]
    reciprocal = [(i, m) for i, m in reciprocal if m]
    assert reciprocal
    start, rcp = reciprocal[-1]
    n_value, d_value = ('N', 'D') if n != d else ('ND', 'ND')
    values = {n: n_value, d: d_value, rcp[1]: 'Y'}
    def arg(token):
        if token.startswith('-'):
            value = arg(token[1:])
            return ('neg', value) if value is not None else None
        if token in ['RZ', '0', '0x0']:
            return 'zero'
        if token in ['1', '1.0', '0x3f800000']:
            return 'one'
        return values.get(token)
    def fma(a, b, c):
        # Canonicalized product order witnesses work/dependencies only. This is
        # not an IEEE/NaN payload equivalence claim about commuting operands.
        return ('FMA', tuple(sorted([a, b], key=repr)), c)
    e = fma(('neg', d_value), 'Y', 'one')
    y = fma('Y', e, 'Y')
    q = fma(n_value, y, 'zero')
    residual = fma(('neg', d_value), q, n_value)
    rounded = fma(y, residual, q)
    expected = [e, y, q, residual, rounded]
    events = []
    guard = None
    for index in range(start + 1, call):
        pc, op = rows[index]
        arithmetic = re.fullmatch(r'FFMA (R\d+), ([^,]+), ([^,]+), ([^,]+)', op)
        if arithmetic:
            dest, one, two, three = arithmetic.groups()
            operands = [arg(word) for word in [one, two, three]]
            if all(value is not None for value in operands):
                expression = fma(*operands)
                values[dest] = expression
                if expression in expected:
                    events.append({'stage': expected.index(expression), 'PC': hex(pc), 'instruction': op})
            else:
                values.pop(dest, None)
            continue
        move = re.fullmatch(r'MOV (R\d+), (\S+)', op)
        if move:
            value = arg(move[2])
            if value is None:
                values.pop(move[1], None)
            else:
                values[move[1]] = value
            continue
        if re.fullmatch(r'@!' + pred + r' BRA .+', op):
            guard = index
        write = re.match(r'(?!ST|BRA|BAR|BSSY|BSYNC|FCHK|CALL)\S+ (R\d+)(?:,|\.)', op)
        if write:
            values.pop(write[1], None)
    assert [event['stage'] for event in events] == [0, 1, 2, 3, 4]
    assert guard is not None and rows[guard][0] > int(events[-1]['PC'], 16)
    assert not any('BRA' in op for _, op in rows[start + 1:guard])
    relevant = collections.Counter()
    for _, op in rows[start:call + 1]:
        opcode = re.sub(r'^@!?P\d+ ', '', op).split()[0]
        if opcode in ['MUFU.RCP', 'FCHK', 'FFMA', 'CALL.REL.NOINC']:
            relevant[opcode] += 1
    return {'RCP_PC': hex(rows[start][0]), 'FCHK_PC': hex(rows[check][0]), 'FCHK_guard_PC': hex(rows[guard][0]),
            'slow_CALL_PC': hex(rows[call][0]), 'slow_CALL': rows[call][1], 'numerator_register': n,
            'denominator_register': d, 'five_original_division_refinement_stages': events, 'local_opcode_inventory': dict(relevant)}

if len(sys.argv) == 1:
    h.custody()
    cap = h.read(H / 'capture-report.json')
    files = [Path(__file__), H / 'protocol.json', H / 'capture-report.json', ROOT / 'runs/D306-normal-division-PTX/report.json', ROOT / 'runs/E124-resource/protocol.json']
    files += [Path(cap['entry_sections'][arm][name]['path']) for arm in ['baseline', 'candidate'] for name in ['down_action', 'up_action']]
    h.save(H / 'reader-protocol.json', {'at': h.now(), 'status': 'FROZEN_PRE_LOCAL_NATIVE_DIVISION_WORK_READER',
        'input_sha256': {str(path): h.sha(path) for path in files},
        'requirements': 'All28candidateRNFTZsites mustbeaccounted via16down/12up slowCALLs, eachlocalRCP/FCHK/5FMAdependencychain andconditionalexceptionalbranch. Comparefirstoriginalcommon normalization reference pertarget. Ifeverycandidate retains original1RCP/5divisionFMA/FCHK/CALL, E124required positive ordinary-work-removal mechanism is not established; close before numerical trials. Preserveallbaseline callwindowinventories as scopedcontext,notglobaldynamiccounts. Fourreadernegativefixtures. NotcompleteCFG/ABI/register-liveness/IEEEsimulator or speed/no-speed proof.'})
    print(h.sha(H / 'reader-protocol.json'), flush=True)
    sys.exit(0)
assert len(sys.argv) == 2
h.pin(H / 'reader-protocol.json', sys.argv[1])
P = h.read(H / 'reader-protocol.json')
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
h.custody()
cap = h.read(H / 'capture-report.json')
counts = h.read(ROOT / 'runs/D306-normal-division-PTX/report.json')['site_counts']
result = {}
for name in ['down_action', 'up_action']:
    original = parse(Path(cap['entry_sections']['baseline'][name]['path']).read_text(encoding='utf-8'))
    candidate = parse(Path(cap['entry_sections']['candidate'][name]['path']).read_text(encoding='utf-8'))
    selected = calls(candidate, True)
    assert len(selected) == counts['compute_120:' + name]
    candidate_witnesses = [core(candidate, index) for index in selected]
    reference = core(original, calls(original, False)[0])
    required = {'MUFU.RCP': 1, 'FCHK': 1, 'FFMA': 5, 'CALL.REL.NOINC': 1}
    assert reference['local_opcode_inventory'] == required
    assert all(row['local_opcode_inventory'] == required for row in candidate_witnesses)
    result[name] = {'original_first_common_normalization_reference': reference,
                    'candidate_all_FTZ_site_witnesses': candidate_witnesses}
sample = parse(Path(cap['entry_sections']['candidate']['down_action']['path']).read_text(encoding='utf-8'))
call = calls(sample, True)[0]
witness = core(sample, call)
mutations = []
for label, pc, before, after in [
    ('missing_FCHK', int(witness['FCHK_PC'], 16), 'FCHK', 'NOP'),
    ('missing_refinement_FMA', int(witness['five_original_division_refinement_stages'][0]['PC'], 16), 'FFMA', 'FADD'),
    ('wrong_RCP_denominator', int(witness['RCP_PC'], 16), ', ' + witness['denominator_register'], ', RZ'),
    ('wrong_refinement_constant', int(witness['five_original_division_refinement_stages'][0]['PC'], 16), ', 1', ', RZ')
]:
    bad = list(sample)
    at = next(index for index, row in enumerate(bad) if row[0] == pc)
    assert before in bad[at][1]
    bad[at] = (pc, bad[at][1].replace(before, after, 1))
    try:
        core(bad, call)
    except AssertionError:
        mutations.append(label)
    else:
        raise AssertionError('negative fixture accepted: ' + label)
h.save(H / 'report.json', {'id': 'D307', 'at': h.now(), 'status': 'rejected_closed_required_native_work_removal_not_established',
    'protocol_sha256': sys.argv[1], 'witnesses': result, 'all_candidate_RNFTZ_sites_accounted': 28,
    'candidate_ordinary_primitive_work_removed': False, 'negative_reader_fixtures_rejected': mutations,
    'decision_basis': 'Eachguardedpositive division retains1RCP/5refinementFMA/FCHK/conditional slowCALL justas originalcommon reference. Added bounds/predicate branches do not establish the predeclared removal of ordinary divisionwork. Close fixedform before GPU application/numerical/speed tests; this is an admission-evidence failure, not a measured regression or universal no-speedup proof.',
    'new_compiler_GPU_module_applicationkernel_solver_or_speed_samples': 0,
    'limits': P['requirements'], 'candidate_adopted': False})
h.custody()
print(json.dumps({'status': 'E124 native mechanism gate not established', 'all_FTZ_sites': 28, 'core_per_site': required, 'negative_fixtures': mutations}), flush=True)
