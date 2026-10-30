import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();old=ROOT/'runs/D174-budget-error-cost';assert not(old/'execution').exists()
h.save(old/'failure.json',{'at':h.now(),'status':'static_adapter_type_error_found_before_first_compiler_or_native','reason':'FIXTURES is a by-value array; rake loop binding is f64, not a reference. Remove one erroneous dereference in test adapter only.','original_protocol_sha256':h.sha(old/'protocol.json'),'original_inputs_preserved':True,'optimization_source_unchanged':True,'native_or_compiler_runs':0})
tail=(ROOT/'runs/D174-tail.rs').read_text(encoding='utf-8');assert tail.count('config.tree.rake_pct=*rake;')==1;fixed=tail.replace('config.tree.rake_pct=*rake;','config.tree.rake_pct=rake;',1);assert fixed.replace('config.tree.rake_pct=rake;','config.tree.rake_pct=*rake;',1)==tail
for name,text in [('D174-tail-r2.rs',fixed),('D174-execute-r2.py',(ROOT/'runs/D174-execute.py').read_text(encoding='utf-8').replace("ROOT/'runs/D174-budget-error-cost'","ROOT/'runs/D174-budget-error-cost-r2'").replace('D174-assess.py','D174-assess-r2.py')),('D174-assess-r2.py',(ROOT/'runs/D174-assess.py').read_text(encoding='utf-8').replace("H=ROOT/'runs/D174-budget-error-cost'","H=ROOT/'runs/D174-budget-error-cost-r2'",1))]:
 p=ROOT/'runs'/name;assert not p.exists()
 if p.suffix=='.py':compile(text,str(p),'exec')
 p.write_text(text,encoding='utf-8',newline='\n')
prep=(ROOT/'runs/D174-prepare.py').read_text(encoding='utf-8').replace("H=ROOT/'runs/D174-budget-error-cost'","H=ROOT/'runs/D174-budget-error-cost-r2'",1).replace('D174-tail.rs','D174-tail-r2.rs').replace('D174-execute.py','D174-execute-r2.py').replace('D174-assess.py','D174-assess-r2.py').replace("s['experiments'].append({'id':'D174'","next(x for x in s['experiments'] if x['id']=='D174').update({'id':'D174'",1)
compile(prep,'D174-prepare-r2.py','exec');p=ROOT/'runs/D174-prepare-r2.py';assert not p.exists();p.write_text(prep,encoding='utf-8',newline='\n');print(str(p),flush=True)
