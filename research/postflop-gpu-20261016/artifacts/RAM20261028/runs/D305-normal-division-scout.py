"""Source/history and exact-rational range review; no CUDA work."""
import hashlib, itertools, json, math, re, struct, subprocess, sys
from fractions import Fraction
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
h.custody()
h.ar.refuse_active(h.ar.live_status())
assert not (ROOT / 'gpu-run.lock').exists() and not (ROOT / 'epoch-sequence.lock').exists()
H = ROOT / 'runs/D305-normal-division-scout'
H.mkdir(exist_ok=False)
seen, hits, inventories = {}, [], []
pattern = re.compile(r'div\.rn\.ftz\.f32')
for folder in [Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs'), ROOT / 'runs']:
    paths = subprocess.check_output(['rg', '--files', str(folder), '-g', '*.cu'], text=True).splitlines()
    inventories.append({'root': str(folder), 'CUDA_files': len(paths)})
    for name in paths:
        blob = Path(name).read_bytes()
        digest = hashlib.sha256(blob).hexdigest()
        if digest in seen:
            continue
        seen[digest] = name
        if pattern.search(blob.decode('utf-8')):
            hits.append({'path': name, 'sha256': digest})
revisions = subprocess.check_output(['git', 'log', '--all', '--format=%H', '--', 'crates/solver/src/gpu/kernels.cu'], cwd=h.REPO, text=True).splitlines()
local = []
for revision in revisions:
    text = subprocess.check_output(['git', 'show', revision + ':crates/solver/src/gpu/kernels.cu'], cwd=h.REPO).decode('utf-8')
    if pattern.search(text):
        local.append(revision)
h.save(H / 'history.json', {'at': h.now(), 'inventories': inventories, 'unique_CUDA_hashes': len(seen),
    'pattern': pattern.pattern, 'retained_matches': hits, 'all_local_ref_revisions': len(revisions), 'local_matches': local,
    'classification': 'New concept uses per-quotient native div.rn.ftz under exact normal-input/output bounds; retains independent native division per action and original ordinary division fallback. E060 instead shares hand-coded reciprocal/refinement across actions; it remains closed with all guard/window/math/arity/scope variants of that sharing form. E101zero bypass/E116singlepositive bypass remainclosed; this concept skips no positive division and includes neither old helper nor shared reciprocal/FMA nor zero/one shortcut. D108 integerchunk quotient is unrelated.',
    'counterevidence': 'D098 original driver SASS already has ordinary reciprocal/FMA fast sequences and exceptional FCHK/CALL branches; ordinary values may already avoid slow work. FTZ may not shorten native ordinary path; added comparisons/branch/codesize/registers may make it worse. No missing generic fastpath, dynamic incidence, removable time or speed inferred.',
    'limits': 'Bounded literal/local-all-ref novelty review, not exhaustive semantic/remote search.'})
assert not hits and not local, 'Review prior same primitive before staging'

def power(exponent):
    return Fraction(1 << exponent) if exponent >= 0 else Fraction(1, 1 << -exponent)

def nearest_integer(value):
    q, r = divmod(value.numerator, value.denominator)
    return q + (2 * r > value.denominator or (2 * r == value.denominator and q % 2 == 1))

def rn32(value):
    assert value >= 0
    if value == 0:
        return 0
    exponent = value.numerator.bit_length() - value.denominator.bit_length()
    if value < power(exponent):
        exponent -= 1
    if exponent < -126:
        mantissa = nearest_integer(value / power(-149))
        assert mantissa <= 0x800000
        return mantissa
    if exponent > 127:
        return 0x7f800000
    mantissa = nearest_integer(value / power(exponent - 23))
    if mantissa == 1 << 24:
        exponent += 1
        mantissa >>= 1
    if exponent > 127:
        return 0x7f800000
    return ((exponent + 127) << 23) | (mantissa - (1 << 23))

def value(bits):
    return struct.unpack('<f', struct.pack('<I', bits))[0]

lo, hi = value(0x20000000), value(0x5f000000)
assert Fraction(lo) == power(-63) and Fraction(hi) == power(63)
assert power(-63) / power(63) == power(-126)
for exact, bits in [(power(-149), 1), (power(-126), 0x800000), (Fraction(1), 0x3f800000), (power(-1), 0x3f000000), (Fraction(0), 0)]:
    assert rn32(exact) == bits
bits = [0, 1, 2, 0x007fffff, 0x00800000, 0x00800001, 0x1ffffffe, 0x1fffffff, 0x20000000, 0x20000001,
        0x3f000000, 0x3f7fffff, 0x3f800000, 0x3f800001, 0x5effffff, 0x5f000000, 0x5f000001,
        0x7f7fffff, 0x7f800000, 0x7fc12345, 0x7f812345]
bits += [word | 0x80000000 for word in bits]
eligible, fallback = 0, 0
for nb, db in itertools.product(bits, repeat=2):
    n, d = value(nb), value(db)
    fast = n >= lo and d <= hi and n <= d
    if fast:
        assert math.isfinite(n) and math.isfinite(d) and n >= power(-126) and d >= power(-126)
        exact = Fraction(n) / Fraction(d)
        assert power(-126) <= exact <= 1
        result = rn32(exact)
        assert 0x00800000 <= result <= 0x3f800000
        eligible += 1
    else:
        fallback += 1
negative = []
for name, nb, db in [('weaken_numerator_bound', 0x1ffffffe, 0x5f000000), ('weaken_denominator_bound', 0x20000000, 0x5f000001)]:
    n, d = value(nb), value(db)
    assert not (n >= lo and d <= hi and n <= d)
    original = rn32(Fraction(n) / Fraction(d))
    assert original == 0x007fffff
    negative.append({'case': name, 'numerator_bits': nb, 'denominator_bits': db, 'RN_original_bits': original,
                     'incorrectly_unguarded_FTZ_output_bits': 0})
h.save(H / 'range-contract.json', {'at': h.now(), 'source': 'https://docs.nvidia.com/cuda/archive/12.9.0/parallel-thread-execution/index.html#floating-point-instructions-div',
    'source_review': 'NVIDIA PTX8.8/CUDA12.9 documents RN as nearest-even and FTZ as flushing subnormal instruction inputs/results. No approximate division, reciprocal multiplication or global compiler fast-math/FTZ option proposed.',
    'fixed_guard': 'n>=2^-63 && d<=2^63 && n<=d; ordinary original n/d otherwise. Zero/NaN/infinity/negative/tiny/too-large inputs fallback naturally through ordered comparisons.',
    'exact_bits': {'numerator_lower': '0x20000000', 'denominator_upper': '0x5f000000', 'minimum_quotient': '0x00800000'},
    'proof': 'Guard implies finite positive normal2^-63<=n<=d<=2^63. Exact real q=n/d lies in[2^-126,1]. RN to binary32 stays in the same representable bounded interval, hence is normal. FTZ modifies neither original operands nor RN output under these bounds. This algebra covers every guard-eligible binary32 pair assuming documented instruction semantics; it does not prove source lowering, branch execution, IEEE special fallback/NaN payloads or actual GPU outputs.',
    'CPU_boundary_cases': len(bits)**2, 'eligible': eligible, 'original_fallback': fallback,
    'exact_rational_nearest_even_reference_fixture_checks': 5, 'negative_guard_counterexamples': negative,
    'new_compiler_GPU_kernel_solver_or_speed_samples': 0})
h.save(H / 'report.json', {'id': 'D305', 'at': h.now(), 'status': 'pass_scoped_history_and_exact_rational_normal_range_contract',
    'history_sha256': h.sha(H / 'history.json'), 'range_contract_sha256': h.sha(H / 'range-contract.json'),
    'eligible_boundary_cases': eligible, 'fallback_boundary_cases': fallback, 'negative_counterexamples': 2,
    'no_native_accuracy_or_performance_claim': True, 'new_compiler_GPU_kernel_solver_or_speed_samples': 0})
h.custody()
print(json.dumps({'unique_CUDA': len(seen), 'boundary_cases': len(bits)**2, 'eligible': eligible, 'fallback': fallback, 'report_sha256': h.sha(H / 'report.json')}), flush=True)
