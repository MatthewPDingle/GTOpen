"""One prospective resource-only compile/load; no solver or application kernel."""
from pathlib import Path
import hashlib,json,re,shutil,sys
H=Path(__file__).resolve().parent;R=H.parent.parent;sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');O=H/'execution'
def verify():
    old.custody();old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
def entries(path):
    t=path.read_text();out={};i=0
    while True:
        i=t.find('.visible .entry ',i)
        if i<0:break
        n=t.index('(',i);name=t[i+len('.visible .entry '):n].strip();a=t.index('{',n);j=a+1;depth=1
        while depth:
            if t[j]=='{':depth+=1
            elif t[j]=='}':depth-=1
            j+=1
        assert name not in out;out[name]=t[i:j];i=j
    return out
def normalize(text):
    t=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',text);t=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',t);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',t)
assert normalize('$L__BB7_2: __local_depot7[64]')==normalize('$L__BB8_2: __local_depot8[64]');assert normalize('add.u32 %r1, %r2, 4;')!=normalize('add.u32 %r1, %r2, 8;')
verify();assert not O.exists()and not(H/'probe.exe').exists();O.mkdir()
with old.ar.exclusive_lock(R/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
    gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid']in gpu['stdout'];old.save(O/'before.json',{'at':old.now(),'GPU':gpu,'application_kernel_launches':0})
    old.child(P['rustc_command'],O,'rustc',old.env(),600);verify();old.save(O/'build-complete.json',{'at':old.now(),'compiler_terminal':True,'binary_sha256':old.sha(H/'probe.exe'),'native_executions':0})
    old.child([str(H/'probe.exe'),str(O)],O,'probe',old.env(),600);verify()
markers=[json.loads(x.split('E089_RESOURCE ',1)[1])for x in(O/'probe.stdout.log').read_text().splitlines()if'E089_RESOURCE 'in x];assert len(markers)==4 and markers[0]['stage']=='device'and markers[-1]['stage']=='complete';rows={x['variant']:x for x in markers[1:-1]};assert set(rows)=={'baseline','candidate'}
tables={(v,a):entries(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']};assert all(set(t)==set(P['expected_entries'])for t in tables.values());gates={};unchanged={}
for arch in['compute_120','compute_75']:
    b,c=tables['baseline',arch],tables['candidate',arch];unchanged[arch]={n:{'normalized_exact':normalize(b[n])==normalize(c[n]),'baseline_sha256':hashlib.sha256(b[n].encode()).hexdigest(),'candidate_sha256':hashlib.sha256(c[n].encode()).hexdigest()}for n in b if n!='up_show'};gates[arch+':other8entries_exact']=all(x['normalized_exact']for x in unchanged[arch].values());bh,ch=b['up_show'].split('{',1)[0],c['up_show'].split('{',1)[0];gates[arch+':global27parameter_ABI_exact']=bh==ch and bh.count('.param ')==27;gates[arch+':action_entry_changed']=b['up_show']!=c['up_show']
b,c=rows['baseline'],rows['candidate'];bo,co=dict(b['occupancy_by_threads']),dict(c['occupancy_by_threads']);gates.update(local_not_increased=c['local_bytes_per_thread']<=b['local_bytes_per_thread'],static_shared_exact=c['static_shared_bytes']==b['static_shared_bytes'],dynamic_shared_exact=c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],max_threads_not_reduced=c['max_threads']>=b['max_threads'],all_fixed_thread_controls_legal=min(b['max_threads'],c['max_threads'])>=256,positive_all_fixed_occupancies=all(x>0 for arm in[bo,co]for x in arm.values()),default_128_occupancy_not_reduced=co[128]>=bo[128],both_fit_default_limits=b['fits_default_limits']and c['fits_default_limits'],no_stack_limit_increase=c['context_stack_limit_after_load']<=b['context_stack_limit_after_load'])
for arch in ['compute_120','compute_75']:
    bt,ct=tables['baseline',arch]['up_show'],tables['candidate',arch]['up_show']
    gates[arch+':target_PTX_body_smaller']=len(ct)<len(bt)
    gates[arch+':CTA_barrier_sites_exact']=bt.count('bar.sync')==ct.count('bar.sync')
passed=all(gates.values());report={'id':'E089-resource','at':old.now(),'status':'pass_compiled_serial_card_loop_prerequisites'if passed else'rejected_compiled_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'baseline':b,'candidate':c,'other8entries':unchanged,'raw_markers':markers,'ptx_sha256':{v+'-'+a:old.sha(O/f'{v}-{a}.ptx')for v in['baseline','candidate']for a in['compute_120','compute_75']},'all_owned_children_terminal':True,'application_kernel_launches':0,'solver_executions':0,'performance_measurements':0,'candidate_accepted':False,'source_activated':False,'accepted_main_live_PTX_unchanged':True,'limits':'Compiler/load resource feasibility only. PTX changes and theoretical occupancy do not establish serial-card-loop numerical correctness, dynamic occupancy, GPU speed, actual whole CPU/memory/capacity costs or application behavior. Exact raw single/mixed-node and metadata controls plus complete performance qualification remain required.'};old.save(H/'report.json',report);old.save(O/'complete.json',{'at':old.now(),'report_sha256':old.sha(H/'report.json'),'all_owned_children_terminal':True,'application_kernel_launches':0});verify();print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items()if not v],'registers':[b['registers'],c['registers']],'local':[b['local_bytes_per_thread'],c['local_bytes_per_thread']],'occupancy128':[bo[128],co[128]],'max_threads':[b['max_threads'],c['max_threads']]}),flush=True)
