"""Assess the one fixed evaluation envelope diagnostic; no timing-based extension or acceptance."""
import collections, hashlib, json, math, re, statistics, struct, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
OUT=ROOT/'comparisons/D057-evaluation-envelope-diagnostic'
artifacts={};checks=[]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(condition,label):
    if not condition:raise AssertionError(label)
    checks.append(label)
def artifact(path,expected=None):
    path=Path(path);actual=sha(path)
    if expected is not None:need(actual==expected,'pin '+str(path))
    artifacts[str(path)]=actual
    return actual
def read(path,expected=None):artifact(path,expected);return json.loads(Path(path).read_text(encoding='utf-8'))
def markers(text,prefix):return [json.loads(line.split(prefix,1)[1]) for line in text.splitlines() if prefix in line]
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:
        f.write(value if isinstance(value,str) else json.dumps(value,indent=2,allow_nan=False)+'\n')
def finite(value):return isinstance(value,(float,int)) and not isinstance(value,bool) and math.isfinite(value) and value>=0
def stats(values):return {'samples':values,'median':statistics.median(values),'min':min(values),'max':max(values)}

def assess():
    need(len(sys.argv)==2,'root authorization SHA argument')
    auth=read(HERE/'authorization.json',sys.argv[1])
    need(auth['candidate']=='D057' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'registered source/script prerequisites')
    seal=read(HERE/'scripts-manifest.json',auth['evidence_sha256'][str(HERE/'scripts-manifest.json')])
    need(seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','prospective seal')
    for path,h in auth['evidence_sha256'].items():artifact(path,h)
    for path,h in seal['script_sha256'].items():artifact(HERE/path,h)
    for path,h in seal['reference_sha256'].items():artifact(path,h)
    protocol=read(HERE/'protocol.json','PENDING_PROTOCOL_SHA256')
    source=read(HERE/'source/source-manifest.json')
    for name,h in source['artifact_sha256'].items():artifact(HERE/'source'/name,h)
    report=read(ROOT/'runs/D057R1/report.json')
    raw_path=ROOT/'runs/D057R1/stdout.log';artifact(raw_path,report['stdout_sha256'])
    raw=raw_path.read_text(encoding='utf-8')
    records=markers(raw,protocol['marker']);write('parsed-records.json',records)
    build_exit=read(ROOT/'runs/D057-build/exit.json')
    execution=read(ROOT/'runs/D057-execution/invocation.json')
    execution_exit=read(ROOT/'runs/D057-execution/exit.json')
    execution_complete=read(ROOT/'runs/D057-execution/complete.json')
    for name in ['stdout.log','stderr.log']:artifact(ROOT/'runs/D057-execution'/name)
    need(build_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'build and native terminal success')
    need(execution_exit['error'] is None and execution_exit['cleanup'] is None,'no interrupted native process')
    need(report['id']=='D057R1' and report['kind']=='diagnostic' and report['fixture']=='two-tone' and report['status']=='measured' and report['test_pass_count']==1 and report['accepted'] is False,'exact one diagnostic and no acceptance')
    need(execution_complete['actual_run']=='D057R1' and execution_complete['native_test_pass'] and execution_complete['performance_acceptance'] is False,'fixed invocation terminal record')
    need(execution['actual_run']=='D057R1' and execution['logical_dashboard_row']=='D057' and execution['performance_acceptance'] is False,'fixed logical/run identity')
    need(execution['authorization_sha256']==sys.argv[1] and execution['protocol_sha256']==sha(HERE/'protocol.json') and execution['script_sha256']==sha(HERE/'run.py'),'execution sealed inputs')
    need(build_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build before run chronology')
    manifest_path=ROOT/'binaries/D057-solver.manifest.json'
    manifest=read(manifest_path,execution['build_manifest_sha256'])
    need(report['binary_build_manifest']['path']==str(manifest_path) and report['binary_build_manifest']['sha256']==sha(manifest_path) and report['binary_build_manifest']['data']==manifest,'runner embedded manifest identity')
    binary=ROOT/'binaries/D057-solver.exe'
    artifact(binary,manifest['binary_sha256'])
    need(manifest['binary_sha256']==execution['binary_sha256']==report['binary_sha256'],'binary build/run identity')
    need(manifest['candidate']=='D057' and manifest['test_only_append_verified'] and manifest['source_matches_prebuild'],'test-only source scope verified')
    need(manifest['primary_protocol_sha256']==sha(HERE/'protocol.json') and manifest['build_script_sha256']==sha(HERE/'build.py') and manifest['probe_authorization_sha256']==sys.argv[1] and manifest['probe_evidence_sha256']==auth['evidence_sha256'],'build sealed inputs')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(HERE/'source/candidate.patch'),'complete archived patch includes new helper')
    before=read(ROOT/'runs/D057-build/source-before.json')
    need(before['source_sha256']==manifest['source_sha256']==execution['source_sha256']==report['provenance']['source_sha256'] and len(before['source_sha256'])==163,'163 build/run source identities exact')
    for name,h in before['source_sha256'].items():artifact(REPO/name,h)
    for value in manifest['source_copies'].values():artifact(value['path'],value['sha256'])
    need(report['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'],'exact ignored diagnostic invocation')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'one executed test and88 filtered')
    need(not any(s in raw for s in ['D057_EVENT_CLEANUP_ERROR','D057_SOLVER_CLEANUP_ERROR','panicked at','D057 invalid diagnostic']),'no native cleanup/panic error')
    need(not (ROOT/'runs/D057-execution/stderr.log').read_text(encoding='utf-8').strip(),'no orchestration stderr error')
    for key,value in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_PROFILE','0'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_FIXTURE','two-tone')]:need(report['environment'][key]==value,'fixed env '+key)
    for snapshot in ['live_status_before','live_status_at_launch']:
        snap=report[snapshot];need(not snap['/api/status']['gpu'] and not snap['/api/preflop/status']['gpu'] and not snap['/api/reports/status']['running'],'live idle '+snapshot)
    need(len(records)==22 and [x['stage'] for x in records]==protocol['expected_stage_order'],'all22 actual markers in fixed order')
    by=collections.defaultdict(list)
    for row in records:by[row['stage']].append(row)
    anchor=read(ROOT/'runs/D057-evaluation-envelope-plan/anchors.json')
    convergence={x['iteration']:x['exploit_bits'] for x in anchor['convergence_anchors']}
    need(list(convergence)==list(range(20,201,20)),'all10 fixed immutable anchors')
    need([x['iteration'] for x in by['warm_check']]==list(range(20,141,20)),'seven normal warm/capture checks')
    need([x['iteration'] for x in by['raw_exact']]==[140,160,180,200],'four post-evaluation raw checks')
    need([x['iteration'] for x in by['checkpoint_exact']]==[140,160,180,200],'four complete compressed-store checks')
    for row in by['warm_check']:
        i=row['iteration'];need(row['exploit_bits']==convergence[i],'warm immutable exploit bits '+str(i))
        need(row['normal_production_method_both_arms'] is True,'ordinary production warm method in both arms')
        need(row['ordinary_eval_warmed'] is True and row['instrumented_eval_warmed'] is True,'both warm flags')
        need(row['ordinary_eval_graph_present'] is (i>=40) and row['instrumented_eval_graph_present'] is (i>=40),'normal eager20 capture40 replay60..140 cadence')
    for row in by['checkpoint_exact']:
        need(row['post_evaluation'] is True and row['raw_and_compressed_pass'] is True,'full stores checked after both complete evaluations')
        need(row['exploit_bits']==convergence[row['iteration']],'post-evaluation anchor '+str(row['iteration']))
    final=by['final_anchor_exact'][0];full=final['state_fingerprint']
    need(full==anchor['final_state_fingerprint'],'entire final arena metadata/hash and root strategy object equals immutable anchor')
    need(final['original_run']=='B038' and final['accepted_run']=='E020C1' and final['historical_anchor_run']=='E015C1','original and accepted anchor provenance')
    for run in ['B038','E015C1','E020C1']:
        rr=read(ROOT/f'runs/{run}/report.json');lp=ROOT/f'runs/{run}/stdout.log';artifact(lp,rr['stdout_sha256']);text=lp.read_text(encoding='utf-8')
        results=markers(text,'AUTORESEARCH_RESULT ');need(results==rr['results'],'historical raw/report '+run)
        result=next(x for x in results if x['fixture_id']=='two-tone')
        need(result['state_fingerprint']==full and result['config']==anchor['config'],'full historical config/state '+run)
        cc=[x for x in markers(text,'AUTORESEARCH_STAGE ') if x.get('stage')=='convergence_check' and x.get('fixture_id')=='two-tone']
        need({x['iteration']:x['exploit_bits'] for x in cc}==convergence,'all10 historical exploit anchors '+run)
        need(result['iteration']==200 and result['target_met'] is True,'registered stopping anchor '+run)
    need(anchor['convergence_anchors'][-2]['exploit_pct_pot']>0.3 and anchor['convergence_anchors'][-1]['exploit_pct_pot']<=0.3,'same target crossing at200')
    a=by['admission'][0]
    need(len(a['device_arena_elements'])==2 and all(isinstance(x,int) and x>0 for x in a['device_arena_elements']),'actual finalized device arena lengths')
    lengths={};raw_words=0;root_words=0
    expected_keys=[(p,n,None) for p in [0,1] for n in ['regrets','strategy','reach','weights']]+[(p,'evaluation_root',m) for p in [0,1] for m in [0,1]]
    for row in by['raw_exact']:
        need(row['pass'] is True and row['before_exploitability'] is False and row['post_evaluation'] is True and row['cfv_scratch_compared'] is False,'matched defined post-evaluation raw scope')
        need(row['chunk_floats']==1048576 and row['peak_pairwise_snapshot_bytes']==8388608,'bounded sequential raw snapshots')
        need([(a['player'],a['array'],a.get('mode')) for a in row['arrays']]==expected_keys,'all8 full raw arrays and4 logical root vectors')
        now={(a['player'],a['array'],a.get('mode')):a['entries'] for a in row['arrays']}
        need(all(isinstance(n,int) and not isinstance(n,bool) and n>0 for n in now.values()),'positive raw counts')
        need(all(isinstance(a['hash'],str) and re.fullmatch('[0-9a-f]{16}',a['hash']) for a in row['arrays']),'raw bit hash records')
        if lengths:need(now==lengths,'stable raw lengths')
        lengths=now;raw_words+=sum(now.values());root_words+=sum(v for k,v in now.items() if k[1]=='evaluation_root')
        need(len(row['discount_bits'])==3 and all(isinstance(v,int) and 0<=v<=0xffffffff for v in row['discount_bits']),'three compared expected discount words')
    for p in [0,1]:
        for rawname in ['regrets','strategy']:need(lengths[p,rawname,None]==a['device_arena_elements'][p],'raw GPU arena length equals finalized compact plan')
        need(lengths[p,'weights',None]==anchor['hands'][p],'full logical root weight length')
        for mode in [0,1]:need(lengths[p,'evaluation_root',mode]==anchor['hands'][p],'defined logical root length excludes padding')
    a=by['admission'][0]
    need(a['diagnostic_only'] is True and a['host_free_before_spot']>=16*1024**3,'initial host admission')
    need(a['cpu_arena_bytes_per_arm']==1391071288 and a['raw_compare_max_bytes']==8388608,'registered two-tone host/scratch sizes')
    need(a['device_reserve_bytes']==2*1024**3 and a['host_reserve_bytes']==8*1024**3,'fixed admission reserves')
    need(a['dual_device_required_with_reserve']==2*a['device_per_arm_payload_bytes']+a['device_reserve_bytes'],'dual device admission formula')
    need(a['host_additional_required']==2*a['cpu_arena_bytes_per_arm']+2*a['pinned_bytes_per_arm']+a['raw_compare_max_bytes']+a['host_reserve_bytes'],'dual host admission formula')
    need(a['device_total_bytes']>=a['device_free_bytes']>=a['dual_device_required_with_reserve'] and a['host_free_after_spot_and_plan']>=a['host_additional_required'],'live memory admission passed')
    g=by['graph_metadata'][0]
    need(g['iteration']==140 and g['own_module_function_mapping'] is True and g['raw_pointer_or_argument_comparison'] is False,'post140 own-module logical descriptor scope')
    need(g['ordinary']==g['instrumented'],'same logical evaluation graph metadata across arms')
    graph=g['ordinary'];kinds=graph['node_kinds'];kernels=graph['kernel_descriptors_sorted']
    need(graph['node_count']==sum(kinds.values()) and graph['node_count']>0,'complete graph node cardinalities')
    need(set(kinds)<=set(['CU_GRAPH_NODE_TYPE_KERNEL','CU_GRAPH_NODE_TYPE_MEMCPY']),'no instrumented event or unexpected graph node kinds')
    need(len(kernels)==kinds['CU_GRAPH_NODE_TYPE_KERNEL'] and len(kernels)>0,'all logical kernel descriptors')
    need(graph['comparison']=='logical multiset only; no raw handles, arguments, memcpy addresses or edges','metadata comparison limitation')
    allowed={'copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','up_action_eval'}
    for d in kernels:
        need(set(d)=={'kernel','grid','block','shared_bytes'} and d['kernel'] in allowed,'logical kernel identity and descriptor shape')
        for key in ['grid','block']:need(len(d[key])==3 and all(isinstance(x,int) and x>0 for x in d[key]),'positive3D launch '+key)
        need(isinstance(d['shared_bytes'],int) and d['shared_bytes']>=0,'nonnegative launch shared bytes')
    outer=[];samples=[];near=0
    for bi,b in enumerate(by['batch']):
        checkpoint=[160,180,200][bi]
        need(b['checkpoint']==checkpoint and b['iterations']==20 and b['arm_order']==protocol['batch_arm_order'][bi],'fixed20-iteration paired batch/order')
        need(b['post_both_arm_completion'] is True and b['event_record_counts']==[bi+1,bi+1],'one interval queried after both evaluations before event reuse')
        need(b['ordinary_exploit_bits']==b['instrumented_exploit_bits']==convergence[checkpoint],'both sampled exploit anchors exact')
        ordinary=b['ordinary_host_batch_ms'];instrumented=b['instrumented_host_batch_ms'];elapsed=b['instrumented_evaluation_device_envelope_ms']
        need(finite(ordinary) and ordinary>0 and finite(instrumented) and instrumented>0 and finite(elapsed),'finite positive host batches and nonnegative event interval')
        pct=100*(instrumented/ordinary-1);absolute=abs(pct)
        need(math.isclose(pct,b['host_batch_change_pct'],rel_tol=1e-12,abs_tol=1e-10) and math.isclose(absolute,b['abs_host_batch_change_pct'],rel_tol=1e-12,abs_tol=1e-10),'recomputed signed/absolute host perturbation')
        need(b['within_10pct'] is (absolute<=10.0),'registered per-batch guard arithmetic')
        need(b['near_resolution'] is (elapsed<=struct.unpack('<f',struct.pack('<f',0.0005))[0]),'event-resolution flag retains small values')
        near+=b['near_resolution'];samples.append(elapsed)
        outer.append({'checkpoint':checkpoint,'order':b['arm_order'],'ordinary_host_batch_ms':ordinary,'instrumented_host_batch_ms':instrumented,'host_change_pct':pct,'abs_host_change_pct':absolute,'within_10pct':absolute<=10.0,'instrumented_evaluation_device_envelope_ms':elapsed,'near_resolution':b['near_resolution']})
    c=by['complete'][0]
    need(c['checkpoints']==[140,160,180,200] and c['sample_iterations']==[160,180,200],'all registered checkpoints completed')
    need(c['event_handles']==2 and c['event_record_counts']==[3,3] and c['evaluation_intervals']==3,'two handles/six records/three fixed intervals')
    need(c['checked_cleanup'] is True and c['accepted_performance_claim'] is False and c['candidate_accepted'] is False,'checked cleanup and no acceptance')
    need(len(outer)==3 and len(samples)==3,'all three fixed samples retained before usefulness assessment')
    useful=all(x['within_10pct'] for x in outer)
    return {'id':'D057','actual_run':'D057R1','status':'pass' if useful else 'inconclusive','diagnostic_only':True,'exactness_pass':True,'usefulness_pass':useful,
        'protocol_sha256':sha(HERE/'protocol.json'),'scope_plan_sha256':protocol['scope_plan_sha256'],'binary_sha256':manifest['binary_sha256'],'native_test_passed':1,'native_test_filtered':88,
        'source_entries_verified':163,'marker_count':len(records),'native_output_streams':'merged stdout/stderr in hashed native stdout.log','raw_f32_words_compared':raw_words,'logical_root_words_compared':root_words,'post_evaluation_checkpoints':[140,160,180,200],
        'final_state_fingerprint':full,'all10_exploit_anchors_exact_both_arms':True,'admission':a,'graph_metadata':g,'outer_batches':outer,
        'evaluation_device_envelope_ms':stats(samples),'evaluation_intervals':3,'event_handles':2,'event_records':6,'near_resolution_count':near,
        'accepted_performance_claim':False,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False,
        'scope':'Three event-perturbed captured raked evaluation-device envelopes at160/180/200 on the fixed two-tone compressed fixture.',
        'interpretation':'All three absolute whole20-iterate/evaluation hostbatch perturbations are <=10%; scoped event-perturbed evaluation interval reporting only.' if useful else 'At least one absolute whole20-iterate/evaluation hostbatch perturbation exceeds10%; inconclusive for low-perturbation interpretation. All fixed samples retained; no extension.',
        'limitations':['The hostbatch guard is not evaluation wall time, pure device work or a bound on individual event interval bias.','The interval includes captured evaluation kernels/root copies and may include scheduling/submission idle; it excludes normal root DTOH and CPU reductions.','No training/evaluation fraction, kernel-family/individual timing, native solve fraction, removable headroom, speedup, acceptance or deployment follows.','Logical graph metadata excludes cross-arm raw handles/argument bytes/memcpy addresses and edges.','Full raw bits and compressed words/scales are compared directly by the frozen native test; multi-GB raw snapshots are not retained.','One fixed fixture and three samples give no workload generalization.']}

OUT.mkdir(exist_ok=False)
try:
    result=assess()
except BaseException as error:
    write('report.json',{'id':'D057','status':'invalid','diagnostic_only':True,'error':repr(error),'checks_passed':checks,'artifact_sha256':artifacts,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False})
    raise
result.update(created_at=datetime.now(timezone.utc).isoformat(),checks_passed=checks,artifact_sha256=artifacts)
write('report.json',result)
write('summary.md','# D057 captured evaluation-envelope diagnostic\n\n'+result['interpretation']+'\n\n'+result['scope']+' All three event intervals and matched host batches remain in report.json. Exact post-evaluation raw/root/full compressed states and immutable anchors passed. No performance candidate is accepted.\n')
write('assessor.py',Path(__file__).read_text(encoding='utf-8'))
write('manifest.json',{'id':'D057-evaluation-envelope-diagnostic','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'diagnostic_only':True,'candidate_accepted':False})
print(json.dumps({'status':result['status'],'report_sha256':sha(OUT/'report.json'),'performance_accepted':False}))
