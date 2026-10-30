import sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();B=H/'build-r3';C=old.read(B/'complete.json');assert C['all_compilers_terminal'] and C['native_executions']==0
for p,h in C['artifact_sha256'].items():old.pin(p,h)
P={'id':'D085-ability','at':old.now(),'status':'FROZEN_BEFORE_NATIVE','binary':str(B/'ability.exe'),'collector':str(B/'D085Collector.dll'),'private_dll_dirs':C['private_dll_dirs'],'output_dir':str(H/'ability-execution'),'expected_kernel_records':13,'expected_eager_records':1,'expected_graph_records':12,'expected_distinct_graph_nodes':3,'expected_each_graph_node_executions':4,'expected_data_words':257,'expected_value':13,'row_bytes':176,'no_drops_errors_missing_timestamps_or_outstanding_buffers':True,'same_GPU':'RTX5090compute120','diagnostic_only':True,'performance_measured':False,'input_sha256':C['artifact_sha256']|{str(p):old.sha(p) for p in [B/'complete.json',H/'build-plan-r3.json',H/'collector.cpp',H/'ability.rs',H/'run-ability.py']}}
old.save(H/'ability-plan.json',P)
for p in [H/'ability-plan.json',H/'run-ability.py',B/'complete.json']:
 key=H.name+'/'+p.relative_to(H).as_posix();dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(H/'ability-plan.json'),flush=True)
