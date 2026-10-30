"""Independent full raw field comparison against frozen metadata and D122 maps."""
from pathlib import Path
import array,struct
def vector(f):
 n,=struct.unpack('<Q',f.read(8));assert n<100000000
 v=array.array('Q');v.fromfile(f,n);assert len(v)==n;return v
def replay(path,case,reference,expected):
 checks=0;words=0;changed=0
 with Path(expected).open('rb')as e:
  assert e.read(16)==b'D122-CFV-MAP1\0\0\0';cid,n,os,ns,ob,nb=struct.unpack('<IQQQQQ',e.read(44));assert cid==case
  slots=array.array('I');slots.fromfile(e,n);assert e.read(1)==b''
 with Path(path).open('rb')as f,Path(reference).open('rb')as r:
  assert f.read(16)==b'E076-PLAN-RAW1\0\0';assert r.read(16)==b'D092-PLAN-RAW1\0\0'
  assert f.read(8)==r.read(8)==struct.pack('<II',case,53)
  sizes=f.read(16);assert sizes==r.read(16)and sizes[:8]==sizes[8:];checks+=4
  for field in range(53):
   assert f.read(4)==r.read(4)==struct.pack('<I',field)
   ac,bc,av,bv=[vector(f)for _ in range(4)];rc1,rc2,rv1,rv2=[vector(r)for _ in range(4)]
   assert ac==bc==rc1==rc2;assert av==rv1;checks+=3;words+=len(av)
   if field==36:
    assert bv[0]==n and len(bv)==n+1 and list(bv[1:])==list(slots);checks+=2
    changed=sum(x!=y for x,y in zip(av,bv))
   elif field==37:assert av==array.array('Q',[ob]) and bv==array.array('Q',[nb]);checks+=2
   else:assert av==bv;checks+=1
  for _ in range(2):assert vector(f)==vector(r);checks+=1
  assert f.read(1)==r.read(1)==b'';checks+=1
 return {'case':case,'fields':53,'unchanged_fields':51,'baseline_words':words,'nodes':n,'changed_slot_words':changed,'old_CFV_blocks':ob,'new_CFV_blocks':nb,'original_scratch_rows':os,'new_scratch_rows':ns,'checks':checks,'all_non_CFV_values_and_all_capacities_exact':True,'map_matches_frozen_lifetime_model':True,'baseline_matches_retained_accepted_metadata':True,'raw_bytes':Path(path).stat().st_size}
