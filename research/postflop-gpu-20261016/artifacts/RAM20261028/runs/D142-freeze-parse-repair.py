import sys,json,shutil,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D142-profile-plan';p=ROOT/'runs/D142-execute.py';old=ROOT/'runs/D142-execute-before-parse-review.py';compile(p.read_text(),str(p),'exec')
original=old.read_text();assert p.read_text()==original.replace("P=h.read(H/'protocol.json')","P=h.read(H/'protocol-r2.json')").replace("h.pin(H/'protocol.json',sys.argv[1])","h.pin(H/'protocol-r2.json',sys.argv[1])").replace("'river'else201","'river' else 201")
h.custody();assert not(ROOT/'runs/D142R1').exists()and not(ROOT/'runs/D142-profile-execution').exists();P=h.read(H/'protocol.json')
P.update(at=h.now(),revision=2,supersedes_protocol_sha256=h.sha(H/'protocol.json'),pre_native_adapter_repair='Python parser found missing whitespace in a conditional expression. Preserve original code/protocol; fix syntax and bind this new protocol. No scientific change, native/compilation/profile process or sample yet.')
P['input_sha256'][str(p)]=h.sha(p)
for x in[old,H/'protocol.json',Path(__file__)]:P['input_sha256'][str(x)]=h.sha(x)
h.save(H/'protocol-r2.json',P);h.save(H/'parse-review.json',{'at':h.now(),'original_source_sha256':h.sha(old),'original_protocol_sha256':h.sha(H/'protocol.json'),'revised_source_sha256':h.sha(p),'revised_protocol_sha256':h.sha(H/'protocol-r2.json'),'parse_error':"SyntaxError: expected else after if expression; line18: else201",'native_or_compiler_children_started':0,'scientific_inputs_sequence_gates_changed':False})
for x in[H/'protocol-r2.json',H/'parse-review.json']:
 key=H.name+'/'+x.name;dst=h.ar.DASHBOARD/'evidence'/key;assert not dst.exists();shutil.copyfile(x,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20)as z:assert z.read()==x.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);x=next(x for x in s['experiments']if x['id']=='D142');x['evidence'].append({'label':'Pre-native syntax repair and revised protocol','url':'evidence/D142-profile-plan/protocol-r2.json'});s['updated_at']=h.now();h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol-r2.json'),flush=True)
