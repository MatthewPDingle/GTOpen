import ast,shutil,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());B=ROOT/'runs/E109-direct-batch';P=h.read(B/'protocol.json')
for stage in P['stages']:
 H=Path(stage['folder']);assert not(H/'execution').exists() and not(H/'probe.exe').exists() and not(H/'output').exists()
source=(ROOT/'runs/E109-run-direct-batch.py').read_bytes().decode('utf-8')
old="H=Path(x['folder']);q=h.read(H/'protocol.json');O=H/'execution';raw=Path(q['raw_output']);"
new="""H=Path(x['folder']);q=h.read(H/'protocol.json');O=H/'execution';raw=Path(q['raw_output']);
  if q['family']=='fold':q.update(marker='D235_FOLD_UNIT ',native_environment={'D235_FOLD_KERNEL_CONTROL_DIR':str(raw)})
  if q['family']=='chance':q['report']=str(ROOT/'comparisons/D234-kernel-control/report.json')
  """
assert source.count(old)==1;source=source.replace(old,new,1)
old="verify();text=(O/'probe.stdout.log').read_text(encoding='utf-8');"
new="""verify()
  if q['family']=='fold':
   assert not(H/'probe.stdout.log').exists();shutil.copyfile(O/'probe.stdout.log',H/'probe.stdout.log');h.pin(H/'probe.stdout.log',h.sha(O/'probe.stdout.log'))
  text=(O/'probe.stdout.log').read_text(encoding='utf-8');"""
assert source.count(old)==1;source=source.replace(old,new,1)
ast.parse(source);out=ROOT/'runs/E109-run-direct-batch-r2.py';assert not out.exists();out.write_bytes(source.encode('utf-8'))
h.save(B/'execution-adapter.json',{'at':h.now(),'status':'PRE_FIRST_COMPILER_NATIVE_METADATA_CORRECTION','original_protocol_sha256':h.sha(B/'protocol.json'),'new_executor_sha256':h.sha(out),'corrections':['Fold marker is D235_FOLD_UNIT, not D235_RAW; read from actual frozen probe.','Fold probe requires D235_FOLD_KERNEL_CONTROL_DIR, not argv; set original specified raw directory.','Chance original auditor writes comparisons/D234-kernel-control/report.json.','Fold original auditor expects stdout next to raw directory; provide byte-verified copy of terminal native stdout at that path.'],'scientific_inputs_unchanged':True,'original_source_corpus_PTX_compiler_arguments_native_arguments_readers_unchanged':True,'native_or_compiler_executions_before_repair':0,'scope':'Execution metadata adapters only. All frozen original artifacts and future full numerical gates retained. No data cases or source optimization changes.'})
print(h.sha(B/'protocol.json'),flush=True)
