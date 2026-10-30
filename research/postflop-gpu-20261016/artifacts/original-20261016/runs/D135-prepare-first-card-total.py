"""Freeze a separate showdown first-card sum reuse experiment, off tree."""
import ast
import difflib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request

R = Path(r'S:\GTOpen-research\postflop-gpu-20261016')
C = R / 'runs/accepted-E080-live-20261018'
sys.path.insert(0, str(C))
import common_e080_live as old
old.custody()
assert not (R / 'gpu-run.lock').exists()
old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free >= 66 * 1024**3
assert shutil.disk_usage('T:\\').free >= 53687091200
D, S, H = [R / ('runs/' + name) for name in
           ['D135-first-card-total', 'E084-source', 'E084-resource']]
assert not any(p.exists() for p in [D, S, H])
for p in [D, S, H]:
    p.mkdir()

history = []
for command in [
    ['git', 'log', '--all', '--oneline', '-G', 'card_total|card_totals|tot_c = chunk_sum|first.card.*total', '--', 'crates/solver/src/gpu/kernels.cu'],
    ['rg', '-n', '-i', 'card.total|card_total|total.*first.card|first.card.*total|tot_c.*cache|cache.*tot_c', 'research/postflop-gpu-20261016/experiments.md'],
]:
    p = subprocess.run(command, cwd=old.REPO, text=True, capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)
    assert p.returncode in [0, 1]
    history.append({'command': command, 'returncode': p.returncode,
                    'stdout': p.stdout, 'stderr': p.stderr})
old.save(D / 'history.json', {
    'at': old.now(), 'bounded_local_history': history,
    'difference': 'Precompute only the full ordered sum for each first hole card. Reuse retired chunk_sum storage. Original first-card lower/higher loops remain; the second-card total loop starts from the identical first-card accumulator. No reassociation or two-independent-card sum combination.',
    'closed_forms_not_composed': ['E029 zero complement', 'E063 precomputed cutoffs', 'E077 selective prefix stores', 'E082 duplicated chunk-prefix consumers', 'E083 initialization fences'],
    'limits': 'Bounded local history and source audit; no exhaustive remote novelty or speed claim.'})

rel = 'crates/solver/src/gpu/kernels.cu'
raw = (old.REPO / rel).read_bytes()
base = raw.decode()
nl = '\r\n' if b'\r\n' in raw else '\n'
before = '''    float total = m_o > 0 ? prefix[m_o - 1] : 0.f;'''
after = '''    // The scan has retired all chunk_sum consumers. Reuse its first 52
    // words for each card's original ordered sum, starting at positive zero.
    for (int c = threadIdx.x; c < 52; c += blockDim.x) {
        float acc = 0.f;
        u32 c0 = o_card_off[(u64)slot * 53 + c];
        u32 c1 = o_card_off[(u64)slot * 53 + c + 1];
        for (u32 t = c0; t < c1; t++)
            acc += reach_sh[card_pos_sh[t - card_base]];
        chunk_sum[c] = acc;
    }
    __syncthreads();
    float total = m_o > 0 ? prefix[m_o - 1] : 0.f;'''.replace('\n', nl)
assert base.count(before) == 1
candidate = base.replace(before, after, 1)
changes = [
    ('float tot_c = 0.f, lower_c = 0.f, higher_c = 0.f;',
     'float tot_c = chunk_sum[pc1[i]], lower_c = 0.f, higher_c = 0.f;'),
    ('                tot_c += r;', '                if (x != 0) tot_c += r;'),
]
for a, b in changes:
    assert candidate.count(a) == 1
    candidate = candidate.replace(a, b, 1)
reverse = candidate
for a, b in reversed(changes):
    reverse = reverse.replace(b, a, 1)
reverse = reverse.replace(after, before, 1)
assert reverse == base
start = base.index('extern "C" __global__ void up_show(')
end = base.index('// Up sweep, chance nodes:', start)
assert base[:start] == candidate[:start]
assert base[end:] == candidate[candidate.index('// Up sweep, chance nodes:', start):]
for name, data in [('baseline.cu', raw), ('candidate.cu', candidate.encode())]:
    (S / name).write_bytes(data)
    shutil.copyfile(S / name, H / name)
