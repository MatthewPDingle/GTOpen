"""Record the original fixed primary outcome without qualification rescue."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
old.custody();assert not(R/'gpu-run.lock').exists()
H=R/'runs/E085-primary-plan';P=old.read(H/'protocol.json')
qp=R/'comparisons/E085-three-pair-comparison/report.json'
rp=R/'comparisons/E085-root-crosscheck/report.json'
q,root=old.read(qp),old.read(rp);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']
assert root['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[] and q['extension_runs']==q['historical_timing_samples_used']==0
for p,h in P['input_sha256'].items():old.pin(p,h)
x=old.read(R/'runs/E085-primary-manager/primary.exit.json')
assert x['returncode']==0 and x['error'] is x['cleanup'] is None
direct=old.read(P['direct_control_report']['path'])
resources=old.read(R/'runs/E085-resource-r2/report.json')
O=R/'runs/E085-initial-closure';O.mkdir(exist_ok=False)
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All18 full non-timing results,138 checkpoints,86 ordinary tests and819direct GPU pairs passed. "
if passed:
    reason+='Initial gate passed. Separate fresh16 confirmation, broader exactness/compatibility, material/capacity, holdout and fresh-original cumulative gates remain. Not adopted.'
else:
    why=[]
    if perf['observed_gain_pct']<1:why.append('below the unrounded1%cutoff')
    failures=[g['fixture_id']for g in perf['fixture_regression_guard']if g['failed']]
    if failures:why.append('repeatable fixture slowdown: '+', '.join(failures))
    reason+='Rejected: '+'; '.join(why)+'. Close this exact strategy streaming-store form; no cache-operator, other-array, threshold, helper/clobber/source-scope/placement variant or additional sample rescue.'
decision={'id':'E085','at':old.now(),'decision':q['decision'],'performance':perf,
    'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,
    'direct_pairs':819,'direct_launches':1638,'direct_reader_checks':direct['checks'],
    'direct_control_report_sha256':P['direct_control_report']['sha256'],
    'resource_report_sha256':old.sha(R/'runs/E085-resource-r2/report.json'),
    'assessment_sha256':old.sha(qp),'root_replay_sha256':old.sha(rp),
    'precompiler_emission_observer_correction_sha256':old.sha(R/'runs/E085-resource-r2/precompile-observer-correction.json'),
    'precompiler_correction_original_compiler_native_observations':0,
    'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,
    'source_adopted':False,'accepted_and_live_source':'E080','no_exclusions_extensions_pooling':True,
    'fresh16_broad_material_holdout_cumulative_run':False,'reason':reason}
old.save(O/'decision.json',decision)
pub=[]
folders=[R/'runs/D136-strategy-streaming-store',R/'runs/E085-source',R/'runs/E085-resource',
    R/'runs/E085-resource-r2',R/'runs/E085-resource-manager',R/'runs/E085-kernel-control',
    R/'runs/E085-direct-manager',R/'comparisons/E085-kernel-control-root-check',
    R/'runs/E085-build-plan',R/'runs/E085-build-manager',H,R/'runs/E085-primary-wrapper',
    R/'runs/E085-native-execution',R/'runs/E085-primary-manager',O,qp.parent,rp.parent]
for folder in folders:
    for p in sorted(folder.rglob('*')):
        if not p.is_file() or p.suffix not in ['.json','.py','.rs','.cu','.patch','.log']:continue
        key=folder.name+'/'+p.relative_to(folder).as_posix()
        dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes(),key
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes(),key
        pub.append(key)
for phase in ['feature','primary']:
    for p in (R/'runs/E085-final-build'/phase).iterdir():
        if not p.is_file() or p.suffix not in ['.json','.log']:continue
        key='E085-final-build-'+phase+'/'+p.name
        dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E085')
    e.update(status='measured' if passed else 'rejected',correctness='pass',accepted=False,
        stage='Initial pass; fresh confirmation pending' if passed else 'Closed: performance gate failed',
        reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],
        full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
    e['evidence'].extend([
        {'label':'Fixed complete-solve comparison','url':'evidence/E085-three-pair-comparison/report.json'},
        {'label':'Full record and arithmetic replay','url':'evidence/E085-root-crosscheck/report.json'},
        {'label':'Initial decision','url':'evidence/E085-initial-closure/decision.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',
        active_experiment='E085' if passed else None,
        stage='E085 fresh confirmation preparation' if passed else 'Investigating the next independent GPU mechanism',
        activity=reason+' Accepted/live E080 remains14.74% faster on the registered complete-solve benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,
    'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes()
assert b'### D136 and E085 strategy streaming stores' not in raw
entry='''

### D136 and E085 strategy streaming stores

Previous turn closed D134/E083 at component admission and E084 at complete-solve regression, leaving E080 accepted/live. New bounded local all-ref/retained-CU/current-ledger audit found no strategy-output streaming-store implementation. E033/E034 context metadata reservation, E054 early parent-CFV publication, E075 immutable LDU loads and E084 first-card reuse remain closed; no such hunks composed. Existing river lists already single-pass and historical isolated rank work6.9594ms do not motivate union-rank work; no new ranking candidate or sample.

One CUDA assignment replaced at its original location: updated_strategy retains exactly strat_p[idx]*ds+reach*sig, then volatile st.global.cs.f32 with typed64bit pointer/float operands and memory clobber stores the same word. Original regret/CFV stores, floating expressions/order, locks/opponents, dispatch, host, launch, graph, allocations, quality and saves unchanged. Source reversal exact. CUDA PTX cache-operator and inline-assembly primary docs recorded. Source suggests a cache-retention hypothesis only: next iteration still reads the strategy and assembly can alter scheduling; no measured miss/causal/no-tradeoff assertion.

Before any compiler/native observation, source audit corrected the emission observer: static4stores assumed one per template although unrolling can emit multiple. Original protocol/scripts preserved; r2 requires streaming-store presence, shared helper source and direct corpus cover all four dispatch forms. Candidate/Rust probe/resource/math/performance gates unchanged;0original compiler/native runs, no observations repeated. One resource compiler/process,fourNVRTCcompiles120/75: other8PTXentries and20argument ABI exact. Actual registers62to56, local64/static0/dynamic0/maxthreads1024/stack1024 unchanged; theoretical128thread residency8to9,64thread16to18,256thread4same. No speed inferred from occupancy.

Original819up_action cases/1638launches use sealed120PTX, unchanged descriptors/discounts/inputs and full outputs. Both players/roles/locks, common/generic wide menus, tails/count0,64/128/256widths and signedzero/subnormal/nonfinite/overflow pass. All12,375,858mutable output words,5,199,114actual immutable words and10,240,828guards checked; actual mutable allocations and parent-childCFV rows disjoint. Separate raw reader63,899checks. All5full raw files stayS; finite scoped controls, no universal malformed-address/NaN proof.

Two fresh isolated feature/primary builds terminal0; accepted E080 CUDA restored aftereach. Frozen primary '''+old.sha(H/'protocol.json')+''': V085unit86pass/4ignored, exactly B281/E085R1,E085R2/B282,B283/E085R3. All18full non-timing records/138checkpoints exact unchangedE020C1. No exclusions/extensions/historypooling. Sum fixture-median completecycle '''+str(perf['baseline_full_cycle_ms'])+' -> '+str(perf['candidate_full_cycle_ms'])+'ms; unrounded gain '+str(perf['observed_gain_pct'])+'%. Guards '+json.dumps(perf['fixture_regression_guard'],separators=(',',':'))+'. '+reason+'\n\nRoot '+str(root['checks'])+'raw/arithmetic checks; assessmentSHA '+old.sha(qp)+'. '+str(len(pub))+'small artifacts HTTP byte-verified, rawbulkS. Primary whole-arena fingerprints/full records exact; primary whole raw arena bytes not independently compared. All owned children terminal, GPUlockabsent, accepted/main/live/protectedPTX custody passed. No adoption/livechange; accepted E08014.7414188354% measured cumulative gain unchanged,lastprimaryB283,goalactive.\n'
nl=b'\r\n' if b'\r\n' in raw else b'\n'
ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: screen streaming strategy output stores','--',
                'research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],
    'guard_failures':[g['fixture_id']for g in perf['fixture_regression_guard']if g['failed']],
    'HTTP_files':len(pub)}),flush=True)
