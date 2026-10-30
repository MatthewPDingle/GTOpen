"""Resolve compiler-coalesced typed paths without recompiling or changing gates."""
import json,re,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();H=ROOT/'runs/D090-wide-OR';B=H/'build';P=old.read(H/'protocol.json')
assert not list((H/'execution').iterdir()) and not (H/'compiler-gate.json').exists() and not (H/'report.json').exists()
receipt=old.read(B/'rustc.exit.json');assert receipt['returncode']==0 and receipt['error'] is receipt['cleanup'] is None
src=next(B.glob('probe.d090_probe*.s'));text=src.read_text(encoding='utf-8');portable=re.findall(r'^\s*callq\s+(\S*portable_i16\S*)$',text,re.M);wide=re.findall(r'^\s*callq\s+(\S*wide_i16\S*)$',text,re.M);assert len(portable)==len(wide)==6
a=text.index('callq\t'+portable[0]);z=text.index('jne\t.LBB48_69',a);z=text.index('jne\t.LBB48_69',z+1);z=text.index('jne\t.LBB48_69',z+1);z=text.index('jne\t.LBB48_69',z+1)+len('jne\t.LBB48_69');witness=text[a-80:z]
assert re.findall(r'callq\s+(\S+)',witness)==[portable[0],portable[0],wide[0],wide[0]] and witness.count('cmpw')==4
(H/'typed-call-witness.asm.txt').write_text(witness,encoding='utf-8',newline='\n')
old.save(H/'compiler-name-observer-failure.json',{'at':old.now(),'outer_exec_chunk_id':'5e8ffb','returncode':1,'compiler_returncode':0,'native_control_or_benchmark_executions':0,'failure':'Reader expected portable_u16 symbol or explicit .set alias. LLVM eliminated duplicate typed symbols and redirected both signed/unsigned paths to the canonical bit-identical i16 bodies.','observer_only_repair':'Resolve source typed paths through observed canonical callees. All4control calls remain and all4results independently compare. Source, compiled executable, raw matrix, benchmark order and all gates unchanged.','assembly_sha256':old.sha(src),'binary_sha256':old.sha(B/'probe.exe'),'witness_sha256':old.sha(H/'typed-call-witness.asm.txt'),'canonical_portable_calls':6,'canonical_wide_calls':6})
s=(H/'execute.py').read_text(encoding='utf-8').replace("H/'protocol.json'","H/'protocol-r2.json'").replace("E=H/'execution'","E=H/'execution-r2'")
s=s.replace('verify();assert not B.exists() and not E.exists();B.mkdir();E.mkdir()','verify();assert B.exists() and not E.exists();E.mkdir()')
s=s.replace(" old.child(P['command'],B,'rustc',old.env(),600);verify()"," old.pin(B/'probe.exe',P['compiled_binary_sha256']);assert old.read(B/'rustc.exit.json')['returncode']==0;verify()")
needle="  candidates=[n for n in sorted(set(labels)|set(aliases)) if name in n];assert candidates,(name,'missing retained helper')"
assert s.count(needle)==1
replacement="  candidates=[n for n in sorted(set(labels)|set(aliases)) if name in n]\n  coalesced=False\n  if not candidates and name.endswith('_u16'):\n   canonical=name.replace('_u16','_i16');candidates=[n for n in labels if canonical in n];coalesced=True\n   assert len(re.findall(r'^\\s*callq\\s+\\S*'+canonical+r'\\S*$',alltext,re.M))==6\n  assert candidates,(name,'missing retained typed path')"
s=s.replace(needle,replacement)
s=s.replace("  (H/(name+'.asm.txt')).write_text(body,encoding='utf-8',newline='\\n');helpers[name]=", "  path=H/(name+'.asm.txt')\n  if path.exists():assert path.read_text(encoding='utf-8')==body\n  else:path.write_text(body,encoding='utf-8',newline='\\n')\n  helpers[name]=")
s=s.replace("'alias':symbol!=resolved,","'alias':symbol!=resolved,'compiler_coalesced_typed_path':coalesced,")
(H/'execute-r2.py').write_text(s,encoding='utf-8',newline='\n')
newP=dict(P);newP.update(id='D090-wide-OR-reader-r2',at=old.now(),original_protocol_sha256=old.sha(H/'protocol.json'),compiled_binary_sha256=old.sha(B/'probe.exe'),reader_repair='Only resolve LLVMmerged typed paths via canonical function and complete four-call witness. No recompilation, helper/source/ISA change, numerical/control/sampling/25%/representativeness gate change or native result seen.')
paths=[H/'execute-r2.py',H/'protocol.json',H/'execute.py',H/'compiler-name-observer-failure.json',H/'typed-call-witness.asm.txt']+[p for p in B.iterdir() if p.is_file()]
newP['input_sha256']=dict(P['input_sha256'])|{str(p):old.sha(p) for p in paths};old.save(H/'protocol-r2.json',newP)
for src in [H/'execute-r2.py',H/'protocol-r2.json',H/'compiler-name-observer-failure.json',H/'typed-call-witness.asm.txt']:
 key=H.name+'/'+src.name;dst=old.ar.DASHBOARD/'evidence'/key;assert not dst.exists();dst.write_bytes(src.read_bytes());assert urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15).read()==src.read_bytes()
with old.ar.exclusive_lock(old.ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(old.ar.STATUS);e=next(x for x in st['experiments'] if x['id']=='D090');e.update(stage='Compiler typed-path merging proved; reader repaired',reason='Same binary/source and fixed gates. LLVMcoalesced identical signed/unsigned bodies; all4control calls and independent comparisons retained. No native control/timing ran before repair.');e['evidence'].append({'label':'D090 typed-call witness and reader-only repair','url':'evidence/D090-wide-OR/compiler-name-observer-failure.json'});st.update(updated_at=old.now(),stage='D090 raw controls and fixed component cohort',activity='Continue unchanged binary with proven typed-path resolution; no compiler/native repetition or gate relaxation.');old.ar.atomic_json(old.ar.STATUS,st)
print(json.dumps({'protocol_sha256':old.sha(H/'protocol-r2.json'),'binary_unchanged':True,'native_executions_so_far':0}),flush=True)
