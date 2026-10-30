import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D246-cluster-resource';assert len(sys.argv)==2;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();O.mkdir(exist_ok=False);assert not(H/'probe.exe').exists()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
rows=[json.loads(l.split('D246_RESOURCE ',1)[1])for l in(O/'probe.stdout.log').read_text().splitlines()if'D246_RESOURCE 'in l];assert len(rows)==9 and rows[-1]=={'stage':'complete','compile_variants':1,'application_kernels':0,'solver_or_speed_samples':0}
ptx=(O/'primitive-compute_120.ptx').read_text();gates={}
for i,row in enumerate(rows[:-1]):
 gates[str(i)+':requiredcluster']=row['required_cluster_dimensions']==[2,1,1];gates[str(i)+':positiveactiveclusters']=row['active_clusters']>0;gates[str(i)+':no_local']=row['local_bytes_per_thread']==0;gates[str(i)+':defaultfit']=row['dynamic_shared_bytes_per_block']+row['static_shared_bytes']<=row['device_shared_limit']and row['threads']<=row['max_threads'];gates[str(i)+':no_stackgrowth']=row['stack_after']==row['stack_before']
gates['PTX_cluster_mapping_present']='mapa.shared::cluster' in ptx;gates['PTX_cluster_barriers_present']='barrier.cluster' in ptx
h.save(H/'report.json',{'id':'D246-resource','at':h.now(),'status':'pass_cluster_primitive_resources_operand_review_pending'if all(gates.values())else'rejected_fixed_cluster_primitive_resource','protocol_sha256':sys.argv[1],'gates':gates,'resources':rows[:-1],'PTX_sha256':h.sha(O/'primitive-compute_120.ptx'),'binary_sha256':h.sha(H/'probe.exe'),'all_owned_children_terminal':True,'application_kernel_launches_solves_speed_samples':0,'candidate_accepted':False,'limits':'Featurecompiler/functionattributes/defaultfit/clusteroccupancy only. Actualmappedoperand/PTXbarriers thenwholeword/guards/immutableinput/lifetime/graphcontrols remain. No poker/GPUoptimizer admitted orspeedgain.'});h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'appkernels':0})
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
print(json.dumps({'all_gates_pass':all(gates.values()),'failed':[k for k,v in gates.items()if not v],'resource_rows':rows[:-1]}),flush=True)
