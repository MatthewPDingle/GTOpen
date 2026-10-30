"""Independent full-output reader; CPU setup observations are not solve gains."""
import hashlib,json,mmap,statistics,struct,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D274-spot-observation';P=h.read(H/'protocol.json')
assert len(sys.argv)==2;h.pin(H/'protocol.json',sys.argv[1])
for p,d in P['input_sha256'].items():h.pin(p,d)
h.custody();schema=h.read(P['schema_path']);last=time.monotonic();checks=0
def check(x):
    global checks
    assert x;checks+=1
def progress(label):
    global last
    if time.monotonic()-last>20:print(label,'checks',checks,flush=True);last=time.monotonic()
class Reader:
    def __init__(self,b):self.b=b;self.i=0
    def get(self,fmt):
        s=struct.Struct('<'+fmt);check(self.i+s.size<=len(self.b));v=s.unpack_from(self.b,self.i);self.i+=s.size;return v[0]if len(v)==1 else v
    def take(self,n):check(self.i+n<=len(self.b));v=self.b[self.i:self.i+n];self.i+=n;return v
    def vector(self,fmt):
        n=self.get('Q');s=struct.Struct('<'+fmt);return list(s.iter_unpack(self.take(n*s.size)))
    def end(self):check(self.i==len(self.b))
