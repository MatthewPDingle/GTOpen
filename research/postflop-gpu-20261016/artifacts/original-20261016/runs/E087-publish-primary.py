import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
H=R/'runs/E087-primary-plan';P=old.read(H/'protocol.json')
qp=R/'comparisons/E087-three-pair-comparison/report.json';rp=R/'comparisons/E087-root-crosscheck/report.json'
q,root=old.read(qp),old.read(rp);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[]and q['extension_runs']==q['historical_timing_samples_used']==0
assert old.read(R/'runs/E087-primary-wrapper/complete.json')['all_children_terminal']
for p,h in P['input_sha256'].items():old.pin(p,h)
direct=old.read(P['direct_control_report']['path'])
O=R/'runs/E087-initial-closure';O.mkdir(exist_ok=False)
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All18full results,138checkpoints,88ordinary tests and808paired raw transfer/state files passed. "
if passed:reason+='Initial gate passed; separate fresh16,broad/material/capacity/holdout/fresh-original cumulative gates remain. Not adopted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below unrounded1%cutoff')
 failures=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if failures:why.append('repeatable fixture slowdown: '+', '.join(failures))
 reason+='Rejected: '+'; '.join(why)+'. Close this exact serial64MiB complete-node pinned-window integration; no window-size, overlap, helper, threshold, source-scope, placement or extra-sample rescue.'
old.save(O/'decision.json',{'id':'E087','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':88,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'raw_file_pairs':808,'manual_arena_phases':192,'small_trained_engines':8,'large_constructor_cases':8,'raw_reader_checks':direct['reader_checks'],'raw_control_report_sha256':old.sha(P['direct_control_report']['path']),'assessment_sha256':old.sha(qp),'root_replay_sha256':old.sha(rp),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E080','no_exclusions_extensions_pooling':True,'fresh16_broad_material_holdout_cumulative_run':False,'reason':reason})
folders=[(R/'runs/E087-source','E087-source'),(R/'runs/E087-host-type-check','E087-host-type-check'),(R/'runs/E087-transfer-control','E087-transfer-control'),(R/'comparisons/E087-transfer-control','E087-transfer-control-comparison'),(R/'runs/E087-source-preparation-failure','E087-source-preparation-failure'),(R/'runs/E087-transfer-preparation-failure','E087-transfer-preparation-failure'),(R/'runs/E087-build-plan','E087-build-plan'),(H,'E087-primary-plan'),(R/'runs/E087-primary-wrapper','E087-primary-wrapper'),(R/'runs/E087-native-execution','E087-native-execution'),(O,'E087-initial-closure'),(qp.parent,qp.parent.name),(rp.parent,rp.parent.name)]
for phase in ['feature','primary']:folders.append((R/'runs/E087-final-build'/phase,'E087-final-build-'+phase))
pub=[]
for folder,prefix in folders:
 for p in sorted(folder.rglob('*')):
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
  key=prefix+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E087')
 x.update(status='measured'if passed else'rejected',correctness='pass',accepted=False,stage='Initial pass; fresh confirmation pending'if passed else'Closed: performance gate failed',reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
 x['evidence'] += [{'label':'Complete-solve comparison','url':'evidence/E087-three-pair-comparison/report.json'},{'label':'Full-record arithmetic replay','url':'evidence/E087-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E087-initial-closure/decision.json'}]
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E087'if passed else None,stage='E087 separate confirmation preparation'if passed else'Investigating the next independent GPU mechanism',activity=reason+' Accepted/liveE080 remains14.7414188354%faster on registered warm complete-solve fixtures.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'bulk_raw_physical_S_only':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes()
assert b'### E087 bounded actual pinned staging'not in raw
entry='\n\n### E087 bounded actual pinned staging\n\n'
entry+='D138 CPU prerequisite retained. Fixed64MiB serial whole-node transfer window in3host files arena/mod/continuation_paging. Reuses compact metadata/coalescedF32spans/inactive snapshots and original Store codecs; full layouts collect active rows. Constructor prepares layout then bounds actual pinned allocation; E080worker/proofs/caller retained. Warm uploads and full/strategy readback drain every boundedcopy before staging reuse/CPUwrite/free, copy-error priority retained. Paging releases added full-layout metadata. CUDA/plan/Store/precision/math/quality/deviceallocations/graphs unchanged. Source reversal exact. Extra metadata/calls/waits can erase allocation benefit. Distinct from closedE040 full-allocation two-window overlap.\n\n'
entry+='Source preparation first stopped before candidate output on reverse-bookkeeping assertion; repairedlaststrategy occurrence with original retained. Transfer harness preparation first stopped on Windows cp1252 read before any compiler/native or source output; explicit UTF8 and complete accepted public-plan shim repaired. Original errors/scripts preserved; algorithm/corpus/gates unchanged. Exact arena standalone typecheck and7CPUunits pass. Actual GPU fixed96manual layouts/192arena phases,8smalltrained engines/24iterations/8exploitchecks and8largeconstructors pass. Compressed/F32/full/compact, fresh/warm/nonfinite/signedzero/subnormal, prechecked/unprechecked, whole active/inactive CPU/GPUimages, repeated readback/reupload, query/save/load/resume/tinybudget exact. Real queued validDMA followed by synthetic reportedcopyerror drains; originalerrorpriority and post-readyCPUunwind/stagingreuse pass. No actual hardwarefailure or atomicrollbackclaim. No performance counters.\n\n'
entry+=f"Independent rawreader:808pairedfiles,1600frames,11712fields,{direct['represented_full_words']}representedwords,{direct['reader_checks']}readerchecks. {direct['raw_pair_bytes']}rawpairbytes stayS. Real pinned requests rainbow740688652to67108864,TT442981120to67108864,river17920unchanged,TTF32743010560to67108864. Request sizes are not measured memory footprint or speed. RawreportSHA{old.sha(P['direct_control_report']['path'])}.\n\n"
entry+=f"Two fresh full feature/primary builds terminal0;3acceptedfiles restored aftereach. Frozenprimary{old.sha(H/'protocol.json')}:V087unit88pass/4ignored; exactlyB287/E087R1,E087R2/B288,B289/E087R3. All18fullnontimingresults/138checkpoints exactE020C1. No exclusions,extension orhistoricaltimingpooling. Sumfixturemedians{perf['baseline_full_cycle_ms']}to{perf['candidate_full_cycle_ms']}ms;unroundedgain{perf['observed_gain_pct']}%. Guards"+json.dumps(perf['fixture_regression_guard'],separators=(',',':'))+'. '+reason+'\n\n'
entry+=f"Root{root['checks']}raw/arithmetic checks; assessmentSHA{old.sha(qp)}. {len(pub)}smallartifactsHTTPbyteverified. Primarywholearenafingerprints/fullscientificrecords exact; wholeprimaryrawarenabytes not independently compared. Allownedchildren terminal, GPUlockabsent, accepted/main/live/protectedPTXcustody passed. No adoption/push/livechange;E08014.7414188354%measuredcumulativegain unchanged. LastprimaryB289,goalactive.\n"
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: test bounded pinned GPU transfers','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'guard_failures':[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']],'HTTP_files':len(pub)}),flush=True)
