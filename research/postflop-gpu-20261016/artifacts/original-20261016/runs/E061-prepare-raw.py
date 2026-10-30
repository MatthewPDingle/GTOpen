"""Freeze fresh complete showdown raw controls after current allocation revalidation."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E061-resource';r=old.read(RES/'report.json');p=old.read(RES/'protocol.json')
for n,h in p['input_sha256'].items():old.pin(n,h)
assert r['status']=='pass_resource_feasibility_only' and all(r['gates'].values()) and r['kernel_launches']==r['solver_executions']==0
for label in ['rustc','probe']:
 e=old.read(RES/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error'] is e['cleanup'] is None
assert r['gates']['all9_sm75_fallback_entries_exact'] and r['gates']['async_copies_emitted']
for pair in r['details'].values():
 assert pair['baseline']['registers']==38 and pair['candidate']['registers']==40
 assert all(pair['allocation_admission']['gates'].values())
H=ROOT/'runs/E061-kernel-control';assert not H.exists();H.mkdir();prior=ROOT/'runs/E053-kernel-control';S=ROOT/'runs/E061-source'
for n in ['accepted-evaluator.rs','corpus.json']:(H/n).write_bytes((prior/n).read_bytes())
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E053_EXACT','E061_EXACT')
probe=probe.replace('//! E053: exact128thread sorted-copy/prefix fusion differential; no timing.','//! E061: fresh exact original E050async staging vs accepted E051, no timing.')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute-r2.py').read_text(encoding='utf-8').replace('E053','E061').replace('execution-plan-r2.json','execution-plan.json').replace('Fixed328case whole-raw shared-cache control','Fixed364case whole-raw asynchronous staging control')
needle="'cases':328,'kernel_launches':656";assert runner.count(needle)==1;runner=runner.replace(needle,"'cases':len(records),'kernel_launches':complete['kernel_launches']")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(prior/'execution-plan-r2.json');P.update(id='E061-kernel-control-execution',at=old.now(),original_form='E050',status='FROZEN_PRE_FIRST_NUMERICAL_LAUNCH',source_manifest_sha256=old.sha(S/'manifest.json'),resource_report_sha256=old.sha(RES/'report.json'))
P['rustc_command']=[x.replace(str(prior),str(H)) for x in P['rustc_command']]
paths=[*H.iterdir(),Path(__file__),*S.iterdir(),RES/'report.json',RES/'protocol.json',ROOT/'runs/D101-resource-eligibility-audit/report.json',ROOT/'runs/D101-resource-eligibility-audit/docket.json',old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(x):old.sha(x) for x in paths if x.is_file()}|{x:h for x,h in old.read(prior/'execution-plan-r2.json')['input_sha256'].items() if Path(x).suffix in ['.rlib','.lib']}
P.update(cases=364,kernel_launches=728,scope='Fresh actual whole up_show output/input/guard words for exact original asynchronous form. Same retained364case corpus/identities, no old numerical/timing result used. Mathematically unchanged operations/production128thread path; rank/geometry/zero/nonfinite/tail/overlap guards all retained. Compare every result bit and actual input. Fail closes form without source variant or extra cases.',performance_measured=False,candidate_accepted=False)
old.save(H/'execution-plan.json',P)
published={}
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_numerical_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E061');e.update(stage='Fresh complete showdown raw matrix',reason='Current resource check passes:38to40nominal but same1,280registers/warp, zero local/static/dynamic/occupancy regressions,27parameter ABI and8other entries exact;9sm75fallback entries exact,2async copies/wait emitted. First fresh364pair numerical controls next, not a speed claim.');e['evidence'].append({'label':'First numerical control protocol','url':'evidence/'+H.name+'/execution-plan.json'});s.update(updated_at=old.now(),stage='E061 exact full-kernel control',activity='Fixed364paired showdown cases, all output/input/guard bits. Exact original E050form, no arithmetic/precision or width changes.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'execution_plan_sha256':old.sha(H/'execution-plan.json'),'pairs':364,'kernel_launches':728,'resource_passed':True}),flush=True)
