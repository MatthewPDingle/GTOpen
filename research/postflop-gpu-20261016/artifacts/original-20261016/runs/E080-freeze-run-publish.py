"""Freeze and own exactly three full-solve pairs for zero-validation overlap."""
from pathlib import Path
import json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E080-final-build/complete.json';built=old.read(build);assert built['all_compilers_terminal']and built['native_executions']==0
for p,h in built['evidence_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E080-build-manager/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
d=R/'runs/D131-zero-check-setup-overlap/report.json';control=old.read(d)
assert control['admit_one_integrated_trial']and control['fixed_six_fresh_processes_complete']and len(control['full_layout_raw_replays'])==18 and control['ability_lifecycle_controls']==12 and control['ability_predicate_controls']==15 and control['all_owned_children_terminal']and control['source_main_live_PTX_custody_pass']
H=R/'runs/E080-primary-plan';assert not H.exists();H.mkdir()
for name in['native.py','assess.py','root-check.py','run.py']:
    code=(R/'runs/E079-primary-plan'/name).read_text(encoding='utf-8').replace('E079','E080').replace('e079','e080').replace('exact one-source scope','exact two-source scope')
    if name in['native.py','assess.py']:
        predicate="assert control['admit_one_integrated_trial'] and control['fixed_six_fresh_processes_complete'] and len(control['full_layout_raw_replays'])==18 and control['ability_lifecycle_controls']==12 and control['ability_predicate_controls']==15 and control['all_owned_children_terminal'] and control['source_main_live_PTX_custody_pass']"
        code,n=re.subn(r"assert control\['admit_one_integrated_trial'\][^\n]+",predicate,code);assert n==1
    compile(code,str(H/name),'exec');(H/name).write_text(code,encoding='utf-8',newline='\n')
source=old.read(R/'runs/E080-source/manifest.json');P=old.read(R/'runs/E079-primary-plan/protocol.json')
P.update(id='E080-primary',at=old.now(),candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E080-build-plan/build-protocol.json'),ordinary_unit_id='V080-unit',control_ids=['V080-unit'],pairs=[{'baseline':'B253','candidate':'E080R1'},{'baseline':'B254','candidate':'E080R2'},{'baseline':'B255','candidate':'E080R3'}],measurement_order=['B253','E080R1','E080R2','B254','B255','E080R3'],direct_control_report={'path':str(d),'sha256':old.sha(d)},source_scope=source['scope']+' The source-matched component passed 18 complete layout images, 12 lifecycle cases, 15 predicates, wrong-store and before/after controls. Complete clocks include tree construction, CPU allocation, all GPU initialization/NVRTC/JIT, quality checks, full solve and full readback. No component timings pooled into this score. No full-solve or material-cost conclusion yet.')
paths=[Path(__file__),build,d,*[R/'runs/D131-zero-check-setup-overlap'/n for n in['protocol.json','execution-plan.json','ability-report.json']],R/'runs/E080-build-plan/build-protocol.json',R/'runs/E080-source/manifest.json',R/'runs/E080-source/candidate-mod.rs',R/'runs/E080-source/candidate-arena.rs',R/'runs/E080-source/source-review.json',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),C/'common_e051_live.py',C/'protected-main.json',old.REPO/'crates/solver/src/gpu/kernels.cu',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in['native.py','assess.py','root-check.py','run.py']]]
for stem in['E080-feature-solver','E080-solver','E080-postflop_autoresearch']:
    exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for name in['E080-native-execution','E080-primary-wrapper','E080-primary-manager']:assert not(R/'runs'/name).exists()
for name in['E080-three-pair-comparison','E080-root-crosscheck']:assert not(R/'comparisons'/name).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)

def publish(src,key):
    dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists():assert dst.read_bytes()==src.read_bytes(),key
    else:shutil.copyfile(src,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
    return {'url':'evidence/'+key,'sha256':old.sha(src)}

pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()]
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'native_primary_executions':0,'all_compilers_terminal':True,'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080')
    e.update(stage='Ordinary tests, then three complete-solve pairs',reason='Fresh builds are terminal and accepted source is restored. Run 86 ordinary tests, then the fixed BC/CB/BC comparison. The unrounded 1% cutoff and strict fixture guards remain unchanged.');e['evidence'].append({'label':'Frozen full-solve screen','url':'evidence/E080-primary-plan/protocol.json'})
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 complete-solve comparison',activity='Run the ordinary suite, then exactly B253/E080R1, E080R2/B254, B255/E080R3. All initialization and readback costs stay in the complete clocks. Accepted and live E051 remain unchanged.')
    old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E080-primary-manager';O.mkdir();print('E080 primary protocol',old.sha(H/'protocol.json'),flush=True)
