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
H=R/'runs/E086-primary-plan';P=old.read(H/'protocol.json')
qp=R/'comparisons/E086-three-pair-comparison/report.json'
rp=R/'comparisons/E086-root-crosscheck/report.json'
q,root=old.read(qp),old.read(rp);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']
assert root['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
assert q['excluded_samples']==[] and q['extension_runs']==q['historical_timing_samples_used']==0
for p,h in P['input_sha256'].items():old.pin(p,h)
x=old.read(R/'runs/E086-primary-manager/primary.exit.json')
assert x['returncode']==0 and x['error'] is x['cleanup'] is None
direct=old.read(P['direct_control_report']['path'])
resources=old.read(R/'runs/E086-resource/report.json')
O=R/'runs/E086-initial-closure';O.mkdir(exist_ok=False)
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All18 full non-timing results,138 checkpoints,86 ordinary tests and425direct GPU pairs passed. "
if passed:
    reason+='Initial gate passed. Separate fresh16 confirmation, broader exactness/compatibility, material/capacity, holdout and fresh-original cumulative gates remain. Not adopted.'
else:
    why=[]
    if perf['observed_gain_pct']<1:why.append('below the unrounded1%cutoff')
    failures=[g['fixture_id']for g in perf['fixture_regression_guard']if g['failed']]
    if failures:why.append('repeatable fixture slowdown: '+', '.join(failures))
    reason+='Rejected: '+'; '.join(why)+'. Close this exact unsigned64 length1 up_chance bit-field form; no other-kernel, packing, width, precision, helper, threshold, source-scope or placement variant or additional sample rescue.'
decision={'id':'E086','at':old.now(),'decision':q['decision'],'performance':perf,
    'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,
    'direct_pairs':425,'direct_launches':850,'direct_reader_checks':direct['checks'],
    'direct_control_report_sha256':P['direct_control_report']['sha256'],
    'resource_report_sha256':old.sha(R/'runs/E086-resource/report.json'),
    'assessment_sha256':old.sha(qp),'root_replay_sha256':old.sha(rp),
    'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,
    'source_adopted':False,'accepted_and_live_source':'E080','no_exclusions_extensions_pooling':True,
    'fresh16_broad_material_holdout_cumulative_run':False,'reason':reason}
old.save(O/'decision.json',decision)
pub=[]
folders=[R/'runs/D137-bitfield-membership',R/'runs/E086-source',R/'runs/E086-resource',
    R/'runs/E086-resource',R/'runs/E086-resource-manager',R/'runs/E086-kernel-control',
    R/'runs/E086-direct-manager',R/'comparisons/E086-kernel-control',
    R/'runs/E086-build-plan',R/'runs/E086-build-manager',H,R/'runs/E086-primary-wrapper',
    R/'runs/E086-native-execution',R/'runs/E086-primary-manager',O,qp.parent,rp.parent]
for folder in dict.fromkeys(folders):
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
    for p in (R/'runs/E086-final-build'/phase).iterdir():
        if not p.is_file() or p.suffix not in ['.json','.log']:continue
        key='E086-final-build-'+phase+'/'+p.name
        dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
        if dst.exists():assert dst.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dst)
        with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as response:
            assert response.read()==p.read_bytes()
        pub.append(key)
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E086')
    e.update(status='measured' if passed else 'rejected',correctness='pass',accepted=False,
        stage='Initial pass; fresh confirmation pending' if passed else 'Closed: performance gate failed',
        reason=reason,baseline_full_cycle_ms=perf['baseline_full_cycle_ms'],
        full_cycle_ms=perf['candidate_full_cycle_ms'],observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now())
    e['evidence'].extend([
        {'label':'Fixed complete-solve comparison','url':'evidence/E086-three-pair-comparison/report.json'},
        {'label':'Full record and arithmetic replay','url':'evidence/E086-root-crosscheck/report.json'},
        {'label':'Initial decision','url':'evidence/E086-initial-closure/decision.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',
        active_experiment='E086' if passed else None,
        stage='E086 fresh confirmation preparation' if passed else 'Investigating the next independent GPU mechanism',
        activity=reason+' Accepted/live E080 remains14.74% faster on the registered complete-solve benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(O/'publication.json',{'at':old.now(),'HTTP_verified_artifacts':pub,
    'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'candidate_adopted':False})

ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md'
raw=ledger.read_bytes()
assert b'### D137 and E086 chance bit-field extraction' not in raw
entry='''

### D137 and E086 chance bit-field extraction

Previous goal turn progressed by closing E085 after0.5220789829%initial gain and strict two-tone guard failure. Current turn revalidates accepted source/main/live/protectedPTX custody and idle GPU. The accepted private up_chance PTX already lowers original left-onehot/AND to right-shift/AND, so an ordinary source-direction rewrite is declined without a candidate. New bounded current-ledger/retained-CU/all-local-ref audit found no explicit bfe.u64 form. E048canonical-card-comparison/removed-mask, E039sharedmetadata, E046packing and E085streaming-store forms stay closed; no hunk composed.

One CUDA-only candidate changes just up_chance's integer membership predicate to pure register unsigned64bit-field extraction, positioncc_card[t], length1. Typed64bit input/output and32bit position, no hidden memory or volatile/clobber needed. Original mask/card arrays, ABI, selected children, all ordered float additions/products, loop/permutation, other8kernels, host/launch/graph, allocation/quality/save retained. Source reversal exact. CPU85,336 canonical/basis/complement checks pass; actual GPU and performance not inferred. NVIDIA PTX bit-field semantics primary source recorded. Virtual instruction may lower to identical or slower native code; no SASS-speed claim.

One sealed resource compiler/process,4NVRTCcompiles120/75. Other8normalized entries and15argumentABI exact, bfe emitted onlycandidate. Actual30registers/local0/static0/dynamic0/maxthreads1024/stack1024 and64/128/256theoreticaloccupancy24/12/6 unchanged. Reuse original425canonical chance descriptors/order:157down unchanged controls plus268up cases,850launches. Delete only historical candidate card-ID ABI builder branches so both variants use original mask ABI; complete original card-ID/mask images still read back. Corpus metadata changes only ID/rawmagic labels. All18,950,844full output words,3,951,272actual immutable words,13,112,256guards and1,840,420independent finite down membership relations pass. Every canonical1326hand/dealt52card relation individually exercised; tails/count0/empty/permutation/nonfinite/subnormal/overflow/fivewidth controls retained. Separate raw reader2,508,695checks. All3full raw files stayS. Finite corpus/small offsets, no malformed-address/universal NaN proof.

Two fresh isolated feature/primary builds terminal0, E080 CUDA restored aftereach. Frozen primary '''+old.sha(H/'protocol.json')+''': V086unit86pass/4ignored; exactly B284/E086R1,E086R2/B285,B286/E086R3. All18complete non-timing records/138checkpoints exact unchangedE020C1, no exclusions/extensions/historical pooling. Sum fixture-median completecycle '''+str(perf['baseline_full_cycle_ms'])+' -> '+str(perf['candidate_full_cycle_ms'])+'ms, unrounded gain '+str(perf['observed_gain_pct'])+'%. Guards '+json.dumps(perf['fixture_regression_guard'],separators=(',',':'))+'. '+reason+'\n\nRoot '+str(root['checks'])+'raw/arithmetic checks, assessmentSHA '+old.sha(qp)+'. '+str(len(pub))+'small artifacts HTTPbyte-verified. Primary full scientific records/whole-arena fingerprints exact; full raw primary arena bytes not independently compared. All owned children terminal, GPUlockabsent, accepted/main/live/protectedPTX custody passed. No adoption/livechange. Accepted E08014.7414188354%measured cumulative gain unchanged,lastprimaryB286,goalactive.\n'
nl=b'\r\n' if b'\r\n' in raw else b'\n'
ledger.write_bytes(raw+entry.encode().replace(b'\n',nl))
subprocess.run(['git','commit','--only','-m','research: screen chance bit-field extraction','--',
                'research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],
    'guard_failures':[g['fixture_id']for g in perf['fixture_regression_guard']if g['failed']],
    'HTTP_files':len(pub)}),flush=True)
