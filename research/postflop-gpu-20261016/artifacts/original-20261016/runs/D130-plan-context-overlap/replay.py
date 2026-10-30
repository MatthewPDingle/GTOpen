"""Compare the entire actual plan with the retained accepted baseline outside timing."""
from pathlib import Path
import array,struct
def replay(path,reference,case):
 checks=0;words=0
 def ck(v,label):
  nonlocal checks
  assert v,(case,label);checks+=1
 def vector(f,read=True):
  n,=struct.unpack('<Q',f.read(8));ck(n<100000000,'bounded vector')
  if not read:f.seek(n*8,1);return None
  v=array.array('Q');v.fromfile(f,n);ck(len(v)==n,'complete vector');return v
 with Path(path).open('rb')as f,Path(reference).open('rb')as g:
  ck(f.read(16)==b'D130-PLAN-RAW1\0\0'and g.read(16)==b'D092-PLAN-RAW1\0\0','magic');ck(f.read(8)==g.read(8)==struct.pack('<II',case,53),'case/schema');size,=struct.unpack('<Q',f.read(8));a,b=struct.unpack('<QQ',g.read(16));ck(size==a==b,'actualstructsize')
  for field in range(53):
   ck(f.read(4)==g.read(4)==struct.pack('<I',field),'fieldid');cap=vector(f);actual=vector(f);refcap=vector(g);vector(g,False);expected=vector(g);vector(g,False);ck(cap==refcap,'fullactualcapacity '+str(field));ck(actual==expected,'fullactualwordbits '+str(field));words+=len(actual)
  ck(vector(f)==vector(g),'allnodekinds');ck(vector(f)==vector(g),'allchildslots');ck(f.read(1)==g.read(1)==b'','fullendpoints')
 return {'reference_case':case,'checks':checks,'encoded_words':words,'all53fields_capacities_struct_kind_child_bits_exact':True,'raw_bytes':Path(path).stat().st_size}
