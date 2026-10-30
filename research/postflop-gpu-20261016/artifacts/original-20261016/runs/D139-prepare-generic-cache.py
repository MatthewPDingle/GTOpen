import sys,ast,re,difflib,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
D,S,H=[R/'runs'/x for x in ['D139-generic-cache','E088-source','E088-resource']]
assert not any(x.exists()for x in [D,S,H])
for x in [D,S,H]:x.mkdir()
history=[]
for cmd in [
 ['git','log','--all','--oneline','-G',r'bool small = NA|generic.{0,30}(uncach|cache)|register.cache.{0,30}generic','--','crates/solver/src/gpu/kernels.cu'],
 ['rg','-n','-i',r'generic.{0,35}(uncach|cache)|cache.{0,35}generic|small.{0,15}NA','research/postflop-gpu-20261016/experiments.md'],
 ['rg','-l',r'bool small = NA|small = \(?NA != 0|generic.{0,30}uncach',str(R/'runs'),'-g','*.cu'],
]:
 x=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
 assert x.returncode in [0,1];history.append({'command':cmd,'returncode':x.returncode,'stdout':x.stdout,'stderr':x.stderr})
rel='crates/solver/src/gpu/kernels.cu';raw=(old.REPO/rel).read_bytes();t=raw.decode()
a=t.index('__device__ __forceinline__ void up_action_impl(');b=t.index('extern "C" __global__ void up_action(',a)
part=t[a:b];assert part.count('bool small = na <= 8;')==1
before='bool small = na <= 8;';after='bool small = NA != 0;'
changed=part.replace(before,after,1);candidate=t[:a]+changed+t[b:]
assert candidate.replace(after,before,1)==t
old.save(D/'history.json',{'at':old.now(),'bounded_local_history':history,'ledger_sha256':old.sha(old.REPO/'research/postflop-gpu-20261016/experiments.md'),'novelty_scope':'Local all-ref and retained CUDA/source ledger only; no semantic/global novelty claim. D058 mode split remains parked; up_action_eval old traced family41.78ms on two-tone does not justify that narrow route. New generic training cache removal is distinct from E074 noinline call: no wrapper/call/dispatch/arity split and no closed hunk composed.','last_primary_baseline':'B289'})
for name,data in [('baseline.cu',raw),('candidate.cu',candidate.encode())]:
 (S/name).write_bytes(data);shutil.copyfile(S/name,H/name)
