import sys,json,statistics
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json');h.custody()
for path,digest in P['input_sha256'].items():h.pin(path,digest)
done=h.read(H/'execution/native-complete.json');assert done['all_owned_children_terminal']
records={};pins={};units=0;warmups=0;scored=0
for row in P['sequence']:
    directory=ROOT/'runs'/row['id'];r=h.read(directory/'report.json');receipt=h.read(directory/'exit.json');assert r['workers']==row['workers'] and r['kind']==row['kind'] and r['returncode']==receipt['returncode']==0
    assert r['protocol_sha256']==h.sha(H/'protocol.json') and receipt['error'] is receipt['cleanup'] is None
    h.pin(directory/'stdout.log',r['stdout_sha256']);t=receipt['terminal_process_times'];assert t==r['terminal_process_times'] and t['lifetime_ms']==(t['exit_FILETIME']-t['creation_FILETIME'])/10000 and t['CPU_ms']==(t['kernel_100ns']+t['user_100ns'])/10000
    assert receipt['parent_wall_ms']>=t['lifetime_ms'] and receipt['parent_wall_ms']<t['lifetime_ms']+2000
    pins[str(directory/'report.json')]=h.sha(directory/'report.json')
    if row['kind']=='unit':units+=1;continue
    assert h.exact(row['id'])==h.read(ROOT/'epoch/exact-anchor.json')
    if row['kind']=='warmup':warmups+=1;continue
    scored+=1;records[row['block'],row['workers']]=r
assert units==warmups==3 and scored==9
outcomes={};advancing=[]
for workers in [8,32]:
    base_sum=candidate_sum=0;fixtures=[]
    for name in ['rainbow','two-tone','river']:
        b=[next(x['full_cycle_ms'] for x in records[k,16]['results'] if x['fixture_id']==name) for k in [1,2,3]];c=[next(x['full_cycle_ms'] for x in records[k,workers]['results'] if x['fixture_id']==name) for k in [1,2,3]]
        bm=statistics.median(b);cm=statistics.median(c);base_sum+=bm;candidate_sum+=cm;slower=sum(y>x for x,y in zip(b,c));fixtures.append({'fixture_id':name,'reference_ms':b,'candidate_ms':c,'reference_median_ms':bm,'candidate_median_ms':cm,'gain_pct':100*(bm-cm)/bm,'slower_matched_blocks':slower,'guard_failed':cm>bm and slower>=2})
    gain=100*(base_sum-candidate_sum)/base_sum;costs={};gates={'aggregate_ge1pct':gain>=P['minimum_aggregate_gain_pct'],'strict_fixture_clear':not any(x['guard_failed'] for x in fixtures)}
    for metric in ['CPU_ms','lifetime_ms']:
        b=[records[k,16]['terminal_process_times'][metric] for k in [1,2,3]];c=[records[k,workers]['terminal_process_times'][metric] for k in [1,2,3]];delta=100*(statistics.median(c)/statistics.median(b)-1);costs[metric]={'reference':b,'candidate':c,'median_regression_pct':delta};gates[metric+'_median_regression_le1pct']=delta<=P['max_process_CPU_or_lifetime_median_regression_pct']
    passed=all(gates.values());outcomes[str(workers)]={'decision':'admit_separately_frozen_confirmation_and_broad_resource_qualification' if passed else 'rejected_closed','reference_sum_fixture_medians_ms':base_sum,'candidate_sum_fixture_medians_ms':candidate_sum,'observed_gain_pct':gain,'fixtures':fixtures,'whole_process_costs':costs,'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'candidate_accepted':False}
    if passed:advancing.append(workers)
D=ROOT/'comparisons/D169-worker-comparison';D.mkdir(exist_ok=False)
h.save(D/'report.json',{'id':'D169','at':h.now(),'status':'fixed_configuration_screen_complete','protocol_sha256':h.sha(H/'protocol.json'),'configuration_outcomes':outcomes,'advancing_worker_counts':advancing,'ordinary_units_passed_per_config':86,'ordinary_units_ignored_per_config':4,'prespecified_unscored_warmups':3,'scored_processes':9,'unique_scored_full_records_exact':27,'unique_scored_checkpoints_exact':207,'actual_workers_observed_after_all_work':True,'shared_reference_controls_prospectively_declared':True,'retained_report_sha256':pins,'excluded_samples':[],'extension_runs':0,'historical_or_RAM_baseline_timings_used':0,'statistical_significance_established':False,'new_gain_accepted':False,'scope':'SameunmodifiedacceptedE080solverlibrary andsinglefreshharnessforallcounts;originalcompletecycleclocksincludeactualNVRTC/JIT andquality. Workerqueryafterwholefunction. Initial3/configbalancedblocksumfixturemedianswithstrictfixtureandwholeprocessCPU/lifetimegates. Libraryunits/rawproofbeforetiming. Warmupsnot scored. Remainingpeak/broad/nonpostflop/holdout/fresh16/applicationqualificationmandatorybeforeadoption.'})
print(json.dumps({'status':'complete','outcomes':outcomes,'advancing':advancing}),flush=True)
