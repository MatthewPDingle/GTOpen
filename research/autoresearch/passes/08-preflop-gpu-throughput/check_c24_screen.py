"""Audit four-sample GPU evidence independently of the Rust test counters."""
import hashlib,json,re
from pathlib import Path
P=Path(__file__).resolve().parent;R=P/'raw';ROOT=P.parents[3]
def read(p):return json.loads(p.read_text(encoding='utf-8'))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
run=read(R/'c24-static-v1-exit.json');out=R/'c24-static-v1'
assert run['returncode']==0 and run['reason'] is None and run['seconds']<=300
for file,digest in run['inputs'].items():assert sha(Path(file))==digest,file
for file,digest in run['solver_source_files'].items():assert sha(ROOT/file)==digest,file
log=(R/'c24-static-v1.log').read_text()
assert '1 passed; 0 failed; 0 ignored' in log
test_seconds=float(re.search(r'finished in ([0-9.]+)s',log)[1])
source_map=read(P/'artifacts/c24-source-map.json')
assert len(source_map)==1
for file,entry in source_map.items():
    assert sha(P/'artifacts/c24-before/static_cdf.rs')==entry['before']
    assert sha(ROOT/file)==sha(P/'artifacts/c24-v1/static_cdf.rs')==entry['after']
r=read(out/'results.json')
expected=[dict(kind=k,pattern=p,compact=c,gate=g,batch=4,count=n,sample_start=s)
    for k in range(5) for p in [1,0,1,2,3,4,5,6,7,8,9,10] for c in [0,1] for g in [0,1]
    for n in [1,2,3,4] for s in [0,17,237,1020]]
assert r['cases']==expected and r['exact'] and r['prefix_cases']==3840
assert r['hand_vector_cases']==len(expected)*7*2==53760
assert r['required_prefixes_checked']==1185984 and r['unused_slots_checked']==4346688
maps=read(out/'maps.json');original_maps=read(R/'c23-static-v1/maps.json')
assert len(maps)==len(original_maps)==5
for m,old in zip(maps,original_maps):
    for key in ['kind','prefix','hand_group','sample_offsets']:assert m[key]==old[key]
    o=m['sample_offsets'];stride=max(o[min(s+4,1024)]-o[s] for s in range(1024))
    assert m['stride']==stride
    for case in expected:
        if case['kind']!=m['kind']:continue
        start=case['sample_start'];count=case['count']
        assert start+count<=1024 and o[start+count]-o[start]<=stride
assert maps[4]['stride']==read(R/'d20-verified.json')['current_layout']['stride']==333
hashes={}
for file in ['control.cu','candidate.cu','control.ptx','candidate.ptx']:
    hashes[file]=sha(out/file)
    assert hashes[file]==sha(R/'c23-static-v1'/file),file
assert r['resources']==read(R/'c23-static-v1/results.json')['resources']
receipt=dict(verified=True,admitted=True,retained=False,
    status='Four-sample static tables pass GPU screen; full solver integration next',
    prefix_cases=r['prefix_cases'],hand_vector_cases=r['hand_vector_cases'],
    hand_values=r['hand_vector_cases']*169,required_prefixes_checked=r['required_prefixes_checked'],
    sentinel_slots_checked=r['unused_slots_checked'],real_row_stride=maps[4]['stride'],
    unchanged_cuda_and_ptx_hashes=hashes,unchanged_kernel_resources=True,
    guarded_build_and_test_seconds=run['seconds'],test_seconds=test_seconds,
    full_solver_integrated=False,
    scope='Standalone GPU layout qualification only. Full ordinary-engine integration, numerical continuation, memory recovery and paired runtime measurements remain. No production deployment.')
(R/'c24-screen-verified.json').write_text(json.dumps(receipt,indent=2)+'\n')
(R/'c24-verified.json').write_text(json.dumps(receipt,indent=2)+'\n')
print(json.dumps(receipt))
