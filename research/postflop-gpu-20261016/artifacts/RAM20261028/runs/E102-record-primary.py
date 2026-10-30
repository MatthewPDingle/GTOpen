import json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
H=ROOT/'runs/E102-primary-plan';P=h.read(H/'protocol.json');Q=h.read(ROOT/'comparisons/E102-three-pair-comparison/report.json');cross=h.read(ROOT/'comparisons/E102-root-crosscheck/report.json')
passed=Q['decision']=='advance_to_separately_frozen_confirmation';assert Q['decision'] in ['rejected','advance_to_separately_frozen_confirmation']
assert cross['status']==('pass_initial_timing_only' if passed else 'pass_rejected') and cross['aggregate_gain_pct']==Q['performance']['observed_gain_pct']
for p,digest in P['input_sha256'].items():h.pin(p,digest)
receipts=[]
for row in P['sequence']:
 p=ROOT/'runs/E102-primary-execution'/(row['id']+'.exit.json');r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
 if not row['unit']:assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
done=h.read(ROOT/'runs/E102-primary-execution/complete.json');assert done['all_owned_children_terminal'] and done['ordinary_units_passed']==86 and done['extension_runs']==done['historical_samples_scored']==0
for folder in [ROOT/'runs/E102-resource/execution',ROOT/'runs/D195-original-chance/execution',ROOT/'runs/D195-parent-fanout/execution',ROOT/'runs/D195-parent-chance-controls/execution',ROOT/'runs/D196-parent-chance-engine/execution',ROOT/'runs/D197-parent-chance-canonical/execution']:
 for p in folder.glob('*.exit.json'):
  r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
assert h.read(ROOT/'runs/D195-parent-chance-controls/execution/complete.json')['all_owned_compilers_native_readers_terminal']
assert h.read(ROOT/'runs/D196-parent-chance-engine/execution/complete.json')['all_owned_children_terminal']
assert h.read(ROOT/'runs/D197-parent-chance-canonical/execution/complete.json')['all_owned_children_terminal']
raw=ROOT/'comparisons/D197-parent-chance-canonical/report.json';r=h.read(raw)
assert r['scientific_full_records_exact']==6 and r['canonical_checkpoints_exact']==46 and r['entire_physical_CFV_and_all65other_device_fields_exact'] and len(r['whole_compared_raw_file_sha256'])==66
for p,identity in r['whole_compared_raw_file_sha256'].items():assert Path(p).stat().st_size==identity['bytes']
build=h.read(ROOT/'runs/E102-final-build/complete.json');assert build['all_compilers_terminal'] and build['native_executions']==0
for p,digest in build['evidence_sha256'].items():h.pin(p,digest)
for phase in ['feature','primary']:assert h.read(ROOT/'runs/E102-final-build'/phase/'restoration.json')['accepted_source_restored'] and h.read(ROOT/'runs/E102-final-build'/phase/'cargo.exit.json')['returncode']==0
N=ROOT/'runs/E102-primary-checkpoint';N.mkdir(exist_ok=False)
g=Q['performance']['observed_gain_pct'];failed=[x['fixture_id'] for x in Q['performance']['fixture_regression_guard'] if x['failed']]
state='pass_initial_speed_screen_confirmation_required' if passed else 'rejected_closed_primary_timing_gate'
h.save(N/'report.json',{'id':'E102-primary-checkpoint','at':h.now(),'status':state,'performance':Q['performance'],'primary_report_sha256':h.sha(ROOT/'comparisons/E102-three-pair-comparison/report.json'),'full_log_root_replay_sha256':h.sha(ROOT/'comparisons/E102-root-crosscheck/report.json'),'resource_report_sha256':h.sha(ROOT/'runs/E102-resource/report.json'),'mechanism_report_sha256':h.sha(ROOT/'comparisons/E102-parent-load-mechanism/report.json'),'direct_report_sha256':h.sha(ROOT/'comparisons/D195-parent-chance-controls/report.json'),'engine_report_sha256':h.sha(ROOT/'comparisons/D196-parent-chance-engine/report.json'),'canonical_raw_report_sha256':h.sha(raw),'all66_retained_raw_file_extents_verified':True,'raw_files_not_rehashed_after_original_full_comparison':True,'successful_child_receipts':receipts,'all_owned_compilers_native_readers_terminal':True,'accepted_source_main_live_protected_PTX_unchanged':True,'new_gain_accepted_or_deployed':False,'extra_confirmation_or_rescue_runs':0,'source_width_group_tile_guard_field_helper_caller_flag_sample_rescue_allowed':False,'later_requirements':P['adoption_requirements'],'resource_caution':'Newentry40registers versus original30; fixedoccupancy/local/shared/defaultstack same in actual resource queries. ActualCPU/memory/capacity/graph/material qualification unproven; no no-tradeoff claim.', 'original_current_RAM_reference_ms':10456.4109,'samecohort_reference_ms':Q['performance']['baseline_full_cycle_ms'],'historical_or_RAM_reference_samples_scored':0,'last_primary_baseline_id':'B316','best_qualified_config':'E080 / GPU / compressed /16workers'})
evidence=[]
for folder,names in [(N,['report.json']),(ROOT/'comparisons/E102-three-pair-comparison',['report.json']),(ROOT/'comparisons/E102-root-crosscheck',['report.json'])]:
 for name in names:
  p=folder/name;dst=h.ar.DASHBOARD/'evidence'/folder.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+folder.name+'/'+name,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name,'url':'evidence/'+folder.name+'/'+name})
