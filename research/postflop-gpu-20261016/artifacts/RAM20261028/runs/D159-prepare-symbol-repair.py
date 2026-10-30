import sys,shutil,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/D159-vectorization-resource';P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
h.custody();assert not (ROOT/'gpu-run.lock').exists()
assert h.read(H/'execution/rustc.exit.json')['returncode']==0 and h.read(H/'execution/probe.exit.json')['returncode']==101
assert not (H/'execution/candidate-compute_120.ptx').exists()
log=(H/'execution/probe.stdout.log').read_text(encoding='utf-8')
import json
oldrows=[json.loads(x.split('D159_RESOURCE ',1)[1]) for x in log.splitlines() if x.startswith('D159_RESOURCE ')]
assert len(oldrows)==7 and all(x['variant']=='baseline' and x['kernel_launches']==0 for x in oldrows)
R=ROOT/'runs/D159R2-vectorization-resource';R.mkdir(exist_ok=False)
src=(H/'probe.rs').read_text(encoding='utf-8')
assert src.count('"up_action_opponent"')==1
src=src.replace('"up_action_opponent"','"copy_span"',1)
src=src.replace('CompileOptions}};','CompileOptions,Ptx}};',1)
needle='let ptx=compile_ptx_with_opts(include_str!("kernels.cu"),CompileOptions{arch:Some(arch),options,..Default::default()}).unwrap();'
replacement='let ptx=if arch=="compute_120" && variant=="baseline" {Ptx::from_src(include_str!("retained-baseline-compute_120.ptx"))} else {compile_ptx_with_opts(include_str!("kernels.cu"),CompileOptions{arch:Some(arch),options,..Default::default()}).unwrap()};'
assert src.count(needle)==1;src=src.replace(needle,replacement,1).replace('"compilations":4','"compilations":3,"retained_PTX_inputs":1',1)
(R/'probe.rs').write_bytes(src.encode());shutil.copyfile(H/'kernels.cu',R/'kernels.cu')
retained=H/'execution/baseline-compute_120.ptx';h.pin(retained,h.read(ROOT/'runs/E091-resource/report.json')['ptx_sha256']['baseline-compute_120'])
shutil.copyfile(retained,R/'retained-baseline-compute_120.ptx')
execute=(H/'execute.py').read_text(encoding='utf-8')
execute=execute.replace("markers[-1]['kernel_launches']==0","markers[-1]['kernel_launches']==0 and markers[-1]['compilations']==3 and markers[-1]['retained_PTX_inputs']==1",1)
execute=execute.replace("D=ROOT/'comparisons/D159-vectorization-resource'","D=ROOT/'comparisons/D159R2-vectorization-resource'",1)
execute=execute.replace("'id':'D159','at':h.now()","'id':'D159R2','at':h.now(),'original_D159_probe_remains_failed_baseline_setup':True,'retained_baseline_PTX_reused':True,'total_main_compilations_across_R1_R2':4",1)
needle="passed=all(gates.values());D="
replacement="""old=h.read(H/'repair-review.json')['original_baseline_resource_rows']
for row in old:
    now=rows['baseline',row['kernel']]
    gates['retained_baseline:'+row['kernel']+':resource_requery_exact']=row==now
gates['retained_baseline:PTX_exact']=(O/'baseline-compute_120.ptx').read_bytes()==(H/'retained-baseline-compute_120.ptx').read_bytes()
passed=all(gates.values());D="""
assert execute.count(needle)==1;execute=execute.replace(needle,replacement,1)
(R/'execute.py').write_bytes(execute.encode());compile(execute,str(R/'execute.py'),'exec')
h.save(R/'repair-review.json',{'at':h.now(),'status':'mechanical_pre_candidate_symbol_adapter_repair','original_protocol_sha256':h.sha(H/'protocol.json'),'original_rustc_exit':0,'original_probe_exit':101,'original_baseline_resource_rows':oldrows,'original_candidate_compilations_or_kernel_launches':0,'error':'Probe asked for obsolete up_action_opponent; accepted/source-bound canonical entry is copy_span. Original expected_entries already correctly listed copy_span.','repair':'Change only hardcoded symbol string to canonical copy_span. Reuse original already-compiled baseline120 PTX exactly; run remaining three originally required NVRTC compiles once. Requery baseline resources and require all7prior read-only rows exact. Resource/ABI/mechanism/source/flag/architecture/gates unchanged. Preserve all R1 files/failed status,do not pool or regrade it.','scope':'No application/numerical/performance observation exists to rescue. Candidate option first compilation occurs only after this repair is frozen. Additional Rust compiler and read-only baseline driver queries disclosed; total NVRTC program variants remain original4.'})
command=list(P['rustc_command']);command=[x.replace(str(H),str(R)) for x in command]
files=[Path(__file__),H/'protocol.json',H/'probe.rs',H/'execute.py',H/'execution/probe.stdout.log',H/'execution/probe.stderr.log',H/'execution/probe.exit.json',retained,ROOT/'runs/E091-resource/report.json']+[p for p in R.iterdir() if p.is_file()]
inputs={**P['input_sha256'],**{str(p):h.sha(p) for p in files}}
h.save(R/'protocol.json',{**P,'id':'D159R2','at':h.now(),'status':'FROZEN_PRE_REPAIRED_COMPILER_AND_FIRST_CANDIDATE_COMPILE','rustc_command':command,'input_sha256':inputs,'original_D159_status':'invalid_baseline_symbol_setup_preserved','scope':'Original one-option/source/arch/ABI/resource/mechanism gates retained. R1baseline PTX reused and all7read-only rows must match; one repaired Rust compiler and three remaining NVRTC compiles. First candidate compilation only now. No app kernels,solver,numerical or timing samples;no source/option/gate/shape rescue after actual candidate result.'})
h.custody();print(h.sha(R/'protocol.json'),flush=True)
