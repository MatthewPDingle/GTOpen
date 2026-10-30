"""Full canonical raw comparison with only the frozen node-identity inverse."""
import array,importlib.util
import numpy as np
_spec=importlib.util.spec_from_file_location('d267io',ROOT/'runs/D267b-model-io.py');d272io=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(d272io)
D272_MAPS={};D272_MAP_EXTENTS=[];D272_LITERAL_GPU_BYTES=0;D272_METADATA_BYTES=0;D272_HEADERS_BYTES=0
def d272_setup():
    schema=[n for n,t in h.read(P['schema_path'])['fields']]
    for arm in P['sequence']:
        log=(H/'execution'/(arm+'.stdout.log')).read_text(encoding='utf-8')
        records=[json.loads(line.split('D272_METADATA ',1)[1])for line in log.splitlines()if'D272_METADATA 'in line]
        req([(r['fixture'],r['constructor'])for r in records]==[(name,c)for name in['rainbow','two-tone','river']for c in['initial','resumed']],'all6 actual constructor map captures per arm')
        for r in records:
            req(r['arm']==arm,'actual canonical source arm');folder=H/(arm+'-output')
            raw=d272io.plans(folder/r['plan_file'],schema);kinds=(folder/r['kinds_file']).read_bytes();nn=struct.unpack('<Q',raw['num_nodes'])[0]
            req(len(kinds)==nn,'whole original node-kind inventory');na=d272io.vec(raw['node_na'],'I');players=d272io.vec(raw['node_player'],'I');cdiv=d272io.vec(raw['node_cdiv'],'I');off=d272io.vec(raw['node_data_off'],'Q')
            nh=struct.unpack('<QQQ',raw['nh']);ae=struct.unpack('<QQQ',raw['arena_elements']);req(nh[0]==ae[0]==2,'whole original2player CPU plan')
            physical=[0,0];mismatch=[False,False]
            for node,kind in enumerate(kinds):
                req(kind in P['kind_constants'].values(),'known original node kind')
                if kind==P['kind_constants']['KIND_ACTION']:
                    p=int(players[node]);req(p in[0,1]and 0<int(na[node])<=250 and cdiv[node]==0,'actual original action shape')
                    mismatch[p]|=int(off[node])!=physical[p];physical[p]+=int(na[node])*nh[p+1]
                elif kind==P['kind_constants']['KIND_CHANCE']:req(na[node]==52 and cdiv[node]!=0,'actual original chance shape')
                else:req(na[node]==0 and cdiv[node]==0,'actual original terminal shape')
            info=r['info'];compact=[ae[p+1]!=physical[p]or mismatch[p]for p in range(2)]
            req(info['nodes']==nn and info['CPU_data_size']==physical and info['hands']==list(nh[1:]),'actual full CPU geometry')
            req(info['compact']==compact and info['pinned_words']==max(ae[1:])and info['pinned_alignment8']and info['wrapper_bytes']==4448,'actual host/pinned layout inputs')
            capable=all(compact)and max(8*nn,4*info['children'])<=4*info['pinned_words'];ordered=capable and arm=='candidate'
            req(info['independently_expected_capability']==capable and info['ordered']==ordered,'actual constructor selection independently derived')
            inverse=[];seen=set()
            if ordered:
                levels=struct.unpack('<Q',raw['num_levels'])[0]
                for level in range(levels):
                    for name,span in[('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')]:
                        a,count=d272io.spans(raw[span])[level];part=d272io.vec(raw[name],'I')[a:a+count];req(not seen.intersection(part),'unique complete frontier IDs');inverse.extend(part);seen.update(part)
                inverse.extend(i for i in range(nn)if i not in seen)
            else:inverse=list(range(nn))
            req(len(inverse)==len(set(inverse))==nn and inverse[0]==0,'total full canonical permutation')
            forward=np.empty(nn,dtype='<u4');forward[np.asarray(inverse,dtype='<u4')]=np.arange(nn,dtype='<u4');inverse=np.asarray(inverse,dtype='<u4')
            maps=d272io.read_projection(folder/r['maps_file']);req(set(maps)=={'old_to_new','new_to_old'},'complete actual map inventory')
            req(np.array_equal(forward,np.asarray(maps['old_to_new'],dtype='<u4'))and np.array_equal(inverse,np.asarray(maps['new_to_old'],dtype='<u4')),'every map word matches independent original plan')
            key=(arm,r['fixture'],r['constructor']);D272_MAPS[key]={'forward':forward,'inverse':inverse,'ordered':ordered,'info':info}
            for label in['plan_file','maps_file','kinds_file']:
                path=folder/r[label];D272_MAP_EXTENTS.append({'path':str(path),'bytes':path.stat().st_size,'sha256':h.sha(path)})
            if arm=='candidate':
                other=H/'baseline-output'
                req((other/r['plan_file']).read_bytes()==(folder/r['plan_file']).read_bytes()and(other/r['kinds_file']).read_bytes()==kinds,'all original53plan/kind bytes identical per constructor pair')
    selected=[(f,c)for(a,f,c),v in D272_MAPS.items()if a=='candidate'and v['ordered']]
    req(selected==[('two-tone','initial'),('two-tone','resumed')],'fixed original compact-layout application; all rainbow/river fallbacks remain')

