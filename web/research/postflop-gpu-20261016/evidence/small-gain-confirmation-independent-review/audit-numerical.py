"""Independent file-only audit. Execute only after root announces terminal family and comparison."""
import collections, datetime, hashlib, json, math, pathlib, re, statistics
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OUT=ROOT/'comparisons/small-gain-confirmation-independent-review'
PLAN=ROOT/'runs/small-gain-confirmation-plan'
checks=collections.Counter(); pins={}

def ck(ok,label):
    if not ok:raise AssertionError(label)
    checks[label]+=1

def sha(path):
    path=pathlib.Path(path);h=hashlib.sha256(path.read_bytes()).hexdigest();pins[str(path)]=h;return h

def pin(path,want):ck(sha(path)==want,'frozen_hash')
def load(path):sha(path);return json.loads(pathlib.Path(path).read_text(encoding='utf-8-sig'))
def dt(x):return datetime.datetime.fromisoformat(x.replace('Z','+00:00'))
def gain(b,c):return 100*(b-c)/b

def same(actual,want,label):
    if isinstance(want,dict):
        ck(isinstance(actual,dict) and set(actual)==set(want),label+'_keys')
        for key,value in want.items():same(actual[key],value,label)
    elif isinstance(want,list):
        ck(isinstance(actual,list) and len(actual)==len(want),label+'_length')
        for a,b in zip(actual,want):same(a,b,label)
    elif isinstance(want,float):ck(isinstance(actual,(float,int)) and math.isfinite(actual) and math.isclose(actual,want,rel_tol=1e-12,abs_tol=1e-9),label)
    else:ck(actual==want,label)

def dist(v,component=False):
    m=statistics.median(v)
    if component:return dict(count=len(v),median_ms=m,min_ms=min(v),max_ms=max(v),range_ms=max(v)-min(v),raw_ms=v)
    return dict(count=len(v),median=m,median_absolute_deviation=statistics.median(abs(x-m) for x in v),min=min(v),max=max(v),range=max(v)-min(v),raw=v)