(S / 'kernels.cu.patch').write_text(''.join(difflib.unified_diff(
    base.splitlines(True), candidate.splitlines(True),
    fromfile='accepted/kernels.cu', tofile='E084/kernels.cu')), encoding='utf-8', newline='')

corpus_path = R / 'runs/E082-kernel-control/corpus.json'
corpus = old.read(corpus_path)
checks, work = 0, []
for g in corpus['geometries']:
    a = g['arrays']; off = a['o_card_off']; pos = a['o_card_pos']
    lists = [pos[off[53+c]:off[53+c+1]] for c in range(52)]
    old_first = 0
    for k in range(g['m_p']):
        i = a['p_idx'][a['p_off'][1] + k]
        first, second = lists[a['pc1'][i]], lists[a['pc2'][i]]
        # Replacing a complete prefix by that exact serial prefix value
        # leaves the same subsequent ordered additions, including duplicates.
        original = [('positive-zero',)] + [('reach', p) for p in first + second]
        replacement = [('positive-zero',)] + [('reach', p) for p in first]
        replacement.extend(('reach', p) for p in second)
        assert original == replacement
        old_first += len(first); checks += 1
    assert all(p < g['m_o'] for lst in lists for p in lst)
    assert sum(map(len, lists)) == 2 * g['m_o']
    checks += 2
    work.append({'geometry': g['id'], 'm_p': g['m_p'], 'm_o': g['m_o'],
                 'old_first_card_total_additions': old_first,
                 'new_all_card_serial_additions': 2*g['m_o'],
                 'nominal_total_additions_saved': old_first - 2*g['m_o']})
old.save(D / 'ordered-sum-control.json', {'at': old.now(),
    'status': 'pass_ordered_symbolic_accumulator_sequence', 'checks': checks,
    'geometries': len(work), 'work_counts': work, 'corpus_sha256': old.sha(corpus_path),
    'limits': 'Integer work counts and identical ordered operand lists only. Extra shared traffic, barrier, register pressure and hardware code are unmeasured. No numerical, synchronization, speed or complete-cycle proof.'})
scope = 'Only up_show: fill first52 retired chunk_sum words with original full per-card serial sums after its original final scan barrier; one extra CTA barrier; initialize tot_c from the first card cache and retain all second-card additions and both lower/higher correction loops. No other entry, ABI, allocation, host, launch, scan, layout, precision, quality or save change.'
old.save(S / 'source-review.json', {'at': old.now(), 'scope': scope,
    'source_reverse_exact': True,
    'ordered_arithmetic': 'Each card sum begins with +0 and adds reach_sh[card_pos_sh[t-card_base]] in original t order. Original tot_c is the completed first-card serial accumulator followed by the second-card serial additions. Cache replaces exactly the first accumulator; it does not add two independently summed cards. Original lower_c/higher_c recurrences are unchanged. GPU bitwise parity including NaN/signedzero remains to be tested.',
    'synchronization': 'Original final scan CTA barrier retires every chunk_sum read and completes reach_sh/card_pos_sh writes. Threads stride over independent card IDs and write only cache[0..52], within the existing257word array even at width1. The added uniform CTA barrier publishes all cached sums before any hand consumes them. No chunk_sum read or write overlaps its scan lifetime.',
    'barriers_before_after': [base[start:end].count('__syncthreads()'), candidate[start:candidate.index('// Up sweep, chance nodes:', start)].count('__syncthreads()')],
    'risks': 'New serial per-card work, a CTA barrier, shared reads/writes and longer register lifetimes may outweigh removed per-hand additions. Small/empty/tail inputs may regress. No resource or no-tradeoff assertion from source.'})
old.save(S / 'manifest.json', {'id': 'E084', 'at': old.now(),
    'owned': {rel: {'base': str(S/'baseline.cu'), 'candidate': str(S/'candidate.cu')}},
    'candidate_owned_sha256': {rel: old.sha(S/'candidate.cu')}, 'scope': scope,
    'source_activated': False, 'candidate_accepted': False, 'previous_accepted': 'E080'})

