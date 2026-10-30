import collections,hashlib,json,math,re,statistics
from datetime import datetime,timezone
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016'); REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016'); OUT=Path(__file__).parent
artifacts={};checks=[]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(value,label):
    if not value:raise AssertionError(label)
    checks.append(label)
def artifact(p,expected=None):
    p=Path(p);actual=sha(p)
    if expected is not None:need(actual.lower()==expected.lower(),'artifact '+str(p))
    artifacts[str(p)]=actual
    return actual
def read(p):artifact(p);return json.loads(Path(p).read_text(encoding='utf-8'))
def write(name,value):
    with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:f.write(value if isinstance(value,str) else json.dumps(value,indent=2)+'\n')
def markers(text,prefix):return [json.loads(line.split(prefix,1)[1]) for line in text.splitlines() if prefix in line]
def stats(v):return {'samples':v,'median':statistics.median(v),'min':min(v),'max':max(v)}
report=read(ROOT/'runs/D033R1/report.json'); logpath=ROOT/'runs/D033R1/stdout.log';artifact(logpath,report['stdout_sha256']);text=logpath.read_text()
records=markers(text,'D033_EVENT_DIAGNOSTIC ');by=collections.defaultdict(list)
for x in records:by[x['stage']].append(x)
protocol=read(ROOT/'runs/D033-graph-event-design/protocol.json');anchor=read(ROOT/'runs/D033-graph-event-design/anchor-rainbow.json');oracle=read(ROOT/'runs/D033-oracle-anchors/anchors.json');rainbow=next(x for x in oracle['fixtures'] if x['fixture_id']=='rainbow')
for name,h in oracle['raw_input_artifact_sha256'].items():artifact(name,h)
for archive in ['runs/D033-implementation','runs/D033-implementation-r2']:
    for name,h in read(ROOT/archive/'checksums.json').items():artifact(ROOT/archive/name,h)
implementation=read(ROOT/'runs/D033-implementation-r2/manifest.json')
for name,h in implementation['failed_build_evidence_sha256'].items():artifact(name,h)
first_exit=read(ROOT/'runs/D033-build/exit.json');second_exit=read(ROOT/'runs/D033-build-r2/exit.json');execution=read(ROOT/'runs/D033-execution/invocation.json');execution_exit=read(ROOT/'runs/D033-execution/exit.json')
for rel in ['runs/D033-build.py','runs/D033-build-r2.py','runs/D033-run.py','runs/D033-execution/stdout.log','runs/D033-execution/stderr.log','comparisons/D033-build-runtime-review/runtime-checklist.json','comparisons/D033-build-runtime-review/build-review.json','comparisons/D033-build-runtime-review/r2-provenance-addendum.json','comparisons/D033-source-review-r2/review.md','comparisons/D033-source-review-r2/manifest.json']:
    artifact(ROOT/rel)
