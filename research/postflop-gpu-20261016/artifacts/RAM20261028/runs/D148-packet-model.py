import sys, json, hashlib, array
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
assert len(sys.argv) == 2
H = ROOT / 'runs/D148-packet-model'
P = h.read(H / 'protocol.json')
h.pin(H / 'protocol.json', sys.argv[1])
for p, digest in P['input_sha256'].items():
    h.pin(p, digest)
h.custody()
U32, U64 = (1 << 32) - 1, (1 << 64) - 1
checks = 0
def req(value, label):
    global checks
    assert value, label
    checks += 1
def plan(blocks, source_len, host_len, scale_len, cfv_words, staging_words, max_desc):
    if source_len < 0 or host_len < 0 or source_len > U64 // 4 or host_len > U64 // 2 or scale_len < 0 or max_desc <= 0:
        return None
    capacity = min(cfv_words, staging_words, U32)
    if capacity < 0:
        return None
    node_ids, host_intervals, source_intervals = set(), [], []
    for b in blocks:
        src, host, length, node = b['source'], b['host'], b['length'], b['node']
        if min(src, host, length, node) < 0 or length > U32 or src + length > U64 or host + length > U64:
            return None
        if src + length > source_len or host + length > host_len or node >= scale_len or node in node_ids:
            return None
        node_ids.add(node)
        if length:
            source_intervals.append((src, src + length))
            host_intervals.append((host, host + length))
        if 5 + (length + 1) // 2 > capacity:
            return None
    for intervals in [source_intervals, host_intervals]:
        intervals.sort()
        if any(a[1] > b[0] for a, b in zip(intervals, intervals[1:])):
            return None
    packets, pending, qwords = [], [], 0
    def finish():
        nonlocal pending, qwords
        if pending:
            packets.append({'blocks': pending, 'descriptor_words': 4 * len(pending), 'scale_words': len(pending), 'q_words': qwords, 'total_words': 5 * len(pending) + qwords})
            pending, qwords = [], 0
    for b in blocks:
        n = (b['length'] + 1) // 2
        if pending and (len(pending) == max_desc or 5 * (len(pending) + 1) + qwords + n > capacity):
            finish()
        pending.append(dict(b, output_q_word=qwords))
        qwords += n
    finish()
    return packets
def word_at(index, salt):
    return (((index & U32) * 40503) ^ ((index >> 32) * 0x9e37) ^ salt) & 0xffff
def scale_at(node, salt):
    return ((node * 0x9e3779b9) ^ salt ^ 0x7fc01234) & U32
