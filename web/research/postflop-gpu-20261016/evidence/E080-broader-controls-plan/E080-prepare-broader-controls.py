"""Freeze the full native compatibility batch after all compilers are terminal."""
from pathlib import Path
import ast,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=106*1024**3
B=R/'runs/E080-broader-build-r2';done=old.read(B/'complete.json');assert done['all_compilers_terminal']and done['native_executions']==0
for p,h in done['artifact_sha256'].items():old.pin(p,h)
receipt=old.read(R/'runs/E080-broader-build-manager-r2/build.exit.json');assert receipt['returncode']==0 and receipt['error']is receipt['cleanup']is None
H=R/'runs/E080-broader-controls-plan';assert not(H/'protocol.json').exists();assert H.exists()
for name in['native.py','root-check.py']:
    code=(R/'runs/E051-broader-controls-plan'/name).read_text(encoding='utf-8').replace('E051','E080').replace("H.parent/'small-gain-confirmation-plan'","H.parent/'accepted-E051-live-20261018'").replace('import common as old','import common_e051_live as old').replace('old.exact_raw','old.historical.exact_raw')
    if name=='native.py':code=code.replace("'gpu_suite_tests_each':6,","'gpu_suite_tests_each':6,'preflop_gpu_tests_each':15,'continuation_symmetry_tests_each':3,")
    ast.parse(code);(H/name).write_text(code,encoding='utf-8',newline='\n')
source=old.read(R/'runs/E080-source/manifest.json');build=old.read(R/'runs/E080-broader-build-plan/protocol-r2.json');rows=[];binaries={};suite_ids={'baseline':{},'candidate':{}}
paths=[Path(__file__),R/'runs/E080-run-broader-controls.py',*[H/n for n in['native.py','root-check.py','warm.py']],B/'complete.json',R/'runs/E080-broader-build-plan/protocol.json',R/'runs/E080-broader-build-plan/protocol-r2.json',R/'comparisons/E080-fresh16-confirmation/report.json',R/'comparisons/E080-fresh16-root-check/report.json',C/'common_e051_live.py',C/'protected-main.json',old.REPO/'tools/postflop_autoresearch.py',old.REPO/'tools/postflop_validate_controls.py']
tests={'state':('postflop_state_perf','postflop_states',False,1),'menu':('postflop_action_menus','postflop_action_menus',False,1),'resume':('postflop_resume_state','postflop_resume_state',False,1),'gpu':('gpu','*',True,6),'preflop_gpu':('preflop_gpu','*',True,15),'f32':('postflop_autoresearch','postflop_complete_cycle',False,1),'paging':('continuation_paging','paging_preserves_resident_trajectories_and_rejects_invalid_inputs',True,1),'symmetry':('continuation_symmetry','*',True,3),'stored':('solver','gpu::continuation::storage::device_tests::direct_gpu_storage_preserves_720_full_state_passes',True,1)}
def bind(stem,arm):
    binary=R/'binaries'/(stem+'.exe');mp=binary.with_suffix('.manifest.json');m=old.read(mp);old.pin(binary,m['binary_sha256']);assert m['source_sha256']==old.BASE|(source['candidate_owned_sha256']if arm=='candidate'else{})
    binaries[stem]={'path':str(binary),'sha256':old.sha(binary),'manifest':str(mp),'manifest_sha256':old.sha(mp)};paths.extend([binary,mp]);return stem
for suite,(target,test,ordinary,passed)in tests.items():
    for arm in['baseline','candidate']:
        if suite in['state','menu','resume','gpu','preflop_gpu']:stem='E080-broader-'+arm+'-'+target
        elif suite=='f32':stem='E051-postflop_autoresearch'if arm=='baseline'else'E080-postflop_autoresearch'
        elif suite in['paging','symmetry']:stem=('E051-broader-'if arm=='baseline'else'E080-broader-')+target
        else:stem='E051-feature-solver'if arm=='baseline'else'E080-feature-solver'
        identity='V080-'+suite+'-'+arm;assert not(R/'runs'/identity).exists();row={'id':identity,'arm':arm,'suite':suite,'binary':bind(stem,arm),'test':test,'ordinary':ordinary,'passes':passed,'storage':'f32'if suite=='f32'else'compressed'}
        if suite=='stored':row['stored_root']=str(R/'runs/E080-broader-stored'/arm)
        rows.append(row)
        if suite in['state','menu','resume']:suite_ids[arm][suite]=identity
warm={arm:bind('E080-broader-'+arm+'-large-warm',arm)for arm in['baseline','candidate']};history={'state':'V020-state','menu':'V020-menu','resume':'V020-resume'}
for identity in list(history.values())+['V020-f32-candidate']:paths.extend([R/'runs'/identity/'report.json',R/'runs'/identity/'stdout.log'])
P={'id':'E080-broader-controls','at':old.now(),'status':'FROZEN_PRE_NATIVE','rows':rows,'binaries':binaries,'suite_ids':suite_ids,'historical_accepted_controls':history,'f32_accepted_anchor':'V020-f32-candidate','io_roots':{arm:data['io_root']for arm,data in build['arms'].items()},'saved_names':['postflop-state.gto','action-menus.gto','postflop-resume.gto'],'warm_binaries':warm,'warm_expected':{'stages':['warm_full','compact_initial_sync','compact_trained','root_query','materialized_resync','loaded','resumed','complete'],'raw_stages':['warm_full','compact_initial_sync','compact_trained','materialized_resync','loaded','resumed'],'iterations':[3,3,5,5,5,7],'q_bytes':1369522280,'minimum_overlap_bytes':64*1024*1024,'tags':[1,1,2,2],'successful_GPU_constructors_per_arm':3,'budget_rejections_per_arm':1,'iterations_executed_per_arm':7,'snapshots_per_arm':6},'input_sha256':{str(p):old.sha(p)for p in paths},'scope':'Fixed broad exact/tolerance controls, complete latest save-file bytes and additional full raw large warm compressed state parity. Compatibility evidence only, not additional performance samples or source variants. Actual CPU/host/GPU peak/capacity/responsiveness, holdout and fresh-original cumulative remain required. All raw output physically S; reserve 40 GiB beyond 66 GiB free. No adoption.'}
old.save(H/'protocol.json',P)
published=[]
for p in[Path(__file__),R/'runs/E080-run-broader-controls.py',*[p for p in H.iterdir()if p.is_file()]]:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
    published.append({'url':'evidence/'+key,'sha256':old.sha(p)})
old.save(H/'pre-native-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified_artifacts':published,'native_broader_observations':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(stage='Broader state, GPU and large warm-state controls',reason='All compilers are terminal and accepted source is restored. Run 18 fixed compatibility rows, then two fixed large warm compressed controls with six complete raw snapshots per arm. Source and timing cohorts remain frozen; material costs, holdout and cumulative checks still follow.');e['evidence'].append({'label':'Frozen broader native controls','url':'evidence/E080-broader-controls-plan/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 broader correctness controls',activity='Check state/menu/save/resume, postflop/preflop GPU equivalence, F32, continuation and full raw large compressed warm initialization. All observations retained; no source adoption.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print('E080 broader native protocol',old.sha(H/'protocol.json'),flush=True)
