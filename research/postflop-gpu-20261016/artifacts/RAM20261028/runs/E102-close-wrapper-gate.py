import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
H=ROOT/'runs/D197-parent-chance-canonical';P=h.read(H/'protocol.json')
for p,digest in P['input_sha256'].items():h.pin(p,digest)
assert h.read(H/'execution/audit.exit.json')['returncode']==1
raw=ROOT/'comparisons/D198-canonical-terminal-diagnostic/report.json';r=h.read(raw)
assert r['status']=='raw_diagnostic_complete_original_wrapper_gate_failed' and not r['original_D197_wrapper_gate_pass'] and not r['E102_qualified']
assert r['pair_bytes_compared']==54608665195 and r['scientific_full_records_exact']==6 and r['canonical_checkpoints_exact']==46 and r['CPU_raw_pairs']==r['GPU_all69field_pairs']==12
assert len(r['wrapper_differences'])==12 and all(x['baseline_bytes']==4448 and x['candidate_bytes']==4464 and x['delta_bytes']==16 for x in r['wrapper_differences'])
assert h.read(ROOT/'runs/D198-canonical-terminal-diagnostic/execution/complete.json')['all_owned_readers_terminal']
receipts=[]
for folder in [ROOT/'runs/E102-resource/execution',ROOT/'runs/D195-original-chance/execution',ROOT/'runs/D195-parent-fanout/execution',ROOT/'runs/D195-parent-chance-controls/execution',ROOT/'runs/D196-parent-chance-engine/execution',H/'execution',ROOT/'runs/D198-canonical-terminal-diagnostic/execution']:
 for p in folder.glob('*.exit.json'):
  x=h.read(p);failed=p==H/'execution/audit.exit.json';assert x['returncode']==(1 if failed else 0) and x['error'] is x['cleanup'] is None
  receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':x['returncode'],'original_wrapper_gate_failure_retained':failed})
