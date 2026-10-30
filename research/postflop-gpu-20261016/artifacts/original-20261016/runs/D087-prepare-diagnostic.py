"""Derive the copied evaluator hooks from the frozen primary source."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D087-cupti-driver-profile';prior=ROOT/'runs/D085-cupti-activity'
s=(prior/'prepare-diagnostic-build.py').read_text(encoding='utf-8').replace('D085','D087').replace("H/'build-r3'","H/'build'")
s=s.replace('fn D087StartTrace()->u32;','fn D087StartTrace()->u32; fn D087PhaseTrace(marker:u32)->u32;')
needle="(H/'evaluator.rs').write_text(source,encoding='utf-8',newline='\\n');"
assert s.count(needle)==1
extra='''# Six diagnostic phase brackets; every benchmark arithmetic/stop path stays exact.
for before,after in [
 ('        let mut gpu = GpuSolver::new(&host)', '        assert_eq!(unsafe{D087PhaseTrace(1)},1,"phase init begin");\\n        let mut gpu = GpuSolver::new(&host)'),
 ('        let gpu_init_ms = elapsed_ms(stage_start);', '        assert_eq!(unsafe{D087PhaseTrace(2)},1,"phase init end");\\n        let gpu_init_ms = elapsed_ms(stage_start);'),
 ('        let solve_start = Instant::now();', '        let solve_start = Instant::now();\\n        assert_eq!(unsafe{D087PhaseTrace(3)},1,"phase solve begin");'),
 ('        let solve_checks_ms = elapsed_ms(solve_start);', '        assert_eq!(unsafe{D087PhaseTrace(4)},1,"phase solve end");\\n        let solve_checks_ms = elapsed_ms(solve_start);'),
 ('        gpu.sync_to_cpu(&mut host).unwrap();', '        assert_eq!(unsafe{D087PhaseTrace(5)},1,"phase readback begin");\\n        gpu.sync_to_cpu(&mut host).unwrap();'),
 ('        let full_readback_ms = elapsed_ms(stage_start);', '        assert_eq!(unsafe{D087PhaseTrace(6)},1,"phase readback end");\\n        let full_readback_ms = elapsed_ms(stage_start);')
]:
 assert source.count(before)==1,before
 source=source.replace(before,after)
'''
s=s.replace(needle,extra+needle)
s=s.replace('same frozen evaluator with only explicit collector lifetime hooks, fixed diagnostic restriction','same frozen evaluator with only explicit collector lifetime hooks, six timestamp phase brackets, fixed diagnostic restriction')
s=s.replace('d085_rainbow_trace','d087_rainbow_trace')
assert "H/'build-r3'" not in s
(H/'prepare-diagnostic-build.py').write_text(s,encoding='utf-8',newline='\n')
(H/'build-diagnostic.py').write_text((prior/'build-diagnostic.py').read_text(encoding='utf-8').replace('D085','D087'),encoding='utf-8',newline='\n')
print('D087 diagnostic derivation script prepared; evaluator not yet built.',flush=True)
