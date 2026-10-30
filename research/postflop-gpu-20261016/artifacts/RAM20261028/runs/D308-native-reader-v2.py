"""Account every primitive FP instruction and its output dependencies."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D308-packed-arithmetic'

def inspect(text):
    rows = [(int(match[1], 16), re.sub(r'\.reuse\b', '', match[2])) for match in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*', text)]
    end = next(i for i, (_, op) in enumerate(rows) if op == 'EXIT')
    live = rows[:end + 1]
    assert not any('CALL' in op or 'BRA' in op for _, op in live)
    floating = [(i, pc, op) for i, (pc, op) in enumerate(live) if re.sub(r'^@!?P\d+ ', '', op).startswith('F')]
    assert len(floating) == 4
    adds, fmas = [], []
    for index, pc, op in floating:
        add = re.fullmatch(r'FADD (R\d+), (-?R\d+), (-?R\d+)', op)
        fma = re.fullmatch(r'FFMA (R\d+), (R\d+), (R\d+), (R\d+)', op)
        assert bool(add) != bool(fma), op
        if add:
            dest, a, b = add.groups()
            assert a.startswith('-') != b.startswith('-')
            adds.append({'index': index, 'PC': hex(pc), 'instruction': op, 'dest': dest,
                         'common_subtrahend': a[1:] if a.startswith('-') else b[1:]})
        else:
            dest, a, b, c = fma.groups()
            fmas.append({'index': index, 'PC': hex(pc), 'instruction': op, 'dest': dest,
                         'multiplicands': [a, b], 'delta': c})
    assert len(adds) == len(fmas) == 2
    assert adds[0]['common_subtrahend'] == adds[1]['common_subtrahend']
    assert {a['dest'] for a in adds} == {f['delta'] for f in fmas}
    assert all(next(a['index'] for a in adds if a['dest'] == f['delta']) < f['index'] for f in fmas)
    stores = []
    for index, (pc, op) in enumerate(live):
        match = re.fullmatch(r'STG.E desc\[UR\d+\]\[(R\d+)\.64(?:\+0x([0-9a-f]+))?\], (R\d+)', op)
        if match:
            base, offset, source = match.groups()
            stores.append({'index': index, 'PC': hex(pc), 'instruction': op, 'base': base,
                           'offset': int(offset or '0', 16), 'source': source})
    assert len(stores) == 2 and stores[0]['base'] == stores[1]['base']
    assert [store['offset'] for store in stores] == [0, 4]
    assert [store['source'] for store in stores] == [fma['dest'] for fma in fmas]
    assert all(store['index'] > fma['index'] for store, fma in zip(stores, fmas))
    return {'straightline_valid_thread_instruction_sites': len(live), 'FP_arithmetic_sites': 4,
            'two_scalar_subtractions': adds, 'two_scalar_FMAs': fmas, 'two_scalar_output_stores': stores,
            'no_packed_arithmetic_opcode_or_outofline_call': True}

if len(sys.argv) == 1:
    h.custody()
    cap = h.read(H / 'capture-report.json')
    files = [Path(__file__), H / 'reader-protocol.json', H / 'reader-preflight-v1.json', ROOT / 'runs/D308-native-reader.py', H / 'protocol.json', H / 'source-contract.json', H / 'resource-report.json', H / 'capture-report.json']
    files += [Path(value['path']) for value in cap['sections'].values()]
    h.save(H / 'reader-protocol-v2.json', {'at': h.now(), 'status': 'FROZEN_PRE_NATIVE_PRIMITIVE_SCALARIZATION_READER',
        'input_sha256': {str(path): h.sha(path) for path in files},
        'requirements': 'Bothprimitivefullvalid-thread paths contain exactly2plainFADD withnegatedcommonsubtrahend,2plainFFMA consumingbothdistinctdeltas,2scalarstores atsamebase+0/+4, no otherFPoperation/branch/call. AllnativeFPsites accounted. Ifboth4sites, requiredfewerissuedarithmetic gatefails.4negativefixtures. Localstructuralworkproof only,notfullparameter/address/IEEE/NaN/equivalence/dynamiclatencyinterpreter.'})
    print(h.sha(H / 'reader-protocol-v2.json'), flush=True)
    sys.exit(0)
assert len(sys.argv) == 2
h.pin(H / 'reader-protocol-v2.json', sys.argv[1])
P = h.read(H / 'reader-protocol-v2.json')
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
h.custody()
capture = h.read(H / 'capture-report.json')
result = {name: inspect(Path(value['path']).read_text(encoding='utf-8')) for name, value in capture['sections'].items()}
text = Path(capture['sections']['packed_regret_pair']['path']).read_text(encoding='utf-8')
text = re.sub(r'\.reuse\b', '', text)
first = result['packed_regret_pair']
fma = first['two_scalar_FMAs'][1]
mutations = [
    ('missing_FMA', text.replace(first['two_scalar_FMAs'][0]['instruction'], first['two_scalar_FMAs'][0]['instruction'].replace('FFMA', 'FMUL'), 1)),
    ('different_FTZ_operation', text.replace(first['two_scalar_subtractions'][0]['instruction'], first['two_scalar_subtractions'][0]['instruction'].replace('FADD', 'FADD.FTZ'), 1)),
    ('wrong_second_output_offset', text.replace(first['two_scalar_output_stores'][1]['instruction'], first['two_scalar_output_stores'][1]['instruction'].replace('+0x4]', '+0x8]'), 1)),
    ('cross_component_delta', text.replace(fma['instruction'], fma['instruction'].replace(', ' + fma['delta'], ', ' + first['two_scalar_FMAs'][0]['delta']), 1))
]
rejected = []
for name, bad in mutations:
    assert bad != text
    try:
        inspect(bad)
    except AssertionError:
        rejected.append(name)
    else:
        raise AssertionError('Negative fixture accepted: ' + name)
h.save(H / 'native-report.json', {'id': 'D308-native', 'at': h.now(), 'status': 'decline_fixed_packed_form_scalarized_to_original4_FP_sites',
    'reader_protocol_sha256': sys.argv[1], 'witnesses': result, 'negative_reader_fixtures_rejected': rejected,
    'decision': 'PackedvirtualSUB/FMA bothlower to2scalarFADD+2scalarFFMA ontestedRTX5090/driver610.88. Requiredfewer-than4nativeFPsites/componentpair notestablished; closebefore anysolverprototype/numerical/speedtrial.',
    'native_subtraction_operand_order': 'Reference and packedlowering differ in ordering of negatedout/value operands. This structuralreader doesnotassertIEEE/NaNpayload equivalence; no actualnumericaltests executed.',
    'applicationkernels_numerical_solver_or_speed_samples': 0, 'solver_candidate_admitted': False,
    'limits': P['requirements'] + ' No claim about allGPUs/drivers/layouts, actual throughput, numericalaccuracy orcompletecycles.'})
h.custody()
print(json.dumps({'status': 'closed_scalarized', 'arithmetic_sites': {name: value['FP_arithmetic_sites'] for name, value in result.items()}, 'negative_fixtures': rejected}), flush=True)
