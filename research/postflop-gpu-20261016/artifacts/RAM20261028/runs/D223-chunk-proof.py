import hashlib,json,struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D223-chunk-division-scout';assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
assert P['m_range_inclusive']==[0,1326]and P['width_range_inclusive']==[1,256]
raw=H/'shapes.bin';count=power=fallback=0;maximum=0;digest=hashlib.sha256()
with raw.open('xb')as f:
 for m in range(1327):
  for width in range(1,257):
   numerator=(m+width-1)&0xffffffff;original=numerator//width;is_power=int((width&(width-1))==0);leading=32-width.bit_length();shift=31-leading if is_power else 0xffffffff;candidate=numerator>>shift if is_power else numerator//width
   assert original==candidate and 0<=candidate<=1326 and 0<=numerator<=1581
   data=struct.pack('<7I',m,width,numerator,original,candidate,is_power,shift);f.write(data);digest.update(data);count+=1;power+=is_power;fallback+=not is_power;maximum=max(maximum,candidate)
 f.flush()
assert count==P['expected_shape_records']==339712 and power==1327*9 and fallback==count-power
# Independent reader uses signed-free mathematical ceil and repeated halving,
# rather than bit_length/leading-zero model or the writer's division expression.
checks=0;reader_power=0
with raw.open('rb')as f:
 for m in range(1327):
  for width in range(1,257):
   values=struct.unpack('<7I',f.read(28));a,w,num,old,new,flag,sh=values;assert a==m and w==width;checks+=1
   q,r=divmod(m,width);expected=q+int(r!=0);assert old==new==expected;checks+=1
   work=width;k=0
   while work>1 and work%2==0:work//=2;k+=1
   actual_power=work==1;assert flag==actual_power and sh==(k if actual_power else 0xffffffff);checks+=1
   assert num==m+width-1 and num<2**32;checks+=1;reader_power+=actual_power
 assert f.read(1)==b''
assert reader_power==power and raw.stat().st_size==count*28
h.custody();h.save(H/'report.json',{'id':'D223','at':h.now(),'status':'pass_exhaustive_supported_chunk_integer_model','protocol_sha256':sys.argv[1],'shape_records':count,'power_two_shapes':power,'fallback_shapes':fallback,'maximum_chunk':maximum,'reader_checks':checks,'raw_bytes':raw.stat().st_size,'raw_sha256':digest.hexdigest(),'all_model_and_reader_values_exact':True,'same_bounds_reason':'Only chunk binding changes; equal integer chunk and unchanged tid/m_o/min expressions imply identical lo_k,hi_k and subsequent ordered float loop bounds for every lane. This is an algebraic inference, not an emitted-code or device-float observation.','CUDA_contexts_kernels_compilers_solves_or_speed_samples':0,'candidate_accepted':False,'limits':P['scope']})
print(json.dumps({'status':'pass','shape_records':count,'power_two':power,'fallback':fallback,'reader_checks':checks,'raw_bytes':raw.stat().st_size}),flush=True)