(S/'kernels.cu.patch').write_bytes(''.join(difflib.unified_diff(t.splitlines(True),candidate.splitlines(True),fromfile='accepted/kernels.cu',tofile='E088/kernels.cu')).encode())
scope='Only up_action_impl cache predicate changes from na<=8 to compile-time NA!=0. Common2/3/4 instantiations retain original caches; arbitrary-menu generic uses existing uncached memory-read branches. No arithmetic/expression/order/address/threshold/lock/opponent/down/eval/host/layout/ABI/graph/precision/quality/save change.'
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'source_reverse_exact':True,'numeric_obligations':'For common NA2/3/4, old predicate is always true; candidate true. Generic changes cache only at actioncounts1,5,6,7,8 (wrapper dispatch otherwise2/3/4; >8 alreadyuncached). Regrets are unchanged throughout sum/sigma loops; strategy writes are disjoint. During final ascending regret updates, prior action writes cannot alias later action reads. Child CFV rows remain unchanged until final parent CFV write; actual plan/direct-control child-parent disjointness is required. Thus existing reread branches consume same bits and execute identical floating operations/order. No atomic/read-race/fault alias guarantee for malformed inputs.','compiler_hypothesis':'Dynamic rc[8]/vc[8] indexing may allocate localmemory in generic path. Removing that cache can trade local stores/reads for extra global loads and alter common physical registers or scheduling. Require complete local removal on actual120 and PTXlocal-memory absence120/75 before numerical work; no speed inferred.','distinct_from_closed':'E074 modifies private generic call boundary while preserving original cache; this changes cache policy without any new call/helper/entry/dispatch or forced parameter. E064localactionindices,E085streamingstores,E087staging are absent.','primary_sources':['https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/writing-cuda-kernels.html'],'required':'Resource/codegen prerequisites, original819raw up_action controls with whole mutable/immutable/guards, full builds/ordinary units, original same-quality complete-solve1%strictfixture screen, separatefresh16/broad/material/capacity/holdout/cumulative beforeadoption.'})
old.save(S/'manifest.json',{'id':'E088','at':old.now(),'owned':{rel:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')}},'candidate_owned_sha256':{rel:old.sha(S/'candidate.cu')},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})
prior=R/'runs/E085-resource-r2';P0=old.read(prior/'protocol.json')
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E085','E088')
(H/'probe.rs').write_bytes(probe.encode())
code=(prior/'execute.py').read_text(encoding='utf-8').replace('E085','E088').replace('pass_compiled_strategy_streaming_prerequisites','pass_compiled_generic_uncached_prerequisites')
needle="gates[arch+':streaming_store_emitted']=bt.count('st.global.cs.f32')==0 and ct.count('st.global.cs.f32')>=1"
assert code.count(needle)==1
code=code.replace(needle,"gates[arch+':local_storage_removed']=('.local ' in bt or '.local\\t' in bt) and not ('.local ' in ct or '.local\\t' in ct)")
needle='passed=all(gates.values());report=';assert code.count(needle)==1
code=code.replace(needle,"gates['actual_local_storage_removed']=b['local_bytes_per_thread']>0 and c['local_bytes_per_thread']==0\n"+needle)
code=code.replace('strategy-value/store-ownership correctness','generic reread/cache numeric correctness')
ast.parse(code);(H/'execute.py').write_bytes(code.encode())
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
files=[Path(__file__),C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for folder in [D,S,H]for p in folder.iterdir()if p.is_file()]]
P={'id':'E088-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE','rustc_command':[x.replace('E085-resource-r2','E088-resource')for x in P0['rustc_command']],'input_sha256':deps|{str(p):old.sha(p)for p in files},'gpu_uuid':P0['gpu_uuid'],'expected_entries':P0['expected_entries'],'target_kernel':'up_action','expected_parameters':20,'resource_gates':'Other8normalizedentries and20parameterABI exact120/75; up_actionPTXlocalstorage absent bothtargets and actual120localbyteszero frompositive baseline. No static/dynamicshared/maxthread/contextstack/128threadresidency regression; fixed64/128/256legal/positive.','scope':'OneRustcompiler,one resource-onlyprocess,fourNVRTCcompiles120/75; no application kernel,solve/performance orproduction sourceactivation.','failure_policy':'Close this exact generic-uncached predicate on actual codegen/resource/numerical/performance/materialfailure. No cache-size/arity/subset/helper/call/placement/threshold/width/source-scope variant or extra samples rescue. Original errors retained; reader-only bookkeeping can replay unchanged data.','candidate_accepted':False}
assert all('E085'not in x for x in P['rustc_command'])
old.save(H/'protocol.json',P)
pub=[]
for folder in [D,S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']in ['D139','E088']for x in s['experiments'])
 s['experiments'] += [{'id':'D139','at':old.now(),'title':'Generic action cache source scout','status':'measured','correctness':'source_only','accepted':False,'reason':'Target dynamic localarrays in generic training action path. Eval mode split remains parked. Source/read-lifetime obligations retained; compiled mechanism unproven.','evidence':[{'label':'Scoped source/history audit','url':'evidence/D139-generic-cache/history.json'}]},{'id':'E088','at':old.now(),'title':'Use existing uncached generic action path','status':'running','stage':'Compiled local-storage prerequisite','correctness':'pending','accepted':False,'reason':'Retain2/3/4registercaches, useoriginaluncachedbranches forgeneric. Requirecompiledlocalstorage removal first; no speed result.','evidence':[{'label':'Exact source and read lifetime','url':'evidence/E088-source/source-review.json'},{'label':'Frozen compiled controls','url':'evidence/E088-resource/protocol.json'}]}]
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E088',stage='E088 compiled storage prerequisite',activity='Test removing dynamically indexed generic action caches; same ordered arithmetic, original uncached branches. No new speed result; E080 remains live.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(D/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'resource_protocol_sha256':old.sha(H/'protocol.json'),'new_native_processes':0})
old.custody();print(old.sha(H/'protocol.json'),flush=True)
