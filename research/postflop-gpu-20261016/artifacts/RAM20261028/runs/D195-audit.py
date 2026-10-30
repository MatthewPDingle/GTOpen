import array, collections, json, struct, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D195-parent-chance-controls';P=h.read(H/'protocol.json');checks=0
def req(value,message):
    global checks
    assert value,message;checks+=1
class Reader:
    def __init__(self,path,magic):
        self.f=Path(path).open('rb');req(self.f.read(len(magic))==magic,'raw magic')
    def u32(self):return struct.unpack('<I',self.f.read(4))[0]
    def vec(self):
        n,=struct.unpack('<Q',self.f.read(8));req(n<=P['max_case_array_words'],'vector bound')
        raw=self.f.read(4*n);req(len(raw)==4*n,'complete vector extent');v=array.array('I');v.frombytes(raw)
        if sys.byteorder!='little':v.byteswap()
        return v
    def vecs(self):
        n=self.u32();req(n<=24,'immutable/output vector count');return [self.vec() for _ in range(n)]
    def eof(self):req(self.f.read(1)==b'','complete raw endpoint');self.f.close()
def masks(im,p,nh):
    m,a,b=im[5+p],im[7+2*p],im[8+2*p];req(len(a)==len(b)==max(nh,1)+3 and len(m)==2*len(a),'canonical mask shapes')
    blocked=[[] for _ in range(52)]
    for i,(x,y) in enumerate(zip(a,b)):
        req(x<y<52 and m[2*i]|(m[2*i+1]<<32)==(1<<x)|(1<<y),'canonical two-card mask')
        if i<nh:blocked[x].append(i);blocked[y].append(i)
    if nh==1326:req(len(set(zip(a[:nh],b[:nh])))==1326,'all 1326 canonical hands')
    return blocked
def guard(output,seed,ranges):
    count=0;cursor=0
    for lo,hi in sorted(ranges):
        req(cursor<=lo<=hi<=len(output),'disjoint physical output intervals')
        req(output[cursor:lo]==seed[cursor:lo],'all physical gap bits');count+=lo-cursor;cursor=hi
    req(output[cursor:]==seed[cursor:],'all physical tail bits');return count+len(output)-cursor
def mapping(im,np,ne,n0,n1,seeds):
    req(len(im)==17 and len(seeds)==2,'all original and parent metadata arrays present')
    pa,ch,card=im[:3];nodes,cs,cc,ca,cn,cp=im[11:]
    req(len(cs)==len(cc)==len(im[3])==len(im[4]),'node metadata extents')
    req(len(ca)==len(cn)==len(cp),'cc table extents')
    req(len(nodes)>=np+1 and len(pa)>=ne+1 and len(ch)==len(pa)==len(card),'worklist extents')
    original=[(pa[1+e],ch[1+e],card[1+e]) for e in range(ne)]
    parents=list(nodes[1:np+1]);grouped=[]
    for parent in parents:
        req(parent<len(cs) and cs[parent]+cc[parent]<=len(cp),'parent cc span in bounds')
        for t in range(cs[parent],cs[parent]+cc[parent]):
            if cp[t]==0:grouped.append((parent,cn[t],ca[t]))
    req(collections.Counter(original)==collections.Counter(grouped),'complete selected original/parent edge Counter')
    req(len(original)==len(set(original)) and len(parents)==len(set(parents)),'no duplicate writers or parent tasks')
    for p,nh in enumerate([n0,n1]):
        rs=im[3+p];sources={rs[n] for n in parents};dest=[]
        for parent,child,card in original:
            req(parent<len(rs) and child<len(rs) and card<52,'edge operands in bounds');dest.append(rs[child])
        req(len(dest)==len(set(dest)) and sources.isdisjoint(dest),'all parent source rows disjoint from unique output rows')
        req(all((x+1)*nh<=len(seeds[p]) for x in sources|set(dest)),'actual full source/output row extents')
    return original,parents
