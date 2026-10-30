import json,re,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D221-showdown-native-scheduling';P=h.read(H/'protocol.json');C=h.read(H/'capture-report.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
h.pin(H/'protocol.json',C['protocol_sha256']);gates={};witness={}
expected={
 'baseline':{'win':[(0x1900,'LDCU.128 UR20, c[0x0][0x390]'),(0x19a0,'IADD.64 R8, R4.reuse, UR20'),(0x1a20,'LDG.E.CONSTANT R13, desc[UR12][R8.64]')],'lose':[(0x1900,'LDCU.128 UR20, c[0x0][0x390]'),(0x19b0,'IADD.64 R20, R4, UR22'),(0x1a30,'LDG.E.CONSTANT R14, desc[UR12][R20.64]')],'tie':[(0x1910,'LDCU.64 UR8, c[0x0][0x3a0]'),(0x19c0,'IADD.64 R22, R4, UR8'),(0x1a40,'LDG.E.CONSTANT R15, desc[UR12][R22.64]')]},
 'candidate':{'win':[(0x0090,'LDC.64 R14, c[0x0][0x390]'),(0x0190,'IMAD.WIDE.U32 R14, R3, 0x4, R14'),(0x01b0,'LDG.E.CONSTANT R0, desc[UR12][R14.64]')],'lose':[(0x00b0,'LDC.64 R16, c[0x0][0x398]'),(0x01a0,'IMAD.WIDE.U32 R16, R3.reuse, 0x4, R16'),(0x01d0,'LDG.E.CONSTANT R10, desc[UR12][R16.64]')],'tie':[(0x00d0,'LDC.64 R18, c[0x0][0x3a0]'),(0x01c0,'IMAD.WIDE.U32 R18, R3, 0x4, R18'),(0x01e0,'LDG.E.CONSTANT R11, desc[UR12][R18.64]')]}}
for arm in ['baseline','candidate']:
 O=H/'execution'/arm;h.pin(O/'up_show.sass.txt',C['captures'][arm]['up_show_sha256']);h.pin(O/'disassemble.stdout.log',C['captures'][arm]['SASS_sha256']);h.pin(O/'module-0.cubin',C['captures'][arm]['CUBIN_sha256']);text=(O/'up_show.sass.txt').read_text(encoding='utf-8');rows={}
 for line in text.splitlines():
  m=re.match(r'^\s*/\*([0-9a-f]{4})\*/\s*(.*?)\s*;',line)
  if m:addr=int(m[1],16);assert addr not in rows;rows[addr]=m[2]
 barriers=[a for a,op in rows.items()if op.startswith('BAR.SYNC')];gates[arm+':exact_five_barriers']=len(barriers)==5;witness[arm]={'barriers':barriers,'loads':{}}
 for field,chain in expected[arm].items():
  gates[arm+':'+field+':exact_parameter_address_load_chain']=all(rows.get(a)==op for a,op in chain)
  # Register definitions between each supplied address-propagation witness must
  # preserve both pointer words. The baseline .128 load also defines UR22/23.
  pointer_regs=({'win':['UR20','UR21'],'lose':['UR22','UR23'],'tie':['UR8','UR9']}if arm=='baseline'else{'win':['R14','R15'],'lose':['R16','R17'],'tie':['R18','R19']})[field]
  addr_regs=({'win':['R8','R9'],'lose':['R20','R21'],'tie':['R22','R23']}if arm=='baseline'else{'win':['R14','R15'],'lose':['R16','R17'],'tie':['R18','R19']})[field]
  def writes(op,regs):
   op=re.sub(r'^@\S+\s+','',op);parts=op.split(None,1)
   if len(parts)<2:return False
   mnemonic,operands=parts;first=operands.split(',',1)[0].strip()
   if mnemonic.startswith(('ST','BRA','BAR','BSSY','BSYNC','EXIT','ISETP','UISETP','PLOP','UPLOP')):return False
   if first in regs:return True
   m=re.fullmatch(r'(U?R)(\d+)',first)
   if m and ('.64'in mnemonic or '.WIDE'in mnemonic or '.128'in mnemonic):
    size=4 if '.128'in mnemonic else 2
    return any(m[1]+str(int(m[2])+i)in regs for i in range(size))
   return False
  for label,lo,hi,regs in [('param_to_address',chain[0][0],chain[1][0],pointer_regs),('address_to_load',chain[1][0],chain[2][0],addr_regs)]:gates[arm+':'+field+':'+label+'_no_intervening_overwrite']=not any(writes(op,regs)for a,op in rows.items()if lo<a<hi)
  before=sum(a<chain[-1][0]for a in barriers);gates[arm+':'+field+':required_placement']=before==(5 if arm=='baseline'else 0);witness[arm]['loads'][field]={'chain':[{'address_hex':hex(a),'instruction':rows.get(a)}for a,_ in chain],'preceding_barriers':before}
 for label in ['capture','disassemble']:
  q=h.read(O/(label+'.exit.json'));gates[arm+':'+label+':terminal_zero']=q['returncode']==0 and q['error']is q['cleanup']is None
passed=all(gates.values());h.save(H/'report.json',{'id':'D221','at':h.now(),'status':'pass_static_native_payout_placement'if passed else'failed_native_mechanism_or_reader_check','capture_report_sha256':h.sha(H/'capture-report.json'),'gates':gates,'witnesses':witness,'parser':'Exact fixed-driver instructions plus conservative register-overwrite checks, no arbitrary SASS CFG/dynamic simulator. Review chains are bound to captured file hashes. Packed128bit constant load offsets win0x390/lose0x398 and tie0x3a0 follow unchanged27parameter ABI.','all_owned_compilers_native_readers_terminal':True,'application_kernels':0,'solver_executions':0,'performance_samples':0,'candidate_accepted':False,'limits':'Confirms static earlier global payout-load instructions in module-loaded driverJIT code at compute120, same default loader. Does not measure latency, prove numerical equivalence, apply to other drivers, or claim speed.'})
for name in ['protocol.json','capture-report.json','report.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D221','title':'Driver machine-code payout placement','kind':'diagnostic','status':'measured'if passed else'failed','accepted':False,'measurement_epoch':'RAM20261028','stage':'Static machine-code scheduling checked','reason':'All three candidate payout data loads precede first barrier; baseline data loads follow five. No application kernels/counters or speed samples. Numerical equivalence remains pending.'if passed else'Native mechanism reader failed; inspect retained evidence.','evidence':[{'label':'Static driver scheduling witnesses','url':'evidence/'+H.name+'/report.json'}]});e=next(x for x in s['experiments']if x['id']=='E107');e['evidence'].append({'label':'Native payout placement','url':'evidence/'+H.name+'/report.json'});s.update(updated_at=h.now(),stage='E107 raw showdown controls preparation',activity='Static NVRTC and driver code preserve earlier reads. Full output/input numerical checks are next; no new speed gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
print(json.dumps({'status':'pass'if passed else'failed','failed_gates':[k for k,v in gates.items()if not v]}),flush=True);assert passed
