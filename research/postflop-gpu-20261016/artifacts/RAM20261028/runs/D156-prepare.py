import sys,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
assert shutil.disk_usage(ROOT).free>=194*1024**3
S=ROOT/'runs/E092-source';M=h.read(S/'manifest.json')
for p,d in M['owned_source_sha256'].items():h.pin(p,d)
for name,d in M['candidate_source_sha256'].items():h.pin(S/'candidate'/name,d)
failure=ROOT/'comparisons/D155-coverage-failure/report.json';assert not h.read(failure)['original_cohort_passed']
H=ROOT/'runs/D156-primary-lifecycle-control';H.mkdir(exist_ok=False)
parent=ROOT/'runs/E090-engine-control/reference/D134-observer-parent.rs';t=parent.read_text(encoding='utf-8');shim=t[t.index('pub mod plan {'):t.index('\nmod arena;')]
benchpath=h.REPO/'crates/solver/tests/postflop_autoresearch.rs';original=benchpath.read_text(encoding='utf-8')
bench,n=re.subn(r'^//!','//',original,flags=re.M);assert n==7
bench=bench.replace('#![cfg(feature = "gpu")]\n','',1).replace('use solver::gpu::{GpuSolver, KERNEL_NAMES};','use observed::{GpuSolver, KERNEL_NAMES};',1).replace('include_str!("../../../bench_spot.json")','include_str!("bench_spot.json")',1)
needle='        completed += 1;';assert bench.count(needle)==1
bench=bench.replace(needle,'        assert!(!profile, "resource/lifecycle control forbids optional profiler");\n        d156_after(gpu,host,name);\n'+needle,1)
helper=(ROOT/'runs/D156-lifecycle.rs').read_text(encoding='utf-8')
commands={}
deps=ROOT/'reference/accepted-e080-deps'
for arm in ['baseline','candidate']:
    d=H/arm;shutil.copytree(S/arm,d)
    prod=(d/'mod.rs').read_text(encoding='utf-8')
    adapted=prod.replace('pub mod plan;',shim,1).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);',1)
    assert adapted.replace(shim,'pub mod plan;',1).replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);',1)==prod
    observer=(ROOT/'runs/D156-observer.rs').read_text(encoding='utf-8').replace('D156_MODULE_LOADED','self.packet_functions.is_some()' if arm=='candidate' else 'false')
    (d/'mod.rs').write_bytes((adapted+'\n'+observer).encode())
    prefix='#![allow(dead_code,unused_imports,unused_mut,hidden_glob_reexports)]\npub use solver::*;\n#[path="'+arm+'/mod.rs"]mod observed;\n'
    source=H/(arm+'-probe.rs');source.write_bytes((prefix+bench+'\n'+helper).encode())
    cmd=['rustc',str(source),'--edition=2021','--test','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for crate,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/file)]
    commands[arm]=cmd+['-o',str(H/(arm+'.exe'))]
shutil.copyfile(h.REPO/'bench_spot.json',H/'bench_spot.json')
for name in ['audit','execute']:shutil.copyfile(ROOT/'runs'/f'D156-{name}.py',H/(name+'.py'))
h.save(H/'scope-review.json',{'at':h.now(),'D155_remains_incomplete_failed_coverage':True,'D155_samples_or_status_regraded':False,'candidate_source_revised':False,'why_next':'The existing full-size primary fixtures and broad save/lock/resume correctness were mandatory before the D155 coverage failure. Run those unchanged fixed workloads with ordinary E09216MiB admission. This does not extend or repair D155, resize its corpus/capacity, alter a threshold, or score an optimization. Compact packed behavior remains unproven until this separate existing workload check succeeds.','full_raw_requirement':'Retain every CPU q/scale/publication word, whole query/save files, and complete physical CFV after converged/continued/locked/resumed readbacks. Require byte equality of CPU/query/save, exact EV bits and same CFV tail beyond65544words on admitted paths (entire physical CFV on original declines).','benchmark_boundary':'Original canonical full results/checkpoints are emitted before added lifecycle work. Control changes later fixture history and includes giant raw output/extra iterations/save/load; its printed timing fields are diagnostics only. Never reuse as primary/fresh16 performance samples or current baseline.','resources':'Compiled wrapper/geometry/graph-presence recorded. This full raw/lifecycle observer is unsuitable for CPU/GPU peak-memory claims. Separate actual resource profiling and broad capacity remain required before timing/adoption.','scope':'One fixed baseline process then one candidate process,three existing canonical fixtures, compressed/DCFR/defaultiso. Extra lock/resume actions and read-only snapshots occur after original fingerprint result. No alternate ranges/boards/algorithm/threshold/candidate source, retries or extra samples after an actual scientific failure.'})
files=[Path(__file__),ROOT/'runs/D156-lifecycle.rs',ROOT/'runs/D156-observer.rs',ROOT/'runs/D156-audit.py',ROOT/'runs/D156-execute.py',parent,benchpath,S/'manifest.json',S/'source-review.json',failure,ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/exact-anchor.json']+[p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for name in ['audit','execute']:compile((H/(name+'.py')).read_text(encoding='utf-8'),name,'exec')
h.save(H/'protocol.json',{'id':'D156','at':h.now(),'status':'FROZEN_PRE_COMPILERS_AND_FULL_PRIMARY_CONTROLS','rustc_commands':commands,'sequence':['baseline','candidate'],'expected_full_results':6,'expected_checkpoints':46,'lifecycle_stages':['converged','continued','locked','resumed'],'expected_CPU_raw_pairs':12,'expected_CFV_raw_pairs':12,'expected_query_pairs':6,'expected_save_pairs':3,'expected_additional_EV_pairs':9,'expected_candidate_module_activation':{'rainbow':True,'two-tone':True,'river':False},'required_free_bytes':194*1024**3,'raw_reservation_bytes':128*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'performance_qualification_samples':0,'scope':'Two compilers and fixed B/C full canonical workload/lifecycle controls,then independent full retained-word reader. E092 production source/shape/admission fixed. D155 incomplete coverage remains failed. Exact old canonical scientific records/checkpoints,whole CPU q/scales/query/save and physical CFV bounds/future EVs required. No source/width/shape/workload/threshold/gate/sample rescue after actual numerical/activation failure. Pre-native adapter or retained-reader bookkeeping preserves originals. No performance, peak-memory or adoption claim.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
