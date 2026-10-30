import sys,json,statistics,math
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'))
import common as h
P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
anchor=h.read(ROOT/'epoch/exact-anchor.json');O=H/'execution';gates={};resources={};rows={}
excluded={'build_ms','fingerprint_ms_excluded','full_cycle_ms','init_ms','readback_ms','solve_ms'}
for entry in P['sequence']:
    ident,arm=entry['id'],entry['arm'];R=h.read(O/(ident+'.resource.json'));resources[ident]=R
    text=(O/(ident+'.stdout.log')).read_text(encoding='utf-8')
    results=[json.loads(x.split('AUTORESEARCH_RESULT ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_RESULT ' in x]
    stages=[json.loads(x.split('AUTORESEARCH_STAGE ',1)[1]) for x in text.splitlines() if 'AUTORESEARCH_STAGE ' in x]
    conv=[{k:x[k] for k in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']} for x in stages if x.get('stage')=='convergence_check']
    gates[ident+':canonical_science_exact']=[[{k:v for k,v in x.items() if k not in excluded} for x in results],conv]==anchor
    current=None;items={f:[] for f in ['rainbow','two-tone','river']}
    for line in text.splitlines():
        if 'AUTORESEARCH_STAGE ' in line:
            x=json.loads(line.split('AUTORESEARCH_STAGE ',1)[1])
            if x.get('stage')=='fixture_start':current=x['fixture_id']
        if line.startswith('D157_RESOURCE '):
            x=json.loads(line.split('D157_RESOURCE ',1)[1]);assert current in items;items[current].append(x)
    rows[ident]=items;L=P['material_prerequisite_limits']
    gates[ident+':sampling_coverage']=R['sample_count']>=L['minimum_samples_per_process'] and R['max_sample_gap_ms']<=L['max_sample_gap_ms']
    gates[ident+':valid_terminal_times']=R['terminal_process_times']['lifetime_ms']>0 and R['terminal_process_times']['CPU_ms']>0
    gates[ident+':version_identity']=R['NVML_versions']==P['NVML_versions']
    for fixture,items_ in items.items():
        snaps=[x for x in items_ if x['kind']=='GPU_snapshot'];plans=[x for x in items_ if x['kind']=='packet_plan']
        expected=P['expected_candidate_module_activation'][fixture] and arm=='candidate'
        order=['gpu_ready','module_before','module_after','readback_complete'] if expected else ['gpu_ready','readback_complete']
        gates[ident+':'+fixture+':snapshot_order']=[x['stage'] for x in snaps]==order
        gates[ident+':'+fixture+':plan_count']=len(plans)==int(expected)
        if plans:gates[ident+':'+fixture+':plan_geometry']=plans[0]['capacity_bytes']==sum(plans[0]['capacities'])*plans[0]['block_bytes'] and all(a<=b for a,b in zip(plans[0]['lengths'],plans[0]['capacities']))
        if snaps:
            gates[ident+':'+fixture+':module_activation']=not snaps[0]['packet_module_loaded'] and snaps[-1]['packet_module_loaded']==expected
        if expected and len(snaps)==4:
            gates[ident+':'+fixture+':load_default_limits_unchanged']=all(snaps[1][k]==snaps[2][k] for k in ['context_stack_limit','context_heap_limit'])
        gates[ident+':'+fixture+':device_payload_stable']=len({x['explicit_device_payload_bytes'] for x in snaps})==1
for pair in P['pairs']:
    b,c=pair['baseline'],pair['candidate']
    for fixture in rows[b]:
        bs=[x for x in rows[b][fixture] if x['kind']=='GPU_snapshot'];cs=[x for x in rows[c][fixture] if x['kind']=='GPU_snapshot']
        for stage in ['gpu_ready','readback_complete']:
            bx=next(x for x in bs if x['stage']==stage);cx=next(x for x in cs if x['stage']==stage)
            for key in ['explicit_device_payload_bytes','pinned_bytes','current_CFV_words','current_regret_words','current_strategy_words','graphs_present','eval_graphs_present','context_stack_limit','context_heap_limit']:
                gates[b+':'+c+':'+fixture+':'+stage+':'+key]=bx[key]==cx[key]
            gates[b+':'+c+':'+fixture+':'+stage+':wrapper32']=cx['wrapper_bytes']==bx['wrapper_bytes']+32
def values(arm,key):
    return [resources[x['id']][key] for x in P['sequence'] if x['arm']==arm]
summary={}
for key,limitkey in [('reported_working_set_high_water_bytes','host_peak_working_set_max_added_bytes'),('reported_commit_high_water_bytes','host_peak_commit_max_added_bytes'),('sampled_global_GPU_used_max_bytes','sampled_device_global_max_added_bytes')]:
    b,c=values('baseline',key),values('candidate',key);allow=P['material_prerequisite_limits'][limitkey]
    summary[key]={'baseline':b,'candidate':c,'median_added':statistics.median(c)-statistics.median(b),'max_added':max(c)-max(b),'allowed_added_bytes':allow}
    gates[key+':median_within_fixed_allowance']=statistics.median(c)<=statistics.median(b)+allow
    gates[key+':max_within_fixed_allowance']=max(c)<=max(b)+allow
for metric,key,limitkey in [('CPU_ms','CPU_ms','process_CPU_median_max_regression_pct'),('process_lifetime_ms','lifetime_ms','whole_process_lifetime_median_max_regression_pct')]:
    b=[resources[x['id']]['terminal_process_times'][key] for x in P['sequence'] if x['arm']=='baseline'];c=[resources[x['id']]['terminal_process_times'][key] for x in P['sequence'] if x['arm']=='candidate']
    change=(statistics.median(c)/statistics.median(b)-1)*100
    summary[metric]={'baseline':b,'candidate':c,'median_regression_pct':change,'allowed_regression_pct':P['material_prerequisite_limits'][limitkey]}
    gates[metric+':median_within_fixed_allowance']=change<=P['material_prerequisite_limits'][limitkey]
passed=all(gates.values());h.custody();D=ROOT/'comparisons/D157-actual-resources';D.mkdir(exist_ok=False)
report={'id':'D157','at':h.now(),'status':'pass_scoped_actual_resource_prerequisites' if passed else 'rejected_actual_resource_prerequisite','protocol_sha256':h.sha(H/'protocol.json'),'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'resource_summary':summary,'diagnostic_geometry_and_module_rows':rows,'actual_process_resources':{k:{n:v for n,v in r.items() if n!='samples'} for k,r in resources.items()},'exact_full_scientific_records':12,'exact_checkpoints':92,'all_children_terminal':True,'source_main_live_PTX_custody_pass':True,'performance_qualification_samples':0,'candidate_accepted':False,'scope':'Fixed two resource pairs on original canonical workload history with small readonly driver/metadata observers and50ms parent Win32/NVML sampling. CPU and process wall cover termination including destructors. Reported host high-water counters may miss a late post-final-sample peak; device values are global sampled WDDM accounting. Fixed64MiB additive allowances and1% total CPU/lifetime regression are coarse feasibility filters,not universal no-cost/capacity guarantees or a speed score. Original D155coverage failure unchanged. Resource failure closes this E092 form without threshold/source/sample rescue.'}
h.save(D/'report.json',report);print(json.dumps({'status':report['status'],'failed_gates':report['failed_gates'],'resource_summary':summary}),flush=True)
