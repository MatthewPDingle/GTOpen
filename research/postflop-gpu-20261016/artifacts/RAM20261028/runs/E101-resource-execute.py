import hashlib, json, re, shutil, sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2
H=ROOT/'runs/E101-resource';P=h.read(H/'protocol.json');O=H/'execution'
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,digest in P['input_sha256'].items():h.pin(p,digest)
def entries(path):
    source=path.read_text(encoding='utf-8');out={};i=0
    while True:
        i=source.find('.visible .entry ',i)
        if i<0:break
        start=source.index('(',i);name=source[i+len('.visible .entry '):start].strip();opening=source.index('{',start);j=opening+1;depth=1
        while depth:
            if source[j]=='{':depth+=1
            elif source[j]=='}':depth-=1
            j+=1
        assert name not in out;out[name]=source[i:j];i=j
    return out
def normalize(source):
    source=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',source)
    source=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',source)
    return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',source)
verify();assert not(H/'probe.exe').exists();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernel_launches':0})
    h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'at':h.now(),'sha256':h.sha(H/'probe.exe')})
    h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('E101_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E101_RESOURCE ' in x]
assert len(markers)==8 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==6
tables={(v,a):entries(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']}
assert all(set(x)==set(P['expected_entries']) for x in tables.values())
gates={};other={};changes={};quotients={};warnings=[]
for arch in ['compute_120','compute_75']:
    b,c=tables['baseline',arch],tables['candidate',arch]
    other[arch]={name:normalize(b[name])==normalize(c[name]) for name in b if name not in P['targets']}
    gates[arch+':other6entries_exact']=len(other[arch])==6 and all(other[arch].values())
    changes[arch]={};quotients[arch]={}
    for name,contract in P['targets'].items():
        bh,ch=b[name].split('{',1)[0],c[name].split('{',1)[0]
        gates[arch+':'+name+':ABI_exact']=bh==ch and bh.count('.param ')==contract['parameters']
        gates[arch+':'+name+':barriers_exact']=b[name].count('bar.sync')==c[name].count('bar.sync')
        changes[arch][name]=normalize(b[name])!=normalize(c[name])
        if arch=='compute_120':gates[name+':actual_entry_changed']=changes[arch][name]
        quotients[arch][name]={}
        for variant,entry in [('baseline',b[name]),('candidate',c[name])]:
            (O/f'{variant}-{arch}-{name}.ptx').write_text(entry,encoding='utf-8',newline='\n')
            lines=entry.splitlines();sites=[]
            for i,line in enumerate(lines):
                if re.search(r'\bdiv\.(?:rn|approx)\.f32\b',line):
                    sites.append({'entry_line_1based':i+1,'instruction':line.strip(),'preceding_40_lines':lines[max(0,i-40):i],'following_8_lines':lines[i+1:i+9]})
            quotients[arch][name][variant]={'native_division_sites':sites,'full_entry_sha256':hashlib.sha256(entry.encode()).hexdigest(),'static_sites_are_not_dynamic_work_or_bypass_proof':True}
for name in P['targets']:
    b,c=rows['baseline',name],rows['candidate',name];bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads'])
    tests={'no_new_local_spill':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'no_dynamic_shared_increase':c['dynamic_shared_bytes']<=b['dynamic_shared_bytes'],'max_threads_not_lowered':c['max_threads']>=b['max_threads'],'positive_fixed_occupancies':all(bo[t]>0 and co[t]>0 for t in [64,128,256]),'both_fit_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'no_stack_growth':c['context_stack_limit_after_load']<=b['context_stack_limit_after_load']}
    gates.update({name+':'+k:v for k,v in tests.items()})
    if c['registers']>b['registers'] or c['static_shared_bytes']>b['static_shared_bytes'] or any(co[t]<bo[t] for t in bo):warnings.append({'entry':name,'baseline':b,'candidate':c})
passed=all(gates.values())
report={'id':'E101-resource','at':h.now(),'status':'stage1_pass_separate_full_entry_bypass_review_required' if passed else 'rejected_closed_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'changed_target_entries':changes,'other6entry_bodies':other,'resource_rows':list(rows.values()),'resource_warnings':warnings,'quotient_sites':quotients,'ptx_sha256':{v+'-'+a:h.sha(O/f'{v}-{a}.ptx') for v in ['baseline','candidate'] for a in ['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'mechanism_proven':False,'scope':'Stage1 only: entry/ABI/barrier/resources/code-change checks. Full-entry static control-flow evidence must establish zero-numerator quotient bypass before any application kernel. No numeric or speed claim. Failed gates close exact source without conditional/predicate/scope/flags/source rescue.'}
h.save(H/'report.json',report);h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify()
dst=h.ar.DASHBOARD/'evidence'/H.name/'report.json';assert not dst.exists();shutil.copyfile(H/'report.json',dst)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/report.json',timeout=20) as response:assert response.read()==(H/'report.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='E101')
    item.update(status='running' if passed else 'rejected',stage='Compiler stage1 passed; static bypass proof pending' if passed else 'Compiled prerequisite failed; exact source closed',reason='Compiler stage1 result: '+str(passed)+'. Failed gates: '+str([k for k,v in gates.items() if not v])+'. No application kernel, numerical or speed result. Separate full-entry bypass proof remains mandatory.')
    item['evidence'].append({'label':'Compiled entries and actual resource stage1','url':'evidence/'+H.name+'/report.json'})
    status.update(updated_at=h.now(),stage=item['stage'],activity='E101 compiler stage1 is published. No application kernels or new gain; E080 with 16 workers remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'changed':changes,'resources':[{'entry':x['kernel'],'variant':x['variant'],'registers':x['registers'],'local':x['local_bytes_per_thread'],'occupancy':x['occupancy_by_threads']} for x in rows.values()],'division_site_counts':{a:{n:{v:len(x['native_division_sites']) for v,x in vv.items()} for n,vv in ns.items()} for a,ns in quotients.items()}}),flush=True)
