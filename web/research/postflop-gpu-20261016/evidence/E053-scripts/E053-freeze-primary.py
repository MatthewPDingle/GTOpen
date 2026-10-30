"""Freeze fixed three-pair initial screen after all builds terminate."""
import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E053-final-build/complete.json';B=old.read(build);assert B['all_compilers_terminal'] is True and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E053-kernel-control-root-check/report.json';C=old.read(control);assert C['status']=='pass_scoped_show_raw_equivalence' and C['cases']==364 and C['all_full_outputs_inputs_guards_exact'] is True
H=ROOT/'runs/E053-primary-plan';H.mkdir();prior=ROOT/'runs/E052-primary-plan'
for dest,source in [('native.py','native.py'),('assess.py','assess-r2.py'),('root-check.py','root-check.py')]:
 text=(prior/source).read_text().replace('E052','E053').replace("control['cases']==328","control['cases']==364").replace("'exact two-source scope'","'exact one-source scope'")
 assert 'import common as old' not in text and "small-gain-confirmation-plan" not in text
 (H/dest).write_text(text,encoding='utf-8',newline='\n')
p=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
p.update(id='E053-primary',at=old.now(),baseline={'path':str(baseline),'sha256':old.sha(baseline)},build_protocol_sha256=old.sha(ROOT/'runs/E053-build-plan/build-protocol.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},candidate_owned_sha256=old.read(ROOT/'runs/E053-source/manifest.json')['candidate_owned_sha256'],ordinary_unit_id='V053-unit',control_ids=['V053-unit'],pairs=[{'baseline':'B174','candidate':'E053R1'},{'baseline':'B175','candidate':'E053R2'},{'baseline':'B176','candidate':'E053R3'}],measurement_order=['B174','E053R1','E053R2','B175','B176','E053R3'],baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},source_scope='One CUDA helper: fuse sorted-reach shared producer into existing per-thread prefix chunk while preserving every input value/addition order, barrier, zeroing store, u32cache, shared layout, host/ABI/allocation/graph and quality setting.')
paths=[baseline,binary,manifest,build,control,ROOT/'runs/E053-build-plan/build-protocol.json',ROOT/'comparisons/E053-resource-root-check/report.json',ROOT/'runs/E053-source/source-review.json',ROOT/'runs/E053-source/manifest.json',ROOT/'runs/E053-kernel-control/execution/terminal.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*H.glob('*.py')]
for stem in ['E053-solver','E053-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');cm=old.read(mp);old.pin(exe,cm['binary_sha256']);assert cm['source_sha256']==old.BASE|p['candidate_owned_sha256'];paths +=[exe,mp]
for identity in p['control_ids']+p['measurement_order']:assert not (ROOT/'runs'/identity).exists()
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'protocol.json',p)
published={}
for src in H.iterdir():
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'all_compilers_terminal':True,'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E053');e.update(stage='Ordinary units then fixed3pair complete-cycle screen',reason='Fresh feature/GPU-only binaries compile from exact one-file fusion; acceptedE051 restored. Source/resources/339712ownership-shapes/364raw controls pass; speed remains unqualified.');e['evidence'].append({'label':'E053 frozen initial1%screen','url':'evidence/E053-primary-plan/protocol.json'});st.update(updated_at=old.now(),stage='E053 fixed primary screen',activity='Run ordinary units then exactly B174/E053R1,E053R2/B175,B176/E053R3. Fixed accuracy/quality and every observation retained.');old.ar.atomic_json(old.ar.STATUS,st)
print(old.sha(H/'protocol.json'),flush=True)
