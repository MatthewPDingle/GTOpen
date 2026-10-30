"""Freeze one3-pair complete-cycle screen after integrated builds have terminated."""
import ast,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E060-final-build/complete.json';B=old.read(build);assert B['all_compilers_terminal'] and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
control=ROOT/'comparisons/E060-kernel-control-root-check/report.json';C=old.read(control)
assert C['status']=='pass_scoped_up_action_raw_equivalence' and C['cases']==819 and C['full_raw_files_equal'] and C['all_parent_child_cfv_rows_disjoint']
scalar=ROOT/'comparisons/E060-scalar-root-check/report.json';assert old.read(scalar)['status']=='pass_scoped_scalar_bit_equivalence'
H=ROOT/'runs/E060-primary-plan';assert not H.exists();H.mkdir();prior=ROOT/'runs/E055-primary-plan'
for name in ['native.py','assess.py','root-check.py']:
 text=(prior/name).read_text(encoding='utf-8').replace('E055','E060').replace('E060-final-build-r2','E060-final-build')
 ast.parse(text);(H/name).write_text(text,encoding='utf-8',newline='\n')
p=old.read(prior/'protocol.json');baseline=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
owned={'crates/solver/src/gpu/kernels.cu':old.sha(ROOT/'runs/E060-source/candidate.cu')}
p.update(id='E060-primary',at=old.now(),baseline={'path':str(baseline),'sha256':old.sha(baseline)},build_protocol_sha256=old.sha(ROOT/'runs/E060-build-plan/build-protocol.json'),gpu_control_report={'path':str(control),'sha256':old.sha(control)},candidate_owned_sha256=owned,ordinary_unit_id='V060-unit',control_ids=['V060-unit'],pairs=[{'baseline':'B186','candidate':'E060R1'},{'baseline':'B187','candidate':'E060R2'},{'baseline':'B188','candidate':'E060R3'}],measurement_order=['B186','E060R1','E060R2','B187','B188','E060R3'],baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},source_scope='One compute120 up_action common2/3/4 denominator reciprocal-refinement reuse. Three numerator-specific FMAs reuse the refined inverse only in the frozen positive-normal guard; native division fallback/other architectures/generic NA0 retained. Original other arithmetic/addresses/host/graphs/layout/quality/ABI unchanged. Resource allocation and64local bytes unchanged; scalar2,130,758and complete819kernel controls exact. No architecture-wide precision or speed guarantee from samples.')
paths=[baseline,binary,manifest,build,control,scalar,ROOT/'runs/E060-build-plan/build-protocol.json',ROOT/'runs/E060-resource/report.json',ROOT/'runs/E060-source/source-review.json',ROOT/'runs/E060-source/manifest.json',ROOT/'runs/E060-kernel-control/execution/terminal.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',old.REPO/'research/postflop-gpu-20261016/resource-admission-policy-20261017.md',Path(__file__),*H.glob('*.py')]
for stem in ['E060-solver','E060-postflop_autoresearch']:
 exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');cm=old.read(mp);old.pin(exe,cm['binary_sha256']);assert cm['source_sha256']==old.BASE|owned;paths.extend([exe,mp])
for identity in p['control_ids']+p['measurement_order']:assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in old.read(old.ar.STATUS)['experiments'])
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'protocol.json',p)
published={}
for src in H.iterdir():
 key='evidence/'+H.name+'/'+src.name;dst=old.ar.DASHBOARD/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
 published[key]=old.sha(src)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'all_compilers_terminal':True,'published':published,'http_bytes_verified':True,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(e for e in st['experiments'] if e['id']=='E060');e.update(stage='Ordinary units then fixed3pair full-cycle screen',reason='Fresh feature/primary builds terminal; accepted E051 restored. Scalar/kernel raw bits and resource constraints passed. Fixed B186/E060R1,E060R2/B187,B188/E060R3,unchanged1%and perfixture guards.');e['evidence'].append({'label':'Frozen initial1%complete-cycle screen','url':'evidence/'+H.name+'/protocol.json'});st.update(updated_at=old.now(),stage='E060 fixed primary screen',activity='Ordinary units then exactly3fresh pairs; all observations retained. No source activation during native measurements.');old.ar.atomic_json(old.ar.STATUS,st)
old.custody();print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'fixed_order':p['measurement_order'],'all_compilers_terminal':True}),flush=True)
