"""Additive extra-path classifier correction; no completed GPU cases repeated."""
import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists()
H=ROOT/'runs/D271-metadata-engine';old=H/'audit.py'
for label,code in [('rustc',0),('probe',0),('audit',1)]:assert h.read(H/'execution'/(label+'.exit.json'))['returncode']==code
assert 'all extra actual66 constructor fields' in(H/'execution/audit.stderr.log').read_text(encoding='utf-8')
assert not(ROOT/'comparisons/D271-metadata-engine').exists()
text=old.read_text(encoding='utf-8')
before="    if path.parent.parent.name=='extra':return D271_MAPS[(1,73+int(path.parent.name))]"
after="    if path.parent.parent.name=='extra':return D271_MAPS[(1,73+int(path.parent.name))] if path.name.startswith('clobbered-') else None"
assert text.count(before)==1;text=text.replace(before,after,1)
before="for p, digest in P['input_sha256'].items(): h.pin(p,digest)"
after=before+"\nassert len(sys.argv)==2\nh.pin(H/'reader-repair-protocol.json',sys.argv[1]);R=h.read(H/'reader-repair-protocol.json')\nfor p,digest in R['input_sha256'].items():h.pin(p,digest)"
assert text.count(before)==1;text=text.replace(before,after,1)
text=text.replace("'id':'D271', 'at':h.now(),", "'id':'D271', 'at':h.now(), 'reader_repair_protocol_sha256':sys.argv[1], 'original_failed_reader_preserved':True, 'completed_native_GPU_cases_repeated':0,",1)
ast.parse(text);dest=H/'audit-r2.py'
with dest.open('x',encoding='utf-8',newline='\n')as f:f.write(text)
runner=ROOT/'runs/D271-execute-reader-repair.py';ast.parse(runner.read_text(encoding='utf-8'))
paths=[Path(__file__),runner,old,dest,H/'protocol.json',H/'source-review.json',H/'execution/rustc.exit.json',H/'execution/probe.exit.json',H/'execution/probe.stdout.log',H/'execution/audit.exit.json',H/'execution/audit.stdout.log',H/'execution/audit.stderr.log',H/'execution/binary.json',H/'output/metadata.json',H/'output/extra-metadata.json']
h.save(H/'reader-repair-protocol.json',{'id':'D271-reader-repair','at':h.now(),'status':'FROZEN_PRE_READ_ONLY_COMPLETE_REPLAY','input_sha256':{str(p):h.sha(p)for p in paths},'original_protocol_sha256':h.sha(H/'protocol.json'),'error_evidence':'All original36/752phases/324EV/32changingroots and all6extra/30phases/54EV actual native GPU cases completed exactly. Original reader independently replayed all156 maps/complete plans/kinds and all original3528raw frames before failing extra constructor field comparison. Its extra-directory path classifier erroneously applied candidate map to baseline files as well. Whole extra constructor byte inverse comparison already passed; field decoder baseline misclassification caused failure.',
 'single_read_only_correction':'In extra directories, return candidate map only when actual filename starts clobbered-; baseline filenames remain literal original data. Core path logic unchanged. All arrays/header/fullbyte/physicalCFV/CPU/case/count/flag/category/graph/negativebit assertions retained, no tolerance/omission/threshold/count/source/fixture/predicate/CUDA/native output changes.',
 'native_cases_repeated':0,'new_compiler_GPU_kernel_solver_speed_samples':0,'scope':'One repaired Python full reader, all original and extra raw files. Preserve original failed reader/log/exit. Source unchanged; no genuine numerical failure rescued. All original fullcanonical/ordinary/full1%/strictfixture/fresh16/broad/material/holdout/cumulative/app gates remain.'})
print(h.sha(H/'reader-repair-protocol.json'),flush=True)
