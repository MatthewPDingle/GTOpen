import sys,ast,re
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');p=R/'runs/E089-freeze-primary.py';assert not p.exists()
t=(R/'runs/E087-freeze-primary.py').read_text(encoding='utf-8').replace('E087','E089').replace('B287','B290').replace('B288','B291').replace('B289','B292')
t=t.replace("comparisons/E089-transfer-control/report.json","comparisons/E089-kernel-control-root-check/report.json").replace("runs/E089-transfer-control/","runs/E089-kernel-control/")
before="assert q['status']=='pass_raw_GPU_controls' and q['full_file_pairs_exact']==808 and q['all_complete_files_compared_in_full']"
after="assert q['status']=='pass_scoped_full_serial_card_loop_raw_equivalence' and q['inventory']['comparison_pairs']==1820 and q['whole_physical_outputs_bitwise_equal'] and q['all21_input_buffers_identical']"
assert t.count(before)==1;t=t.replace(before,after)
predicate="assert control['status']=='pass_scoped_full_serial_card_loop_raw_equivalence' and control['inventory']['comparison_pairs']==1820 and control['whole_physical_outputs_bitwise_equal'] and control['all21_input_buffers_identical']"
t,n=re.subn(r'^predicate=.*$',lambda _: 'predicate='+repr(predicate),t,flags=re.M);assert n==1
t=t.replace("('88','0','4','0','0')","('86','0','4','0','0')").replace("'ordinary_units_passed':88","'ordinary_units_passed':86")
t=t.replace("88 ordinary","86 ordinary").replace("Run88ordinary","Run86ordinary")
t=t.replace('exact three-host-file source scope','exact one-CUDA-file source scope')
assert 'transfer-control'not in t
ast.parse(t);p.write_bytes(t.encode());print(str(p),flush=True)
