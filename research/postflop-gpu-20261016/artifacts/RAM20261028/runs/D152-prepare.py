import sys,re,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
import numpy as np
h.custody();h.ar.refuse_active(h.ar.live_status())
assert not (ROOT/'gpu-run.lock').exists()
assert h.read(ROOT/'runs/D151-auxiliary-resource/report.json')['status']=='pass_scoped_auxiliary_compile_load_resources'
assert shutil.disk_usage(ROOT).free>=74*1024**3
H=ROOT/'runs/D152-packet-numerics';H.mkdir(exist_ok=False)
original=ROOT/'runs/D148-packed-readback-design/reference/original-encoding-proof.rs'
t=original.read_text(encoding='utf-8')
generator=t[t.index('struct Case {'):t.index('\n#[test]')]
seed=re.search(r'const SEED: u64 = .*?;',t).group()
lengths=re.search(r'const LENGTHS: &\[usize\] = &\[.*?\];',t,re.S).group()
prefix='''#![allow(dead_code,unused_imports)]
use cudarc::{driver::{CudaContext,LaunchConfig,PushKernelArg},nvrtc::Ptx};
use solver::store::{encode_i16,encode_u16};
use serde_json::{json,Value};
use std::{fs::OpenOptions,io::{Write,BufWriter},path::{Path,PathBuf}};
'''
(H/'probe.rs').write_bytes((prefix+seed+'\n'+lengths+'\n'+generator+'\n'+(ROOT/'runs/D152-main.rs').read_text(encoding='utf-8')).encode())
for name in ['audit','execute']:shutil.copyfile(ROOT/'runs'/f'D152-{name}.py',H/(name+'.py'))
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for crate,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',crate+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
ptx=ROOT/'runs/D151-auxiliary-resource/execution/packet-compute_120.ptx'
h.pin(ptx,h.read(ROOT/'runs/D151-auxiliary-resource/report.json')['PTX_sha256']['compute_120'])
npnative=list(Path(np.__file__).parent.rglob('*multiarray_umath*.pyd'));assert len(npnative)==1
files=[Path(__file__),ROOT/'runs/D152-main.rs',ROOT/'runs/D152-audit.py',ROOT/'runs/D152-execute.py',original,ptx,ROOT/'runs/D151-auxiliary-resource/report.json',ROOT/'runs/D151-auxiliary-resource/source-review.json',ROOT/'comparisons/D148-packet-model/report.json',ROOT/'comparisons/D150-CFV-liveness/report.json',ROOT/'epoch/common.py',ROOT/'epoch/accepted-source.json',ROOT/'epoch/protected-main.json',ROOT/'epoch/preexisting-target-artifacts.json',Path(np.__file__)]+npnative+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
for name in ['audit','execute']:compile((H/(name+'.py')).read_text(encoding='utf-8'),name,'exec')
h.save(H/'protocol.json',{'id':'D152','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_ACTUAL_PACKET_KERNELS','rustc_command':cmd,'PTX_path':str(ptx),'PTX_sha256':h.sha(ptx),'cases_per_type':2212,'cohorts':6,'descriptor_limits':[1,7,31],'capacity_words':65544,'raw_reservation_bytes':8*1024**3,'required_free_bytes':74*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'One Rust compiler, one finite serialized GPU data control process using persisted D151 PTX with no NVRTC, then independent retained full-word reader. Original2212case generator extracted byte-exact, shared accepted Rust encode_i16/u16 as oracle. Every packet/host q/scale/guard exact; full source bits before/after six cohorts. Signedzeros,ties,NaN/Inf/subnormal/saturation and empty/odd/long tail cases retained. No source/width/case/gate/sampling variants after actual numerical failure. Reader/pre-native build adapter bookkeeping may preserve originals and replay unchanged scientific observations. No integration, performance measurement or acceptance.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
