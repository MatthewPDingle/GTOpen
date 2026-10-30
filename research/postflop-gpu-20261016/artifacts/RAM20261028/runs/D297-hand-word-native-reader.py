"""Bounded fixed-driver instruction witness for the private terminal word."""
import collections
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D297-hand-word-native'

def parse(text):
    return {int(m[1], 16): m[2] for m in re.finditer(r'/\*([0-9a-f]+)\*/\s*(.*?)\s*;\s*/\*', text)}

def argument_reads(rows):
    out = []
    for pc, op in rows.items():
        if 'c[0x0]' not in op:
            continue
        match = re.fullmatch(r'LDCU?(?:\.(64|128))? \w+, c\[0x0\]\[0x([0-9a-f]+)\]', op)
        assert match, ('unsupported constant-read spelling', pc, op)
        width = int(match[1] or '32') // 8
        out.append((pc, int(match[2], 16), width, op))
    return out

def inspect(name, text, baseline):
    r = parse(text)
    old = parse(baseline)
    deprecated = [0x3d0, 0x3d8] if name == 'up_fold' else [0x418, 0x420]
    reads = argument_reads(r)
    old_reads = argument_reads(old)
    for offset in deprecated:
        assert any(start <= offset < start + size for pc, start, size, op in old_reads)
        assert not any(start < offset + 8 and offset < start + size for pc, start, size, op in reads)
    math = lambda rows: dict(collections.Counter(op.split()[0] for op in rows.values() if op.startswith(('FADD', 'FMUL', 'FFMA'))))
    assert math(r) == math(old)
    bars = [op for op in r.values() if op.startswith('BAR.')]
    assert bars == [op for op in old.values() if op.startswith('BAR.')]
    if name == 'up_fold':
        required = {
            0x1470: 'LDC.64 R2, c[0x0][0x3f0]',
            0x1520: 'IMAD.WIDE R8, R0, 0x4, R2',
            0x1530: 'LDG.E.CONSTANT R8, desc[UR6][R8.64]',
            0x1560: 'SHF.R.U32.HI R13, RZ, 0xc, R8.reuse',
            0x1570: 'IMAD.SHL.U32 R10, R8, 0x4, RZ',
            0x1580: 'SHF.R.U32.HI R11, RZ, 0x4, R8',
            0x15a0: 'ISETP.NE.AND P0, PT, R13, 0x7ff, PT',
            0x15b0: 'LOP3.LUT R17, R10, 0xfc, RZ, 0xc0, !PT',
            0x15c0: 'LOP3.LUT R16, R11, 0xfc, RZ, 0xc0, !PT',
            0x15e0: 'LDS R14, [R17+UR11]',
            0x1610: 'LDS R15, [R16+UR11]',
            0x1630: '@P0 LEA R13, R13, UR4, 0x2',
            0x1640: '@P0 LDS R12, [R13]',
        }
    else:
        required = {
            0x1ac0: 'LDCU.64 UR4, c[0x0][0x410]',
            0x1b30: 'LEA R24, P0, R12, UR4, 0x2',
            0x1b40: 'LEA.HI.X R25, R12, UR5, RZ, 0x2, P0',
            0x1b50: 'LDG.E.CONSTANT R11, desc[UR12][R24.64]',
            0x1bb0: 'IMAD.SHL.U32 R6, R11, 0x4, RZ',
            0x1bc0: 'LOP3.LUT R6, R6, 0xfc, RZ, 0xc0, !PT',
            0x1bd0: 'IADD.64 R6, R2, R6',
            0x2a00: 'SHF.R.U32.HI R6, RZ, 0x4, R11',
            0x2a20: 'LOP3.LUT R6, R6, 0xfc, RZ, 0xc0, !PT',
            0x2a30: 'IADD.64 R6, R2, R6',
            0x3730: 'SHF.R.U32.HI R9, RZ, 0xc, R11',
            0x3780: 'ISETP.NE.AND P0, PT, R9, 0x7ff, PT',
            0x37f0: 'MOV R6, RZ',
            0x3800: '@P0 IMAD R9, R9, 0x4, R10',
            0x3820: '@P0 LDS R6, [R9]',
        }
        assert not any(re.match(r'(?:@!?\w+ )?\S+ R11(?:,|\.)', op) for pc, op in r.items() if 0x1b50 < pc < 0x3730)
    for pc, op in required.items():
        assert r[pc] == op
    return {
        'required_native_operand_chain': [{'PC': hex(pc), 'op': op} for pc, op in required.items()],
        'all_constant_read_ranges': [{'PC': hex(pc), 'start': hex(start), 'bytes': size, 'op': op} for pc, start, size, op in reads],
        'legacy_card_pointer_ranges_absent': [hex(x) for x in deprecated],
        'FP_opcode_inventory_unchanged': math(r), 'static_barriers_unchanged': bars,
        'same_sentinel': 2047, 'same_shift': 12, 'card_byte_shifts': [2, 4], 'card_byte_mask': 252,
        'limits': 'Fixed-driver local CB0 argument-slot/load/decode/compare/consumer witness. CB0 slots agree with unchanged typed PTX ABI and baseline; not a universal ABI/pointer interpreter. Native FP opcode counts are inventory only; D296 ordered PTX topology, complete host-address domain, future raw GPU/engine/canonical/broad qualification remain required. No counters, dynamic load counts, speed, or adoption claim.'
    }