reason=f"Complete fixture medians {Q['performance']['baseline_full_cycle_ms']:.7f} to {Q['performance']['candidate_full_cycle_ms']:.7f} ms; observed gain {g:.8f}%. Strict fixture guards failed: {','.join(failed) or 'none'}. All86ordinary units/18primary records/138checks exact. "+('Initial screen only; fresh16/broad/material/capacity/holdout/cumulative/application gates remain.' if passed else 'Rejected exact parent-fanout form; no extra samples, source/grouping/tile/width/guard/caller/helper/flags rescue or adoption.')
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E102');item.update(status='measured' if passed else 'rejected',accepted=False,correctness='resource_direct_engine_canonical_and_primary_science_pass',performance=Q['performance'],stage='Initial speed screen passed; confirmation required' if passed else 'Closed: complete-cycle timing gate failed',reason=reason);item.setdefault('evidence',[]).extend(evidence)
 s.update(updated_at=h.now(),active_experiment='E102',stage=item['stage'],activity=reason+' E080/GPU/compressed/16 remains live.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
 f.write('\n\n### E102 complete-cycle primary outcome\n\n'+reason+'\n\n')
 for x in Q['fixtures']:f.write(f"{x['fixture_id']}: {x['baseline_median_ms']:.7f} -> {x['candidate_median_ms']:.7f} ms, gain{x['gain_pct']:.10f}%, paired slower{sum(v<0 for v in x['paired_gain_pct'])}/3, guardfailed={x['guard_failed']}.\n\n")
 f.write('Separate full-log and arithmetic replay agrees. All owned resource/direct/engine/canonical/build/primary compilers/native/readers terminal;66retained canonical file extents match original full reader receipts. Accepted source/main/live/protectedPTX verified, locks absent. Earlier RAM10456.4109ms reference and historical E080 gain stay separate, no pooling/addition. Newentry40registers versus old30 with same measured theoretical residency and no spill/shared/defaultstack growth; actual broad material/capacity unproven. Bestqualified E080/GPU/compressed/16workers remains live. All new outputX; goal active.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: record parent chance full-cycle primary screen'],cwd=h.REPO,check=True)
h.custody();print(json.dumps({'E102':state,'observed_gain_pct':g,'fixture_guards_failed':failed,'all_owned_children_terminal':True,'new_gain_accepted':False}),flush=True)
