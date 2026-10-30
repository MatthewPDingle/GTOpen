"""Regenerate the original corpus inputs and read every physical output word independently."""
import collections,json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E125-kernel-control';P=h.read(H/'protocol.json');O=H/'execution';D=O/'raw'
assert len(sys.argv)==2
h.pin(H/'protocol.json',sys.argv[1])
for path,digest in P['input_sha256'].items():h.pin(path,digest)
class Reader:
    def __init__(self,path,magic):
        self.path=path;self.file=path.open('rb');assert self.file.read(len(magic))==magic
    def read(self,n):
        data=self.file.read(n);assert len(data)==n,(str(self.path),n,len(data));return data
    def scalar(self,fmt):return struct.unpack(fmt,self.read(struct.calcsize(fmt)))[0]
    def vector(self,dtype='<u4'):
        n=self.scalar('<Q');assert n<=1000000
        return np.frombuffer(self.read(n*np.dtype(dtype).itemsize),dtype=dtype)
    def vectors(self,count):
        assert self.scalar('<I')==count
        return[self.vector()for _ in range(count)]
    def eof(self):assert self.file.read(1)==b'';self.file.close()
def equal(a,b,label):assert np.array_equal(a,b),label
SPECIAL=np.array([0,0x80000000,1,0x80000001,0x00800000,0x80800000,0x7f800000,0xff800000,0x7fc01234,0xffc05678,0x3f800000,0xbf800000],dtype=np.uint32)
STRESS=np.array([np.finfo(np.float32).max,-np.finfo(np.float32).max,1e-20,-1e-20,13.25,-7.125],dtype=np.float32).view(np.uint32)
HANDS=np.array([(a,b)for a in range(52)for b in range(a+1,52)],dtype=np.uint32)
def regenerate(case):
    family,n,pad,threads,active,mode,permuted,width,pattern,salt=case['descriptor']
    assert family==1
    nn=width+10
    nodes=np.array([0xdeadbeef,2,0xdeadbeef],dtype=np.uint32)
    start=np.zeros(nn,dtype=np.uint32);start[2]=3
    count=np.zeros(nn,dtype=np.uint32);count[2]=width
    card=np.full(width+6,0xdeadbeef,dtype=np.uint32);child=card.copy();perm=card.copy();slot=np.zeros(nn,dtype=np.uint32);slot[2]=2
    for j in range(width):
        card[j+3]=(j%52 if pattern==0 else [0,25,51][j%3]if pattern==1 else(j*17+13)%52 if pattern==2 else 0 if pattern==4 else 51 if pattern==5 else(j+salt)%52)
        child[j+3]=4+j;perm[j+3]=0 if not permuted else j%4;slot[4+j]=4+width-1-j
    inverse=np.full(nn,0x7fc0eeee,dtype=np.uint32);inverse[2]=case['inv_bits']
    index=np.arange(max(n,1)+3,dtype=np.uint32)
    a=HANDS[(index*73+salt)%1326,0].copy();b=HANDS[(index*73+salt)%1326,1].copy()
    if case['mask_style']:
        a[:]=0;b[:]=1+index%51 if case['mask_style']==1 else 1
    masks=(np.left_shift(np.uint64(1),a.astype(np.uint64))|np.left_shift(np.uint64(1),b.astype(np.uint64))).astype('<u8').view('<u4')
    index=np.arange(4*n+7,dtype=np.uint32)
    hp=((index%n+(index//n)*17)%n).astype(np.uint32)if n else np.zeros(7,dtype=np.uint32)
    length=(width+12)*(n+pad)+17;index=np.arange(length,dtype=np.uint32)+salt
    seed=((np.float32(1)+((index%257).astype(np.float32)/np.float32(32))).view(np.uint32)if mode==0 else SPECIAL[index%12]if mode==1 else STRESS[index%6])
    return[nodes,start,count,card,child,perm,inverse,masks,a,b,hp,slot],seed
def check_case(case,expected,seed,baseline,candidate,typed):
    for arm,post in [('baseline',baseline[0]),('candidate',candidate[0])]:
        assert len(post)==12
        for index,(actual,want)in enumerate(zip(post,expected)):equal(actual,want,(case['id'],arm,'immutable',index))
    assert typed.dtype==np.dtype('<u2')and len(typed)==len(expected[10])
    equal(typed.astype(np.uint32),expected[10],(case['id'],'whole_actual_candidate_u16_table'))
    assert len(baseline[1])==len(candidate[1])==1
    a,b=baseline[1][0],candidate[1][0]
    assert len(a)==len(b)==len(seed);equal(a,b,(case['id'],'whole_physical_CFV'))
    n,pad,active=case['descriptor'][1],case['descriptor'][2],case['descriptor'][4]
    lo=2*(n+pad);hi=lo+(n if active else 0)
    equal(a[:lo],seed[:lo],(case['id'],'left_guard'));equal(a[hi:],seed[hi:],(case['id'],'right_guard'))
    return len(a)*2,sum(len(v)for v in expected)*2,len(typed),2*(lo+len(a)-hi)
negative=[]
case={'id':0,'descriptor':[1,7,5,128,1,0,1,8,2,7],'inv_bits':0x3cb21643,'mask_style':0}
im,seed=regenerate(case);post=[x.copy()for x in im];out=seed.copy();typed=im[10].astype('<u2')
check_case(case,im,seed,(post,[out]),(post,[out]),typed)
for label in ['immutable_word','typed_u16_word','CFV_word','guard_word']:
    bp=[x.copy()for x in post];cp=[x.copy()for x in post];bo=out.copy();co=out.copy();tp=typed.copy()
    if label=='immutable_word':cp[5][3]^=np.uint32(1)
    elif label=='typed_u16_word':tp[-1]^=np.uint16(1)
    elif label=='CFV_word':co[24]^=np.uint32(1)
    else:bo[0]^=np.uint32(1);co[0]^=np.uint32(1)
    try:check_case(case,im,seed,(bp,[bo]),(cp,[co]),tp)
    except AssertionError:negative.append(label)
    else:raise AssertionError('reader accepted '+label)
cases=h.read(H/'corpus.json')['cases'];assert len(cases)==1688
readers=[Reader(D/'inputs.bin',b'E125_IN1'),Reader(D/'baseline.bin',b'E125_OUT1'),Reader(D/'candidate.bin',b'E125_OUT1'),Reader(D/'candidate-handperm-u16.bin',b'E125_U16')]
native=[json.loads(line.split('E125_CONTROL ',1)[1])for line in(O/'native.stdout.log').read_text(encoding='utf-8').splitlines()if'E125_CONTROL 'in line]
assert len(native)==1689 and native[-1]['stage']=='complete'and native[-1]['kernel_launches']==3376
totals=np.zeros(4,dtype=np.uint64);groups=collections.Counter();address_checks=0
for index,case in enumerate(cases):
    assert case['id']==index and native[index]['id']==index and native[index]['descriptor']==case['descriptor']and native[index]['inv_bits']==case['inv_bits']and native[index]['mask_style']==case['mask_style']
    original,baseline,candidate,narrow=readers
    assert original.scalar('<I')==baseline.scalar('<I')==candidate.scalar('<I')==narrow.scalar('<I')==index
    equal(original.vector(),np.array(case['descriptor'],dtype=np.uint32),(index,'original_descriptor'))
    inputs=original.vectors(12);seeds=original.vectors(1)
    expected,seed=regenerate(case)
    for field,(actual,want)in enumerate(zip(inputs,expected)):equal(actual,want,(index,'regenerated_original',field))
    equal(seeds[0],seed,(index,'regenerated_whole_seed'))
    bp,bo=baseline.vectors(12),baseline.vectors(1);cp,co=candidate.vectors(12),candidate.vectors(1);typed=narrow.vector('<u2')
    totals+=np.array(check_case(case,expected,seed,(bp,bo),(cp,co),typed),dtype=np.uint64)
    # Independently validate every original used-or-ignored read address, including all blocked hands.
    n,pad,width=case['descriptor'][1],case['descriptor'][2],case['descriptor'][7];stride=n+pad;lo=2*stride;hi=lo+n
    for j in range(width):
        k=int(expected[5][3+j]);idx=np.arange(n,dtype=np.uint32)if k==0 else expected[10][k*n:(k+1)*n]
        assert len(idx)==n and np.all(idx<n)
        address=int(expected[11][int(expected[4][3+j])])*stride+idx.astype(np.uint64)
        assert np.all(address<len(seed))and np.all((address<lo)|(address>=hi));address_checks+=n
    assert native[index]['full_outputs_exact']and native[index]['actual_immutable_inputs_exact']and native[index]['guards_exact']
    groups[case['group']]+=1
    if(index+1)%200==0:print('E125_READER_PROGRESS',index+1,flush=True)
for reader in readers:reader.eof()
end=native[-1]
assert int(totals[0])==end['output_words_both_arms']and int(totals[1])==end['immutable_words_both_arms']and int(totals[3])==end['guard_words_both_arms']and address_checks==end['all_ignored_and_used_read_addresses_prechecked']
files=[{'path':str(p),'bytes':p.stat().st_size,'sha256':h.sha(p)}for p in sorted(D.iterdir())]
assert len(files)==4 and sum(x['bytes']for x in files)<=P['raw_reservation_bytes']
h.save(H/'reader-report.json',{'id':'E125-direct-reader','at':h.now(),'status':'all_original1688cases_full_raw_CFVs_12inputs_typed_u16_and_guards_exact',
    'cases':1688,'application_kernel_launches':3376,'original_corpus_sha256':h.sha(H/'corpus.json'),'case_groups':dict(groups),
    'all_original_inputs_and_seeds_independently_regenerated':True,'entire_physical_CFV_words_both_arms':int(totals[0]),'immutable_input_words_both_arms':int(totals[1]),'actual_candidate_u16_words':int(totals[2]),'guard_words_both_arms':int(totals[3]),'read_addresses_prechecked':address_checks,
    'all_original_cases_order_fields_and_widths_retained':True,'negative_reader_fixtures_rejected':negative,'raw_files':files,
    'solver_or_speed_samples':0,'candidate_accepted':False,'scope':'Directchancekernel corpusonly. DoesnotprovefullGPUengine/CPUplan/upload/capacity/convergence/wholecycleperformance/broad/material/fresh16/holdout/cumulative/appgates.'})
print(json.dumps({'status':'pass','cases':1688,'full_raw_files':4,'negative_fixtures':4,'CFV_words_both_arms':int(totals[0]),'u16_physical_words':int(totals[2])}),flush=True)
