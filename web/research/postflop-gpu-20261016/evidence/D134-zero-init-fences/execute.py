"""One compile/ability then fixed six copied-constructor processes; no full solves."""
from pathlib import Path
import json,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=H/'execution'
def verify():
    old.custody();old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
verify();assert not E.exists()and not(H/'probe.exe').exists();E.mkdir()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=P['minimum_free_S_bytes']
    gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee'in gpu['stdout'];old.save(E/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
    old.child(P['rustc_command'],E,'rustc',old.env(),900);verify();old.save(E/'build-complete.json',{'at':old.now(),'binary_sha256':old.sha(H/'probe.exe'),'compiler_terminal':True,'native_processes':0})
    a=E/'ability';a.mkdir();old.child([str(H/'probe.exe'),'ability',str(a)],E,'ability',old.env(),600);verify()
    marks=[json.loads(x.split('D134 ',1)[1])for x in(E/'ability.stdout.log').read_text().splitlines()if'D134 'in x];assert len(marks)==9 and marks[-1]['stage']=='ability_complete'and marks[-1]['comparisons']==4 and marks[-1]['fresh_warm_compressed_F32']and marks[-1]['four_budget_rejections_equal']and marks[-1]['injected_nonzero_OR_controls_rejected']==3
    for mark in marks[:-1]:assert mark['stage']=='case'and not mark['timed']and mark['proof']['fields']==66 and mark['proof']['all_complete_images_exact']
    old.save(E/'ability-report.json',{'at':old.now(),'status':'pass_scoped_fresh_warm_compressed_F32_and_budget','summary':marks[-1],'records':marks[:-1],'native_processes':1,'performance_samples':0,'candidate_accepted':False})
    for row in P['order']:
        verify();old.ar.refuse_active(old.ar.live_status());d=E/row['id'];d.mkdir();old.child([str(H/'probe.exe'),row['arm'],str(d)],E,row['id'],old.env(),600);verify();markers=[json.loads(x.split('D134 ',1)[1])for x in(E/(row['id']+'.stdout.log')).read_text().splitlines()if'D134 'in x];assert len(markers)==4 and markers[-1]['stage']=='complete'and markers[-1]['cases']==3 and markers[-1]['kernel_launches']==0
        for i,mark in enumerate(markers[:-1]):assert mark['stage']=='case'and mark['arm']==row['arm']and mark['id'].startswith(str(i)+'-')and mark['timed']and mark['all_four_host_stores_positive_zero']and mark['proof']['all_complete_images_exact']and mark['proof']['fields']==66 and mark['solver_iteration']==0
        old.save(E/(row['id']+'.parsed.json'),{'at':old.now(),'cases':markers[:-1],'complete':markers[-1],'frame_sha256':{str(p):old.sha(p)for p in d.glob('*.bin')}});print('D134 component finished',row['id'],flush=True)
    old.save(E/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'compiler_count':1,'ability_processes':1,'timing_processes':6,'initialization_components':18,'application_kernel_launches':0,'full_solver_executions':0,'protocol_sha256':sys.argv[1],'source_main_live_PTX_custody_pass':True});verify()
print('D134 fixed component observations terminal; assess retained data next.',flush=True)
