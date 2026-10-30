"""Complete the standalone unit harness before either planned compiler runs."""
from pathlib import Path
import ast,shutil,sys,urllib.request
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');C=R/'runs/accepted-E051-live-20261018';sys.path.insert(0,str(C));import common_e051_live as old
H=R/'runs/E076-plan-control';old.custody();assert not (H/'build').exists() and not (H/'execution').exists()
P=old.read(H/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
source=H/'probe.rs';before=old.sha(source);text=source.read_text(encoding='utf-8')
assert text.count('pub use solver::{cards,cfr,evaluator,range,store,tree};')==1
shutil.copyfile(source,H/'original-probe.rs')
text=text.replace('pub use solver::{cards,cfr,evaluator,range,store,tree};','pub use solver::{cards,cfr,evaluator,range,store,tree,parse_sizes,StreetSizing,TreeConfig};\npub use game::SpotConfig;')
source.write_text(text,encoding='utf-8',newline='\n')
execute=(H/'execute.py').read_text(encoding='utf-8').replace("H/'protocol.json'","H/'protocol-r2.json'")
ast.parse(execute);(H/'execute-r2.py').write_text(execute,encoding='utf-8',newline='\n')
old.save(H/'precompile-amendment.json',{'at':old.now(),'original_protocol_sha256':old.sha(H/'protocol.json'),'original_harness_sha256':before,'completed_harness_sha256':old.sha(source),'reason':'Source review found the standalone --test harness needs crate-root SpotConfig, parse_sizes, StreetSizing and TreeConfig reexports used by both preexisting plan unit modules. Added only those imports before any compiler/native execution. Original protocol/harness retained. Candidate/source/map/case/order/criteria unchanged.','compiler_executions':0,'native_executions':0,'source_candidate_unchanged':True})
P.update(at=old.now(),supersedes_unexecuted_protocol_sha256=old.sha(H/'protocol.json'),amendment=str(H/'precompile-amendment.json'))
P['input_sha256'][str(source)]=old.sha(source)
for p in [Path(__file__),H/'execute-r2.py',H/'precompile-amendment.json',H/'original-probe.rs',H/'protocol.json']:P['input_sha256'][str(p)]=old.sha(p)
old.save(H/'protocol-r2.json',P)
for p in [source,H/'execute-r2.py',H/'precompile-amendment.json',H/'original-probe.rs',H/'protocol-r2.json']:
 key=H.name+'/'+('completed-probe.rs'if p==source else p.name);dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(old.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=15)as r:assert r.read()==p.read_bytes()
old.custody();print('E076 completed unit harness protocol',old.sha(H/'protocol-r2.json'),flush=True)