prior = R / 'runs/E082-resource'
probe = (prior / 'probe.rs').read_text().replace('E082', 'E084')
(H / 'probe.rs').write_text(probe, encoding='utf-8', newline='\n')
execute = (prior / 'execute.py').read_text().replace('E082', 'E084')
execute = execute.replace('pass_compiled_prefix_consumer_prerequisites', 'pass_compiled_first_card_total_prerequisites')
execute = execute.replace('prefix/synchronization correctness', 'ordered-card-sum/synchronization correctness')
ast.parse(execute)
(H / 'execute.py').write_text(execute, encoding='utf-8', newline='\n')
P0 = old.read(prior / 'protocol.json')
deps = {p: h for p, h in P0['input_sha256'].items()
        if Path(p).suffix in ['.rlib', '.rmeta', '.lib', '.dll']}
paths = [Path(__file__), corpus_path, C/'common_e080_live.py', C/'protected-main.json',
         old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',
         *[p for folder in [D, S, H] for p in folder.iterdir() if p.is_file()]]
P = {'id': 'E084-resource', 'at': old.now(), 'status': 'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE',
     'rustc_command': [x.replace('E082-resource', 'E084-resource') for x in P0['rustc_command']],
     'input_sha256': deps | {str(p): old.sha(p) for p in paths},
     'gpu_uuid': P0['gpu_uuid'], 'expected_entries': P0['expected_entries'],
     'target_kernel': 'up_show', 'expected_parameters': 27,
     'resource_gates': 'Other8entry normalized PTX and27parameter ABI exact at120/75. Actual120 local/static/dynamic shared not increased; maxthreads not reduced; fixed64/128/256 legal and positive residency; default128 residency not reduced; no context stack increase.',
     'scope': 'One Rust compiler, one resource-only process, four NVRTC compiles. No application kernel, solver, timing score or production source activation.',
     'failure_policy': 'Close this exact first-card full-sum cache and retired-scan-storage form on a real resource, numerical, performance or material failure. No widths, card subsets, thresholds, helpers, array encodings, caller/source scopes, placement variants, sweeps, retries or extra samples to rescue it. Reader-only repairs may replay retained observations.',
     'candidate_accepted': False}
old.save(H / 'protocol.json', P)
pub = []
for folder in [D, S, H]:
    for p in folder.iterdir():
        if not p.is_file(): continue
        key = folder.name + '/' + p.name
        dst = old.ar.DASHBOARD/'evidence'/key
        dst.parent.mkdir(parents=True, exist_ok=True)
        assert not dst.exists()
        shutil.copyfile(p, dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key, timeout=20) as response:
            assert response.read() == p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'), timeout=3):
    st = old.read(old.ar.STATUS)
    assert not any(x['id'] in ['D135', 'E084'] for x in st['experiments'])
    st['experiments'].extend([
        {'id': 'D135', 'at': old.now(), 'title': 'Reuse original first-card totals',
         'status': 'measured', 'correctness': 'source_only', 'accepted': False,
         'reason': 'Ordered operand-list and storage-lifetime audit supports a resource trial; GPU exactness and speed remain unproven.',
         'evidence': [{'label': 'Ordered-sum source control', 'url': 'evidence/D135-first-card-total/ordered-sum-control.json'},
                      {'label': 'Bounded history search', 'url': 'evidence/D135-first-card-total/history.json'}]},
        {'id': 'E084', 'at': old.now(), 'title': 'Cache showdown first-card totals',
         'status': 'running', 'correctness': 'pending', 'accepted': False,
         'stage': 'Compiled resource prerequisite',
         'reason': 'Reuse the exact first-card serial sum from retired shared scan storage. A new barrier and extra card work may outweigh removed additions. No speed result.',
         'evidence': [{'label': 'Arithmetic and synchronization review', 'url': 'evidence/E084-source/source-review.json'},
                      {'label': 'Frozen resource gates', 'url': 'evidence/E084-resource/protocol.json'}]}
    ])
    st.update(updated_at=old.now(), state='running', goal_status='active', active_experiment='E084',
              stage='E084 compiled resource prerequisite',
              activity='Testing reuse of exact first-card totals in showdown without regrouping floating additions. Added synchronization and shared traffic may negate any benefit. Accepted E080 remains live at14.74% benchmark gain.')
    old.ar.atomic_json(old.ar.STATUS, st)
old.save(D/'publication.json', {'at': old.now(), 'HTTP_verified_artifacts': pub,
    'resource_protocol_sha256': old.sha(H/'protocol.json'), 'new_native_processes': 0})
old.custody()
print(old.sha(H/'protocol.json'), flush=True)
