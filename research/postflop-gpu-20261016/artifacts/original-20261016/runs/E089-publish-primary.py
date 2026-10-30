import sys,json,shutil,subprocess,urllib.request
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E080-live-20261018'
sys.path.insert(0,str(C));import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
H=R/'runs/E089-primary-plan';P=old.read(H/'protocol.json');qp=R/'comparisons/E089-three-pair-comparison/report.json';rp=R/'comparisons/E089-root-crosscheck/report.json'
q,root=old.read(qp),old.read(rp);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[]and q['extension_runs']==q['historical_timing_samples_used']==0
assert old.read(R/'runs/E089-primary-wrapper/complete.json')['all_children_terminal']
for p,h in P['input_sha256'].items():old.pin(p,h)
direct=old.read(P['direct_control_report']['path']);resources=old.read(R/'runs/E089-resource/report.json')
O=R/'runs/E089-initial-closure';O.mkdir(exist_ok=False)
reason=f"The fixed complete-solve comparison showed {perf['observed_gain_pct']:.6f}% aggregate improvement. All 18 full results, 138 checkpoints, 86 ordinary tests and 1,820 direct GPU comparisons passed. "
if passed:reason+='The initial speed gate passed. Separate fresh 16-pair confirmation, broader state checks, actual resource and capacity checks, holdout and fresh-original cumulative qualification remain. Not adopted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded 1% cutoff')
 failures=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if failures:why.append('repeatable fixture slowdown: '+', '.join(failures))
 reason+='Rejected: '+'; '.join(why)+'. The exact serial card-loop directive is closed, with no factor, loop, helper, subset, placement, width or extra-sample rescue.'
old.save(O/'decision.json',{'id':'E089','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'direct_GPU_pairs':1820,'direct_GPU_launches':3640,'direct_reader_checks':direct['checks'],'raw_control_report_sha256':old.sha(P['direct_control_report']['path']),'resource_report_sha256':old.sha(R/'runs/E089-resource/report.json'),'assessment_sha256':old.sha(qp),'root_replay_sha256':old.sha(rp),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E080','no_exclusions_extensions_pooling':True,'fresh16_broad_material_holdout_cumulative_run':False,'reason':reason})
folders=[R/'runs/D140-serial-card-loop',R/'runs/E089-source',R/'runs/E089-resource',R/'runs/E089-kernel-control',R/'runs/E089-direct-audit',R/'comparisons/E089-kernel-control-root-check',R/'runs/E089-build-plan',H,R/'runs/E089-primary-wrapper',R/'runs/E089-native-execution',O,qp.parent,rp.parent]
pub=[]
for folder in folders:
 for p in sorted(folder.rglob('*')):
  if not p.is_file()or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
  key=folder.name+'/'+p.relative_to(folder).as_posix();dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
for phase in ['feature','primary']:
 for p in (R/'runs/E089-final-build'/phase).iterdir():
  if not p.is_file()or p.suffix not in ['.json','.log']:continue
  key='E089-final-build-'+phase+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==p.read_bytes()
  pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='E089')
 x.update(status='measured'if passed else'rejected',correctness='pass',accepted=False,stage='Initial pass; fresh confirmation pending'if passed else'Closed: performance gate failed',reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
 x['evidence'] += [{'label':'Complete-solve comparison','url':'evidence/E089-three-pair-comparison/report.json'},{'label':'Full-record arithmetic replay','url':'evidence/E089-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E089-initial-closure/decision.json'}]
 x=next(x for x in s['experiments']if x['id']=='D140');x['reason']='No matching showdown loop directive was found in 400 retained CUDA sources. The compiler prerequisite and 1,820 direct GPU comparisons passed. Whole-solve speed is assessed separately in E089.'
 s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E089'if passed else None,stage='E089 separate confirmation preparation'if passed else'Investigating the next independent GPU mechanism',activity=reason+' Accepted E080 remains live with 14.74% measured cumulative improvement on the registered warm-cache benchmarks.')
 old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'bulk_raw_physical_S_only':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### D140 and E089 serial showdown loop'not in raw
entry=f"""

### D140 and E089 serial showdown loop

Previous goal turn completed E087 and rejected its fixture tradeoffs. This turn first declined duplicate generic-cache and fold-shuffle leads (D139/E088), preserving the unexecuted source/protocol and attribution correction. A bounded audit then found no pragma in 400 retained up_show source bodies or matching all-local-ref history. New E089 adds only pragma unroll 1 to the existing inner serial card-correction loop. It leaves every iteration, predicate, operand, ordered floating recurrence, prefix/cache/barrier, ABI, host, launch, graph, precision, quality and save path unchanged. This is distinct from E042's up_action hand-loop unroll and the closed cache/prefix forms. Source reversal is exact.

Frozen resource protocol {old.sha(R/'runs/E089-resource/protocol.json')}: one Rust compiler and one resource process, four NVRTC compilations for 120/75. Both target entries are smaller; other eight normalized entries, 27-parameter ABI and barrier sites match. Actual registers 38 to 40; local 0, static shared 1040, dynamic 22600, max threads 1024, context stack and checked occupancy remain unchanged. Smaller virtual code is not measured instruction-cache behavior or speed. No performance counters.

The original 364 physical showdown cases and five widths ran once: 1820 pairs and 3640 launches using the sealed PTX. Full 986200 active output words, 6464120 guards, 15329720 actual immutable input words, 417280 nonfinite output words and two sparse rounding witnesses passed. All 21 actual input buffers match. Separate raw reader passed {direct['checks']} checks. Raw 194327502 bytes remain physically on S, SHA {direct['raw_sha256']}. These are finite controls, not universal NaN/address proof.

Two fresh feature/primary builds finished successfully and restored accepted CUDA after each. Pre-native freezer review corrected the copied unit ID to V089 and limited the raw-control scope text before any protocol or sample. Frozen primary {old.sha(H/'protocol.json')}: V089 has 86 passed, four ignored; exactly B290/E089R1, E089R2/B291, B292/E089R3. All 18 full non-timing results and 138 checkpoints match unchanged E020C1. No exclusions, extensions or historical pooling. Sum fixture medians {perf['baseline_full_cycle_ms']} to {perf['candidate_full_cycle_ms']} ms; unrounded aggregate {perf['observed_gain_pct']}%. Guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}.

{reason}

Root replay passed {root['checks']} arithmetic/raw-record checks; assessment SHA {old.sha(qp)}. {len(pub)} small artifacts were HTTP byte-verified. Primary full scientific records and whole-arena fingerprints match; whole primary raw arena bytes were not independently compared. All owned children are terminal, GPU lock absent, accepted/main/live/protected PTX custody passed. No adoption, push or live change. Accepted E080 remains 14.7414188354% measured cumulative gain, last primary B292, goal active.
"""
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: test serial showdown loop generation','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'guard_failures':[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']],'HTTP_files':len(pub)}),flush=True)
