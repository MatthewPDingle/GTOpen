import ast, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
parent = ROOT / 'runs/D301-predicated-correction-native.py'
path = ROOT / 'runs/D307-normal-division-native.py'
code = parent.read_text(encoding='utf-8')
changes = [
    ('D301-predicated-correction-native', 'D307-normal-division-native'), ('E122-resource', 'E124-resource'),
    ('E122-source', 'E124-source'), ('D300-predicated-correction-PTX', 'D306-normal-division-PTX'),
    ("'pass_scoped_predicated_correction_PTX_original_words_priority_and_barriers'", "'pass_scoped_all_RNFTZ_guard_operands_fallback_and_join'"),
    ("ROOT / 'runs/D306-normal-division-PTX/protocol.json'", "ROOT / 'runs/D306-normal-division-PTX/protocol-v2.json'"),
    ("['up_fold', 'up_show']", "['down_action', 'up_action']"),
    ("'id': 'D301'", "'id': 'D307'"),
    ('two terminal entry sections', 'two normalization entry sections'),
    ('Two terminal sections.', 'Two normalization sections.'),
    ('captured_predicated_correction_native_operand_review_pending', 'captured_guarded_normal_division_native_review_pending'),
    ('Require actualnativeup_showFSEL30to0, bothoriginalrank-conditionedadditionoperand/prioritychains andalloriginalbarriers beforefullrawdirectGPUcontrols.', 'Require originalguard/operand/fallback provenance and a native guardedpositive path removing division-specific FCHK/CALL or ordinary instruction work without moreRCP/refinementFMA; virtualFTZalone/countonlyhistograms insufficient beforefullrawcontrols.'),
    ('D301 native sections captured; explicit correction operand and selector review pending.', 'D307 native sections captured; guarded division work/path review pending.')
]
for before, after in changes:
    assert before in code, before
    code = code.replace(before, after)
ast.parse(code)
with path.open('xb') as stream:
    stream.write(code.encode())
print(path, flush=True)
