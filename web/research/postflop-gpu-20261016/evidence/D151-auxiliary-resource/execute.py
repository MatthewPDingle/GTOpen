import sys, json, re, shutil
from pathlib import Path
H=Path(__file__).resolve().parent
ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2
P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for p,digest in P['input_sha256'].items():h.pin(p,digest)
verify()
O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status())
    assert shutil.disk_usage(ROOT).free >= P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version,memory.total','--format=csv,noheader'])
    assert gpu['returncode']==0 and P['GPU_uuid'] in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'kernel_launches':0})
    for label,cmd in zip(['rustc-offline','rustc-load'],P['rustc_commands']):
        h.child(cmd,O,label,600);verify()
    h.child([str(H/'offline-compile.exe'),str(O)],O,'offline-compile',600);verify()
    compiled=[json.loads(x.split('D151_COMPILE ',1)[1]) for x in (O/'offline-compile.stdout.log').read_text(encoding='utf-8').splitlines() if x.startswith('D151_COMPILE ')]
    assert [x['arch'] for x in compiled]==['compute_120','compute_75']
    assert all(x['kernel_launches']==0 and not x['GPU_context_created'] for x in compiled)
    artifacts={a:h.sha(O/f'packet-{a}.ptx') for a in ['compute_120','compute_75']}
    h.save(O/'prebuilt-artifacts.json',{'at':h.now(),'source_sha256':h.sha(H/'packet.cu'),'PTX_sha256':artifacts,'binary_sha256':{n:h.sha(H/(n+'.exe')) for n in ['offline-compile','load-resource']},'offline_compile_process_terminal_before_fresh_driver_process':True})
    h.child([str(H/'load-resource.exe'),str(O/'packet-compute_120.ptx')],O,'load-resource',600);verify()
    for a,digest in artifacts.items():h.pin(O/f'packet-{a}.ptx',digest)
    lines=(O/'load-resource.stdout.log').read_text(encoding='utf-8').splitlines()
    rows=[json.loads(x.split('D151_RESOURCE ',1)[1]) for x in lines if x.startswith('D151_RESOURCE ')]
    complete=[json.loads(x.split('D151_LOAD_COMPLETE ',1)[1]) for x in lines if x.startswith('D151_LOAD_COMPLETE ')]
    assert len(rows)==2 and len(complete)==1 and complete[0]['module_dropped'] and complete[0]['context_error_check_pass']
    gates={}
    for a in artifacts:
        text=(O/f'packet-{a}.ptx').read_text(encoding='utf-8')
        entries=re.findall(r'\.visible \.entry\s+(\w+)\s*\((.*?)\)\s*',text,re.S)
        gates[a+':two_expected_entries']=sorted(n for n,_ in entries)==sorted(P['expected_entries'])
        gates[a+':64bit_address']=bool(re.search(r'\.address_size\s+64',text))
        gates[a+':three_parameter_ABI']=all(len(re.findall(r'\.param\s+\.u64',params))==2 and len(re.findall(r'\.param\s+\.u32',params))==1 and params.count('.param ')==3 for _,params in entries)
    for row in rows:
        name=row['kernel'];assert name in P['expected_entries']
        gates[name+':shared_exact512']=row['static_shared_bytes']==512
        gates[name+':local_and_dynamic_zero']=row['local_bytes_per_thread']==row['dynamic_shared_bytes']==0
        gates[name+':fixed128_legal']=min(row['max_threads'],row['device_thread_limit'])>=128 and row['static_shared_bytes']<=row['device_shared_limit']
        gates[name+':occupancy_positive']=row['occupancy_128_threads']>0
        gates[name+':default_limits_unchanged']=row['context_stack_before']==row['context_stack_after'] and row['context_heap_before']==row['context_heap_after']
        gates[name+':no_launch_or_NVRTC_in_load']=row['kernel_launches']==row['NVRTC_compilations_in_load_process']==0
    passed=all(gates.values())
    report={'id':'D151','at':h.now(),'status':'pass_scoped_auxiliary_compile_load_resources' if passed else 'rejected_auxiliary_prerequisite','protocol_sha256':sys.argv[1],'gates':gates,'raw_resource_rows':rows,'offline_compile_rows':compiled,'PTX_sha256':artifacts,'source_sha256':h.sha(H/'packet.cu'),'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'kernel_launches':0,'solver_executions':0,'performance_measurements':0,'source_activated':False,'candidate_accepted':False,'scope':'Two auxiliary PTX targets compiled and actual compute120 module loaded/dropped in a separate process with bounded driver resource/default-limit checks. No numerical data executed, no resource equivalence to an integrated solver and no speed, actual memory/capacity or compatibility guarantee. Exact CPU-oracle packet controls required before any integration.'}
    h.save(H/'report.json',report)
    h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'report.json'),'all_owned_children_terminal':True,'kernel_launches':0})
    verify()
print(json.dumps({'status':report['status'],'failed_gates':[k for k,v in gates.items() if not v],'resources':rows}),flush=True)
