import json,shutil,sys,urllib.request,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists() and not(ROOT/'epoch-sequence.lock').exists();h.ar.refuse_active(h.ar.live_status())
H=ROOT/'runs/E103-primary-plan';P=h.read(H/'protocol.json');Q=h.read(ROOT/'comparisons/E103-three-pair-comparison/report.json');X=h.read(ROOT/'comparisons/E103-root-crosscheck/report.json');passed=Q['decision']=='advance_to_separately_frozen_confirmation'
assert X['status']==('pass_initial_screen_only' if passed else 'pass_rejection_replay') and X['observed_gain_pct']==Q['performance']['observed_gain_pct']
assert h.read(H/'execution/complete.json')['all_owned_children_terminal']
for p,d in P['input_sha256'].items():h.pin(p,d)
receipts=[]
for row in P['sequence']:
 p=ROOT/'runs'/row['id']/'exit.json';r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
for p in (ROOT/'runs/D201-affinity-raw-controls/execution').glob('*.exit.json'):
 r=h.read(p);assert r['returncode']==0 and r['error'] is r['cleanup'] is None;receipts.append({'path':str(p),'sha256':h.sha(p),'returncode':0})
raw=ROOT/'comparisons/D201-affinity-raw-controls/report.json';r=h.read(raw);assert r['pair_bytes_compared']==54608665195 and r['entire_physical_CFV_and_all65other_device_fields_exact'] and len(r['whole_compared_raw_file_sha256'])==66
for p,v in r['whole_compared_raw_file_sha256'].items():assert Path(p).stat().st_size==v['bytes']
assert h.read(ROOT/'runs/D201-affinity-raw-controls/execution/complete.json')['all_owned_children_terminal']
N=ROOT/'runs/E103-primary-checkpoint';N.mkdir(exist_ok=False)
h.save(N/'report.json',{'id':'E103-primary-checkpoint','at':h.now(),'status':'initial_speed_and_cost_screen_pass_confirmation_required' if passed else 'rejected_closed_fixed_affinity_form','performance':Q['performance'],'whole_process_costs':Q['whole_process_costs'],'primary_report_sha256':h.sha(ROOT/'comparisons/E103-three-pair-comparison/report.json'),'root_replay_sha256':h.sha(ROOT/'comparisons/E103-root-crosscheck/report.json'),'raw_control_report_sha256':h.sha(raw),'all66_retained_raw_extents_verified':True,'raw_bytes_not_rehashed_after_original_fullcomparison':True,'child_receipts':receipts,'all_owned_compiler_native_readers_terminal':True,'new_source_or_compiler_variants':0,'new_gain_accepted_or_deployed':False,'alternate_sibling_CCD_subset_count_priority_power_OS_clock_source_flags_samples_rescue_allowed':False,'future_requirements':P['adoption_requirements'],'accepted_source_main_live_protected_PTX_unchanged':True,'last_primary_baseline_id':'B316','original_current_RAM_reference_ms':10456.4109,'historical_or_RAM_reference_samples_scored':0,'best_qualified':'E080 / GPU / compressed /16workers / defaultalllogicalaffinity','goal_active':True})
evidence=[]
for folder in [N,ROOT/'comparisons/E103-three-pair-comparison',ROOT/'comparisons/E103-root-crosscheck']:
 p=folder/'report.json';key=folder.name+'/'+p.name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
 evidence.append({'label':folder.name,'url':'evidence/'+key})
perf=Q['performance'];reason=f"Complete fixture medians {perf['baseline_full_cycle_ms']:.7f} to {perf['candidate_full_cycle_ms']:.7f}ms, observed gain {perf['observed_gain_pct']:.8f}%. Failed gates: {','.join(perf['failed_gates']) or 'none'}. "+('Initial screen only; fresh16/broad/material/capacity/holdout/cumulative/application checks remain.' if passed else 'Exact16worker/0x55555555placement closed; no alternative sibling/CCDsubset/count/priority/source/flags/samples rescue.')
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);item=next(x for x in s['experiments'] if x['id']=='E103');item.update(status='measured' if passed else 'rejected',accepted=False,correctness='fullraw_ordinary_units_and_original_science_pass',performance=perf,stage='Initialspeedandcostscreenpassed;confirmationrequired' if passed else 'Closed: fixed placement speed/cost gate failed',reason=reason);item.setdefault('evidence',[]).extend(evidence)
 s.update(updated_at=h.now(),active_experiment='E103',stage=item['stage'],activity=reason+' E080/GPU/compressed/16/defaultaffinity remains live; no new gain adopted.');h.ar.atomic_json(h.ar.STATUS,s)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/status.json',timeout=20) as response:assert response.read()==h.ar.STATUS.read_bytes()
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:
 f.write('\n\n### E103 physical-core placement primary outcome\n\n'+reason+'\n\n')
 for x in Q['fixtures']:f.write(f"{x['fixture_id']}: {x['baseline_median_ms']:.7f} -> {x['candidate_median_ms']:.7f}ms, gain{x['gain_pct']:.10f}%, slowerpairs{x['slower_pairs']}/3, strictguardfailed={x['guard_failed']}.\n\n")
 for k,v in Q['whole_process_costs'].items():f.write(f"Wholeprocess {k} median regression {v['median_regression_pct']:.10f}% (<=1% required).\n\n")
 f.write('SameexactacceptedE080ordinarynativebenchmark/solverbytesbotharms; no source/compiler variant.86units/4ignored perarm,2fixedunscoredwarmups,18scoredfullscientificrecords/138checkpoints exact;warmupsalsoexact. Initialchildmaskbeforeexecution verified andcontrollerrestoredforeachprocess. FullprocessCPU/lifetime/parentwall covercleanup/masksetup. Separatelog/arithmeticreplayagrees, allsamplesretained,nohistorical/RAMreferencepooling. D201full66device/CPU/physicalCFV/wrapper/query/save/lifecycle bytes remainexact;66fileextentsverifiedwithoutrehash. Allownedchildren terminal,locksabsent,acceptedsource/main/live/PTX unchanged. E080/GPU/compressed/16/defaultalllogicalaffinity stayslive; no newgainadopted. AllnewoutputX;goalactive.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: record physical core placement complete cycle screen'],cwd=h.REPO,check=True)
h.custody();print(json.dumps({'decision':Q['decision'],'observed_gain_pct':perf['observed_gain_pct'],'failed_gates':perf['failed_gates'],'all_owned_children_terminal':True,'new_gain_accepted':False}),flush=True)
