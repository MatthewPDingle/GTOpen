"""One compiler/module resource process; no application kernel launches or array allocations."""
import json,re,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-resource';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def entries(path):
    text=path.read_text(encoding='utf-8');result={}
    for match in re.finditer(r'\.visible \.entry (\w+)\(',text):
        opening=text.index('{',match.end());i=opening+1;depth=1
        while depth:depth+=(text[i]=='{')-(text[i]=='}');i+=1
        result[match[1]]=text[match.start():i]
    return result
def normalize(text):
    text=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text);text=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',text)
    return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',text)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    assert gpu['stdout']==h.read(ROOT/'runs/E126-resource/execution/before.json')['GPU']['stdout']and P['GPU_uuid']in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'application_kernels':0})
    h.child(P['rustc_command'],O,'rustc',300);verify();h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(line.split('E127_RESOURCE ',1)[1])for line in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E127_RESOURCE 'in line]
assert len(markers)==20 and markers[-1]['resource_rows']==19 and markers[-1]['application_kernels']==0
rows={(x['variant'],x['kernel']):x for x in markers[:-1]};assert len(rows)==19
gates,tables={},{}
for arch in['compute_120','compute_75']:
    a,b=entries(H/('baseline-'+arch+'.ptx')),entries(O/('candidate-'+arch+'.ptx'))
    assert set(a)==set(P['original_entries'])and set(b)==set(a)|{'up_action_star'};tables[arch]={}
    for name in P['original_entries']:
        exact=normalize(a[name])==normalize(b[name]);gates[arch+':'+name+':original_body_header_exact']=exact;tables[arch][name]={'body_header_alpha_exact':exact}
    header=b['up_action_star'].split('{',1)[0];expected=a['up_action'].split('{',1)[0].replace('up_action','up_action_star')
    gates[arch+':new20paramABI_originalupaction']=header==expected and header.count('.param ')==20
    gates[arch+':one_original_star_barrier']=len(re.findall(r'\bbar\.sync\b',b['up_action_star']))==1
    (O/('star-'+arch+'.ptx.txt')).write_bytes(b['up_action_star'].encode())
keys=['registers','local_bytes_per_thread','constant_bytes','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
for name in P['original_entries']:gates[name+':original_resources_exact']=all(rows['baseline',name][k]==rows['candidate',name][k]for k in keys)
a,b=rows['baseline','up_action'],rows['candidate','up_action_star']
gates.update({'star:no_local_growth':b['local_bytes_per_thread']<=a['local_bytes_per_thread'],'star:no_constant_growth':b['constant_bytes']<=a['constant_bytes'],'star:no_static_growth':b['static_shared_bytes']<=a['static_shared_bytes'],'star:no_dynamic_growth':b['dynamic_shared_bytes']==a['dynamic_shared_bytes'],'star:no_stack_growth':b['context_stack_after']<=a['context_stack_after'],'star:no_maxthread_loss':b['max_threads']>=a['max_threads'],'star:positive_occupancy':all(v>0 for t,v in b['occupancy_by_threads']),'star:default_limits_fit':b['max_threads']>=256 and b['static_shared_bytes']+b['dynamic_shared_bytes']<=b['device_shared_limit']})
warnings=[]
if b['registers']>a['registers']or any(dict(b['occupancy_by_threads'])[t]<v for t,v in a['occupancy_by_threads']):warnings.append({'baseline':a,'candidate':b})
passed=all(gates.values())
h.save(H/'report.json',{'id':'E127-resource','at':h.now(),'status':'pass_shader_resources_mechanism_and_host_still_pending'if passed else'rejected_closed_shader_resource_gate',
    'protocol_sha256':sys.argv[1],'gates':gates,'entry_tables':tables,'resource_rows':markers[:-1],'resource_warnings':warnings,
    'PTX_sha256':{arm+'-'+arch:h.sha((H if arm=='baseline'else O)/(arm+'-'+arch+'.ptx'))for arm in['baseline','candidate']for arch in['compute_120','compute_75']},
    'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_or_speed_trials':0,'source_activated':False,'candidate_accepted':False,
    'limits':'Resource/ABI/prefix proof only. No actualtwo-levelGPUarithmetic/hostschedule/ownership/material/capacity/speedqualification. Genuinehardfailureclosesfixedformwithouttuning.'})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E127')
    row.update(at=h.now(),status='running'if passed else'rejected',stage='Shader resources passed; mechanism and host work pending'if passed else'Closed at shader resource gate',correctness='no_device_numerical_trials',reason='Shader resource gate passed: '+str(passed)+'. Failed checks: '+str([k for k,v in gates.items()if not v])+'. Original nine kernels remain unchanged. No GPU numerical or speed result.')
    status.update(updated_at=h.now(),active_experiment='E127',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'pass':passed,'failed':[k for k,v in gates.items()if not v],'baseline_upaction':a,'new_star':b}),flush=True)
