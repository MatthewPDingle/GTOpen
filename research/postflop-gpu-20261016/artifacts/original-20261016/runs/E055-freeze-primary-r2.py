"""Freeze exactly three paired full-cycle observations for E055 after build."""
import json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E055-final-build-r2/complete.json';B=old.read(build);assert B['all_compilers_terminal'] is True and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E055-kernel-control-root-check/report.json';C=old.read(control)
assert C['status']=='pass_scoped_up_action_raw_equivalence' and C['cases']==819 and C['full_raw_files_equal'] and C['all_parent_child_cfv_rows_disjoint']
H=ROOT/'runs/E055-primary-plan';H.mkdir();prior=ROOT/'runs/E053-primary-plan'
for name in ['native.py','assess.py','root-check.py']:
 text=(prior/name).read_text(encoding='utf-8').replace('E053','E055').replace('E055-final-build','E055-final-build-r2')
 text=text.replace("control['status']=='pass_scoped_show_raw_equivalence' and control['cases']==364 and control['all_full_outputs_inputs_guards_exact']","control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal'] and control['all_parent_child_cfv_rows_disjoint']")
 assert '364' not in text and 'import common as old' not in text
 (H/name).write_text(text,encoding='utf-8',newline='\n')
p=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
p.update(id='E055-primary',at=old.now(),baseline={'path':str(baseline),'sha256':old.sha(baseline)},build_protocol_sha256=old.sha(ROOT/'runs/E055-build-plan/build-protocol-r2.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},candidate_owned_sha256=old.read(ROOT/'runs/E055-source/manifest.json')['candidate_owned_sha256'],ordinary_unit_id='V055-unit',control_ids=['V055-unit'],pairs=[{'baseline':'B180','candidate':'E055R1'},{'baseline':'B181','candidate':'E055R2'},{'baseline':'B182','candidate':'E055R3'}],measurement_order=['B180','E055R1','E055R2','B181','B182','E055R3'],baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},source_scope='One store scheduling move in unlocked own-node up_action: publish completed parent CFV before unchanged regret loop. Parent/child rows disjoint in production and every actual direct control. All arithmetic/order, strategy store, other branches, host/layout/ABI/graphs/allocations/precision and quality settings unchanged.')
p['source_scope']='One readonly load placement: read3immutable discount floats only in unlocked own-node up_action. Same values/arithmetic/reduction/store order, allother branches/ABI/host/graphs/allocations/quality. Actual PTX proves unused roles skip reads.'
paths=[baseline,binary,manifest,build,control,ROOT/'runs/E055-build-plan/build-protocol-r2.json',ROOT/'comparisons/E055-resource-root-check/report.json',ROOT/'runs/E055-source/source-review.json',ROOT/'runs/E055-source/manifest.json',ROOT/'runs/E055-kernel-control/execution/terminal.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*H.glob('*.py')]
for stem in ['E055-solver','E055-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');cm=old.read(mp);old.pin(exe,cm['binary_sha256']);assert cm['source_sha256']==old.BASE|p['candidate_owned_sha256'];paths +=[exe,mp]
for identity in p['control_ids']+p['measurement_order']:
 assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in old.read(old.ar.STATUS)['experiments'])
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'protocol.json',p)
published={}
for src in H.iterdir():
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as r:assert r.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'all_compilers_terminal':True,'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E055');e.update(stage='Ordinary units then fixed3pair full-cycle screen',reason='Fresh feature and primary artifacts built from exact one-file transform and acceptedE051 restored.819raw cases exact; no performance claim.');e['evidence'].append({'label':'E055 frozen initial1%screen','url':'evidence/E055-primary-plan/protocol.json'});st.update(updated_at=old.now(),stage='E055 fixed primary screen',activity='Ordinary units then exactly B180/E055R1,E055R2/B181,B182/E055R3; fixed accuracy and all observations retained.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
