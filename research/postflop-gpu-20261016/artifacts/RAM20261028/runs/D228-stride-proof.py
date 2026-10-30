import hashlib,itertools,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D228-CFV-stride-scout';assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
strides=sorted(set(range(1345))|{2**n+d for n in range(11,31)for d in [-1,0,1]}|{2**31-1});slots=P['slot_values'];indices=P['hand_index_i32_values'];bases=P['base_u64_values'];mask=2**64-1;raw=H/'addresses.bin';count=wide=truncation=basechecks=0;digest=hashlib.sha256()
def signed32(bits):return bits if bits<2**31 else bits-2**32
with raw.open('xb')as f:
 for stride,slot,index in itertools.product(strides,slots,indices):
  assert 0<=stride<=2**31-1 and 0<=slot<=2**32-1 and -(2**31)<=index<=2**31-1
  old_stride=signed32(stride)&mask;new_stride=stride;old=(slot*old_stride+(index&mask))&mask;new=(slot*new_stride+(index&mask))&mask;assert old==new
  wrong=(((slot*stride)&0xffffffff)+(index&mask))&mask;wide+=slot*stride>0xffffffff;truncation+=wrong!=new
  for base in bases:assert(base+4*old)&mask==(base+4*new)&mask;basechecks+=1
  data=struct.pack('<IIIQQ',stride,slot,index&0xffffffff,old,new);f.write(data);digest.update(data);count+=1
 f.flush()
assert wide>1000 and truncation==wide and raw.stat().st_size==count*28
checks=0;decoded=0
with raw.open('rb')as f:
 for stride,slot,index in itertools.product(strides,slots,indices):
  ss,sl,ib,old,new=struct.unpack('<IIIQQ',f.read(28));assert(ss,sl,signed32(ib))==(stride,slot,index);checks+=1
  expected=(slot*stride+index)%(2**64);assert old==new==expected;checks+=1
  for base in bases:assert(base+old*4)%(2**64)==(base+new*4)%(2**64)==(base+expected*4)%(2**64);checks+=1
  decoded+=1
 assert f.read(1)==b''and decoded==count
h.custody();h.save(H/'report.json',{'id':'D228','at':h.now(),'status':'pass_nonnegative_stride_wide_address_algebra','protocol_sha256':sys.argv[1],'sampled_strides':len(strides),'full_record_pairs':count,'wide_product_pairs':wide,'intentional_u32_product_truncation_differences_detected':truncation,'base_byte_address_checks':basechecks,'reader_checks':checks,'raw_bytes':raw.stat().st_size,'raw_sha256':digest.hexdigest(),'all_signed_positive_and_unsigned_addresses_identical':True,'algebraic_full_domain_reason':'For every0<=n<=i32MAX, signed32(n) andunsigned32(n) have identical nonnegative integer values and identicalu64 conversion. Multiplying sameu32slot afterexistingu64cast andadding sameint32index therefore yields identicalmod2^64index, including >32bitproducts. Byte/base arithmetic isalso identical. Only signature type changes; sourceproducts stayu64.','new_CUDA_contexts_compilers_kernels_solves_or_speed_samples':0,'candidate_accepted':False,'limits':'Complete retained boundaryCartesian records and independent arithmetic replay support algebra; not exhaustive allpositive32bitstrides/allslots, no validallocation/dereference/ISA/devicefloat orspeed proof. Negative handindices are only integer wrapcontrols, not claims of legalpointeraccess; actualpositive stride enginecontract and compiler/numerical gates remain.'})
print(json.dumps({'status':'pass','record_pairs':count,'wide_pairs':wide,'reader_checks':checks,'raw_bytes':raw.stat().st_size}),flush=True)
