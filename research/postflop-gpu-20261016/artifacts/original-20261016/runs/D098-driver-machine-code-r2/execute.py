"""Compile/capture/disassemble one source-matched module; never launch a kernel."""
import json,os,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
 old.pin(H/'protocol.json',sys.argv[1])
 for p,h in P['input_sha256'].items():old.pin(p,h)
 old.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['reserve_bytes']
 gpu=old.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'],timeout=10);assert gpu['returncode']==0 and P['gpu_uuid'] in gpu['stdout']
 B.mkdir();E.mkdir();old.save(E/'before.json',{'at':old.now(),'gpu':gpu,'protocol_sha256':sys.argv[1],'executor_sha256':old.sha(__file__)})
 env=old.env();env['PATH']=P['private_dll_dir']+os.pathsep+env['PATH']
 assert not any(k in env for k in ['CUDA_INJECTION64_PATH','CUDA_INJECTION32_PATH','CUPTI_INJECTION64_PATH','NVBIT_TOOL'])
 old.child(P['command'],B,'cl',env,180);verify()
 binary=old.sha(B/'probe.exe');old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary,'compiler_terminal':True,'native_executions':0})
 old.child([str(B/'probe.exe'),P['ptx'],str(E)],E,'capture',env,120);verify();old.pin(B/'probe.exe',binary)
 raw=(E/'capture.stdout.log').read_text(encoding='utf-8');rows={}
 for line in raw.splitlines():
  prefix,payload=line.split(' ',1);assert prefix in ['D098_DEVICE','D098_KERNEL','D098_MODULE','D098_COMPLETE']
  rows.setdefault(prefix,[]).append(json.loads(payload))
 assert len(rows['D098_DEVICE'])==len(rows['D098_COMPLETE'])==1
 assert set(r['name'] for r in rows['D098_KERNEL'])==set(P['expected_entries']) and len(rows['D098_KERNEL'])==len(P['expected_entries'])
 end=rows['D098_COMPLETE'][0];assert end['kernel_launches']==end['solver_executions']==end['callback_errors']==0 and end['performance_measured'] is False
 modules=list(E.glob('module-*.cubin'));assert len(modules)==end['modules']==len(rows['D098_MODULE'])
 old.child([P['nvdisasm'],'--version'],E,'nvdisasm-version',env,30)
 for p in sorted(modules):
  assert p.read_bytes()[:6]==b'\x7fELF\x02\x01'
  old.child([P['nvdisasm'],'--print-code','--print-instruction-encoding',str(p)],E,p.stem+'-sass',env,60)
  old.child([P['nvdisasm'],'--emit-json',str(p)],E,p.stem+'-json',env,60)
  verify()
 report={'id':'D098','at':old.now(),'status':'captured_source_matched_driver_code','protocol_sha256':sys.argv[1],'executor_sha256':old.sha(__file__),'input_ptx_sha256':old.sha(P['ptx']),'probe_sha256':binary,'markers':rows,'module_sha256':{p.name:old.sha(p) for p in modules},'disassembly_sha256':{p.name:old.sha(p) for p in E.glob('module-*.log')},'kernel_launches':0,'solver_executions':0,'source_activated':False,'performance_measured':False,'accepted162_main_live_ptx_unchanged':True,'limits':P['scope']}
 old.save(H/'capture-report.json',report);old.save(E/'complete.json',{'at':old.now(),'capture_report_sha256':old.sha(H/'capture-report.json'),'all_owned_children_terminal':True,'no_solve_or_kernel_run':True});verify()
print(json.dumps({'status':report['status'],'modules':len(modules),'kernel_attributes':rows['D098_KERNEL'],'all_owned_children_terminal':True}),flush=True)
