"""One fixed before/after large warm-state control, with complete raw byte parity."""
from pathlib import Path
import array,json,struct,sys
H=Path(__file__).resolve().parent;R=H.parent.parent
sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as old
assert len(sys.argv)==2;old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json');E=R/'runs/E080-broader-warm-execution';O=R/'comparisons/E080-large-warm-controls'
def verify():
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
def equal(a,b):
    assert a.stat().st_size==b.stat().st_size
    with a.open('rb')as x,b.open('rb')as y:
        while True:
            left,right=x.read(8*1024*1024),y.read(8*1024*1024);assert left==right
            if not left:break
def decode(path,row):
    with path.open('rb')as f:
        assert f.read(16)==b'E080-WARM-RAW1\0\0';iteration,n=struct.unpack('<II',f.read(8));assert iteration==row['iteration']and n==4;elements=0
        for i,expected in enumerate(row['stores']):
            tag,qlen,scalen=struct.unpack('<IQQ',f.read(20));assert tag==P['warm_expected']['tags'][i]and(tag,qlen,scalen)==(expected['tag'],expected['q_len'],expected['scale_len']);f.seek(qlen*2,1)
            a=array.array('I');a.fromfile(f,scalen);assert sys.byteorder=='little'and a.itemsize==4;assert sum(x!=0 for x in a)==expected['nonzero_scale_words'];elements+=qlen+scalen
        assert f.tell()==path.stat().st_size==row['raw_bytes']and f.read(1)==b''
    return{'raw_sha256':old.sha(path),'raw_bytes':path.stat().st_size,'encoded_elements':elements,'iteration':iteration,'stage':row['stage'],'raw_path':str(path)}
verify();assert not E.exists()and not O.exists()and not(R/'gpu-run.lock').exists();E.mkdir();O.mkdir();records={};raws={};ex=P['warm_expected']
for arm in['baseline','candidate']:
    verify();old.ar.refuse_active(old.ar.live_status());b=P['binaries'][P['warm_binaries'][arm]];old.pin(b['path'],b['sha256']);old.pin(b['manifest'],b['manifest_sha256']);out=E/arm;out.mkdir();raw=E/('raw-'+arm);assert not raw.exists()
    with old.ar.exclusive_lock(R/'gpu-run.lock'):old.child([b['path'],str(raw)],out,'native',old.env(),900)
    verify();text=(out/'native.stdout.log').read_text(encoding='utf-8');rows=[json.loads(x.split('E080_WARM ',1)[1])for x in text.splitlines()if x.startswith('E080_WARM ')]
    assert[x['stage']for x in rows]==ex['stages'];last=rows[-1];assert last['snapshots']==6 and last['GPU_constructor_calls']==4 and last['iterations_executed']==7 and last['q_bytes']==ex['q_bytes']>=ex['minimum_overlap_bytes']
    assert last['overlap_eligibility_condition_verified']and last['all_four_warm_scale_predicates_false']and last['budget_rejection_pass']and not last['performance_measured']and not last['worker_observed_by_thread_trace']
    images=[]
    for i,row in enumerate(x for x in rows if'stores'in x):
        path=raw/(row['stage']+'.bin');assert row['raw_file']==str(path)and row['stage']==ex['raw_stages'][i]and row['iteration']==ex['iterations'][i];images.append(decode(path,row))
    assert len(images)==6 and all(x['nonzero_scale_words']>0 for x in rows[0]['stores']);records[arm]=rows;raws[arm]=images
    old.save(out/'parsed.json',{'at':old.now(),'markers':rows,'full_raw_layout_replays':images,'binary_sha256':b['sha256'],'stdout_sha256':old.sha(out/'native.stdout.log')});print('Completed large warm state',arm,flush=True)
canonical=lambda rows:[{k:v for k,v in x.items()if k!='raw_file'}for x in rows]
assert json.dumps(canonical(records['baseline']),sort_keys=True)==json.dumps(canonical(records['candidate']),sort_keys=True)
for stage in ex['raw_stages']:equal(E/'raw-baseline'/(stage+'.bin'),E/'raw-candidate'/(stage+'.bin'))
saved={arm:E/('raw-'+arm)/'large-warm.gto'for arm in['baseline','candidate']};equal(saved['baseline'],saved['candidate']);saved_info={arm:{'path':str(p),'sha256':old.sha(p),'bytes':p.stat().st_size}for arm,p in saved.items()}
verify();old.save(O/'report.json',{'id':'E080-large-warm-controls','at':old.now(),'status':'pass_six_full_raw_large_warm_states_each','protocol_sha256':sys.argv[1],'source_candidate_unchanged':True,'raw_layouts':raws,'raw_files_stream_compared':6,'all_full_q_and_scale_bytes_exact':True,'root_query_and_all_non_path_markers_exact':True,'raw_bytes_retained':sum(x['raw_bytes']for rows in raws.values()for x in rows),'encoded_elements_per_arm':sum(x['encoded_elements']for x in raws['baseline']),'complete_save_files':saved_info,'complete_save_files_stream_compared':True,'successful_GPU_constructors_each':3,'budget_rejections_each':1,'iterations_each':7,'verified_q_bytes':ex['q_bytes'],'performance_measured':False,'candidate_accepted':False,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'limits':'One fixed large compressed two-tone case. Warm full-plan initialization, compact reconstruction, materialized query/resync, complete save/load and resume are actual executions. Eligibility is verified by real q-byte lengths and pinned source; no external worker thread trace. Entire raw frames and all q/scale bytes compare, not only hashes. No complete-cycle, whole-memory, capacity or responsiveness conclusion.'})
old.save(E/'complete.json',{'at':old.now(),'all_children_terminal':True,'raw_snapshots_each':6,'report_sha256':old.sha(O/'report.json'),'no_extra_samples_or_source_variants':True});print('Large warm-state controls passed full raw parity.',flush=True)
