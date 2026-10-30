"""Freeze the runner, execute once, then publish the complete CPU prefetch outcome."""
from pathlib import Path
import ast,json,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/D126-owned-memory-prefetch';M=R/'runs/D126-manager';P=old.read(H/'protocol.json');old.custody();assert not(R/'gpu-run.lock').exists()and not M.exists()
for p,h in P['input_sha256'].items():old.pin(p,h)
ast.parse((H/'execute.py').read_text(encoding='utf-8'));P.update(at=old.now(),original_preparation_protocol_sha256=old.sha(H/'protocol.json'));P['input_sha256'].update({str(p):old.sha(p)for p in[H/'protocol.json',H/'execute.py',Path(__file__)]});old.save(H/'execution-plan.json',P)
def publish(p,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
 else:shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(p)}
pub=[publish(H/'execute.py',H.name+'/execute.py'),publish(H/'execution-plan.json',H.name+'/execution-plan.json'),publish(Path(__file__),H.name+'/run-publish.py')]
old.save(H/'runner-pre-execution-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'execution-plan.json'),'HTTP_byte_verified_artifacts':pub,'compiler_or_native_executions':0})
M.mkdir();print('D126 execution protocol',old.sha(H/'execution-plan.json'),flush=True);old.child([sys.executable,'-B',str(H/'execute.py'),old.sha(H/'execution-plan.json')],M,'cpu',old.env(),2400)
q=old.read(H/'report.json');receipt=old.read(M/'cpu.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None;old.custody();assert not(R/'gpu-run.lock').exists()
for folder in[H,H/'build',H/'execution',M]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in['.py','.rs','.json','.log']:pub.append(publish(p,(H.name+'-'+folder.name if folder in[H/'build',H/'execution']else folder.name)+'/'+p.name))
reason='CPU-only prefault/prefetch screen '+q['status']+'. '
if q['sum_fixture_CPU_component_saving_ms']is not None:reason+=f"Sum fixture-median component saving {q['sum_fixture_CPU_component_saving_ms']:.6f}ms versus fixed95.825124ms budget. "
reason+='Original full validation retained; all owned guards/controls pass. No new complete-solve speed/material result or source adoption.'
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='D126');e.update(status='measured',correctness='Owned API/data/predicate controls pass',stage='One integrated trial admitted'if q['admit_one_integrated_trial']else'Closed: CPU component admission failed',reason=reason,accepted=False,updated_at=old.now());e['evidence'].extend([{'label':'Final frozen ability/cohort runner','url':'evidence/D126-owned-memory-prefetch/execution-plan.json'},{'label':'Full CPU component and page-fault results','url':'evidence/D126-owned-memory-prefetch/report.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment=None,stage='Preparing an integrated prefetch trial'if q['admit_one_integrated_trial']else'Investigating the next GPU optimization',activity=reason+' E051 accepted/live gain12.44% and last primary B246 unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(M/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':pub,'source_main_live_PTX_custody_pass':True,'all_owned_children_terminal':True})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D126 owned Windows prefetch CPU component screen'not in raw
entry=f'''

### D126 owned Windows prefetch CPU component screen

Previous goal turn completed E077 full12 host maps/1820 GPU pairs/85 ordinary tests and fixed3 complete-solve pairs, rejected0.1919971774% aggregate slowdown plus rainbow/two-tone guards. Source/cases closed, no rescue. Current accepted162/main163/live/protected2PTX/idle and last primary B246 revalidated. New independent source/local-all-ref screen found no Windows owned-range prefetch. Official Microsoft API review retained: optional current-process hint, flags0, chiefly paged-out memory; fresh zero pages may not benefit. Prefetched cache is not immediately working set, so counters alone cannot prove physical-cache cost. No settings/privileges/limits/eviction/locking/external-process access. Closed parallel-OR/provenance/SIMD/initialization/prefix forms not composed or reopened.

Frozen preparation {old.sha(H/'protocol.json')} and final runner {old.sha(H/'execution-plan.json')} before first compiler/native execution. Same accepted E051 solver RLIB/mimalloc/Spot/Solver/GpuPlan CPU setup. Exact original can_upload_zeros scale/q predicate body, all4 scans retain reg0/reg1/strat0/strat1 order. Candidate only hints4 borrowed quantized buffers when total>=64MiB and all4 scale arrays positive-zero; threshold fixed prospectively, tiny fallback before precheck. Additional eligibility/API/timer costs included. No scan/data/math/initialization omission, metadata hint or solver source activation. Model deliberately omits CUDA context/pinned/device/ArenaLayout construction; it is not full production upload.

One compiler, one small owned-range ABI/API/data/predicate ability process; outcome {old.read(H/'ability-report.json')['status']}. Full4128u16 before/after image including guards exact, original15 predicate controls pass, Win64 layouts16/72 bytes checked. Then {q['native_component_processes']} fresh CPU-only processes in fixed B1/T1,T2/B2,B3/T3 order, each3 canonical fixtures. All original4 full-zero results pass; process-wide page-fault/current+peak working-set/commit counters retained, not hard-fault attribution or OS-cache physical measurement. No repeated process/source/API/flag/filter/threshold/extra sample. Every observation retained, no exclusions/extensions.

Result {q['status']}; sum fixture CPU-component median saving {q['sum_fixture_CPU_component_saving_ms']}ms versus prospective95.825124ms budget (1% of preserved9582.5124ms accepted suite, budgeting constant only/no historical pooling). Applicable>=64MiB fixture component guards are positive median and>=2/3 improving pairs; tiny fallback retained but only future full-cycle strict fixture rule could qualify it. Full per-process/paired/counter results in report SHA {old.sha(H/'report.json')}. {reason} No causal/unbiased/full-solve/universal speed/no-tradeoff assertion from model.

All{len(pub)} published code/API-review/protocol/report/log artifacts HTTP byte verified. All native/parent handles terminal, no GPU lock, source never activated, no E078 source or new primary IDs. Accepted162/main163/live/protected2PTX exact; E051 accepted/deployed cumulative12.4372274192% unchanged. Goal active; {'one integrated trial still needs all GPU exact/broad/material/full-cycle/fresh16/holdout/cumulative gates'if q['admit_one_integrated_trial']else'this exact PrefetchVirtualMemory source/filter/threshold form is closed after failed component admission; pursue a distinct mechanism'}.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: screen process-local memory prefetch and scan fault costs','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'status':q['status'],'sum_component_saving_ms':q['sum_fixture_CPU_component_saving_ms'],'admit_integrated':q['admit_one_integrated_trial'],'published_files':len(pub)}),flush=True)
