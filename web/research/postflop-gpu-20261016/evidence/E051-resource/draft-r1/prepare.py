"""Freeze early independent strategy stores, without a sigma cache or alias qualifier change."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E051-source';D.mkdir();path=old.REPO/'crates/solver/src/gpu/kernels.cu';base=path.read_text(encoding='utf-8')
a=base.index('__device__ __forceinline__ void up_action_impl(');z=base.index('extern "C" __global__ void up_action(',a)
body=base[a:z];c=body
reach='            float reach = rp[i];\n';assert c.count(reach)==1;c=c.replace(reach,'',1)
uni='            float uni = 1.f / (float)na;\n';assert c.count(uni)==1;c=c.replace(uni,uni+reach,1)
third='''                float r = small ? rc[a] : regrets_p[idx];
                float sig = sum > 1e-12f ? (r > 0.f ? r : 0.f) / sum : uni;
                float d = r > 0.f ? pos : neg;
                regrets_p[idx] = r * d + (val - out);
                strat_p[idx] = strat_p[idx] * ds + reach * sig;'''
assert c.count(third)==1
c=c.replace(third,'''                float r = small ? rc[a] : regrets_p[idx];
                float d = r > 0.f ? pos : neg;
                regrets_p[idx] = r * d + (val - out);''',1)
out='                out += sig * v;\n';assert c.count(out)==1
c=c.replace(out,out+'''                // Independent of the completed node value: use this action's
                // original sigma while it is already available.
                u64 idx = doff + (u64)a * nh_p + i;
                strat_p[idx] = strat_p[idx] * ds + reach * sig;
''',1)
candidate=base[:a]+c+base[z:]
assert candidate[:a]==base[:a] and candidate[candidate.index('extern "C" __global__ void up_action('):]==base[z:]
(D/'baseline.cu').write_bytes(path.read_bytes());(D/'candidate.cu').write_bytes(candidate.replace('\n','\r\n').encode('utf-8'))
(D/'candidate.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='crates/solver/src/gpu/kernels.cu',tofile='crates/solver/src/gpu/kernels.cu')),encoding='utf-8')
review={'id':'D082-action-strategy-store-scheduling','at':old.now(),'root_source_review_only':True,'proposal':'Move each unlocked own-node strategy FMA/store to its existing ascending action expectation loop after out+=sig*v. Read the unchanged hand reach before that loop. The final ordered loop updates regrets only.','source_invariants':['No new cached array, arity specialization/dispatch, loop factor, launch or alias qualifier. Existing rc/vc sizes/uses preserved.','sum, sigma, val, out, discount, regret and strategy FMA expressions and within-out action order unchanged; output CFV still stored at original end.','Locked/opponent bodies, common2/3/4/generic dispatch and all other CUDA entries remain source-identical.','Strategy writes are independent of the final node value. Actual production regrets/strategy/CFV allocations are disjoint; per-node action spans are disjoint. Data race/alias contracts must be confirmed from every actual caller and raw controls before primary timing.','Regrets are not changed until every child expectation contribution is consumed; therefore original sigma operands remain available for every action. No graph/traversal/state/stopping/save-format change.'],'counterevidence':['D038 final-code observations already share sigma registers on common2/3/4 paths; no claim of fewer common-path divisions. Potential scheduling/lifetime improvement needs actual compiled/native measurement.','Generic source avoids a duplicate sigma expression, but its incidence alone is not speed headroom. Existing E047 one-action dispatch/E024 cache removal stay rejected and are not composed.','E003 alias qualifiers already imply related disjointness facts and are not revived; all original qualifiers remain unchanged. This is an explicit store-scheduling transform without added cache/qualifier or factor.'],'novelty':'No early strategy-store/move-to-expectation transform found in scoped retained source reviews/README/ledger; current byte-exact helper retains strategy store in final regret-update loop.','resource_gate':'Actual up_action body must change, no increased registers/local/shared or reduced maxthreads/64/128/256occupancy; unchanged ABI and other8entries. No outcome-driven schedule/cache/factor rescue.','candidate_accepted':False,'source_sha256':{'baseline':old.sha(D/'baseline.cu'),'candidate':old.sha(D/'candidate.cu')}}
old.save(D/'source-review.json',review);old.save(D/'manifest.json',{'id':'E051','at':old.now(),'owned':{'crates/solver/src/gpu/kernels.cu':{'base':str(D/'baseline.cu'),'base_sha256':old.sha(D/'baseline.cu'),'candidate':str(D/'candidate.cu'),'candidate_sha256':old.sha(D/'candidate.cu')}},'source_review_sha256':old.sha(D/'source-review.json'),'production_activated':False,'compiler_native_gpu_runs':0})
H=ROOT/'runs/E051-resource';H.mkdir()
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((D/n).read_bytes())
prior=ROOT/'runs/E047-resource';probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E047','E051');(H/'probe.rs').write_text(probe,encoding='utf-8')
template=ROOT/'runs/E048-resource';script=(template/'execute.py').read_text(encoding='utf-8').replace('E048','E051').replace('len(markers)==6','len(markers)==4').replace('other7_entries_exact','other8_entries_exact');(H/'execute.py').write_text(script,encoding='utf-8')
p0=old.read(prior/'protocol.json');p1=old.read(template/'protocol.json')
p={'id':'E051-resource','at':old.now(),'status':'FROZEN_PRE_EXECUTION_NO_LAUNCH','source_manifest_sha256':old.sha(D/'manifest.json'),'changed_entries':['up_action'],'gpu_uuid':p1['gpu_uuid'],'expected_entries':p1['expected_entries'],'expected_abi':p0['expected_abi'],'rustc_command':[x.replace('E048-resource','E051-resource') for x in p1['rustc_command']],'input_sha256':{k:v for k,v in p1['input_sha256'].items() if Path(k).suffix in ['.rlib','.lib'] or Path(k).name in ['common.py','postflop_autoresearch.py','protected-main.json']},'fixed_gates':'Changed entry, exact originalABI/other8entries, no register/local/shared increase, no maxthreads/64/128/256occupancy decrease, fits limits. No numerical or speed work after any failure.'}
p['input_sha256'].update({str(x):old.sha(x) for x in [H/'execute.py',H/'probe.rs',H/'baseline.cu',H/'candidate.cu',D/'manifest.json',D/'source-review.json',ROOT/'runs/D038-next-hypothesis-source/README.md',ROOT/'runs/E003.patch']})
old.save(H/'protocol.json',p)
published={}
for directory in [D,H]:
 for src in directory.rglob('*'):
  if not src.is_file():continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
  published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);assert not any(x['id']=='E051' for x in st['experiments']);st['experiments'].append({'id':'E051','title':'Independent strategy-store scheduling','kind':'candidate','status':'running','stage':'Frozen no-launch compiler/resource gate','reason':'One store-scheduling transform; same arithmetic/order, no new array/cache/qualifier/launch. Actual disjoint production buffers must be proved before timing.','evidence':[{'label':'D082/E051 source review','url':'evidence/E051-source/source-review.json'},{'label':'E051 resource protocol','url':'evidence/E051-resource/protocol.json'}]});st.update(state='running',stage='E051 compiler/resource prerequisite',activity='Test actual compiled scheduling/resource effect before raw numerical or timing work.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'candidate_sha256':old.sha(D/'candidate.cu'),'resource_protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
