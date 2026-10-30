import json,shutil,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
assert len(sys.argv)==2;old.pin(HERE/'protocol.json',sys.argv[1]);P=old.read(HERE/'protocol.json')
for p,h in P['input_sha256'].items():old.pin(p,h)
OUT=HERE/'execution'
with old.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 old.custody();old.ar.refuse_active(old.ar.live_status());assert shutil.disk_usage(ROOT).free>=82*1024**3;assert not OUT.exists();OUT.mkdir()
 old.child(P['rustc_command'],OUT,'rustc',old.env(),180)
 rows=[]
 for case in P['cases']:
  old.child([str(HERE/'probe.exe'),str(case['id']),case['path']],OUT,'case-'+str(case['id']).zfill(2),old.env(),120)
  lines=(OUT/('case-'+str(case['id']).zfill(2)+'.stdout.log')).read_text(encoding='utf-8').splitlines();markers=[json.loads(x.split('D102_RESULT ',1)[1]) for x in lines if x.startswith('D102_RESULT ')];assert len(markers)==1;row=markers[0];assert row['case_id']==case['id'] and row['status']=='pass_exact_integer_selectors';rows.append(row)
 old.custody();report={'id':'D102-card-cutoffs','at':old.now(),'status':'pass_cpu_integer_selector_proof_only','protocol_sha256':sys.argv[1],'binary_sha256':old.sha(HERE/'probe.exe'),'cases':rows,'checks':sum(r['checks'] for r in rows),'rows':sum(r['rows'] for r in rows),'selected_card_positions':sum(r['selected_card_positions'] for r in rows),'exhaustive_field_values':sum(r['exhaustive_disjoint_field_values'] for r in rows),'maximum_extra_host_capacity_bytes':max(r['extra_host_capacity_bytes'] for r in rows),'extra_gpu_bytes':0,'source_activated':False,'gpu_executions':0,'performance_measured':False,'candidate_accepted':False,'all_children_terminal':True,'limits':'CPU logical selected-index order only; no float GPU/compiler/resource or speed qualification. Mirror struct contains the exact required field types, not a full GpuPlan. Candidate helper bytes exactly match the function staged in candidate-mod.rs; integrated compile/tests still mandatory. Retained D092only baseline words used; old action-order candidate not used.'};old.save(HERE/'report.json',report);print(json.dumps({k:v for k,v in report.items() if k!='cases'}),flush=True)
