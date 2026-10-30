"""Freeze initial3pairs after every compiler/control is terminal."""
import sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E052-final-build/complete.json';B=old.read(build);assert B['all_compilers_terminal'] is True and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E052-kernel-control/report.json';C=old.read(control);assert C['status']=='pass_scoped_show_raw_equivalence' and C['cases']==328 and C['all_full_outputs_inputs_guards_exact'] is True
H=ROOT/'runs/E052-primary-plan';H.mkdir();prior=ROOT/'runs/E051-primary-plan'
for name in ['native.py','assess.py','root-check.py']:
 text=(prior/name).read_text().replace('E051','E052').replace("sys.path.insert(0,str(HERE.parent/'small-gain-confirmation-plan'));import common as old","sys.path.insert(0,str(HERE.parent/'accepted-E051'));import common_e051 as old")
 text=text.replace('old.exact_raw','old.historical.exact_raw').replace("control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal']","control['status']=='pass_scoped_show_raw_equivalence' and control['cases']==328 and control['all_full_outputs_inputs_guards_exact']")
 text=text.replace("bs=math.fsum(f['baseline_median_ms'] for f in fixture);cs=math.fsum(f['candidate_median_ms'] for f in fixture)","bs=sum(f['baseline_median_ms'] for f in fixture);cs=sum(f['candidate_median_ms'] for f in fixture)")
 text=text.replace("'exact one-source scope'","'exact two-source scope'")
 (H/name).write_text(text,encoding='utf-8',newline='\n')
p=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
p.update(id='E052-primary',at=old.now(),baseline={'path':str(baseline),'sha256':old.sha(baseline)},build_protocol_sha256=old.sha(ROOT/'runs/E052-build-plan/build-protocol.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},candidate_owned_sha256=old.read(ROOT/'runs/E052-source/manifest.json')['candidate_owned_sha256'],ordinary_unit_id='V052-unit',control_ids=['V052-unit'],pairs=[{'baseline':'B171','candidate':'E052R1'},{'baseline':'B172','candidate':'E052R2'},{'baseline':'B173','candidate':'E052R3'}],measurement_order=['B171','E052R1','E052R2','B172','B173','E052R3'],baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},source_scope='Two files: per-CTA position cache uses unsigned16 while global u32metadata/ABI and all float expressions/order stay unchanged. Both up_show launch reservations reduce16*m+4*nh to12*m+4*nh. No new buffer, allocation, transfer, graph node, precision or quality change.')
paths=[baseline,binary,manifest,build,control,ROOT/'runs/E052-build-plan/build-protocol.json',ROOT/'comparisons/E052-resource-root-check/report.json',ROOT/'runs/E052-source/source-review.json',ROOT/'runs/E052-source/manifest.json',ROOT/'runs/E052-kernel-control/execution/terminal.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',*H.glob('*.py')]
for stem in ['E052-solver','E052-postflop_autoresearch']:
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
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E052');e.update(stage='Ordinary units then fixed3pair complete-cycle screen',reason='Fresh feature/GPU-only artifacts compiled from exact2file candidate; acceptedE051 restored. Source/resources/raw controls pass; same frozen evaluator/quality.');e['evidence'].append({'label':'E052 frozen primary1%screen','url':'evidence/E052-primary-plan/protocol.json'});st.update(updated_at=old.now(),stage='E052 fixed primary screen',activity='Run ordinary units then exactly B171/E052R1,E052R2/B172,B173/E052R3. Preserve every observation; no timing pooled.');old.ar.atomic_json(old.ar.STATUS,st)
print(old.sha(H/'protocol.json'),flush=True)