TIMING={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
def normalized(obj,stage=False):return {k:v for k,v in obj.items() if k not in TIMING and not(stage and k=='solve_checks_elapsed_ms')}
def parse(identity):
    r=load(ROOT/f'runs/{identity}/report.json');path=ROOT/f'runs/{identity}/stdout.log';pin(path,r['stdout_sha256'])
    text=path.read_text(encoding='utf-8');results=[];stages=[]
    for line in text.splitlines():
        for marker,dest in [('AUTORESEARCH_RESULT ',results),('AUTORESEARCH_STAGE ',stages)]:
            if marker in line:dest.append(json.loads(line.split(marker,1)[1]))
    ck(results==r['results'] and stages==[x['data'] for x in r['stages']],'raw_report_equality')
    return r,text,results,stages

def main():
    ck(not (OUT/'numerical-validation.json').exists(),'immutable_new_review')
    terminal=load(OUT/'numerical-terminal-inputs.json')
    ck(terminal['root_all_native_terminal'] is True and terminal['root_comparison_announced'] is True,'root_terminal_permission')
    pin(PLAN/'authorization.json','193b030dc4014176b26218b2c87d90acee5deadb71d2f916b18974f33c30402d')
    pin(PLAN/'scripts-manifest.json','34e9a0372539975170a01d3d137f483fb9656839d0faeb6dd3f6a3a67044131f')
    pin(PLAN/'protocol.json','6a81d6a768f234e46cd148960ecdefa1c396985508616833ac081644a634517b')
    pin(PLAN/'schedule.json','16b1e0b18e162f3bcf8c75b9b1379ba9f42a85d198523666035392a6b736cc0a')
    P=load(PLAN/'protocol.json');S=load(PLAN/'schedule.json');seal=load(PLAN/'scripts-manifest.json')
    for n in ['assess.py','common.py','run.py']:pin(PLAN/n,seal['script_sha256'][n])
    EX=ROOT/P['execution_output'];CP=ROOT/P['comparison_output']
    pin(CP/'report.json',terminal['comparison_sha256']);C=load(CP/'report.json')
    ck(C['id']==P['id'] and C['protocol_sha256']==sha(PLAN/'protocol.json') and C['schedule_sha256']==sha(PLAN/'schedule.json'),'comparison_protocol')
    ck(C['authorization_sha256']==sha(PLAN/'authorization.json') and C['effective_policy']==P['policy'],'comparison_effective_policy')
    ck(C['family_size']==4 and C['fresh_evaluator_processes']==128 and C['exactness']=={'fixture_results':384,'convergence_records':2944,'all_exact_to_accepted_anchor':True},'comparison_complete_scope')
    ck(C['historical_timing_samples_used']==0 and C['excluded_samples']==[] and C['extension_runs']==0 and C['candidate_accepted'] is False,'no_pooling_extensions_adoption')
    ck(P['family']==['E007','E008','E032','E036'] and len(S['pairs'])==64 and len(set(S['measurement_order']))==128,'fixed_family')
    ck([i for row in S['pairs'] for i in row['order']]==S['measurement_order'],'adjacent_frozen_pairs')
    done=load(EX/'complete.json');inv=load(EX/'invocation.json');uc=load(EX/'units-complete.json')
    ck(done['measurement_order']==S['measurement_order'] and done['unit_order']==S['unit_order'] and uc['all_passed'] is True,'terminal_all_runs')
    ck(done['authorization_sha256']==sha(PLAN/'authorization.json') and done['schedule_sha256']==sha(PLAN/'schedule.json'),'terminal_authority')
    ck(inv['all_native_ids_previously_absent'] is True and inv['authorization_sha256']==sha(PLAN/'authorization.json'),'fresh_fixed_runs')
    ck(C['complete_sha256']==sha(EX/'complete.json') and dt(done['at'])<=dt(C['at']),'comparison_after_native_terminal')
    for n,h in uc['evidence_sha256'].items():pin(n,h)
    anchor_r,_,anchor,astages=parse(P['anchor'])
    for n in ['report.json','stdout.log']:pin(ROOT/f"runs/{P['anchor']}/{n}",seal['reference_sha256'][str(ROOT/f"runs/{P['anchor']}/{n}")])
    baseline_map=load(P['accepted_manifest']['path'])['source_sha256']
    priorunit=ROOT/'runs/V020-unit/stdout.log';sha(priorunit)
    prior_names=sorted(re.findall(r'^test (\S+) \.\.\.',priorunit.read_text(encoding='utf-8'),re.M))
    ck(len(prior_names)==88,'accepted_unit_inventory')
    reports={};payloads={};units={};count_results=0;count_checks=0;previous=dt(inv['at'])
    arm_by_id={i:'E020' for i in S['measurement_order']}
    for pair in S['pairs']:arm_by_id[pair['candidate_run']]=pair['candidate']
    unit_arm={P['arms'][c]['unit_id']:c for c in P['build_order']}
    for identity in S['unit_order']+S['measurement_order']:
        e=load(EX/(identity+'.exit.json'));start,end=dt(e['started_at']),dt(e['finished_at'])
        ck(e['returncode']==0 and e['error'] is None and e['cleanup'] is None,'wrapper_terminal_success')
        ck(previous<=start<=end,'serialized_wrapper_intervals');previous=end
        if identity==S['measurement_order'][0]:ck(dt(uc['at'])<=start,'units_complete_before_timing')
        r,text,res,st=parse(identity);ck(r['id']==identity and r['returncode']==0 and r['status']=='measured','native_success')
        ns,ne=dt(r['started_at']),dt(r['finished_at'])
        ck(ns.microsecond==ne.microsecond==0 and start.replace(microsecond=0)<=ns<=ne<=end,'second_precision_interval')
        arm=unit_arm[identity] if identity in unit_arm else arm_by_id[identity]
        kind='solver' if identity in unit_arm else 'postflop_autoresearch'
        bm=ROOT/f'binaries/SG-{arm}-{kind}.manifest.json';manifest=load(bm)
        ck(r['binary_sha256']==manifest['binary_sha256'] and r['binary_build_manifest']['sha256']==sha(bm) and r['binary_build_manifest']['data']==manifest and r['binary_build_manifest']['binary_hash_verified'] is True,'binary_source_association')
        ck(manifest['source_sha256']==(baseline_map|P['arms'][arm]['candidate_owned_sha256']),'right_arm_source_map')
        ck(r['environment']['RAYON_NUM_THREADS']=='16' and r['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and r['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and r['environment']['POSTFLOP_AUTORESEARCH_FIXTURE'] is None,'fixed_environment')
        summaries=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)
        if identity in unit_arm:
            info=P['arms'][arm];expected=(str(info['unit_inventory']['passed']),'0','4','0','0')
            ck(summaries==[expected] and r['test_pass_count']==int(expected[0]),'ordinary_summary')
            names=sorted(re.findall(r'^test (\S+) \.\.\.',text,re.M))
            ck(names==sorted(prior_names+info['focused_tests']),'ordinary_exact_inventory')
            for name in info['focused_tests']:
                block=re.search(r'^test '+re.escape(name)+r' \.\.\.(.*?)(?=^test |\Z)',text,re.M|re.S)
                ck(block is not None and block.group(1).strip().endswith('ok'),'focused_test_pass')
            marker=info['test_marker']
            if marker:ck([json.loads(line.split(marker['prefix'],1)[1]) for line in text.splitlines() if marker['prefix'] in line]==[marker['fields']],'focused_exact_marker')
            units[arm]={'summary':list(map(int,expected)),'focused_tests':info['focused_tests'],'marker':marker};continue
        ck(summaries==[('1','0','0','0','0')] and r['test_pass_count']==1,'evaluator_native_summary')
        ck(r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored'],'fixed_evaluator_invocation')
        ck([x['fixture_id'] for x in res]==P['expected_fixtures'],'three_fixture_order')
        ck([normalized(x) for x in res]==[normalized(x) for x in anchor],'entire_non_timing_result_exact')
        ck([normalized(x,True) for x in st]==[normalized(x,True) for x in astages],'entire_non_timing_stage_trajectory_exact')
        for z in res:
            f=z['fixture_id'];ts=[x for x in st if x['stage']=='convergence_check' and x['fixture_id']==f]
            ck([x['iteration'] for x in ts]==list(range(20,P['expected_stops'][f]+1,20)),'all_checkpoints')
            ck(z['iteration']==P['expected_stops'][f] and z['target_met'] is True and ts[-1]['exploit_bits']==z['exploit_bits'],'stopping_anchor')
            tc=[x for x in st if x['stage']=='timing_complete' and x['fixture_id']==f];ck(len(tc)==1,'one_timing_complete')
            ck(all(z[k]==v for k,v in tc[0].items() if k!='stage'),'raw_timing_stage_result_agreement')
            for field in TIMING:ck(isinstance(z[field],(float,int)) and math.isfinite(z[field]) and z[field]>0,'finite_positive_timings')
            count_checks+=len(ts)
        count_results+=len(res);reports[identity]=r;payloads[identity]=res
        pin(ROOT/f'runs/{identity}/report.json',C['preserved_artifacts'][str(ROOT/f'runs/{identity}/report.json')])
    ck(count_results==384 and count_checks==2944 and len(reports)==128,'all_fresh_results')
    arms={};fields=['full_cycle_ms','build_ms','init_ms','solve_ms','readback_ms']
    for arm in P['family']:
        ps=sorted([x for x in S['pairs'] if x['candidate']==arm],key=lambda x:x['pair']);published=C['arms'][arm]
        ck([x['pair'] for x in ps]==list(range(1,17)),'all16_pairs')
        ck(load(CP/(arm+'.json'))==published,'arm_report_matches_combined')
        for role in ['baseline','candidate']:
            ids=[x['baseline' if role=='baseline' else 'candidate_run'] for x in ps]
            ck(published['cohorts'][role]['run_ids']==ids and published['cohorts'][role]['count']==16,'all_samples_in_cohorts')
        fixture_rows=[];bscore=0;cscore=0;guard=[]
        for j,f in enumerate(P['expected_fixtures']):
            row=published['fixtures'][j];ck(row['fixture_id']==f,'fixture_report_order')
            for field in fields:
                for role,key in [('baseline','baseline'),('candidate','candidate_run')]:
                    values=[payloads[x[key]][j][field] for x in ps];same(row[role][field],dist(values,True),'component_distribution')
            b=[payloads[x['baseline']][j]['full_cycle_ms'] for x in ps];c=[payloads[x['candidate_run']][j]['full_cycle_ms'] for x in ps]
            bm,cm=statistics.median(b),statistics.median(c);fg=gain(bm,cm);same(row['observed_gain_pct'],fg,'fixture_gain')
            bscore+=bm;cscore+=cm;slower=[-gain(x,y) for x,y in zip(b,c)];n=sum(x>0 for x in slower)
            guard.append(dict(fixture_id=f,median_slowdown_pct=-fg,paired_slowdown_pct=slower,strictly_slower_pairs=n,required_slower_pairs=9,failed=-fg>0 and n>=9))
            fixture_rows.append(dict(fixture=f,baseline_median_ms=bm,candidate_median_ms=cm,gain_pct=fg))
        pairg=[];diffs=[];pairs=[]
        for i,pair in enumerate(ps):
            b=payloads[pair['baseline']];c=payloads[pair['candidate_run']];bt=sum(x['full_cycle_ms'] for x in b);ct=sum(x['full_cycle_ms'] for x in c)
            rec=dict(baseline_id=pair['baseline'],candidate_id=pair['candidate_run'],order=pair['order'],baseline_full_cycle_ms=bt,candidate_full_cycle_ms=ct,observed_gain_pct=gain(bt,ct),fixture_gain_pct={f:gain(x['full_cycle_ms'],y['full_cycle_ms']) for f,x,y in zip(P['expected_fixtures'],b,c)},block=pair['block'],round=pair['round'],orientation=pair['orientation'])
            same(published['pairs'][i],rec,'pair_record');pairs.append(rec);pairg.append(gain(bt,ct));diffs.append(bt-ct)
        block=[dict(block=i,gain_pct=dist([g for p,g in zip(ps,pairg) if p['block']==i])) for i in range(1,5)]
        order=[dict(orientation=o,gain_pct=dist([g for p,g in zip(ps,pairg) if p['orientation']==o])) for o in ['BC','CB']]
        ck(all(x['gain_pct']['count']==4 for x in block) and all(x['gain_pct']['count']==8 for x in order),'fixed_stratum_sizes')
        aggregate=gain(bscore,cscore);wins=sum(x>0 for x in diffs)
        gates=dict(aggregate_ge_1pct=aggregate>=1,at_least13_positive_pairs=wins>=13,paired_median_positive=statistics.median(pairg)>0,every_block_median_positive=all(x['gain_pct']['median']>0 for x in block),both_orientation_medians_positive=all(x['gain_pct']['median']>0 for x in order),fixture_guard_pass=not any(x['failed'] for x in guard))
        expected=dict(baseline_full_cycle_ms=bscore,candidate_full_cycle_ms=cscore,observed_gain_pct=aggregate,required_gain_pct=1.0,positive_pairs=wins,pair_outcomes=dict(wins=wins,ties=sum(x==0 for x in diffs),losses=sum(x<0 for x in diffs)),paired_gain_pct=dist(pairg),paired_difference_ms=dist(diffs),blocks=block,order_strata=order,fixture_regression_guard=guard,gates=gates,timing_gate_pass=all(gates.values()),statistical_significance_established=False)
        for k,v in expected.items():same(published['performance'][k],v,'performance_'+k)
        decision='qualifying_pending_cost_and_broader_gates' if all(gates.values()) else 'rejected'
        ck(published['decision']==decision and published['candidate_accepted'] is False,'unaccepted_correct_decision')
        ck(published['exactness']=={'complete_non_timing_results':96,'convergence_records':736,'accepted_anchor':P['anchor'],'pass':True},'published_exactness')
        ck(published['adoption_requirements']==P['conditional_adoption_requirements'] and published['cost_validation'].startswith('pending;'),'qualification_costs_pending')
        arms[arm]=dict(decision=decision,performance=expected,fixtures=fixture_rows,pairs=pairs)
    ck(C['chronology']==[dict(id=i,started_at=reports[i]['started_at'],finished_at=reports[i]['finished_at']) for i in S['measurement_order']],'published_chronology')
    sha(__file__)
    result=dict(id='small-gain-confirmation-independent-numerical-review',at=datetime.datetime.now(datetime.timezone.utc).isoformat(),verdict='PASS_FIXED_FAMILY_NUMERICAL_AUDIT',independent_numerical_audit_pass=True,comparison_sha256=sha(CP/'report.json'),all384_complete_non_timing_results_exact=True,all2944_checkpoints_exact=True,all_normalized_stage_trajectories_exact=True,unit_screens=units,arms=arms,checks=dict(checks),assertions=sum(checks.values()),input_sha256=pins,scope='Independent file-only recomputation; no assessor/helper import, no native or GPU execution. Source/build/lock/custody reviewed separately.',limits=['Four selected hypotheses; operational fixed-sample rule, no calibrated statistical confidence or additive speedup claim.','Timing qualification is not adoption: material memory/compatibility costs and broader/holdout/cumulative qualification remain pending.','Component summaries are descriptive; component medians need not sum to complete-cycle medians.'],candidate_accepted=False,native_or_gpu_executed_by_reviewer=False)
    (OUT/'numerical-validation.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'audit_pass':True,'report_sha256':sha(OUT/'numerical-validation.json'),'arms':{k:dict(decision=v['decision'],gain_pct=v['performance']['observed_gain_pct'],gates=v['performance']['gates']) for k,v in arms.items()}},indent=2))

if __name__=='__main__':main()
