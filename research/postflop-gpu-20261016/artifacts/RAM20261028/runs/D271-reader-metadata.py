"""Injected root reader helpers; complete original data retained, no GPU runs."""
import array, importlib.util, json, re
_spec=importlib.util.spec_from_file_location('d267io',ROOT/'runs/D267b-model-io.py')
d271io=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(d271io)
D271_ROWS=set(P['metadata_row_fields']);D271_IDS=set(P['metadata_ID_fields'])
D271_MAPS={};D271_BINDINGS=[];D271_EXTENTS=[];D271_CORE_SELECTED=0;D271_EXTRA_SELECTED=0
def d271_setup():
    global D271_BINDINGS,D271_CORE_SELECTED,D271_EXTRA_SELECTED
    log=(H/'execution/probe.stdout.log').read_text(encoding='utf-8')
    D271_BINDINGS=[json.loads(line.split('D271_METADATA_BIND ',1)[1])for line in log.splitlines()if'D271_METADATA_BIND 'in line]
    req(len(D271_BINDINGS)==156,'all144original plus12extra actual constructor bindings')
    schema=[n for n,t in h.read(P['schema_path'])['fields']]
    for index,marker in enumerate(D271_BINDINGS):
        arm=index%2;call=index//2+1
        req(marker['arm']==arm and marker['call']==call,'actual constructor arm and source order')
        path=O/marker['plan_file'];raw=d271io.plans(path,schema);nn=struct.unpack('<Q',raw['num_nodes'])[0]
        kinds=(O/marker['kinds_file']).read_bytes();req(len(kinds)==nn,'whole original CPU node-kind inventory')
        na=d271io.vec(raw['node_na'],'I');player=d271io.vec(raw['node_player'],'I');cdiv=d271io.vec(raw['node_cdiv'],'I');data=d271io.vec(raw['node_data_off'],'Q')
        nh=struct.unpack('<QQQ',raw['nh']);ae=struct.unpack('<QQQ',raw['arena_elements']);req(nh[0]==ae[0]==2,'full original CPU plan two-player framing')
        physical=[0,0];mismatch=[False,False]
        for node,kind in enumerate(kinds):
            req(kind in P['kind_constants'].values(),'known original node kind')
            if kind==P['kind_constants']['KIND_ACTION']:
                p=int(player[node]);req(p in[0,1]and 0<int(na[node])<=250 and cdiv[node]==0,'original CPU action shape')
                mismatch[p]|=int(data[node])!=physical[p];physical[p]+=int(na[node])*nh[p+1]
            elif kind==P['kind_constants']['KIND_CHANCE']:req(na[node]==52 and cdiv[node]!=0,'original CPU chance shape')
            else:req(na[node]==0 and cdiv[node]==0,'original CPU terminal shape')
        info=marker['info'];compact=[ae[p+1]!=physical[p]or mismatch[p]for p in range(2)]
        req(info['nodes']==nn and info['hands']==list(nh[1:])and info['CPU_data_size']==physical,'actual original CPU geometry')
        req(info['compact']==compact and info['pinned_words']==max(ae[1:])and info['pinned_alignment8']and info['wrapper_bytes']==4448,'actual layout/pinned/type inputs')
        capable=all(compact)and max(8*nn,4*info['children'])<=4*info['pinned_words']
        req(info['independently_expected_capability']==capable,'independently recomputed exact capability')
        ordered=capable if arm else False;req(info['ordered']==ordered,'actual constructor selected/original source branch')
        inverse=[];seen=set()
        if ordered:
            nlevels=struct.unpack('<Q',raw['num_levels'])[0]
            for level in range(nlevels):
                for nodes,spans in [('action_nodes','action_spans'),('chance_nodes','chance_node_spans'),('fold_nodes','fold_spans'),('show_nodes','show_spans')]:
                    a,count=d271io.spans(raw[spans])[level];part=d271io.vec(raw[nodes],'I')[a:a+count]
                    req(not seen.intersection(part),'unique original whole frontier IDs');inverse.extend(part);seen.update(part)
            inverse.extend(i for i in range(nn)if i not in seen)
        else:inverse=list(range(nn))
        req(len(inverse)==len(set(inverse))==nn and inverse[0]==0,'complete total original-node permutation')
        forward=np.empty(nn,dtype='<u4');forward[np.asarray(inverse,dtype='<u4')]=np.arange(nn,dtype='<u4');inverse=np.asarray(inverse,dtype='<u4')
        actual=d271io.read_projection(O/marker['maps_file'])
        req(set(actual)=={'old_to_new','new_to_old'}and np.array_equal(forward,np.asarray(actual['old_to_new'],dtype='<u4'))and np.array_equal(inverse,np.asarray(actual['new_to_old'],dtype='<u4')),'all observed map words match independent original plan')
        D271_MAPS[(arm,call)]={'forward':forward,'inverse':inverse,'ordered':ordered,'raw':raw,'kinds':kinds,'info':info}
        if arm:
            b=D271_BINDINGS[index-1]
            req((O/b['plan_file']).read_bytes()==path.read_bytes()and(O/b['kinds_file']).read_bytes()==kinds,'whole original53field plans/kinds identical per constructor pair')
            if call<=72:D271_CORE_SELECTED+=ordered
            else:D271_EXTRA_SELECTED+=ordered
        for key in ['plan_file','maps_file','kinds_file']:
            f=O/marker[key];D271_EXTENTS.append({'path':str(f),'bytes':f.stat().st_size,'sha256':h.sha(f)})
    req(0<D271_CORE_SELECTED<72 and 0<D271_EXTRA_SELECTED<6,'positive selected and original fallback paths in core and extra controls')
    ptx=[json.loads(line.split('D271_PTX_BIND ',1)[1])for line in log.splitlines()if'D271_PTX_BIND 'in line]
    req(len(ptx)==156 and all(x['arm']==i%2 and x['call']==i//2+1 and x['architecture']=='compute_120'for i,x in enumerate(ptx)),'all identical sealed accepted PTX bindings')

def d271_map_for(path):
    if path.parent.parent.name=='extra':return D271_MAPS[(1,73+int(path.parent.name))]
    m=re.match(r'clobber(?:ed)?-(\d+)-(.+)',path.name)
    if not m:return None
    ident=int(m.group(1));stage=m.group(2);resume=stage.startswith('resumed-')or stage.startswith('continuation-')
    return D271_MAPS[(1,2*ident+1+int(resume))]

def d271_normalize(path,name,v):
    mapping=d271_map_for(path)
    if mapping is None:return v
    forward,inverse=mapping['forward'],mapping['inverse']
    if name in D271_ROWS:
        width=2 if name in['d_node_data_off','d_lock_off']else 1
        req(len(v)==len(forward)*width,'full actual metadata row width '+name)
        return v.reshape(len(forward),width)[forward].reshape(-1)
    if name in D271_IDS:
        out=v.copy();valid=out!=0xffffffff
        req(not np.any(out[valid]>=len(inverse)),'all actual GPU node IDs in original bounds '+name)
        out[valid]=inverse[out[valid]];return out
    return v

def d271_whole_constructor(path):
    data=bytearray(path.read_bytes());req(data[:16]==b'D150-FRAME-v1\0\0\0','whole actual constructor magic')
    at=16
    while at<len(data):
        kind,n=struct.unpack_from('<II',data,at);at+=8;name=data[at:at+n].decode();at+=n;count=struct.unpack_from('<Q',data,at)[0];at+=8
        if kind==0:req(struct.unpack_from('<I',data,at)[0]==0,'whole actual constructor zero run');at+=4
        else:
            req(kind==1,'whole actual constructor reference/actual kind')
            for _ in range(2):
                v=np.frombuffer(data,dtype='<u4',count=count,offset=at).copy();data[at:at+count*4]=d271_normalize(path,name,v).tobytes();at+=count*4
    req(at==len(data),'whole actual constructor all bytes visited');return bytes(data)

def d271_extra_reader():
    global expected_algo,requested_iso
    extras=h.read(O/'extra-metadata.json');req(len(extras)==6,'all fixed extra GPU lock cases')
    expected=[('Compressed','Dcfr',True,'Ks7s2d'),('Compressed','CfrPlus',True,'Ks7s2d'),('F32','Dcfr',True,'Ks7s2d'),('Compressed','Dcfr',False,'Ks7s2d'),('Compressed','Dcfr',True,'KsQs2dJd'),('Compressed','Dcfr',True,'Ks7s2dQhTc')]
    evcount=0;selected_nonaction=selected_action=0
    for ident,(row,dims)in enumerate(zip(extras,expected)):
        req(row['case']==ident and(row['storage'],row['algorithm'],row['iso'],row['board'])==dims,'fixed full extra dimensions')
        expected_algo=0 if dims[1]=='Dcfr'else 1;requested_iso=dims[2]
        base=O/'extra'/str(ident);mapping=D271_MAPS[(1,73+ident)];req(row['selected']==mapping['ordered'],'extra actual constructor source branch')
        p=mapping['raw'];kinds=mapping['kinds'];offset=d271io.vec(p['node_data_off'],'Q');forward=mapping['forward']
        for cat in row['categories']:
            key=cat['category'];possible=[]
            for node,kind in enumerate(kinds):
                action=kind==P['kind_constants']['KIND_ACTION']
                yes=(node==0)if key=='root'else(node>0 and action and offset[node]!=0xffffffffffffffff)if key=='active_action'else(node>0 and action and offset[node]==0xffffffffffffffff)if key=='inactive_action'else kind==P['kind_constants'][{'chance':'KIND_CHANCE','fold':'KIND_TERM_FOLD','show':'KIND_TERM_SHOWDOWN'}[key]]
                if yes:possible.append(node)
            selected=next((i for i in possible if forward[i]!=i),possible[0]if possible else None)
            req(cat['available']==len(possible)and cat['chosen']==selected and cat['changed_ID']==(selected is not None and forward[selected]!=selected),'full CPU category selection and changed-ID witness')
            if row['selected']and cat['changed_ID']:
                selected_action+=key=='active_action';selected_nonaction+=key in['chance','fold','show']
        req(len(row['categories'])==6 and[row['stage']for row in row['phases']]==['warm','lock-upload','locked','unlock-upload','unlocked'],'every extra phase retained')
        a=base/'baseline-constructor.bin';b=base/'clobbered-constructor.bin'
        req(a.read_bytes()==d271_whole_constructor(b),'all extra constructor frame bytes after metadata inverse')
        af=frame(a,b'D150-FRAME-v1\0\0\0');bf=frame(b,b'D150-FRAME-v1\0\0\0')
        req(len(af)==66 and set(af)==set(bf)and all(eq(af[k],bf[k])for k in af),'all extra actual66 constructor fields')
        locked=None
        for phase in row['phases']:
            stage=phase['stage'];info=phase['info'];a=gpu(base/f'baseline-{stage}.gpu.bin',info);b=gpu(base/f'clobbered-{stage}.gpu.bin',info)
            req(all(eq(a[k],b[k])for k in gpunames),'all70extra fields/physical CFV exact after metadata inverse')
            if stage in['lock-upload','unlock-upload']:req(not info['graphs_present']and info['eval_graphs_present']==[False,False],'actual lock buffer graph invalidation')
            if stage=='lock-upload':
                locked=b['d_lock_off'].view('<i8').copy();chosen={x['chosen']for x in row['categories']if x['chosen']is not None}
                req(set(np.flatnonzero(locked>=0).tolist())==chosen,'all chosen action/nonaction locks actually uploaded at original IDs')
                for cat in row['categories']:
                    node=cat['chosen']
                    if node is not None and cat['category']in['chance','fold','show']:
                        start=int(locked[node]);req(b['d_lock_sigma'][start:start+4].tolist()==[0,0x80000000,0x7fc00123,0x7f800123],'actual manual nonaction sigma payload bits')
            if stage=='unlock-upload':req(np.all(b['d_lock_off']==0xffffffff)and b['d_lock_sigma'].tolist()==[0],'all actual lock rows cleared/dummy restored')
        a=base/'baseline-final.cpu.bin';b=base/'clobbered-final.cpu.bin';req(a.read_bytes()==b.read_bytes(),'all extra CPU/qscale/state bytes')
        af=frame(a,b'D150-STATE-v1\0\0\0');bf=frame(b,b'D150-STATE-v1\0\0\0');req(set(af)==set(bf)and all(eq(af[k],bf[k])for k in af),'full extra CPU raw fields')
        req(len(row['EV_bits'])==9 and all(math.isfinite(struct.unpack('<d',struct.pack('<Q',x))[0])for x in row['EV_bits']),'all9 finite exact extra EVs');evcount+=9
    req(selected_action>0 and selected_nonaction>0,'selected nonroot action and manual nonaction changed-ID witnesses')
    return {'cases':6,'phase_pairs':30,'EV_pairs':evcount,'constructor_pairs':6,'selected_cases':D271_EXTRA_SELECTED,'changed_active_action_lock_witnesses':selected_action,'changed_nonaction_lock_witnesses':selected_nonaction,'all66device_plus_whole_physical_CFV_and_CPU_exact':True}
