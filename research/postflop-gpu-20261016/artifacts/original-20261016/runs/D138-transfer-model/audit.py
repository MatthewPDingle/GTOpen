"""Independent interval/raw-image reader; no GPU or timing decision."""
import itertools
import json
import mmap
from pathlib import Path
import struct
import sys
H=Path(__file__).resolve().parent
R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'))
import common_e080_live as old
P=old.read(H/'protocol.json');C=old.read(H/'execution/complete.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
for p,h in C['raw_file_sha256'].items():old.pin(p,h)
meta=old.read(H/'output/metadata.json');checks=0
def req(v,message):
    global checks
    assert v,message
    checks+=1
class Reader:
    def __init__(self,path,magic):
        self.file=Path(path).open('rb');self.mm=mmap.mmap(self.file.fileno(),0,access=mmap.ACCESS_READ)
        req(self.mm[:len(magic)]==magic,'raw magic');self.at=len(magic)
    def take(self,fmt):
        s=struct.Struct(fmt);req(self.at+s.size<=len(self.mm),'raw bounds')
        result=s.unpack_from(self.mm,self.at);self.at+=s.size;return result
    def vec(self):
        n,=self.take('<Q');req(n<=1000000 and self.at+n*4<=len(self.mm),'vector bounds')
        v=memoryview(self.mm)[self.at:self.at+n*4].cast('I');self.at+=n*4;return v
    def eof(self):req(self.at==len(self.mm),'complete raw endpoint')
req(sys.byteorder=='little','word endianness')
N=Reader(H/'output/nodes.bin',b'D138-NODES-v1\0\0\0')
G=Reader(H/'output/groups.bin',b'D138-GROUP-v1\0\0\0')
LIMIT=64*1024*1024//4
expected_cases=list(itertools.product(['rainbow','two-tone','river'],[False,True],[False,True]))
req(len(meta['cases'])==12,'12 original geometry cases')
req(meta['block_size_bytes']==32,'actual prototype descriptor ABI')
layout_rows=[];node_count=block_count=group_count=0
for ident,(row,(fixture,iso,full)) in enumerate(zip(meta['cases'],expected_cases)):
    req((row['id'],row['fixture'],row['iso_requested'],row['force_full'])==(ident,fixture,iso,full),'declared layout order')
    ni,nn=N.take('<IQ');req((ni,nn)==(ident,row['nodes']),'original full node frame')
    expected=[[],[]];host_cursor=[0,0];mismatch=[False,False];active_gpu_cursor=[0,0]
    for index in range(nn):
        kind,actor,na,host,device=N.take('<BBHQQ')
        req(kind in [0,1,2,3],'original node kind')
        if kind!=0:continue
        req(actor in [0,1] and 1<=na<=250,'original action actor/arity')
        size=na*row['players'][actor]['nh']
        req(host==host_cursor[actor],'original host action arenas exactly contiguous')
        host_cursor[actor]+=size;mismatch[actor]|=device!=host
        if device==2**64-1:continue
        req(device==active_gpu_cursor[actor],'original selected GPU offsets exactly contiguous')
        active_gpu_cursor[actor]+=size
        expected[actor].append((index,host,device,size))
    for actor in range(2):
        p=row['players'][actor]
        req(host_cursor[actor]==p['host_words'],'whole original host extent')
        compact=p['arena_words']!=p['host_words'] or mismatch[actor]
        req(compact==p['compact'],'compact relation derived from original fields')
        req(active_gpu_cursor[actor]==p['arena_words'],'whole original selected device extent')
        caseid,player,nblocks,capacity=G.take('<IIQQ')
        req((caseid,player,nblocks)==(ident,actor,len(expected[actor])),'complete block list geometry')
        for b in expected[actor]:req(G.take('<IQQQ')==b,'every proposed block matches original node/host/device/length')
        largest=max((b[3]for b in expected[actor]),default=0)
        want_capacity=max(min(p['arena_words'],LIMIT),largest)
        req(capacity==want_capacity==p['window_words'],'bounded capacity and whole-node enlargement')
        req(p['max_node_words']==largest and largest<=250*1326,'legal maximum complete node')
        req(p['active_blocks']==nblocks and p['prototype_block_capacity']>=nblocks,'whole diagnostic vector capacity')
        extra=p['prototype_block_capacity']*32 if not compact and p['arena_words']>LIMIT else 0
        req(p['extra_full_layout_metadata_capacity_bytes']==extra,'prospective full-layout metadata capacity accounting')
        ng,=G.take('<Q');req(ng==p['groups'],'group inventory')
        first=offset=0
        for _ in range(ng):
            start,end,device,length=G.take('<QQQQ')
            req(start==first and start<end<=nblocks,'unique complete-node ownership and progress')
            req(device==offset,'continuous transfer address coverage')
            whole=sum(b[3]for b in expected[actor][start:end])
            req(length==whole and length<=capacity,'no split node and bounded window')
            if end<nblocks:req(length+expected[actor][end][3]>capacity,'fixed greedy boundary')
            first=end;offset+=length;group_count+=1
        req(first==nblocks and offset==p['arena_words'],'all blocks and every device word covered once')
        block_count+=nblocks
    req(row['baseline_pinned_request_bytes']==max(p['arena_words']for p in row['players'])*4,'original full pinned request')
    req(row['proposed_pinned_request_bytes']==max(p['window_words']for p in row['players'])*4,'shared bounded pinned request')
    node_count+=nn
    layout_rows.append({k:row[k]for k in ['id','fixture','iso_requested','force_full','baseline_pinned_request_bytes','proposed_pinned_request_bytes']})
N.eof();G.eof()
F=Reader(H/'output/codecs.bin',b'D138-CODEC-v1\0\0\0')
shapes=[[0,1,31,0,129,257,17],[1,32,33,127,128,129,1023,1326],[0,250*1326,1,0,4097],[0,0,0]]
descriptors=list(itertools.product(range(4),[0,1],[257,4097,LIMIT],range(3),range(3)))
req(meta['codec_cases']==len(descriptors)==216,'fixed codec matrix')
codec_words=upload_words=guard_words=0
for ident,(shape,gaps,limit,kind,mode) in enumerate(descriptors):
    caseid,actual_shape,actual_gaps,actual_kind,actual_mode,nb=F.take('<6I')
    actual_limit,capacity,total,host_len,nscales=F.take('<5Q')
    req((caseid,actual_shape,actual_gaps,actual_kind,actual_mode,actual_limit)==(ident,shape,gaps,kind,mode,limit),'codec case order and parameters')
    lens=shapes[shape];req(nb==len(lens),'all declared synthetic nodes')
    expected=[];host=5 if gaps else 0;device=0
    for i,length in enumerate(lens):
        b=(3*i+1,host,device,length);req(F.take('<IQQQ')==b,'full synthetic row mapping')
        expected.append(b);host+=length+(3 if gaps else 0);device+=length
    req((host_len,total,nscales)==(host+(7 if gaps else 0),device,3*nb+5),'all host/device/scale extents')
    req(capacity==max(min(total,limit),max(lens)),'codec capacity covers every full node')
    source_before,source_after,seed,baseline,candidate,upload_baseline,upload_candidate=[F.vec()for _ in range(7)]
    req(source_before==source_after,'every original source-store word unchanged')
    req(upload_baseline==upload_candidate and len(upload_baseline)==total,'full original and grouped upload images bitwise exact')
    req(baseline==candidate,'full original/grouped output stores bitwise exact')
    for v in [source_before,source_after,seed,baseline,candidate]:
        req(list(v[:3])==[kind,host_len,0 if kind==0 else nscales],'actual whole store schema')
        req(len(v)==3+host_len+(0 if kind==0 else nscales),'every actual q/float/scale word retained')
    before=seed[3:3+host_len];after=baseline[3:3+host_len]
    cursor=0
    for node,lo,_,length in expected:
        req(after[cursor:lo]==before[cursor:lo],'all nonowned prefix/gap words unchanged')
        guard_words+=lo-cursor;cursor=lo+length
    req(after[cursor:]==before[cursor:],'full nonowned suffix unchanged');guard_words+=host_len-cursor
    if kind:
        owned={b[0]for b in expected}
        for i in range(nscales):
            if i not in owned:req(baseline[3+host_len+i]==seed[3+host_len+i],'every nonowned node scale unchanged');guard_words+=1
    codec_words+=sum(map(len,[source_before,source_after,seed,baseline,candidate]));upload_words+=2*total
F.eof();req(meta['invalid_controls_rejected']==6,'invalid/gap/overlap/overflow/no-progress controls')
req(meta['prototype_only'] and meta['CUDA_contexts']==meta['GPU_kernels']==meta['solver_iterations']==0 and not meta['performance_measurement'],'CPU-only diagnostic scope')
old.custody();out=R/'comparisons/D138-transfer-model';out.mkdir(exist_ok=False)
report={'id':'D138-transfer-model','at':old.now(),'status':'pass_scoped_CPU_layout_and_codec_equivalence',
    'checks':checks,'layouts':12,'original_nodes_read':node_count,'complete_active_blocks':block_count,
    'transfer_groups':group_count,'codec_cases':216,'full_codec_store_words':codec_words,
    'full_upload_words':upload_words,'unowned_guard_words':guard_words,'invalid_controls_rejected':6,
    'layout_allocation_requests':layout_rows,'raw_file_sha256':C['raw_file_sha256'],
    'all_complete_original_node_fields_read':True,'no_complete_node_split':True,
    'full_source_store_upload_store_output_images_exact':True,'GPU_contexts':0,'GPU_kernels':0,
    'solver_iterations':0,'performance_measurement':False,'production_source_activated':False,
    'candidate_accepted':False,'root_reader_only':True,
    'limits':'CPU interval model and unchanged Store codec calls only, not an implemented bounded GPU transfer, actual pinned allocation/process footprint, driver/error behavior, GPU numerical or complete-cycle speed proof. Diagnostic vectors are not a production allocation design. No source adoption.'}
old.save(out/'report.json',report)
print(json.dumps({k:report[k]for k in ['status','checks','original_nodes_read','complete_active_blocks','transfer_groups','codec_cases','full_codec_store_words','full_upload_words']}),flush=True)
