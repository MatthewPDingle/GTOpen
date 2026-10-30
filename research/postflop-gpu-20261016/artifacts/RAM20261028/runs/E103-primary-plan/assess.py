import json,sys,statistics,datetime
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
P=h.read(H/'protocol.json');h.custody()
for p,d in P['input_sha256'].items():h.pin(p,d)
done=h.read(H/'execution/complete.json');assert done['all_owned_children_terminal'] and done['protocol_sha256']==h.sha(H/'protocol.json')
reports={};pins={};last=None;units=warmups=scored=0
for row in P['sequence']:
 D=ROOT/'runs'/row['id'];r=h.read(D/'report.json');exit_=h.read(D/'exit.json');inv=h.read(D/'invocation.json');mask=P['masks'][row['arm']]
 assert r['returncode']==exit_['returncode']==0 and exit_['error'] is exit_['cleanup'] is None and r['arm']==inv['arm']==row['arm'] and r['affinity_mask']==inv['mask']==mask and r['workers']==16
 assert r['binary_sha256']==P['unit_binary_sha256' if row['kind']=='unit' else 'benchmark_binary_sha256'] and r['protocol_sha256']==h.sha(H/'protocol.json')
 begin=datetime.datetime.fromisoformat(exit_['started_at']);end=datetime.datetime.fromisoformat(exit_['finished_at']);assert begin<=end and(last is None or last<=begin);last=end
 w=exit_['affinity_spawn_witnesses'];assert len(w)==1 and w[0]['actual_child_at_spawn']['process_mask']==mask and w[0]['selected_parent_before_spawn']['process_mask']==mask
 assert w[0]['original_parent']==w[0]['restored_parent_after_spawn']==exit_['parent_final_affinity']=={'process_mask':P['masks']['baseline'],'system_mask':P['masks']['baseline']}
 t=exit_['terminal_process_times'];assert t==r['terminal_process_times'] and t['lifetime_ms']==(t['exit_FILETIME']-t['creation_FILETIME'])/10000 and t['CPU_ms']==(t['kernel_100ns']+t['user_100ns'])/10000
 assert t['lifetime_ms']<=exit_['parent_wall_ms']<t['lifetime_ms']+2000
 h.pin(D/'stdout.log',r['stdout_sha256']);pins[str(D/'report.json')]=h.sha(D/'report.json')
 if row['kind']=='unit':units+=1;continue
 assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
 if row['kind']=='warmup':warmups+=1;continue
 scored+=1;reports[row['id']]=r
assert units==warmups==2 and scored==6
fixtures=[];bs=cs=0.
for name in ['rainbow','two-tone','river']:
 b=[next(x['full_cycle_ms'] for x in reports[p['baseline']]['results'] if x['fixture_id']==name) for p in P['pairs']];c=[next(x['full_cycle_ms'] for x in reports[p['candidate']]['results'] if x['fixture_id']==name) for p in P['pairs']]
 bm,cm=statistics.median(b),statistics.median(c);bs+=bm;cs+=cm;gains=[100*(x-y)/x for x,y in zip(b,c)]
 fixtures.append({'fixture_id':name,'baseline_ms':b,'candidate_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'gain_pct':100*(bm-cm)/bm,'paired_gain_pct':gains,'slower_pairs':sum(v<0 for v in gains),'guard_failed':cm>bm and sum(v<0 for v in gains)>=2})
gain=100*(bs-cs)/bs;gates={'aggregate_ge1pct':gain>=P['minimum_aggregate_gain_pct'],'strict_fixture_clear':not any(x['guard_failed'] for x in fixtures)};costs={}
for metric in ['CPU_ms','lifetime_ms','parent_wall_ms']:
 b=[(reports[p['baseline']]['terminal_process_times'][metric] if metric!='parent_wall_ms' else h.read(ROOT/'runs'/p['baseline']/'exit.json')[metric]) for p in P['pairs']]
 c=[(reports[p['candidate']]['terminal_process_times'][metric] if metric!='parent_wall_ms' else h.read(ROOT/'runs'/p['candidate']/'exit.json')[metric]) for p in P['pairs']]
 regression=100*(statistics.median(c)/statistics.median(b)-1);costs[metric]={'baseline':b,'candidate':c,'median_regression_pct':regression};gates[metric+'_median_regression_le1pct']=regression<=P['max_process_cost_regression_pct']
passed=all(gates.values());D=ROOT/'comparisons/E103-three-pair-comparison';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'E103-primary','at':h.now(),'measurement_epoch':'RAM20261028','status':'fixed_affinity_primary_screen_complete','protocol_sha256':h.sha(H/'protocol.json'),'decision':'advance_to_separately_frozen_confirmation' if passed else 'rejected_closed','performance':{'aggregation':'Unrounded sum fixture medians,3observations perarm','baseline_full_cycle_ms':bs,'candidate_full_cycle_ms':cs,'observed_gain_pct':gain,'required_gain_pct':1.,'primary_timing_and_cost_pass':passed,'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'fixture_regression_guard':[{'fixture_id':x['fixture_id'],'median_slowdown_pct':-x['gain_pct'],'slower_pairs':x['slower_pairs'],'failed':x['guard_failed']} for x in fixtures]},'fixtures':fixtures,'whole_process_costs':costs,'ordinary_units_passed_per_arm':86,'ordinary_units_ignored_per_arm':4,'prespecified_unscored_warmups':2,'scored_processes':6,'unique_scored_records_exact':18,'unique_scored_checkpoints_exact':138,'actual_child_affinity_before_native_start_verified':True,'actual_workers_after_lifecycle_from_D201':16,'retained_report_sha256':pins,'excluded_samples':[],'extension_runs':0,'historical_or_RAM_reference_samples_used':0,'statistical_significance_established':False,'candidate_accepted':False,'later_requirements':P['adoption_requirements'],'scope':'One byte-identicalacceptedE080ordinarybenchmark andsolver binaries. Same16workers/quality/cadence/cap/stops/runtimeNVRTC/JIT clocks;onlyfixedchildaffinitymaskdiffers. FullprocessCPU/lifetime/parentwall includesdestructors andmasksetup. Initial3pair screencannotestablish significance/universal/no-tradeoff/adoption. No alternate sibling/CCDsubset/count/priority/OS/source/flags/samples rescue afterfailure.'})
print(json.dumps({'decision':'advance' if passed else 'rejected','observed_gain_pct':gain,'gates':gates,'costs':costs,'fixture_guards':[{'fixture_id':x['fixture_id'],'failed':x['guard_failed']} for x in fixtures]},indent=2),flush=True)
