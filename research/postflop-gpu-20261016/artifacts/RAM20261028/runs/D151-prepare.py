import sys, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists()
assert h.read(ROOT/'comparisons/D150-CFV-liveness/report.json')['status']=='pass_scoped_actual_CFV_clobber_liveness'
H=ROOT/'runs/D151-auxiliary-resource'
H.mkdir(exist_ok=False)
for source,name in [('D151-packet-quantize.cu','packet.cu'),('D151-offline-compile.rs','offline-compile.rs'),('D151-load-resource.rs','load-resource.rs'),('D151-execute.py','execute.py')]:
    shutil.copyfile(ROOT/'runs'/source,H/name)
deps=ROOT/'reference/accepted-e080-deps'
commands=[]
for name in ['offline-compile','load-resource']:
    cmd=['rustc',str(H/(name+'.rs')),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
    for crate,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:
        cmd += ['--extern',crate+'='+str(deps/file)]
    cmd += ['-o',str(H/(name+'.exe'))]
    commands.append(cmd)
proof=ROOT/'runs/D148-packed-readback-design/reference/original-encoding-proof.cu'
registry=Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\cudarc-0.19.7\src\nvrtc\safe.rs')
files=[Path(__file__),ROOT/'runs/D151-execute.py',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',ROOT/'comparisons/D148-packet-model/report.json',ROOT/'comparisons/D150-CFV-liveness/report.json',ROOT/'comparisons/D149-invalid-fixture/report.json',ROOT/'comparisons/D149-invalid-fixture/fixture-repair-review.json',ROOT/'runs/D148-packed-readback-design/design-review.json',proof,registry]
files += [p for p in H.rglob('*') if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]+[p for p in Path(h.ar.NVRTC).iterdir() if p.is_file()]
compile((ROOT/'runs/D151-execute.py').read_text(encoding='utf-8'),'D151-execute.py','exec')
h.save(H/'source-review.json',{'at':h.now(),'prototype_not_linked_or_active':True,'main_solver_CUDA_and_source_unchanged':True,'reference_encoder_source_sha256':h.sha(proof),'packet_source_sha256':h.sha(H/'packet.cu'),'arithmetic':'Retain original fmax/abs max reduction, explicit fdiv_rn/fmul_rn, ties-even conversion and Rust saturation/NaN logic. Change transport only: four-word descriptors and padded packed uint32 q output. Whole-word writers prevent odd node boundary halfword races. Exact numerical equivalence still requires actual CPU-oracle controls.','addressing':'All source offsets and induction are u64. Four descriptor words per node; scale/output regions follow 4N/5N. D148 finite address model passed. Host planner must prove every region in bounds and mutually disjoint before upload. GPU entry contract exactly128 threads/grid=count, with no grid-stride packet variant. Native physical high-offset allocation remains unproven.','lifetime':'D150 finite actual full-scratch replacement controls passed752 phases, including explicit save/load fixture setting restoration. D149 remains invalid, not pooled. This supports only subsequent scratch regeneration in the finite matrix. Actual packet runtime/pinned borrow/current swapped buffer validity remain integration obligations.','prebuilt_contract':'Compile two PTX architectures in one source-only helper, persist artifact and bind SHA. Load compute120 only from file in a separate fresh process with no NVRTC call, no solver and no application kernel launch. Driver JIT/module costs remain unmeasured and cannot be claimed removed.','resource_gate':'Exactly2 entries/3-parameter ABI/64-bit PTX, successful120/75 compile and120 load/drop, exact512 static shared bytes, zero local/dynamic shared, positive128-thread theoretical occupancy and default stack/heap limits unchanged. These are bounded prerequisites, not a no-memory-cost or speed claim.'})
files += [H/'source-review.json']
h.save(H/'protocol.json',{'id':'D151','at':h.now(),'status':'FROZEN_PRE_COMPILERS_NVRTC_AND_DRIVER_LOAD','rustc_commands':commands,'GPU_uuid':'GPU-a5459b5a-632b-3e73-d7f1-a06e167102ee','required_free_bytes':66*1024**3,'expected_entries':['packet_quantize_i16','packet_quantize_u16'],'input_sha256':{str(p):h.sha(p) for p in files},'scope':'Two Rust compilers, one offline helper with exactly2 NVRTC compilations, then one separate fresh driver module-load/resource helper. No solver or kernel launches. Source/flags/resource gates frozen before compilation; no resource/width/shape/source rescue after a real prerequisite failure. All new artifacts X; old rejected E009/E010 remain closed. No timing, production activation or candidate acceptance.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
