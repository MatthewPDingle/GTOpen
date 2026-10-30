"""Freeze exact full-workload resource controls using independently calibrated APIs."""
from pathlib import Path
import ast,difflib,json,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
old.custody();assert not(R/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(R).free>=66*1024**3
H=R/'runs/E080-resource-controls';assert H.exists()and not(H/'protocol.json').exists()
cpu=R/'runs/E080-cpu-commit-ability/report.json';gpu=R/'runs/E080-memory-observer-ability/report.json';cq=old.read(cpu);gq=old.read(gpu);assert cq['all_checks_pass']and cq['CUDA_contexts']==0
gpu_checks=[x for x in gq['checks']if'GPU'in x['label']];assert len(gpu_checks)==18 and all(x['passed']for x in gpu_checks)and not gq['all_checks_pass']
assert old.read(R/'runs/E080-memory-observer-ability/calibration-closure.json')['overall_observer_form']=='closed_after_failed_combined_private_commit_control'
assert old.read(R/'comparisons/E080-remaining-root-check/report.json')['status']=='pass_remaining_timing_and_capacity_only'
original_path=old.REPO/'crates/solver/tests/postflop_autoresearch.rs';original=original_path.read_text(encoding='utf-8')
bridge=r'''
#[repr(C)] #[derive(Default)] struct ResourceFileTime { low: u32, high: u32 }
#[repr(C)] #[derive(Default)] struct ResourceMemory {
    cb: u32, faults: u32, peak_working: usize, working: usize,
    quota_peak_paged: usize, quota_paged: usize, quota_peak_nonpaged: usize,
    quota_nonpaged: usize, pagefile: usize, peak_pagefile: usize, private: usize,
}
#[link(name = "kernel32")]
extern "system" {
    fn GetCurrentProcess() -> *mut std::ffi::c_void;
    fn GetProcessTimes(h: *mut std::ffi::c_void, c: *mut ResourceFileTime,
        e: *mut ResourceFileTime, k: *mut ResourceFileTime, u: *mut ResourceFileTime) -> i32;
    fn K32GetProcessMemoryInfo(h: *mut std::ffi::c_void, p: *mut ResourceMemory, n: u32) -> i32;
}
fn resource_os_sample() -> Value {
    assert_eq!(std::mem::size_of::<ResourceFileTime>(), 8);
    assert_eq!(std::mem::size_of::<ResourceMemory>(), 80);
    let mut c=ResourceFileTime::default(); let mut e=ResourceFileTime::default();
    let mut k=ResourceFileTime::default(); let mut u=ResourceFileTime::default();
    let mut m=ResourceMemory::default(); m.cb=80;
    unsafe {
        let h=GetCurrentProcess();
        assert_ne!(GetProcessTimes(h,&mut c,&mut e,&mut k,&mut u),0);
        assert_ne!(K32GetProcessMemoryInfo(h,&mut m,80),0);
    }
    let ticks=|x: &ResourceFileTime| ((x.high as u64)<<32)|x.low as u64;
    json!({"cpu_ticks100ns":ticks(&k)+ticks(&u),"creation_filetime":ticks(&c),
        "peak_working_bytes":m.peak_working,"working_bytes":m.working,
        "private_bytes":m.private,"peak_commit_bytes":m.peak_pagefile,
        "pagefile_bytes":m.pagefile,"page_faults":m.faults,"memory_structure_bytes":m.cb})
}
'''
source=original;needle='\nconst TARGET_PCT_POT';assert source.count(needle)==1;source=source.replace(needle,bridge+needle,1)
needle='include_str!("../../../bench_spot.json")';assert source.count(needle)==1;source=source.replace(needle,'include_str!(r"'+str(old.REPO/'bench_spot.json')+'")',1)
needle='        let total_start = Instant::now();';assert source.count(needle)==1;source=source.replace(needle,'        let resource_os_begin = resource_os_sample();\n'+needle,1)
needle='        let total_ms = elapsed_ms(total_start);';assert source.count(needle)==1;source=source.replace(needle,needle+'\n        let resource_os_timing_complete = resource_os_sample();',1)
needle='        assert!(target_met, "{name} did not reach the frozen target within {MAX_ITERATIONS} iterations");';assert source.count(needle)==1
extra='''
        let resource_os_after_fingerprint = resource_os_sample();
        let resource_cpu_begin = resource_os_begin["cpu_ticks100ns"].as_u64().unwrap();
        let resource_cpu_end = resource_os_timing_complete["cpu_ticks100ns"].as_u64().unwrap();
        assert!(resource_cpu_end >= resource_cpu_begin);
        emit_stage(json!({"stage":"resource_fixture","fixture_id":name,
            "cpu_delta_ticks100ns":resource_cpu_end-resource_cpu_begin,
            "os_begin":resource_os_begin,"os_timing_complete":resource_os_timing_complete,
            "os_after_fingerprint":resource_os_after_fingerprint,"performance_score":false}));
'''
source=source.replace(needle,needle+extra,1);pos=source.rfind('\n}');assert pos>0;source=source[:pos]+'\n    emit_stage(json!({"stage":"resource_suite_complete","OS":resource_os_sample()}));\n'+source[pos:]
(H/'evaluator.rs').write_text(source,encoding='utf-8',newline='\n');(H/'evaluator.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='frozen-primary',tofile='resource-observation-only')),encoding='utf-8',newline='\n')
for name in['build.py','execute.py','assess.py']:ast.parse((H/name).read_text(encoding='utf-8'))
S=old.read(R/'runs/E080-source/manifest.json');compilers=[];paths=[Path(__file__),*[p for p in H.iterdir()if p.is_file()],original_path,old.REPO/'bench_spot.json',cpu,gpu,R/'runs/E080-memory-observer-ability/win_observer.py',R/'runs/E080-memory-observer-ability/calibration-closure.json',R/'runs/E080-cpu-commit-manager/ability.exit.json',R/'runs/E080-memory-observer-manager/ability.exit.json',R/'comparisons/E080-remaining-root-check/report.json',R/'comparisons/E080-fresh16-confirmation/report.json',C/'common_e051_live.py',C/'protected-main.json',R/'runs/E020C1/report.json',R/'runs/E020C1/stdout.log']
for arm,stem in[('baseline','E051-postflop_autoresearch'),('candidate','E080-postflop_autoresearch')]:
    mp=R/'binaries'/(stem+'.manifest.json');m=old.read(mp);assert m['source_sha256']==old.BASE|(S['candidate_owned_sha256']if arm=='candidate'else{});deps=m['dependency_artifact_sha256'];libs={}
    for name in['solver','serde_json']:
        found=[p for p in deps if Path(p).suffix=='.rlib'and Path(p).name.startswith('lib'+name+'-')];assert len(found)==1;libs[name]=found[0]
    for p,h in deps.items():old.pin(p,h)
    dest=H/'build'/('resource-'+arm+'.exe');cmd=['rustc','--edition=2021','--test','--cfg','feature="gpu"',str(H/'evaluator.rs'),'--crate-name','e080_resource_'+arm,'-C','opt-level=3','-C','lto=thin','-C','codegen-units=1']
    for name,p in libs.items():cmd+=['--extern',name+'='+p]
    cmd+=['-L','dependency='+str(Path(libs['solver']).parent),'-o',str(dest)];compilers.append({'arm':arm,'binary':str(dest),'command':cmd,'dependencies':deps,'source_sha256':m['source_sha256'],'primary_manifest':str(mp)});paths.append(mp)
P={'id':'E080-actual-resource-controls','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_COST_OBSERVATIONS','input_sha256':{str(p):old.sha(p)for p in paths},'compilers':compilers,'order':[{'id':'MB1','arm':'baseline'},{'id':'MC1','arm':'candidate'},{'id':'MC2','arm':'candidate'},{'id':'MB2','arm':'baseline'},{'id':'MB3','arm':'baseline'},{'id':'MC3','arm':'candidate'}],'pairs':[{'baseline':'MB1','candidate':'MC1'},{'baseline':'MB2','candidate':'MC2'},{'baseline':'MB3','candidate':'MC3'}],'GPU_counter_paths':old.read(R/'runs/E080-resource-readiness/report.json')['GPU_process_memory_counter_paths'],'sampling_interval_ms':20,'minimum_GPU_peak_bytes':512*1024*1024,'minimum_GPU_peak_samples':5,'minimum_GPU_peak_span_ms':100,'maximum_p99_sampling_gap_ms':100,'guards':{'CPU_phase_sum_ratio':1.02,'CPU_phase_fixture_ratio':1.02,'CPU_whole_process_ratio':1.02,'CPU_allowance_ms':15.625,'host_peak_fraction':0.01,'host_peak_minimum_allowance_bytes':16*1024*1024,'GPU_peak_allowance_bytes':2*1024*1024},'observer_evidence':'Use original fixed GPU allocation/release records (18/18 GPU checks passed) and independent CPU-only VirtualAlloc commitment/RSS control. Original combined private-payload control remains failed, closed and not relabeled. Actual resource measurements retain total CUDA/driver process commitment; no driver bytes are subtracted.','scope':'Exactly6fresh full compressed primary suites BC/CB/BC. Same solver libraries, fixture order, target, checks, stop rules, storage and full readback as accepted benchmark. Add only native OS snapshots before total_start, after full readback and after fingerprint, plus post-suite snapshot. GPU memory is PID-filtered read-only OS software accounting. Process-CPU totals and native phase CPU capture all threads including completed worker. Full raw OS/PID/GPU samples retained. CPU phase windows include original solve work with negligible snapshot-call boundary overhead; whole-process CPU additionally covers fingerprint/startup/destruction. Host peak fields are OS process-lifetime highwaters, not per-fixture isolated peaks. GPU peaks are sampled, with cadence/plateau coverage gates. No new application GPU calls, math, quality or source activation. No timing score or historical timing pooling; resource timings not used to rescue earlier performance.','policy':'Material CPU <=baseline median*1.02+one15.625ms accounting quantum, both per-fixture phases and phase sum/whole-process. Host highwater medians <=baseline+max(1%,16MiB). GPU dedicated/shared peak medians <=baseline+2MiB. All fixed records/checkpoints exact. No exclusions/extensions/source/threshold/helper/thread/flag/placement variants after an actual material failure. Responsiveness and final scope/resource audit remain before adoption.','candidate_accepted':False}
for row in compilers:P['input_sha256'].update(row['dependencies'])
old.save(H/'protocol.json',P)
for p in[Path(__file__),*[p for p in H.iterdir()if p.is_file()]]:
    key=H.name+'/'+p.name;dst=old.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
    with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as response:assert response.read()==p.read_bytes()
old.save(H/'pre-build-publication.json',{'at':old.now(),'protocol_sha256':old.sha(H/'protocol.json'),'HTTP_byte_verified':True,'compiler_or_solver_cost_observations':0})
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=old.read(old.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E080');e.update(status='running',accepted=False,stage='Full-workload resource controls',reason='Freeze three resource pairs on all primary workloads. Native snapshots measure all-thread CPU inside complete-cycle boundaries and OS process highwaters; PID-filtered GPU accounting was calibrated with real allocations. Retain all driver commitment and all samples. Original combined calibration stays failed, independent CPU control passed. No adoption yet.');e['evidence'].append({'label':'Prospective full-workload resource gates','url':'evidence/E080-resource-controls/protocol.json'});s.update(updated_at=old.now(),state='running',goal_status='active',active_experiment='E080',stage='E080 actual resource controls',activity='Build and run the fixed actual CPU, host/GPU memory resource comparison. Timings are diagnostic only; prior primary/fresh16/holdout/cumulative scores stay unchanged. Source and live E051 remain untouched.');old.ar.atomic_json(old.ar.STATUS,s)
old.custody();print('E080 actual resource protocol',old.sha(H/'protocol.json'),flush=True)
