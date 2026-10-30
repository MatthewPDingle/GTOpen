"""Frozen CPU-only compilation and twelve control processes; no solver mutation."""
import json, shutil, sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
from replay import replay
assert len(sys.argv)==2
old.pin(H/'protocol.json',sys.argv[1]);P=old.read(H/'protocol.json')
def verify():
    old.pin(H/'protocol.json',sys.argv[1])
    for p,h in P['input_sha256'].items():old.pin(p,h)
    old.custody()
verify();B=H/'build';E=H/'execution';assert not B.exists() and not E.exists()
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
    old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=82*1024**3
    B.mkdir();E.mkdir();old.child(P['command'],B,'rustc',old.env(),600);verify()
    binary=old.sha(B/'probe.exe')
    old.save(B/'complete.json',{'at':old.now(),'binary_sha256':binary,'protocol_sha256':sys.argv[1],'production_source_activated':False,'native_executions':0})
    results=[]
    for case in P['cases']:
        verify();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=66*1024**3
        label=f'case-{case:02d}';old.pin(B/'probe.exe',binary)
        old.child([str(B/'probe.exe'),str(case),str(E/(label+'.bin'))],E,label,old.env(),120)
        verify();r=replay(E/(label+'.bin'),case);results.append(r)
        old.save(E/(label+'.replay.json'),r)
        print(json.dumps({k:r[k] for k in ['id','nodes','reordered_positions','root_checks','baseline_plan_ms','candidate_plan_ms']}),flush=True)
    assert len(results)==12 and [r['id'] for r in results]==list(range(12))
    assert all(r['reordered_positions']>0 for r in results if r['fixture_index'] in [0,1])
    report={'at':old.now(),'id':P['id'],'status':'pass_cpu_metadata_and_concrete_ownership','protocol_sha256':sys.argv[1],'binary_sha256':binary,'cases':results,'root_checks':sum(r['root_checks'] for r in results),'all53fields_captured':True,'nonorder_fields_exact':True,'all_vec_capacities_struct_sizes_equal':True,'all_level_node_multisets_preserved':True,'concrete_same_level_ownership_pass':True,'production_source_activated':False,'gpu_executions':0,'full_cycle_performance_measured':False,'optimization_accepted':False,'excluded_samples':[],'extension_runs':0,'limits':'CPU-only exact metadata and ownership controls. Diagnostic component times do not establish complete-cycle speed or material costs. No GPU raw state, graph execution, whole-run timing, F32, save/resume or broad qualification yet. Root replay is not external independent review.'}
    old.save(H/'report.json',report);verify()
print(json.dumps({'status':report['status'],'cases':len(results),'root_checks':report['root_checks'],'gpu_executions':0,'full_cycle_performance_measured':False}),flush=True)