def one(r,fmt):return[x[0]for x in r.vector(fmt)]
def parse(path,fixture):
    with path.open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
        check(mm[:16]==b'D274-SPOT-v1\0\0\0\0');r=Reader(mm);r.i=16;fields={};extents=[]
        for name in schema['field_order']:
            n=r.get('I');check(r.take(n).decode('utf-8')==name);size=r.get('Q');start=r.i
            fields[name]=r.take(size);extents.append({'field':name,'offset':start,'bytes':size})
        r.end()
    def rd(name):return Reader(fields[name])
    def scalar(name,fmt):
        t=rd(name);v=t.get(fmt);t.end();return v
    def vec(name,fmt):
        t=rd(name);v=one(t,fmt);t.end();return v
    config=json.loads(bytes(vec('config_json','B')));treeconfig=json.loads(bytes(vec('tree_config_json','B')))
    check(config==fixture['config']);check(treeconfig==config['tree']);board=vec('board','B');check(3<=len(board)<=5 and len(set(board))==len(board)and all(c<52 for c in board));bm=scalar('board_mask','Q');check(bm==sum(1<<c for c in board))
    street=len(board)-3;check(scalar('tree_root_street','B')==scalar('river_root_street','B')==street)
    t=rd('hands');check(t.get('Q')==2);hands=[t.vector('BBIQ')for _ in range(2)];t.end();nh=list(map(len,hands));check(all(nh))
    for player in hands:
        check(len({x[3]for x in player})==len(player))
        for c1,c2,w,mask in player:check(c1<52 and c2<52 and c1!=c2 and mask==(1<<c1|1<<c2)and not(mask&bm))
    t=rd('weights');check(t.get('Q')==2);weights=[one(t,'I')for _ in range(2)];t.end()
    t=rd('same_combo');check(t.get('Q')==2);same=[one(t,'I')for _ in range(2)];t.end()
    for p in range(2):
        check(weights[p]==[x[2]for x in hands[p]]and len(same[p])==nh[p]);other={x[3]:i for i,x in enumerate(hands[1-p])}
        check(same[p]==[other.get(x[3],0xffffffff)for x in hands[p]])
    children=vec('tree_children','I');t=rd('tree_actions');na=t.get('Q');action_counts=[0]*5
    for _ in range(na):
        tag=t.get('B');check(tag<5);action_counts[tag]+=1
        if tag>=2:t.get('Q')
    t.end();t=rd('tree_data_size');check(t.get('Q')==2);data=[t.get('Q')for _ in range(2)];t.end()
    t=rd('tree_nodes');nn=t.get('Q');check(nn==fixture['expected_nodes']);sizes=[0,0];kinds=[0]*4
    for node in struct.iter_unpack('<4B2I7Q',t.take(nn*68)):
        kind,player,st,n,cs,ac,offset,putlen,*fp=node;check(kind<4 and player<2 and st<3 and putlen==2);kinds[kind]+=1
        if kind==0:
            check(cs+n<=len(children)and ac+n<=na and offset==sizes[player]);sizes[player]+=n*nh[player]
        elif kind==1:check(n==52 and cs+n<=len(children))
        else:check(n==0)
    t.end();check(sizes==data);check(all(x==0xffffffff or x<nn for x in children));progress('tree '+fixture['fixture'])
    t=rd('river_entries');nr=t.get('Q');check(nr==[2704,52,1][street]);river_lengths=[];some=0
    for i in range(nr):
        extra=([i//52,i%52]if street==0 else[i]if street==1 else[]);valid=(street!=0 or extra[0]<extra[1])and all(not(bm&(1<<c))for c in extra);present=t.get('B');check(present==int(valid))
        if not present:continue
        some+=1;check(t.get('Q')==2);em=sum(1<<c for c in extra)
        for p in range(2):
            values=t.vector('IH');check(values==sorted(values));ids=[v[1]for v in values];check(len(ids)==len(set(ids))and set(ids)=={j for j,x in enumerate(hands[p])if not x[3]&em});river_lengths.append(len(values))
    t.end();t=rd('suit_perms');nk=t.get('Q');perms=[]
    for _ in range(nk):
        check(t.get('Q')==4);pm=[t.get('B')for _ in range(4)];check(sorted(pm)==list(range(4)));check(all(c//4*4+pm[c%4]==c for c in board));perms.append(pm)
    t.end();check(perms[0]==list(range(4)));t=rd('hand_perm');check(t.get('Q')==2);handperm=[]
    for p in range(2):
        check(t.get('Q')==nk);allperm=[]
        for k in range(nk):
            idx=one(t,'H');check(sorted(idx)==list(range(nh[p])));pm=perms[k]
            for j,to in enumerate(idx):
                c1,c2=hands[p][j][:2];mask=1<<(c1//4*4+pm[c1%4])|1<<(c2//4*4+pm[c2%4]);check(hands[p][to][3]==mask)
            allperm.append(idx)
        handperm.append(allperm)
    t.end();caps=vec('data_vector_capacities','Q');lengths=[len(board),nn,len(children),na,nr,nk]
    for p in range(2):lengths +=[nh[p],len(weights[p]),len(same[p]),nk]+[len(x)for x in handperm[p]]
    lengths+=river_lengths;check(len(caps)==14+2*nk+2*some and len(caps)==len(lengths));check(all(c>=n for c,n in zip(caps,lengths)))
    return{'fields':extents,'nodes':nn,'hands':nh,'node_kinds':kinds,'action_variants':action_counts,'river_some':some,'suit_permutations':nk,'capacity_values':len(caps),'all_typed_payload_endpoints_verified':True}
def pair(a,b,fixture):
    check(a.stat().st_size==b.stat().st_size);ha=hashlib.sha256();hb=hashlib.sha256();size=0
    with a.open('rb')as x,b.open('rb')as y:
        while True:
            aa=x.read(8*1024**2);bb=y.read(8*1024**2);check(aa==bb)
            if not aa:break
            size+=len(aa);ha.update(aa);hb.update(bb);progress('full byte comparison')
    check(ha.digest()==hb.digest());shape=parse(a,fixture)
    return{'baseline':str(a),'observed':str(b),'each_bytes':size,'baseline_sha256':ha.hexdigest(),'observed_sha256':hb.hexdigest(),'entire_files_literal_equal':True,'shape':shape}
cases=[];events=[];error_events=[];native=[]
for sequence in P['sequence']:
    identity=sequence['id'];O=H/'execution';exit=h.read(O/(identity+'.exit.json'));check(exit['returncode']==0 and exit['error']is None)
    log=(O/(identity+'.stdout.log')).read_text(encoding='utf-8');check('1 passed; 0 failed;'in log)
    def extract(tag):return[json.loads(line.split(tag+' ',1)[1])for line in log.splitlines()if tag+' 'in line]
    observations=extract('D274_SPOT');errors=extract('D274_ERROR');complete=extract('D274_COMPLETE');check(len(observations)==3 and len(errors)==8 and len(complete)==1)
    check([e['fixture']for e in observations]==[f['fixture']for f in P['fixtures']]);check([e['case']for e in errors]==P['error_cases']);check(complete==[{'fixtures':3,'full_Spot_pairs':3,'error_cases':8,'CFR_iterations_GPU_calls':0}])
    for e in errors:check(e['river_not_started']is True and e['symmetry_not_started']is True and isinstance(e['same_error'],str)and len(e['same_error'])>0)
    for f,e in zip(P['fixtures'],observations):
        check(e['order']==sequence['order']and e['nodes']==f['expected_nodes']and e['worker_count']==16 and e['full_data_native_exact']is True and e['CPU_only']is True and e['CFR_iterations_GPU_calls']==0)
        check(all(e[k]>0 for k in['baseline_ns','observed_ns','tree_ns','river_ns','symmetry_ns','profiled_constructor_ns']));check(e['tree_ns']+e['river_ns']+e['symmetry_ns']<=e['profiled_constructor_ns']<=e['observed_ns'])
        id=f['fixture'];c=pair(H/identity/(id+'-baseline.spot.bin'),H/identity/(id+'-observed.spot.bin'),f);check(c['shape']['hands']==e['hands']);cases.append({'process':identity,'fixture':id,**c})
    events+=observations;error_events+=errors;native.append({'id':identity,'order':sequence['order'],'exit_sha256':h.sha(O/(identity+'.exit.json')),'stdout_sha256':h.sha(O/(identity+'.stdout.log'))});print(identity,'all complete Spot bytes and errors exact',flush=True)
check(len(cases)==P['expected_full_Spot_pairs']and len(error_events)==P['expected_error_pairs']);raw_bytes=sum(2*c['each_bytes']for c in cases);check(raw_bytes<=P['raw_reservation_bytes']);medians=[]
for f in P['fixtures']:
    rows=[x for x in events if x['fixture']==f['fixture']];check(len(rows)==3);m={k[:-3]+'_ms':statistics.median(x[k]for x in rows)/1e6 for k in['baseline_ns','observed_ns','tree_ns','river_ns','symmetry_ns','profiled_constructor_ns']};m['observer_minus_baseline_ms']=m['observed_ms']-m['baseline_ms'];medians.append({'fixture':f['fixture'],**m})
proxy=sum(min(m['tree_ms'],m['river_ms'])for m in medians);h.custody()
report={'id':'D274','at':h.now(),'status':'pass_observer_CPU_full_Spot_only','protocol_sha256':sys.argv[1],'source_review_sha256':h.sha(H/'source-review.json'),'compiler_exit':h.read(H/'execution/compile.exit.json'),'native_processes':native,'full_Spot_pairs':len(cases),'error_pairs':len(error_events),'checks':checks,'raw_retained_bytes':raw_bytes,'literal_paired_bytes':raw_bytes//2,'cases':cases,'observations':events,'errors':error_events,'medians':medians,'idealized_overlap_arithmetic_proxy_ms':proxy,'planning_effort_constant_ms':P['planning_effort_constant_ms'],'proxy_above_effort_constant':proxy>=P['planning_effort_constant_ms'],'source_candidate_created':False,'new_GPU_CFR_solver_or_speed_samples':0,'scope_limits':P['scope']+' '+P['interpretation'],'next_contract_review':'Only effort triage. Timers do not admit an optimization. Any overlap still needs supported max_nodes/validation/error ordering, speculative work, worker/FPU/cleanup/peak contracts and every existing exactness and complete-cycle performance gate.'}
h.save(H/'report.json',report);print(json.dumps({'status':report['status'],'pairs':len(cases),'errors':len(error_events),'raw_bytes':raw_bytes,'medians':medians,'proxy_ms':proxy}),flush=True)
