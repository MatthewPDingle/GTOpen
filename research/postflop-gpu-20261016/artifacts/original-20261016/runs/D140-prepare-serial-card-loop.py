import sys,ast,re,difflib,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
D,S,H=[R/'runs'/x for x in ['D140-serial-card-loop','E089-source','E089-resource']]
assert not any(x.exists()for x in [D,S,H])
sources=[];hits=[]
for p in (R/'runs').rglob('*.cu'):
 t=p.read_text(encoding='utf-8',errors='replace');a=t.find('extern "C" __global__ void up_show(')
 if a<0:continue
 b=t.find('extern "C" __global__ void ',a+20);part=t[a:b if b>=0 else len(t)]
 sources.append({'path':str(p),'sha256':old.sha(p)})
 if '#pragma'in part:hits.append({'path':str(p),'lines':[x.strip()for x in part.splitlines()if'#pragma'in x]})
assert not hits,'Matching showdown pragma requires attribution review before preparation'
commands=[]
for cmd in [
 ['git','log','--all','--oneline','-G','unroll','--','crates/solver/src/gpu/kernels.cu'],
 ['rg','-n','-i',r'unroll|fold.reduction candidate|generic action cache','research/postflop-gpu-20261016/experiments.md'],
]:
 x=subprocess.run(cmd,cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);assert x.returncode in [0,1]
 commands.append({'command':cmd,'returncode':x.returncode,'stdout':x.stdout,'stderr':x.stderr})
