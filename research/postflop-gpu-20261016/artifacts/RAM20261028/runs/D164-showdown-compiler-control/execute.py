import sys,json,shutil,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
def publish(folder,names):
    for name in names:
        p=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==p.read_bytes()
        else:shutil.copyfile(p,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False);publish(H,['protocol.json','source-review.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D164' for x in status['experiments'])
    status['experiments'].append({'id':'D164','title':'CUDA13 full raw showdown equivalence','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending_raw_controls','measurement_epoch':'RAM20261028','stage':'364original cases x5widths,whole outputs and21inputs','reason':'Same accepted source;sealed12.9/13PTX,no compiler repeat. No solver or speed result. Actual numerical mismatch closes compiler form.','evidence':[{'label':'Frozen showdown matrix','url':'evidence/D164-showdown-compiler-control/protocol.json'},{'label':'Original corpus and output-only adapters','url':'evidence/D164-showdown-compiler-control/source-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='D164',stage='CUDA13 showdown raw numerical controls',activity='Action2349cases exact;now1820physical showdown comparisons acrossfivewidths,full21actual input buffers and entire CFV/guards. No speed claim.')
    h.ar.atomic_json(h.ar.STATUS,status)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    h.child(P['rustc_command'],O,'rustc',600);verify();data=(H/'probe.exe').read_bytes();assert all((H/(arm+'.ptx')).read_bytes() in data for arm in ['baseline','candidate'])
    h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe'),'both_sealed_PTX_embedded':True})
    h.child([str(H/'probe.exe'),str(O)],O,'probe',1200);verify()
    markers=[json.loads(x.split('E089_EXACT ',1)[1]) for x in (O/'probe.stdout.log').read_text(encoding='utf-8').splitlines() if 'E089_EXACT ' in x]
    assert len(markers)==1823 and markers[0]['stage']=='corpus_validated' and markers[1]['stage']=='device' and markers[-1]['stage']=='complete'
    corpus=h.read(H/'corpus.json');matrix=[(width,c) for width in P['widths'] for c in corpus['cases']]
    for (width,case),row in zip(matrix,markers[2:-1]):assert row['stage']=='full_show_exact' and row['case_id']==case['id'] and row['threads']==width and row['all_output_bits_exact'] and row['input_bits_unchanged']
    summary=markers[-1];assert summary['comparison_pairs']==1820 and summary['kernel_launches']==3640 and summary['all_output_bits_exact'] and summary['all_inputs_unchanged'] and summary['tested_block_widths']==P['widths']
    assert (O/'probe.stderr.log').read_bytes()==b''
    for arm in ['baseline','candidate']:assert (O/(arm+'.ptx')).read_bytes()==(H/(arm+'.ptx')).read_bytes()
    raw=O/'raw-results.jsonl';assert raw.stat().st_size<P['raw_reservation_bytes']
    h.save(O/'complete.json',{'at':h.now(),'protocol_sha256':sys.argv[1],'summary':summary,'binary_sha256':h.sha(H/'probe.exe'),'raw_sha256':h.sha(raw),'raw_bytes':raw.stat().st_size,'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_measured':False,'candidate_accepted':False})
    h.child([sys.executable,str(H/'audit.py')],O,'audit',1200);verify()
D=ROOT/'comparisons/D164-showdown-compiler-control';r=h.read(D/'report.json');h.save(O/'reader-complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'new_gain_accepted':False});publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D164')
    item.update(status='measured',correctness='pass_scoped_full_raw_showdown',stage='1820physical showdown pairs exact',reason=f"All{r['inventory']['full_output_words_both_arms']}physical output words and{r['inventory']['device_input_word_checks']}actual input words exact. No solver/performance score;engine and other kernels remain.")
    item.setdefault('evidence',[]).append({'label':'Full retained showdown result','url':'evidence/D164-showdown-compiler-control/report.json'})
    status.update(updated_at=h.now(),active_experiment='D164',stage='CUDA13 showdown controls passed',activity='Action2349cases andshowdown1820pairs exact. Next complete-engine state/quality/lifecycle controls before runtime compiler integration or speed qualification. E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:r[k] for k in ['status','checks','inventory']}),flush=True)
