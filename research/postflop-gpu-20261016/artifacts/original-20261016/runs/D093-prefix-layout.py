"""One fixed bank-aware prefix permutation, CPU controls before any CUDA work."""
import array, collections, difflib, hashlib, json, re, shutil, struct, sys
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(ROOT).free>=54*1024**3
D=ROOT/'runs/D093-prefix-layout';S=ROOT/'runs/E057-source';assert not D.exists() and not S.exists();D.mkdir();S.mkdir()
path=old.REPO/'crates/solver/src/gpu/kernels.cu';base=path.read_bytes();old.pin(path,'a926bf0bc818a2ba808c862b59a552dfb7ade453ca18f347b4307784e47d9647')
text=base.decode();begin=text.index('// Up sweep, showdown terminals:');end=text.index('// Up sweep, chance nodes:',begin);body=text[begin:end]
helper='''// In complete 32-word tiles, XOR high index bits into bank bits. The
// final partial tile stays in place, so the allocation and bounds are exact.
__device__ __forceinline__ int show_prefix_index(int k, int m, bool permute)
{
    return permute && k < (m & ~31) ? k ^ ((k >> 5) & 31) : k;
}

'''.replace('\n','\r\n')
old_decl='    {\r\n        int chunk = (m_o + blockDim.x - 1) / blockDim.x;\r\n'
new_decl='    int chunk = (m_o + blockDim.x - 1) / blockDim.x;\r\n    bool permute_prefix = chunk > 1 && (chunk & (chunk - 1)) == 0;\r\n    {\r\n'
assert body.count(old_decl)==1
body=body.replace(old_decl,new_decl)
replacements={'prefix[k]':'prefix[show_prefix_index(k, m_o, permute_prefix)]','prefix[m_o - 1]':'prefix[show_prefix_index(m_o - 1, m_o, permute_prefix)]','prefix[lb - 1]':'prefix[show_prefix_index((int)lb - 1, m_o, permute_prefix)]','prefix[ub - 1]':'prefix[show_prefix_index((int)ub - 1, m_o, permute_prefix)]'}
for src,dest in replacements.items():
    assert body.count(src)==(2 if src=='prefix[k]' else 1)
    body=body.replace(src,dest)
