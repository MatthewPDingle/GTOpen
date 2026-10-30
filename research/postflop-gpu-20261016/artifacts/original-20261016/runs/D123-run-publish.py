"""Own and publish the single frozen CPU initialization component screen."""
from pathlib import Path
import json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/D123-node-array-initialization';P=old.read(H/'protocol.json');M=R/'runs/D123-manager';old.custody();assert not (R/'gpu-run.lock').exists()and not M.exists();M.mkdir()
for p,h in P['input_sha256'].items():old.pin(p,h)
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'protocol.json')],M,'cpu',old.env(),1800)
q=old.read(H/'report.json');e=old.read(M/'cpu.exit.json');assert e['returncode']==0 and e['error']is e['cleanup']is None
assert len(q['cases'])==12 and q['all53_values_capacities_structs_match_retained_accepted']and q['original_and_candidate_plan_tests_pass']and q['excluded_samples']==[]and q['extension_runs']==0 and q['GPU_or_solver_executions']==0
old.custody();assert not (R/'gpu-run.lock').exists()
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[]
for folder in [H,H/'build',H/'execution',M]:
 for p in folder.iterdir():
  if not p.is_file()or p.suffix not in ['.py','.rs','.json','.patch','.log']:continue
  key=(H.name+'-'+folder.name if folder in[H/'build',H/'execution']else folder.name)+'/'+p.name
  pub.append(publish(p,key))
pub.append(publish(Path(__file__),H.name+'/run-publish.py'));old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_owned_children_terminal':True,'all_bulk_raw_metadata_retained_physically_on_S':True})
admit=q['admit_one_integrated_trial'];saving=q['canonical_sum_CPU_plan_saving_ms']
reason=f"All12 compiled metadata cases and both plan tests pass; every53-field value/capacity/struct matches accepted data. Fixed CPU-plan median saving across canonical cases: {saving:.6f}ms; prospective screening budget:95.825124ms. "
reason+=('Component screen admits one integrated trial only; no complete-solve speed or material conclusion.'if admit else'Budget not met; close this direct-append initialization form without extra samples or source/helper/initialization/threshold variants. No GPU/full-solve speed measurement.')
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);row=next(x for x in s['experiments']if x['id']=='D123');row.update(status='measured',correctness='All53 CPU metadata fields/capacities/structs exact',stage='One integrated trial admitted'if admit else'Closed: CPU component saving budget missed',reason=reason,accepted=False,updated_at=old.now());row['evidence'].append({'label':'Complete metadata and CPU component result','url':'evidence/D123-node-array-initialization/report.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing a metadata initialization trial'if admit else'Investigating the next GPU optimization',activity=reason+' Accepted/live E051 cumulative gain12.44% unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D123 direct scalar-array initialization component screen'not in raw
canon=[{k:q['cases'][i][k]for k in ['case','board','baseline_median_ms','candidate_median_ms','saving_of_medians_ms','median_paired_saving_ms']}for i in [2,6,10]]
entry=f'''

### D123 direct scalar-array initialization component screen

Previous goal turn completed D122/E076 and rejected CFV lifetime sharing after0.5218589436% aggregate slowdown and rainbow1.2403234098% slower2/3. Current accepted162/main163/live/protected2PTX, idle live APIs and last primary B243 revalidated. Retained D087/D088 traces still show substantial constructor/readback host work, but do not make any gap a removable bound. Graph-launch, zero-scan/provenance/encoder, CFV, parallel planner and closed kernel families were not reopened. Bounded local all-ref plan history found no direct scalar-vector construction form.

D123 changes only the eight per-node scalar array constructions in an off-tree accepted plan copy: reserve exact n then append every final value in the original serial node order, including unchanged conditional offset/u64MAX and chance-divisor/positive-zero branches. Safe Rust; no new unsafe/initialization omission, fields, array values/types/capacities, worklist/CFV layout, float cast/divide expressions, per-player arena order, CUDA/kernel ABI, quality or save behavior. Candidate SHA {old.sha(H/'candidate-plan.rs')}. Source syntax does not establish removed emitted instructions, allocator internal work or speed.

Frozen protocol {old.sha(H/'protocol.json')} before either compiler/native process: one probe compiler, one unit compiler, one two-test CPU plan process and exactly12 fixture/iso/full processes. Each case runs2 warmup pairs,9 fixed alternating measured CPU-plan pairs and1 untimed full raw pair. No production activation/GPU kernels/solve/full-cycle timing. All53 fields and complete vector-capacity/struct geometry match each other and retained accepted D092 data. {sum(x['root_checks']for x in q['cases'])} root framing/full-array checks, {sum(x['baseline_words']for x in q['cases'])} baseline encoded words; {sum(x['raw_bytes']for x in q['cases'])} raw bytes retained onS. Native and separate raw comparisons are finite controls; root is not external independent review.

Prospective component gate is95.825124ms saved across canonical cases2/6/10, with nonnegative median and median-paired savings in every canonical case. Its reference is1% of the preserved9582.5124ms accepted E051 complete-suite median, a budgeting constant only: no historical sample pooling, necessary-condition/hardware-headroom or speed claim. Canonical results {json.dumps(canon,separators=(',',':'))}. Sum saved {saving:.10f}ms; status {q['status']}. {reason} Every observation retained; no exclusions/extensions or timing rescue.

All compilers/owned native children terminal0, source never activated, accepted162/main163/live/protected2PTX exact. {len(pub)} published code/protocol/report/log artifacts HTTP byte verified. No allocator/host/GPU peak/capacity/responsiveness or complete-solve gain established. No new E077 source or primary IDs created. Accepted/deployed E051 cumulative12.4372274192% and last primary B243 unchanged. Goal active; next action {'one integrated trial with all original complete-cycle and broader gates'if admit else'a distinct optimization mechanism; this initialization form is closed'}.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: screen exact planner array initialization costs','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':q['status'],'canonical_sum_CPU_plan_saving_ms':saving,'admit_one_integrated_trial':admit,'published_files':len(pub),'accepted_gain_unchanged':True}),flush=True)
