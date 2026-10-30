import sys,shutil,ast
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
contract=ROOT/'runs/D167-runtime-compiler-contract/design-review.json';assert h.read(contract)['status']=='FROZEN_PRE_RUNTIME_OPTIMIZER_SOURCE'
H=ROOT/'runs/D167-runtime-compiler-control';H.mkdir(exist_ok=False)
for source,dest in [('E093-nvrtc13.rs','nvrtc13.rs'),('D167-runtime-probe.rs','probe.rs'),('D167-execute-runtime.py','execute.py')]:shutil.copyfile(ROOT/'runs'/source,H/dest)
ast.parse((H/'execute.py').read_text(encoding='utf-8'))
shutil.copyfile(h.REPO/'crates/solver/src/gpu/kernels.cu',H/'kernels.cu');shutil.copyfile(ROOT/'runs/D162-private-dependency-repair/execution/candidate.ptx',H/'expected-candidate.ptx')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib'),('libloading','liblibloading-8d2068e2bf38a2f1.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')]
tool=ROOT/'runs/D161-toolchain-scout';directory=tool/'toolchain/nvidia/cu13/bin/x86_64'
files=[Path(__file__),contract,ROOT/'comparisons/D166-canonical-compiler-control/report.json',ROOT/'runs/E093-nvrtc13.rs',ROOT/'runs/D167-runtime-probe.rs',ROOT/'runs/D167-execute-runtime.py',tool/'toolchain-files.json',tool/'toolchain/nvidia/cu13/include/nvrtc.h',Path(r'C:\Users\there\.cargo\registry\src\index.crates.io-1949cf8c6b5b557f\libloading-0.9.0\src\os\windows\mod.rs')]+[p for p in directory.glob('*.dll')]+[p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
h.save(H/'protocol.json',{'id':'D167','at':h.now(),'status':'FROZEN_PRE_RUST_COMPILER_AND_RUNTIME_API_CONTROL','rustc_command':cmd,'private_runtime_directory':str(directory),'required_free_bytes':8*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'expected_successful_shader_compilations':1,'expected_invalid_syntax_program_compilations':1,'hard_gates':'Native0,exactsealed candidatePTX,allfallback/assertions,exact actualmodulepaths enforced,new13success marker exactly1. Expected syntax/NUL declines are negative controls. Report postclose modulepresence asactualcost risk,not zerocost inference. Any unexpected API/numerical mismatch closes this helperform without source/flag/arch/version/corpus rescue. Mechanical adapter failures preserve originals andneedreview.','scope':'One Rustcompile andone runtime API process with real absolute DLLs/owned program/destroy/close,actualdrivercontext,no application kernels orsolver. Module not integrated into productioncache yet;privatefallback source/cfg/Cargo/loader/resource andfresh speedqualification remain. No elapsed speed samples oracceptedgain.'})
h.custody();print(h.sha(H/'protocol.json'),flush=True)
