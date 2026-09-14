"""Read-only live fallback diagnosis and static-table address audit."""
import gzip, hashlib, json, re, urllib.request
from pathlib import Path
P = Path(__file__).resolve().parent
ROOT = P.parents[3]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def api(path):
    with urllib.request.urlopen('http://127.0.0.1:56708/api/'+path, timeout=10) as f:
        return json.load(f)
session = api('preflop/session'); status = api('preflop/status')
assert session['state'] == status['state'] == 'stopped'
log = ROOT/'target/deployments/r03-20260914-live/r03.log'
text = log.read_text(encoding='utf-8')
line = [x for x in text.splitlines() if 'particles,' in x][-1]
union, batch = map(int, re.search(r'(\d+) reach CDFs, (\d+)-particle batches', line).groups())
line = [x for x in text.splitlines() if 'compact CDF slots' in x][-1]
capacity = int(re.search(r'slots (\d+) of', line)[1])
assert batch == 4 and session['nodes'] == 5704840 and capacity == 1292228
maps_file = P/'raw/d19-static-cdf-maps.json.gz'
a = json.loads(gzip.decompress(maps_file.read_bytes()))
b = next(x for x in json.loads((P/'raw/c23-static-v1/maps.json').read_bytes()) if x['kind'] == 4)
for key in ['prefix', 'hand_group', 'sample_offsets']: assert a[key] == b[key]
o = a['sample_offsets']; prefix = a['prefix']; hands = a['hand_group']
assert len(o) == 1025 and o[0] == 0 and len(prefix) == 1024*170 and len(hands) == 1024*169
hand_checks = 0
for sample in range(1024):
    ids = [x for x in prefix[sample*170:(sample+1)*170] if x != 4294967295]
    assert ids == list(range(o[sample+1]-o[sample])) and prefix[sample*170] == 0
    for h in range(169):
        lo = hands[sample*169+h]
        assert 0 <= lo < lo+1 < o[sample+1]-o[sample]
        hand_checks += 1
rows = []; windows = 0
for width in range(1,33):
    stride = max(o[min(s+width,1024)]-o[s] for s in range(1024))
    for start in range(1024):
        for sample in range(start,min(start+width,1024)):
            assert 0 <= o[sample]-o[start] < o[sample+1]-o[start] <= stride
        windows += 1
    rows.append(dict(batch=width, stride=stride, old_bytes=capacity*width*170*4,
        packed_bytes=capacity*stride*4, allocation_reduction=1-stride/(width*170)))
r = rows[batch-1]; static_bytes = (len(prefix)+len(hands)+len(o))*4
assert r['packed_bytes'] < r['old_bytes'] and r['packed_bytes']//4 < 2**32
scratch = (capacity+(1<<(2*capacity-1).bit_length()))*4
result = dict(verified=True, admitted=True, retained=False,
    status='Four-sample static CDF prototype admitted; no timing claim',
    session={k:session[k] for k in ['config','nodes','action_nodes','arena_mb','iteration','multiway_equity_model']},
    live_status=status, live_log_sha256=sha(log), maps_sha256=sha(maps_file),
    union_slots=union, capacity=capacity, batch=batch, windows_checked=windows,
    hand_boundaries_checked=hand_checks, layouts=rows, current_layout=r,
    static_metadata_bytes=static_bytes,
    net_cdf_bytes_saved=r['old_bytes']-r['packed_bytes']-static_bytes,
    existing_hash_scratch_bytes=scratch, existing_hash_cap_bytes=16*1024*1024,
    old_32_sample_stride_on_four_sample_bytes=capacity*a['row_stride']*4,
    recommendation='Prototype static boundary storage directly on the normal compact normalized engine, retaining four-sample grouping; do not require cohorts or exact-reuse hash storage.',
    limitations='Storage arithmetic and compatibility diagnosis only. No new GPU run, speed result, changed batch size, deployment or accuracy claim.')
(P/'raw/d20-verified.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps({k:result[k] for k in ['status','current_layout','static_metadata_bytes','net_cdf_bytes_saved','existing_hash_scratch_bytes','windows_checked']}))
