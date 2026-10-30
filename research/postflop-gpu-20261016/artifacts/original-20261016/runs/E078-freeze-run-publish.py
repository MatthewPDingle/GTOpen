"""Own one fixed complete-solve screen of the exact parent-block fold producer."""
from pathlib import Path
import json,re,shutil,subprocess,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
build=R/'runs/E078-final-build/complete.json';built=old.read(build);assert built['all_compilers_terminal']and built['native_executions']==0
for p,h in built['evidence_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E078-build-manager/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
d=R/'runs/E078-kernel-control/report.json';control=old.read(d);assert control['status']=='pass_full_raw_fold_action_controls'and control['raw_replay']['completed_case_count']==1638 and control['raw_replay']['all_full_output_words_exact']and control['raw_replay']['all_finite_fold_oracle_words_exact']and control['all_owned_children_terminal']and control['accepted_main_live_PTX_custody_pass']
H=R/'runs/E078-primary-plan';assert not H.exists();H.mkdir()
for name in['native.py','assess.py','root-check.py','run.py']:
 code=(R/'runs/E077-primary-plan'/name).read_text(encoding='utf-8').replace('E077','E078').replace('e077','e078').replace('exact three-source scope','exact two-source scope')
 if name in['native.py','assess.py']:
  predicate="assert control['status']=='pass_full_raw_fold_action_controls' and control['raw_replay']['completed_case_count']==1638 and control['raw_replay']['all_full_output_words_exact'] and control['raw_replay']['all_finite_fold_oracle_words_exact'] and control['all_owned_children_terminal'] and control['accepted_main_live_PTX_custody_pass']"
  code,n=re.subn(r"assert control\['status'\][^\n]+",predicate,code);assert n==1
 compile(code,str(H/name),'exec');(H/name).write_text(code,encoding='utf-8',newline='\n')
source=old.read(R/'runs/E078-source/manifest-r2.json');P=old.read(R/'runs/E077-primary-plan/protocol.json')
P.update(id='E078-primary',at=old.now(),candidate_owned_sha256=source['candidate_owned_sha256'],build_protocol_sha256=old.sha(R/'runs/E078-build-plan/build-protocol.json'),ordinary_unit_id='V078-unit',control_ids=['V078-unit'],pairs=[{'baseline':'B247','candidate':'E078R1'},{'baseline':'B248','candidate':'E078R2'},{'baseline':'B249','candidate':'E078R3'}],measurement_order=['B247','E078R1','E078R2','B248','B249','E078R3'],direct_control_report={'path':str(d),'sha256':old.sha(d)},source_scope=source['scope']+' All12compiledhostmetadata maps and2,309,410markers exact; original test-empty-menu failure retained with attributed explicit-menu/noop test-only correction, no production change. All1638directGPUcasepairs/4095launches pass40,767,252wholeoutputs/23,829,848actualinputs/36,129,230guards and173,187CPUfoldoraclewords. OriginalresourceABIreaderfailure/D129samePTXrepair retained; no resource/compiler rerun. CPUmarking/extraGPUmetadata/staticshared/fold+actionwork, NVRTC/JIT/setup/quality/fullreadback all remain in completeclocks. No speed/material claim yet.')
paths=[Path(__file__),build,d,R/'runs/E078-kernel-control/protocol.json',R/'runs/E078-plan-control/report.json',R/'runs/E078-plan-control/protocol-r2.json',R/'runs/E078-plan-control/test-fixture-amendment.json',R/'runs/E078-build-plan/build-protocol.json',R/'runs/E078-source/manifest-r2.json',R/'runs/E078-source/manifest.json',R/'runs/E078-source/candidate.cu',R/'runs/E078-source/candidate-mod-r2.rs',R/'runs/D128-fold-parent/report.json',R/'runs/D129-ABI-pointer-audit/report.json',Path(P['baseline']['path']),Path(P['baseline_binary']['path']),Path(P['baseline_binary']['manifest']),C/'common_e051_live.py',C/'protected-main.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*[H/n for n in['native.py','assess.py','root-check.py','run.py']]]
for stem in['E078-feature-solver','E078-solver','E078-postflop_autoresearch']:
 exe=R/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');m=old.read(mp);old.pin(exe,m['binary_sha256']);assert m['source_sha256']==old.BASE|P['candidate_owned_sha256'];paths.extend([exe,mp])
st=old.read(old.ar.STATUS)
for identity in P['control_ids']+P['measurement_order']:assert not(R/'runs'/identity).exists()and not any(x['id']==identity for x in st['experiments'])
for name in['E078-native-execution','E078-primary-wrapper','E078-primary-manager']:assert not(R/'runs'/name).exists()
for name in['E078-three-pair-comparison','E078-root-crosscheck']:assert not(R/'comparisons'/name).exists()
P['input_sha256']={str(p):old.sha(p)for p in paths};old.save(H/'protocol.json',P)
def publish(src,key):
 dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
 if dst.exists():assert dst.read_bytes()==src.read_bytes(),key
 else:shutil.copyfile(src,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==src.read_bytes()
 return {'url':'evidence/'+key,'sha256':old.sha(src)}
pub=[publish(p,H.name+'/'+p.name)for p in H.iterdir()if p.is_file()];old.save(H/'pre-timing-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'native_primary_executions':0,'all_compilers_terminal':True,'HTTP_byte_verified_artifacts':pub})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E078');e.update(stage='Ordinary tests, then three complete-solve pairs',reason='Both fresh builds are terminal and accepted source is restored. All 12 host metadata cases and 1,638 direct GPU pairs passed. The fixed BC/CB/BC comparison includes CPU marking, GPU setup, NVRTC/JIT, quality checks, and full readback. No speed claim yet.');e['evidence'].append({'label':'Frozen complete-solve screen with 1% cutoff','url':'evidence/E078-primary-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E078',stage='E078 complete-solve comparison',activity='Run 85 ordinary tests, then exactly B247/E078R1, E078R2/B248, B249/E078R3. Same quality, unrounded 1% cutoff, and strict fixture guard. No extra samples or rescue runs; accepted and live E051 remain unchanged.');old.ar.atomic_json(old.ar.STATUS,s)
O=R/'runs/E078-primary-manager';O.mkdir();print('E078primaryprotocol',old.sha(H/'protocol.json'),flush=True);old.child([sys.executable,'-B',str(H/'run.py'),old.sha(H/'protocol.json')],O,'primary',old.env(),2400)
qpath=R/'comparisons/E078-three-pair-comparison/report.json';rootpath=R/'comparisons/E078-root-crosscheck/report.json';q=old.read(qpath);root=old.read(rootpath);perf=q['performance'];passed=perf['primary_timing_pass']
assert root['aggregate_gain_pct']==perf['observed_gain_pct']and root['status']==('pass_initial_timing_only'if passed else'pass_rejected');assert q['exactness']=={'fixture_results':18,'convergence_records':138,'all_exact':True}and q['excluded_samples']==[]and q['extension_runs']==0 and q['historical_timing_samples_used']==0
old.custody();assert not(R/'gpu-run.lock').exists();out=R/'runs/E078-initial-closure';out.mkdir();reason=f"Initial complete-solve gain {perf['observed_gain_pct']:.6f}%. All 18 full non-timing results, 138 checkpoints, 85 ordinary tests, 12 host metadata cases, and 1,638 direct GPU pairs passed. "
if passed:reason+='Initial gate passed; separately frozen fresh16 confirmation, broad compatibility, actual CPU and memory costs, capacity, holdout, and cumulative checks remain. Not accepted.'
else:
 why=[]
 if perf['observed_gain_pct']<1:why.append('below the unrounded 1% cutoff')
 guards=[x['fixture_id']for x in perf['fixture_regression_guard']if x['failed']]
 if guards:why.append('repeatable fixture slowdown: '+', '.join(guards))
 reason+='Rejected: '+'; '.join(why)+'. No extra samples, source/helper/marker/arity/thread/width/placement/threshold variants, or rescue runs.'
decision={'id':'E078','at':old.now(),'decision':q['decision'],'performance':perf,'ordinary_units_passed':85,'ignored_units':4,'exact_fixture_results':18,'exact_checkpoints':138,'CPU_metadata_cases':12,'direct_control_report_sha256':old.sha(d),'direct_GPU_cases':1638,'direct_GPU_launches':4095,'assessment_sha256':old.sha(qpath),'root_replay_sha256':old.sha(rootpath),'primary_whole_arena_fingerprints_exact':True,'primary_raw_arena_bytes_independently_compared':False,'source_adopted':False,'accepted_and_live_source':'E051','fresh16_broad_material_holdout_cumulative_run':False,'no_exclusions_extensions_pooling':True,'reason':reason};old.save(out/'decision.json',decision)
published=[]
for folder in[H,R/'runs/E078-build-plan',R/'runs/E078-primary-wrapper',R/'runs/E078-native-execution',out,qpath.parent,rootpath.parent]:
 for p in folder.iterdir():
  if p.is_file()and p.suffix in['.json','.py','.rs','.patch','.log']:published.append(publish(p,folder.name+'/'+p.name))
for phase in['feature','primary']:
 for p in(R/'runs/E078-final-build'/phase).iterdir():
  if p.is_file()and p.suffix in['.json','.log']:published.append(publish(p,'E078-final-build-'+phase+'/'+p.name))
for stem in['E078-feature-solver','E078-solver','E078-postflop_autoresearch']:published.append(publish(R/'binaries'/(stem+'.manifest.json'),'E078-binary-manifests/'+stem+'.manifest.json'))
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E078');e.update(status='measured'if passed else'rejected',correctness='pass',stage='Initial pass; confirmation and broader qualification pending'if passed else'Closed: initial performance gate failed',reason=reason,observed_gain_pct=perf['observed_gain_pct'],updated_at=old.now(),accepted=False);e['evidence'].extend([{'label':'Fixed complete-solve assessment','url':'evidence/E078-three-pair-comparison/report.json'},{'label':'Raw-record arithmetic replay','url':'evidence/E078-root-crosscheck/report.json'},{'label':'Initial decision','url':'evidence/E078-initial-closure/decision.json'}]);s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E078'if passed else None,stage='E078 fresh confirmation preparation'if passed else'Investigating the next GPU optimization',activity=reason+' Accepted and live E051 remain unchanged: 12.44% cumulative improvement on the registered benchmarks.');old.ar.atomic_json(old.ar.STATUS,s)
old.save(out/'publication.json',{'at':old.now(),'HTTP_byte_verified_artifacts':published,'accepted_and_live_source_unchanged':True,'candidate_adopted':False})
ledger=old.REPO/'research/postflop-gpu-20261016/experiments.md';raw=ledger.read_bytes();assert b'### E078 parent-block fold complete-solve screen'not in raw
entry=f'''

### E078 parent-block fold complete-solve screen

Exact2fileproductionform remainsfrozen{json.dumps(P['candidate_owned_sha256'],separators=(',',':'))}. Originalfoldcopy/card/reduction/payout/fullcachedCFVrowwrite executesinuniqueparentactionCTA beforeoriginalunchangedactionhelper/dispatch;trainingseparatefoldlaunches removed,evaluationunchanged. Privateexistingnode_nafoldmarker-1,noaddedglobal/CPUarray/payload/layout/threadshape/quality/savechange. Default128threadoccupancy8unchanged,staticshared0to6544driverbytes/64threadoccupancy16to13warningsretained. D128all12ownershipmodels/D129samePTXABIobserverrepair andall12compiledfullhostmetadata/2,309,410markerspass. Originalemptydefaultmenutestpreconditionfailure/test-onlyexplicit50pctplusnoopcorrectionretained;productionunchanged. Same1638directGPUcasepairs/4095launchespass40,767,252fulloutputwords,23,829,848actualimmutablewords,36,129,230guards,173,187finitefoldoraclewords. No scopedcontrolspeed/materialclaim.

Twofreshisolatedfeature/primarybuildsterminal0,acceptedE051restoredaftereach. Frozenprimaryprotocol{old.sha(H/'protocol.json')},V078-unit85passed/4ignored;fixedB247/E078R1,E078R2/B248,B249/E078R3. All18fullnon-timingpayloads/138qualitycheckpoints exact. Sumfixturemediancompletecycle{perf['baseline_full_cycle_ms']:.10f}to{perf['candidate_full_cycle_ms']:.10f}ms,unroundedgain{perf['observed_gain_pct']:.10f}%. Strictfixtureguards{json.dumps(perf['fixture_regression_guard'],separators=(',',':'))}. Root{root['checks']}raw/arithmeticchecks;assessment{old.sha(qpath)}. {reason}

Noexclusions/extensions/historicaltimingpooling/adoption. Fresh16,broadF32/state/menu/save/resume/continuation,actualCPU/host+GPUpeak/capacity/responsiveness,holdout/cumulative notrunforE078. Primaryfullarenafingerprints exact;primaryfullrawarenabytesnotindependentlycompared. All{len(published)}publishedfiles HTTPbyteverified,allownedchildrenterminal,accepted162/main163/live/protected2PTXexact. E051accepted/deployedcumulative12.4372274192%unchanged. LastprimaryB249,goalactive.
''';nl=b'\r\n'if b'\r\n'in raw else b'\n';ledger.write_bytes(raw+entry.encode().replace(b'\n',nl));old.custody();subprocess.run(['git','commit','--only','-m','research: screen parent-block fold production with complete-solve clocks','--','research/postflop-gpu-20261016/experiments.md'],cwd=old.REPO,check=True);old.custody();print(json.dumps({'decision':q['decision'],'gain_pct':perf['observed_gain_pct'],'report_sha256':old.sha(qpath),'published_files':len(published),'accepted_and_live_source':'E051'}),flush=True)
