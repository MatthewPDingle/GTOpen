import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();old=ROOT/'runs/E094-stage-source.py';source=old.read_text(encoding='utf-8')
h.save(ROOT/'runs/E094-source/failure.json',{'at':h.now(),'status':'packager_failed_before_source_activation_compiler_or_protocol','error':'continuation_capacity.rs uses LF, while packager return-n anchor assumed CRLF','original_script_sha256':h.sha(old),'partial_off_tree_files_retained':True,'native_or_compiler_children':0})
fixed=source.replace("H=ROOT/'runs/E094-source';","H=ROOT/'runs/E094-source-r2';",1).replace("b'    n\\r\\n}',b'    n+g.d_node_data_off.bytes()\\r\\n}'","b'    n\\n}',b'    n+g.d_node_data_off.bytes()\\n}'",1)
assert fixed!=source and fixed.replace("H=ROOT/'runs/E094-source-r2';","H=ROOT/'runs/E094-source';",1).replace("b'    n\\n}',b'    n+g.d_node_data_off.bytes()\\n}'","b'    n\\r\\n}',b'    n+g.d_node_data_off.bytes()\\r\\n}'",1)==source
compile(fixed,'E094-stage-source-r2.py','exec');new=ROOT/'runs/E094-stage-source-r2.py';assert not new.exists();new.write_text(fixed,encoding='utf-8',newline='\n')
print(str(new),flush=True)
