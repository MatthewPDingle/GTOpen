import sys,json
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');H=R/'runs/E087-transfer-control'
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody()
Q=old.read(R/'runs/E087-host-type-check/protocol.json')
deps=R/'build-e080-final-primary/release/deps'
cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for crate,fn in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('rayon','librayon-8ab48cfec9cf00f9.rlib')]:cmd+=['--extern',crate+'='+str(deps/fn)]
cmd+=['-o',str(H/'probe.exe')]
pins={p:h for p,h in Q['input_sha256'].items()if str(deps)in p}
files=list(H.rglob('*'))+[R/'runs/E087-prepare-transfer-control-r2.py',R/'runs/E087-arena-observer.rs',R/'runs/E087-transfer-probe.rs',R/'runs/E087-source/manifest.json',R/'runs/E087-source/source-review.json',R/'runs/E087-host-type-check/execution/complete.json',R/'runs/accepted-E080-live-20261018/common_e080_live.py',R/'runs/E087-freeze-transfer-control.py']
files+=list((R/'runs/E087-source/candidate').glob('*.rs'))+list((R/'runs/E087-source/baseline').glob('*.rs'))
for p in files:
 if p.is_file():pins[str(p)]=old.sha(p)
for p,h in pins.items():old.pin(p,h)
old.save(H/'protocol.json',{'id':'E087-transfer-control','at':old.now(),'status':'FROZEN_PRE_COMPILER_AND_GPU_CONTROLS','rustc_command':cmd,'input_sha256':pins,'manual_layouts':96,'manual_arena_phases':192,'small_engine_cases':8,'large_constructor_cases':8,'raw_reservation_bytes':32*1024**3,'admission_S_free_bytes':98*1024**3,'T_reserve_bytes':50*1024**3,'production_window_bytes':67108864,'correctness_only_manual_window_words':257,'D104_performance_counters_closed':True,'candidate_source_sha256':old.read(R/'runs/E087-source/manifest.json')['candidate_owned_sha256'],'scope':'Same real production source with reversible accepted public-plan adapter and appended read-only controls. Whole CPU/GPU raw comparisons, full nodes, inactive snapshots, positive/signedzero/subnormal/nonfinite warm states, compressed/F32/full/compact, prechecked/unprechecked, repeated and warm transfers, actual 64MiB constructors, small trained exact query/save/load/resume, tiny budget, queued valid DMA with reported error and post-ready CPU unwind. No performance or memory footprint score. Source/math/precision/CUDA/quality/window/gates fixed; no tuning or failed sample rescue.','candidate_accepted':False})
print(old.sha(H/'protocol.json'),flush=True)
