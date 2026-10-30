import sys,json,struct,math,hashlib
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for path,digest in P['input_sha256'].items():h.pin(path,digest)
anchor=h.read(ROOT/'epoch/exact-anchor.json');inventory=h.read(H/'source-review.json')['device_field_inventory']
checks=pair_bytes=represented_words=0;hashes={}
def req(condition,label):
    global checks
    assert condition,label;checks+=1
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

def pair(a,b):
    global pair_bytes
    req(a.stat().st_size==b.stat().st_size,'whole file sizes');digest=hashlib.sha256()
    with a.open('rb') as x,b.open('rb') as y:
        while True:
            left=x.read(1024*1024);right=y.read(1024*1024);req(left==right,'every retained pair byte')
            if not left:break
            pair_bytes+=len(left);digest.update(left)
    hashes[str(a)]={'bytes':a.stat().st_size,'sha256':digest.hexdigest()};hashes[str(b)]={'bytes':b.stat().st_size,'sha256':digest.hexdigest()}
def gpu_frame(path,info):
    global represented_words
    names=['iteration','algorithm','hands']+inventory;desc={x['name']:x for x in info['device_fields']}
    req(len(desc)==66 and list(desc)==inventory,'all actual66buffer descriptors andorder');req(info['host_fields']==3,'host field count')
    with path.open('rb') as f:
        req(f.read(16)==b'D166-GPU-RAW1\0\0\0','GPU frame magic')
        for name in names:
            kind,length=struct.unpack('<II',f.read(8));req(0<length<512,'boundedfieldname');actual=f.read(length).decode();count,=struct.unpack('<Q',f.read(8));req(name==actual,'complete unique field inventory');req(count<=2**31,'boundedactualfieldsize')
            if name in desc:
                d=desc[name];req(d['element_bytes'] in [4,8] and d['elements']*d['element_bytes']==d['words']*4==d['raw_bytes'] and d['words']==count,'exact original dtype and physical word extent')
                req(d['raw_bytes']<=8*1024**3,'native field staging bound')
                if name=='d_cfv':req(count==info['CFV_words'],'entire physical CFV')
            else:req(count==(2 if name=='hands' else 1),'host scalar extent')
            if kind==0:
                req(f.read(4)==b'\0'*4,'lossless positive-zero run')
                values=[0]*count if name not in desc else None
            else:
                req(kind==2,'literal full raw encoding')
                if name not in desc:values=list(struct.unpack('<'+'I'*count,f.read(4*count)))
                else:f.seek(4*count,1);values=None
            if name=='iteration':req(values==[info['iteration']],'actual iteration scalar')
            elif name=='algorithm':req(values==[0]==[info['algorithm']],'actual DCFR scalar')
            elif name=='hands':req(values==info['hands'],'actualhandcounts')
            represented_words+=count
        req(f.tell()==path.stat().st_size and f.read(1)==b'','whole69field frame endpoint')
def cpu_frame(path,iteration):
    global represented_words
    with path.open('rb') as f:
        req(f.read(16)==b'D156-CPU-RAW1\0\0\0','CPUmagic');it,iso,locks,preds=struct.unpack('<IIII',f.read(16));req(it==iteration and iso==1 and preds==0,'CPUpublicationstate')
        for kind in [1,1,2,2]:
            actual,=struct.unpack('<I',f.read(4));n,sc=struct.unpack('<QQ',f.read(16));req(actual==kind,'Store type');req(n<2**32 and sc<2**32,'boundedStoreextent');f.seek(2*n+4*sc,1);represented_words+=n+sc
        req(f.tell()==path.stat().st_size,'whole CPUq/scale endpoint')
