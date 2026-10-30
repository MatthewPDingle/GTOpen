"""Freeze, execute once, assess and publish the E070 initial screen."""
from pathlib import Path
import json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (R/'gpu-run.lock').exists()
old.ar.refuse_active(old.ar.live_status())
assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E070-final-build/complete.json';built=old.read(build)
assert built['all_compilers_terminal'] and built['native_executions']==0
for path,h in built['evidence_sha256'].items():old.pin(path,h)
host=R/'runs/E070-direct-kernel-controls/host-integration'
hm=old.read(host/'manifest.json')
assert hm['files']==7 and hm['baseline_source_sha256']=={k:old.BASE[k] for k in hm['candidate_source_sha256']}
for rel,h in hm['candidate_source_sha256'].items():old.pin(host/'candidate'/rel,h)
control_path=R/'runs/E070-input-contract-correction/complete.json'
control=old.read(control_path)
assert control['status']=='pass_scoped_seven_entry_exact_controls_with_recorded_fixture_correction' and control['cases']==5953 and control['application_kernel_launches']==11906 and control['source_main_live_PTX_custody_pass'] and control['all_owned_child_handles_terminal']
H=R/'runs/E070-primary-plan';prep=old.read(H/'preparation.json')
for name,h in prep['source_sha256'].items():old.pin(H/name,h)
P=old.read(R/'runs/E069-primary-plan/protocol.json')
P.pop('cpu_control_report')
P.update(id='E070-primary',at=old.now(),candidate_owned_sha256=hm['candidate_source_sha256'],build_protocol_sha256=old.sha(R/'runs/E070-build-plan/build-protocol.json'),ordinary_unit_id='V070-unit',control_ids=['V070-unit'],pairs=prep['pairs'],measurement_order=prep['measurement_order'],direct_control_report={'path':str(control_path),'sha256':old.sha(control_path)},source_scope='Seven-file private device metadata integration: original u8 player and arity pack into one u16, high8player/low8arity, device payload8*N to2*N. CPU plan vectors and public budget formulas unchanged; one temporary2*N host vector remains in constructor scope. All seven CUDA entry ABIs and ten callers covered. Floating expressions, reductions, launch geometry/order/count, quality checks and save schema unchanged. Complete-cycle clocks include packing, upload, NVRTC/JIT and all init costs. Main down-action registers40to46 and theoretical blocks/SM12to10 are retained resource warnings; material impact still requires full qualification. Direct5953case pairs exact with preserved original invalid-actor harness stop and correction of twelve previously unexecuted descriptors to source-valid255. No completed GPU pair repeated. Integrated exact state, continuation, F32, memory/capacity and material checks remain required before adoption.')
paths=[Path(__file__),build,control_path,R/'runs/E070-build-plan/build-protocol.json',host/'manifest.json',host/'candidate.patch',host/'abi-source-audit.json',host/'syntax-and-integer-report.json',R/'runs/E070-resource/report.json',R/'runs/E070-direct-kernel-controls/helper-resource/report.json',R/'runs/E070-input-contract-correction/diagnosis.json',R/'runs/E070-input-contract-correction/protocol-r2.json',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',H/'preparation.json',*[H/n for n in prep['source_sha256']]]
for stem in ['E070-feature-solver','E070-solver','E070-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp)
 old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'] and m['build_protocol_sha256']==P['build_protocol_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:
 assert not (R/'runs'/identity).exists() and not any(x['id']==identity for x in st['experiments'])
for name in ['E070-native-execution','E070-primary-wrapper','E070-primary-manager']:
 assert not (R/'runs'/name).exists()
for name in ['E070-three-pair-comparison','E070-root-crosscheck']:
 assert not (R/'comparisons'/name).exists()
P['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'protocol.json',P)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes()
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
 return {'path':str(src),'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(x,H.name+'/'+x.name) for x in H.iterdir() if x.is_file()]
old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'all_compilers_terminal':True,'native_primary_executions':0,'http_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E070')
 e.update(stage='Ordinary units then fixed three-pair complete-solve screen',reason='Both isolated builds completed; accepted source restored. Seven-entry5953case-pair controls exact, with original harness error and prospective unexecuted-input correction preserved. Frozen BC/CB/BC screen includes all packing/setup costs; down-action resource warning retained. No speed claim yet.')
 e['evidence'].append({'label':'Frozen three-pair 1% complete-solve screen','url':'evidence/E070-primary-plan/protocol.json'})
 st.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E070',stage='E070 fixed primary screen',activity='Full-access/never native execution is operational. Running84ordinary units, then exactly B226/E070R1,E070R2/B227,B228/E070R3. Same quality and unchanged strict fixture guard.');old.ar.atomic_json(old.ar.STATUS,st)
manager=R/'runs/E070-primary-manager';manager.mkdir();ph=old.sha(H/'protocol.json');print('E070 frozen primary protocol',ph,flush=True)
old.child([sys.executable,str(H/'run.py'),ph],manager,'primary',old.env(),2400)
qpath=R/'comparisons/E070-three-pair-comparison/report.json';rootpath=R/'comparisons/E070-root-crosscheck/report.json'
q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct'] and root['status']==('pass_initial_timing_only' if passed else 'pass_rejected')
assert q['excluded_samples']==[] and q['extension_runs']==0 and q['historical_timing_samples_used']==0
assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}
old.custody();assert not (R/'gpu-run.lock').exists()
out=R/'runs/E070-initial-closure';out.mkdir()
reason=f"Initial aggregate complete-solve gain {perf['observed_gain_pct']:.6f}%. All18 full non-timing results,138 checkpoints,84ordinary units and5953direct GPU case pairs passed. "
if passed:reason+='Initial gate passed; fresh16, broader exact compatibility, actual material resources/capacity and holdout/cumulative qualification remain. No adoption.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below unrounded1% cutoff')
 guards=[g['fixture_id'] for g in perf['fixture_regression_guard'] if g['failed']]
 if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
 reason+='Rejected: '+'; '.join(why)+'. No additional samples, widths, scope variants or rescue.'
decision={'id':'E070','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':84,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'direct_control_report_sha256':old.sha(control_path),'direct_GPU_case_pairs':5953,'direct_GPU_application_launches':11906,'original_input_contract_failure_preserved':True,'no_completed_direct_pair_repeated':True,'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_compared':False,'source_adopted':False,'accepted_source':'E051','fresh16_broader_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason}
old.save(out/'decision.json',decision)
published=[]
for folder in [H,R/'runs/E070-build-plan',R/'runs/E070-primary-wrapper',R/'runs/E070-native-execution',out,R/'comparisons/E070-three-pair-comparison',R/'comparisons/E070-root-crosscheck']:
 for x in folder.iterdir():
  if x.is_file() and x.suffix in ['.json','.py','.rs','.patch','.log']:published.append(publish(x,folder.name+'/'+x.name))
for phase in ['feature','primary']:
 for x in (R/'runs/E070-final-build'/phase).iterdir():
  if x.is_file() and x.suffix in ['.json','.log']:published.append(publish(x,'E070-final-build-'+phase+'/'+x.name))
for stem in ['E070-feature-solver','E070-solver','E070-postflop_autoresearch']:
 published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E070-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E070')
 e.update(status='measured' if passed else 'rejected',correctness='pass',stage='Initial pass; fresh16 and broader qualification pending' if passed else 'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False)
 e['evidence'].extend([{'label':'Fixed three-pair complete-solve assessment','url':'evidence/E070-three-pair-comparison/report.json'},{'label':'Raw-record and arithmetic replay','url':'evidence/E070-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E070-initial-closure/decision.json'}])
 st.update(updated_at=old.now(),state='running',active_experiment='E070' if passed else None,stage='E070 fresh16 preparation' if passed else 'Next independent GPU mechanism investigation',activity=reason+' Accepted E051 source and cumulative benchmark gain remain unchanged.');old.ar.atomic_json(old.ar.STATUS,st)
old.save(out/'publication.json',{'at':old.now(),'http_byte_verified_artifacts':published,'accepted_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E070 packed byte metadata' not in raw
entry=f'''\n\n### E070 packed byte metadata integrated initial screen\n\nFull-access/never native research is operational without approval prompts; no security configuration or database changes. Seven-file integration packs original u8player/arity into one private u16 (device8*Nto2*N), unchanged CPU plan and public budgets, temporary host2*Nvector included in complete-cycle costs. All seven CUDA entries/ten callers covered; no float expression, reduction, launch/quality/save-schema changes. Resource core48gates plus helper34gates pass; down-action40to46registers and theoretical12to10blocks/SM warning retained, not a no-tradeoff claim.\n\nExactly5953direct GPU case pairs/11906launches pass, with full raw bytes/immutables/guards and scoped helper CPU oracles. Original harness stops on actor=-1 outside sourceu8domain after819up+1172down cases; preserved. Twelve previously unexecuted descriptors corrected to255 in both arms with branch equivalence; remaining24down,1638eval,180fold,2120helper pairs completed exactly once. No completed pair repeated. Assessment-only parser repairs preserved; no extra GPU. Closure SHA{old.sha(control_path)}.\n\nTwo isolated feature/primary builds; accepted E051 restored after each. V070-unit84passed/4ignored. Fixed B226/E070R1,E070R2/B227,B228/E070R3, all18full non-timing results/138checkpoints exact. Sum fixture median complete-cycle clocks{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms; unrounded gain{perf['observed_gain_pct']:.10f}%. Strict fixture guards{json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root{root['checks']}raw/arithmetic checks; assessment SHA{old.sha(qpath)}. {reason}\n\nNo exclusions, extensions, historical timing pooling or adoption. Fresh16/broader/F32/state/save/resume/continuation/material/holdout/cumulative not yet run for E070. Whole arena fingerprints exact; primary raw arena bytes not independently compared. All{len(published)}published artifacts HTTP-byte verified; owned children terminal, accepted research/main/live/protected PTX unchanged. E051 accepted cumulative12.4372274192% remains unchanged. Last primary baseline B228.\n'''
nl=b'\r\n' if b'\r\n' in raw else b'\n';ledger.write_bytes(raw+entry.encode('utf-8').replace(b'\n',nl));old.custody()
print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_source':'E051','permission_block_resolved':True}),flush=True)
