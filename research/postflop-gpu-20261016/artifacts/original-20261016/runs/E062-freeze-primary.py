"""Freeze fresh paired complete-cycle testing for attributed E057source reuse."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E062-final-build/complete.json';B=old.read(build);assert B['all_compilers_terminal'] and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E062-kernel-control-root-check/report.json';C=old.read(control);assert C['status']=='pass_scoped_show_raw_equivalence' and C['cases']==364 and C['all_full_outputs_inputs_guards_exact']
H=ROOT/'runs/E062-primary-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E053-primary-plan'
for n in ['native.py','assess.py','root-check.py']:
 s=(prior/n).read_text(encoding='utf-8').replace('E053','E062');ast.parse(s);(H/n).write_text(s,encoding='utf-8',newline='\n')
P=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
owned=old.read(ROOT/'runs/E062-source/manifest.json')['candidate_owned_sha256'];pairs=[{'baseline':'B192','candidate':'E062R1'},{'baseline':'B193','candidate':'E062R2'},{'baseline':'B194','candidate':'E062R3'}]
P.update(id='E062-primary',at=old.now(),status='FROZEN_BEFORE_FIRST_SOURCE_FORM_SPEED_OBSERVATION',baseline={'path':str(baseline),'sha256':old.sha(baseline)},baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},candidate_owned_sha256=owned,build_protocol_sha256=old.sha(ROOT/'runs/E062-build-plan/build-protocol.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},control_ids=['V062-unit'],ordinary_unit_id='V062-unit',measurement_order=['B192','E062R1','E062R2','B193','B194','E062R3'],pairs=pairs,source_scope='Exact original E057prefix-index mapping helper and accesses, byte-identical complete CUDA source on accepted E051. Same ordered FPoperations, ABI, buffers/launches/graphs/quality; current actual resource/capacity prefilter and fresh364raw paired kernel controls passed. Attributed source requalification under D101, not a new independent mechanism.',source_ancestry={'original_form':'E057','new_qualification':'E062','policy_sha256':old.sha(old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md'),'audit_sha256':old.sha(ROOT/'runs/D101-resource-eligibility-audit/report.json'),'original_performance_observations':0,'historical_source_form_timings_scored':0})
paths=[*H.glob('*.py'),Path(__file__),baseline,binary,manifest,build,control,ROOT/'runs/E062-build-plan/build-protocol.json',ROOT/'runs/E062-resource/report.json',ROOT/'runs/E062-source/source-review.json',ROOT/'runs/E062-source/manifest.json',ROOT/'runs/E062-kernel-control/execution/terminal.json',ROOT/'runs/D101-resource-eligibility-audit/docket.json',ROOT/'runs/D101-resource-eligibility-audit/report.json',old.REPO/'research/postflop-gpu-20261016/unmeasured-resource-eligibility-20261017.md',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md']
for stem in ['E062-solver','E062-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');cm=old.read(mp);old.pin(exe,cm['binary_sha256']);assert cm['source_sha256']==old.BASE|owned;paths.extend([exe,mp])
for identity in P['control_ids']+P['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(e['id']==identity for e in old.read(old.ar.STATUS)['experiments'])
P['input_sha256']={str(p):old.sha(p) for p in paths};old.save(H/'protocol.json',P)
published={}
for p in H.iterdir():
 if not p.is_file():continue
 key='evidence/'+H.name+'/'+p.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(p.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 published[key]=old.sha(p)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'published':published,'http_bytes_verified':True,'all_compilers_terminal':True,'new_timing_observations':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E062');e.update(stage='Ordinary GPU units then first fixed3pair speed screen',reason='Feature/primary builds terminal and accepted E051restored. Original source form has no prior speed data. Exactly B192/E062R1,E062R2/B193,B194/E062R3, unchanged1%/fixture/exactness rules; no performance claim before all observations.');e['evidence'].append({'label':'First fresh complete-cycle speed protocol','url':'evidence/'+H.name+'/protocol.json'});st.update(updated_at=old.now(),state='running',active_experiment='E062',stage='E062 first complete-cycle speed screen',activity='Ordinary84GPU units then3fixed pairs. Actual quality/stops/storage/fixtures unchanged, accepted source remains E051during measurements.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'pairs':pairs,'all_builds_terminal':True,'minimum_gain_pct':P['policy']['minimum_complete_cycle_gain_pct']}),flush=True)
