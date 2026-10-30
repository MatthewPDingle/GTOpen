"""Publish the fixed E084 screen, preserving all attempts and samples."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody()
assert not(R/'gpu-run.lock').exists()
H=R/'runs/E084-primary-plan-r2'
P=old.read(H/'protocol.json')
qpath=R/'comparisons/E084-three-pair-comparison/report.json'
rootpath=R/'comparisons/E084-root-crosscheck/report.json'
q,root=old.read(qpath),old.read(rootpath)
perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']
assert root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[]and q['extension_runs']==q['historical_timing_samples_used']==0
for p,h in P['input_sha256'].items():old.pin(p,h)
x=old.read(R/'runs/E084-primary-manager/primary.exit.json')
assert x['returncode']==0and x['error']is x['cleanup']is None
O=R/'runs/E084-initial-closure'
O.mkdir(exist_ok=False)
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All18 full non-timing results,138 checkpoints,86 ordinary tests and1820 direct GPU pairs passed. "
if passed:
    reason+='Initial timing passed; separate fresh16 confirmation, broader accuracy/compatibility, actual material/capacity, holdout and fresh-original cumulative qualification remain. Not adopted.'
else:
    why=[]
    if perf['observed_gain_pct']<1:why.append('below the unrounded1%cutoff')
    failures=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
    if failures:why.append('repeatable fixture slowdown: '+', '.join(failures))
    reason+='Rejected: '+'; '.join(why)+'. Close this exact first-card full-sum cache and retired-scan-storage form. No extra samples, widths, card subsets, thresholds, helpers, encodings, caller/source-scope or placement variants.'
decision={'id':'E084','at':old.now(),'decision':q['decision'],'performance':perf,
    'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,
    'direct_pairs':1820,'direct_launches':3640,'direct_report_sha256':P['direct_control_report']['sha256'],
    'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),
    'preparation_label_collision_preserved':True,'pre_native_label_repair_sha256':old.sha(R/'runs/E084-primary-preparation-repair/report.json'),
    'resource_registers_before_after':[38,39],'resource_local_static_dynamic_and_residency_unchanged':True,
    'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,
    'source_adopted':False,'accepted_and_live_source':'E080','no_exclusions_extensions_pooling':True,
    'fresh16_broad_material_holdout_cumulative_run':False,'reason':reason}
old.save(O/'decision.json',decision)
pub=[]
folders=[H,R/'runs/E084-primary-plan',R/'runs/E084-primary-preparation-repair',
         R/'runs/E084-build-plan',R/'runs/E084-primary-wrapper',R/'runs/E084-native-execution',
         R/'runs/E084-primary-manager',O,qpath.parent,rootpath.parent]
for folder in folders:
    for p in sorted(folder.rglob('*')):
        if not p.is_file()or p.suffix not in['.json','.py','.rs','.cu','.patch','.log']:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix()
        dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes(),key
        pub.append(key)
for phase in['feature','primary']:
    for p in(R/'runs/E084-final-build'/phase).iterdir():
        if not p.is_file()or p.suffix not in['.json','.log']:continue
        key='E084-final-build-'+phase+'/'+p.name
        dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS)
    e=next(x for x in s['experiments']if x['id']=='E084')
    e.update(status='measured'if passed else'rejected',correctness='pass',accepted=False,
             stage='Initial pass; fresh confirmation pending'if passed else'Closed: performance gate failed',
             reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],
             full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
    e['evidence'].extend([
        {'label':'Fixed complete-solve comparison','url':'evidence/E084-three-pair-comparison/report.json'},
        {'label':'Raw result and arithmetic replay','url':'evidence/E084-root-crosscheck/report.json'},
        {'label':'Initial decision and preparation attribution','url':'evidence/E084-initial-closure/decision.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',
             active_experiment='E084'if passed else None,
             stage='E084 fresh confirmation preparation'if passed else'Investigating the next independent GPU mechanism',
             activity=reason+' Accepted/live E080 remains14.74% faster on the registered complete-solve suite.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,
    'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'candidate_adopted':False})

ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md'
raw=ledger.read_bytes()
assert b'### D135 and E084 showdown first-card totals'not in raw
entry='''

### D135 and E084 showdown first-card totals

D134/E083 remains rejected at its frozen component gates. Bounded source scout found river card lists and strength boundaries already use a single pass/merge; no candidate created there. Separate showdown hypothesis reuses only the full first-card serial sum, never the sum of independently accumulated cards. After the original final scan barrier retires chunk_sum, each card writer accumulates its complete original ordered reach list from positivezero into the first52 existing shared words; one new CTA barrier precedes hand consumers. Original first-card lower/higher loops remain. tot_c starts from exactly the first-card serial accumulator, then performs every original second-card addition. Every other floating expression, scan/barrier, host/ABI/launch/layout/quality/save remains. No E029/E063/E077/E082/E083 hunk composed. Local all-ref/current-ledger matching audit is bounded novelty only. Ordered-operand/source-reversal/storage-lifetime control passed; no speed inferred from counts.

One sealed resource compiler/process, four NVRTC compiles at120/75. Other8PTXentries and27argument ABI match. Registers38to39; local0/static1040/dynamic22600/maxthreads1024/contextstack1024 and64/128/256 theoretical occupancy4 unchanged. Full physical showdown corpus unchanged:364cases x5widths,1820pairs/3640launches. All986200activewords,6464120guardchecks,15329720actual input words,417280nonfinite output words and2rounding witnesses pass. Separate decoder105571checks; all21input buffers identical. Raw194327502bytes SHA e5c2fe9939e18e97d6537cc844f1699d1b21a98d92035d55ba11a5b202f5415b staysS. Finite controls, not universal NaN/address/synchronization proof.

Two fresh isolated full builds terminal0, accepted E080 CUDA restored after each. Build stdout inherited an obsolete E051 display label; restoration records and actual162source hashes verify E080. First timing-preparer stopped before writing protocol because reused V082-unit identity already existed. Original four generated scripts preserved. Observer-only label repair uses V084-unit and primary-plan-r2; no source/binary/workload/order/gate changes, no native samples existed or were repeated. Repaired frozen primary '''+old.sha(H/'protocol.json')+'''. V084unit86pass/4ignored. Exactly B278/E084R1,E084R2/B279,B280/E084R3. All18fullnon-timingrecords/138checkpoints exact unchangedE020C1. No historical timing pooling/exclusions/extensions. Sum fixture-median complete cycles '''+str(perf['baseline_full_cycle_ms'])+' -> '+str(perf['candidate_full_cycle_ms'])+'ms, unrounded gain '+str(perf['observed_gain_pct'])+'%. Guards '+json.dumps(perf['fixture_regression_guard'],separators=(',',':'))+'. '+reason+'\n\nRoot '+str(root['checks'])+' raw/arithmetic checks; assessmentSHA '+old.sha(qpath)+'. All'+str(len(pub))+' small artifacts HTTP byte-verified. Primary whole-arena fingerprints/full scientific records exact; whole raw primary arena bytes not independently compared. All owned children terminal, GPUlockabsent, accepted/main/live/protected PTX custody passed. No adoption/livechange; E08014.7414188354% measured cumulative gain remains. Last primaryB280, goalactive.\n'
nl=b'\r\n'if b'\r\n'in raw else b'\n'
ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: screen cached showdown first-card totals','--',
                'research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],
                  'guard_failures':[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']],
                  'HTTP_files':len(pub)}),flush=True)