need(first_exit['returncode']==101 and '--no-run' in first_exit['command'],'R1 compile failure preserved with no-run command')
need(second_exit['returncode']==execution_exit['returncode']==report['returncode']==0,'R2 build and native run succeeded')
need(report['id']=='D033R1' and report['kind']=='diagnostic' and report['fixture']=='rainbow' and report['status']=='measured' and report['test_pass_count']==1 and not report['accepted'],'one actual diagnostic test, no acceptance')
need(execution['actual_run']=='D033R1' and execution['logical_dashboard_row']=='D033' and execution['performance_acceptance'] is False,'actual and logical IDs preserved')
need(second_exit['at']<=execution['at']<=report['process_started_at']<=report['finished_at']<=execution_exit['at'],'build completed before native launch and native completion')
manifestpath=Path(report['binary_build_manifest']['path']);artifact(manifestpath,report['binary_build_manifest']['sha256']);manifest=read(manifestpath)
need(manifest==report['binary_build_manifest']['data'],'embedded build manifest exact')
need(execution['build_manifest_sha256']==artifact(manifestpath),'invocation manifest identity exact')
binary=Path(report['command'][0]);artifact(binary,report['binary_sha256']);need(report['binary_sha256']==manifest['binary_sha256']==execution['binary_sha256']=='713eef623cf21b9d702f9dafadab27f7162c8587023c4f8c51e3527a09d10d34','frozen R2 binary identity')
for key,hashkey in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:artifact(manifest[key],manifest[hashkey])
for rel,h in manifest['diagnostic_inputs_sha256'].items():artifact(ROOT/rel,h)
need(execution['diagnostic_inputs_sha256']==manifest['diagnostic_inputs_sha256'],'runtime fixed external inputs exact')
need(manifest['patch_sha256']==implementation['patch_sha256'],'R2 build patch exact')
source_before=read(ROOT/'runs/D033-build-r2/source-before.json')
need(source_before['source_sha256']==manifest['source_sha256']==report['provenance']['source_sha256'],'build and run source identities equal')
current={rel:artifact(REPO/rel,h) for rel,h in manifest['source_sha256'].items()}
need(current==manifest['source_sha256'],'all163 source entries unchanged at post-runtime independent review')
for rel,name in [('crates/solver/src/gpu/mod.rs','mod.rs'),('crates/solver/src/gpu/graph_device_events.rs','graph_device_events.rs')]:artifact(ROOT/'runs/D033-build-r2/source'/name,current[rel])
need(report['environment']['RAYON_NUM_THREADS']=='16' and report['environment']['POSTFLOP_AUTORESEARCH_PROFILE']=='0' and report['environment']['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and report['environment']['POSTFLOP_AUTORESEARCH_FIXTURE']=='rainbow','fixed runtime environment')
need(report['command'][1:]==['gpu::graph_device_events::captured_graph_device_event_diagnostic','--nocapture','--test-threads=1','--ignored'],'exact native diagnostic filter and one test thread')
for snap in ['live_status_before','live_status_at_launch']:
    need(not report[snap]['/api/status']['gpu'] and not report[snap]['/api/preflop/status']['gpu'] and not report[snap]['/api/reports/status']['running'],'recorded live-solve preflight '+snap)
need('test result: ok. 1 passed; 0 failed; 0 ignored;' in text,'native1pass0fail')
need(not any(s in text for s in ['D033_CLEANUP_ERROR','D033_SOLVER_CLEANUP_ERROR','panicked at','D033 invalid diagnostic']),'no error or cleanup failure through native process exit')
need(not (ROOT/'runs/D033-execution/stderr.log').read_text().strip(),'orchestration stderr empty')
expected_stage=['admission']+['warm_check']*6+['raw_exact','warm_check','graph','graph']+['batch','raw_exact','checkpoint_exact']*3+['final_anchor_exact','complete']
need([x['stage'] for x in records]==expected_stage,'all22 markers in registered source/control-flow order')
need([x['iteration'] for x in by['warm_check']]==list(range(20,141,20)),'every warm exploit checkpoint through140')
need([x['iteration'] for x in by['raw_exact']]==[140,160,180,200],'all4 raw-before-evaluation checkpoints')
need([x['iteration'] for x in by['checkpoint_exact']]==[160,180,200],'all3 explicit post-sample compressed checkpoints')
convergence={x['iteration']:x['exploit_bits'] for x in rainbow['convergence_anchors']}
for x in by['warm_check']+by['checkpoint_exact']:need(x['exploit_bits']==convergence[x['iteration']],'exploit anchor '+str(x['iteration']))
full=by['final_anchor_exact'][0]['state_fingerprint'];need(full==anchor['state_fingerprint'],'full final historical state object exact, including all arena/root fields')
need(full['hash']=='65fb2853a11f3acc' and full['iteration']==200 and full['exploit_bits']==4595130701932466176,'final fixed200 fingerprint/exploit')
non_time={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
original_results=[]
for run in ['B038','E015C1']:
    rr=read(ROOT/f'runs/{run}/report.json');pp=ROOT/f'runs/{run}/stdout.log';artifact(pp,rr['stdout_sha256'])
    raw=markers(pp.read_text(),'AUTORESEARCH_RESULT ');need(raw==rr['results'],'historical raw results equal report '+run)
    res=next(x for x in raw if x['fixture_id']=='rainbow');original_results.append({k:v for k,v in res.items() if k not in non_time})
    need(res['state_fingerprint']==full and res['config']==anchor['config'],'full historical anchor/config '+run)
    rawchecks=[x for x in markers(pp.read_text(),'AUTORESEARCH_STAGE ') if x.get('stage')=='convergence_check' and x.get('fixture_id')=='rainbow']
    if rawchecks:need({x['iteration']:x['exploit_bits'] for x in rawchecks}==convergence,'raw original convergence anchors '+run)
need(original_results[0]==original_results[1],'original and accepted E015 entire non-timing rainbow records exact')
raw_lengths={};raw_words=0
for x in by['raw_exact']:
    need(x['pass'] and x['before_exploitability'] and not x['cfv_scratch_compared'],'raw exact before eval '+str(x['iteration']))
    need(x['chunk_floats']==1048576 and x['peak_pairwise_snapshot_bytes']==8388608,'bounded raw comparison '+str(x['iteration']))
    keys=[(v['player'],v['array']) for v in x['arrays']]
    need(keys==[(p,n) for p in [0,1] for n in ['regrets','strategy','reach','weights']],'all8 raw arrays '+str(x['iteration']))
    lengths={(v['player'],v['array']):v['entries'] for v in x['arrays']}
    if raw_lengths:need(lengths==raw_lengths,'raw array lengths stable '+str(x['iteration']))
    raw_lengths=lengths;raw_words+=sum(lengths.values())
    need(len(x['discount_bits'])==3,'three direct checked discount words '+str(x['iteration']))
for p in [0,1]:
    for arena,rawname in [('regrets','regrets'),('strategy_sums','strategy')]:
        n=next(v['entries'] for v in full['arenas'] if v['arena']==arena and v['player']==p)
        need(raw_lengths[p,rawname]==n,'raw and frozen full arena length '+str((p,rawname)))
    need(len({next(v['hash'] for v in x['arrays'] if v['array']=='weights' and v['player']==p) for x in by['raw_exact']})==1,'weights unchanged player'+str(p))
a=by['admission'][0]
need(a['cpu_arena_bytes_per_arm']==1386321040 and a['raw_compare_max_bytes']==8388608,'registered CPU arena and scratch size')
need(a['dual_device_required_with_reserve']==2*a['device_per_arm_payload_bytes']+a['device_reserve_bytes'],'dual device admission formula')
need(a['host_additional_required']==2*a['cpu_arena_bytes_per_arm']+2*a['pinned_bytes_per_arm']+a['raw_compare_max_bytes']+a['host_reserve_bytes'],'dual host admission formula')
need(a['device_free_bytes']>=a['dual_device_required_with_reserve'] and a['host_free_after_spot_and_plan']>=a['host_additional_required'],'admission headroom positive')
graphs={x['topology']['graph']:x['topology'] for x in by['graph']};need(set(graphs)=={0,1},'both ordinary paired graphs')
for gi,g in graphs.items():
    n=g['original_kernel_nodes'];need(n>0 and g['event_nodes']==n+1,'N+1 events graph'+str(gi))
    need(g['original_edges']==[[f'K{i}',f'K{i+1}'] for i in range(n-1)],'original chain graph'+str(gi))
    need(g['added_edges']==[e for i in range(n) for e in [[f'E{i}',f'K{i}'],[f'K{i}',f'E{i+1}']]],'all2N ordered event edges graph'+str(gi))
    need([d['ordinal'] for d in g['kernel_descriptors']]==list(range(n)) and g['kernel_argument_setter_calls']==0,'all ordered original kernel descriptors/no setters graph'+str(gi))
    need(all(d['logical']['block']==[128,1,1] and all(v>0 for v in d['logical']['grid']) for d in g['kernel_descriptors']),'unchanged valid launch descriptors graph'+str(gi))
node_samples=collections.defaultdict(list);family_samples=collections.defaultdict(list);outer=[];envelopes=[];near=0
for bi,b in enumerate(by['batch']):
    checkpoint=[160,180,200][bi];need(b['batch']==bi and b['checkpoint']==checkpoint and b['arm_order']==protocol['batch_arm_order'][bi],'registered batch/order '+str(checkpoint))
    for arm in ['native','instrumented']:
        v=b[arm];need(v['iterations']==20 and v['end_iteration']==checkpoint and v['arm']==arm,'fixed20 iteration arm '+str((checkpoint,arm)))
        need(all(math.isfinite(v[k]) and v[k]>=0 for k in ['device_batch_ms','host_batch_ms']),'finite outer times '+str((checkpoint,arm)))
    ins=b['instrumented'];need(ins['setup_upload_wait_excluded'],'setup excluded '+str(checkpoint))
    need(math.isfinite(ins['final_replay_inter_graph_gap_ms']) and ins['final_replay_inter_graph_gap_ms']>=0,'finite intergraph gap '+str(checkpoint))
    need([g['graph'] for g in ins['final_replay_only']]==[0,1],'both final graph replay samples '+str(checkpoint))
    combined=collections.defaultdict(float);graphrows=[]
    for g in ins['final_replay_only']:
        gi=g['graph'];desc=graphs[gi]['kernel_descriptors'];need(g['iteration']==checkpoint,'last replay iteration '+str((checkpoint,gi)))
        need([n['ordinal'] for n in g['nodes']]==list(range(len(desc))),'all ordered node samples '+str((checkpoint,gi)))
        families=collections.defaultdict(float)
        for v,d in zip(g['nodes'],desc):
            need(v['kernel']==d['logical']['kernel'] and math.isfinite(v['ms']) and v['ms']>=0,'valid node '+str((checkpoint,gi,v['ordinal'])))
            need(v['near_resolution']==(v['ms']<=0.0005),'near-resolution flag '+str((checkpoint,gi,v['ordinal'])))
            near+=v['near_resolution'];families[v['kernel']]+=v['ms'];node_samples[gi,v['ordinal'],v['kernel']].append(v['ms'])
        need(dict(families)==g['family_ms'],'recomputed family sums '+str((checkpoint,gi)))
        need(math.isfinite(g['graph_envelope_ms']) and g['graph_envelope_ms']>=0,'finite graph envelope '+str((checkpoint,gi)))
        for k,v in families.items():combined[k]+=v
        graphrows.append({'graph':gi,'envelope_ms':g['graph_envelope_ms'],'node_sum_ms':sum(v['ms'] for v in g['nodes']),'node_sum_minus_envelope_ms':sum(v['ms'] for v in g['nodes'])-g['graph_envelope_ms']})
    for k,v in combined.items():family_samples[k].append(v)
    outer.append({'iteration':checkpoint,'order':b['arm_order'],'native_device_batch_ms':b['native']['device_batch_ms'],'instrumented_device_batch_ms':ins['device_batch_ms'],'native_host_batch_ms':b['native']['host_batch_ms'],'instrumented_host_batch_ms':ins['host_batch_ms'],'device_ratio':ins['device_batch_ms']/b['native']['device_batch_ms'],'device_increase_pct':100*(ins['device_batch_ms']/b['native']['device_batch_ms']-1),'host_ratio':ins['host_batch_ms']/b['native']['host_batch_ms'],'final_replay_inter_graph_gap_ms':ins['final_replay_inter_graph_gap_ms']})
    envelopes.append({'iteration':checkpoint,'graphs':graphrows,'combined_graph_envelope_ms':sum(v['envelope_ms'] for v in graphrows),'combined_node_sum_ms':sum(combined.values()),'inter_graph_gap_ms':ins['final_replay_inter_graph_gap_ms']})
need(by['complete'][0]['checkpoints']==[140,160,180,200] and by['complete'][0]['node_samples']==[160,180,200] and not by['complete'][0]['accepted_performance_claim'],'complete covers exactly registered checkpoints and no acceptance')
node_rows=[{'graph':k[0],'ordinal':k[1],'kernel':k[2],**stats(v),'descriptor':graphs[k[0]]['kernel_descriptors'][k[1]]['logical']} for k,v in node_samples.items()];node_rows.sort(key=lambda x:x['median'],reverse=True)
family_rows={k:stats(v) for k,v in family_samples.items()}
ratios=stats([x['device_ratio'] for x in outer]);families_sorted=sorted(family_rows,key=lambda f:family_rows[f]['median'],reverse=True)
result={'id':'D033-independent-review','created_at':datetime.now(timezone.utc).isoformat(),'verdict':'PASS_EXACT_PROTOCOL_DIAGNOSTIC; MATERIAL_INSTRUMENTATION_PERTURBATION_LIMITS_NATIVE_HOTSPOT_INFERENCE','performance_accepted':False,'actual_run':'D033R1','source_revision':2,'binary_sha256':report['binary_sha256'],'build_manifest_sha256':report['binary_build_manifest']['sha256'],'checks_passed':len(checks),'checks':checks,'artifact_sha256':artifacts,'source_entries_verified':len(current),'r1_failure_retained':first_exit,'r2_build_exit':second_exit,'chronology':{'r2_built_at':manifest['built_at'],'run_started_at':report['process_started_at'],'run_finished_at':report['finished_at'],'native_test_seconds':37.09,'process_wall_ms':report['process_wall_ms'],'stale_progress_elapsed_process_seconds_not_used':report['elapsed_process_seconds']},'marker_count':len(records),'exactness':{'raw_before_eval_iterations':[140,160,180,200],'raw_arrays_per_checkpoint':8,'raw_f32_words_directly_compared_total':raw_words,'compressed_direct_equality_iterations':[140,160,180,200],'checkpoint140_marker_boundary':'Mandatory frozen compare_cpu after warm_check140 before graph construction; no separate checkpoint_exact140 marker','historical_convergence_anchors_checked':10,'all_non_timing_original_vs_E015_rainbow_records_equal':True,'final_full_state_object_equal':True,'final_fingerprint':full['hash'],'final_exploit_bits':full['exploit_bits'],'final_root_strategy_vector_length':len(full['root_strategy_bits']),'cfv_scratch_compared':False},'admission':{**a,'device_headroom_bytes':a['device_free_bytes']-a['dual_device_required_with_reserve'],'host_headroom_bytes':a['host_free_after_spot_and_plan']-a['host_additional_required']},'graphs':[{ 'graph':k,'kernels':v['original_kernel_nodes'],'events':v['event_nodes'],'original_edges':len(v['original_edges']),'added_edges':len(v['added_edges'])} for k,v in graphs.items()],'outer_batches':outer,'instrumented_native_device_ratio':ratios,'final_replay_envelopes':envelopes,'paired_final_replay_family_ms':family_rows,'family_order_by_median':families_sorted,'node_samples':node_rows,'near_resolution_sample_count':near,'all_node_sample_count':sum(len(x['samples']) for x in node_rows),'limitations':['One fixed rainbow compressed diagnostic with two resident solvers; not a production full-cycle benchmark or generalization proof.','Instrumented20-iteration device envelopes are68.9-72.1percent longer; event-perturbed family/node intervals cannot establish native kernel time shares or predict optimization gains.','Inner intervals are only final replays160/180/200; dividing outer20 envelopes gives a batch average with a different scope, not a correction to last-replay node intervals.','Source-enforced direct raw equality is recorded via pass/hashes/lengths; multi-GB raw images are intentionally not archived.','Recorded pre/post telemetry has no continuous clocks/temperature/utilization series and includes desktop processes; do not attribute timing differences to a specific hardware cause.','Numeric source and run controls pass; high perturbation makes native hotspot attribution limited rather than invalidating the preserved numeric observations.'],'next_step':'No performance candidate is qualified. If further profiling is chosen, prespecify a separate sparse-event protocol around the dominant captured up_action ordinal34/38 (and optionally up_show29 as a comparator), retain native outer controls and exact checkpoints, verify descriptors, and assess reduced perturbation before interpreting normal captured timing. This is a prospective confirmation, not a replacement/rescue of D033 or rejected optimizations.'}
write('parsed-records.json',records);write('validation.json',result)
lines=['# D033 independent runtime review','', '**PASS for exactness and protocol execution; materially perturbed timing diagnostic.** D033R1 ran once from the frozen R2 binary, returned one passing test, and preserved all three samples. R1 remains a documented no-run compile failure (E0425); R2 changes only the versioned getter identifier. Build/input/archive hashes and all163 source identities match, and the build finished before native launch.','',f'All four raw-before-evaluation checkpoints140/160/180/200 passed direct word comparison: {raw_words:,} raw f32 word pairs total across regrets, strategy, reaches and weights, plus discount and iteration checks. Full compressed stores matched at all four checkpoints;140 is enforced in frozen control flow before graph setup. All10 original convergence anchors matched. Both final full state objects equal original B038 and accepted E015C1, including all arena metadata/hashes and root strategy bits; final fingerprint`65fb2853a11f3acc`, exploit bits`4595130701932466176`.','', 'Each original graph contains63 kernel nodes/62 chain edges. Its clone adds64 events and126 boundary edges, keeping every original kernel/argument/order. All378 node samples are finite and retained; none was marked near timer resolution. No invalid, panic or cleanup-error marker appeared through native process exit.','', '| Batch end | Native20 iterations (ms) | Instrumented20 iterations (ms) | Increase |','|---|---:|---:|---:|']
for x in outer:lines.append(f"| {x['iteration']} | {x['native_device_batch_ms']:.3f} | {x['instrumented_device_batch_ms']:.3f} | {x['device_increase_pct']:.2f}% |")
lines += ['',f"Median instrumented/native ratio is{ratios['median']:.4f}x. Native host-wall durations track their device envelopes; this does not remove instrumentation perturbation. The three final-replay combined graph envelopes are{envelopes[0]['combined_graph_envelope_ms']:.3f},{envelopes[1]['combined_graph_envelope_ms']:.3f},{envelopes[2]['combined_graph_envelope_ms']:.3f}ms, with0.000576ms intergraph gaps. These are final-replay samples, not20-iteration means.",'','| Family | Event-perturbed paired-replay median ms | Range ms |','|---|---:|---:|']
for name in families_sorted:
    v=family_rows[name];lines.append(f"| {name} | {v['median']:.3f} | {v['min']:.3f}-{v['max']:.3f} |")
lines += ['', 'The ordering up_action > up_show > down_action repeats across all three instrumented final replays. The heaviest individual action samples are graph1 ordinal38 (grid127302, median1.338ms), graph1 ordinal34 (grid141120,1.313ms), and graph0 ordinal34 (grid141120,1.183ms). This prioritizes where to confirm a hotspot; the69-72% outer slowdown prevents treating these values as native shares or predicted gains.','', 'If another diagnostic is justified, use a new prospective sparse-event design around the selected up_action ordinals with exact descriptor checks, native outer controls and the same numerical protections; optionally retain up_show29 as a comparator. Confirm perturbation is reduced before drawing native-time conclusions. Do not modify this run, resurrect rejected changes, or accept/deploy an optimization from these timings.','', f"Admission reported{a['device_per_arm_payload_bytes']:,} payload bytes per arm and{a['dual_device_required_with_reserve']:,} combined required bytes including reserve, against{a['device_free_bytes']:,} free. Host additional requirement was{a['host_additional_required']:,} against{a['host_free_after_spot_and_plan']:,} available. These are admission observations/reservations, not measured peak usage. Whole native test took37.09s; process wall was{report['process_wall_ms']/1000:.3f}s including startup, checks, hashing and cleanup, not primary benchmark time.",'', 'The adjacent audit script, parsed raw records and validation JSON preserve all source/data hashes, chronology, checks, node medians/ranges, exact anchors, overhead envelopes and limitations. No GPU/build, production edits or dashboard changes were performed by this reviewer.','']
write('summary.md','\n'.join(lines));write('manifest.json',{'id':'D033-independent-review','files':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()},'no_gpu_build_or_source_edits':True})
print(json.dumps({'checks':len(checks),'artifacts':len(artifacts),'validation_sha256':sha(OUT/'validation.json'),'summary_sha256':sha(OUT/'summary.md'),'ratio_median':ratios['median'],'raw_words':raw_words,'verdict':result['verdict']},indent=2))
