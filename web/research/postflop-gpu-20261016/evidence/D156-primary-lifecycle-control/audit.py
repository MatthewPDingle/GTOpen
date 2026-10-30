import sys,json,struct,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
anchor=h.read(ROOT/'epoch/exact-anchor.json')
checks=bytes_compared=raw_words=0
def req(v,s):
    global checks
    assert v,s;checks+=1
def compare(a,b,offset=0):
    global bytes_compared
    req(a.stat().st_size==b.stat().st_size and a.stat().st_size>=offset,'whole pair geometry')
    with a.open('rb') as x,b.open('rb') as y:
        x.seek(offset);y.seek(offset)
        while True:
            left,right=x.read(1024*1024),y.read(1024*1024);req(left==right,'every retained pair byte')
            if not left:break
            bytes_compared+=len(left)
logs={}
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
for arm in P['sequence']:
    text=(H/'execution'/(arm+'.stdout.log')).read_text(encoding='utf-8')
    results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    req([[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==anchor,'canonical full scientific records and all23 checkpoints')
    controls=[json.loads(x.split('D156_CONTROL ',1)[1]) for x in text.splitlines() if x.startswith('D156_CONTROL ')]
    req([x['fixture_id'] for x in controls]==['rainbow','two-tone','river'],'fixed existing fixtures')
    req('test result: ok. 1 passed; 0 failed; 0 ignored;' in text,'test process complete')
    logs[arm]=controls
pairs=cpu_pairs=cfv_pairs=query_pairs=save_pairs=evpairs=0
for b,c in zip(logs['baseline'],logs['candidate']):
    name=b['fixture_id'];req(name==c['fixture_id'] and b['all_GPU_and_CPU_objects_dropped'] and c['all_GPU_and_CPU_objects_dropped'],'same fixture and terminal ownership')
    req([x['stage'] for x in b['stages']]==[x['stage'] for x in c['stages']]==P['lifecycle_stages'],'all ordered lifecycle stages')
    expected=P['expected_candidate_module_activation'][name]
    for bs,cs in zip(b['stages'],c['stages']):
        stage=bs['stage'];bi,ci=bs['info'],cs['info']
        req(bs['iteration']==cs['iteration'] and bs['ev_bits']==cs['ev_bits'],'exact future iteration and EV bits')
        if bs['ev_bits'] is not None:req(math.isfinite(struct.unpack('<d',struct.pack('<Q',bs['ev_bits']))[0]),'finite future EV');evpairs+=1
        req(not bi['packet_module_loaded'] and ci['packet_module_loaded']==expected,'actual ordinary production admission per fixture')
        normalized=dict(ci);normalized['packet_module_loaded']=bi['packet_module_loaded'];normalized['wrapper_bytes']=bi['wrapper_bytes']
        req(normalized==bi and ci['wrapper_bytes']==bi['wrapper_bytes']+32,'same actual geometry and known32byte host wrapper addition')
        bo,co=H/'baseline-output',H/'candidate-output'
        compare(bo/f'{name}-{stage}.cpu.bin',co/f'{name}-{stage}.cpu.bin');cpu_pairs+=1
        # Decode raw CPU frame geometry independently while equality compares every byte.
        with (bo/f'{name}-{stage}.cpu.bin').open('rb') as f:
            req(f.read(16)==b'D156-CPU-RAW1\0\0\0','CPU magic');iteration,iso,locks,preds=struct.unpack('<IIII',f.read(16))
            req(iteration==bs['iteration'] and iso==1 and preds==0,'CPU publication flags')
            for kind in [1,1,2,2]:
                actual=struct.unpack('<I',f.read(4))[0];n,scales=struct.unpack('<QQ',f.read(16));req(actual==kind,'actual Store format');f.seek(2*n+4*scales,1);raw_words+=n+scales
            req(f.tell()==(bo/f'{name}-{stage}.cpu.bin').stat().st_size,'whole CPU Store/q/scale image')
        a,z=bo/f'{name}-{stage}.cfv.u32',co/f'{name}-{stage}.cfv.u32'
        req(a.stat().st_size==bi['CFV_words']*4,'full physical CFV image')
        compare(a,z,65544*4 if expected else 0);cfv_pairs+=1
    for stage in ['locked','resumed']:compare(H/'baseline-output'/f'{name}-{stage}.query.json',H/'candidate-output'/f'{name}-{stage}.query.json');query_pairs+=1
    compare(H/'baseline-output'/f'{name}.save',H/'candidate-output'/f'{name}.save');save_pairs+=1
req(cpu_pairs==cfv_pairs==12 and query_pairs==6 and save_pairs==3 and evpairs==9,'whole fixed lifecycle inventory')
h.custody();D=ROOT/'comparisons/D156-primary-lifecycle-control';D.mkdir(exist_ok=False)
report={'id':'D156','at':h.now(),'status':'pass_scoped_full_primary_raw_lifecycle_equivalence','protocol_sha256':h.sha(H/'protocol.json'),'scientific_full_records_exact':6,'canonical_checkpoints_exact':46,'full_CPU_raw_pairs':cpu_pairs,'physical_CFV_raw_pairs':cfv_pairs,'query_pairs':query_pairs,'save_pairs':save_pairs,'additional_EV_pairs':evpairs,'all_CPU_q_scale_and_file_bytes_exact':True,'all_physical_CFV_words_beyond65544_preserved_on_packed_paths':True,'entire_physical_CFV_exact_on_declined_paths':True,'actual_normal_admission':P['expected_candidate_module_activation'],'reader_checks':checks,'pair_bytes_compared':bytes_compared,'CPU_q_scale_values_represented_per_arm':raw_words,'baseline_controls':logs['baseline'],'candidate_controls':logs['candidate'],'D155_original_coverage_failure_not_regraded':True,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_qualification_samples':0,'candidate_accepted':False,'scope':'Existing three full canonical workloads with ordinary frozen production admission, exact full raw CPU q/scales and physical CFV boundary guards through continued/locked/save/load/warm resume. Primary scientific records/checkpoints still exact original anchor. Printed timing fields are diagnostic because large raw/lifecycle work changes suite history; never use for speed score. Broader F32/CfrPlus/paging/holdout/resource/capacity and fresh performance qualification remain required.'}
h.save(D/'report.json',report);print({k:report[k] for k in ['status','full_CPU_raw_pairs','canonical_checkpoints_exact','pair_bytes_compared','reader_checks']},flush=True)
