"""One compiler/module-only resource control, preserve all9entry comparisons."""
import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E125-resource';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def entries(path):
    text=path.read_text(encoding='utf-8');result={}
    for match in re.finditer(r'\.visible \.entry (\w+)\(',text):
        opening=text.index('{',match.end());index=opening+1;depth=1
        while depth:
            depth+=(text[index]=='{')-(text[index]=='}');index+=1
        result[match[1]]=text[match.start():index]
    return result
def normalized(text):
    text=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text)
    text=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',text)
    return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',text)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    assert gpu['stdout']==h.read(ROOT/'runs/D308-packed-arithmetic/execution/before.json')['gpu']['stdout']and P['GPU_uuid']in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'application_kernels':0})
    h.child(P['rustc_command'],O,'rustc',300);verify()
    h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(line.split('E125_RESOURCE ',1)[1])for line in(O/'probe.stdout.log').read_text(encoding='utf-8').splitlines()if'E125_RESOURCE 'in line]
assert len(markers)==19 and markers[-1]['resource_rows']==18 and markers[-1]['application_kernels']==0
rows={(row['variant'],row['kernel']):row for row in markers[:-1]}
assert len(rows)==18
gates,tables,warnings={},{},[]
for arch in ['compute_120','compute_75']:
    a,b=entries(H/('baseline-'+arch+'.ptx')),entries(O/('candidate-'+arch+'.ptx'))
    assert set(a)==set(b)==set(P['original_entries']);tables[arch]={}
    for name in P['original_entries']:
        table={'header_ABI_exact':a[name].split('{',1)[0]==b[name].split('{',1)[0],'body_alpha_exact':normalized(a[name])==normalized(b[name])}
        tables[arch][name]=table;gates[arch+':'+name+':header_exact']=table['header_ABI_exact']
        if name!='up_chance':gates[arch+':'+name+':untargeted_exact']=table['body_alpha_exact']
        else:
            gates[arch+':up_chance:body_changed']=not table['body_alpha_exact']
            gates[arch+':up_chance:barriers_same']=a[name].count('bar.sync')==b[name].count('bar.sync')
            narrow=lambda text:len(re.findall(r'\bld\.global(?:\.\w+)*\.u16\b',text))
            wide=lambda text:len(re.findall(r'\bld\.global(?:\.\w+)*\.u32\b',text))
            gates[arch+':one_u16_load_instead_of_u32']=narrow(a[name])==0 and narrow(b[name])==1 and wide(b[name])==wide(a[name])-1
            tables[arch][name].update(baseline_global_u32_load_sites=wide(a[name]),candidate_global_u32_load_sites=wide(b[name]),candidate_global_u16_load_sites=narrow(b[name]))
            for arm,text in [('baseline',a[name]),('candidate',b[name])]:
                (O/(arm+'-'+arch+'-up_chance.ptx.txt')).write_bytes(text.encode())
keys=['registers','local_bytes_per_thread','constant_bytes','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','context_stack_after']
for name in P['original_entries']:
    a,b=rows['baseline',name],rows['candidate',name]
    if name!='up_chance':gates[name+':actual_resources_exact']=all(a[k]==b[k]for k in keys)
    else:
        gates.update({name+':no_new_local':b['local_bytes_per_thread']<=a['local_bytes_per_thread'],name+':no_constant_growth':b['constant_bytes']<=a['constant_bytes'],name+':no_dynamic_growth':b['dynamic_shared_bytes']==a['dynamic_shared_bytes'],name+':no_maxthread_loss':b['max_threads']>=a['max_threads'],name+':positive_occupancies':all(count>0 for width,count in b['occupancy_by_threads']),name+':defaultlimits_fit':b['static_shared_bytes']+b['dynamic_shared_bytes']<=b['device_shared_limit']and b['max_threads']>=256 and b['device_thread_limit']>=256,name+':no_stack_growth':b['context_stack_after']<=a['context_stack_after']})
        if b['registers']>a['registers']or b['static_shared_bytes']>a['static_shared_bytes']or any(dict(b['occupancy_by_threads'])[t]<v for t,v in a['occupancy_by_threads']):warnings.append({'entry':name,'baseline':a,'candidate':b})
passed=all(gates.values())
h.save(H/'report.json',{'id':'E125-resource','at':h.now(),'status':'pass_resource_and_emitted_u16_load_prerequisites'if passed else'rejected_closed_resource_or_emitted_load_gate',
    'protocol_sha256':sys.argv[1],'gates':gates,'entry_tables':tables,'resource_rows':list(rows.values()),'resource_warnings':warnings,
    'PTX_sha256':{arm+'-'+arch:h.sha((H if arm=='baseline'else O)/(arm+'-'+arch+'.ptx'))for arm in['baseline','candidate']for arch in['compute_120','compute_75']},
    'all_owned_children_terminal':True,'application_kernel_launches':0,'source_activated':False,'solver_or_speed_samples':0,'candidate_accepted':False,
    'limits':'Typedreadonlyu16load/resource/ABIgate only. ActualfullGPUword/CPUplan/upload/capacity/broad/solverquality/completecyclespeed notyettested. No newgain.'})
h.custody()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);row=next(x for x in status['experiments']if x['id']=='E125')
    row.update(status='running'if passed else'rejected',at=h.now(),stage='Resource/emitted-load passed; fullraw controls pending'if passed else'Closed atresource/emittedloadgate',correctness='no_device_numerical_trials',reason='Resource/emittedu16load pass='+str(passed)+'. Failedgates='+str([k for k,v in gates.items()if not v])+'. All8otherentriesexact. E080liveunchanged; no speedgainclaimed.')
    status.update(updated_at=h.now(),active_experiment='E125',stage=row['stage'],activity=row['reason']);h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'pass':passed,'failed':[k for k,v in gates.items()if not v],'resource_warnings':[x['entry']for x in warnings],'up_chance':{a:tables[a]['up_chance']for a in tables}}),flush=True)
