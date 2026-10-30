import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists()
parent=ROOT/'runs/D226-prepare-canonical.py';source=parent.read_bytes().decode('utf-8').replace('D226','D237').replace('E108','E109').replace('chunk-division-canonical','stride-canonical').replace('Chunk division-load','Unsigned stride').replace('Chunk division','Unsigned stride').replace('chunk-division','unsigned-stride').replace('chunk binding','stride scalar typing').replace('Chunk integer','Stride integer')
a=source.index('direct=');b=source.index('parent=',a)
new="""direct=ROOT/'comparisons/D236-stride-eval-root-check/report.json'
assert h.read(direct)['cases']==1638 and h.read(direct)['kernel_launches']==3276
assert h.read(ROOT/'runs/E109-direct-batch/report.json')['cases']==1604
assert h.read(ROOT/'comparisons/D232-kernel-control-root-check/report.json')['inventory']['comparison_pairs']==7640
for group in ['D233-stride-up-action','D234-stride-chance','D235-stride-fold','D236-stride-eval']:
 for label in ['rustc','probe','audit']:
  r=h.read(ROOT/'runs'/group/'execution'/(label+'.exit.json'));assert r['returncode']==0 and r['error']is r['cleanup']is None
"""
source=source[:a]+new+source[b:]
source=source.replace("ROOT/'runs/D225-chunk-native-bypass/report.json'","ROOT/'runs/D230-native-stride/report.json'").replace("ROOT/'runs/E109-kernel-control/protocol.json'","ROOT/'runs/D232-stride-showdown/protocol.json'").replace("ROOT/'runs/E109-kernel-control/execution/complete.json'","ROOT/'runs/D232-stride-showdown/execution/complete.json'").replace("ROOT/'runs/E109-direct-audit/audit.exit.json'","ROOT/'runs/D232-stride-showdown-audit/audit.exit.json'")
source=source.replace('Only guarded integer stride scalar typing differs.','Only six nonnegative stride scalar declarations differ; original64bit address products retained.').replace('7640directpairs/15280launches passed.','10882directpairs/21764launches across allfive affected entries passed.').replace('7640directpairs passed','10882directpairs passed').replace('all764 exceptional/physical cases at10widths including nonpower fallback, all21actualinputs and physicaloutputs/guards','showdown7640,uptraining819,chance425,fold360,eval1638pairs, allactualimmutableinputs/fullphysicaloutputs andguards').replace('source/if/ternary/helper/flags/entry subset/threshold/quality/sample','source/width/helper/flags/entry subset/threshold/quality/sample')
assert 'E108'not in source and 'D226'not in source and 'D225'not in source
ast.parse(source);out=ROOT/'runs/D237-prepare-canonical.py';assert not out.exists();out.write_bytes(source.encode('utf-8'));h.save(ROOT/'runs/D237-preparer-lineage.json',{'at':h.now(),'parent':str(parent),'parent_sha256':h.sha(parent),'adapted_sha256':h.sha(out),'scope':'Same full canonical harness/reader/state/quality/resources. Only candidate IDs, sealed source/PTX and allfive-entry direct prerequisites changed; no data/corpus/quality/gate relaxation.'})
