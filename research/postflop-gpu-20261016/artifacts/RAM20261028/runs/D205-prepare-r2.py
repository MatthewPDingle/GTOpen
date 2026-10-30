import ast,json,sys,urllib.request,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();H=ROOT/'runs/D205-cooperative-grid-controls';P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
assert h.read(H/'execution/rustc.exit.json')['returncode']==1 and not(H/'output').exists() and not(H/'probe.exe').exists()
stderr=(H/'execution/rustc.stderr.log').read_text();assert 'CU_LAUNCH_ATTRIBUTE_COOPERATIVE' in stderr and 'E0599' in stderr
source=(H/'probe.rs').read_text();old='sys::CUkernelNodeAttrID::CU_KERNEL_NODE_ATTRIBUTE_COOPERATIVE';new='sys::CUkernelNodeAttrID::CU_LAUNCH_ATTRIBUTE_COOPERATIVE';assert source.count(old)==1
source=source.replace(old,new,1)+'\nconst _: () = assert!(sys::CUkernelNodeAttrID::CU_LAUNCH_ATTRIBUTE_COOPERATIVE as u32 == 2);\n';(H/'probe-r2.rs').write_text(source,encoding='utf-8',newline='\n')
audit=(H/'audit.py').read_text().replace("'protocol.json'","'repair-protocol.json'");ast.parse(audit);(H/'audit-r2.py').write_text(audit,encoding='utf-8',newline='\n')
execute=(H/'execute.py').read_text().replace("'protocol.json'","'repair-protocol.json'").replace("O=H/'execution'","O=H/'execution-r2'").replace("H/'probe.exe'","H/'probe-r2.exe'").replace("H/'audit.py'","H/'audit-r2.py'")
ast.parse(execute);(H/'execute-r2.py').write_text(execute,encoding='utf-8',newline='\n')
cmd=[x.replace(str(H/'probe.rs'),str(H/'probe-r2.rs')).replace(str(H/'probe.exe'),str(H/'probe-r2.exe')) for x in P['rustc_command']]
files=[Path(__file__),H/'protocol.json',H/'execution/rustc.exit.json',H/'execution/rustc.stderr.log',H/'probe-r2.rs',H/'audit-r2.py',H/'execute-r2.py']
h.save(H/'repair-review.json',{'id':'D205-R2','at':h.now(),'status':'mechanical_Rust_API_enum_alias_before_any_native_GPU_process','original_failure':'Frozen Rust shim referenced legacy CUkernelNodeAttrID enum variant CU_KERNEL_NODE_ATTRIBUTE_COOPERATIVE. This exact retained cudarc build aliases the parameter type to CUlaunchAttributeID and exports CU_LAUNCH_ATTRIBUTE_COOPERATIVE instead. Both identify attribute2; compile-time numericassert==2 added.','original_compiler_returncode':1,'original_native_GPU_processes':0,'original_protocol_sha256':h.sha(H/'protocol.json'),'change':'One constant spelling in actual graph attribute getter, pluscompile-time attribute2 check. No shader/PTX/barrier/graphs/data/case/grid/threads/phases/CPUoracle/flags/gates/speedchange. Alloriginalfiles/failedcompilerreceiptretained; onecorrectedRustcompilerthenalloriginalunexecuted256nativecasesonce. No completednativecase repeated.'})
files.append(H/'repair-review.json')
h.save(H/'repair-protocol.json',{**P,'id':'D205-R2','at':h.now(),'status':'FROZEN_PRE_CORRECTED_RUST_COMPILER_AND_ORIGINAL_UNEXECUTED_GPU_CASES','rustc_command':cmd,'input_sha256':{**P['input_sha256'],**{str(p):h.sha(p) for p in files}},'repair':'Sameattribute2 via actualretainedcudarcenumalias; original256case/768launch corpusandallgatesunchanged. NoNVRTC/newsourcevariant/native observationrepeat.'})
for name in ['repair-protocol.json','repair-review.json']:
 p=H/name;key=H.name+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='D205');item.update(stage='Mechanical enum-alias repair before first GPU process',reason='OriginalRustcompilefailedonlegacygraphattributeconstantname. Correctactualcudarc aliasstillsameattribute2,compile-timechecked. PTX/corpus/flags/gatesunchanged; noapplicationkernelobserved/repeated.');item.setdefault('evidence',[]).extend([{'label':n,'url':'evidence/'+H.name+'/'+n} for n in ['repair-review.json','repair-protocol.json']]);s.update(updated_at=h.now(),active_experiment='D205',stage=item['stage'],activity='Originalcompilerfailurepreserved; correctedAPIconstantbeforerunningalloriginal256casegridcontrols. No solver/speed/corpus/source rescue.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'repair-protocol.json'),flush=True)
