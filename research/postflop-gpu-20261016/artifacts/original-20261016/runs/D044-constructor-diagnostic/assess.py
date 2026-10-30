"""Assess the fixed constructor diagnostic cohort; never accept a candidate."""
import hashlib, json, math, re, statistics
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent.parent
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def finite_nonnegative(value):return type(value) in (int,float) and math.isfinite(value) and value>=0
seal=read(HERE/'scripts-manifest.json')
authorization=read(HERE/'authorization.json')
assert authorization['candidate']=='D044'
assert authorization['independent_source_review_pass'] is True and authorization['independent_script_review_pass'] is True
assert authorization['evidence_sha256'][str(HERE/'scripts-manifest.json')]==sha(HERE/'scripts-manifest.json')
for name,digest in seal['script_sha256'].items():assert sha(HERE/name)==digest,name
for path,digest in seal['reference_sha256'].items():assert sha(path)==digest,path
for path,digest in authorization['evidence_sha256'].items():assert sha(path)==digest,path
plan=read(HERE/'protocol.json');schema=read(HERE/'schema.json')
assert plan['candidate']=='D044' and plan['performance_acceptance'] is False
assert not (ROOT/'gpu-run.lock').exists()
assert read(ROOT/'runs/D044-execution/complete.json')['order']==plan['order']

