import hashlib, json, re, shutil, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/E102-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,digest in P['input_sha256'].items():h.pin(p,digest)
def entries(path):
    text=path.read_text(encoding='utf-8');out={};i=0
    while True:
        i=text.find('.visible .entry ',i)
        if i<0:break
        n=text.index('(',i);name=text[i+len('.visible .entry '):n].strip();a=text.index('{',n);j=a+1;depth=1
        while depth:
            if text[j]=='{':depth+=1
            elif text[j]=='}':depth-=1
            j+=1
        assert name not in out;out[name]=text[i:j];i=j
    return out
def normalize(text):
    text=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text);text=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',text)
    return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',text)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
    h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E102_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E102_RESOURCE ' in x]
assert len(markers)==5 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==3
gates={};originals={};bodies={}
for arch in ['compute_120','compute_75']:
    b=entries(O/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'))
    assert set(b)==set(P['expected_original_entries']) and set(c)==set(b)|{P['new_entry']}
    originals[arch]={name:normalize(b[name])==normalize(c[name]) for name in b}
    gates[arch+':original9_entries_and_ABIs_exact']=len(originals[arch])==9 and all(originals[arch].values())
    new=c[P['new_entry']];header=new.split('{',1)[0]
    gates[arch+':new16parameter_ABI']=header.count('.param ')==P['new_entry_parameters']
    gates[arch+':no_barriers']='bar.sync' not in new
    arithmetic=[line.strip() for line in new.splitlines() if re.search(r'\b(?:add|sub|mul|mad|fma|div|rcp|sqrt|cvt)(?:\.[\w]+)*\.f32\b',line)]
    gates[arch+':no_floating_arithmetic']=not arithmetic
    path=O/('candidate-'+arch+'-down_chance_parent.ptx');path.write_text(new,encoding='utf-8',newline='\n')
    bodies[arch]={'path':str(path),'sha256':h.sha(path),'f32_arithmetic':arithmetic,'header':header,'static_mechanism_review_required':True}
b=rows['baseline','down_chance'];oldc=rows['candidate','down_chance'];c=rows['candidate','down_chance_parent']
keys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','occupancy_by_threads','fits_default_limits']
gates['actual_original_down_chance_resource_rows_exact']=all(b[k]==oldc[k] for k in keys)
bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads'])
tests={'no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_shared_growth':c['static_shared_bytes']+c['dynamic_shared_bytes']<=b['static_shared_bytes']+b['dynamic_shared_bytes'],'max_threads_not_lowered':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'both_fit_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'no_default_stack_growth':c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']}
gates.update(tests)
warnings=[]
if c['registers']>b['registers'] or any(co[t]<bo[t] for t in bo):warnings.append({'baseline':b,'candidate':c})
passed=all(gates.values())
q={'id':'E102-resource','at':h.now(),'status':'stage1_pass_parent_load_loop_review_required' if passed else 'rejected_closed_compiler_resource_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'original9_entries':originals,'new_entry_bodies':bodies,'resource_rows':list(rows.values()),'resource_warnings':warnings,'ptx_sha256':{v+'-'+a:h.sha(O/(v+'-'+a+'.ptx')) for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'all_owned_compiler_native_children_terminal':True,'application_kernels':0,'solver_runs':0,'performance_samples':0,'source_activated':False,'candidate_accepted':False,'mechanism_proven':False,'limits':'Compiler/ABI/resources/copy-only stage. Parent reach-load outside representative-card loops still needs static proof; no numerical/physical-liveness/full-solve/material/capacity or speed claim.'}
h.save(H/'report.json',q);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_compiler_native_children_terminal':True,'application_kernels':0});verify()
dst=h.ar.DASHBOARD/'evidence'/H.name/'report.json';assert not dst.exists();shutil.copyfile(H/'report.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=20) as response:assert response.read()==(H/'report.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E102')
    item.update(status='running' if passed else 'rejected',stage='Compiler stage1 passed; parent-load loop proof pending' if passed else 'Compiler prerequisite failed; exact form closed',reason='Original9 entries/ABIs and new16-parameter copy-only/resource stage1: '+str(passed)+'. No application kernels or accuracy/speed result. Parent-load placement and full raw controls still required. Failed gates: '+str([k for k,v in gates.items() if not v]))
    item['evidence'].append({'label':'Compiled entries and actual resource stage1','url':'evidence/'+H.name+'/report.json'})
    status.update(updated_at=h.now(),stage=item['stage'],activity='E102 compiler stage1 is published. No application kernels or new gain. E080 with 16 workers remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'status':q['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':[{k:x[k] for k in ['variant','kernel','registers','local_bytes_per_thread','occupancy_by_threads']} for x in rows.values()],'application_kernels':0}),flush=True)