d272_setup()
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms','runtime_nvrtc_jit_included'}
logs={};science_counts=[]
for arm in P['sequence']:
    text=(H/'execution'/(arm+'.stdout.log')).read_text(encoding='utf-8');results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x];stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    req(len(results)==3 and all(x['runtime_nvrtc_jit_included'] is False for x in results),'honest diagnostic prebuilt PTX telemetry')
    req([x for x in text.splitlines() if x.startswith('D272_BIND ')]==['D272_BIND '+arm]*P['expected_PTX_bindings_per_arm'],'actual sealed module bindings forinitial/resume')
    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    req([[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==[[{k:v for k,v in x.items() if k not in excluded} for x in anchor[0]],anchor[1]],'every unchanged full science/config/state/stopping record and23checkpoints')
    controls=[json.loads(x.split('D156_CONTROL ',1)[1]) for x in text.splitlines() if x.startswith('D156_CONTROL ')]
    req([x['fixture_id'] for x in controls]==['rainbow','two-tone','river'],'original fixed fixture order');req('test result: ok. 1 passed; 0 failed; 0 ignored;' in text,'test terminal pass');logs[arm]=controls;science_counts.append([len(results),len(conv)])
    resource=h.read(H/'execution'/(arm+'.resource.json'));L=P['limits'];req(resource['sample_count']>0,'memory guard observed samples');req(resource['reported_peak_working_set_bytes']<=L['process_reported_peak_max_bytes'] and resource['reported_peak_commit_bytes']<=L['process_reported_peak_max_bytes'],'observedreportedprocesspeakswithincap');req(resource['minimum_observed_available_RAM_bytes']>=L['available_RAM_during_bytes'],'available RAM observations')
cpu=gpu=query=save=evs=0
for b,c in zip(logs['baseline'],logs['candidate']):
    name=b['fixture_id'];req(name==c['fixture_id'] and b['all_GPU_and_CPU_objects_dropped'] and c['all_GPU_and_CPU_objects_dropped'],'samefixture/terminalownership')
    req([x['stage'] for x in b['stages']]==[x['stage'] for x in c['stages']]==P['lifecycle_stages'],'orderedfixedlifecycle')
    for bs,cs in zip(b['stages'],c['stages']):
        stage=bs['stage'];req(bs==cs,'every EV/iteration/fielddtype/count/geometry/graph/wrappermetadatabit exact')
        if bs['ev_bits'] is not None:req(math.isfinite(struct.unpack('<d',struct.pack('<Q',bs['ev_bits']))[0]),'finite futureEV');evs+=1
        bo=H/'baseline-output';co=H/'candidate-output'
        a,z=bo/f'{name}-{stage}.cpu.bin',co/f'{name}-{stage}.cpu.bin';pair(a,z);cpu_frame(a,bs['iteration']);cpu_frame(z,cs['iteration']);cpu+=1
        a,z=bo/f'{name}-{stage}.gpu.bin',co/f'{name}-{stage}.gpu.bin';d272_gpu_pair(a,z,name,stage);gpu_frame(a,bs['info']);gpu_frame(z,cs['info']);gpu+=1
        print('D166 raw reader',name,stage,'complete',flush=True)
    for stage in ['locked','resumed']:pair(H/'baseline-output'/f'{name}-{stage}.query.json',H/'candidate-output'/f'{name}-{stage}.query.json');query+=1
    pair(H/'baseline-output'/f'{name}.save',H/'candidate-output'/f'{name}.save');save+=1
req(cpu==gpu==12 and query==6 and save==3 and evs==9,'entire fixed lifecycle inventory');req(science_counts==[[3,23],[3,23]],'complete6records46checkpoints')
raw_bytes=sum(p.stat().st_size for d in H.glob('*-output') for p in d.iterdir() if p.is_file());req(raw_bytes<=P['limits']['raw_reservation_bytes'],'raw output withinreservation')
h.custody();D=ROOT/'comparisons/D272-metadata-canonical-v2';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D272','at':h.now(),'status':'pass_scoped_full_canonical_all_device_and_CPU_raw_lifecycle','protocol_sha256':h.sha(H/'protocol.json'),'scientific_full_records_exact':6,'canonical_checkpoints_exact':46,'CPU_raw_pairs':cpu,'GPU_all69field_pairs':gpu,'actual_device_buffers_per_frame':66,'host_fields_per_GPU_frame':3,'query_pairs':query,'save_pairs':save,'future_EV_pairs':evs,'reader_checks':checks,'pair_bytes_compared':pair_bytes,'represented_GPU_and_CPU_words_both_arms':represented_words,'raw_output_bytes':raw_bytes,'whole_compared_raw_file_sha256':hashes,'baseline_controls':logs['baseline'],'candidate_controls':logs['candidate'],'all43_unmapped_device_buffers_including_entire_physical_CFV_literal_exact':True,'all66_device_buffers_exact_under_only_declared_metadata_identity':True,'literal_GPU_data_bytes_compared':D272_LITERAL_GPU_BYTES,'metadata_data_bytes_compared_after_identity_inverse':D272_METADATA_BYTES,'GPU_header_bytes_compared':D272_HEADERS_BYTES,'metadata_row_fields':P['metadata_row_fields'],'metadata_ID_fields':P['metadata_ID_fields'],'whole_original_CPU_plan_kind_map_extents':D272_MAP_EXTENTS,'candidate_selected_constructors':2,'candidate_original_fallback_constructors':4,'raw_metadata_byte_identity_claimed':False,'all_CPU_q_scale_publication_query_save_resume_exact':True,'all_owned_children_terminal':True,'source_main_live_protected_PTX_custody_pass':True,'honest_runtime_NVRTC_included_telemetry':False,'performance_qualification_samples':0,'new_runtime_compiler_implemented':False,'candidate_accepted':False,'scope':'Original full three same-quality canonical science anchors and continued/locked/save/load/resume;6science46checks/12CPU/12all69fieldGPU/6queries3saves9EV. AllCPU/qscale/query/save/EV/geometry/graph/wrapper/dtype/length and entire physical CFV/padding literal exact. In full GPU frames only23metadata row/node-ID fields require declared original-identity inverse, all other43buffers literal exact; every raw byte/header accounted and both original GPU SHA256 values recorded separately. No prefix/padding omission or raw metadata byte-identity claim. Identical sealed accepted9entryCUDA/observer/map allocations/clocks are diagnostic; no performance qualification, runtimeNVRTC/JIT/material/supportedcaller/holdout/cumulative/app proof.'})
print(json.dumps({'status':'pass_full_raw_canonical','records':6,'checkpoints':46,'CPU_pairs':cpu,'GPU_pairs':gpu,'pair_bytes':pair_bytes,'checks':checks}),flush=True)
