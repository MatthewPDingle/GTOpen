import sys,json,shutil,urllib.request,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D161-compiler-resource';P=h.read(H/'protocol.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
O=H/'execution';assert h.read(O/'compile-baseline.exit.json')['returncode']==0 and h.read(O/'compile-candidate.exit.json')['returncode']==1
assert (O/'baseline.ptx').read_bytes()==(H/'reference-baseline.ptx').read_bytes() and not (O/'candidate.ptx').exists()
assert not(O/'rustc-resource.invocation.json').exists() and not(O/'resource.invocation.json').exists()
log=(O/'candidate.compiler.log').read_bytes();assert log==b'nvrtc: error: failed to open nvrtc-builtins64_130.dll.\n  Make sure that nvrtc-builtins64_130.dll is installed correctly.\x00'
D=ROOT/'comparisons/D161-compiler-resource';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D161','at':h.now(),'status':'invalid_private_builtin_dependency_setup','original_protocol_sha256':h.sha(H/'protocol.json'),'baseline_exit':0,'baseline_PTX_byte_exact':True,'candidate_exit':1,'candidate_log':log.rstrip(b'\0').decode(),'candidate_PTX_generated':False,'Rust_resource_compilers_or_driver_module_processes':0,'application_kernel_or_solver_executions':0,'performance_samples':0,'source_or_math_failure_observed':False,'all_owned_children_terminal':True,'scope':'Preserved failed API adapter setup. Source-bound trace reached compiler log retrieval and clean destroy,reporting unavailable builtins before any PTX. No baseline repeat,no successful candidate program/module/numerical/timing observation exists. Original compilation-failure gate does not pass and original status is never relabeled. Distinct mechanical dependency binding repair requires frozen explicit DLL identity and same original source/options/ABI/resource/mechanism gates.'})
R=ROOT/'runs/D162-private-dependency-repair';R.mkdir(exist_ok=False)
for source in ['kernels.cu','reference-baseline.ptx','retained-original-compute75.ptx','resource.rs','source-review.json']:shutil.copyfile(H/source,R/source)
for source in ['baseline.ptx','baseline.compile.json']:shutil.copyfile(O/source,R/('retained-'+source))
src=(H/'compile.py').read_text(encoding='utf-8')
needle='directory=os.add_dll_directory(str(library.parent));dll=c.CDLL(str(library))'
replacement='''directory=os.add_dll_directory(str(library.parent))
builtin=library.parent/'nvrtc-builtins64_130.dll';assert builtin.is_file()
# Bind the exact private dependency first; no PATH/global search-policy change.
builtin_dll=c.CDLL(str(builtin))
kernel32=c.WinDLL(r'C:\\Windows\\System32\\kernel32.dll',use_last_error=True)
kernel32.GetModuleFileNameW.argtypes=[c.c_void_p,c.c_wchar_p,c.c_uint32];kernel32.GetModuleFileNameW.restype=c.c_uint32
loaded=c.create_unicode_buffer(32768);length=kernel32.GetModuleFileNameW(builtin_dll._handle,loaded,len(loaded));assert 0<length<len(loaded)
assert Path(loaded.value).resolve()==builtin.resolve()
dll=c.CDLL(str(library))'''
assert src.count(needle)==1;src=src.replace(needle,replacement,1)
needle="'DLL_path':str(library),";replacement="'builtin_absolute_path_verified':str(builtin),'builtin_sha256':hashlib.sha256(builtin.read_bytes()).hexdigest(),'DLL_path':str(library),"
assert src.count(needle)==1;src=src.replace(needle,replacement,1)
(R/'compile.py').write_bytes(src.encode());ast.parse(src)
execute=(H/'execute.py').read_text(encoding='utf-8');execute=execute.replace("D=ROOT/'comparisons/D161-compiler-resource'","D=ROOT/'comparisons/D162-private-dependency-repair'")
execute=execute.replace("compile_records={}\n    for arm in ['baseline','candidate']:","shutil.copyfile(H/'retained-baseline.ptx',O/'baseline.ptx');shutil.copyfile(H/'retained-baseline.compile.json',O/'baseline.compile.json')\n    compile_records={'baseline':h.read(O/'baseline.compile.json')}\n    for arm in ['candidate']:")
execute=execute.replace("'id':'D161','at':h.now(),'status':","'id':'D162','at':h.now(),'original_D161_invalid_preserved':True,'baseline_compiler_output_reused_without_repeat':True,'candidate_builtin_absolute_binding_verified':True,'status':")
execute=execute.replace("publish(H,['protocol.json','source-review.json','compile.py','resource.rs'])","publish(H,['protocol.json','repair-review.json','compile.py','resource.rs'])")
execute=execute.replace("x['id']=='D161'","x['id']=='D162'").replace("active_experiment='D161'","active_experiment='D162'")
execute=execute.replace("evidence/D161-compiler-resource/protocol.json","evidence/D162-private-dependency-repair/protocol.json").replace("evidence/D161-compiler-resource/report.json","evidence/D162-private-dependency-repair/report.json")
execute=execute.replace("Exactly one compile per target compiler through header-bound C API. Baseline PTX must equal retained E080 before13compile.","Reused exact original12.9control;one13compile with explicit absolute builtins binding. Original failed D161 remains invalid.")
execute=execute.replace("Literal baseline adapter matches retained accepted PTX first.","Literal baseline adapter matches retained accepted PTX from original successful control;no baseline compiler repeated. Original D161 failed private DLL setup is retained and not regraded.")
(R/'execute.py').write_bytes(execute.encode());ast.parse(execute)
h.save(R/'repair-review.json',{'at':h.now(),'status':'mechanical_dependency_binding_before_first_candidate_PTX_or_module','original_failed_report_sha256':h.sha(D/'report.json'),'error':'NVRTC internal builtins lookup did not resolve the private directory registered by os.add_dll_directory. Exact internal load flags are not traced;search-rule explanation is an inference from observed error and primary Windows documentation.','primary_sources':['https://learn.microsoft.com/en-us/windows/win32/api/libloaderapi/nf-libloaderapi-adddlldirectory','https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order'],'documentation':'AddDllDirectory applies only to LoadLibraryEx USER_DIRS unless process default flags request it. Loaded-module lookup can find an already loaded matching base name. Absolute primary DLL alone does not guarantee dependency resolution.','repair':'Load exact pinned builtins DLL by absolute path before exact primary13DLL;verify actual module path with GetModuleFileNameW. This child-only explicit binding avoids global/PATH/search-policy changes. No renamed DLL,compiler/source/options/target/ABI/resource/mechanism gate changes.','preservation':'Original D161 remains invalid with native exit1 and no PTX. Original12.9control exact PTX/compile record reused,not rerun. One repaired candidate compile then original never-executed Rust/resource steps. Extra native failed setup/process disclosed. No numerical/performance failure rescored or input corpus repaired.','failure':'If explicit dependency still fails,or later actual source/ABI/resources/codegen fails,close exact form without further load/flag/version/shape rescue. No application kernel before all original prerequisites pass.'})
command=[x.replace(str(H),str(R)) for x in P['rustc_command']]
inputs={**P['input_sha256'],**{str(p):h.sha(p) for p in [Path(__file__),H/'protocol.json',H/'compile.py',H/'execute.py',D/'report.json',O/'compile-candidate.exit.json',O/'compile-candidate.stderr.log',O/'candidate.compiler.log',O/'baseline.ptx',O/'baseline.compile.json']+[x for x in R.iterdir() if x.is_file()]}}
h.save(R/'protocol.json',{**P,'id':'D162','at':h.now(),'status':'FROZEN_PRE_EXPLICIT_BINDING_AND_FIRST_CANDIDATE_PTX','rustc_command':command,'input_sha256':inputs,'original_D161_status':'invalid_dependency_setup_preserved','original_control_reused':True,'scope':'Mechanical explicit absolute builtins dependency binding only;retain original exact source/options/target/ABI/default-resource/instruction-mechanism criteria. Original12.9control reused;one repaired13compile,no actual candidate numerical/timing observation repeated. Further dependency/source/compile failure closes form without rescue.'})
dest=h.ar.DASHBOARD/'evidence/D161-compiler-resource/report.json';dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();shutil.copyfile(D/'report.json',dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/D161-compiler-resource/report.json',timeout=20) as response:assert response.read()==dest.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D161')
    item.update(status='invalid',correctness='not_executed',stage='Private builtins dependency lookup failed before PTX',reason='Original12.9control PTX exact.13compile log reports unavailable private builtins DLL;exit1,clean program destroy,no PTX,module or solver. Original failure retained. Separate D162explicit absolute dependency binding repair keeps all code/gates fixed and reuses original baseline.')
    item.setdefault('evidence',[]).append({'label':'Preserved private dependency setup failure','url':'evidence/D161-compiler-resource/report.json'})
    status['experiments'].append({'id':'D162','title':'Explicit private compiler dependency binding','kind':'diagnostic','status':'staged','accepted':False,'correctness':'not_executed','measurement_epoch':'RAM20261028','stage':'Frozen absolute builtins load before same13compiler call','reason':'Mechanical DLL adapter repair only;retains original code/options/ABI/resources/mechanism gates. Original D161invalid,no baseline repeat,no candidate kernel/numerical/performance rescue.','evidence':[]})
    status.update(updated_at=h.now(),active_experiment='D162',stage='Private compiler dependency binding repair',activity='12.9control exact;13internal builtins lookup failed before PTX. Preserved failure;explicit private DLL binding staged with original unchanged compiler/resource gates. No new gain.')
    h.ar.atomic_json(h.ar.STATUS,status)
h.custody();print(h.sha(R/'protocol.json'),flush=True)
