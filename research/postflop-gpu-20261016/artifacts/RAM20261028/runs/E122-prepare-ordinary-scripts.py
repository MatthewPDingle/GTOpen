"""Stage ordinary-build and initial timing preparers; do not run dependents."""
import ast
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
replacements = [
    ('E120', 'E122'), ('e120', 'e122'), ('13180', '13300'), ('26360', '26600'),
    ('pass_scoped_full_sparse_card_raw_equivalence', 'pass_scoped_full_predicated_correction_raw_equivalence'),
    ('D293-sparse-card-PTX', 'D300-predicated-correction-PTX'),
    ('D294-sparse-card-native', 'D301-predicated-correction-native'),
    ("b'kept_card_end[52]' in data", "b'@p_lo add.rn.f32' in data"),
    ('fixed sparse-card CUDA body', 'fixed predicated-correction CUDA body'),
    ('One stable sparse-card CUDA form.', 'One fixed inline-predicated original rank-correction CUDA form.'),
    ('52sharedendpoints/+208B andregister38to40warningsretained.', 'No sharedgrowth; register38to40 warningretained.'),
    ('Same oneCUDAform', 'Same one predicated-correction CUDA form'),
    ('stable within-original-cardlistcompaction andfullprefix/payout', 'explicit nativeconditional corrections with original fullprefix/payout'),
    ('register38to40/static+208Bwarningsretained', 'register38to40warning; no staticsharedgrowth'),
    ('B369', 'B375'), ('B370', 'B376'), ('B371', 'B377')
]
for stem in ['prepare-build', 'prepare-primary']:
    code = (ROOT / 'runs' / ('E120-' + stem + '.py')).read_text()
    for before, after in replacements:
        code = code.replace(before, after)
    # This literal is an argument to a second generator, so substitute in its
    # resulting script expression as well as the inherited resource narration.
    if stem == 'prepare-build':
        assert 'D300-predicated-correction-PTX' in code
    ast.parse(code)
    path = ROOT / 'runs' / ('E122-' + stem + '.py')
    with path.open('xb') as stream:
        stream.write(code.encode())
    print(path)
