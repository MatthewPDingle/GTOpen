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
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms','runtime_nvrtc_jit_included'}
logs={};science_counts=[]
for arm in P['sequence']:
    text=(H/'execution'/(arm+'.stdout.log')).read_text(encoding='utf-8');results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x];stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    req(len(results)==3 and all(x['runtime_nvrtc_jit_included'] is False for x in results),'honest diagnostic prebuilt PTX telemetry')
    req([x for x in text.splitlines() if x.startswith('D237_BIND ')]==['D237_BIND '+arm]*P['expected_PTX_bindings_per_arm'],'actual sealed module bindings forinitial/resume')
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
        a,z=bo/f'{name}-{stage}.gpu.bin',co/f'{name}-{stage}.gpu.bin';pair(a,z);gpu_frame(a,bs['info']);gpu_frame(z,cs['info']);gpu+=1
        print('D166 raw reader',name,stage,'complete',flush=True)
    for stage in ['locked','resumed']:pair(H/'baseline-output'/f'{name}-{stage}.query.json',H/'candidate-output'/f'{name}-{stage}.query.json');query+=1
    pair(H/'baseline-output'/f'{name}.save',H/'candidate-output'/f'{name}.save');save+=1
req(cpu==gpu==12 and query==6 and save==3 and evs==9,'entire fixed lifecycle inventory');req(science_counts==[[3,23],[3,23]],'complete6records46checkpoints')
raw_bytes=sum(p.stat().st_size for d in H.glob('*-output') for p in d.iterdir() if p.is_file());req(raw_bytes<=P['limits']['raw_reservation_bytes'],'raw output withinreservation')
h.custody();D=ROOT/'comparisons/D237-stride-canonical';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D237','at':h.now(),'status':'pass_scoped_full_canonical_all_device_and_CPU_raw_lifecycle','protocol_sha256':h.sha(H/'protocol.json'),'scientific_full_records_exact':6,'canonical_checkpoints_exact':46,'CPU_raw_pairs':cpu,'GPU_all69field_pairs':gpu,'actual_device_buffers_per_frame':66,'host_fields_per_GPU_frame':3,'query_pairs':query,'save_pairs':save,'future_EV_pairs':evs,'reader_checks':checks,'pair_bytes_compared':pair_bytes,'represented_GPU_and_CPU_words_both_arms':represented_words,'raw_output_bytes':raw_bytes,'whole_compared_raw_file_sha256':hashes,'baseline_controls':logs['baseline'],'candidate_controls':logs['candidate'],'entire_physical_CFV_and_all65other_device_fields_exact':True,'all_CPU_q_scale_publication_query_save_resume_exact':True,'all_owned_children_terminal':True,'source_main_live_protected_PTX_custody_pass':True,'honest_runtime_NVRTC_included_telemetry':False,'performance_qualification_samples':0,'new_runtime_compiler_implemented':False,'candidate_accepted':False,'scope':'Original three full same-quality canonical science anchors plus continued/locked/save/load/warmresume. Every retained CPU/qscale andall66actualdevicebuffers withdtype/hoststate andentirephysicalCFV bit-exact;no padding/prefix omission. Original runtime-NVRTCclock telemetry honestly falseandprospectivelyexcludedfromsciencecomparison only. PrebuiltPTX/giantobserver/lifecycle clocks arediagnostic,never speed qualification. Existing broaderengine/directkernel evidence stays scoped. Runtime loader/integration,otherdevice/non120fallback,actualresource/capacity/holdout/fresh performance/fresh16/serveradoption remain.'})
print(json.dumps({'status':'pass_full_raw_canonical','records':6,'checkpoints':46,'CPU_pairs':cpu,'GPU_pairs':gpu,'pair_bytes':pair_bytes,'checks':checks}),flush=True)
