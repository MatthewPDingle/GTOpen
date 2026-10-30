import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/E111-resource';P=h.read(H/'protocol.json');O=H/'execution';assert len(sys.argv)==2
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
 t=path.read_text();out={};i=0
 while True:
  i=t.find('.visible .entry ',i)
  if i<0:break
  a=t.index('(',i);name=t[i+len('.visible .entry '):a].strip();a=t.index('{',a);j=a+1;depth=1
  while depth:
   depth+=(t[j]=='{')-(t[j]=='}');j+=1
  assert name not in out;out[name]=t[i:j];i=j
 return out
def norm(t):
 t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',t);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E111_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text().splitlines()if'E111_RESOURCE 'in x];assert len(markers)==22 and markers[-1]['stage']=='complete';rows={(x['variant'],x['kernel']):x for x in markers if x['stage']=='resource'};clusters=[x for x in markers if x['stage']=='cluster_resource'];assert len(rows)==18 and len(clusters)==3
gates={};tables={};allentries={}
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));allentries[arch]=c;gates[arch+':entryset']=set(c)==set(b)|({'up_show_cluster'}if arch=='compute_120'else set());tables[arch]={}
 for name in P['original_entries']:
  exact=norm(b[name])==norm(c[name]);tables[arch][name]={'header_ABI_exact':b[name].split('{',1)[0]==c[name].split('{',1)[0],'entire_entry_alpha_exact':exact};gates[arch+':'+name+':entire_entry_exact']=exact
cluster=allentries['compute_120']['up_show_cluster'];original=allentries['compute_120']['up_show'];params=lambda t:[(typ,int(n))for typ,n in re.findall(r'\.param\s+\.(\w+)\s+\w+_param_(\d+)',t.split('{',1)[0])]
gates['cluster:original27paramABI']=params(cluster)==params(original)and len(params(cluster))==27;gates['cluster:mapa_present']='mapa.u64'in cluster;gates['cluster:publication_lifetime_instructions_present']=cluster.count('barrier.cluster.arrive')>=2 and cluster.count('barrier.cluster.arrive')==cluster.count('barrier.cluster.wait');gates['cluster:four_original_local_barriers']=cluster.count('bar.sync')==4
for name in P['original_entries']:
 b,c=rows['baseline',name],rows['candidate',name];keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after'];gates[name+':actual_resources_exact']=all(b[k]==c[k]for k in keys)
b=rows['baseline','up_show']
for c in clusters:
 prefix='cluster:'+str(c['threads']);gates.update({prefix+':required_dims':c['required_cluster_dimensions']==[2,1,1],prefix+':positive_actual_clusters':c['active_clusters']>0,prefix+':no_new_local':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],prefix+':no_dynamic_growth':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],prefix+':no_maxthread_loss':c['max_threads']>=b['max_threads'],prefix+':default_limits_fit':c['static_shared_bytes']+c['dynamic_shared_bytes']<=c['device_shared_limit']and c['max_threads']>=256 and c['device_thread_limit']>=256,prefix+':no_stack_growth':c['context_stack_after']<=b['context_stack_after']})
passed=all(gates.values());h.save(H/'report.json',{'id':'E111-resource','at':h.now(),'status':'pass_scoped_cluster_resources_ABI_mechanism_pending'if passed else'rejected_closed_cluster_resource_or_ABI','protocol_sha256':sys.argv[1],'gates':gates,'original_entry_tables':tables,'original_resource_rows':list(rows.values()),'cluster_resources':clusters,'warnings':'Cluster co-scheduling changes effective node residency and remote access/barrier costs; reported registers/static shared/occupancy are disclosures, not measured performance or no-material-cost proof. Additional code/JIT/host costs unqualified.','PTX_sha256':{arm+'-'+arch:h.sha((H if arm=='baseline'else O)/(arm+'-'+arch+'.ptx'))for arm in ['baseline','candidate']for arch in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches_solver_or_speed_samples':0,'source_activated':False,'candidate_accepted':False,'limits':P['scope']});h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True});verify()
p=H/'report.json';dst=h.ar.DASHBOARD/'evidence'/H.name/p.name;assert not dst.exists();shutil.copyfile(p,dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E111');e.update(status='running'if passed else'rejected',stage='Compiled cluster gate passed; mapped operand and host controls pending'if passed else'Closed at fixed cluster resource/ABI gate',reason='Module-only pass='+str(passed)+'; failed gates='+str([k for k,v in gates.items()if not v])+'. No application kernels or speed samples.');e['evidence'].append({'label':'Actual compiled resources and ABI','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),active_experiment='E111',stage=e['stage'],activity=e['reason']+' E080 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'pass':passed,'failed':[k for k,v in gates.items()if not v],'cluster_resources':clusters}),flush=True)
