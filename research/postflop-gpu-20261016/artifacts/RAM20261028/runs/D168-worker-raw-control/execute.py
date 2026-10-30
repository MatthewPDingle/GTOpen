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
        p=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False);publish(H,['protocol.json','source-review.json','probe.rs'])
spec=importlib.util.spec_from_file_location('bounded',H/'bounded_child.py');bounded=importlib.util.module_from_spec(spec);spec.loader.exec_module(bounded)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D168')
    item.update(status='running',correctness='raw_controls_in_progress',stage='Actualpoolandfullcanonicalrawproof16/8/32;unscored',reason='SameacceptedE080/prebuilt12PTX. ActualRayoncountcheckedafterentirework;allCPU/66GPUbuffers/CFV/query/save/EVscompared. No clocks/source/quality/preinitialization changes. Alltimingsdiagnostic,notqualification.')
    item.setdefault('evidence',[]).append({'label':'Frozen CPU configuration rawcontrols','url':'evidence/D168-worker-raw-control/protocol.json'});status.update(updated_at=h.now(),active_experiment='D168',stage='CPU workers actualpool/rawstate controls',activity='Check16/8/32actualglobalpoolafterallworkandcomparefullcanonicalCPU/device/lifecycledata. SameacceptedE080,noCUDA13variant orspeedscore.');h.ar.atomic_json(h.ar.STATUS,status)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['limits']['required_free_bytes'];assert bounded.memory()['available_physical']>=P['limits']['available_RAM_before_bytes']
    h.child(P['rustc_command'],O,'rustc',1200);verify();assert (H/'baseline.ptx').read_bytes() in(H/'probe.exe').read_bytes();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'one_binary_allconfigs':True,'sealed12PTXembedded':True})
    for row in P['sequence']:
        verify();h.ar.refuse_active(h.ar.live_status());out=H/(row['id']+'-output');out.mkdir(exist_ok=False)
        bounded.run([str(H/'probe.exe'),'--exact','d168_worker_controls','--ignored','--nocapture','--test-threads=1'],O,row['id'],h,P['limits'],H,out,row['workers']);verify()
        lines=(O/(row['id']+'.stdout.log')).read_text(encoding='utf-8').splitlines();pool=[json.loads(x.split('D168_POOL ',1)[1]) for x in lines if x.startswith('D168_POOL ')]
        assert pool==[{'requested':row['workers'],'actual':row['workers'],'observation_after_entire_suite_and_lifecycle':True}]
    h.child([sys.executable,str(H/'audit.py')],O,'audit',1800);verify();D=ROOT/'comparisons/D168-worker-raw-control';r=h.read(D/'report.json');h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'no_performance_samples':True,'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D168');item.update(status='measured',correctness='pass_actualpools_fullraw_allconfigs',stage='Actual8/16/32poolsandallfullrawcanonicalstateexact',reason=f"All9fullrecords/69checkpointsand{r['pair_bytes_compared']}comparedpairbytesexact. SameE080;metadataafterallsuitework. No performancegainclaimed;nextseparatelyfrozenbalancedfinitecomparison.")
    item.setdefault('evidence',[]).append({'label':'Actualworker/fullrawoutcomes','url':'evidence/D168-worker-raw-control/report.json'});status.update(updated_at=h.now(),active_experiment='D168',stage='CPUworkerrawproofpassed',activity='8/16/32actualpoolsandfullCPU/device/lifecycledataexact. Nextfreeze3freshobservations/configbalancedcomparisonwithrealruntimecompilerclocks. No gainadopted;E08016workersstayslive.');h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:r[k] for k in ['status','actual_workers','unique_full_records_exact','unique_checkpoints_exact','pair_bytes_compared','reader_checks']}),flush=True)
