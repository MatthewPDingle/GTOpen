"""Build, run, replay and publish one frozen full-workload resource comparison."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
assert len(sys.argv)==2;H=R/'runs/E080-resource-controls';old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists();M=R/'runs/E080-resource-manager';assert not M.exists();assert not(H/'build').exists()and not(H/'execution').exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
for p in[Path(__file__),H/'root-check.py']:ast.parse(p.read_text(encoding='utf-8'))
old.save(H/'runner-binding.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'runner_sha256':old.sha(__file__),'root_reader_sha256':old.sha(H/'root-check.py'),'subject_or_guards_changed':False,'solver_resource_observations':0});pub=[]
def publish(p,key):
    dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
    else:shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:assert response.read()==p.read_bytes()
    pub.append({'url':'evidence/'+key,'sha256':old.sha(p)})
for p in[Path(__file__),H/'root-check.py',H/'runner-binding.json']:publish(p,H.name+'/'+p.name)
for folder in[R/'runs/E080-cpu-commit-ability',R/'runs/E080-cpu-commit-ability/execution',R/'runs/E080-cpu-commit-manager']:
    for p in folder.iterdir():
        if p.is_file()and p.suffix in['.json','.py','.log']:publish(p,('E080-cpu-commit-execution'if folder.name=='execution'else folder.name)+'/'+p.name)
M.mkdir();print('Resource screen protocol',sys.argv[1],flush=True)
old.child([sys.executable,'-B',str(H/'build.py'),sys.argv[1]],M,'build',old.env(),1500)
old.child([sys.executable,'-B',str(H/'execute.py'),sys.argv[1]],M,'native',old.env(),2400)
old.child([sys.executable,'-B',str(H/'assess.py'),sys.argv[1]],M,'assessment',old.env(),180)
old.child([sys.executable,'-B',str(H/'root-check.py'),sys.argv[1]],M,'root-replay',old.env(),180)
q=old.read(H/'report.json');root=old.read(H/'root-report.json');assert q['all_material_guards_pass']==root['all_material_guards_pass'];passed=q['all_material_guards_pass'];old.custody();assert not(R/'gpu-run.lock').exists();O=R/'runs/E080-resource-closure';assert not O.exists();O.mkdir()
reason='All fixed full-workload process CPU and memory resource gates passed. Native complete-cycle all-thread CPU, whole-process CPU, OS host highwaters and calibrated PID-filtered GPU peaks show no material increase under the prospective bounds. Responsiveness and final compiled-resource/graph/scope audit remain; not adopted.'if passed else'Rejected by prospective material resource guards: '+', '.join(x['metric']for x in q['checks']if not x['passed'])+'. No extra samples, threshold, helper, thread, source, placement or eligibility variants or rescue runs. Accepted and live E051 remain unchanged.'
old.save(O/'decision.json',{'at':old.now(),'id':'E080-resource','status':'material_screen_pass_pending_remaining_audit'if passed else'rejected_material_cost','reason':reason,'protocol_sha256':sys.argv[1],'report_sha256':old.sha(H/'report.json'),'root_report_sha256':old.sha(H/'root-report.json'),'candidate_adopted':False,'original_combined_calibration_pass':False,'independent_CPU_control_pass':True,'GPU_component_checks_pass':18})
for folder in[H,M,O]:
    for p in folder.iterdir():
        if p.is_file()and p.suffix in['.json','.py','.rs','.patch','.log']:publish(p,folder.name+'/'+p.name)
for folder in[H/'build',H/'execution']:
    for p in folder.rglob('*'):
        if p.is_file()and p.suffix in['.json','.log']:publish(p,H.name+'/'+p.relative_to(H).as_posix())
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='measured'if passed else'rejected',accepted=False,stage='Resource screen passed; responsiveness and final audit next'if passed else'Closed: material resource guard failed',reason=reason,updated_at=old.now());e['evidence'].extend([{'label':'Full-workload CPU and memory cost screen','url':'evidence/E080-resource-controls/report.json'},{'label':'Resource observation arithmetic replay','url':'evidence/E080-resource-controls/root-report.json'},{'label':'Independent CPU commitment validation','url':'evidence/E080-cpu-commit-ability/report.json'},{'label':'Material qualification decision','url':'evidence/E080-resource-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080'if passed else None,stage='E080 responsiveness and final audit preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Existing accepted live E051 cumulative gain remains 12.44%.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'all_owned_children_terminal':True,'source_main_live_PTX_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E080 actual process CPU and memory cost screen'not in raw
entry=f'''

### E080 actual process CPU and memory cost screen

Previous gates remain frozen: initial2.4834500515%, fresh16incremental1.7148158134% with16/16improving, fixed holdout1.1740303114%, fresh original cumulative14.7414188354%; exact states/checkpoints, six actual capacity cases per arm and large warm raw parity. No source adoption. Known changing-range experimental equivalence failure stays failed identically in both arms and is not cleared.

Resource preflight validates Win64 FILETIME8/PROCESS_MEMORY_COUNTERS_EX80 and software GPU memory catalog, not measurement quality. Freeze original combined allocation calibration {old.sha(R/'runs/E080-memory-observer-ability/protocol.json')}, one compiler/one native process,9fixed states and40samples/state50ms/final20plateau/4MiB tolerance. All18GPU known allocation/release/stability checks and CPU RSS pass, two private-commit expectations fail. Raw CPU128 samples change777031680to709791744private bytes despite constant134217728payload; after release575303680versus642547712baseline. Total commitment has independent changes, so mixed private-payload expectation cannot calibrate it. Original whole form is closed failed and remains failed, no tolerance/sample edits or GPU reruns. No solver cost claim from that control.

Independent CPU-only explicit VirtualAlloc/touch/VirtualFree128/256/repeated128MiB, sevenstates, same40samples/50ms/final20/4MiB tolerance, CUDA absent verified. All21private/RSS/stability checks pass; this validates APIs without driver commitment interference. It does not exclude driver bytes from actual solver profiling or replace any workload. GPU calibration facts come from original unchanged18checks; original combined gate is not relabeled green.

Freeze actual resource protocol {sys.argv[1]} before compiler or solver resource observations, plus additive runner/root-reader binding before compile. Two identical observation harnesses linked to frozen accepted/candidate libraries add only native OS snapshots around original full-cycle clock and after fingerprint/suite. Every original fixture, algorithm, quality, storage, checks, stop, solve/readback and payload unchanged; no solver source activation or added application GPU calls. Exactly6fresh full suites MB1/MC1,MC2/MB2,MB3/MC3. All18fullresults/138checkpoints exact; all driver commitment retained. Native all-thread CPU includes completed worker; whole-process CPU also startup/fingerprint/shutdown. Host OS lifetime highwaters, PID-filtered calibrated GPU dedicated/shared sampled peaks with predefined cadence and plateau coverage. Timings are diagnostic, never pooled into prior speed scores.

Prospective CPU median<=baseline*1.02+15.625ms perfixture/phase sum/wholeprocess; host peaks<=baseline+max(1%,16MiB); GPU peaks<=baseline+2MiB. Results {json.dumps(q['checks'],separators=(',',':'))}. {reason} Resource report{old.sha(H/'report.json')}, root{root['checks']}owner/raw/arithmetic checks {old.sha(H/'root-report.json')}. No exclusions, extensions, score updates or source variants. GPU software-accounting peaks are sampled with coverage gates, not shader hardware counters or universal physical-memory guarantees. Root audit is not external independent review.

All{len(pub)}artifactsHTTPbyteverified, rawphysicallyS; all ownedchildren terminal, GPUlockreleased, source/main/live/protectedPTX exact. {'Responsiveness and final compiled-resource/graph/scope audit remain before any adoption.'if passed else'This exact candidate form is closed after material failure, with no rescue variants or additional samples.'} Original experimental and combined calibration gates stay failed. Accepted/deployed E051 cumulative12.4372274192%unchanged,lastprimaryB274,goalactive.
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: measure zero-validation overlap process CPU and memory costs','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':'material_screen_pass_pending_audit'if passed else'rejected_material_cost','checks':q['checks'],'published_files':len(pub),'candidate_adopted':False}),flush=True)