def fan_expected(im,seeds,n0,n1,edges,active):
    expected=[[],[]];ranges=[[],[]];count=0;source_categories=collections.Counter()
    for p,nh in enumerate([n0,n1]):
        blocked=masks(im,p,nh);rs=im[3+p];cache={}
        for parent in {x[0] for x in edges}:
            start=rs[parent]*nh
            for value in seeds[p][start:start+nh]:
                exp=(value>>23)&255;frac=value&0x7fffff
                if exp==255:source_categories['inf' if frac==0 else 'qnan' if frac&0x400000 else 'snan']+=1
                elif exp==0:source_categories['signed_zero' if frac==0 and value>>31 else 'positive_zero' if frac==0 else 'subnormal']+=1
        if not active:continue
        for parent,child,card in edges:
            key=(parent,card)
            if key not in cache:
                lo=rs[parent]*nh;row=seeds[p][lo:lo+nh]
                for i in blocked[card]:row[i]=0
                cache[key]=row
            lo=rs[child]*nh;expected[p].append((lo,cache[key]));count+=nh
            if nh:ranges[p].append((lo,lo+nh))
    return expected,ranges,count,source_categories

h.custody();req(not(ROOT/'gpu-run.lock').exists(),'native/GPU lease released before raw reader')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
results={};all_categories=collections.Counter()
for category in ['original','fanout']:
    folder=Path(P['folders'][category]);corpus=h.read(folder/'corpus.json');cases=corpus['cases'];done=h.read(folder/'execution/complete.json')
    for p,digest in done['raw_file_sha256'].items():h.pin(p,digest)
    im_magic,out_magic=(b'E086_IN1',b'E086_OUT1') if category=='original' else (b'FAN1_IN\0',b'FAN1OUT\0')
    raw=folder/'output';inp=Reader(raw/'inputs.bin',im_magic);baseline=Reader(raw/'baseline.bin',out_magic);candidate=Reader(raw/'candidate.bin',out_magic)
    if category=='original':
        oldinp=Reader(P['original_reference']['inputs'],b'E086_IN1');oldout=Reader(P['original_reference']['baseline'],b'E086_OUT1')
    output_words=immutable_words=guards=oracle_words=prefix_words=0;families=collections.Counter();full_dealt=set();max_parent=0
    for case in cases:
        cid=case['id'];req(inp.u32()==cid,'input case order');d=list(inp.vec());req(d==case['descriptor'],'frozen descriptor')
        im,seeds=inp.vecs(),inp.vecs()
        if category=='original':
            family,n0,n1,threads,active,mode,perm,width,pattern,salt=d;families[family]+=1
            req(oldinp.u32()==cid and list(oldinp.vec())==d,'all original descriptor IDs retained')
            oldim,oldseed=oldinp.vecs(),oldinp.vecs();req(seeds==oldseed,'all original seeds retained')
            req(im[:11 if family==0 else 12]==oldim,'all original immutable input words retained')
            req(oldout.u32()==cid,'old baseline case order');oldpost,oldoutputs=oldout.vecs(),oldout.vecs()
            req(oldpost==oldim,'old baseline actual immutable images');prefix_words+=sum(map(len,oldim))+sum(map(len,oldseed))+sum(map(len,oldoutputs))
            np,ne=(1,width) if family==0 else (0,0)
        else:
            n0,n1,threads,np,active,mode,pattern,salt=d;family=0;families[0]+=1;ne=sum([0,1,3,7,47-p%3,52][pattern] for p in range(np))
        req(threads in [1,32,64,128,256] and n0<=1326 and n1<=1326,'fixed hand/thread domain')
        expected=ranges=None;copy_words=0
        if family==0:
            edges,parents=mapping(im,np,ne,n0,n1,seeds);expected,ranges,copy_words,categories=fan_expected(im,seeds,n0,n1,edges,bool(active));all_categories.update(categories)
            max_parent=max(max_parent,np)
            if category=='fanout' and active and mode==0 and pattern==5 and n0==n1==1326 and np:
                full_dealt.update(x[2] for x in edges)
        elif family==1:
            req(len(im)==12 and len(seeds)==1,'original up-chance inventory')
            shim=[array.array('I') for _ in range(11)];shim[5]=im[7];shim[7]=im[8];shim[8]=im[9];masks(shim,0,n0)
        else:raise AssertionError('unexpected family')
        previous=None
        for arm in [baseline,candidate]:
            req(arm.u32()==cid,'actual device image case order');post,out=arm.vecs(),arm.vecs()
            req(post==im,'every actual immutable input word preserved');req([len(x) for x in out]==[len(x) for x in seeds],'whole physical output shapes')
            if previous is not None:req(out==previous,'every full original/candidate output word equal')
            else:previous=out
            if category=='original':req(out==oldoutputs,'all original full actual baseline output words unchanged')
            if family==0:
                for p in [0,1]:
                    for lo,wanted in expected[p]:req(out[p][lo:lo+len(wanted)]==wanted,'independent complete bit-copy/mask row oracle')
                    guards+=guard(out[p],seeds[p],ranges[p])
                oracle_words+=copy_words
            else:
                lo=2*(n0+5);guards+=guard(out[0],seeds[0],[(lo,lo+n0)] if active and n0 else [])
            output_words+=sum(map(len,out));immutable_words+=sum(map(len,post))
    for reader in [inp,baseline,candidate]:reader.eof()
    if category=='original':oldinp.eof();oldout.eof();req(len(cases)==425 and families=={0:157,1:268},'entire original corpus retained')
    else:req(len(cases)==7920 and full_dealt==set(range(52)) and max_parent==9,'whole prospective parent matrix and all52/full1326 coverage')
    end=done['raw_marker_summary']
    req(end['cases']==len(cases) and end['kernel_launches']==2*len(cases),'native case/launch accounting')
    req((output_words,immutable_words,guards)==(end['output_words_both_arms'],end['immutable_words_both_arms'],end['guard_words_both_arms']),'entire raw word accounting')
    results[category]={'cases':len(cases),'kernel_launches':2*len(cases),'family_cases':dict(families),'output_words_both_arms':output_words,'immutable_words_both_arms':immutable_words,'guard_words_both_arms':guards,'independent_bitcopy_words_both_arms':oracle_words,'old_original_input_seed_baseline_words_preserved':prefix_words,'raw_file_sha256':done['raw_file_sha256']}
