import ast,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();assert not(ROOT/'epoch-sequence.lock').exists()
parent=ROOT/'runs/D197-parent-chance-canonical';p=parent/'protocol.json';P=h.read(p)
for path,digest in P['input_sha256'].items():h.pin(path,digest)
for arm in ['baseline','candidate']:
 r=h.read(parent/'execution'/(arm+'.exit.json'));assert r['returncode']==0 and r['error'] is r['cleanup'] is None
assert h.read(parent/'execution/audit.exit.json')['returncode']==1
stderr=(parent/'execution/audit.stderr.log').read_text();assert 'every EV/iteration/fielddtype/count/geometry/graph/wrappermetadatabit exact' in stderr
H=ROOT/'runs/D198-canonical-terminal-diagnostic';H.mkdir(exist_ok=False)
code=(parent/'audit.py').read_text();code=code.replace("H=Path(__file__).resolve().parent;ROOT=H.parent.parent;", "ROOT=Path(__file__).resolve().parents[2];H=ROOT/'runs/D197-parent-chance-canonical';",1)
code=code.replace('checks=pair_bytes=represented_words=0;hashes={}','checks=pair_bytes=represented_words=0;hashes={};wrapper_differences=[]',1)
old="stage=bs['stage'];req(bs==cs,'every EV/iteration/fielddtype/count/geometry/graph/wrappermetadatabit exact')"
new="""stage=bs['stage']
        # Diagnostic-only completion: original strict wrapper equality failure remains failed.
        req(bs['info']['wrapper_bytes']!=cs['info']['wrapper_bytes'],'original wrapper gate remains failed')
        wrapper_differences.append({'fixture':name,'stage':stage,'baseline_bytes':bs['info']['wrapper_bytes'],'candidate_bytes':cs['info']['wrapper_bytes'],'delta_bytes':cs['info']['wrapper_bytes']-bs['info']['wrapper_bytes']})
        left=__import__('copy').deepcopy(bs);right=__import__('copy').deepcopy(cs)
        del left['info']['wrapper_bytes'];del right['info']['wrapper_bytes']
        req(left==right,'all remaining original metadata exact; wrapper failure separately retained')"""
assert code.count(old)==1;code=code.replace(old,new,1)
code=code.replace("D=ROOT/'comparisons/D197-parent-chance-canonical'","D=ROOT/'comparisons/D198-canonical-terminal-diagnostic'",1)
code=code.replace("{'id':'D197','at':h.now(),'status':'pass_scoped_full_canonical_all_device_and_CPU_raw_lifecycle'", "{'id':'D198','at':h.now(),'status':'raw_diagnostic_complete_original_wrapper_gate_failed','original_D197_wrapper_gate_pass':False,'E102_qualified':False,'wrapper_differences':wrapper_differences",1)
code=code.replace("'scope':'Original three full same-quality", "'scope':'DIAGNOSTIC ONLY: D197 strict host wrapper equality failed and remains failed. This reader completes all retained raw bytes without native repeats, reporting the wrapper cost separately; it cannot qualify E102 or open timing/adoption gates. Original three full same-quality",1)
code=code.replace("'status':'pass_full_raw_canonical'","'status':'raw_diagnostic_complete_original_wrapper_gate_failed'",1)
ast.parse(code);(H/'audit.py').write_text(code,encoding='utf-8',newline='\n')
files=[Path(__file__),H/'audit.py',p,parent/'audit.py',parent/'execute.py',parent/'execution/audit.exit.json',parent/'execution/audit.stderr.log',ROOT/'epoch/common.py']
for arm in ['baseline','candidate']:
 for name in [arm+'.stdout.log',arm+'.exit.json',arm+'.resource.json']:files.append(parent/'execution'/name)
h.save(H/'protocol.json',{'id':'D198','at':h.now(),'status':'FROZEN_PRE_RETAINED_RAW_READER','original_D197_protocol_sha256':h.sha(p),'input_sha256':{str(x):h.sha(x) for x in files},'retained_raw_extents':{str(x):x.stat().st_size for d in parent.glob('*-output') for x in d.iterdir() if x.is_file()},'native_or_compiler_processes':0,'command':[sys.executable,str(H/'audit.py')],'original_wrapper_gate_failure_retained':True,'scope':'One read-only full retained raw reader. No rerun, source/field exception qualification or rescue. Complete scientific records/all CPU/GPU/raw pair bytes and all remaining metadata exact or fail. Original per-stage wrapper byte inequality explicitly remains failed and recorded, never a pass or speed/adoption admission. No new E102 integrated builds or timing permitted.'})
print(h.sha(H/'protocol.json'),flush=True)
