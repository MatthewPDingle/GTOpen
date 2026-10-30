"""Freeze one three-pair full-cycle ordering-only screen after builds finish."""
import json, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
build=ROOT/'runs/E056-final-build/complete.json';B=old.read(build)
assert B['all_compilers_terminal'] and B['native_executions']==0
for p,h in B['evidence_sha256'].items():old.pin(p,h)
D=ROOT/'runs/D092-action-arity-order/report.json';d=old.read(D)
assert d['status']=='pass_cpu_metadata_and_concrete_ownership' and len(d['cases'])==12 and d['concrete_same_level_ownership_pass']
H=ROOT/'runs/E056-primary-plan';assert not H.exists();H.mkdir()
condition="control['status']=='pass_scoped_up_action_raw_equivalence' and control['cases']==819 and control['full_raw_files_equal'] and control['all_parent_child_cfv_rows_disjoint']"
replacement="control['status']=='pass_cpu_metadata_and_concrete_ownership' and len(control['cases'])==12 and control['concrete_same_level_ownership_pass'] and control['nonorder_fields_exact']"
for name in ['native.py','assess.py','root-check.py']:
    text=(ROOT/'runs/E055-primary-plan'/name).read_text(encoding='utf-8').replace('E055','E056').replace('E056-final-build-r2','E056-final-build').replace('gpu_control_report','cpu_control_report')
    if name!='root-check.py':
        assert condition in text
        text=text.replace(condition,replacement)
    text=text.replace("e.pop('E056_KERNEL_CONTROL_DIR',None)","e.pop('E056_PLAN_CONTROL_DIR',None)")
    assert not any(x in text for x in ['E055','e055','r2','819','scoped_up_action'])
    (H/name).write_text(text,encoding='utf-8',newline='\n')
runner='''"""Serially run, assess and independently replay the fixed initial screen."""
import sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
old.custody();out=ROOT/'runs/E056-primary-wrapper';assert not out.exists();out.mkdir()
old.child([sys.executable,str(H/'native.py'),sys.argv[1]],out,'native',old.env(),1800)
ex=ROOT/'runs/E056-native-execution'
receipt=old.read(out/'native.exit.json');assert receipt['returncode']==0 and receipt['error'] is None
old.save(ex/'terminal.json',{'at':old.now(),'returncode':0,'complete_sha256':old.sha(ex/'complete.json'),'wrapper_receipt_sha256':old.sha(out/'native.exit.json')})
old.child([sys.executable,str(H/'assess.py'),sys.argv[1]],out,'assessment',old.env(),120)
old.child([sys.executable,str(H/'root-check.py'),sys.argv[1]],out,'root-replay',old.env(),120)
old.custody();q=old.read(ROOT/'comparisons/E056-three-pair-comparison/report.json')
old.save(out/'complete.json',{'at':old.now(),'all_children_terminal':True,'decision':q['decision'],'assessment_sha256':old.sha(ROOT/'comparisons/E056-three-pair-comparison/report.json'),'root_replay_sha256':old.sha(ROOT/'comparisons/E056-root-crosscheck/report.json')})
print({'decision':q['decision'],'performance':q['performance']},flush=True)
'''
(H/'run.py').write_text(runner,encoding='utf-8',newline='\n')
p=old.read(ROOT/'runs/E055-primary-plan/protocol.json')
base=ROOT/'runs/accepted-E051/baseline.json';binary=ROOT/'binaries/E051-postflop_autoresearch.exe';manifest=binary.with_suffix('.manifest.json');m=old.read(manifest);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE
p.pop('gpu_control_report')
p.update(id='E056-primary',at=old.now(),baseline={'path':str(base),'sha256':old.sha(base)},build_protocol_sha256=old.sha(ROOT/'runs/E056-build-plan/build-protocol.json'),cpu_control_report={'path':str(D),'sha256':old.sha(D)},candidate_owned_sha256=old.read(ROOT/'runs/E056-source/manifest.json')['candidate_owned_sha256'],ordinary_unit_id='V056-unit',control_ids=['V056-unit'],pairs=[{'baseline':'B183','candidate':'E056R1'},{'baseline':'B184','candidate':'E056R2'},{'baseline':'B185','candidate':'E056R3'}],measurement_order=['B183','E056R1','E056R2','B184','B185','E056R3'],baseline_binary={'path':str(binary),'sha256':old.sha(binary),'manifest':str(manifest),'manifest_sha256':old.sha(manifest)},source_scope='One CPU plan-list permutation: ascending actual action count within each existing depth, unchanged CUDA source/dispatch, span counts, node/child IDs, arenas, physical maps, buffer capacities, launch code and graph structure. Full cycle includes sorting. All53 plan fields/capacities and actual ownership controlled across12 CPU cases; actual GPU results, graphs and broader costs must still qualify.')
p['adoption_requirements']=['Separately frozen fresh16 pairs: unrounded aggregate >=1%, >=13 improving pairs, positive paired/block/order medians, no repeatable fixture slowdown.','Broader exact state/F32/menu/save/resume/continuation, actual graph/launch/memory/capacity and material CPU setup-cost checks.','Fixed holdout and fresh-original cumulative qualification. Initial screen alone does not establish significance, universal behavior or adoption.']
paths=[base,binary,manifest,build,D,ROOT/'runs/E056-build-plan/build-protocol.json',ROOT/'runs/E056-source/source-review.json',ROOT/'runs/E056-source/manifest.json',old.REPO/'research/postflop-gpu-20261016/qualification-policy-20261017.md',Path(__file__),*H.glob('*.py')]
for stem in ['E056-solver','E056-postflop_autoresearch']:
    exe=ROOT/'binaries'/(stem+'.exe');mp=exe.with_suffix('.manifest.json');cm=old.read(mp);old.pin(exe,cm['binary_sha256']);assert cm['source_sha256']==old.BASE|p['candidate_owned_sha256'];paths.extend([exe,mp])
status=old.read(old.ar.STATUS)
for identity in p['control_ids']+p['measurement_order']:
    assert not (ROOT/'runs'/identity).exists() and not any(x['id']==identity for x in status['experiments'])
for directory in ['E056-native-execution','E056-primary-wrapper']:
    assert not (ROOT/'runs'/directory).exists()
for directory in ['E056-three-pair-comparison','E056-root-crosscheck']:
    assert not (ROOT/'comparisons'/directory).exists()
p['input_sha256']={str(x):old.sha(x) for x in paths};old.save(H/'protocol.json',p)
published={}
for src in H.iterdir():
    if not src.is_file():continue
    key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
    published[key]=old.sha(src)
old.save(H/'pre-timing-publication.json',{'at':old.now(),'all_compilers_terminal':True,'artifact_sha256':published,'candidate_accepted':False})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='E056');e.update(stage='Ordinary units then fixed three-pair complete-cycle screen',reason='Exact one-file ordering candidate built; accepted E051 restored. Twelve CPU raw metadata/ownership controls pass. No GPU result or speed claim yet.');e['evidence'].append({'label':'Frozen initial 1% complete-cycle screen','url':'evidence/E056-primary-plan/protocol.json'});st.update(updated_at=old.now(),stage='E056 fixed primary screen',activity='Ordinary units then exactly B183/E056R1, E056R2/B184, B185/E056R3. Same quality, full sorting/setup cost included, all observations retained.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
