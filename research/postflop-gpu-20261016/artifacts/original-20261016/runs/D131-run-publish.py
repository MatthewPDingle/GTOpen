"""Freeze execution before compiler, then publish the complete component result."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/D131-zero-check-setup-overlap';M=R/'runs/D131-manager';old.custody();assert not M.exists()and not(R/'gpu-run.lock').exists();P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
for n in['execute.py','replay.py']:ast.parse((H/n).read_text(encoding='utf-8'))
P.update(at=old.now(),original_preparation_protocol_sha256=old.sha(H/'protocol.json'));P['input_sha256'].update({str(p):old.sha(p)for p in[Path(__file__),H/'execute.py',H/'replay.py',H/'protocol.json']});old.save(H/'execution-plan.json',P)

def publish(p,key):
    dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
    else:shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
    return {'url':'evidence/'+key,'sha256':old.sha(p)}

pub=[publish(H/n,H.name+'/'+n)for n in['execute.py','replay.py','execution-plan.json']]+[publish(Path(__file__),H.name+'/prepare-run.py')]
old.save(H/'runner-pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'execution-plan.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_native_executions':0})
M.mkdir();print('D131 execution protocol',old.sha(H/'execution-plan.json'),flush=True)
old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'execution-plan.json')],M,'component',old.env(),3000)
q=old.read(H/'report.json');old.custody();assert not(R/'gpu-run.lock').exists()
for folder in[H,H/'build',H/'execution',M]:
    for p in folder.iterdir():
        if p.is_file()and p.suffix in['.py','.rs','.json','.log']:pub.append(publish(p,(H.name+'-'+folder.name if folder in[H/'build',H/'execution']else folder.name)+'/'+p.name))
for spec in P['order']:
    for p in(H/'execution'/spec['id']).glob('*.json'):pub.append(publish(p,H.name+'-'+spec['id']+'/'+p.name))
reason=f"Component saving {q['sum_fixture_component_saving_ms']:.6f} ms versus the fixed 95.825124 ms screening budget. All original predicates, lifecycle controls and complete layout images pass. "+('One integrated trial admitted; full-solve speed and material costs still require qualification.'if q['admit_one_integrated_trial']else'Component admission failed. This overlap form is closed; no rescue variants or extra samples.')
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D131')
    e.update(status='measured',correctness='12 lifecycle cases, 15 predicates, 14 wrong-store controls and 18 full layout images pass',stage='One integrated source trial admitted'if q['admit_one_integrated_trial']else'Closed: component admission failed',reason=reason,updated_at=old.now(),accepted=False)
    e['evidence'].extend([{'label':'Frozen execution plan','url':'evidence/D131-zero-check-setup-overlap/execution-plan.json'},{'label':'Complete component wall, CPU and layout results','url':'evidence/D131-zero-check-setup-overlap/report.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing zero-validation overlap integration'if q['admit_one_integrated_trial']else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain at 12.44% cumulative gain; last primary B252.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'bulk_raw_retained_physically_S':True,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D131 full zero-validation and setup overlap'not in raw
entry=f'''

### D131 full zero-validation and setup overlap

E079 is closed after the strict river fixture failed, despite its aggregate gain. Accepted source, main checkout, live executable and protected PTX were reverified before this distinct component. CUDA context and stream creation stay on the original caller before the test window. The caller performs original NVRTC/module, pinned staging allocation and original ArenaLayout construction while one CPU-only worker runs all four original serial scale-first/full-q predicates exactly once, in original order. Private borrow-lifetime tokens accept only the identical Store; all original inactive/snapshot guards execute after joining. No scan is omitted, no persistent provenance added, no parallel integer reduction or sparse page prepass, no planner or CUDA work moved to the worker. Fixed total quantized bytes >=64 MiB, smaller and F32 paths serial. No threshold, helper, placement or thread variants after failure.

Preparation {old.sha(H/'protocol.json')} and execution {old.sha(H/'execution-plan.json')} were frozen and HTTP published before the first compiler/native run. One compiler and one CPU-only ability process passed 12 lifecycle/error/panic/drop/priority cases, 15 original-predicate cases, 14 wrong-store rejections and 7,308 complete before/after words. OS spawn failure and actual driver exhaustion remain source-reviewed, not injected. Six fresh processes in BC/CB/BC order each ran the three canonical compressed fixtures. All 18 complete private layout images and capacities match original reference construction; {q['encoded_words_checked']} encoded words, {q['root_checks']} comparison checks and {q['raw_bytes']} raw bytes retained physically on S. Zero application kernels or GPU solves.

Component saving {q['sum_fixture_component_saving_ms']} ms against the prospectively fixed 95.825124 ms budget. Eligible large fixtures also require positive median saving, at least two improving pairs and all-thread CPU median <= baseline *1.10 +5 ms. Results: {json.dumps(q['fixtures'],separators=(',',':'))}. Report SHA {old.sha(H/'report.json')}. {reason}

This source-matched setup window omits device arena uploads and full solving. It establishes neither a complete-cycle gain nor no tradeoffs. Broad exactness/F32/state/menu/save/resume/continuation, actual CPU/host/GPU peak/capacity/responsiveness, strict complete-cycle fixture guard, fresh16, holdout and fresh-original cumulative gates remain required. All {len(pub)} published artifacts were HTTP byte verified. All owned children are terminal, GPU lock released, source/main/live/protected PTX custody exact. No E080 source or new primary IDs yet. E051 remains accepted and deployed at 12.4372274192% measured cumulative gain; last primary B252; goal active. {'One integrated trial is admitted.'if q['admit_one_integrated_trial']else'This exact form is closed without rescue variants or resampling.'}
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody()
subprocess.run(['git','commit','--only','-m','research: screen full zero-validation and setup overlap','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(json.dumps({'status':q['status'],'saving_ms':q['sum_fixture_component_saving_ms'],'admit_integrated':q['admit_one_integrated_trial'],'published_files':len(pub)}),flush=True)
