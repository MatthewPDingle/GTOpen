import sys,re,shutil,platform,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert shutil.disk_usage(ROOT).free>=74*1024**3
S=ROOT/'runs/E092-source';M=h.read(S/'manifest.json')
for p,d in M['owned_source_sha256'].items():h.pin(p,d)
for name,d in M['candidate_source_sha256'].items():h.pin(S/'candidate'/name,d)
cal=ROOT/'runs/D157-sampler-calibration/report.json';C=h.read(cal);assert C['status']=='pass_sampler_API_self_calibration'
h.pin(ROOT/'runs/D157-sampler.py',C['sampler_sha256'])
assert h.read(ROOT/'comparisons/D156-primary-lifecycle-control/report.json')['status']=='pass_scoped_full_primary_raw_lifecycle_equivalence'
H=ROOT/'runs/D157-actual-resources';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E090-engine-control/reference/D134-observer-parent.rs';t=parent.read_text(encoding='utf-8');shim=t[t.index('pub mod plan {'):t.index('\nmod arena;')]
benchpath=h.REPO/'crates/solver/tests/postflop_autoresearch.rs';original=benchpath.read_text(encoding='utf-8')
bench,n=re.subn(r'^//!','//',original,flags=re.M);assert n==7
bench=bench.replace('#![cfg(feature = "gpu")]\n','',1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};','use observed::{GpuSolver, KERNEL_NAMES};',1).replace('include_str!("../../../bench_spot.json")','include_str!("bench_spot.json")',1)
base_bench=bench
changes=[('        let solve_start = Instant::now();','        d157_emit(gpu.d157_resources("gpu_ready"));\n        let solve_start = Instant::now();'),('        let total_ms = elapsed_ms(total_start);','        let total_ms = elapsed_ms(total_start);\n        d157_emit(gpu.d157_resources("readback_complete"));')]
for a,b in changes:assert bench.count(a)==1;bench=bench.replace(a,b,1)
reverse=bench
for a,b in reversed(changes):reverse=reverse.replace(b,a,1)
assert reverse==base_bench
commands={};geometry={};deps=ROOT/'reference/accepted-e080-deps'
for arm in ['baseline','candidate']:
    d=H/arm;shutil.copytree(S/arm,d)
    prod=(d/'mod.rs').read_text(encoding='utf-8')
    adapted=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
    assert adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==prod
    body=prod[prod.index('pub struct GpuSolver {'):prod.index('\nfn checks_with_setup')];terms=[]
    for name,dtype,count in re.findall(r'^\s*(\w+):\s*\[?CudaSlice<(\w+)>\s*(?:;\s*(\d+)\])?',body,re.M):
        for i in range(int(count)) if count else [None]:terms.append(f'self.{name}'+(f'[{i}]' if i is not None else '')+f'.len()*std::mem::size_of::<{dtype}>()')
    assert len(terms)==66;geometry[arm]=terms
    obs=(ROOT/'runs/D157-observer.rs').read_text(encoding='utf-8').replace('D157_DEVICE_BYTES',' + '.join(terms)).replace('D157_MODULE_LOADED','self.packet_functions.is_some()' if arm=='candidate' else 'false')
    (d/'mod.rs').write_bytes((adapted+'\n'+obs).encode())
    if arm=='candidate':
        packet=d/'packet_readback.rs';raw=packet.read_text(encoding='utf-8');instrumented=raw
        pairs=[('        let [Some(a),Some(b)]=plans else {return Ok(false);};let plans=[a,b];','        let [Some(a),Some(b)]=plans else {return Ok(false);};let plans=[a,b];\n        crate::d157_emit(serde_json::json!({"kind":"packet_plan","capacity_bytes":plans.iter().map(|p|p.capacity()*std::mem::size_of::<Block>()).sum::<usize>(),"lengths":[plans[0].len(),plans[1].len()],"capacities":[plans[0].capacity(),plans[1].capacity()],"block_bytes":std::mem::size_of::<Block>(),"source_bytes":bytes}));'),('        if self.packet_functions.is_none() {','        if self.packet_functions.is_none() {\n            crate::d157_emit(self.d157_resources("module_before"));'),('        let stage=staging(&mut self.h_staging).expect("preflight checked prefix geometry");','        crate::d157_emit(self.d157_resources("module_after"));\n        let stage=staging(&mut self.h_staging).expect("preflight checked prefix geometry");')]
        for a,b in pairs:assert instrumented.count(a)==1;instrumented=instrumented.replace(a,b,1)
        reverse=instrumented
        for a,b in reversed(pairs):reverse=reverse.replace(b,a,1)
        assert reverse==raw;packet.write_bytes(instrumented.encode())
    prefix='#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="'+arm+'/mod.rs"]mod observed;\nfn d157_emit(v:serde_json::Value){println!("D157_RESOURCE {v}");std::io::Write::flush(&mut std::io::stdout()).unwrap();}\n'
    source=H/(arm+'-probe.rs');source.write_bytes((prefix+bench).encode())
    cmd=['rustc',str(source),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for crate,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/file)]
    commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
