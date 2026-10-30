import json,sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
cup=H/'vendor/cuda_cupti/cuda_cupti-windows-x86_64-12.9.79-archive';rt=H/'vendor/cuda_cudart/cuda_cudart-windows-x86_64-12.9.79-archive';B=H/'build'
deps=old.read(ROOT/'binaries/E051-postflop_autoresearch.manifest.json')['dependency_artifact_sha256'];cudarc=next(p for p in deps if Path(p).name.startswith('libcudarc-') and p.endswith('.rlib'))
vc=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Auxiliary\Build\vcvars64.bat');cl=Path(r'C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC\14.41.34120\bin\Hostx64\x64\cl.exe')
P={'id':'D085-build','at':old.now(),'status':'FROZEN_BEFORE_BUILD_OR_NATIVE','build_dir':str(B),'vcvars':str(vc),'cl_exe':str(cl),'collector_command':['cl','/nologo','/LD','/O2','/MD','/EHsc','/std:c++17','/W4','/I'+str(cup/'include'),'/I'+str(rt/'include'),str(H/'collector.cpp'),'/Fe:'+str(B/'D085Collector.dll'),'/link','/LIBPATH:'+str(cup/'lib'),'cupti.lib','/IMPLIB:'+str(B/'D085Collector.lib')],'ability_command':['rustc','--edition=2021',str(H/'ability.rs'),'--crate-name','d085_ability','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1','--extern','cudarc='+cudarc,'-L','dependency='+str(Path(cudarc).parent),'-L','native='+str(B),'-o',str(B/'ability.exe')],'private_dll_dirs':[str(B),str(cup/'lib')],'diagnostic_only':True,'review':{'no_exit_hooks_or_injection':True,'explicit_start_stop_before_cuda_owner_drops':True,'no_performance_counter_or_pc_sampling_api':True,'no_privilege_driver_or_global_environment_change':True,'trace_schema':'16byte magic plus176byte little-endian records','buffer_budget':'2MiBperbuffer,max64outstanding; excess is a collector failure','no_native_solve_or_speed_claim':True,'windows_cleanup_reference':str(cup/'samples/cupti_trace_injection/cupti_trace_injection.cpp')},'input_sha256':{str(p):old.sha(p) for p in [H/'collector.cpp',H/'ability.rs',H/'bootstrap.json',vc,cl,*list((cup/'include').rglob('*.h')),*list((rt/'include').rglob('*.h')),*list((cup/'lib').glob('*'))] if p.is_file()}|deps}
old.save(H/'build-plan.json',P)
for src in [H/'collector.cpp',H/'ability.rs',H/'build-plan.json',H/'bootstrap.json']:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==src.read_bytes()
print(old.sha(H/'build-plan.json'),flush=True)
