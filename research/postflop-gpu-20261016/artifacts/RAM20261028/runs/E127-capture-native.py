"""Capture the compiled module's native code once; leave dataflow proof pending."""
import json,os,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-native';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
verify();O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    gpu=h.ar.read_command(['nvidia-smi','--query-gpu=name,uuid,driver_version','--format=csv,noheader'])
    assert gpu['stdout']==h.read(ROOT/'runs/E127-resource/execution/before.json')['GPU']['stdout']and P['GPU_uuid']in gpu['stdout']
    h.save(O/'before.json',{'at':h.now(),'GPU':gpu,'application_kernels':0})
    os.environ['PATH']=P['private_dll_dir']+os.pathsep+os.environ.get('PATH','')
    h.child([P['capture_binary'],P['candidate_PTX'],str(O)],O,'capture',180);verify()
    markers=[json.loads(line.split(' ',1)[1])for line in(O/'capture.stdout.log').read_text(encoding='utf-8').splitlines()if line.startswith('D098_COMPLETE ')]
    assert markers==[{'callback_errors':0,'modules':1,'kernel_launches':0,'solver_executions':0,'performance_measured':False}]
    cubin=O/'module-0.cubin';assert cubin.read_bytes()[:6]==b'\x7fELF\x02\x01'
    h.child([P['nvdisasm'],'--print-code','--print-instruction-encoding',str(cubin)],O,'disassemble',180);verify()
    sass=(O/'disassemble.stdout.log').read_text(encoding='utf-8');marker='//--------------------- .text.up_action_star '
    start=sass.index(marker);end=sass.find('//--------------------- .text.',start+len(marker));section=sass[start:end if end>=0 else None]
    target=O/'up_action_star.sass.txt';target.write_bytes(section.encode())
h.save(H/'capture-report.json',{'id':'E127-native-capture','at':h.now(),'status':'native_code_captured_dataflow_proof_pending',
    'candidate_PTX_sha256':h.sha(P['candidate_PTX']),'CUBIN_sha256':h.sha(O/'module-0.cubin'),'SASS_section_sha256':h.sha(target),'SASS_section_path':str(target),
    'callback_errors':0,'owned_modules_captured':1,'original9_function_resource_queries':True,'all_owned_children_terminal':True,
    'application_kernel_launches':0,'solver_or_speed_samples':0,'source_activated':False,
    'scope':'OneexistingownedCUPTIresourcecallbackcaptureandnvdisasm only. No counters/injection/globalsettings/arrays/appkernels/solver/timing. Nativebarrier/loop/uniformreturn/helperbindingproofstillpending; capturealoneisnotmechanismornumericalqualification.'})
print(json.dumps({'captured':True,'section_sha256':h.sha(target),'mechanism_proof':'pending'}),flush=True)
