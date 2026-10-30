"""Independently regenerate and read every physical word of fixed E127 direct corpus."""
import json,struct,sys
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
H=ROOT/'runs/E127-direct';P=h.read(H/'protocol.json');O=H/'execution'
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1]);h.custody()
for p,digest in P['input_sha256'].items():h.pin(p,digest)
C=h.read(H/'corpus.json');original=h.read(H/'original-corpus.json')['cases'];assert len(original)==819
def u(v):return np.asarray(v,dtype=np.uint32)
def fb(v):return np.asarray(v,dtype=np.float32).view(np.uint32)
def split(v):return np.asarray(v,dtype=np.uint64).view(np.uint32)
def value(i,mode):
    i=np.asarray(i,dtype=np.int64)
    if mode==1:return np.where(i%2==0,0,0x80000000).astype(np.uint32)
    if mode==2:
        ordinary=fb(((i*73%1009).astype(np.float32)-np.float32(504))/np.float32(32))
        special=u([0x7f800000,0xff800000,0x7fc01234,0xffc05678])[(i//7)%4]
        return np.where(i%7==0,special,ordinary).astype(np.uint32)
    if mode==3:return np.where(i%3==0,0xff7fffff,0x7f7fffff).astype(np.uint32)
    if mode==4:return u([1,0x80000001,0,0x80000000,0x00800000,0x80800000,0x00800001])[i%7]
    return fb([0.,-0.,.25,-.75,13.25,-7.125,1e10,-1e10,1e-20,-1e-20])[(i*5+i//11)%10]
def regenerate(row):
    index=row['id'];v=row['variant'];base=original[row['original_case_id']]
    nh,na,block,p,role,algo,t,mode,count,st,start,parent,off,loff=base['descriptor']
    nn=na+8;k=min(2,na)if v else 0;new_nn=nn+k*na
    nodes=[0xdeadbeef,parent,0xdeadbeef];player=[0xfffffff9]*new_nn;player[parent]=1-p if role==2 else p
    arity=[0xfffffff9]*new_nn;arity[parent]=na;offset=[0]*new_nn;offset[parent]=off
    starts=[0]*new_nn;starts[parent]=2;children=[0xdeadbeef]*(na+4);children[2:2+na]=list(range(4,4+na))
    rsrc=[0]*new_nn;rsrc[parent]=3;reach=value(np.arange(6*max(nh,1)+7)+19,mode)&0x7fffffff
    locks=[0xffffffffffffffff]*new_nn
    if role==1:locks[parent]=loff
    sigma=u([0x7fc0cafe]*(loff+na*nh+17));den=np.float32(na*(na+1)//2)
    weights=fb(np.arange(1,na+1,dtype=np.float32)/den)
    for a in range(na):sigma[loff+a*nh:loff+(a+1)*nh]=weights[a]
    slots=list(range(nn))+[0]*(k*na)
    for a in range(na):slots[4+a]=4+na-1-a
    reg=u([0x7fc0aa55]*(off+na*nh+17));strategy=reg.copy()
    reg[off:off+na*nh]=value(np.arange(na*nh)+index,mode)
    strategy[off:off+na*nh]=value(np.arange(na*nh)+index+3,mode)&0x7fffffff
    cfv=value(np.arange((nn+3)*st+17)+index*7,mode);cfv[parent*st:parent*st+st]=0x7fc0babe
    owned_reg=[(off,off+na*nh)]if role==0 else[];owned_cfv=[(parent*st,parent*st+nh)]
    if v:
        for j,a in enumerate([0]if na==1 else[0,na-1]):
            child=4+a;nodes.append(child);player[child]=1-player[parent];arity[child]=na;starts[child]=len(children)
            children.extend(range(nn+j*na,nn+(j+1)*na))
            for x in range(na):slots[nn+j*na+x]=nn+4+j*na+x
            rsrc[child]=1+j;child_off=len(reg)+16;offset[child]=child_off
            reg=np.concatenate((reg,u([0x7fc0aa55]*(33+na*nh))));strategy=np.concatenate((strategy,u([0x7fc0aa55]*(33+na*nh))))
            reg[child_off:child_off+na*nh]=value(np.arange(na*nh)+index+29+j*11,mode)
            strategy[child_off:child_off+na*nh]=value(np.arange(na*nh)+index+31+j*13,mode)&0x7fffffff
            child_lock=len(sigma);sigma=np.concatenate((sigma,u([0x7fc0cafe]*(na*nh+17))))
            for a2 in range(na):sigma[child_lock+a2*nh:child_lock+(a2+1)*nh]=weights[a2]
            if v==2:locks[child]=child_lock
            if player[child]==p and locks[child]==0xffffffffffffffff:owned_reg.append((child_off,child_off+na*nh))
            owned_cfv.append((slots[child]*st,slots[child]*st+nh))
        end=(nn+7+k*na)*st+17;cfv=np.concatenate((cfv,value(np.arange(len(cfv),end)+index*7,mode)))
        if v==2:
            slots[nn]=slots[parent];cfv[parent*st:parent*st+nh]=value(np.arange(nh)+index*7+101,mode)
    immutable=[u(nodes),u(player),u(arity),split(offset),u(starts),u(children),u(rsrc),reach,split(locks),sigma,u(slots),u(base['discount_bits'])]
    assert sum(map(len,immutable))==row['expected_immutable_words']
    seeds=[reg,strategy,cfv];assert sum(map(len,seeds))==row['expected_mutable_words']
    return u(base['descriptor']),immutable,seeds,owned_reg,owned_cfv
class Reader:
    def __init__(self,p,magic):
        self.p=p;self.f=p.open('rb');assert self.f.read(len(magic))==magic
    def num(self,fmt):
        n=struct.calcsize(fmt);b=self.f.read(n);assert len(b)==n,(self.p,'eof');return struct.unpack(fmt,b)[0]
    def vec(self):
        n=self.num('<Q');assert n<1000000,(self.p,n);data=self.f.read(4*n);assert len(data)==4*n
        return np.frombuffer(data,dtype='<u4')
    def close(self):assert not self.f.read(1),(self.p,'trailing');self.f.close()
def exact(a,b,label):
    assert a.shape==b.shape,(label,a.shape,b.shape)
    bad=np.flatnonzero(a!=b)
    assert len(bad)==0,(label,int(bad[0])if len(bad)else None,hex(int(a[bad[0]]))if len(bad)else None,hex(int(b[bad[0]]))if len(bad)else None)
F=O/'raw';readers=[Reader(F/'inputs.bin',b'E127_IN1'),Reader(F/'baseline.bin',b'E127_OUT1'),Reader(F/'candidate.bin',b'E127_OUT1'),Reader(F/'baseline-inputs.bin',b'E127_IM1'),Reader(F/'candidate-inputs.bin',b'E127_IM1')]
logs=[json.loads(x.split('E127_UNIT ',1)[1])for x in(O/'native.stdout.log').read_text(encoding='utf-8').splitlines()if'E127_UNIT 'in x]
assert len(logs)==2458 and logs[-1]['stage']=='complete'
counts={'input_seed_words':0,'immutable_post_words_both_arms':0,'output_words_both_arms':0,'guard_words_both_arms':0,'allocation_pairs_checked':0,'cases':0}
for row,log in zip(C['cases'],logs[:-1]):
    idx=row['id'];desc,expected_imm,seeds,oreg,ocfv=regenerate(row)
    assert all(r.num('<I')==idx for r in readers);exact(readers[0].vec(),desc,(idx,'descriptor'))
    for j,want in enumerate(expected_imm):exact(readers[0].vec(),want,(idx,'seed_immutable',j));counts['input_seed_words']+=len(want)
    for j,want in enumerate(seeds):exact(readers[0].vec(),want,(idx,'seed_mutable',j));counts['input_seed_words']+=len(want)
    outputs=[[readers[arm].vec()for _ in range(3)]for arm in[1,2]]
    for arm in[0,1]:
        for j,want in enumerate(expected_imm):exact(readers[3+arm].vec(),want,(idx,'postimmutable',arm,j));counts['immutable_post_words_both_arms']+=len(want)
        for j,(actual,seed)in enumerate(zip(outputs[arm],seeds)):
            assert actual.shape==seed.shape
            owned=np.zeros(len(seed),dtype=np.bool_)
            if desc[8]:
                for a,b in(oreg if j<2 else ocfv):owned[a:b]=True
            exact(actual[~owned],seed[~owned],(idx,'guard',arm,j));counts['guard_words_both_arms']+=int(np.count_nonzero(~owned));counts['output_words_both_arms']+=len(actual)
    for j in range(3):exact(outputs[0][j],outputs[1][j],(idx,'whole_output',j))
    assert log['id']==idx and log['original_case_id']==row['original_case_id']and log['variant']==row['variant']and log['selected_action_children']==row['selected_action_children']
    assert log['discount_bits']==expected_imm[-1].tolist()and log['output_words_per_arm']==sum(map(len,seeds))and log['immutable_words_per_arm']==sum(map(len,expected_imm))
    for arm in log['disjoint_device_ranges']:
        regions=arm['regions'];assert len(regions)==15
        expected_lengths=[4*len(v)for v in expected_imm+seeds];assert[x[1]for x in regions]==expected_lengths
        for i,(a,n)in enumerate(regions):
            assert a>0 and n>0
            for b,m in regions[i+1:]:assert a+n<=b or b+m<=a;counts['allocation_pairs_checked']+=1
    counts['cases']+=1
    if idx%300==0:print('E127 full-physical reader',idx,'/2457',flush=True)
for r in readers:r.close()
complete=logs[-1];assert complete['cases']==2457 and complete['kernel_launches']==P['expected_kernel_launches']
for k in['output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']:assert complete[k]==counts['immutable_post_words_both_arms'if k=='immutable_words_both_arms'else k]
assert complete['solver_executions']==0 and complete['performance_measurement']is False
files={str(p):{'bytes':p.stat().st_size,'sha256':h.sha(p)}for p in F.iterdir()};assert sum(x['bytes']for x in files.values())==P['expected_raw_bytes']
h.custody()
h.save(H/'report.json',{'id':'E127-direct','at':h.now(),'status':'pass_all2457_original_and_derived_whole_physical_cases','protocol_sha256':sys.argv[1],'counts':counts,'kernel_launches':complete['kernel_launches'],'raw_files':files,'scope':'Exact baseline original child kernels then parent versus fused candidate. Entire original819 parent corpus retained; two819-case child/lock/own-grandchild-alias variants. Every input and seed independently regenerated, all12 immutable postarrays and all3 whole mutable outputs read both arms, allunowned guardwords exact, all15actual devicebuffers pairwise disjoint. No engine/canonical/runtime cost/speed/adoption claim.','solver_speed_samples':0,'candidate_accepted':False})
print(json.dumps({'status':'pass','counts':counts,'report_sha256':h.sha(H/'report.json')}),flush=True)