def execute(case, packets, corrupt=None):
    q = array.array('H', [0xa55a]) * case['host_len']
    scales = array.array('I', [0x7fc0cafe]) * case['scale_len']
    injected = False
    for packet in packets:
        blocks = packet['blocks']
        n, total = len(blocks), packet['total_words']
        cap = min(case['cfv_words'], case['staging_words'], U32)
        req(total <= cap and 4 * n <= case['staging_words'] and n + packet['q_words'] <= case['staging_words'], 'all packet regions and both transfers fit')
        scratch = array.array('I', [0xdeadbeef]) * (cap + 16)
        for i, b in enumerate(blocks):
            d = 8 + 4 * i
            scratch[d:d + 4] = array.array('I', [b['source'] & U32, b['source'] >> 32, b['length'], b['output_q_word']])
        for i, b in enumerate(blocks):
            d = 8 + 4 * i
            src = scratch[d] | (scratch[d + 1] << 32)
            length, qstart = scratch[d + 2], scratch[d + 3]
            req(src == b['source'] and length == b['length'], 'u64 source descriptor exact')
            scratch[8 + 4 * n + i] = scale_at(b['node'], case['salt'])
            for j in range((length + 1) // 2):
                lo = word_at(src + 2 * j, case['salt'])
                hi = word_at(src + 2 * j + 1, case['salt']) if 2 * j + 1 < length else 0xd00d
                scratch[8 + 5 * n + qstart + j] = lo | (hi << 16)
        if corrupt and not injected:
            if corrupt == 'scale':
                scratch[8 + 4 * n] ^= 1
                injected = True
            elif any(b['length'] for b in blocks):
                block = next(b for b in blocks if b['length'])
                scratch[8 + 5 * n + block['output_q_word']] ^= 1
                injected = True
        req(all(x == 0xdeadbeef for x in scratch[:8]) and all(x == 0xdeadbeef for x in scratch[8 + total:]), 'all scratch guards exact')
        output = scratch[8 + 4 * n:8 + total]
        for i, b in enumerate(blocks):
            scales[b['node']] = output[i]
            for j in range(b['length']):
                q[b['host'] + j] = (output[n + b['output_q_word'] + j // 2] >> (16 * (j % 2))) & 0xffff
    return q, scales, injected
cases = h.read(H / 'cases.json')
passed = declined = calibrations = wide_cases = 0
represented = 0
details = []
raw_digest = hashlib.sha256()
for index, case in enumerate(cases):
    packets = plan(case['blocks'], case['source_len'], case['host_len'], case['scale_len'], case['cfv_words'], case['staging_words'], case['max_desc'])
    if packets is None:
        declined += 1
        details.append({'case': index, 'decision': 'declined_before_any_write'})
        continue
    expected_q = array.array('H', [0xa55a]) * case['host_len']
    expected_scale = array.array('I', [0x7fc0cafe]) * case['scale_len']
    for b in case['blocks']:
        expected_scale[b['node']] = scale_at(b['node'], case['salt'])
        for j in range(b['length']):
            expected_q[b['host'] + j] = word_at(b['source'] + j, case['salt'])
    actual_q, actual_scale, _ = execute(case, packets)
    req(actual_q == expected_q and actual_scale == expected_scale, 'all host q and scale words including guards match independent direct scatter')
    for corruption in ['q', 'scale']:
        bad_q, bad_scale, injected = execute(case, packets, corruption)
        req(injected and (bad_q != expected_q or bad_scale != expected_scale), 'injected output corruption rejected')
        calibrations += 1
    raw_digest.update(expected_q.tobytes())
    raw_digest.update(expected_scale.tobytes())
    represented += len(expected_q) + len(expected_scale)
    passed += 1
    wide_cases += any(b['source'] > U32 for b in case['blocks'])
    details.append({'case': index, 'decision': 'all_words_and_guards_exact', 'packets': packets, 'words': len(expected_q) + len(expected_scale)})
invalid = h.read(H / 'invalid-cases.json')
for case in invalid:
    req(plan(**case['arguments']) is None, 'invalid/overflow/bounds case declined before packet output')
req(passed > 0 and declined > 0 and wide_cases > 0 and len(invalid) >= 10, 'nontrivial pass/decline/wide inventory')
D = ROOT / 'comparisons/D148-packet-model'
D.mkdir(exist_ok=False)
h.save(D / 'report.json', {'id': 'D148-packet-model', 'at': h.now(), 'status': 'pass_finite_integer_packet_model', 'protocol_sha256': sys.argv[1], 'cases': len(cases), 'physical_cases_passed': passed, 'capacity_declines': declined, 'invalid_declines': len(invalid), 'high_u64_source_cases': wide_cases, 'injected_failure_calibrations': calibrations, 'checks': checks, 'represented_host_q_and_scale_words': represented, 'expected_image_stream_sha256': raw_digest.hexdigest(), 'details': details, 'scope': 'Finite CPU integer/layout model only. Four u32 descriptor words per block, then scales and padded packed q words. All host q/scale and scratch guard words checked against direct writes; odd unused high halves intentionally nonzero. u64 source offsets roundtrip symbolically without allocating huge arrays. No CUDA, quantization arithmetic, native wide-offset, timing, runtime liveness or integration proof.', 'native_or_compiler_children_started': 0, 'candidate_accepted': False})
h.custody()
print(json.dumps({'passed_cases': passed, 'capacity_declines': declined, 'invalid_declines': len(invalid), 'wide_source_cases': wide_cases, 'checks': checks}), flush=True)