timing={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
reference_results=reference_checks=None
runs={};all_profiles=[]
candidate_ids=[pair['candidate'] for pair in plan['pairs']]
baseline_ids=[pair['baseline'] for pair in plan['pairs']]
accepted_manifest=read(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')
candidate_manifest=read(ROOT/'binaries/D044-postflop_autoresearch.manifest.json')
assert sha(ROOT/'binaries/D044-postflop_autoresearch.exe')==candidate_manifest['binary_sha256']
assert sha(ROOT/'binaries/E020-postflop_autoresearch.exe')==plan['reference_binary_sha256']
assert sha(ROOT/'binaries/E020-postflop_autoresearch.manifest.json')==plan['reference_manifest_sha256']
assert candidate_manifest['primary_protocol_sha256']==sha(HERE/'protocol.json')
assert candidate_manifest['probe_authorization_sha256']==sha(HERE/'authorization.json')
assert candidate_manifest['build_script_sha256']==sha(HERE/'build.py')
expected_sources={**accepted_manifest['source_sha256'],**plan['candidate_owned_sha256']}
assert candidate_manifest['source_sha256']==expected_sources
identities={v['fixture_id']:v for v in schema['expected_identity']}

for identity in plan['order']:
    directory=ROOT/'runs'/identity
    report=read(directory/'report.json')
    assert report['id']==identity and report['kind']=='diagnostic'
    assert report['status']=='measured' and report['returncode']==0 and report['test_pass_count']==1
    instrumented=identity in candidate_ids
    binary_name='D044-postflop_autoresearch' if instrumented else 'E020-postflop_autoresearch'
    expected_manifest=candidate_manifest if instrumented else accepted_manifest
    assert report['binary_sha256']==expected_manifest['binary_sha256']
    assert report['binary_build_manifest']['sha256']==sha(ROOT/'binaries'/(binary_name+'.manifest.json'))
    assert report['binary_build_manifest']['data']==expected_manifest and report['binary_build_manifest']['binary_hash_verified'] is True
    assert report['stdout_sha256']==sha(directory/'stdout.log')
    assert report['command']==[str(ROOT/'binaries'/(binary_name+'.exe')),'postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
    for key,value in {'RAYON_NUM_THREADS':'16','POSTFLOP_AUTORESEARCH_FIXTURE':None,
                       'POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_PROFILE':'0'}.items():
        assert report['environment'][key]==value
    raw=(directory/'stdout.log').read_text(encoding='utf-8')
    assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','0')]
    results=[];checks=[];profiles=[];builds={};starts={}
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
            if stage=='convergence_check':
                checks.append({key:record[key] for key in ['fixture_id','iteration','exploit_bits','exploit_pct_pot','exploit_chips']})
        if 'AUTORESEARCH_RESULT ' in line:
            results.append(json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]))
        if 'SPOT_CONSTRUCTOR_PROFILE ' in line:
            assert stage=='fixture_start' and fixture in plan['expected_fixtures']
            record=json.loads(line.split('SPOT_CONSTRUCTOR_PROFILE ',1)[1])
            assert set(record)==set(schema['record'])
            assert record['schema_version']==1 and record['diagnostic_only'] is True
            assert record['instrumentation']=='D044_unconditional_source_only'
            assert record['extra_cuda_synchronizations']==0
            assert set(record['stage_us'])==set(plan['stage_names'])
            assert all(finite_nonnegative(v) for v in record['stage_us'].values())
            assert finite_nonnegative(record['constructor_us_before_logging'])
            assert record['constructor_us_before_logging']+1e-6>=sum(record['stage_us'].values())
            for key in ['board_mask','board_cards','node_count','suit_permutations']:
                assert type(record[key]) is int and record[key]>=0
            assert 1<=record['suit_permutations']<=24
            assert len(record['hands'])==2 and all(type(n) is int and n>0 for n in record['hands'])
            for key in ['board_mask','board_cards','hands','node_count']:assert record[key]==identities[fixture][key]
            assert starts[fixture]['board']==identities[fixture]['board']
            profiles.append({'run_id':identity,'fixture_id':fixture,**record})
    assert results==report['results']
    assert len(results)==3 and [v['fixture_id'] for v in results]==plan['expected_fixtures']
    assert list(starts)==list(builds)==plan['expected_fixtures']
    assert len(checks)==plan['expected_convergence_records_per_run']==23
    for result in results:
        fixture=result['fixture_id'];build=builds[fixture]
        assert result['iteration']==plan['expected_stops'][fixture] and result['target_met'] is True
        assert result['storage']=='compressed' and result['target_pct']==.3 and result['check_every']==20 and result['max_iterations']==400
        assert all(finite_nonnegative(result[key]) for key in timing)
        assert result['full_cycle_ms']>0 and result['build_ms']==build['build_ms']
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
            assert builds[record['fixture_id']]['build_ms']*1000+1e-6>=record['constructor_us_before_logging']
        all_profiles.extend(profiles)
    else:assert identity in baseline_ids and not profiles
    runs[identity]={'results':results,'profiles':profiles,'builds':builds,'process_wall_ms':report['process_wall_ms'],
                    'report_sha256':sha(directory/'report.json'),'stdout_sha256':sha(directory/'stdout.log')}

fixtures=[]
for index,fixture in enumerate(plan['expected_fixtures']):
    base_values=[runs[name]['results'][index]['full_cycle_ms'] for name in baseline_ids]
    prof_values=[runs[name]['results'][index]['full_cycle_ms'] for name in candidate_ids]
    b,p=statistics.median(base_values),statistics.median(prof_values)
    records=[runs[name]['profiles'][index] for name in candidate_ids]
    assert len({v['suit_permutations'] for v in records})==1
    components=[]
    values_by_stage={name:[r['stage_us'][name]/1000 for r in records] for name in plan['stage_names']}
    values_by_stage['constructor_before_logging']=[r['constructor_us_before_logging']/1000 for r in records]
    values_by_stage['unprofiled_constructor_and_timer_overhead']=[(r['constructor_us_before_logging']-sum(r['stage_us'].values()))/1000 for r in records]
    values_by_stage['unprofiled_constructor_CPU_storage_and_timing_logging_overhead']=[runs[name]['results'][index]['build_ms']-sum(r['stage_us'].values())/1000 for name,r in zip(candidate_ids,records)]
    values_by_stage['outer_build_minus_constructor_CPU_storage_return_logging_other_overhead']=[runs[name]['results'][index]['build_ms']-r['constructor_us_before_logging']/1000 for name,r in zip(candidate_ids,records)]
    for name,values in values_by_stage.items():
        components.append({'stage':name,'all_profiled_ms':values,'median_ms':statistics.median(values),'range_ms':[min(values),max(values)]})
    fixtures.append({'fixture_id':fixture,'ordinary_full_cycles_ms':base_values,'instrumented_full_cycles_ms':prof_values,
        'ordinary_median_ms':b,'instrumented_median_ms':p,'median_change_pct':100*(p/b-1),
        'paired_change_pct':[100*(q/a-1) for a,q in zip(base_values,prof_values)],
        'ordinary_build_ms':[runs[name]['results'][index]['build_ms'] for name in baseline_ids],
        'instrumented_build_ms':[runs[name]['results'][index]['build_ms'] for name in candidate_ids],
        'identity':{**identities[fixture],'suit_permutations':records[0]['suit_permutations']},'components':components})
baseline_total=sum(f['ordinary_median_ms'] for f in fixtures)
profiled_total=sum(f['instrumented_median_ms'] for f in fixtures)
change=100*(profiled_total/baseline_total-1)
useful=abs(change)<=plan['usefulness_guard']['maximum_percent']
grouped={name:sum(next(c['median_ms'] for c in f['components'] if c['stage']==name) for f in fixtures) for name in plan['stage_names']}
result={'id':'D044-constructor-diagnostic','status':'pass' if useful else 'inconclusive',
    'scope':'Grouped diagnostic host spans only; no performance acceptance or projected saving.',
    'protocol_sha256':sha(HERE/'protocol.json'),'schema_sha256':sha(HERE/'schema.json'),
    'all_complete_states_exact':18,'convergence_checks_exact':138,'profile_records':len(all_profiles),'uninstrumented_records':0,
    'fixtures':fixtures,'raw_profiles':all_profiles,'ordinary_sum_fixture_medians_ms':baseline_total,
    'instrumented_sum_fixture_medians_ms':profiled_total,'observed_outer_change_pct':change,
    'absolute_change_limit_pct':10.0,'diagnostic_usefulness_guard_pass':useful,
    'grouped_stage_sum_fixture_medians_ms':grouped,
    'grouped_stage_fraction_of_ordinary_pct':{name:100*value/baseline_total for name,value in grouped.items()},
    'possible_2pct_saving_established':False,
    'interpretation':'The river-table span contains the entire unchanged builder, not isolated ranking. No removable fraction is established. Residuals include unprofiled constructor/CPU storage and timing/logging overhead. Overlapping envelopes and residuals must not be summed as disjoint components. The10pct outer usefulness guard does not bound component bias or establish a performance saving.',
    'candidate_accepted':False,'deployment_changed':False,
    'native_process_wall_ms_including_teardown':{name:runs[name]['process_wall_ms'] for name in plan['order']},
    'evidence':{name:{'report_sha256':runs[name]['report_sha256'],'stdout_sha256':runs[name]['stdout_sha256']} for name in plan['order']},
    'binary_manifests':{'ordinary':sha(ROOT/'binaries/E020-postflop_autoresearch.manifest.json'),
                        'instrumented':sha(ROOT/'binaries/D044-postflop_autoresearch.manifest.json')}}
assert len(all_profiles)==9
destination=ROOT/'comparisons/D044-constructor-diagnostic';destination.mkdir(exist_ok=False)
(destination/'report.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({key:result[key] for key in ['status','observed_outer_change_pct','grouped_stage_sum_fixture_medians_ms','candidate_accepted']},indent=2))