for key in ['inf','qnan','snan','signed_zero','positive_zero','subnormal']:req(all_categories[key]>0,'exceptional source input coverage '+key)
R=ROOT/'comparisons/D195-parent-chance-controls';R.mkdir(exist_ok=False)
h.save(R/'report.json',{'id':'D195','at':h.now(),'status':'pass_scoped_full_raw_parent_fanout_equivalence','checks':checks,'categories':results,
    'cases':sum(x['cases'] for x in results.values()),'kernel_launches':sum(x['kernel_launches'] for x in results.values()),'source_float_categories':dict(all_categories),
    'all_original425_inputs_and_baseline_actual_outputs_preserved':True,'all_actual_immutable_outputs_guards_exact':True,'protocol_sha256':h.sha(H/'protocol.json'),
    'GPU_solve_or_speed_samples':0,'candidate_accepted':False,'limits':'Finite direct copy/chance corpus and actual word-level outputs. Canonical multi-level engine/lifecycle/physical state and full-solve/material/capacity/holdout/application qualification remain required. Error/invalid consumed metadata and all address domains are not proven.'})
h.custody();print(json.dumps({'status':'pass_scoped_full_raw_parent_fanout_equivalence','checks':checks,'cases':sum(x['cases'] for x in results.values()),'categories':{k:{n:v for n,v in x.items() if n!='raw_file_sha256'} for k,x in results.items()}}),flush=True)