def d272_normalize(name,raw,mapping):
    v=np.frombuffer(raw,dtype='<u4');forward,inverse=mapping['forward'],mapping['inverse']
    if name in P['metadata_row_fields']:
        width=2 if name in['d_node_data_off','d_lock_off']else 1
        req(len(v)==len(forward)*width,'whole metadata row shape '+name);return v.reshape(len(forward),width)[forward].reshape(-1).tobytes()
    req(name in P['metadata_ID_fields'],'declared metadata transform only');out=v.copy();valid=out!=0xffffffff
    req(not np.any(out[valid]>=len(inverse)),'all node-ID values in original bounds '+name);out[valid]=inverse[out[valid]];return out.tobytes()

def d272_gpu_pair(a,b,fixture,stage):
    global pair_bytes,D272_LITERAL_GPU_BYTES,D272_METADATA_BYTES,D272_HEADERS_BYTES
    req(a.stat().st_size==b.stat().st_size,'whole GPU raw file shape');da=hashlib.sha256();db=hashlib.sha256()
    mapping=D272_MAPS[('candidate',fixture,'resumed'if stage=='resumed'else'initial')]
    metadata=set(P['metadata_row_fields'])|set(P['metadata_ID_fields']);names=['iteration','algorithm','hands']+inventory
    def read_same(x,y,n,kind):
        global pair_bytes,D272_HEADERS_BYTES,D272_LITERAL_GPU_BYTES
        left=x.read(n);right=y.read(n);req(len(left)==len(right)==n and left==right,'every literal GPU '+kind+' byte')
        da.update(left);db.update(right);pair_bytes+=n
        if kind=='header':D272_HEADERS_BYTES+=n
        else:D272_LITERAL_GPU_BYTES+=n
        return left
    with a.open('rb')as x,b.open('rb')as y:
        req(read_same(x,y,16,'header')==b'D166-GPU-RAW1\0\0\0','whole actual GPU frame magic')
        for expected in names:
            kind,length=struct.unpack('<II',read_same(x,y,8,'header'));req(0<length<512,'whole GPU bounded field name')
            name=read_same(x,y,length,'header').decode();count,=struct.unpack('<Q',read_same(x,y,8,'header'));req(name==expected and count<=2**31,'whole GPU field order/count')
            if kind==0:req(read_same(x,y,4,'literal')==b'\0'*4,'whole actual positive-zero run')
            else:
                req(kind==2,'whole actual GPU literal encoding')
                if name in metadata and mapping['ordered']:
                    left=x.read(count*4);right=y.read(count*4);req(len(left)==len(right)==count*4,'full actual metadata extent')
                    da.update(left);db.update(right);req(left==d272_normalize(name,right,mapping),'every full metadata word after only identity inverse '+name)
                    pair_bytes+=len(left);D272_METADATA_BYTES+=len(left)
                else:
                    remaining=count*4
                    while remaining:
                        n=min(1024*1024,remaining);read_same(x,y,n,'literal');remaining-=n
        req(x.tell()==a.stat().st_size and y.tell()==b.stat().st_size and not x.read(1)and not y.read(1),'whole69field GPU endpoints no omissions')
    hashes[str(a)]={'bytes':a.stat().st_size,'sha256':da.hexdigest()};hashes[str(b)]={'bytes':b.stat().st_size,'sha256':db.hexdigest()}
