import json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
P=h.read(ROOT/'runs/E096-primary-plan/protocol.json');Q=h.read(ROOT/'comparisons/E096-three-pair-comparison/report.json');cross=h.read(ROOT/'comparisons/E096-root-crosscheck/report.json');assert Q['decision']=='rejected' and cross['status']=='pass_rejected' and cross['aggregate_gain_pct']==Q['performance']['observed_gain_pct'] and cross['checks']==95
for path,digest in P['input_sha256'].items():h.pin(path,digest)
receipts=[]
for row in P['sequence']:
 p=ROOT/'runs/E096-primary-execution'/(row['id']+'.exit.json');r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
 if not row['unit']:assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
done=h.read(ROOT/'runs/E096-primary-execution/complete.json');assert done['all_owned_children_terminal'] and done['ordinary_units_passed']==86 and done['extension_runs']==done['historical_samples_scored']==0
for folder in [ROOT/'runs/E096-resource/execution',ROOT/'runs/D176-cache-engine-control/execution',ROOT/'runs/D177-up-action/execution',ROOT/'runs/D177-chance/execution',ROOT/'runs/D178-canonical-cache-control/execution']:
 for p in folder.glob('*.exit.json'):
  r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
raw=ROOT/'comparisons/D178-canonical-cache-control/report.json';r=h.read(raw);assert r['scientific_full_records_exact']==6 and r['canonical_checkpoints_exact']==46 and r['entire_physical_CFV_and_all65other_device_fields_exact'] and len(r['whole_compared_raw_file_sha256'])==66
for p,identity in r['whole_compared_raw_file_sha256'].items():assert Path(p).stat().st_size==identity['bytes']
build=h.read(ROOT/'runs/E096-final-build/complete.json');assert build['all_compilers_terminal'] and build['native_executions']==0
for path,digest in build['evidence_sha256'].items():h.pin(path,digest)
for phase in ['feature','primary']:assert h.read(ROOT/'runs/E096-final-build'/phase/'restoration.json')['accepted_source_restored'] and h.read(ROOT/'runs/E096-final-build'/phase/'cargo.exit.json')['returncode']==0
N=ROOT/'runs/E096-terminal-checkpoint';N.mkdir(exist_ok=False);h.save(N/'report.json',{'id':'E096-close','at':h.now(),'status':'rejected_closed_complete_cycle_below1pct','performance':Q['performance'],'primary_report_sha256':h.sha(ROOT/'comparisons/E096-three-pair-comparison/report.json'),'full_log_arithmetic_root_sha256':h.sha(ROOT/'comparisons/E096-root-crosscheck/report.json'),'resource_report_sha256':h.sha(ROOT/'runs/E096-resource/report.json'),'engine_report_sha256':h.sha(ROOT/'comparisons/D176-cache-engine-control/report.json'),'edge_report_sha256':h.sha(ROOT/'comparisons/D177-cache-direct-controls/report.json'),'canonical_raw_report_sha256':h.sha(raw),'all66_retained_raw_file_extents_verified':True,'full_raw_bytes_not_rehashed_after_original_stream_comparison':True,'successful_owned_child_receipts':receipts,'all_compilers_native_readers_terminal':True,'accepted_source_main_live_protected_PTX_unchanged':True,'variant_or_extra_confirmation_runs':0,'source_or_cacheop_or_entrysubset_rescue_allowed':False,'new_gain_accepted':False,'current_RAM_original_baseline_ms':10456.4109,'samecohort_E096_reference_ms':Q['performance']['baseline_full_cycle_ms'],'historical_or_RAMbaseline_timing_pooling':False,'last_primary_baseline_id':'B307','best_qualified_workers':16})
def publish(folder,names):
 for filename in names:
  p=folder/filename;dst=h.ar.DASHBOARD/'evidence'/folder.name/filename;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+filename,timeout=20) as response:assert response.read()==p.read_bytes()
for folder,names in [(N,['report.json']),(ROOT/'comparisons/E096-three-pair-comparison',['report.json']),(ROOT/'comparisons/E096-root-crosscheck',['report.json'])]:publish(folder,names)
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E096');item.update(status='rejected',accepted=False,correctness='all_resource_edge_engine_canonical_raw_and_primary_science_pass',stage='Closed: no aggregate speedup',performance=Q['performance'],reason='9530.8429 -> 9544.2733 ms sumfixturemedians;observedgain -0.1409151335%,below1%. No strictfixtureguardfailed. All86units/18primaryrecords/138checks exactplusfullraw. No extra samples,cacheop/entrysubset/source/flagvariants or adoption.');item['evidence'].extend([{'label':'All fixed complete-solve results','url':'evidence/E096-three-pair-comparison/report.json'},{'label':'Independent full-log and arithmetic replay','url':'evidence/E096-root-crosscheck/report.json'},{'label':'Terminal ownership/source custody','url':'evidence/'+N.name+'/report.json'}]);s.update(updated_at=h.now(),active_experiment='E096',stage='CFV cache hint closed; next source audit',activity='E096exactbut0.1409%slower in fixedcomplete-cycle screen,rejected. No acceptedgain. KeepE080/16 andcurrentRAMbaseline10.4564109s. Next auditshared scanlayout withoutreopeningclosedforms.');h.ar.atomic_json(h.ar.STATUS,s)
h.custody();print(json.dumps({'E096':'closed','observed_gain_pct':Q['performance']['observed_gain_pct'],'strict_fixture_failed':False,'all_children_terminal':True,'new_gain_accepted':False}),flush=True)
