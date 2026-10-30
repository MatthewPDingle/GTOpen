"""Full raw53-field/capacity/struct equality, independently matched to accepted data."""
from pathlib import Path
import array,struct
def vec(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference):
 checks=0;words=0
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'D123-PLAN-RAW1\0\0'and r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vec(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vec(r)for _ in range(4)]
   assert ac==bc==rc1==rc2 and av==bv==rv1;checks+=4;words+=len(av)
  for _ in range(2):assert vec(f)==vec(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'all_values_capacities_structs_exact':True,'baseline_matches_retained_accepted_metadata':True,'baseline_words':words,'root_checks':checks,'raw_bytes':Path(path).stat().st_size}
