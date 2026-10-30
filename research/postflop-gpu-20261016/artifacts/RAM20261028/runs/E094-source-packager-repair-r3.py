import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();old=ROOT/'runs/E094-stage-source-r2.py';source=old.read_text(encoding='utf-8')
h.save(ROOT/'runs/E094-source-r2/failure.json',{'at':h.now(),'status':'packager_failed_before_source_activation_compiler_or_protocol','error':'LF return-n anchor occurs in both spot_owned and observed_metadata; require unique following function boundary','original_script_sha256':h.sha(old),'partial_off_tree_files_retained':True,'native_or_compiler_children':0})
a="b'    n\\n}',b'    n+g.d_node_data_off.bytes()\\n}'";b="b'    n\\n}\\n\\npub fn stored_capacity_plan',b'    n+g.d_node_data_off.bytes()\\n}\\n\\npub fn stored_capacity_plan'"
assert source.count(a)==1
fixed=source.replace("H=ROOT/'runs/E094-source-r2';","H=ROOT/'runs/E094-source-r3';",1).replace(a,b,1)
assert fixed.replace("H=ROOT/'runs/E094-source-r3';","H=ROOT/'runs/E094-source-r2';",1).replace(b,a,1)==source
original=(h.REPO/'crates/solver/src/gpu/continuation_capacity.rs').read_bytes();assert original.count(b'    n\n}\n\npub fn stored_capacity_plan')==1
compile(fixed,'E094-stage-source-r3.py','exec');new=ROOT/'runs/E094-stage-source-r3.py';assert not new.exists();new.write_text(fixed,encoding='utf-8',newline='\n')
print(str(new),flush=True)
