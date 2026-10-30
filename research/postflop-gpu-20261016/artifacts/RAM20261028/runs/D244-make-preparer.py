import ast,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();parent=ROOT/'runs/D226-prepare-canonical.py';source=parent.read_bytes().decode('utf-8').replace('D226','D244').replace('E108','E110').replace('chunk-division-canonical','fold-copy-canonical').replace('Chunk division-load','Fold copy/partial').replace('Chunk division','Fold copy/partial').replace('chunk-division','fold-copy-partial').replace('guarded integer chunk binding','same-thread fold copy/partial fusion')
a=source.index('direct=');b=source.index('parent=',a)
source=source[:a]+"""direct=ROOT/'comparisons/D243-fold-copy-direct/report.json';q=h.read(direct);assert q['cases']==360 and q['kernel_launches']==720 and q['full_raw_files_equal']
engine=ROOT/'comparisons/D242-fold-copy-engine/report.json';assert h.read(engine)['cases']==36 and h.read(engine)['status']=='pass_scoped_fold_copy_engine_raw_lifecycle_equivalence'
for group in ['D243-fold-copy-direct','D242-fold-copy-engine']:
 for label in ['rustc','probe','audit']:
  r=h.read(ROOT/'runs'/group/'execution'/(label+'.exit.json'));assert r['returncode']==0 and r['error']is r['cleanup']is None
"""+source[b:]
source=source.replace("ROOT/'runs/D225-chunk-native-bypass/report.json'","ROOT/'runs/D241-native-fold-copy/report.json'").replace("ROOT/'runs/E110-kernel-control/protocol.json'","ROOT/'runs/D243-fold-copy-direct/protocol.json'").replace("ROOT/'runs/E110-kernel-control/execution/complete.json'","ROOT/'runs/D243-fold-copy-direct/execution/complete.json'").replace("ROOT/'runs/E110-direct-audit/audit.exit.json'","ROOT/'runs/D243-fold-copy-direct/execution/audit.exit.json'")
source=source.replace(",direct,ROOT/'runs/D243",",direct,engine,ROOT/'runs/D243",1).replace('7640directpairs/15280launches','360directpairs/720launches plus36enginecases').replace('7640directpairs_all_outputs_inputs_guards_exact','360foldpairs_and36enginecases_exact').replace('All7640directpairs passed includingall764 exceptional/physical cases at10widths including nonpower fallback, all21actualinputs and physicaloutputs/guards.','All360foldpairs passed, originalexceptional/empty/count/menu/threadscorpus,14actualimmutableinputs/wholephysicaloutputs/guards. Original36enginecases passed.').replace('source/if/ternary/helper/flags/entry subset/threshold/quality/sample','source/order/loop/width/helper/flags/entry subset/threshold/quality/sample')
old='assert not dst.exists();shutil.copyfile(p,dst)';assert source.count(old)==1;source=source.replace(old,"\n  if dst.exists():assert dst.read_bytes()==p.read_bytes()\n  else:shutil.copyfile(p,dst)",1)
assert 'E108'not in source and 'D226'not in source and 'D225'not in source
ast.parse(source);out=ROOT/'runs/D244-prepare-canonical.py';assert not out.exists();out.write_bytes(source.encode('utf-8'));h.save(ROOT/'runs/D244-preparer-lineage.json',{'at':h.now(),'parent':str(parent),'parent_sha256':h.sha(parent),'adapted_sha256':h.sha(out),'scope':'Exact originalcanonical host/observers/reader/quality/workloads/resources. E110sealedPTX/source andcompletefold/engine prerequisites; samefields andentirephysicalCFV equality, noneexcluded.'})
