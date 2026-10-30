"""Freeze fresh complete showdown raw controls after current feasibility revalidation."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
RES=ROOT/'runs/E066-resource';r=old.read(RES/'report.json');p=old.read(RES/'protocol.json')
for n,h in p['input_sha256'].items():old.pin(n,h)
assert r['status']=='pass_resource_feasibility_only' and all(r['gates'].values()) and r['kernel_launches']==r['solver_executions']==0
for label in ['rustc','probe']:
 e=old.read(RES/'execution'/(label+'.exit.json'));assert e['returncode']==0 and e['error'] is e['cleanup'] is None
assert r['gates']['other8_sm75_entries_exact'] and r['gates']['full212byte_cache_emitted_actual'] and r['gates']['full212byte_cache_emitted_sm75']
for pair in r['details'].values():
 assert pair['baseline']['registers']==38 and pair['candidate']['registers']==39
 assert pair['baseline']['static_shared_bytes']==1040 and pair['candidate']['static_shared_bytes']==1248
 assert all(pair['feasibility_admission']['gates'].values())
R=ROOT/'comparisons/E066-resource-root-check';assert not R.exists();R.mkdir()
raw=(RES/'execution/probe.stdout.log').read_text();import json as _json
markers=[_json.loads(x.split('E066_RESOURCE ',1)[1]) for x in raw.splitlines() if x.startswith('E066_RESOURCE ')];assert markers==r['raw_markers'] and len(markers)==22
rows=markers[1:-1];assert len(rows)==20 and {x['shape'] for x in rows}==set(p['shapes'])
assert all(x['dynamic_shared_bytes']<=26520 and x['static_shared_bytes']+x['dynamic_shared_bytes']<=markers[0]['shared_limit'] and x['max_threads']>=256 and x['fits_default_limits'] and all(t[1]>0 for t in x['occupancy_by_threads']) for x in rows)
assert len(r['abi']['baseline'])==len(r['abi']['candidate'])==27 and r['abi']['baseline']==r['abi']['candidate']
old.save(R/'report.json',{'id':R.name,'at':old.now(),'status':'pass_feasibility_and_abi_only','resource_report_sha256':old.sha(RES/'report.json'),'actual_native_rows_match_report':True,'registered_shapes':10,'rows':20,'all_supported_hand_counts_bounded_by1326_monotone_dynamic_formula':'4*nh_o+16*m_o<=26520; full bound actual queried, static1248 added fitsdefault','reported_registers':[38,39],'static_shared_bytes':[1040,1248],'warnings':'Two128thread shapes12to11theoretical residency; disclosed, not a measured capacity/speed result. No per-threadlocal or dynamic allocation increase.','kernel_launches':0,'new_native_executions':0,'candidate_accepted':False,'limits':'Root replay, not external independent audit; compiled resources/positive theoretical occupancy do not establish numerical correctness, measured memory/CPU/responsiveness, speed or adoption.'})
H=ROOT/'runs/E066-kernel-control';assert not H.exists();H.mkdir();prior=ROOT/'runs/E053-kernel-control';S=ROOT/'runs/E066-source'
for n in ['accepted-evaluator.rs','corpus.json']:(H/n).write_bytes((prior/n).read_bytes())
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((S/n).read_bytes())
probe=(prior/'probe.rs').read_text(encoding='utf-8').replace('E053_EXACT','E066_EXACT')
probe=probe.replace('//! E053: exact128thread sorted-copy/prefix fusion differential; no timing.','//! E066: fresh exact original E031shared card-offset cache vs accepted E051, no timing.')
(H/'probe.rs').write_text(probe,encoding='utf-8',newline='\n')
runner=(prior/'execute-r2.py').read_text(encoding='utf-8').replace('E053','E066').replace('execution-plan-r2.json','execution-plan.json').replace('Fixed328case whole-raw shared-cache control','Fixed364case whole-raw card-offset cache control')
needle="'cases':328,'kernel_launches':656";assert runner.count(needle)==1;runner=runner.replace(needle,"'cases':len(records),'kernel_launches':complete['kernel_launches']")
ast.parse(runner);(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P=old.read(prior/'execution-plan-r2.json');P.update(id='E066-kernel-control-execution',at=old.now(),original_form='E031',status='FROZEN_PRE_FIRST_NUMERICAL_LAUNCH',source_manifest_sha256=old.sha(S/'manifest.json'),resource_report_sha256=old.sha(RES/'report.json'))
P['rustc_command']=[x.replace(str(prior),str(H)) for x in P['rustc_command']]
paths=[*H.iterdir(),Path(__file__),*S.iterdir(),RES/'report.json',RES/'protocol.json',R/'report.json',old.REPO/'tools/postflop_resource_feasibility.py',ROOT/'runs/D108-resource-feasibility-audit/report.json',ROOT/'runs/D108-resource-feasibility-audit/docket.json',old.REPO/'research/postflop-gpu-20261016/resource-feasibility-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(x):old.sha(x) for x in paths if x.is_file()}|{x:h for x,h in old.read(prior/'execution-plan-r2.json')['input_sha256'].items() if Path(x).suffix in ['.rlib','.lib']}
P.update(cases=364,kernel_launches=728,scope='Fresh actual whole up_show output/input/guard words for exact original shared offset-cache form. Same retained364case corpus/identities, no old numerical/timing result used. Same original floating operations/production128thread path; rank/geometry/zero/nonfinite/tail/overlap guards all retained. Compare every result bit and actual input. Fail closes form without source variant or extra cases.',performance_measured=False,candidate_accepted=False)
old.save(H/'execution-plan.json',P)
published={}
for p in [*H.iterdir(),*RES.rglob('*'),R/'report.json']:
 if p.suffix in ['.exe','.pdb','.bin'] or not p.is_file():continue
 if not p.is_file():continue
 folder=H if p.is_relative_to(H) else RES if p.is_relative_to(RES) else R
 key='evidence/'+folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists() or dst.read_bytes()==p.read_bytes()
 if not dst.exists():dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_numerical_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(e for e in s['experiments'] if e['id']=='E066');e.update(stage='Fresh complete showdown raw matrix',reason='Current feasibility passes:38to39registers,1040to1248static shared; two registered128thread occupancies12to11disclosed. All10shapes including1326handbound fitdefaultlimits; no local/dynamic/maxthreads regression;27parameter ABI and8other entries exact onactual/sm75,212Bcache emitted,5barriers. Fresh364pair controls next, no speed/material conclusion.');e['evidence'].append({'label':'First numerical control protocol','url':'evidence/'+H.name+'/execution-plan.json'});s.update(updated_at=old.now(),stage='E066 exact full-kernel control',activity='Fixed364paired showdown cases, all output/input/guard bits. Exact original E031form, no arithmetic/precision or table/placement changes.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print(json.dumps({'execution_plan_sha256':old.sha(H/'execution-plan.json'),'pairs':364,'kernel_launches':728,'resource_passed':True}),flush=True)
