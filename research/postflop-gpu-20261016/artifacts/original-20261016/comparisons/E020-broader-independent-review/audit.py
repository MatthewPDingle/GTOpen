import pathlib,json,hashlib,datetime,re,math,itertools,collections
R=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');O=R/'comparisons/E020-broader-independent-review';P=R/'runs/E020-qualification-plan-r3';art={};checks=collections.Counter()
def ck(v,label):
    assert v,label;checks[label]+=1
def sha(p):return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()
def pin(p,h=None):
    p=pathlib.Path(p);d=sha(p);ck(h is None or d==h,'artifact_hash');art[str(p)]=d;return d
def load(p):pin(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def dt(v):return datetime.datetime.fromisoformat(v.replace('Z','+00:00'))
def unique(pairs):
    d={}
    for k,v in pairs:ck(k not in d,'unique_json_key');d[k]=v
    return d
def bad(v):raise AssertionError('nonfinite JSON '+v)
def markers(raw,tag):
    return [json.loads(x.split(tag+' ',1)[1],object_pairs_hook=unique,parse_constant=bad) for x in raw.splitlines() if tag+' ' in x]
def smap(m):return {k.replace('\\','/'):v.lower() for k,v in m.get('source_sha256',m.get('hashes',{})).items()}
def norm(x,excluded):return {k:v for k,v in x.items() if k not in excluded}
TIMING={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
proto=load(P/'protocol.json');auth=load(P/'authorization.json');pin(P/'authorization.json','e935a6b3f29f4de2b44cb7724adc6499119b68afa1934265e218dd76f559c76f')
ready=load(P/'all-builds-ready.json');pin(P/'all-builds-ready.json','4c53c85b4d7e83915ce31ec93d13a0dc916d8aca5c722441152e10886a6fdda0')
for n,h in auth['evidence_sha256'].items():pin(n,h)
for n,h in load(P/'input-pins.json').items():pin(n,h)
prep=load(P/'prepared-manifest.json');pin(P/'prepared-manifest.json',auth['prepared_manifest_sha256'])
for n,h in prep['artifact_sha256'].items():pin(P/n,h)
C=load(R/'comparisons/E020-broader-qualification/report.json');S=load(R/'comparisons/E020-controls-comparison/report.json');inv=load(R/'runs/E020-qualification-execution/invocation.json');pin(C['invocation']['path'],C['invocation']['sha256'])
ck(inv['authorization_sha256']==sha(P/'authorization.json') and inv['all_builds_ready_sha256']==sha(P/'all-builds-ready.json')==C['all_builds_ready_sha256'],'execution_gate_pins')
ck(inv['order']==[x['id'] for x in proto['controls']],'fixed_nine_order');ck(C['status']=='pass' and C['error'] is None and not C['accepted'] and not C['deployed'] and not C['performance_claim'],'provisional_broader_pass_only')
ck((C['original_snapshots'],C['f32_fixtures'],C['gpu_tests'],C['continuation_tests'])==(160,3,6,3),'published_counts')
ck([x['id'] for x in C['checks']]==inv['order'],'published_fixed_checks')
for n,h in C['verified_artifacts'].items():pin(n,h)
source=load(P/'primary-source.json');original=load(R/'binaries/baseline-complete.manifest.json');original_source=smap(original);runs={};raws={};summaries={};manifests={}
for row in proto['controls']:
    identity=row['id'];d=R/'runs'/identity;r=load(d/'report.json');raw=(d/'stdout.log').read_text();pin(d/'stdout.log',r['stdout_sha256']);runs[identity]=r;raws[identity]=raw
    ck(r['id']==identity and r['status']=='measured' and r['returncode']==0 and r['test_pass_count']==row['passes'],'run_success')
    bm=r['binary_build_manifest'];pin(bm['path'],bm['sha256']);m=load(bm['path']);manifests[identity]=m;ck(bm['data']==m and bm['binary_hash_verified'] and m['binary_sha256']==r['binary_sha256'],'binary_manifest_relation')
    expected=inv['binary_pins'][row['binary']];pin(r['command'][0],expected['binary_sha256']);ck(r['binary_sha256']==expected['binary_sha256'] and bm['sha256']==expected['manifest_sha256'],'fixed_executed_binary')
    ck(smap(m)==(original_source if row['binary']=='baseline-complete' else source),'actual_binary_source_map')
    ck(r['provenance']['source_sha256']==source,'runtime_checkout_is_candidate_snapshot')
    command=[] if row['test']=='*' else [row['test']];command+=['--nocapture','--test-threads=1']+([] if row['ordinary'] else ['--ignored']);ck(r['command'][1:]==command,'native_command_exact')
    found=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out; finished in ([0-9.]+)s',raw);ck(len(found)==1,'one_native_summary');summary=tuple(map(int,found[0][:5]));summaries[identity]=summary;ck(summary[:4]==(row['passes'],0,0,0),'executed_pass_no_ignored')
    ck(summary[4]==({'V020-continuation-rejection':2,'V020-continuation-stored':199}.get(identity,0)),'expected_filter_count')
    if row['test']!='*':ck(bool(re.search(r'^test '+re.escape(row['test'])+r' \.\.\.',raw,re.M)),'named_test_executed')
    e=r['environment'];ck(e['RAYON_NUM_THREADS']=='16' and e['POSTFLOP_AUTORESEARCH_STORAGE']==row['storage'] and e['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and e['POSTFLOP_AUTORESEARCH_FIXTURE'] is None,'fixed_runtime_environment')
    for key in ['live_status_before','live_status_at_launch']:
        ck(r[key]['/api/status']['state']!='running' and not r[key]['/api/reports/status']['running'],'no_live_solve')
    ck(r['disk_free_bytes']>=50*1024**3,'disk_reserve')
for a,b in zip(inv['order'],inv['order'][1:]):ck(dt(runs[a]['finished_at'])<=dt(runs[b]['started_at']),'serialized_nine_chronology')
ck(dt(ready['at'])<dt(inv['at'])<=dt(runs[inv['order'][0]]['started_at']) and dt(runs[inv['order'][-1]]['finished_at'])<=dt(C['at']),'readiness_before_native_and_terminal_comparison')
# Independently parse immutable-original control records; do not call the same comparison helper.
specs=[('state','V020-state','V000-state-baseline','states',12,24),('menu','V020-menu','V000-menu-baseline','menu_states',12,24),('resume','V020-resume','V000-resume-baseline-r','resume_states',16,112)];control_rows=[]
for suite,cid,bid,field,nrecords,nsnap in specs:
    br=load(R/f'runs/{bid}/report.json');braw=(R/f'runs/{bid}/stdout.log').read_text();pin(R/f'runs/{bid}/stdout.log',br['stdout_sha256']);bm=br['binary_build_manifest'];pin(bm['path'],bm['sha256']);pin(br['command'][0],br['binary_sha256']);bs=smap(bm['data'])
    for k,v in bs.items():
        if k.startswith('crates/solver/src/') and k in original_source:ck(v==original_source[k],'original_control_solver_identity')
    ck(br['status']=='measured' and br['returncode']==0 and br['test_pass_count']==1 and br['environment']==runs[cid]['environment'],'original_control_valid')
    baseline=markers(braw,'METRIC_JSON');candidate=markers(raws[cid],'METRIC_JSON');ck(len(baseline)==len(candidate)==nrecords and baseline==candidate,'complete_original_control_records_exact')
    ck(sum(len(x[field]) for x in candidate)==nsnap and all(x['metrics']=={} for x in candidate),'fixed_snapshot_count_empty_metrics')
    observed=next(x for x in S['suites'] if x['suite']==suite);ck(observed['matched_records']==candidate and observed['snapshot_count_each']==nsnap,'published_snapshot_comparison_exact')
    if suite=='state':
        settings=[(x['board'],x['iso'],x['rake']) for x in candidate];expected=list(itertools.product(['KsQs2d','Qs7h2dKh','AsKsQsJsTs'],[False,True],[0.,.05]));ck(settings==expected,'state_fixture_matrix')
    elif suite=='menu':
        settings=[(x['bets'],x['algorithm']) for x in candidate];expected=list(itertools.product(['','50','33 75','25 50 100','20 40 60 100','10 20 30 40 50 60 70 80 90 100'],['Dcfr','CfrPlus']));ck(settings==expected,'menu_fixture_matrix')
    else:
        settings=[(x['board'],x['storage'],x['iso'],x['warm']) for x in candidate];ck(settings==list(itertools.product(['KsQs2d','KsQs2dJd'],['F32','Compressed'],[False,True],[False,True])),'resume_fixture_matrix')
        for x in candidate:
            ck([q['stage'] for q in x[field]]==['initial','first_sync','materialized','strategy_resync','full_resync','locked_sync','resumed'],'resume_lifecycle_stages')
            start=4 if x['warm'] else 0;ck([q['iteration'] for q in x[field]]==[start+t for t in [0,7,7,7,7,16,21]],'resume_iterations')
    control_rows.append({'suite':suite,'baseline':bid,'candidate':cid,'records':nrecords,'snapshots_each':nsnap,'all_fields_exact':True})
# Complete F32 JSON and convergence trajectories compared to fresh original and historical anchor.
anchor=load(R/'runs/V004-f32-baseline/report.json');anchor_raw=(R/'runs/V004-f32-baseline/stdout.log').read_text();pin(R/'runs/V004-f32-baseline/stdout.log',anchor['stdout_sha256']);f32={};stagecounts={}
for identity,r,raw in [('V004-f32-baseline',anchor,anchor_raw)]+[(i,runs[i],raws[i]) for i in ['V020-f32-original','V020-f32-candidate']]:
    result=markers(raw,'AUTORESEARCH_RESULT');stages=markers(raw,'AUTORESEARCH_STAGE');ck(result==r['results'] and stages==[x['data'] for x in r['stages']],'F32_raw_report_exact')
    ck([x['fixture_id'] for x in result]==['rainbow','two-tone','river'] and [x['iteration'] for x in result]==[200,200,60],'F32_fixed_fixtures_stops')
    for x in result:ck(x['storage']=='f32' and x['target_met'] and x['target_pct']==.3 and x['check_every']==20 and x['max_iterations']==400 and math.isfinite(x['exploit_chips']),'F32_settings_quality')
    f32[identity]=[norm(x,TIMING) for x in result];stagecounts[identity]=len([x for x in stages if x['stage']=='convergence_check'])
    clean=[norm(x,TIMING|{'solve_checks_elapsed_ms'}) for x in stages]
    if identity=='V004-f32-baseline':reference_stages=clean
    else:ck(clean==reference_stages,'F32_all_stage_trajectories_exact')
ck(f32['V004-f32-baseline']==f32['V020-f32-original']==f32['V020-f32-candidate'],'all_F32_nontiming_exact_original')
# Six actual integration test names; these tests include CPU/GPU tolerance checks.
gpu_names=re.findall(r'^test (\S+) \.\.\.',raws['V020-gpu'],re.M)
ck(set(gpu_names)=={'gpu_converges_and_matches_cpu','gpu_locked_always_call_kills_bluffs','gpu_exploitability_matches_cpu','gpu_with_compressed_cpu_storage','gpu_suit_isomorphism_equivalence','gpu_clairvoyance_closed_form'} and len(gpu_names)==6,'six_GPU_tests_executed')
ck(raws['V020-continuation-paging'].count('bitwise paging matches: 160 alternating board/player sweeps;')==1,'paging160_success_marker')
rows=markers(raws['V020-continuation-stored'],'GPU_STORED_PASS');summary=markers(raws['V020-continuation-stored'],'GPU_STORED_SUMMARY')
ck(len(rows)==720 and all(x['passed'] is True for x in rows),'720_stored_passes')
ck({(x['entry'],x['iteration'],x['player']) for x in rows}==set(itertools.product(range(6),range(1,61),range(2))),'stored_complete720_domain')
ck(len(summary)==1 and summary[0]['passes']==720 and all(summary[0][k] is True for k in ['full_device_arrays_bitwise_equal','restored_arrays_bitwise_equal','values_bitwise_equal']),'stored_full_state_summary')
ck(inv['GTO_SSD_STUDY_DIR']==proto['stored_directory'] and pathlib.Path(inv['GTO_SSD_STUDY_DIR']).is_dir(),'stored_unique_bulk_directory')
for name in ['gpu.rs','continuation_paging.rs','continuation_symmetry.rs']:
    path=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')/'crates/solver/tests'/name;pin(path,source['crates/solver/tests/'+name])
pin(pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016/crates/solver/src/gpu/continuation_stored_device_tests.rs'),source['crates/solver/src/gpu/continuation_stored_device_tests.rs'])
chronology=[{'id':i,'started_at':runs[i]['started_at'],'finished_at':runs[i]['finished_at'],'summary':summaries[i]} for i in inv['order']]
v={'id':'E020-broader-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_SCOPED_BROADER_CORRECTNESS','nine_runs_terminal_and_fixed_order':True,'control_snapshots':control_rows,'original_snapshots_each':160,'F32_fixtures':3,'F32_all_nontiming_and_stage_trajectories_exact':True,'F32_convergence_records_each':stagecounts,'GPU_test_names':gpu_names,'continuation':{'selected_tests':3,'paging_sweeps':160,'stored_full_state_passes':720,'stored_domain':'entries0..5 x iterations1..60 x players0..1','stored_summary':summary[0],'invalid_input_test_executed':True},'chronology':chronology,'broader_report_sha256':sha(R/'comparisons/E020-broader-qualification/report.json'),'readiness_sha256':sha(P/'all-builds-ready.json'),'authorization_sha256':sha(P/'authorization.json'),'checks':dict(checks),'assertions':sum(checks.values()),'artifacts':art,'limits':['No performance conclusion from correctness-control timings.','Original compressed/F32/saved-state comparisons cover fixed fixtures, not every possible state.','GPU integration tests include tolerances; continuation arms share candidate kernels and establish integration consistency rather than independent original-kernel equivalence.','Stored test uses unlimitedRAM, not forcedSSD spill.','Separate holdout audit and fresh original cumulative cohort still gate adoption; no accepted/deployed claim.'],'review_actions':{'test_reruns':0,'builds':0,'gpu_jobs':0,'production_edits':0,'dashboard_edits':0}}
with (O/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(v,f,indent=2);f.write('\n')
print(json.dumps({'verdict':v['verdict'],'snapshots_each':160,'F32_fixtures':3,'F32_trajectory_counts':stagecounts,'GPU_tests':6,'continuation_tests':3,'stored_passes':720,'assertions':sum(checks.values()),'artifacts':len(art),'validation_sha256':sha(O/'validation.json')},indent=2))
