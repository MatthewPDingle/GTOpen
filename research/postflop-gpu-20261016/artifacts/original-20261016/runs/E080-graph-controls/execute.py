"""Compile observation-only harnesses, then execute exactly the frozen controls."""
from pathlib import Path
import json,os,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
    old.custody();old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
verify();B=H/'build';E=H/'execution';assert not B.exists()and not E.exists();B.mkdir();E.mkdir()
try:
    with old.ar.exclusive_lock(R/'gpu-run.lock'):
        old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
        for row in P['commands']:
            d=B/row['id'];d.mkdir();old.child(row['command'],d,'rustc',old.env(),600);verify()
        bins={'baseline':P['baseline_binary'],'candidate':P['commands'][0]['path']}
        old.save(H/'binary-binding.json',{'at':old.now(),'protocol_sha256':sys.argv[1],'sha256':{p:old.sha(p)for p in list(bins.values())+[P['commands'][1]['path']]},'candidate_source_sha256':P['source_sha256']['candidate'],'native_observations':0})
        for arm in P['order']:
            verify();old.ar.refuse_active(old.ar.live_status());d=E/arm;d.mkdir();e=old.env();e['POSTFLOP_AUTORESEARCH_FIXTURE']='rainbow';e['D087_TRACE_FILE']=str(d/'trace.bin');e['D087_META_FILE']=str(d/'collector.jsonl');e['PATH']=os.pathsep.join(P['private_dll_dirs'])+os.pathsep+e['PATH']
            assert not e.get('CUDA_INJECTION64_PATH')and not e.get('CUDA_INJECTION32_PATH')
            old.child([bins[arm],'--exact','postflop_complete_cycle','--ignored','--nocapture','--test-threads=1'],d,'native',e,600);verify();print('Trace completed',arm,flush=True)
        d=E/'resources';d.mkdir();old.child([P['commands'][1]['path'],str(d)],d,'native',old.env(),600);verify()
    old.save(E/'complete.json',{'at':old.now(),'all_owned_children_terminal':True,'native_trace_processes':2,'resource_probe_processes':1,'protocol_sha256':sys.argv[1],'performance_score':False,'candidate_adopted':False})
except BaseException as exc:
    old.save(E/'failure.json',{'at':old.now(),'error':repr(exc),'preserve_all_observations':True,'candidate_adopted':False});raise
