import ast,difflib,json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/D105-local-index-proof';S=ROOT/'runs/E064-source';H=ROOT/'runs/E064-resource';prior=ROOT/'runs/E060-resource';oldp=old.read(prior/'protocol.json')
assert not (H/'protocol.json').exists() and not (H/'execution').exists()
for n in ['baseline.cu','candidate.cu']:assert (S/n).read_bytes()==(H/n).read_bytes()
runner=(prior/'execute.py').read_text(encoding='utf-8').replace('E060','E064')
assert runner.count("\nold.save(HERE/'report.json'")==1
runner=runner.replace("\nold.save(HERE/'report.json'","\n old.save(HERE/'report.json'")
needle="assert len(markers)==4 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'";assert runner.count(needle)==1;runner=runner.replace(needle,"assert len(markers)==5 and markers[0]['stage']=='integer_proof' and markers[1]['stage']=='device' and markers[-1]['stage']=='complete'\n assert markers[0]['local_combinations']==7918209 and markers[0]['base_address_cases']==55427463 and markers[0]['max_local_element_index']==5303")
assert runner.count('markers[1:-1]')==1;runner=runner.replace('markers[1:-1]','markers[2:-1]')
needle="unchanged=[k for k in be if be[k]==ce[k]];gates=";assert runner.count(needle)==1;runner=runner.replace(needle,"bf,cf=entries(OUT/'baseline-compute75.ptx'),entries(OUT/'candidate-compute75.ptx');assert set(bf)==set(cf)==set(P['expected_entries'])\n unchanged=[k for k in be if be[k]==ce[k]];gates=")
needle="'other8_entries_exact':set(unchanged)==set(be)-set(P['changed_entries'])";assert runner.count(needle)==1;runner=runner.replace(needle,needle+",'other8_compute75_entries_exact':all(bf[k]==cf[k] for k in bf if k not in P['changed_entries'])")
needle=" report={'id':'E064-resource'";assert runner.count(needle)==1
metrics=r''' def integer_sites(t):
  ops=re.findall(r'^\s*(?:@!?%p\d+\s+)?((?:add|sub|mul|mad|shl|shr|cvt)(?:\.[A-Za-z0-9_]+)+)\s',t,re.M)
  ops=[x for x in ops if not re.search(r'\.f(?:16|32|64)',x)]
  return {'explicit64_arithmetic_sites':sum(bool(re.search(r'\.(?:s64|u64|b64)$',x)) for x in ops if not x.startswith('cvt.')),'wide_u32_multiply_sites':sum('.wide.u32' in x for x in ops),'integer_arithmetic_and_conversion_sites':len(ops),'entry_lines':len(t.splitlines()),'opcode_histogram':{x:ops.count(x) for x in sorted(set(ops))}}
 static={'baseline':integer_sites(be['up_action']),'candidate':integer_sites(ce['up_action']),'limits':'PTX virtual static sites only. No machine-address throughput, dynamic instruction or runtime speed inference. If resources pass, separately pinned driver-machine proof required before any application kernel.'}
'''
runner=runner.replace(needle,metrics+needle)
needle="'raw_markers':markers,";assert runner.count(needle)==1;runner=runner.replace(needle,needle+"'integer_model_proof':markers[0],'static_address_code':static,")
ast.parse(runner)
# Execute only this pure static parser against a small known instruction list.
parsed=ast.parse(runner);fn=next(n for n in ast.walk(parsed) if isinstance(n,ast.FunctionDef) and n.name=='integer_sites');testns={'re':re};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<metric-parser-check>','exec'),testns)
trial=testns['integer_sites'](' add.s64 %rd1, %rd2, %rd3;\n mul.wide.u32 %rd4, %r1, 4;\n add.f32 %f1, %f2, %f3;\n')
assert trial['explicit64_arithmetic_sites']==1 and trial['wide_u32_multiply_sites']==1 and trial['integer_arithmetic_and_conversion_sites']==2
(H/'execute.py').write_text(runner,encoding='utf-8',newline='\n')
P={k:oldp[k] for k in ['changed_entries','gpu_uuid','expected_entries','expected_abi','allocation_proof']};P.update(id='E064-resource',at=old.now(),status='FROZEN_PRE_INTEGER_AND_RESOURCE_EXECUTION',source_manifest_sha256=old.sha(S/'manifest.json'),rustc_command=[s.replace(str(prior),str(H)) for s in oldp['rustc_command']],fixed_gates='Exhaust all7,918,209local common-arity inputs and55,427,463base cases. Current D094allocation/local/shared/maxthread/occupancy/fit filter, unchanged20parameter ABI and8other entries actual/compute75. If pass, actual current-driver machine proof of intended address-work reduction required before GPU numerics. No source variants or resampling. All1%/strict-fixture/exactness/fresh16/broad/material/holdout/cumulative rules unchanged.')
paths=[*D.iterdir(),*S.iterdir(),*H.iterdir(),Path(__file__),ROOT/'runs/D104-counter-availability/report.json',ROOT/'comparisons/D104-availability-root-check/report.json',ROOT/'runs/D094-resource-materiality/report.json',ROOT/'runs/D094-resource-materiality/test-report.json',old.REPO/'tools/postflop_resource_admission.py',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',ROOT/'runs/accepted-E051/common_e051.py']
P['input_sha256']={str(p):old.sha(p) for p in paths if p.is_file()}|{p:h for p,h in oldp['input_sha256'].items() if Path(p).suffix in ['.rlib','.lib']};old.save(H/'protocol.json',P)
old.save(D/'protocol.json',{'id':'D105-local-index-proof','at':old.now(),'combined_resource_protocol_sha256':old.sha(H/'protocol.json'),'execution':'Integer model first inside the same one-shot no-launch E064resource probe; no separate duplicate execution.','scope':'Typed32/64element arithmetic proof only; GPU raw values not compared yet.','source_activated':False,'performance_measured':False})
published={}
for folder in [D,S,H]:
 for p in folder.iterdir():
  if not p.is_file():continue
  key='evidence/'+folder.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  published[key]=old.sha(p)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'artifact_sha256':published,'http_bytes_verified':True,'native_executions':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);assert not any(e['id'] in ['D105','E064'] for e in st['experiments']);st['experiments'].extend([{'id':'D105','at':old.now(),'kind':'diagnostic','title':'Bounded local action-index arithmetic proof','status':'running','correctness':'pending','stage':'Exhaustive integer model before CUDA resource query','reason':'CommonNA2/3/4local index<=5303; generic/global64bit semantics retained.55million synthetic base comparisons, no actual memory access or FP/speed claim.','evidence':[{'label':'Frozen model scope','url':'evidence/D105-local-index-proof/protocol.json'}]},{'id':'E064','at':old.now(),'kind':'candidate','title':'Common-arity local action-index narrowing','status':'running','correctness':'pending','accepted':False,'stage':'No-launch compiler/resource admission','reason':'One fixed integer-only helper at4local expressions inside trainingup_action. Prove bounds/ABI/unchanged entries/resources, then actual machine mechanism before any GPU numerical or speed work.','evidence':[{'label':'Fixed source review','url':'evidence/E064-source/source-review.json'},{'label':'Frozen combined prelaunch protocol','url':'evidence/E064-resource/protocol.json'}]}]);st.update(updated_at=old.now(),state='running',active_experiment='E064',stage='E064integer and compiled-resource proof',activity='Distinct common-arity local address-generation hypothesis. No profiler counters, application kernels, source activation or speed measurement.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'status':'integer_resource_screen_frozen','protocol_sha256':old.sha(H/'protocol.json'),'candidate_sha256':old.sha(S/'candidate.cu'),'native_executions':0}),flush=True)
