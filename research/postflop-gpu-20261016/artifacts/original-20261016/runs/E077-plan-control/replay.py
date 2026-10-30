"""Full53 fields and actual compiled high-bit maps versus independently frozen images."""
from pathlib import Path
import array,struct
def vec(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference,tags):
 checks=0;words=0
 with Path(tags).open('rb')as e:
  assert e.read(16)==b'D124-TAG-RAW1\0\0\0'and struct.unpack('<II',e.read(8))==(case,2)
  original=array.array('Q',[2]);encoded=array.array('Q',[2])
  for p in range(2):
   n,=struct.unpack('<Q',e.read(8));a=array.array('I');a.fromfile(e,n);b=array.array('I');b.fromfile(e,n)
   original.append(n);original.extend(a);encoded.append(n);encoded.extend(b)
  assert e.read(1)==b''
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'E077-PLAN-RAW1\0\0'and r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vec(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vec(r)for _ in range(4)]
   assert ac==bc==rc1==rc2 and av==rv1;checks+=3;words+=len(av)
   if field==46:assert av==original and bv==encoded;checks+=2
   else:assert av==bv;checks+=1
  for _ in range(2):assert vec(f)==vec(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'unchanged_fields':52,'baseline_words':words,'root_checks':checks,'all_non_tag_values_capacities_structs_exact':True,'compiled_tags_match_frozen_D124':True,'baseline_all53fields_match_retained_accepted_metadata':True,'raw_bytes':Path(path).stat().st_size}