old.child([sys.executable,'-B',str(H/'run.py'),old.sha(H/'protocol.json')],O,'primary',old.env(),2400)
qpath=R/'comparisons/E080-three-pair-comparison/report.json';rootpath=R/'comparisons/E080-root-crosscheck/report.json';q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected')
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not(R/'gpu-run.lock').exists();out=R/'runs/E080-initial-closure';out.mkdir()
reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All 18 full non-timing results, 138 checkpoints and 86 ordinary tests passed. "
if passed:reason+='Initial gate passed. Separately frozen fresh16 confirmation, broad compatibility, actual CPU and memory costs, capacity, holdout and cumulative checks remain. Not accepted.'
else:
    why=[]
    if perf['observed_gain_pct']<1:why.append('below the unrounded 1% cutoff')
    guards=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
    if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
    reason+='Rejected: '+'; '.join(why)+'. No extra samples, threshold, thread, helper, scope, placement or eligibility variants, or rescue runs.'
decision={'id':'E080','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':86,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'component_full_layout_snapshots':18,'component_lifecycle_mocks':12,'component_predicates':15,'component_control_report_sha256':old.sha(d),'CUDA_source_unchanged':True,'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E051','fresh16_broad_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason}
old.save(out/'decision.json',decision);published=[]
for folder in[H,R/'runs/E080-build-plan',R/'runs/E080-primary-wrapper',R/'runs/E080-native-execution',out,qpath.parent,rootpath.parent]:
    for p in folder.iterdir():
        if p.is_file()and p.suffix in['.json','.py','.rs','.patch','.log']:published.append(publish(p,folder.name+'/'+p.name))
for phase in['feature','primary']:
    for p in(R/'runs/E080-final-build'/phase).iterdir():
        if p.is_file()and p.suffix in['.json','.log']:published.append(publish(p,'E080-final-build-'+phase+'/'+p.name))
for stem in['E080-feature-solver','E080-solver','E080-postflop_autoresearch']:published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E080-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080')
    e.update(status='measured'if passed else'rejected',correctness='pass',stage='Initial pass; confirmation and broader qualification pending'if passed else'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False)
    e['evidence'].extend([{'label':'Fixed full-solve assessment','url':'evidence/E080-three-pair-comparison/report.json'},{'label':'Raw-record arithmetic replay','url':'evidence/E080-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E080-initial-closure/decision.json'}])
    s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080'if passed else None,stage='E080 fresh confirmation preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain at 12.44% cumulative improvement on the registered benchmarks.')
    old.ar.atomic_json(old.ar.STATUS,s)
old.save(out/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'accepted_and_live_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E080 zero-validation overlap full-solve screen'not in raw
entry=f'''

### E080 zero-validation overlap full-solve screen

Frozen two-host-file source {json.dumps(P['candidate_owned_sha256'],separators=(',',':'))}. D131 admitted exactly one integrated form: original full serial zero scans overlap caller-only NVRTC/module/pinned/layout setup using one CPU worker and ephemeral immutable Store tokens. All four predicates run once, all original snapshot/inactive guards remain at consumption, CUDA context/stream/driver work and CPU plan/budget remain on original caller. Fixed >=64 MiB total q-byte eligibility; smaller/F32 paths retain original serial upload checks. No persistent provenance, changed scan grouping, kernel, precision, quality, layout, save, graph or payload changes. Component timing is not pooled into full-solve score.

Two fresh isolated feature/primary builds terminal zero; accepted E051 restored after each. Frozen primary {old.sha(H/'protocol.json')}, V080-unit 86 passed and 4 ignored. Added units exercise 12 actual helper success/error/panic/drop/priority combinations and token address, original predicate, immutable bits and snapshot guards. Fixed B253/E080R1, E080R2/B254, B255/E080R3; all 18 full non-timing payloads and 138 quality checkpoints exact. Sum fixture-median complete cycle {perf['baseline_full_cycle_ms']:.10f} to {perf['candidate_full_cycle_ms']:.10f} ms; unrounded gain {perf['observed_gain_pct']:.10f}%. Strict fixture guards {json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root replay made {root['checks']} raw/arithmetic checks; assessment SHA {old.sha(qpath)}. {reason}

No exclusions, extensions, historical pooling or adoption. Fresh16, broad F32/state/menu/save/resume/continuation, actual CPU/host/GPU peak/capacity/responsiveness, holdout and fresh-original cumulative qualification have not run for E080. Primary whole-arena fingerprints are exact; primary raw arenas were not independently byte-compared. All {len(published)} published artifacts were HTTP byte verified. All owned children are terminal, GPU lock released, accepted source, main checkout, live executable and protected PTX exact. E051 accepted/deployed 12.4372274192% unchanged; last primary B255; goal active.
'''
nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody()
subprocess.run(['git','commit','--only','-m','research: screen zero-validation overlap with complete-solve clocks','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True)
old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_and_live_source':'E051'}),flush=True)
