import sys,json,re,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=68*1024**3 and shutil.disk_usage('T:\\').free>=50*1024**3
H=R/'runs/D141-cfv-width';H.mkdir(exist_ok=False);A=R/'runs/D092-action-arity-order'
old.pin(A/'accepted-plan.rs',old.BASE['crates/solver/src/gpu/plan.rs'])
history=[];count=0
for p in (R/'runs').rglob('*.rs'):
 t=p.read_text(encoding='utf-8',errors='replace')
 if 'fn paired_sweep'not in t:continue
 count+=1
 for x in re.finditer(r'let\s+nh_max\s*=\s*([^;]+);',t):
  if x.group(1).strip()!='self.nh_max':history.append({'path':str(p),'expression':x.group(1)})
assert all(x['expression']=='NH_MAX as i32'and'E035'in x['path']for x in history)
q=subprocess.run(['git','log','--all','--oneline','-G',r'let nh_max = self.nh\[','--','crates/solver/src/gpu/mod.rs'],cwd=old.REPO,text=True,capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW);assert q.returncode==0 and not q.stdout.strip()
old.save(H/'history.json',{'at':old.now(),'GpuSolver_sources_scanned':count,'non_default_stride_hits':history,'local_all_ref_query':q.args,'local_all_ref_matches':q.stdout,'scope':'Bounded local source/history audit; no exhaustive semantic or remote novelty claim. Existing E025 pads every row and changes allocations/admission; E076 changes node-to-row IDs via lifetime sharing. This proposal preserves all row IDs and allocations and only passes nh[p] as the five up-kernel row-stride argument. No padding, coloring, sharing, fusion or closed hunk is composed.','declined_other_lead':'Chance child-to-slot resolution overlaps closed E018/E039 and stays declined.'})
sources=[old.REPO/'crates/solver/src/gpu'/n for n in ['mod.rs','kernels.cu','plan.rs','continuation.rs','continuation_storage.rs','continuation_paging.rs','continuation_capacity.rs']]
files=[Path(__file__),R/'runs/D141-cfv-width-model.py',A/'report.json',A/'field-schema.json',A/'accepted-plan.rs',*[A/'execution'/f'case-{i:02d}.bin'for i in range(12)],*sources,C/'common_e080_live.py',C/'protected-main.json',H/'history.json']
for p in files:assert p.is_file(),p
old.save(H/'protocol.json',{'id':'D141','at':old.now(),'status':'FROZEN_PRE_RETAINED_DATA_MODEL','input_sha256':{str(p):old.sha(p)for p in files},'raw_reservation_bytes':2*1024**3,'cases':12,'scope':'Decode baseline arms of the 12 accepted D092 full metadata dumps. Check all row intervals, actual action/chance consumers and old writer ordering. CPU source/integer model only: no new plan build, compiler, CUDA context, kernel, solver, timing or source activation.','fixed_checks':['All actual CFV row IDs are in range, root is zero, every row is written during each full up sweep.','Every action/chance read sees its exact child as last writer under unchanged per-level fold/show/chance/action schedule. Same-level outputs cannot alias any input or other output; persistent terminal rows are disjoint.','BR full producer pass followed by average pass with retained terminals has identical row-writer identities; a full pass does not need incoming CFV bytes from a prior player.','For every row and each p, [row*nh[p],(row+1)*nh[p]) is injective, same-row/same-hand aliases exactly match old spacing, original allocation cfv_blocks*nh_max bounds all accesses; hand permutations stay in nh[p].','Root extraction/evaluation-root offsets remain at original zero/fixed nh_max spacing; no allocation/admission/payload or saved layout changes.'],'proposal':'Only two existing local assignments in paired_sweep and eval_up pass nh_p instead of self.nh_max as CFV stride. Every original kernel/float expression/count/schedule/slot map/learning and reach allocation/save remains. Shader code/compiled resources identical; changing row spacing still requires real GPU raw semantic/guard/state/graph tests and full performance/material qualification.','admission':'Require all 12 exact finite models, positive hand counts and at least one canonical asymmetric layout. This only admits one off-tree host prototype; no speed/capacity/no-tradeoff claim follows from narrower address envelopes. Keep 1%/strictfixture/fresh16/broad/material/holdout/fresh-original gates unchanged.','failure_policy':'Close exact per-traverser unpadded CFV stride form on real structural/numerical/performance/material failure; no padding/factor/subset/helper/source-scope/placement variant or extra samples rescue. Reader-only bookkeeping may replay retained observations.','candidate_accepted':False})
pub=[]
for p in [H/'history.json',H/'protocol.json',R/'runs/D141-cfv-width-model.py',Path(__file__)]:
 key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
 pub.append(key)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'retained_metadata_cases_decoded':0,'protocol_sha256':old.sha(H/'protocol.json')})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);assert not any(x['id']=='D141'for x in s['experiments'])
 s['experiments'].append({'id':'D141','at':old.now(),'title':'CFV rows sized to the current traverser','status':'running','stage':'Retained graph and address model','correctness':'pending','accepted':False,'reason':'Check using each player hand count as scratch-row stride while retaining all slot IDs, allocation sizes, kernel arithmetic and schedule. No GPU or speed claim.','evidence':[{'label':'Frozen row/dependency analysis','url':'evidence/D141-cfv-width/protocol.json'}]})
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='D141',stage='CFV row-width dependency analysis',activity='Check every retained action/chance dependency and row boundary before a per-player CFV stride prototype. E080 remains live; accepted measured gain is unchanged.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(old.sha(H/'protocol.json'),flush=True)
