import json,os,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D221-showdown-native-scheduling';A=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs');RES=ROOT/'runs/E107-resource'
assert len(sys.argv)>=2
if sys.argv[1]=='prepare':
 h.custody();h.ar.refuse_active(h.ar.live_status());assert not H.exists();q=h.read(RES/'report.json');assert all(q['gates'].values())and q['status']=='pass_compiled_prerequisites_numerical_pending'
 H.mkdir();old=A/'D098-driver-machine-code-r2';exe=old/'build/probe.exe';h.pin(exe,h.read(old/'capture-report.json')['probe_sha256']);shutil.copyfile(exe,H/'capture.exe')
 dis=A/'D098-driver-machine-code/vendor/cuda_nvdisasm-windows-x86_64-12.9.88-archive/bin/nvdisasm.exe';shutil.copyfile(dis,H/'nvdisasm.exe')
 inputs=[Path(__file__),old/'probe.cpp',old/'protocol.json',old/'capture-report.json',exe,dis,H/'capture.exe',H/'nvdisasm.exe',RES/'report.json',ROOT/'epoch/common.py']
 paths={'baseline':RES/'baseline-compute_120.ptx','candidate':RES/'execution/candidate-compute_120.ptx'}
 for arm,p in paths.items():h.pin(p,q['PTX_sha256'][arm+'-compute_120']);inputs.append(p)
 private=ROOT/'runs/D212-current-RAM-activity/private';inputs+=list(private.glob('*.dll'))
 h.save(H/'protocol.json',{'id':'D221','at':h.now(),'status':'FROZEN_PRE_MODULE_LOAD','PTX':{a:str(p)for a,p in paths.items()},'capture_binary':str(H/'capture.exe'),'nvdisasm':str(H/'nvdisasm.exe'),'private_dll_dir':str(private),'input_sha256':{str(p):h.sha(p)for p in inputs},'GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','required_free_bytes':8*1024**3,'sequence':['baseline-capture','baseline-disassemble','candidate-capture','candidate-disassemble'],'emission_gate':'All three candidate payout global-load instructions, traced from unchanged parameter byte offsets0x390/0x398/0x3a0, must precede the first BAR.SYNC; baseline must load after its scan barriers. A missing native mechanism closes this frozen source form. Conservative static witness only, no dynamic latency or speed claim.','scope':'Reuse checksum-bound original D098 generic module-capture executable and code unchanged; same cuModuleLoadData/default JIT as cudarc. Copy nvdisasm12.9.88 to X. Two owned primary-context module loads and two disassembly readers, no new compiler, application kernels, hardware counters, activity profiling, injection, live attach, solve or speed samples. Query helper occupancy uses zero dynamic shared and is not scored; actual worst-shape resources are E107-resource.'})
 print(h.sha(H/'protocol.json'),flush=True);sys.exit(0)
assert sys.argv[1]=='execute'and len(sys.argv)==3;P=h.read(H/'protocol.json');O=H/'execution'
def verify():
 h.pin(H/'protocol.json',sys.argv[2]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
verify();assert not O.exists();O.mkdir()
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader']);assert gpu['returncode']==0 and P['GPU_uuid']in gpu['stdout'];h.save(O/'before.json',{'at':h.now(),'gpu':gpu,'application_kernels':0})
 os.environ['PATH']=P['private_dll_dir']+os.pathsep+os.environ.get('PATH','');captures={}
 for arm in ['baseline','candidate']:
  E=O/arm;E.mkdir();h.child([P['capture_binary'],P['PTX'][arm],str(E)],E,'capture',180);verify();raw=(E/'capture.stdout.log').read_text(encoding='utf-8');rows={}
  for line in raw.splitlines():
   prefix,payload=line.split(' ',1);assert prefix in ['D098_DEVICE','D098_KERNEL','D098_MODULE','D098_COMPLETE'];rows.setdefault(prefix,[]).append(json.loads(payload))
  assert len(rows['D098_COMPLETE'])==1 and rows['D098_COMPLETE'][0]=={'callback_errors':0,'modules':1,'kernel_launches':0,'solver_executions':0,'performance_measured':False}
  assert len(rows['D098_MODULE'])==1 and rows['D098_MODULE'][0]['same_owned_context']and rows['D098_MODULE'][0]['elf_magic'];assert len(rows['D098_KERNEL'])==9
  image=E/'module-0.cubin';assert image.read_bytes()[:6]==b'\x7fELF\x02\x01';h.child([P['nvdisasm'],'--print-code','--print-instruction-encoding',str(image)],E,'disassemble',180);verify()
  text=(E/'disassemble.stdout.log').read_text(encoding='utf-8');a=text.index('//--------------------- .text.up_show');b=text.find('//--------------------- .text.',a+len('//--------------------- .text.up_show'));target=text[a:b if b>=0 else None];assert target.count('.text.up_show:')==1;(E/'up_show.sass.txt').write_bytes(target.encode('utf-8'))
  captures[arm]={'CUBIN_sha256':h.sha(image),'SASS_sha256':h.sha(E/'disassemble.stdout.log'),'up_show_sha256':h.sha(E/'up_show.sass.txt'),'markers':rows,'all_children_terminal':True}
h.save(H/'capture-report.json',{'id':'D221','at':h.now(),'status':'captured_native_showdown_code_semantic_review_pending','protocol_sha256':sys.argv[2],'captures':captures,'all_owned_compilers_native_readers_terminal':True,'application_kernels':0,'solver_executions':0,'speed_samples':0,'new_compilers':0,'candidate_accepted':False,'limits':P['scope']});h.save(O/'complete.json',{'at':h.now(),'report_sha256':h.sha(H/'capture-report.json'),'all_owned_children_terminal':True});verify()
print(json.dumps({'status':'captured_native_showdown_code_semantic_review_pending','CUBINs':{a:v['CUBIN_sha256']for a,v in captures.items()},'kernel_launches':0}),flush=True)