for source,dest in [('D157-sampler.py','sampler.py'),('D157-execute.py','execute.py'),('D157-assess.py','assess.py')]:shutil.copyfile(ROOT/'runs'/source,H/dest)
official=[{'url':'https://learn.microsoft.com/en-us/windows/win32/api/psapi/ns-psapi-process_memory_counters_ex','used':'Documented C fields; PeakPagefileUsage is private commit high-water,not disk paging. Win64 80byte layout inferred then verified by self calibration.'},{'url':'https://learn.microsoft.com/en-us/windows/win32/api/psapi/nf-psapi-getprocessmemoryinfo','used':'Process handle and counter access/size API contract.'},{'url':'https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-getprocesstimes','used':'Creation/exit and summed-thread CPU FILETIME,100ns. Interpret exit only after confirmed termination.'},{'url':'https://docs.nvidia.com/deploy/nvml-api/latest/api/structnvmlMemory__t.html','used':'Device-memory C fields; runtime size24 verified.'},{'url':'https://docs.nvidia.com/deploy/nvml-api/latest/api/group__nvmlDeviceQueries.html','used':'Global memory accounting and WDDM OS-managed limitations. No per-process/instantaneous peak claim.'}]
h.save(H/'source-review.json',{'at':h.now(),'observer_only_candidate_changes_reverse_exact':True,'canonical_workload_quality_and_history_unchanged_except_small_readonly_resource_calls':True,'no_raw_states_extra_iterations_queries_saves_or_forcing':True,'explicit_device_field_count':66,'device_byte_expressions':geometry,'new_wrapper_bytes':32,'sampler_calibration_sha256':h.sha(cal),'official_API_sources':official,'scope':'Read-only geometry/default-limit/free-memory snapshots plus exact actual temporary plan capacities. Main CUDA/PTX/production source frozen. Parent samples Win32/NVML every50ms,records terminal CPU/lifetime through all cleanup. No hardware counters,global settings or speed score. Sampling/observer overhead and device-wide accounting prevent universal peak/no-cost inference.'})
gates={'host_peak_working_set_max_added_bytes':64*1024**2,'host_peak_commit_max_added_bytes':64*1024**2,'sampled_device_global_max_added_bytes':64*1024**2,'process_CPU_median_max_regression_pct':1.0,'whole_process_lifetime_median_max_regression_pct':1.0,'nominal_sampling_interval_ms':50,'max_sample_gap_ms':1000,'minimum_samples_per_process':50,'wrapper_added_bytes_exact':32,'device_and_pinned_payload_exact':True,'context_stack_heap_exact':True}
files=[Path(__file__),ROOT/'runs/D157-observer.rs',ROOT/'runs/D157-sampler.py',ROOT/'runs/D157-execute.py',ROOT/'runs/D157-assess.py',cal,parent,benchpath,S/'manifest.json',S/'source-review.json',ROOT/'runs/D157-actual-resource-scope/scope-review.json',ROOT/'comparisons/D156-primary-lifecycle-control/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/exact-anchor.json',Path(sys.executable),Path(r'C:\Windows\System32\nvml.dll'),Path(r'C:\Windows\System32\kernel32.dll'),Path(r'C:\Windows\System32\KernelBase.dll')]+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for name in ['execute','assess','sampler']:compile((H/(name+'.py')).read_text(encoding='utf-8'),name,'exec')
h.save(H/'protocol.json',{'id':'D157','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_RESOURCE_COHORT','rustc_commands':commands,'sequence':[{'id':i,'arm':a} for i,a in [('B1','baseline'),('C1','candidate'),('C2','candidate'),('B2','baseline')]],'pairs':[{'baseline':'B1','candidate':'C1'},{'baseline':'B2','candidate':'C2'}],'material_prerequisite_limits':gates,'expected_candidate_module_activation':{'rainbow':True,'two-tone':True,'river':False},'NVML_versions':C['NVML_versions'],'required_free_bytes':74*1024**3,'raw_reservation_bytes':8*1024**3,'expected_scientific_full_records':12,'expected_checkpoints':92,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Two Rust compilers then fixed B1/C1/C2/B2 resource processes with exact canonical science. Freeze64MiB added reported CPU working-set/commit and sampled global GPU allowance,max1% total-process median CPU and lifetime regressions,exact explicit/pinned payload and default limits,+32byte wrapper. These are coarse prospective feasibility limits,not universal materiality/capacity or confidence claims. Whole process includes teardown. No numerical/source/admission/width/gate/sample rescue after failed form. Mechanical pre-native adapter or retained-reader bookkeeping preserves originals. Zero performance-qualification samples; separate fresh uninstrumented builds/cohort still required if feasible.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