if len(sys.argv) == 1:
    h.custody()
    capture = h.read(H / 'capture-report.json')
    files = [Path(__file__), H / 'protocol.json', H / 'capture-report.json', ROOT / 'runs/D296-hand-word-PTX/report.json']
    files += [Path(row['path']) for arm in capture['entry_sections'].values() for row in arm.values()]
    h.save(H / 'reader-protocol.json', {
        'at': h.now(), 'status': 'FROZEN_PRE_NATIVE_TERMINAL_WORD_READER',
        'input_sha256': {str(p): h.sha(p) for p in files},
        'requirements': 'Both entry word-pointer/load/cardbytefields/index12/sentinel2047/selected original consumers. Legacy card argument ranges absent from every parsed constant read including128-bit overlapping ranges. Native floating-op/barrier inventory unchanged. Negative sentinel/cardmask/word-load/pointer-range fixtures. Full raw GPU and original-value metadata decode remain mandatory.'
    })
    print(h.sha(H / 'reader-protocol.json'), flush=True)
    sys.exit(0)

assert len(sys.argv) == 2
h.pin(H / 'reader-protocol.json', sys.argv[1])
P = h.read(H / 'reader-protocol.json')
h.custody()
for path, digest in P['input_sha256'].items():
    h.pin(path, digest)
capture = h.read(H / 'capture-report.json')
witnesses = {}
negative = []
for name in ['up_fold', 'up_show']:
    text = Path(capture['entry_sections']['candidate'][name]['path']).read_text()
    baseline = Path(capture['entry_sections']['baseline'][name]['path']).read_text()
    witness = inspect(name, text, baseline)
    witnesses[name] = witness
    mutations = [('wrong_sentinel', text.replace('0x7ff, PT', '0x7fe, PT', 1)),
                 ('wrong_card_mask', text.replace('0xfc, RZ', '0xf8, RZ', 1))]
    old = 'LDG.E.CONSTANT R8, desc[UR6][R8.64]' if name == 'up_fold' else 'LDG.E.CONSTANT R11, desc[UR12][R24.64]'
    mutations.append(('wrong_word_load', text.replace(old, old.replace('R8,', 'R9,') if name == 'up_fold' else old.replace('R11,', 'R10,'), 1)))
    old = 'c[0x0][0x3f0]' if name == 'up_fold' else 'c[0x0][0x410]'
    new = 'c[0x0][0x3d0]' if name == 'up_fold' else 'c[0x0][0x418]'
    mutations.append(('legacy_card_pointer_read', text.replace(old, new, 1)))
    for label, bad in mutations:
        assert bad != text
        try:
            inspect(name, bad, baseline)
        except AssertionError:
            negative.append(name + ':' + label)
        else:
            raise AssertionError('negative fixture accepted: ' + label)

h.save(H / 'report.json', {
    'id': 'D297', 'at': h.now(), 'status': 'pass_scoped_two_terminal_native_hand_word_operand_and_removed_load_witness',
    'protocol_sha256': sys.argv[1], 'entry_witnesses': witnesses, 'negative_reader_fixtures': negative,
    'all_owned_capture_disassembly_children_terminal': True,
    'new_application_kernel_solver_or_speed_samples': 0, 'candidate_adopted': False
})
h.custody()
print('D297 both native terminal word/load/decode witnesses passed.', flush=True)
