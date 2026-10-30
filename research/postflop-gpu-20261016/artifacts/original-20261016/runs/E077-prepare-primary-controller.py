"""Prepare, but do not freeze or run, the next fixed whole-solve screen."""
from pathlib import Path
import re
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');p=R/'runs/E077-freeze-run-publish.py';assert not p.exists()
s=(R/'runs/E076-freeze-run-publish.py').read_text(encoding='utf-8').replace('E076','E077').replace('e076','e077').replace('V076','V077').replace('B241','B244').replace('B242','B245').replace('B243','B246')
s=s.replace('pass_scoped_full_in_place_CFV_raw_equivalence','pass_scoped_full_selective_prefix_raw_equivalence').replace("control['cases']==819 and control['alias_cases']==138 and control['application_kernel_launches']==1638","control['cases']==1820 and control['application_kernel_launches']==3640")
a=s.index("for name in ['native.py','assess.py','root-check.py','run.py']:");b=s.index("source=old.read(",a)
s=s[:a]+'''for name in ['native.py','assess.py','root-check.py','run.py']:
 code=(R/'runs/E076-primary-plan'/name).read_text(encoding='utf-8').replace('E076','E077').replace('e076','e077').replace('pass_scoped_full_in_place_CFV_raw_equivalence','pass_scoped_full_selective_prefix_raw_equivalence').replace("control['cases']==819","control['cases']==1820").replace("control['application_kernel_launches']==1638","control['application_kernel_launches']==3640")
 if name=='native.py':code=re.sub(r'\\b84\\b','85',code)
 code=code.replace('exact one-source scope','exact three-source scope')
 compile(code,str(H/name),'exec');(H/name).write_text(code,encoding='utf-8',newline='\\n')
'''+s[b:]
s=s.replace('import json,shutil,subprocess,sys,urllib.request','import json,re,shutil,subprocess,sys,urllib.request')
s=s.replace("R/'runs/E075-primary-plan/protocol.json'","R/'runs/E076-primary-plan/protocol.json'")
scope=' All12 compiled tag arrays match independently frozen D124 maps; all52 other fields/capacities/structs exact and3 plan tests pass.1820 full raw GPU pairs/3640 launches across5 widths preserve whole outputs, expected input images and guards. CPU in-place tagging loops, NVRTC/JIT, all GPU setup/quality solves/full readback remain inside complete clocks. No full-solve speed or broad/material result yet.'
s,n=re.subn(r"source_scope=source\['source_scope'\]\+'[^']+'",'source_scope=source[\'source_scope\']+'+repr(scope),s,count=1);assert n==1
s=s.replace('D122-cfv-lifetimes','D124-prefix-liveness')
needle="st=old.read(old.ar.STATUS)";assert s.count(needle)==1
s=s.replace(needle,"paths.extend([R/'runs/E077-source/candidate.cu',R/'runs/E077-source/candidate-mod.rs',R/'runs/D125-index-address-audit/report.json',R/'runs/D125-index-address-audit/protocol.json'])\n"+needle)
s=s.replace('84 ordinary tests','85 ordinary tests').replace('Run84 ordinary tests','Run85 ordinary tests').replace('84 ordinary tests','85 ordinary tests').replace("'ordinary_units_passed':84","'ordinary_units_passed':85")
s=s.replace('819 direct GPU pairs','1820 direct GPU pairs').replace("'direct_GPU_cases':819,'direct_GPU_alias_cases':138,'direct_GPU_launches':1638","'direct_GPU_cases':1820,'direct_GPU_launches':3640")
s=s.replace('CPU layout/coloring costs','CPU in-place tagging costs').replace('All CPU layout costs included.','All CPU tagging costs included.').replace('CFV row sharing','selective prefix materialization').replace('CFV lifetime-sharing','selective prefix materialization')
s=s.replace('12 metadata cases and819 raw GPU pairs passed.','12 metadata cases and1820 raw GPU pairs passed.')
s=s.replace('All18 full non-timing results,138 checkpoints,84 ordinary tests,12 CPU metadata cases and819 direct GPU pairs passed.','All18 full non-timing results,138 checkpoints,85 ordinary tests,12 CPU metadata cases and1820 direct GPU pairs passed.')
s=s.replace('No extra samples, layout/source/placement variants or rescue.','No extra samples, flag/map/mask/guard/helper/source/width/placement variants or rescue.')
a=s.index('The sole D122-admitted original-schedule Rust allocator,');b=s.index('\n\nTwo fresh isolated',a)
s=s[:a]+'''The exact3-file selective prefix-materialization source remains frozen: {json.dumps(P['candidate_owned_sha256'],separators=(',',':'))}. D124's retained-data demand analysis found84–86% weighted unused shared-prefix cells in canonical flops, a structural opportunity only. The kernel masks original hand indices from in-place bit31 tags and suppresses only unread prefix stores/dead offset additions; original live arithmetic/ordered chunk recurrences/barriers/output spans remain. Same public plan build, ABI27, arrays/bytes, launch/graph, save and quality settings. CPU tagging stays inside the constructor clock. E077 original resource literal-mask proxy failure and D125 immutable-PTX address-semantic repair retained, no resource rerun/source change. All12 compiled host tag maps and52 other field/capacity/struct values exact,3 plan tests pass. Original Python reader type-error and corrected iterator replay retained; no compiler/test/case00 native repeat.1820 direct GPU pairs/3640 launches across5 widths:8,436,520 full output words,15,329,720 actual immutable words and6,464,120 guards exact. Root decoder is not external independence. No material or complete-cycle conclusion from scoped source/controls.'''+s[b:]
s=s.replace('V077-unit84 passed/4 ignored','V077-unit85 passed/4 ignored')
assert not any(x in s for x in ['D122','E075','alias_cases','direct_GPU_alias_cases','CFV row','CFV lifetime','819 direct','ordinary_units_passed\':84'])
compile(s,str(p),'exec');p.write_text(s,encoding='utf-8',newline='\n')
print('E077 primary controller prepared/syntax checked only: V077-unit85 expected; fixed B244/E077R1,E077R2/B245,B246/E077R3. No primary IDs frozen/run yet.',flush=True)
