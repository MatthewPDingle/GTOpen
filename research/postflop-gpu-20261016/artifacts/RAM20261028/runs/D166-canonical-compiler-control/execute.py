import sys,json,shutil,importlib.util,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def publish(folder,names):
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False)
spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
initial=bounded.memory();assert initial['available_physical']>=P['limits']['available_RAM_before_bytes'] and shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes']
h.save(O/'admission.json',{'at':h.now(),'actual_global_memory':initial,'X_free_bytes':shutil.disk_usage(ROOT).free,'all_admission_limits_passed':True,'no_native_children_yet':True})
publish(H,['protocol.json','source-review.json','bounded_child.py','audit.py'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D166')
    item.update(status='running',stage='Original full canonical CPU/66device raw state and lifecycle',reason='Frozen2compilers/BthenC,exactscienceanchors,target/cadence/cap,12wholeCPU+12all69fieldGPUframes/query/save/futureEVpairs.256GiBrawreserve+64GiBdiskheadroom,32GiBprocesscap. Honest prebuilt-PTX telemetry;no speed score.')
    item.setdefault('evidence',[]).append({'label':'Frozen full canonical raw state protocol','url':'evidence/D166-canonical-compiler-control/protocol.json'})
    status.update(updated_at=h.now(),active_experiment='D166',stage='CUDA13 full canonical raw state',activity='Capture all66actualdevicebuffers/CPUstate across original same-quality solves andcontinued/locked/resumed lifecycle,with RAM/disk guards. No runtime compiler implementation or acceptedgain.')
    h.ar.atomic_json(h.ar.STATUS,status)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes']
    for arm in P['sequence']:
        h.child(P['rustc_commands'][arm],O,'rustc-'+arm,1200);verify();data=(H/(arm+'.exe')).read_bytes();assert(H/(arm+'.ptx')).read_bytes() in data
        h.save(O/(arm+'.binary.json'),{'sha256':h.sha(H/(arm+'.exe')),'sealed_arm_PTX_embedded':True})
    for arm in P['sequence']:
        verify();h.ar.refuse_active(h.ar.live_status());output=H/(arm+'-output');output.mkdir(exist_ok=False)
        bounded.run([str(H/(arm+'.exe')),'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],O,arm,h,P['limits'],H,output);verify()
    h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify()
    D=ROOT/'comparisons/D166-canonical-compiler-control';r=h.read(D/'report.json');h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'source_main_live_protected_PTX_custody_pass':True,'report_sha256':h.sha(D/'report.json'),'performance_qualification_samples':0,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D166')
    item.update(status='measured',correctness='pass_full_canonical_raw_state',stage='6fullrecords/46checks and12CPU+12wholeGPUstatepairs exact',reason=f"Every{r['pair_bytes_compared']}comparedpairbytes exact;all66devicebuffers andphysicalCFV,CPUq/scales,query/save/resume/futureEVs. No prefix/paddingexception. Runtime compiler implementation andresource/speed qualification remain.")
    item.setdefault('evidence',[]).append({'label':'Complete canonical raw state/lifecycle result','url':'evidence/D166-canonical-compiler-control/report.json'})
    status.update(updated_at=h.now(),active_experiment='D166',stage='CUDA13 canonical accuracy prerequisite passed',activity='Original fullsize science andallCPU/device rawstate/lifecycle pairs exact. Next postflop-only runtime compiler integration with real loader/compile/JIT cost beforefresh speed qualification. E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:r[k] for k in ['status','scientific_full_records_exact','canonical_checkpoints_exact','GPU_all69field_pairs','pair_bytes_compared','reader_checks']}),flush=True)