for p,v in r['whole_compared_raw_file_sha256'].items():assert Path(p).stat().st_size==v['bytes']
assert len(r['whole_compared_raw_file_sha256'])==66
assert not(ROOT/'runs/E102-build-plan').exists() and not(ROOT/'runs/E102-primary-plan').exists()
for n in ['E102R1','E102R2','E102R3','B314','B315','B316']:assert not(ROOT/'runs'/n).exists()
N=ROOT/'runs/E102-terminal-checkpoint';N.mkdir(exist_ok=False)
h.save(N/'report.json',{'id':'E102-close','at':h.now(),'status':'closed_original_canonical_wrapper_equality_gate_failed','reason':'Frozen D197 requires full metadata equality including wrapper_bytes. Actual accepted wrapper4448B versus E1024464B, +16B at all12lifecycle stages, consistent with added CudaFunction handle. This is a host resource/layout gate failure, not observed numeric or solve-speed failure. Do not waive after observing or rescue through alternate handle/caller/helper/source form.','original_D197_failure_retained':True,'original_D197_protocol_sha256':h.sha(H/'protocol.json'),'retained_raw_diagnostic_report_sha256':h.sha(raw),'direct_cases':8345,'direct_kernel_launches':16690,'engine_cases':36,'engine_phase_pairs':752,'canonical_scientific_records_exact':6,'canonical_checkpoints_exact':46,'canonical_all66device_plusCPU_query_save_futureEV_pairs_exact':True,'entire_raw_pair_bytes_exact':r['pair_bytes_compared'],'wrapper_differences':r['wrapper_differences'],'all66_retained_raw_file_extents_verified':True,'raw_files_not_rehashed_after_full_comparison':True,'original_numeric_failure_observed':False,'speed_or_improvement_measured':False,'new_integrated_Cargo_builds':0,'new_primary_or_confirmation_samples':0,'build_primary_preparers_written_but_never_executed':{str(ROOT/'runs'/n):h.sha(ROOT/'runs'/n) for n in ['E102-prepare-build.py','E102-prepare-primary.py','E102-record-primary.py']},'all_owned_compilers_native_readers_terminal':True,'child_receipts':receipts,'no_native_repeated_for_retained_reader':True,'accepted_source_main_live_protected_PTX_unchanged':True,'new_gain_accepted_or_deployed':False,'closure':'Exact parent-fanout form closed; no grouping/tile/width/guard/field/helper/caller/handle/flag/source/sample rescue. D198 raw completion is diagnostic, never a wrapper-equality pass or speed/adoption admission. Future unrelated forms must declare expected nonnumeric structural costs prospectively before native runs, while retaining full numerical/state equality and actual material/capacity gates.','last_primary_baseline_id':'B313','current_RAM_reference_ms':10456.4109,'historical_or_other_cohort_timing_pooled':False,'best_qualified':'E080 / GPU / compressed / 16workers','goal_active':True})
evidence=[]
for folder,names in [(N,['report.json']),(ROOT/'runs/D198-canonical-terminal-diagnostic',['protocol.json']),(raw.parent,['report.json']),(H/'execution',['audit.exit.json','audit.stderr.log'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D197');item.update(status='rejected',correctness='raw_numeric_exact_wrapper_equality_failed',stage='Frozen wrapper metadata equality failed',reason='Original reader stops at4448to4464byte hostwrapper, +16B. Sixscientific records/46checks exact. Diagnostic D198 completes54.6087GBpair-bytecomparison exact but original gate remains failed. No native repeat/timing admission.');item.setdefault('evidence',[]).extend(evidence)
 s['experiments'].append({'id':'D198','title':'Retained canonical raw diagnostic after wrapper gate failure','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','correctness':'all_numeric_raw_exact_original_wrapper_gate_failed','stage':'Read-only raw completion; original failure retained','reason':'All54,608,665,195pairbytes exact across66retained files,12wholeCPU/12all66GPUbuffers plusquery/save/futureEV. +16Bhostwrapper recorded atall12stages; notqualified,notiming/native repeats.','evidence':evidence})
 item=next(x for x in s['experiments'] if x['id']=='E102');item.update(status='rejected',accepted=False,correctness='direct_engine_canonical_numeric_exact_wrapper_gate_failed',stage='Closed before speed: host wrapper equality failed',reason='8345directpairs/36enginecases andall54.6GBcanonical pairbytes exact. AddedCUDAfunction handle grows hostwrapper4448to4464B, failing frozen equality check. No complete-cycle speed gain/loss measured; no waiver,handle/caller/source rescue oradoption.');item.setdefault('evidence',[]).extend(evidence)
 s.update(updated_at=h.now(),active_experiment='E102',stage='Parent chance form closed; independent source research continues',activity='E102 matched all tested numerical state, but failed frozen hostwrapper equality by16B. No speed claim or new gain. E080/GPU/compressed/16 remains live; currentRAMbaseline10.4564s separate.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('''

### E102 closed at frozen wrapper-equality gate; D198 raw completion

D197 original two compilers and baseline/candidate native processes terminal0. Six original full scientific records and46convergence checks exact. Original frozen reader terminal1 at full lifecycle metadata equality: wrapper_bytes4448baseline versus4464candidate at all12stages, +16B consistent with added CudaFunction handle. This is a host layout/resource gate failure, NOT a numerical failure or measured speed regression. The full wrapper-equality requirement should have been reconciled with the declared extra handle before freezing; it is not waived after observation.

D198 separately freezes one retained-data read-only reader. Original D197 protocol/source/error remains unchanged. It explicitly keeps original wrapper gate failed and records all12differences, then completes every other metadata and all54,608,665,195rawpairbytes across66files:12CPU/qscale pairs,12whole66devicebuffer pairs including allphysicalCFV,6queries,3saves,9futureEVs. All exact,62,564reader checks,109,217,330,390totalrawbytes. No native/solver/compiler repeat or field omission qualification; diagnostic completion cannot turn original gate green or admit speed.

E102 exact parent-fanout form CLOSED. No grouping/tile/width/guard/field/handle/helper/caller/flags/source/sample rescue. Planned ordinary Cargo and primary scripts remain unexecuted; B314/B315/B316 andE102R1-R3 unallocated. No speed/improvement measured, fresh16/broad/material/capacity/holdout/adoption never opened. Future unrelated forms must declare nonnumeric structural costs prospectively and keep full numerical equality and actual material/capacity checks. All compiler/native/readers terminal, accepted source/main/live/protectedPTX verified, locks absent, no gain accepted. E080/GPU/compressed/16 remains live, currentRAM reference10456.4109ms and lastprimaryB313 remain separate. All new outputX; goal active.
''')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: retain parent chance wrapper gate failure and full raw diagnostic'],cwd=h.REPO,check=True)
h.custody();print(json.dumps({'E102':'closed_wrapper_gate_failed','numeric_raw_pair_bytes_exact':r['pair_bytes_compared'],'wrapper_growth_bytes':16,'speed_samples':0,'all_owned_children_terminal':True,'new_gain_accepted':False}),flush=True)
