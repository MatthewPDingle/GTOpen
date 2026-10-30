"""Assess the fixed full-readback diagnostic cohort; never accept a candidate."""
import hashlib, json, math, re, statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def finite_nonnegative(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
seal=read(HERE/'scripts-manifest.json')
authorization=read(HERE/'authorization.json')
assert authorization['candidate']=='D065'
assert authorization['independent_source_review_pass'] is True and authorization['independent_script_review_pass'] is True
assert authorization['evidence_sha256'][str(HERE/'scripts-manifest.json')]==sha(HERE/'scripts-manifest.json')
for name,digest in seal['script_sha256'].items():assert sha(HERE/name)==digest,name
for path,digest in seal['reference_sha256'].items():assert sha(path)==digest,path
for path,digest in authorization['evidence_sha256'].items():assert sha(path)==digest,path
plan=read(HERE/'protocol.json');schema=read(HERE/'source/schema.json')
assert plan['candidate']=='D065' and plan['performance_acceptance'] is False
assert not (ROOT/'gpu-run.lock').exists()
assert read(ROOT/'runs/D065-execution/complete.json')['order']==plan['order']

timing={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
reference_results=reference_checks=None
runs={};all_profiles=[]
candidate_ids=[pair['candidate'] for pair in plan['pairs']]
baseline_ids=[pair['baseline'] for pair in plan['pairs']]
accepted_manifest=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')
candidate_manifest=read(ROOT/'binaries/D065-postflop_autoresearch.manifest.json')
assert sha(ROOT/'binaries/D065-postflop_autoresearch.exe')==candidate_manifest['binary_sha256']
assert sha(ROOT/'binaries/E020-postflop_autoresearch.exe')==plan['reference_binary_sha256']
assert sha(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')==plan['reference_manifest_sha256']
assert candidate_manifest['primary_protocol_sha256']==sha(HERE/'protocol.json')
assert candidate_manifest['probe_authorization_sha256']==sha(HERE/'authorization.json')
assert candidate_manifest['build_script_sha256']==sha(HERE/'build.py')
expected_sources={**accepted_manifest['source_sha256'],**plan['candidate_owned_sha256']}
assert candidate_manifest['source_sha256']==expected_sources
identities={v['fixture_id']:v for v in plan['expected_identity']}

for identity in plan['order']:
    directory=ROOT/'runs'/identity
    report=read(directory/'report.json')
    assert report['id']==identity and report['kind']=='diagnostic'
    assert report['status']=='measured' and report['returncode']==0 and report['test_pass_count']==1
    instrumented=identity in candidate_ids
    binary_name='D065-postflop_autoresearch' if instrumented else 'E020-postflop_autoresearch'
    expected_manifest=candidate_manifest if instrumented else accepted_manifest
    assert report['binary_sha256']==expected_manifest['binary_sha256']
    assert report['binary_build_manifest']['sha256']==sha(ROOT/'binaries'/(binary_name+'.manifest.json'))
    assert report['binary_build_manifest']['data']==expected_manifest and report['binary_build_manifest']['binary_hash_verified'] is True
    assert report['stdout_sha256']==sha(directory/'stdout.log')
    assert report['command']==[str(ROOT/'binaries'/(binary_name+'.exe')),'postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
    for key,value in {'RAYON_NUM_THREADS':'16','POSTFLOP_AUTORESEARCH_FIXTURE':None,
                       'POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'}.items():
        assert report['environment'][key]==value
    invocation=read(ROOT/'runs/D065-execution'/(identity+'.invocation.json'))
    assert invocation['environment_overrides']=={plan['runtime_flag']:'1' if instrumented else '0'}
    assert invocation['command'][invocation['command'].index('--id')+1]==identity
    assert invocation['command'][invocation['command'].index('--binary')+1]==str(ROOT/'binaries'/(binary_name+'.exe'))
    raw=(directory/'stdout.log').read_text(encoding='utf-8')
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','0')]
    results=[];checks=[];profiles=[];builds={};starts={};timings={}
    fixture=stage=None
    for line in raw.splitlines():
        if 'AUTORESEARCH_STAGE ' in line:
            record=json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]);stage=record['stage']
            if stage=='fixture_start':
                fixture=record['fixture_id'];assert fixture not in starts
                starts[fixture]=record
            if stage=='build_complete':
                assert record['fixture_id']==fixture and fixture not in builds
                builds[fixture]=record
            if stage=='timing_complete':
                assert record['fixture_id']==fixture and fixture not in timings
                timings[fixture]=record
            if stage=='convergence_check':
                checks.append({key:record[key] for key in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']})
        if 'AUTORESEARCH_RESULT ' in line:
            results.append(json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]))
        if 'LIFECYCLE_PROFILE ' in line:
            assert stage=='convergence_check' and fixture in plan['expected_fixtures']
            assert checks and checks[-1]['fixture_id']==fixture and checks[-1]['iteration']==plan['expected_stops'][fixture]
            record=json.loads(line.split('LIFECYCLE_PROFILE ',1)[1])
            assert set(record)==set(schema['fixed_fields'])|set(schema['fields'])
            for key,value in schema['fixed_fields'].items():
                assert type(record[key]) is type(value) and record[key]==value,key
            assert isinstance(record['thread'],str) and record['thread']
            assert record['note']==plan['expected_trace_note']
            assert finite_nonnegative(record['wall_ms_before_logging'])
            assert len(record['spans'])==len(schema['ordered_spans'])==plan['expected_spans_per_record']==14
            for span,expected in zip(record['spans'],schema['ordered_spans']):
                assert set(span)=={'stage','player','arena','bytes','wall_ms'}
                assert finite_nonnegative(span['wall_ms'])
                for key in ['stage','player','arena']:
                    assert type(span[key]) is type(expected[key]) and span[key]==expected[key],key
                if expected['player'] is None:assert span['bytes'] is None
                else:
                    assert type(span['bytes']) is int
                    assert span['bytes']==plan['expected_device_arena_bytes'][fixture][expected['player']]
            assert record['wall_ms_before_logging']+1e-6>=sum(span['wall_ms'] for span in record['spans'])
            assert starts[fixture]['board']==identities[fixture]['board']
            profiles.append({'run_id':identity,'fixture_id':fixture,**record})
    assert results==report['results']
    assert len(results)==3 and [v['fixture_id'] for v in results]==plan['expected_fixtures']
    assert list(starts)==list(builds)==list(timings)==plan['expected_fixtures']
    assert len(checks)==plan['expected_convergence_records_per_run']==23
    for result in results:
        fixture=result['fixture_id'];build=builds[fixture]
        assert result['iteration']==plan['expected_stops'][fixture] and result['target_met'] is True
        assert result['storage']=='compressed' and result['target_pct']==.3 and result['check_every']==20 and result['max_iterations']==400
        assert all(finite_nonnegative(result[key]) for key in timing)
        assert result['full_cycle_ms']>0 and result['build_ms']==build['build_ms']
        assert result['readback_ms']==timings[fixture]['readback_ms']
        assert result['nodes']==build['nodes']==identities[fixture]['node_count']
        assert build['hands']==identities[fixture]['hands']
        assert [c['iteration'] for c in checks if c['fixture_id']==fixture]==list(range(20,result['iteration']+1,20))
    exact=[{k:v for k,v in result.items() if k not in timing} for result in results]
    if reference_results is None:reference_results,reference_checks=exact,checks
    else:assert exact==reference_results and checks==reference_checks,identity
    if instrumented:
        assert len(profiles)==plan['expected_profile_records_per_run']==3
        assert [v['fixture_id'] for v in profiles]==plan['expected_fixtures']
        for record in profiles:
            assert timings[record['fixture_id']]['readback_ms']+1e-6>=record['wall_ms_before_logging']
        all_profiles.extend(profiles)
    else:assert identity in baseline_ids and not profiles
    runs[identity]={'results':results,'profiles':profiles,'builds':builds,'process_wall_ms':report['process_wall_ms'],
                    'report_sha256':sha(directory/'report.json'),'stdout_sha256':sha(directory/'stdout.log'),'invocation_sha256':sha(ROOT/'runs/D065-execution'/(identity+'.invocation.json'))}

fixtures=[]
for index,fixture in enumerate(plan['expected_fixtures']):
    base_values=[runs[name]['results'][index]['full_cycle_ms'] for name in baseline_ids]
    prof_values=[runs[name]['results'][index]['full_cycle_ms'] for name in candidate_ids]
    b,p=statistics.median(base_values),statistics.median(prof_values)
    records=[runs[name]['profiles'][index] for name in candidate_ids]
    values_by_stage={name:[sum(s['wall_ms'] for s in r['spans'] if s['stage']==name) for r in records] for name in plan['stage_names']}
    # Group within each run before taking medians; component medians need not add.
    values_by_stage['transfer_host_ms']=[a+b for a,b in zip(values_by_stage['dtoh_host_call'],values_by_stage['dtoh_stream_wait'])]
    values_by_stage['cpu_encode_scatter_restore_ms']=list(values_by_stage['encode_scatter_restore_cpu'])
    values_by_stage['optimistic_overlap_ceiling_ms']=[min(t,e) for t,e in zip(values_by_stage['transfer_host_ms'],values_by_stage['cpu_encode_scatter_restore_ms'])]
    values_by_stage['measured_span_sum_ms']=[sum(s['wall_ms'] for s in r['spans']) for r in records]
    values_by_stage['full_readback_before_logging_ms']=[r['wall_ms_before_logging'] for r in records]
    values_by_stage['trace_timer_bookkeeping_residual_ms']=[r['wall_ms_before_logging']-sum(s['wall_ms'] for s in r['spans']) for r in records]
    values_by_stage['outer_readback_minus_trace_ms']=[runs[name]['results'][index]['readback_ms']-r['wall_ms_before_logging'] for name,r in zip(candidate_ids,records)]
    components=[{'stage':name,'all_profiled_ms':values,'median_ms':statistics.median(values),'range_ms':[min(values),max(values)]} for name,values in values_by_stage.items()]
    ordered_components=[]
    for slot,expected in enumerate(schema['ordered_spans']):
        values=[r['spans'][slot]['wall_ms'] for r in records]
        ordered_components.append({'ordinal':slot,'stage':expected['stage'],'player':expected['player'],'arena':expected['arena'],
            'bytes':records[0]['spans'][slot]['bytes'],'all_profiled_ms':values,'median_ms':statistics.median(values),'range_ms':[min(values),max(values)]})
    fixtures.append({'fixture_id':fixture,'ordinary_full_cycles_ms':base_values,'instrumented_full_cycles_ms':prof_values,
        'ordinary_median_ms':b,'instrumented_median_ms':p,'median_change_pct':100*(p/b-1),
        'paired_change_pct':[100*(q/a-1) for a,q in zip(base_values,prof_values)],
        'ordinary_readback_ms':[runs[name]['results'][index]['readback_ms'] for name in baseline_ids],
        'instrumented_readback_ms':[runs[name]['results'][index]['readback_ms'] for name in candidate_ids],
        'identity':identities[fixture],'device_arena_bytes_per_player':plan['expected_device_arena_bytes'][fixture],
        'components':components,'ordered_spans':ordered_components,
        'optimistic_overlap_ceiling_pct_of_ordinary_fixture':100*statistics.median(values_by_stage['optimistic_overlap_ceiling_ms'])/b})
baseline_total=sum(f['ordinary_median_ms'] for f in fixtures)
profiled_total=sum(f['instrumented_median_ms'] for f in fixtures)
change=100*(profiled_total/baseline_total-1)
useful=abs(change)<=plan['usefulness_guard']['maximum_percent']
grouped={name:sum(next(c['median_ms'] for c in f['components'] if c['stage']==name) for f in fixtures) for name in values_by_stage}
result={'id':'D065-readback-diagnostic','status':'pass' if useful else 'inconclusive',
    'scope':'Grouped diagnostic host spans only; optimistic measured-span overlap ceiling is not a saving or candidate qualification.',
    'protocol_sha256':sha(HERE/'protocol.json'),'schema_sha256':sha(HERE/'source/schema.json'),
    'all_complete_states_exact':18,'convergence_checks_exact':138,'profile_records':len(all_profiles),'ordered_spans':14*len(all_profiles),'uninstrumented_records':0,
    'fixtures':fixtures,'raw_profiles':all_profiles,'ordinary_sum_fixture_medians_ms':baseline_total,
    'instrumented_sum_fixture_medians_ms':profiled_total,'observed_outer_change_pct':change,
    'absolute_change_limit_pct':10.0,'diagnostic_usefulness_guard_pass':useful,
    'grouped_stage_sum_fixture_medians_ms':grouped,
    'grouped_stage_fraction_of_ordinary_pct':{name:100*value/baseline_total for name,value in grouped.items()},
    'optimistic_overlap_ceiling_pct_of_ordinary':100*grouped['optimistic_overlap_ceiling_ms']/baseline_total,
    'possible_2pct_saving_established':False,
    'interpretation':'Copy host call plus existing wait is transfer-related host elapsed, not isolated PCIe duration. CPU spans include encoding, scatter and inactive restore. min(transfer_host,CPUencode) is only an optimistic measured-span overlap ceiling; unavoidable startup/tail, extra pinned buffers, bandwidth/contention and implementation costs remain unmeasured. No actual saving, family attribution or full-cycle headroom is proven. Grouped components/envelopes overlap and must not be summed. The10pct outer usefulness guard does not bound component bias.',
    'candidate_accepted':False,'deployment_changed':False,
    'native_process_wall_ms_including_teardown':{name:runs[name]['process_wall_ms'] for name in plan['order']},
    'evidence':{name:{'report_sha256':runs[name]['report_sha256'],'stdout_sha256':runs[name]['stdout_sha256'],'invocation_sha256':runs[name]['invocation_sha256']} for name in plan['order']},
    'binary_manifests':{'ordinary':sha(ROOT/'binaries/E020-postflop_autoresearch.manifest.json'),
                        'instrumented':sha(ROOT/'binaries/D065-postflop_autoresearch.manifest.json')}}
assert len(all_profiles)==9

destination=ROOT/'comparisons/D065-readback-diagnostic';destination.mkdir(exist_ok=False)
(destination/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({key:result[key] for key in ['status','observed_outer_change_pct','grouped_stage_sum_fixture_medians_ms','optimistic_overlap_ceiling_pct_of_ordinary','candidate_accepted']},indent=2))
