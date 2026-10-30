"""Assess the one fixed sparse diagnostic; no timing-based extension or acceptance."""
import collections, hashlib, json, math, re, statistics, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
HERE=Path(__file__).resolve().parent
OUT=ROOT/'comparisons/D045-sparse-event-diagnostic'
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
    need(auth['candidate']=='D045' and all(auth[k] is True for k in ['E020_accepted','E020_server_qualification_pass','independent_source_review_pass','independent_script_review_pass']),'registered source/script prerequisites')
    seal=read(HERE/'scripts-manifest.json',auth['evidence_sha256'][str(HERE/'scripts-manifest.json')])
    need(seal['status']=='FROZEN_PROSPECTIVE_NOT_EXECUTED','prospective seal')
    for path,h in auth['evidence_sha256'].items():artifact(path,h)
    for path,h in seal['script_sha256'].items():artifact(HERE/path,h)
    for path,h in seal['reference_sha256'].items():artifact(path,h)
    protocol=read(HERE/'protocol.json','7b5d249b65c4dcaefb13fa6e928b445ede1f0f5228d4931f57f7c2ecdf6ab0b2')
    source=read(HERE/'source/source-manifest.json')
    for name,h in source['artifact_sha256'].items():artifact(HERE/'source'/name,h)
    report=read(ROOT/'runs/D045R1/report.json')
    raw_path=ROOT/'runs/D045R1/stdout.log';artifact(raw_path,report['stdout_sha256'])
    raw=raw_path.read_text(encoding='utf-8')
    records=markers(raw,protocol['marker']);write('parsed-records.json',records)
    build_exit=read(ROOT/'runs/D045-build/exit.json')
    execution=read(ROOT/'runs/D045-execution/invocation.json')
    execution_exit=read(ROOT/'runs/D045-execution/exit.json')
    execution_complete=read(ROOT/'runs/D045-execution/complete.json')
    for name in ['stdout.log','stderr.log']:artifact(ROOT/'runs/D045-execution'/name)
    need(build_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'build and native terminal success')
    need(execution_exit['error'] is None and execution_exit['cleanup'] is None,'no interrupted native process')
    need(report['id']=='D045R1' and report['kind']=='diagnostic' and report['fixture']=='rainbow' and report['status']=='measured' and report['test_pass_count']==1 and report['accepted'] is False,'exact one diagnostic and no acceptance')
    need(execution_complete['actual_run']=='D045R1' and execution_complete['native_test_pass'] and execution_complete['performance_acceptance'] is False,'fixed invocation terminal record')
    need(execution['actual_run']=='D045R1' and execution['logical_dashboard_row']=='D045' and execution['performance_acceptance'] is False,'fixed logical/run identity')
    need(execution['authorization_sha256']==sys.argv[1] and execution['protocol_sha256']==sha(HERE/'protocol.json') and execution['script_sha256']==sha(HERE/'run.py'),'execution sealed inputs')
    need(build_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build before run chronology')
    manifest_path=ROOT/'binaries/D045-solver.manifest.json'
    manifest=read(manifest_path,execution['build_manifest_sha256'])
    need(report['binary_build_manifest']['path']==str(manifest_path) and report['binary_build_manifest']['sha256']==sha(manifest_path) and report['binary_build_manifest']['data']==manifest,'runner embedded manifest identity')
    binary=ROOT/'binaries/D045-solver.exe'
    artifact(binary,manifest['binary_sha256'])
    need(manifest['binary_sha256']==execution['binary_sha256']==report['binary_sha256'],'binary build/run identity')
    need(manifest['candidate']=='D045' and manifest['test_only_append_verified'] and manifest['source_matches_prebuild'],'test-only source scope verified')
    need(manifest['primary_protocol_sha256']==sha(HERE/'protocol.json') and manifest['build_script_sha256']==sha(HERE/'build.py') and manifest['probe_authorization_sha256']==sys.argv[1] and manifest['probe_evidence_sha256']==auth['evidence_sha256'],'build sealed inputs')
    for key,hkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hkey])
    need(manifest['patch_sha256']==sha(HERE/'source/candidate.patch'),'complete archived patch includes new helper')
    before=read(ROOT/'runs/D045-build/source-before.json')
    need(before['source_sha256']==manifest['source_sha256']==execution['source_sha256']==report['provenance']['source_sha256'] and len(before['source_sha256'])==163,'163 build/run source identities exact')
    for name,h in before['source_sha256'].items():artifact(REPO/name,h)
    for value in manifest['source_copies'].values():artifact(value['path'],value['sha256'])
    need(report['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored'],'exact ignored diagnostic invocation')
    need(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw)==[('1','0','0','0','88')],'one executed test and88 filtered')
    need(not any(s in raw for s in ['D045_CLEANUP_ERROR','D045_SOLVER_CLEANUP_ERROR','panicked at','D045 invalid diagnostic']),'no native cleanup/panic error')
    need(not (ROOT/'runs/D045-execution/stderr.log').read_text(encoding='utf-8').strip(),'no orchestration stderr error')
    for key,value in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_PROFILE','0'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_FIXTURE','rainbow')]:need(report['environment'][key]==value,'fixed env '+key)
    for snapshot in ['live_status_before','live_status_at_launch']:
        snap=report[snapshot];need(not snap['/api/status']['gpu'] and not snap['/api/preflop/status']['gpu'] and not snap['/api/reports/status']['running'],'live idle '+snapshot)
    need(len(records)==22 and [x['stage'] for x in records]==protocol['expected_stage_order'],'all22 markers in fixed order')
    by=collections.defaultdict(list)
    for row in records:by[row['stage']].append(row)
    anchor=read(ROOT/'runs/D033-graph-event-design/anchor-rainbow.json')
    oracle=read(ROOT/'runs/D033-oracle-anchors/anchors.json')
    rainbow=next(x for x in oracle['fixtures'] if x['fixture_id']=='rainbow')
    convergence={x['iteration']:x['exploit_bits'] for x in rainbow['convergence_anchors']}
    need([x['iteration'] for x in by['warm_check']]==list(range(20,141,20)),'all7 warm checkpoints')
    need([x['iteration'] for x in by['raw_exact']]==[140,160,180,200],'all4 raw-before-eval checkpoints')
    need([x['iteration'] for x in by['checkpoint_exact']]==[160,180,200],'all3 sampled full-store checkpoints')
    for row in by['warm_check']+by['checkpoint_exact']:need(row['exploit_bits']==convergence[row['iteration']],'exploit anchor '+str(row['iteration']))
    need(all(x['raw_and_compressed_pass'] is True for x in by['checkpoint_exact']),'full compressed equality after samples')
    final=by['final_anchor_exact'][0];full=final['state_fingerprint']
    need(full==anchor['state_fingerprint'],'complete final arena/root state equals frozen anchor')
    need(final['original_run']=='B038' and final['accepted_run']=='E020C1' and final['historical_anchor_run']=='E015C1','original and accepted anchor provenance')
    for run in ['B038','E015C1','E020C1']:
        rr=read(ROOT/f'runs/{run}/report.json');lp=ROOT/f'runs/{run}/stdout.log';artifact(lp,rr['stdout_sha256']);text=lp.read_text(encoding='utf-8')
        results=markers(text,'AUTORESEARCH_RESULT ');need(results==rr['results'],'historical raw/report '+run)
        result=next(x for x in results if x['fixture_id']=='rainbow')
        need(result['state_fingerprint']==full and result['config']==anchor['config'],'full historical config/state '+run)
        cc=[x for x in markers(text,'AUTORESEARCH_STAGE ') if x.get('stage')=='convergence_check' and x.get('fixture_id')=='rainbow']
        need({x['iteration']:x['exploit_bits'] for x in cc}==convergence,'all10 historical exploit anchors '+run)
    lengths={};raw_words=0
    for row in by['raw_exact']:
        need(row['pass'] is True and row['before_exploitability'] is True and row['cfv_scratch_compared'] is False,'raw comparison scope '+str(row['iteration']))
        need(row['chunk_floats']==1048576 and row['peak_pairwise_snapshot_bytes']==8388608,'bounded sequential raw snapshots')
        need([(a['player'],a['array']) for a in row['arrays']]==[(p,n) for p in [0,1] for n in ['regrets','strategy','reach','weights']],'all8 raw arrays')
        now={(a['player'],a['array']):a['entries'] for a in row['arrays']}
        need(all(isinstance(n,int) and n>0 for n in now.values()),'positive raw counts')
        if lengths:need(now==lengths,'stable raw lengths')
        lengths=now;raw_words+=sum(now.values())
        need(len(row['discount_bits'])==3,'three compared discount words')
    for p in [0,1]:
        for arena,rawname in [('regrets','regrets'),('strategy_sums','strategy')]:need(lengths[p,rawname]==next(a['entries'] for a in full['arenas'] if a['player']==p and a['arena']==arena),'raw/store full arena length')
    a=by['admission'][0]
    need(a['cpu_arena_bytes_per_arm']==1386321040 and a['raw_compare_max_bytes']==8388608,'registered host state and scratch sizes')
    need(a['dual_device_required_with_reserve']==2*a['device_per_arm_payload_bytes']+a['device_reserve_bytes'],'dual device admission formula')
    need(a['host_additional_required']==2*a['cpu_arena_bytes_per_arm']+2*a['pinned_bytes_per_arm']+a['raw_compare_max_bytes']+a['host_reserve_bytes'],'dual host admission formula')
    need(a['device_free_bytes']>=a['dual_device_required_with_reserve'] and a['host_free_after_spot_and_plan']>=a['host_additional_required'],'live memory admission passed')
    graphs={row['topology']['graph']:row['topology'] for row in by['graph']}
    need(set(graphs)=={0,1},'both captured graph topologies')
    selectors=protocol['selector_rule']['resolved_selectors'];boundaries=[19,20,29,30,34,35]
    for gi,g in graphs.items():
        need((g['original_kernel_nodes'],g['event_nodes'],g['total_nodes'],g['total_edges'])==(63,6,69,74),'fixed sparse node/edge counts')
        need(g['event_boundaries']==boundaries and g['selected_ordinals']==[19,29,34],'fixed sparse selection')
        need(g['original_edges']==[[f'K{i}',f'K{i+1}'] for i in range(62)],'all62 original edges retained')
        need(g['added_edges']==[e for b in boundaries for e in [[f'K{b-1}',f'E{b}'],[f'E{b}',f'K{b}']]],'exact12 added ordered edges')
        need([d['ordinal'] for d in g['kernel_descriptors']]==list(range(63)) and g['kernel_argument_setter_calls']==0,'all63 original descriptors and no setters')
        for s in [x for x in selectors if x['graph']==gi]:
            d=g['kernel_descriptors'][s['ordinal']]['logical'];need(d=={k:s[k] for k in ['kernel','grid','block','shared_bytes']},'selected exact descriptor '+str((gi,s['ordinal'])))
            candidates=[x for x in g['kernel_descriptors'] if x['logical']['kernel']==s['kernel']]
            chosen=min(candidates,key=lambda x:(-math.prod(x['logical']['grid']),x['ordinal']))
            need(chosen['ordinal']==s['ordinal'],'largest-grid earliest-ordinal selector')
    samples=collections.defaultdict(list);outer=[];near=0
    for bi,b in enumerate(by['batch']):
        checkpoint=[160,180,200][bi]
        need(b['batch']==bi and b['checkpoint']==checkpoint and b['arm_order']==protocol['batch_arm_order'][bi],'fixed batch/order '+str(checkpoint))
        for arm in ['native','instrumented']:
            v=b[arm];need(v['iterations']==20 and v['end_iteration']==checkpoint and v['arm']==arm,'20 iterations per arm')
            need(all(finite(v[k]) for k in ['device_batch_ms','host_batch_ms']) and v['device_batch_ms']>0,'finite positive device envelopes')
        ins=b['instrumented'];need(ins['setup_upload_wait_excluded'] is True,'setup upload excluded')
        need('final_replay_inter_graph_gap_ms' not in ins,'no unmeasured intergraph gap')
        need([g['graph'] for g in ins['final_replay_only']]==[0,1],'both final replay samples')
        for g in ins['final_replay_only']:
            gi=g['graph'];need(g['iteration']==checkpoint and [n['ordinal'] for n in g['nodes']]==[19,29,34],'exact3 final-replay selections')
            need('family_ms' not in g and 'graph_envelope_ms' not in g,'no family sums or full graph envelope')
            for n in g['nodes']:
                d=graphs[gi]['kernel_descriptors'][n['ordinal']]['logical']
                need(n['logical']==d and n['kernel']==d['kernel'] and n['start_boundary']==n['ordinal'] and n['end_boundary']==n['ordinal']+1,'selected sample exact descriptor/boundaries')
                need(finite(n['ms']) and n['near_resolution']==(n['ms']<=0.0005),'finite interval and timer-resolution flag')
                near+=n['near_resolution'];samples[gi,n['ordinal'],n['kernel']].append(n['ms'])
        native=b['native']['device_batch_ms'];instrumented=ins['device_batch_ms'];pct=100*(instrumented/native-1)
        outer.append({'checkpoint':checkpoint,'order':b['arm_order'],'native_device_batch_ms':native,'instrumented_device_batch_ms':instrumented,'native_host_batch_ms':b['native']['host_batch_ms'],'instrumented_host_batch_ms':ins['host_batch_ms'],'device_change_pct':pct,'abs_device_change_pct':abs(pct),'within_10pct':abs(pct)<=10.0})
    c=by['complete'][0]
    need(c['checkpoints']==[140,160,180,200] and c['node_samples']==[160,180,200] and c['selected_intervals_per_graph_per_checkpoint']==3 and c['total_selected_intervals']==18 and c['accepted_performance_claim'] is False,'checked cleanup then fixed complete marker')
    need(len(samples)==6 and all(len(v)==3 for v in samples.values()),'all18 selected intervals retained')
    useful=all(x['within_10pct'] for x in outer)
    return {'id':'D045','actual_run':'D045R1','status':'pass' if useful else 'inconclusive','diagnostic_only':True,'exactness_pass':True,'usefulness_pass':useful,
        'protocol_sha256':sha(HERE/'protocol.json'),'binary_sha256':manifest['binary_sha256'],'native_test_passed':1,'native_test_filtered':88,
        'source_entries_verified':163,'marker_count':len(records),'raw_f32_words_compared':raw_words,'compressed_checkpoints':[140,160,180,200],
        'checkpoint140_evidence':'Frozen source compares every compressed q/scale after warm_check140 and before graph setup; no separate marker.',
        'final_state_fingerprint':full,'all10_exploit_anchors_exact':True,'admission':a,'graphs':list(graphs.values()),'outer_batches':outer,
        'selected_launch_samples':[{'graph':k[0],'ordinal':k[1],'kernel':k[2],'descriptor':graphs[k[0]]['kernel_descriptors'][k[1]]['logical'],**stats(v)} for k,v in sorted(samples.items())],
        'selected_interval_count':18,'near_resolution_count':near,'accepted_performance_claim':False,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False,
        'scope':'Six selected captured training launches at final replays160/180/200. Event-perturbed intervals only; not complete-solve or whole-family cost.',
        'interpretation':'All three absolute outer20-iteration perturbations are <=10%; scoped selected-launch prioritization only.' if useful else 'At least one absolute outer20-iteration perturbation exceeds10%; inconclusive for native-like selected-launch prioritization. All samples retained; no extension.',
        'limitations':['The outer10% usefulness guard does not bound individual interval bias or prove uninstrumented native timing.','Final replay intervals are not20-iteration means and omit every unselected kernel, exploitability evaluation, initialization/readback and host work.','No family sums, native time shares, intergraph gap, graph envelope, causal speedup, acceptance or deployment follow.','One fixed rainbow compressed paired-state diagnostic; no broad workload generalization.','Raw arrays are compared directly in bounded chunks by the frozen native test; multi-GB raw snapshots are not retained.']}

OUT.mkdir(exist_ok=False)
try:
    result=assess()
except BaseException as error:
    write('report.json',{'id':'D045','status':'invalid','diagnostic_only':True,'error':repr(error),'checks_passed':checks,'artifact_sha256':artifacts,'candidate_accepted':False,'deployment_changed':False,'extension_allowed':False})
    raise
result.update(created_at=datetime.now(timezone.utc).isoformat(),checks_passed=checks,artifact_sha256=artifacts)
write('report.json',result)
write('summary.md','# D045 sparse selected-kernel diagnostic\n\n'+result['interpretation']+'\n\n'+result['scope']+' All18 selected intervals and all three outer batches are preserved in report.json. Exact raw/full compressed states and immutable anchors passed. No performance candidate is accepted.\n')
write('assessor.py',Path(__file__).read_text(encoding='utf-8'))
write('manifest.json',{'id':'D045-sparse-event-diagnostic','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'diagnostic_only':True,'candidate_accepted':False})
print(json.dumps({'status':result['status'],'outer_abs_perturbation_pct':[x['abs_device_change_pct'] for x in result['outer_batches']],'selected_intervals':18,'report_sha256':sha(OUT/'report.json'),'performance_accepted':False}))
