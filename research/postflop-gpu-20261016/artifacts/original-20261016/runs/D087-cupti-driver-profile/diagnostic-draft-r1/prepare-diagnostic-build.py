import difflib,sys,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();ability=old.read(H/'ability-report.json');assert ability['status']=='pass_activity_graph_feasibility'
base=old.REPO/'crates/solver/tests/postflop_autoresearch.rs';old.pin(base,'f13d79410a22f140c05cb9a822fe9685c2180e5baeda4b625d52ae03feebd327');source=base.read_text();original=source
defs='''
#[link(name="D087Collector")] extern "system" { fn D087StartTrace()->u32; fn D087PhaseTrace(marker:u32)->u32; fn D087FlushTrace()->u32; fn D087StopTrace()->u32; }
struct D087Guard;impl Drop for D087Guard {fn drop(&mut self){unsafe{D087StopTrace();}}}
'''
assert source.count('use std::time::Instant;')==1;source=source.replace('use std::time::Instant;','use std::time::Instant;\n'+defs)
source=source.replace('include_str!("../../../bench_spot.json")','include_str!(r"'+str(old.REPO/'bench_spot.json')+'")')
before='        let stage_start = Instant::now();\n        let mut gpu = GpuSolver::new(&host).expect("benchmark requires CUDA");'
after='        let stage_start = Instant::now();\n        let _d085_guard = D087Guard;\n        assert_eq!(unsafe{D087StartTrace()},1,"private CUPTI start");\n        let mut gpu = GpuSolver::new(&host).expect("benchmark requires CUDA");'
assert source.count(before)==1;source=source.replace(before,after)
before='        if profile {\n            let diagnostic = gpu.iterate_profiled().unwrap();';after='        gpu.synchronize().unwrap();\n        assert_eq!(unsafe{D087FlushTrace()},1,"private CUPTI flush");\n        assert_eq!(unsafe{D087StopTrace()},1,"private CUPTI stop while context alive");\n        if profile {\n            let diagnostic = gpu.iterate_profiled().unwrap();';assert source.count(before)==1;source=source.replace(before,after)
before='    emit_stage(json!({\n        "schema_version": 1, "stage": "suite_start"';after='    assert_eq!(filter.as_deref(),Some("rainbow"),"D087 diagnostic fixture");\n    assert!(storage==Storage::Compressed && !profile,"D087 diagnostic settings");\n    emit_stage(json!({\n        "schema_version": 1, "stage": "suite_start"';assert source.count(before)==1;source=source.replace(before,after)
# Six diagnostic phase brackets; every benchmark arithmetic/stop path stays exact.
for before,after in [
 ('        let mut gpu = GpuSolver::new(&host)', '        assert_eq!(unsafe{D087PhaseTrace(1)},1,"phase init begin");\n        let mut gpu = GpuSolver::new(&host)'),
 ('        let gpu_init_ms = elapsed_ms(stage_start);', '        assert_eq!(unsafe{D087PhaseTrace(2)},1,"phase init end");\n        let gpu_init_ms = elapsed_ms(stage_start);'),
 ('        let solve_start = Instant::now();', '        let solve_start = Instant::now();\n        assert_eq!(unsafe{D087PhaseTrace(3)},1,"phase solve begin");'),
 ('        let solve_checks_ms = elapsed_ms(solve_start);', '        assert_eq!(unsafe{D087PhaseTrace(4)},1,"phase solve end");\n        let solve_checks_ms = elapsed_ms(solve_start);'),
 ('        gpu.sync_to_cpu(&mut host).unwrap();', '        assert_eq!(unsafe{D087PhaseTrace(5)},1,"phase readback begin");\n        gpu.sync_to_cpu(&mut host).unwrap();'),
 ('        let full_readback_ms = elapsed_ms(stage_start);', '        assert_eq!(unsafe{D087PhaseTrace(6)},1,"phase readback end");\n        let full_readback_ms = elapsed_ms(stage_start);')
]:
 assert source.count(before)==1,before
 source=source.replace(before,after)
(H/'evaluator.rs').write_text(source,encoding='utf-8',newline='\n');(H/'evaluator.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='frozen-primary-evaluator',tofile='D087-diagnostic-evaluator')),encoding='utf-8',newline='\n')
manifest=old.read(ROOT/'binaries/E051-postflop_autoresearch.manifest.json');deps=manifest['dependency_artifact_sha256'];libs={name:next(p for p in deps if Path(p).name.startswith('lib'+name+'-') and p.endswith('.rlib')) for name in ['solver','cudarc','serde_json']};B=H/'diagnostic-build'
cmd=['rustc','--edition=2021','--test','--cfg','feature="gpu"',str(H/'evaluator.rs'),'--crate-name','d087_rainbow_trace','-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
for name,path in libs.items():cmd+=['--extern',name+'='+path]
cmd+=['-L','dependency='+str(Path(libs['solver']).parent),'-L','native='+str(H/'build'),'-o',str(B/'postflop-trace.exe')]
P={'id':'D087-diagnostic-build','at':old.now(),'status':'FROZEN_PRE_COMPILE','command':cmd,'output_dir':str(B),'source_sha256':old.BASE,'source_relationship':'Exact measured E051 solver rlib; same frozen evaluator with only explicit collector lifetime hooks, six timestamp phase brackets, fixed diagnostic restriction, and identical absolute bench input relocation. Start inside GPU-init clock, stop/flush after score/fingerprint with CUDA context alive. No primary source/evaluator changed.','diagnostic_scope':'One largest primary fixture, no optimization acceptance or whole-suite speed claim. Fresh3pairs must preserve full states/checkpoints and assess observer overhead before kernel-family evidence is used.','input_sha256':deps|{str(p):old.sha(p) for p in [H/'evaluator.rs',H/'evaluator.patch',H/'ability-report.json',H/'collector.cpp',H/'build-r3/D087Collector.dll',H/'build-r3/D087Collector.lib',base,old.REPO/'bench_spot.json']},'candidate_accepted':False,'performance_qualification':False};old.save(H/'diagnostic-build-plan.json',P)
for p in [H/'evaluator.rs',H/'evaluator.patch',H/'diagnostic-build-plan.json',H/'ability-report.json']:
 key=H.name+'/'+p.name;dest=old.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True);assert not dest.exists();dest.write_bytes(p.read_bytes())
 with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
print(old.sha(H/'diagnostic-build-plan.json'),flush=True)