candidate=(text[:begin]+helper+body+text[end:]).encode()
assert base.count(b'__syncthreads();')==candidate.count(b'__syncthreads();')
for name,data in [('baseline.cu',base),('candidate.cu',candidate)]:(S/name).write_bytes(data)
(S/'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(True),candidate.decode().splitlines(True),fromfile='a/crates/solver/src/gpu/kernels.cu',tofile='b/crates/solver/src/gpu/kernels.cu')),encoding='utf-8',newline='')
anchor=ROOT/'runs/E051-resource/execution/candidate.ptx';ptx=anchor.read_text();a=ptx.index('.entry up_show(');b=ptx.index('.visible .entry ',a+10);show=ptx[a:b]
(D/'accepted-up-show.ptx.txt').write_text(show,encoding='utf-8',newline='\n')
prior=old.read(ROOT/'runs/D092-action-arity-order/report.json');cases=[prior['cases'][i] for i in [3,7,11]]
schema=old.read(ROOT/'runs/D092-action-arity-order/field-schema.json')['fields']
protocol={'id':'D093-prefix-layout','at':old.now(),'status':'FROZEN_BEFORE_CPU_MODEL','candidate':'E057','candidate_sha256':old.sha(S/'candidate.cu'),'transform':'Only prefix-buffer physical indices change. Full32word tiles use k XOR ((k>>5)&31); final partial tile is identity. Enable only for power-of-two per-thread chunk lengths greater than1; otherwise identity. This fixed structural choice targets power-of-two bank strides, not measured parameter tuning. All five prefix accesses use the same function. No new storage, barriers, metadata, ABI, launch or float operation.','history':'Scoped ledger/research plus retained CU/patch/review search found no postflop prefix swizzle. E008 carry, E022 tail pruning, E031 offset cache, E050 async, E052 width and E053 producer fusion remain absent/closed; this changes addresses only, not those mechanisms.','proof':'Each full tile retains tile ID and XORs a tile-constant into its lower5bits, hence is an involution/bijection. Partial tail identity is disjoint. Original same-k producer/consumer ownership and arithmetic dependencies are preserved. Test both flags for every0..1326length and all integer block geometries1..256.','bank_reference':{'url':'https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html#shared-memory','fact':'NVIDIA documents32banks with successive32bit words mapped to successive banks; same-address reads may broadcast. This model counts distinct words per bank, not hardware time.'},'ptx_observation':'Accepted E051 up_show PTX contains scalar f32 shared loads/stores in the blocked prefix recurrence and carry application. This is PTX, not final SASS or a measured bank-conflict counter. Driver lowering may change transactions.','fixed_cpu_model_gate':'Exact bounded permutation, at least one fixture has reduced modeled total prefix requests and none increases. Model one complete show pass for both players; count scan prefix stores plus carry read/store, total read and lower/upper queries. Reach/card-position traffic, arithmetic, barriers, instruction issue, actual iterations and driver SASS are outside this model. A pass only admits resource inspection.','later_gates':'One no-launch resource probe, no register/local/static/dynamic increase or maxthread/occupancy loss, exact ABI/other8entries at compute120/75. If that passes, direct raw up_show equivalence before unchanged three-pair1%screen, separately frozen16pairs and all broad/material/holdout/cumulative checks. No key/width/guard/block/schedule variants to rescue a failed gate.','inputs':{str(anchor):old.sha(anchor),str(ROOT/'runs/D092-action-arity-order/report.json'):old.sha(ROOT/'runs/D092-action-arity-order/report.json'),**{c['raw_file']:c['raw_sha256'] for c in cases}},'source_activated':False,'gpu_executions':0,'performance_measured':False,'reviewer':'Root source review/model, not external independent review'}
old.save(D/'protocol.json',protocol)
for p,h in protocol['inputs'].items():old.pin(p,h)
def index(k,m,enabled):return k^((k>>5)&31) if enabled and k<(m&~31) else k
proof_cases=0;words=0
for m in range(1327):
    for enabled in [False,True]:
        out=[index(k,m,enabled) for k in range(m)]
        assert sorted(out)==list(range(m)) and all(index(out[k],m,enabled)==k for k in range(m))
        proof_cases+=1;words+=m
geometry=collections.Counter()
for m in range(1327):
    for block in range(1,257):
        chunk=(m+block-1)//block;enable=chunk>1 and chunk&(chunk-1)==0
        geometry[enable]+=1
        assert (chunk==0 and m==0) or (chunk>0 and (m+chunk-1)//chunk<=block)
def readvec(f,keep):
    n,=struct.unpack('<Q',f.read(8));assert n<100000000
    if not keep:f.seek(n*8,1);return None
    v=array.array('Q');v.fromfile(f,n)
    if sys.byteorder!='little':v.byteswap()
    return v
def metadata(path,identity):
    wanted={'show_nodes','node_river_slot','riv_cnt','riv_off','riv_lower','riv_upper'};out={}
    with path.open('rb') as f:
        assert f.read(16)==b'D092-PLAN-RAW1\0\0';i,n=struct.unpack('<II',f.read(8));assert i==identity and n==53;f.read(16)
        for j,definition in enumerate(schema):
            fieldid,=struct.unpack('<I',f.read(4));assert fieldid==j
            for a in range(4):
                value=readvec(f,definition['name'] in wanted and a==2)
                if value is not None:out[definition['name']]=value
    return out
def vec(v):assert v[0]==len(v)-1;return v[1:]
def pair(v):
    assert v[0]==2;n=v[1];x=v[2:2+n];k=2+n;m=v[k];y=v[k+1:];assert len(y)==m;return [x,y]
def pressure(indices):
    banks=[set() for _ in range(32)]
    for k in indices:banks[k%32].add(k)
    return max(map(len,banks),default=0)
scan_cache={}
def scan(m):
    if m in scan_cache:return scan_cache[m]
    block=128;chunk=(m+block-1)//block;enable=chunk>1 and chunk&(chunk-1)==0
    old_units=new_units=0
    for j in range(chunk):
        for warp in range(0,block,32):
            kk=[t*chunk+j for t in range(warp,warp+32) if t*chunk+j<m]
            old_units+=3*pressure(kk);new_units+=3*pressure([index(k,m,enable) for k in kk])
    if m:old_units+=1;new_units+=1
    scan_cache[m]=(old_units,new_units,enable);return scan_cache[m]
results=[]
for case in cases:
    maps=metadata(Path(case['raw_file']),case['id']);slots=vec(maps['node_river_slot']);counts=collections.Counter(slots[n] for n in vec(maps['show_nodes']));cnt=pair(maps['riv_cnt']);off=pair(maps['riv_off']);lower=pair(maps['riv_lower']);upper=pair(maps['riv_upper'])
    rows=[]
    for p in [0,1]:
        totals=collections.Counter();shapes=collections.Counter()
        for slot,freq in counts.items():
            mo=cnt[1-p][slot];mp=cnt[p][slot];start=off[p][slot];old_scan,new_scan,enable=scan(mo);shapes[mo]+=freq
            old_query=new_query=0
            for warp in range(0,mp,32):
                for boundaries in [lower[p],upper[p]]:
                    kk=[boundaries[start+k]-1 for k in range(warp,min(warp+32,mp)) if boundaries[start+k]>0]
                    assert all(k<mo for k in kk)
                    old_query+=pressure(kk);new_query+=pressure([index(k,mo,enable) for k in kk])
            totals.update({'baseline_scan':old_scan*freq,'candidate_scan':new_scan*freq,'baseline_query':old_query*freq,'candidate_query':new_query*freq,'swizzled_terminals':freq if enable else 0,'all_terminals':freq})
        rows.append({'player':p,**dict(totals),'opponent_count_distribution':dict(sorted(shapes.items()))})
    before=sum(r['baseline_scan']+r['baseline_query'] for r in rows);after=sum(r['candidate_scan']+r['candidate_query'] for r in rows)
    results.append({'fixture_index':case['fixture_index'],'board':case['board'],'source_metadata_case':case['id'],'raw_metadata_sha256':case['raw_sha256'],'baseline_modeled_requests':before,'candidate_modeled_requests':after,'rows':rows})
gates={'all_lengths_bounded_bijections':proof_cases==2654,'both_flags_all_length_words':words==1759602,'all_integer_geometries':sum(geometry.values())==339712,'some_registered_model_improves':any(r['candidate_modeled_requests']<r['baseline_modeled_requests'] for r in results),'none_registered_model_regresses':all(r['candidate_modeled_requests']<=r['baseline_modeled_requests'] for r in results)}
report={'id':'D093-prefix-layout','at':old.now(),'status':'admit_no_launch_resource_probe' if all(gates.values()) else 'closed_cpu_model_gate','protocol_sha256':old.sha(D/'protocol.json'),'permutation_cases':proof_cases,'permutation_words':words,'block_geometry_cases':sum(geometry.values()),'block_geometry_enabled':dict(geometry),'fixtures':results,'gates':gates,'static_shared_ops_in_accepted_ptx':dict(collections.Counter(re.findall(r'\b(?:ld|st)\.shared\.[a-z0-9]+',show))),'source_activated':False,'gpu_executions':0,'performance_measured':False,'candidate_accepted':False,'limits':'Analytic32bank distinct-word request model of selected prefix accesses only. No hardware counter/SASS, latency/utilization, whole-kernel or complete-cycle gain, numerical GPU or no-tradeoff qualification.'}
old.save(D/'report.json',report)
old.save(S/'source-review.json',{'at':old.now(),'id':'E057','root_source_review_only':True,'proposal':protocol,'cpu_model_sha256':old.sha(D/'report.json'),'candidate_accepted':False})
old.save(S/'manifest.json',{'at':old.now(),'baseline':'E051','baseline_source_sha256':old.BASE,'candidate_owned_sha256':{'crates/solver/src/gpu/kernels.cu':old.sha(S/'candidate.cu')},'artifact_sha256':{p.name:old.sha(p) for p in S.iterdir()},'no_production_activation':True})
old.custody();print(json.dumps({'status':report['status'],'gates':gates,'model':[{k:r[k] for k in ['board','baseline_modeled_requests','candidate_modeled_requests']} for r in results],'candidate_sha256':old.sha(S/'candidate.cu')}),flush=True)
