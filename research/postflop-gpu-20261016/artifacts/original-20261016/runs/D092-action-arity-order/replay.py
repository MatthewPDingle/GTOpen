"""Stream complete CPU plan dumps and independently check concrete ownership."""
import array, hashlib, json, math, struct, sys
from pathlib import Path
H=Path(__file__).resolve().parent
SCHEMA=json.loads((H/'field-schema.json').read_text())['fields']
def replay(path, identity):
    checks=0
    def req(v,label):
        nonlocal checks
        assert v,(identity,label)
        checks+=1
    def vector(f):
        n,=struct.unpack('<Q',f.read(8));req(n<=100000000,'bounded word count')
        v=array.array('Q');v.fromfile(f,n)
        if sys.byteorder!='little':v.byteswap()
        req(len(v)==n,'complete word count')
        return v
    wanted={'num_levels','nh','num_nodes','action_nodes','action_spans','node_player','node_na','node_children_start','node_data_off','arena_elements','reach_slot','cfv_slot','cfv_blocks','reach_blocks'}
    fields={};baseline_words=0;nonorder_words=0
    with path.open('rb') as f:
        req(f.read(16)==b'D092-PLAN-RAW1\0\0','magic')
        i,n=struct.unpack('<II',f.read(8));req(i==identity and n==len(SCHEMA)==53,'case and schema')
        sa,sb=struct.unpack('<QQ',f.read(16));req(sa==sb and sa>0,'actual struct sizes')
        for index,definition in enumerate(SCHEMA):
            fieldid,=struct.unpack('<I',f.read(4));req(fieldid==index,'field identity')
            ca,cb,wa,wb=[vector(f) for _ in range(4)]
            req(ca==cb,'all actual field capacities equal')
            if definition['name']!='action_nodes':
                req(wa==wb,definition['name']+' exact full bits')
                nonorder_words+=len(wa)
            baseline_words+=len(wa)
            if definition['name'] in wanted:fields[definition['name']]=(wa,wb)
        kinds=vector(f);children=vector(f)
        req(f.read(1)==b'','raw endpoint')
    def scalar(name):
        v=fields[name][0];req(len(v)==1,'scalar '+name);return v[0]
    def vec(name,arm=0):
        v=fields[name][arm];req(v[0]==len(v)-1,'flat Vec '+name);return v[1:]
    def fixed(name):
        v=fields[name][0];req(v[0]==2 and len(v)==3,'array '+name);return v[1:]
    def pairvec(name):
        v=fields[name][0];req(v[0]==2,'two vectors '+name)
        n=v[1];x=v[2:2+n];k=2+n;m=v[k];y=v[k+1:];req(len(y)==m,'second vector '+name);return [x,y]
    levels=scalar('num_levels');nodes=scalar('num_nodes');cfv_blocks=scalar('cfv_blocks')
    nh=fixed('nh');arena=fixed('arena_elements');reach_blocks=fixed('reach_blocks')
    a=vec('action_nodes');b=vec('action_nodes',1)
    rawsp=fields['action_spans'][0];req(rawsp[0]==levels and len(rawsp)==1+levels*2,'level spans')
    player=vec('node_player');na=vec('node_na');start=vec('node_children_start');off=vec('node_data_off');cfv=vec('cfv_slot');reach=pairvec('reach_slot')
    req(kinds[0]==nodes and all(len(v)==nodes for v in [player,na,start,off,cfv,*reach]),'complete node maps')
    req(children[0]==len(children)-1,'full tree child inventory');children=children[1:];kinds=kinds[1:]
    transitions_a=0;transitions_b=0;changed=0;changed_levels=0;intervals=[[],[]];at=0;readwrites=0;childreads=0
    for level in range(levels):
        lo,count=rawsp[1+2*level:3+2*level];req(lo==at,'contiguous original spans');at+=count
        av=a[lo:lo+count];bv=b[lo:lo+count]
        req(sorted(av)==sorted(bv),'same per-level complete node multiset')
        req(all(na[bv[j]]<=na[bv[j+1]] for j in range(max(0,len(bv)-1))),'ascending actual arity')
        different=sum(x!=y for x,y in zip(av,bv));changed+=different;changed_levels+=bool(different)
        transitions_a+=sum(na[x]!=na[y] for x,y in zip(av,av[1:]));transitions_b+=sum(na[x]!=na[y] for x,y in zip(bv,bv[1:]))
        inputs=set();outputs=set();cfvouts=set();cfvins=set()
        for node in av:
            p=player[node];req(node<nodes and kinds[node]==0 and p in [0,1] and na[node]>0,'active valid action')
            req(reach[p][node]<reach_blocks[p] and cfv[node]<cfv_blocks,'input address bounds')
            inputs.add((p,reach[p][node]));req(cfv[node] not in cfvouts,'unique current-level CFV writes');cfvouts.add(cfv[node])
            end=off[node]+na[node]*nh[p];req(off[node]<end<=arena[p],'bounded learning interval');intervals[p].append((off[node],end))
            cs=start[node];req(cs+na[node]<=len(children),'all action children bounded')
            for child in children[cs:cs+na[node]]:
                req(child<nodes and reach[p][child]<reach_blocks[p] and cfv[child]<cfv_blocks,'child bounds')
                key=(p,reach[p][child]);req(key not in outputs,'unique down-action reach writes');outputs.add(key);cfvins.add(cfv[child]);childreads+=1
        req(not inputs.intersection(outputs),'down-action reads disjoint from all same-level writes')
        req(not cfvins.intersection(cfvouts),'up-action child reads disjoint from all same-level writes')
        readwrites+=len(outputs)
    req(at==len(a)==len(b),'all work-list entries covered')
    for p in [0,1]:
        z=sorted(intervals[p]);req(all(x[1]<=y[0] for x,y in zip(z,z[1:])),'globally disjoint actor learning intervals')
    native=[json.loads(line.split('D092 ',1)[1]) for line in path.with_suffix('.stdout.log').read_text().splitlines() if line.startswith('D092 ')]
    req(len(native)==1,'one complete native result');v=native[0]
    req(v['id']==identity and v['fields']==53 and v['baseline_words']==baseline_words and v['action_nodes']==len(a) and v['nodes']==nodes,'native/raw inventory')
    req(all(math.isfinite(v[k]) and v[k]>0 for k in ['baseline_plan_ms','candidate_plan_ms']),'finite diagnostic timings')
    return dict(v,root_checks=checks,all_nonorder_words_exact=nonorder_words,raw_file=str(path),raw_bytes=path.stat().st_size,raw_sha256=hashlib.file_digest(path.open('rb'),'sha256').hexdigest(),reordered_positions=changed,changed_levels=changed_levels,baseline_arity_transitions=transitions_a,candidate_arity_transitions=transitions_b,concrete_down_write_rows_checked=readwrites,concrete_child_reads_checked=childreads,struct_bytes=sa,ownership_pass=True)
