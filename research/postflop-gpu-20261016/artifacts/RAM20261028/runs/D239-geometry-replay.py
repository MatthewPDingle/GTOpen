import struct,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();H=ROOT/'runs/D239-fold-copy-sum-scout';P=h.read(H/'source-review.json');raw=H/'geometry.bin';h.pin(raw,P['geometry_raw_sha256']);data=raw.read_bytes();assert len(data)==339712*24
count=0
for i,(n,width,oldloops,removed_shared_reads)in enumerate(struct.iter_unpack('<IIQQ',data)):
 expected_n,expected_w=divmod(i,256);assert(n,width)==(expected_n,expected_w+1)
 q,r=divmod(n,width);assert oldloops==q*width+r==n and removed_shared_reads==n;count+=1
assert count==P['geometry_records']==339712
S=ROOT/'runs/E110-source';review=h.read(S/'source-review.json');text=(S/'candidate.cu').read_bytes().decode('utf-8');back=text
for row in reversed(review['replacements']):
 if row['new']:back=back.replace(row['new'],row['old'],1)
 else:
  needle='    total_parts[threadIdx.x] = partial;';assert back.count(needle)==1;back=back.replace(needle,row['old']+needle,1)
assert back.encode()==(S/'baseline.cu').read_bytes();O=ROOT/'comparisons/D239-geometry-replay';O.mkdir(exist_ok=False)
h.save(O/'report.json',{'id':'D239-geometry-replay','at':h.now(),'status':'pass_retained_full_geometry_and_source_reverse','records':count,'geometry_sha256':h.sha(raw),'source_review_sha256':h.sha(S/'source-review.json'),'all_shape_records_in_original_order':True,'all_thread_partition_counts_exact':True,'byte_exact_source_reverse':True,'GPU_or_speed_runs':0,'limits':'Integer iteration-count partition andsource reversal only; floating order follows unchangedinduction/sourceproof. ActualPTX/native andfiniteGPUraw/fullcanonical/equivalence plusperformance/material gates remain separate.'});print('339712 retained geometry records and exact source reversal passed.',flush=True)
