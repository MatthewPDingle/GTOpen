import sys, struct, itertools
from pathlib import Path
import numpy as np
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
O=H/'output';M=h.read(O/'metadata.json');C=h.read(O/'case-manifest.json')
checks=words=packets=odd=empty=guards=corruptions=0
def req(v,s):
    global checks
    assert v,s;checks+=1
def raw(name):
    global words
    p=O/name;req(p.stat().st_size%4==0,'whole u32 image');a=np.fromfile(p,dtype='<u4');words+=len(a);return a
def eq(a,b):return a.shape==b.shape and bool(np.array_equal(a,b))
req(len(C)==M['cases']==2212 and len(M['cohorts'])==6 and not M['performance_measurement'] and not M['integration_created'],'fixed cohort inventory')
source=raw('source-input.u32');req(len(source)==M['source_words'],'complete source')
req(sum(c['length'] for c in C)==M['encoded_values_per_type']==1964131,'fixed encoded value inventory')
source_guard=np.ones(len(source),dtype=bool)
for i,c in enumerate(C):
    req(c['node']==i and c['source']>=3 and c['source']+c['length']+3<=len(source),'case bounds')
    source_guard[c['source']:c['source']+c['length']]=False
req(bool(np.all(source[source_guard]==0x7fc055aa)),'every source guard exact')
for cohort,(signed,maxdesc) in zip(M['cohorts'],itertools.product([True,False],[1,7,31])):
    variant='i16' if signed else 'u16';label=f'{variant}-d{maxdesc}'
    req(cohort['label']==label and cohort['signed']==signed and cohort['max_descriptors']==maxdesc and cohort['capacity_words']==65544,'fixed cohort order/configuration')
    oq=raw(f'oracle-{variant}-q.u32');os=raw(f'oracle-{variant}-scale.u32')
    req(len(oq)==len(source) and len(os)==len(C) and bool(np.all(oq<=65535)),'complete shared CPU oracle images')
    req(bool(np.all(oq[source_guard]==0xa55a)),'every CPU q guard preserved')
    req(eq(raw(f'{label}-source-before.u32'),source) and eq(raw(f'{label}-source-after.u32'),source),'all source bits unchanged at cohort boundaries')
    host=np.full(len(oq),0xa55a,dtype='<u4');scales=np.full(len(os),0x7fc0cafe,dtype='<u4');seen=[]
    for index,packet in enumerate(cohort['packets']):
        bs=packet['blocks'];n=len(bs);total=packet['total_words'];key=packet['raw_label']
        req(index==packet['packet'] and key==f'{label}-packet-{index:04}' and 0<n<=maxdesc and total<=65544,'packet geometry')
        initial=raw(key+'-initial.u32');native_expected=raw(key+'-expected.u32');actual=raw(key+'-actual.u32')
        expected=np.full(total+16,0xdeadbeef,dtype='<u4');qoff=0
        for j,b in enumerate(bs):
            node=b['node'];case=C[node];start=b['source'];length=b['length']
            req(start==case['source'] and length==case['length'] and b['qoff']==qoff,'original corpus case geometry and dense packet words')
            expected[8+4*j:8+4*j+4]=[start&0xffffffff,start>>32,length,qoff]
            expected[8+4*n+j]=os[node]
            vals=oq[start:start+length]
            if length:
                low=vals[::2].copy();high=np.full(len(low),0xd00d,dtype='<u4');high[:length//2]=vals[1::2]
                expected[8+5*n+qoff:8+5*n+qoff+len(low)]=low|(high<<16)
            qoff+=(length+1)//2;seen.append(node);odd+=length%2;empty+=length==0
        req(qoff==packet['q_words'] and total==5*n+qoff,'full disjoint packet footprint')
        init_expected=np.full(total+16,0xdeadbeef,dtype='<u4');init_expected[8:8+4*n]=expected[8:8+4*n]
        req(eq(initial,init_expected),'every initial descriptor and unwritten scratch word')
        req(eq(native_expected,expected),'all native oracle packet words match independent CPU-oracle scatter')
        req(eq(actual,expected),'every actual packed/scale/descriptor/guard word exact')
        req(bool(np.all(actual[:8]==0xdeadbeef)) and bool(np.all(actual[8+total:]==0xdeadbeef)),'all physical guards exact');guards+=16
        for j,b in enumerate(bs):
            node,start,length=b['node'],b['source'],b['length'];scales[node]=actual[8+4*n+j]
            packed=actual[8+5*n+b['qoff']:8+5*n+b['qoff']+(length+1)//2]
            unpacked=np.empty(2*len(packed),dtype='<u4');unpacked[::2]=packed&65535;unpacked[1::2]=packed>>16
            host[start:start+length]=unpacked[:length]
        if index==0:
            bad=actual.copy();bad[8+4*n]^=1;req(not eq(bad,expected),'injected scale-bit corruption rejected');corruptions+=1
        if index==1:
            req(qoff>0,'nonempty q corruption witness')
            bad=actual.copy();bad[8+5*n]^=1;req(not eq(bad,expected),'injected q-bit corruption rejected');corruptions+=1
        packets+=1
    req(seen==list(range(len(C))),'all cases once in original order, no skips')
    req(eq(host,oq) and eq(scales,os),'full independent host images including all q guards')
    req(eq(raw(f'{label}-host-q.u32'),host) and eq(raw(f'{label}-host-scale.u32'),scales),'actual native scatter exact in full')
req(packets==M['kernel_launches'] and odd>0 and empty>0 and corruptions==12,'whole native inventory and reader calibration')
h.custody();D=ROOT/'comparisons/D152-packet-numerics';D.mkdir(exist_ok=False)
report={'id':'D152','at':h.now(),'status':'pass_scoped_actual_packet_CPU_oracle_equivalence','protocol_sha256':h.sha(H/'protocol.json'),'binary_sha256':h.sha(H/'probe.exe'),'PTX_sha256':P['PTX_sha256'],'cases_per_type':2212,'cohorts':6,'descriptor_limits':[1,7,31],'capacity_words':65544,'encoded_values_per_type':1964131,'actual_kernel_launches':packets,'all_packet_descriptor_q_scale_and_guard_words_exact':True,'all_host_q_scale_words_exact':True,'source_bits_exact_at_all_six_cohort_boundaries':True,'represented_raw_words':words,'physical_packet_guard_words_checked':guards,'odd_block_occurrences':odd,'empty_block_occurrences':empty,'injected_reader_failure_calibrations':corruptions,'reader_checks':checks,'performance_measurement':False,'integration_created':False,'candidate_accepted':False,'source_main_live_PTX_custody_pass':True,'scope':'Fixed2212case source-bound shared Rust CPU encoding oracle, signed/unsigned x max1/7/31 descriptors and65544-word packets. Complete packet inputs/expected/actual and direct-scattered host q/scales retained and checked, including all guard/odd-tail words. Full source words checked before/after each cohort, not after every individual packet. No physical >4Gi-element source allocation, large-app capacity, pinned/runtime borrow proof, integrated engine readback or speed qualification.'}
h.save(D/'report.json',report);print({k:report[k] for k in ['status','cases_per_type','actual_kernel_launches','reader_checks']},flush=True)
