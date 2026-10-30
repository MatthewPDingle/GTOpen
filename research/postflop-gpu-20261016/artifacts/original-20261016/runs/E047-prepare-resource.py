"""Fixed one-action template dispatch; no new entry, allocation or launch."""
import difflib,json,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E047-design';D.mkdir();rel='crates/solver/src/gpu/kernels.cu';raw=(ar.REPO/rel).read_bytes();text=raw.decode('utf-8');nl='\r\n' if '\r\n' in text else '\n'
at=text.index('extern "C" __global__ void up_action(');end=text.index('// Copy the first n floats',at);part=text[at:end]
line=next(x for x in part.splitlines() if x.startswith('    if (na == 2) up_action_impl<2>'))
new=line.replace('na == 2','na == 1').replace('up_action_impl<2>','up_action_impl<1>')+nl+line.replace('    if (','    else if (',1)
assert part.count(line)==1;part2=part.replace(line,new);candidate=text[:at]+part2+text[end:]
assert candidate.replace(new,line)==text
(D/'baseline.cu').write_bytes(raw);(D/'candidate.cu').write_bytes(candidate.encode('utf-8'))
(D/'candidate.patch').write_text(''.join(difflib.unified_diff(text.splitlines(keepends=True),candidate.splitlines(keepends=True),fromfile='a/'+rel,tofile='b/'+rel)),encoding='utf-8')
census_path=ROOT/'runs/D001-action-census.log';old.pin(census_path,'9e1c4779fc7f26536edce23e214ee12431bbc024f8695be66556e4983e5b418e')
records=[json.loads(x.split('POSTFLOP_ACTION_CENSUS ',1)[1]) for x in census_path.read_text(encoding='utf-8').splitlines() if x.startswith('POSTFLOP_ACTION_CENSUS ')]
incidence=[{'fixture_id':r['fixture_id'],'action_count_histogram':r['action_count_histogram'],'one_action_fraction':r['action_count_histogram'].get('1',0)/sum(r['action_count_histogram'].values())} for r in records]
files=subprocess.check_output(['rg','--files','-g','*.cu',str(ROOT/'runs')],text=True).splitlines();prior_hashes={p:old.sha(p) for p in files if not Path(p).is_relative_to(D)};assert old.sha(D/'candidate.cu') not in prior_hashes.values()
hist=subprocess.run(['git','log','--all','--format=%H %s','-G','up_action_impl<1>','--','crates/solver/src/gpu'],cwd=ar.REPO,capture_output=True,text=True);assert hist.returncode==0 and not hist.stdout.strip()
A=ROOT/'runs/D077-one-action-source';A.mkdir()
old.save(A/'report.json',{'id':'D077-one-action-source','at':old.now(),'status':'go_one_fixed_no_launch_resource_probe','root_review_only':True,'source_sha256':{str(ar.REPO/p):old.sha(ar.REPO/p) for p in [rel,'crates/solver/src/gpu/mod.rs','crates/solver/src/gpu/plan.rs']},'mechanism':'In the existing up_action entry, dispatch na==1 to the existing byte-unchanged up_action_impl<1>, before the current2/3/4/generic cases. No independent entry/list/launch/plan or hand-loop change.','source_exactness':'All helper arithmetic, branch bodies and child ordering remain byte-identical. New compile-time arity may change generated floating instructions, so actual original-versus-candidate raw controls remain mandatory. Arbitrary arity fallback unchanged.','historical_incidence':incidence,'incidence_sha256':old.sha(census_path),'incidence_limits':'Old retained structural work counts, not current latency shares, removable work or a projected speed gain. No new census.','novelty':{'unique_cuda_bytes':True,'preserved_cuda_files_checked':len(prior_hashes),'local_all_ref_up_action_impl_1_history':hist.stdout,'difference_from_prior':'E005/E014 added separate2/3 entries with list partition/new launches. E042 unrolled the own-unlocked hand loop. This adds only existing-entry compile-time arity1 routing. Preserved patch/readme search found no prior up_action_impl<1>.'},'possible_costs':['Extra uniform dispatch branch and code/NVRTC/JIT footprint; full-cycle timing must include them.','Kernel-wide registers/local storage can rise despite a smaller1-action case; resource gate comes first.'],'no_new_host_device_pinned_event_stream_graph_allocation':True,'predeclared_gates':['Changed up_action, same exact PTX ABI, other8 entries byte-exact.','No register/local/shared increase, thread-limit reduction or theoretical64/128/256 occupancy decrease.','If resource passes, fixed direct originalGPU raw corpus before full solver timing.','Current1%/strict fixture policy; separately frozen16pair/broader/holdout/cumulative/resource qualification before adoption.'],'no_arity_or_factor_sweep_after_outcome':True,'source_activated':False,'compiler_native_executions':0,'performance_measured':False,'candidate_accepted':False})
old.save(D/'manifest.json',{'id':'E047-cuda-source','at':old.now(),'accepted_cuda_sha256':old.sha(D/'baseline.cu'),'candidate_cuda_sha256':old.sha(D/'candidate.cu'),'patch_sha256':old.sha(D/'candidate.patch'),'exact_reversal':True,'source_audit_sha256':old.sha(A/'report.json'),'only_changed_entry':'up_action','source_activated':False})
HERE=ROOT/'runs/E047-resource';HERE.mkdir();prior=ROOT/'runs/E043-resource-r2'
for n in ['baseline.cu','candidate.cu']:(HERE/n).write_bytes((D/n).read_bytes())
(HERE/'probe.rs').write_text((prior/'probe.rs').read_text(encoding='utf-8').replace('E043','E047').replace('down_action','up_action'),encoding='utf-8')
execute=(prior/'execute.py').read_text(encoding='utf-8').replace('E043','E047').replace('down_action','up_action')
needle=" report={'id':'E047-resource'";assert execute.count(needle)==1
execute=execute.replace(needle," gates['up_action_abi_exact']=be['up_action'].split('{',1)[0]==ce['up_action'].split('{',1)[0]\n"+needle)
(HERE/'execute.py').write_text(execute,encoding='utf-8')
p=old.read(prior/'protocol.json');p.update(id='E047-resource',at=old.now(),source_manifest_sha256=old.sha(D/'manifest.json'));p['rustc_command']=[x.replace('E043-resource-r2','E047-resource') for x in p['rustc_command']]
deps={n:h for n,h in p['input_sha256'].items() if '/build/' in n.replace('\\','/')};refs=[HERE/'baseline.cu',HERE/'candidate.cu',HERE/'probe.rs',HERE/'execute.py',D/'manifest.json',A/'report.json',census_path,ar.REPO/'tools/postflop_autoresearch.py',ROOT/'runs/small-gain-confirmation-plan/common.py'];p['input_sha256']=deps|{str(x):old.sha(x) for x in refs}
p['resource_gates']=['Only up_action body changes; other8 bodies and exact up_action PTX header unchanged.','No higher registers/local/static shared, lower max threads or64/128/256 theoretical occupancy; default limits fit.','No numerical kernel or solver execution. No factor/arity sweep after outcome.'];old.save(HERE/'protocol.json',p)
published={}
for directory in [D,A,HERE]:
 for src in directory.iterdir():
  if not src.is_file():continue
  key=directory.name+'/'+src.name;dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);raw=src.read_bytes();assert not dst.exists();dst.write_bytes(raw)
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==raw
  published[key]=old.sha(src)
old.save(HERE/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published,'kernel_launches':0})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(ar.STATUS);assert not any(x['id']=='E047' for x in s['experiments']);s['experiments'].append({'id':'E047','at':old.now(),'title':'Specialize existing one-action training dispatch','kind':'candidate','status':'preparing','correctness':'pending','stage':'Frozen no-launch resource gate','reason':'Existing unchanged template gets compile-time arity1 routing. No new entry/list/allocation/launch; extra dispatch/code-size costs unproven. Resources and raw GPU correctness precede timing.','evidence':[{'label':'D077 source and history audit','url':'evidence/D077-one-action-source/report.json'},{'label':'E047 fixed resource protocol','url':'evidence/E047-resource/protocol.json'}]});s.update(state='running',stage='E047 no-launch resource probe',activity='Check unchanged one-action template routing before numerical or solver work.',updated_at=ar.now());ar.atomic_json(ar.STATUS,s)
print(json.dumps({'protocol_sha256':old.sha(HERE/'protocol.json'),'manifest_sha256':old.sha(D/'manifest.json'),'candidate_sha256':old.sha(D/'candidate.cu'),'historical_incidence':incidence}),flush=True)
