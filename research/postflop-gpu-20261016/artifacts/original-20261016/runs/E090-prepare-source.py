import sys,json,shutil,difflib,urllib.request,subprocess
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
D=R/'runs/D141-cfv-width';q=old.read(D/'report.json');assert q['status']=='pass_retained_CFV_width_model_admit_one_host_prototype'and len(q['cases'])==12
x=old.read(D/'execution/model.exit.json');assert x['returncode']==0 and x['error']is x['cleanup']is None
S=R/'runs/E090-source';S.mkdir(exist_ok=False);rel='crates/solver/src/gpu/mod.rs';raw=(old.REPO/rel).read_bytes();text=raw.decode()
before='let nh_max = self.nh_max;';after='let nh_max = nh_p;'
assert text.count(before)==2
candidate=text.replace(before,after);assert candidate.replace(after,before)==text
(S/'baseline.rs').write_bytes(raw);(S/'candidate.rs').write_bytes(candidate.encode())
(S/'mod.rs.patch').write_bytes(''.join(difflib.unified_diff(text.splitlines(True),candidate.splitlines(True),fromfile='accepted/gpu/mod.rs',tofile='E090/gpu/mod.rs')).encode())
scope='Only the existing local CFV stride in paired_sweep and eval_up becomes nh_p. All original kernel bytes, ordered float math, logical hand counts, CFV slot IDs and lifetimes, level/worklists, reach/learning state, allocated bytes/budget, root staging, graphs and save behavior remain. Physical scratch row addresses differ per traverser.'
old.save(S/'source-review.json',{'at':old.now(),'scope':scope,'source_reverse_exact':True,'D141_report_sha256':old.sha(D/'report.json'),'production_statements_changed':2,'new_persistent_fields':0,'device_allocation_formulas_changed':False,'kernel_bytes_changed':False,'root_contract':'Root CFV slot remains zero, root downloads remain first nh[p] floats. d_eval_roots offsets and allocation keep self.nh_max; only up-kernel stride arguments use nh_p.','lifetime_contract':'Every full up pass computes all logical rows from the current traverser before their consumers. Within-player BR/average terminal reuse retains that same stride. Switching players runs a full producer pass; no incoming other-player CFV bytes are required. Actual raw GPU/controller checks remain necessary.','risks':'Tighter row addresses can change cache-line sharing and coalescing, scheduling, performance or expose missed consumer assumptions. Smaller address envelope does not reduce allocated VRAM. No no-tradeoff claim from source/model.','distinct_from_closed':'No E025 padding or capacity change; no E076 row-ID/lifetime/coloring/alias change; no E018/E039 metadata translation. Same row map and allocation, per-traverser unpadded spacing only.','required':'Real full logical CFV/raw physical guard images and whole learning/reach equivalence versus immutable baseline, eager/graphs/evaluation/warm/locks/F32/compressed/algorithms/continuation. Fresh full builds and unchanged whole-solve1%/strictfixture/fresh16/broad/material/holdout/cumulative before adoption.'})
old.save(S/'manifest.json',{'id':'E090','at':old.now(),'owned':{rel:{'base':str(S/'baseline.rs'),'candidate':str(S/'candidate.rs')}},'candidate_owned_sha256':{rel:old.sha(S/'candidate.rs')},'scope':scope,'source_activated':False,'candidate_accepted':False,'previous_accepted':'E080'})
pub=[]
for folder in [D,S]:
 for p in folder.rglob('*'):
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.patch','.log']:continue
  key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
old.save(S/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'GPU_executions':0,'source_activated':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='D141')
 x.update(status='measured',correctness='retained_model_pass',stage='CPU model passed; GPU controls pending',reason='All 12 retained layouts passed 124,239,154 producer/dependency/permutation/row-boundary checks. Allocations and row IDs stay unchanged. This is a CPU model, not a GPU numerical or speed result.')
 x['evidence'].append({'label':'Full retained graph and row model','url':'evidence/D141-cfv-width/report.json'})
 s['experiments'].append({'id':'E090','at':old.now(),'title':'Use each traverser hand count for CFV row spacing','status':'planned','stage':'Real GPU control preparation','correctness':'pending','accepted':False,'reason':'Two host stride assignments only; kernels, allocation sizes and row map unchanged. D141 model passed. Real GPU compatibility and speed remain unproven.','evidence':[{'label':'Exact host scope and lifetime contract','url':'evidence/E090-source/source-review.json'},{'label':'Candidate source identities','url':'evidence/E090-source/manifest.json'}]})
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E090',stage='E090 real GPU control preparation',activity='D141 model passed on all 12 layouts. Test a two-line per-traverser CFV stride change against the original GPU engine. No new accepted speedup; E080 remains live.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(S/'manifest.json'),flush=True)
