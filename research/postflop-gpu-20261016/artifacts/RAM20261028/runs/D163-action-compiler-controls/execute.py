import sys,json,shutil,urllib.request
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
    h.pin(H/'protocol.json',sys.argv[1]);h.custody()
    for path,digest in P['input_sha256'].items():h.pin(path,digest)
    for key,folder in P['folders'].items():h.pin(Path(folder)/'protocol.json',P['category_protocol_sha256'][key])
def publish(folder,names):
    for name in names:
        path=folder/name;key=folder.name+'/'+name;dest=h.ar.DASHBOARD/'evidence'/key;dest.parent.mkdir(exist_ok=True,parents=True)
        if dest.exists():assert dest.read_bytes()==path.read_bytes()
        else:shutil.copyfile(path,dest)
        with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==path.read_bytes()
verify();O=H/'execution';O.mkdir(exist_ok=False);publish(H,['protocol.json','source-review.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);assert not any(x['id']=='D163' for x in status['experiments'])
    status['experiments'].append({'id':'D163','title':'CUDA13 raw action-kernel equivalence','kind':'diagnostic','status':'running','accepted':False,'correctness':'pending_raw_controls','measurement_epoch':'RAM20261028','stage':'1530down then819up cases;full physical words and guards','reason':'Sealed original/compiler13PTX and existing unfiltered action corpora. No NVRTCrepeat,engine or performance score. Actual mismatch closes compiler form. Other7changed kernels/engine/material/full-cycle qualification remain.','evidence':[{'label':'Frozen raw action controls','url':'evidence/D163-action-compiler-controls/protocol.json'},{'label':'Unchanged corpora and adapter review','url':'evidence/D163-action-compiler-controls/source-review.json'}]})
    status.update(updated_at=h.now(),active_experiment='D163',stage='CUDA13 full raw action comparisons',activity='Compiler resources pass;compare2349fixed cases/4698kernel launches with retained all-word inputs,outputs and guards. No speed claim. E080 remains live.')
    h.ar.atomic_json(h.ar.STATUS,status)
reports={}
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes']
    for label in P['category_order']:
        folder=Path(P['folders'][label]);out=folder/'execution';out.mkdir(exist_ok=False);q=h.read(folder/'protocol.json')
        verify();h.ar.refuse_active(h.ar.live_status());h.child(P['rustc_commands'][label],out,'rustc',600);verify()
        data=(folder/'probe.exe').read_bytes();assert (folder/'baseline.ptx').read_bytes() in data and (folder/'candidate.ptx').read_bytes() in data
        h.save(out/'binary.json',{'sha256':h.sha(folder/'probe.exe'),'both_sealed_PTX_embedded':True})
        h.child([str(folder/'probe.exe'),str(folder/'output')],out,'probe',1200);verify()
        text=(out/'probe.stdout.log').read_text(encoding='utf-8');marker='E091_RAW ' if label=='down' else 'E085_UNIT '
        rows=[json.loads(x.split(marker,1)[1]) for x in text.splitlines() if marker in x];assert len(rows)==q['cases']+1 and rows[-1]['stage']=='complete'
        last=rows[-1];assert last['cases']==q['cases'] and last['kernel_launches']==q['kernel_launches']
        corpus=h.read(folder/'corpus.json')
        if label=='down':assert [m['case'] for m in rows[:-1]]==corpus
        else:
            for case,m in zip(corpus['cases'],rows[:-1]):
                assert m['stage']=='case' and all(m[k]==case[k] for k in ['id','hands','actions','threads','p','role','algorithm','iteration','value_mode','count','discount_bits']) and m['all_raw_exact'] and m['guards_exact']
        raw={str(p):h.sha(p) for p in (folder/'output').iterdir()};assert len(raw)==5
        assert sum(p.stat().st_size for p in (folder/'output').iterdir())<=P['raw_reservation_bytes']
        if label=='down':h.save(out/'native-complete.json',{'at':h.now(),'all_native_children_terminal':True,'last_marker':last,'raw_sha256':raw})
        else:h.save(out/'complete.json',{'at':h.now(),'raw_marker_summary':last,'raw_file_sha256':raw,'all_children_terminal':True})
        h.child([sys.executable,str(folder/'audit.py')],out,'audit',1200);verify()
        report_path=ROOT/'comparisons'/('D163-down-action' if label=='down' else 'D163-up-action-root-check')/'report.json';reports[label]=h.read(report_path)
        h.save(out/'reader-complete.json',{'at':h.now(),'report_sha256':h.sha(report_path),'all_owned_children_terminal':True})
        publish(report_path.parent,['report.json'])
    verify();D=ROOT/'comparisons/D163-action-compiler-controls';D.mkdir(exist_ok=False)
    result={'id':'D163','at':h.now(),'status':'pass_scoped_down_and_up_action_raw_equivalence','protocol_sha256':sys.argv[1],'cases':sum(x['cases'] for x in reports.values()),'kernel_launches':sum(x['kernel_launches'] for x in reports.values()),'checks':sum(x['checks'] for x in reports.values()),'output_words_both_arms':sum(x['output_words_both_arms'] for x in reports.values()),'immutable_words_both_arms':sum(x['immutable_words_both_arms'] for x in reports.values()),'guard_words_both_arms':sum(x['guard_words_both_arms'] for x in reports.values()),'category_reports':{key:{'path':str(ROOT/'comparisons'/('D163-down-action' if key=='down' else 'D163-up-action-root-check')/'report.json'),'status':value['status']} for key,value in reports.items()},'all_owned_children_terminal':True,'source_main_live_PTX_custody_pass':True,'NVRTC_compilations':0,'solver_executions':0,'performance_samples':0,'candidate_accepted':False,'scope':'Finite existing action corpora only. All physical outputs,actual immutable input words and guards exact through independent retained readers,including both zero signs/nonfinite witnesses. Other7changed kernels,full engine/primary raw-state/quality/save/resume/continuation and actual runtime integration/material/capacity/performance qualification still required. Not universal numerical identity or speed proof.'}
    assert result['cases']==P['expected_cases'] and result['kernel_launches']==P['expected_kernel_launches']
    h.save(D/'report.json',result);h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(D/'report.json'),'new_gain_accepted':False})
publish(D,['report.json'])
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    status=h.read(h.ar.STATUS);item=next(x for x in status['experiments'] if x['id']=='D163')
    item.update(status='measured',correctness='pass_scoped_raw_action_controls',stage='2349action cases exact;other kernels and engine pending',reason=f"All{result['output_words_both_arms']}output words,{result['immutable_words_both_arms']}actual immutable words and{result['guard_words_both_arms']}guards exact. No solver or performance score;full compiler qualification remains.")
    item.setdefault('evidence',[]).append({'label':'Retained full raw action outcomes','url':'evidence/D163-action-compiler-controls/report.json'})
    status.update(updated_at=h.now(),active_experiment='D163',stage='CUDA13 action numerical controls passed',activity='2349fixed direct action cases exact. Next remaining kernels and complete engine controls before a runtime compiler candidate or fresh speed qualification. E08010.4564s unchanged.')
    h.ar.atomic_json(h.ar.STATUS,status)
verify();print(json.dumps({k:result[k] for k in ['status','cases','kernel_launches','checks','output_words_both_arms','immutable_words_both_arms','guard_words_both_arms']}),flush=True)
