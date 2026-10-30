import sys,shutil,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
assert h.read(ROOT/'comparisons/D163-action-compiler-controls/report.json')['cases']==2349
prior=Path(r'S:\GTOpen-research\postflop-gpu-20261016\runs\E089-kernel-control');H=ROOT/'runs/D164-showdown-compiler-control';H.mkdir(exist_ok=False)
for name in ['corpus.json','accepted-evaluator.rs']:shutil.copyfile(prior/name,H/name)
for arm in ['baseline','candidate']:
    shutil.copyfile(ROOT/'runs/D162-private-dependency-repair/execution'/(arm+'.ptx'),H/(arm+'.ptx'))
    shutil.copyfile(h.REPO/'crates/solver/src/gpu/kernels.cu',H/(arm+'.cu'))
src=(prior/'probe.rs').read_text(encoding='utf-8');needle='fn main(){if let Err(error)=run()'
assert src.count(needle)==1;src=src.replace(needle,'fn main(){std::env::set_current_dir(std::env::args_os().nth(1).expect("fresh output directory")).unwrap();if let Err(error)=run()',1)
(H/'probe.rs').write_bytes(src.encode())
audit=(prior/'audit.py').read_text(encoding='utf-8');needle="sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old"
assert audit.count(needle)==1;audit=audit.replace(needle,"sys.path.insert(0,str(R/'epoch'));import common as old",1).replace('E089-kernel-control-root-check','D164-showdown-compiler-control').replace("'id':'E089-kernel-control'","'id':'D164'").replace('pass_scoped_full_serial_card_loop_raw_equivalence','pass_scoped_full_showdown_raw_equivalence')
(H/'audit.py').write_bytes(audit.encode());ast.parse(audit)
shutil.copyfile(ROOT/'runs/D164-execute-showdown.py',H/'execute.py');ast.parse((H/'execute.py').read_text(encoding='utf-8'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-A','unused_imports','-L','dependency='+str(deps)]
for name,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
corpus=h.read(H/'corpus.json');assert len(corpus['cases'])==364 and len(corpus['geometries'])==36
h.save(H/'source-review.json',{'at':h.now(),'id':'D164','status':'full_existing_showdown_corpus_no_math_or_range_change','origin':str(prior),'original_corpus_sha256':h.sha(prior/'corpus.json'),'kernel':'up_show','source':'Same accepted CUDA inboth arms,sealed12.9/13PTX from D162. No compilation repeated. Original364physical cases x5widths and all geometry/profiles/inputs/expected/tolerances unchanged.','adapters':'Native main changes only child own current directory to explicit fresh output argument. Retained reader changes only common import,output ID/status/path. Historical E089native marker/magic retained as format;no historical outputs reused. Accepted evaluator source/corpus copied exact from archived original.','scope':'Physical showdown output span/full guards and all21actual immutable input buffers perarm. Bothfinite/nonfinite/signedzero/subnormal/tie/rake/rounding witnesses and whole0..1326hand/geometries as existing corpus. Only one of9changed kernels;not full engine or compiler qualification. Any actual mismatch closes13compiler form without source/shape/width/version/flag/sample rescue.','limitations':'Source bodies include unused old NVRTC imports,but actual run loads sealedPTX only. No compiler,solver or timing call in native control. No global/preflop or live source mutation.'})
files=[Path(__file__),ROOT/'runs/D164-execute-showdown.py',prior/'probe.rs',prior/'audit.py',prior/'corpus.json',prior/'accepted-evaluator.rs',ROOT/'comparisons/D163-action-compiler-controls/report.json',ROOT/'comparisons/D162-private-dependency-repair/report.json']+[p for p in H.iterdir() if p.is_file()]+[deps/'libcudarc-ba3140064b5903a3.rlib',deps/'libserde_json-83a0670a02a34a4d.rlib']
h.save(H/'protocol.json',{'id':'D164','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_SHOWDOWN_KERNELS','rustc_command':cmd,'widths':[1,32,64,128,256],'base_cases':364,'geometries':36,'expected_pairs':1820,'expected_application_launches':3640,'raw_reservation_bytes':2*1024**3,'required_free_bytes':70*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One fresh Rust compiler,one original1820pair native process,full retained reader. Same source/default math,exact sealed PTX. No NVRTC/source activation/solver/performance. Numerical failure closes form without rescue;no corpus/width/source/version/flag/sample changes.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