for p in [D,S,H]:p.mkdir()
old.save(D/'history.json',{'at':old.now(),'bounded_local_history':commands,'retained_up_show_sources':sources,'show_pragma_hits':hits,'novelty_scope':'400retainedCUDAup_showbodies plus all-local-ref/ledger scout. No matching showdown pragma; bounded textual audit, not exhaustive semantic/remote novelty. Distinct from E042up_actionhandloop2xunroll, E077selectiveprefix, E084firstcardcache; no closed hunk composed. E019foldshuffle/E024genericcache remainclosed.','previous_goal_turn':'progress:E087executedandclosed','this_turn':'D139/E088duplicateguardthennewsource/codegenmechanism'})
rel='crates/solver/src/gpu/kernels.cu';raw=(old.REPO/rel).read_bytes();base=raw.decode();nl='\r\n'if b'\r\n'in raw else'\n'
before='            for (u32 t = c0; t < c1; t++) {'
after='            #pragma unroll 1'+nl+before
assert base.count(before)==1;candidate=base.replace(before,after,1);assert candidate.replace(after,before,1)==base
for n,data in [('baseline.cu',raw),('candidate.cu',candidate.encode())]:(S/n).write_bytes(data);shutil.copyfile(S/n,H/n)
(S/'kernels.cu.patch').write_bytes(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='accepted/kernels.cu',tofile='E089/kernels.cu')).encode())
scope='Only #pragma unroll1 on existing up_show inner serial card-correction loop. Original two-card/ascending-position iterations, selected loads/predicates, all float expressions and accumulator order, prefix/card cache, barriers/shared/ABI/host/launch/graph/precision/quality/save unchanged.'
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'source_reverse_exact':True,'hypothesis':'Suppress compiler loop replication for serial card corrections to reduce generated instruction body/working resources. Compiled smaller PTX is a prerequisite only; no measured instruction-cache pressure/SASS/dynamic memory/cycle attribution. Reduced replication may lose load overlap and hurt throughput.','numeric_contract':'Directive leaves loopbound/torder/operandarrays,tot/lower/higheraccumulation exactlysourceidentical. Compiler still owns scheduling; require original/candidate full GPU float/immutable/guard comparisons, including nonfinite and rounding witnesses. No reordering/reassociation/precision/FTZ/fastmath/tolerance change.','separation':'E042unroll2 targets own unlocked up_action hand-stride loop. This targets code replication of a serial conditional card-correction walk in up_show; no hand unroll, caches, fused producers, selectiveprefix, offset widths or previous candidate hunk.','primary_sources':['https://docs.nvidia.com/cuda/archive/12.9.1/cuda-c-programming-guide/index.html#pragma-unroll'],'required':'Other8entries/27ABI exact120/75; targetentry strictlysmaller bothPTXtargets; unchangedbarrier count; noactual local/shared/limits/defaultresidency/stackregression. Then full1820rawGPUcontrolpairs,ordinaryunits/fullcomplete-solve1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative beforeadoption.'})
old.save(S/'manifest.json',{'id':'E089','at':old.now(),'owned':{rel:{'base':str(S/'baseline.cu'),'candidate':str(S/'candidate.cu')}},'candidate_owned_sha256':{rel:old.sha(S/'candidate.cu')},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})
prior=R/'runs/E084-resource';P0=old.read(prior/'protocol.json')
(H/'probe.rs').write_bytes((prior/'probe.rs').read_text(encoding='utf-8').replace('E084','E089').encode())
code=(prior/'execute.py').read_text(encoding='utf-8').replace('E084','E089').replace('pass_compiled_first_card_total_prerequisites','pass_compiled_serial_card_loop_prerequisites')
needle='passed=all(gates.values());report=';assert code.count(needle)==1
add="""for arch in ['compute_120','compute_75']:
    bt,ct=tables['baseline',arch]['up_show'],tables['candidate',arch]['up_show']
    gates[arch+':target_PTX_body_smaller']=len(ct)<len(bt)
    gates[arch+':CTA_barrier_sites_exact']=bt.count('bar.sync')==ct.count('bar.sync')
"""
code=code.replace(needle,add+needle,1).replace('ordered-card-sum/synchronization correctness','serial-card-loop numerical correctness')
ast.parse(code);(H/'execute.py').write_bytes(code.encode())
deps={p:h for p,h in P0['input_sha256'].items()if Path(p).suffix in ['.rlib','.rmeta','.lib','.dll']}
files=[Path(__file__),C/'common_e080_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[p for folder in [D,S,H]for p in folder.iterdir()if p.is_file()]]
P={'id':'E089-resource','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_RESOURCE_PROBE','rustc_command':[x.replace('E084-resource','E089-resource')for x in P0['rustc_command']],'input_sha256':deps|{str(p):old.sha(p)for p in files},'gpu_uuid':P0['gpu_uuid'],'expected_entries':P0['expected_entries'],'target_kernel':'up_show','expected_parameters':27,'resource_gates':'Other8normalizedentries and27parameterABI exact120/75; up_showentrystrictlysmallerandbar.syncsitesexactboth. Actual120local/static/dynamicshared/maxthreads/default128residency/contextstacknotworse; all64/128/256legalpositive.','scope':'OneRustcompiler,one resource-onlyprocess,fourNVRTCcompiles120/75; no application kernel,solve/performance orproduction sourceactivation.','failure_policy':'Close exact pragmaunroll1 serial up_showcardcorrection form on actual codegen/resource/numerical/performance/materialfailure. No factor/loop/helper/subset/placement/threshold/width/source-scope variant or extra samples rescue. Reader-only bookkeeping can replay retained observations.','candidate_accepted':False}
old.save(H/'protocol.json',P)
pub=[]
for folder in [D,S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key=folder.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']in ['D140','E089']for x in s['experiments'])
 s['experiments'] += [{'id':'D140','at':old.now(),'title':'Serial showdown card-loop replication scout','status':'measured','correctness':'source_only','accepted':False,'reason':'No showdown pragmas in400retainedsources; all-local-ref/history scopedaudit. Examinecode-replicationhypothesis, no speed inference.','evidence':[{'label':'Bounded history and retained source hashes','url':'evidence/D140-serial-card-loop/history.json'}]},{'id':'E089','at':old.now(),'title':'Keep serial showdown corrections in one loop','status':'running','stage':'Compiled body-size prerequisite','correctness':'pending','accepted':False,'reason':'Onepragmaunroll1 on originalserialcardwalk. RequireactualPTXbodysmaller/resourcepass; orderedmath/sourceotherwiseexact. No speed result.','evidence':[{'label':'Source and arithmetic contract','url':'evidence/E089-source/source-review.json'},{'label':'Frozen resource prerequisite','url':'evidence/E089-resource/protocol.json'}]}]
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E089',stage='E089 compiled serial-loop prerequisite',activity='Test suppressing serial showdown loop replication; same original floating recurrence and inputs. Compiled resources and speed unproven. E080 stays live.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(D/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'resource_protocol_sha256':old.sha(H/'protocol.json'),'new_native_processes':0})
old.custody();print(old.sha(H/'protocol.json'),flush=True)
