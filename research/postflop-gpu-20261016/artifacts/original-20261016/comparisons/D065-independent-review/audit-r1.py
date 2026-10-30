"""Post-terminal file-only D065 audit. Never imports or executes diagnostic scripts."""
from pathlib import Path
import json,hashlib,statistics,math,re,subprocess,datetime
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');P=R/'runs/D065-readback-diagnostic';O=Path(__file__).parent;REPO=Path(r'X:\Dev\GTOpen-gpu-research-20261016')
pins={};checks=[]
def ck(v,label):
 if not v:raise AssertionError(label)
 checks.append(label)
def sha(p):
 p=Path(p);h=hashlib.sha256(p.read_bytes()).hexdigest();pins[str(p)]=h;return h
def read(p):sha(p);return json.loads(Path(p).read_text(encoding='utf8'))
def pinmap(m,base=P):
 for p,h in m.items():ck(sha(Path(p) if Path(p).is_absolute() else base/p)==h,'pin:'+p)
def same(a,b,label):ck(math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-8),label)
def finite(x):return type(x) in [int,float] and math.isfinite(x) and x>=0
seal=read(P/'scripts-manifest.json');plan=read(P/'protocol.json');schema=read(P/'source/schema.json');source=read(P/'source/source-manifest.json')
ck(sha(P/'scripts-manifest.json')=='a8e1cba0df3ecad7dd8d29bb1eef8d1ef13114cdb1a83059729e018363b256af','frozen script seal')
ck(sha(P/'source/source-manifest.json')=='742d75d2acd0ad495e35b3a5feb7507bd441518297390cd9bb01f9d91c31efd8','frozen source seal')
for key in ['script_sha256','supporting_sha256','reference_sha256']:pinmap(seal[key])
pinmap(source['artifact_sha256'],P/'source')
auth=read(P/'authorization.json');pinmap(auth['evidence_sha256'])
for v in auth['prerequisites'].values():ck(sha(v['path'])==v['sha256'],'root prerequisite')
ck(auth['candidate']=='D065' and auth['independent_source_review_pass'] and auth['independent_script_review_pass'],'root reviewed authorization')
base=read(R/'binaries/E020-postflop_autoresearch.manifest.json');candidate=read(R/'binaries/D065-postflop_autoresearch.manifest.json');expected=base['source_sha256']|plan['candidate_owned_sha256']
act=read(R/'runs/D065-source/activation.json');ck(act['source_before']['source_sha256']==base['source_sha256'] and act['source_after']['source_sha256']==expected,'exact sole-file activation')
ck(act['authorization_sha256']==sha(P/'authorization.json')==candidate['probe_authorization_sha256'],'activation/build authorization binding')
ck(candidate['source_sha256']==expected and len(expected)==162,'complete candidate build map')
ck(read(R/'runs/D065-build/source-before.json')['source_sha256']==expected,'prebuild source custody')
ck(sha(R/'runs/D065-build/candidate-mod.rs')==source['candidate_source_sha256'],'build source copy')
ck(sha(R/'runs/D065-build/candidate.patch')==source['artifact_sha256']['candidate.patch'],'build exact patch')
env=read(R/'runs/D065-build/build-environment.json');ck(env['target_previously_absent'] and env['compiler_override_absence']=={},'fresh target / compiler environment')
exit=read(R/'runs/D065-build/exit.json');ck(exit['returncode']==0 and '--no-run' in exit['command'] and '--locked' in exit['command'] and '--offline' in exit['command'],'single compile-only terminal success')
rows=[json.loads(x) for x in (R/'runs/D065-build/build.jsonl').read_text().splitlines() if x.strip()]
ck(rows[-1]=={'reason':'build-finished','success':True},'Cargo terminal success')
ck(not any(x.get('reason')=='compiler-message' and x.get('message',{}).get('level')=='error' for x in rows),'no compiler error')
for a in [candidate['cargo_artifact'],candidate['solver_artifact']]:
 ck(a['features']==['gpu'] and a['fresh'] is False,'fresh GPU-only artifact')
 ck(all(Path(x).is_relative_to(Path(candidate['target_dir'])) for x in a['filenames']),'artifact target containment')
for key,pathkey in [('build_log_sha256','build_log'),('build_stderr_sha256','build_stderr_log')]:ck(sha(candidate[pathkey])==candidate[key],'build raw pin')
ck(candidate['primary_protocol_sha256']==sha(P/'protocol.json') and candidate['build_script_sha256']==sha(P/'build.py'),'build/script protocol binding')
cp=R/'binaries/D065-postflop_autoresearch.exe';bp=R/'binaries/E020-postflop_autoresearch.exe';ck(sha(cp)==candidate['binary_sha256']==sha(candidate['cargo_artifact']['executable']),'frozen binary matches compiled artifact');ck(sha(bp)==base['binary_sha256'],'immutable reference binary')
ck((P/'source/base/mod.rs').read_bytes()==(R/'runs/D065-source/accepted-mod.rs').read_bytes(),'accepted source archive')
cuda=REPO/'crates/solver/src/gpu/kernels.cu';ck(cuda.read_bytes() in cp.read_bytes() and b'LIFECYCLE_PROFILE' in cp.read_bytes(),'embedded unchanged CUDA and diagnostic marker')
EX=R/'runs/D065-execution';inv=read(EX/'invocation.json');done=read(EX/'complete.json');C=read(R/'comparisons/D065-readback-diagnostic/report.json')
order=['D065B1','D065P1','D065P2','D065B2','D065B3','D065P3'];ck(plan['order']==inv['order']==done['order']==order,'fixed order completed')
ck(sorted(x.name for x in EX.glob('*.invocation.json'))==sorted(x+'.invocation.json' for x in order),'only six native invocations')
ck(inv['primary_protocol_sha256']==sha(P/'protocol.json') and inv['script_sha256']==sha(P/'cohort.py'),'cohort invocation pin')
exclude={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'};norm=lambda x,ks:{k:v for k,v in x.items() if k not in ks}
runs={};allrecords=[];reference=None;reference_stages=None;check_count=0
for identity in order:
 d=R/'runs'/identity;r=read(d/'report.json');text=(d/'stdout.log').read_text();ck(sha(d/'stdout.log')==r['stdout_sha256'],'raw log pin '+identity)
 profiled='P' in identity;bm=candidate if profiled else base;binary=cp if profiled else bp
 ck(r['id']==identity and r['kind']=='diagnostic' and r['status']=='measured' and r['returncode']==0 and r['test_pass_count']==1,'terminal diagnostic '+identity)
 ck(r['command']==[str(binary),'postflop_complete_cycle','--nocapture','--test-threads=1','--ignored'],'frozen native command '+identity)
 ck(r['binary_sha256']==bm['binary_sha256'] and r['binary_build_manifest']['data']==bm and r['binary_build_manifest']['sha256']==sha(R/'binaries'/('D065-postflop_autoresearch.manifest.json' if profiled else 'E020-postflop_autoresearch.manifest.json')),'runtime build identity '+identity)
 ck(r['provenance']['source_sha256']==expected,'current-source versus binary-source distinction '+identity)
 si=read(EX/(identity+'.invocation.json'));sx=read(EX/(identity+'.exit.json'));ck(sx['returncode']==0 and sx['error'] is None,'wrapper terminal '+identity)
 ck(si['environment_overrides']=={'POSTFLOP_AUTORESEARCH_LIFECYCLE_PROFILE':'1' if profiled else '0'},'explicit child flag '+identity)
 for k,v in {'RAYON_NUM_THREADS':'16','POSTFLOP_AUTORESEARCH_PROFILE':'0','POSTFLOP_AUTORESEARCH_STORAGE':'compressed','POSTFLOP_AUTORESEARCH_FIXTURE':None}.items():ck(r['environment'][k]==v,'unchanged workload environment')
 ck(si['at']<=r['started_at']<=r['finished_at']<=sx['at'],'child chronology '+identity)
 ck(re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',text)==[('1','0','0','0','0')],'native full summary '+identity)
 ck('panicked at' not in text and 'test result: FAILED' not in text,'no hidden test failure '+identity)
 stages=[];results=[];records=[];events=[]
 for line in text.splitlines():
  if 'AUTORESEARCH_STAGE ' in line:
   x=json.loads(line.split('AUTORESEARCH_STAGE ',1)[1]);stages.append(x);events.append(('stage',x))
  if 'AUTORESEARCH_RESULT ' in line:results.append(json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]))
  if 'LIFECYCLE_PROFILE ' in line:
   x=json.loads(line.split('LIFECYCLE_PROFILE ',1)[1]);events.append(('profile',x))
 ck(stages==[x['data'] for x in r['stages']] and results==r['results'],'all raw/report JSON exact '+identity)
 ck([x['fixture_id'] for x in results]==plan['expected_fixtures'] and [x['iteration'] for x in results]==[200,200,60],'fixed fixtures and stops '+identity)
 ck(stages[0]['stage']=='suite_start' and stages[0]['primary_suite'] and not stages[0]['smoke_only'] and not stages[0]['profile_after_timing'] and stages[-1]['stage']=='suite_complete' and stages[-1]['fixtures_completed']==3,'complete ordinary suite '+identity)
 normalized=[norm(x,exclude) for x in results];ns=[norm(x,exclude|{'solve_checks_elapsed_ms'}) for x in stages]
 if reference is None:reference=normalized;reference_stages=ns
 ck(normalized==reference and ns==reference_stages,'complete normalized results and trajectory exact '+identity)
 checks_here=[x for x in stages if x['stage']=='convergence_check'];ck(len(checks_here)==23,'23 checkpoints '+identity);check_count+=len(checks_here)
 for row in results:
  ck(row['target_met'] and row['target_pct']==.3 and row['check_every']==20 and row['max_iterations']==400 and row['storage']=='compressed','frozen quality')
  ck(row['runtime_nvrtc_jit_included'] and row['flushed_progress_logging_included'],'complete-cycle boundaries')
  ck(all(finite(row[k]) for k in exclude),'finite cycle spans')
  same(sum(row[k] for k in ['build_ms','init_ms','solve_ms','readback_ms']),row['full_cycle_ms'],'full cycle component sum')
  fixture=row['fixture_id'];fs=next(i for i,(kind,x) in enumerate(events) if kind=='stage' and x.get('fixture_id')==fixture and x['stage']=='fixture_start');fe=next(i for i,(kind,x) in enumerate(events) if kind=='stage' and x.get('fixture_id')==fixture and x['stage']=='timing_complete');seg=events[fs:fe+1]
  local=[(i,x) for i,(kind,x) in enumerate(seg) if kind=='profile'];ck(len(local)==(1 if profiled else 0),'one trace per instrumented fixture')
  if not profiled:continue
  i,x=local[0];last=max(j for j,(kind,v) in enumerate(seg) if kind=='stage' and v['stage']=='convergence_check');ck(last<i<len(seg)-1,'trace after final convergence before timing completion')
  ck(seg[last][1]['iteration']==row['iteration'],'trace after actual final check')
  ck(set(x)==set(schema['fixed_fields'])|set(schema['fields']),'trace field set')
  for k,v in schema['fixed_fields'].items():ck(type(x[k]) is type(v) and x[k]==v,'trace fixed field '+k)
  ck(x['note']==plan['expected_trace_note'] and isinstance(x['thread'],str) and bool(x['thread']),'trace explanation and identity')
  ck(len(x['spans'])==14 and finite(x['wall_ms_before_logging']),'complete trace14')
  for span,want in zip(x['spans'],schema['ordered_spans']):
   ck(set(span)=={'stage','player','arena','bytes','wall_ms'} and finite(span['wall_ms']),'span fields and elapsed')
   for k in ['stage','player','arena']:ck(type(span[k]) is type(want[k]) and span[k]==want[k],'ordered span identity')
   expect=None if want['player'] is None else plan['expected_device_arena_bytes'][fixture][want['player']]
   ck(type(span['bytes']) is type(expect) and span['bytes']==expect,'actual device extent')
  ck(sum(y['wall_ms'] for y in x['spans'])<=x['wall_ms_before_logging']+1e-6<=row['readback_ms']+2e-6,'trace/outer nesting')
  record={'run_id':identity,'fixture_id':fixture,**x};records.append(record);allrecords.append(record)
 ck(len([x for k,x in events if k=='profile'])==(3 if profiled else 0),'no extra or misplaced profiles')
 runs[identity]={'report':r,'results':results,'records':records}
for a,b in zip(order,order[1:]):ck(runs[a]['report']['finished_at']<=runs[b]['report']['started_at'],'serialized fixed cohort')
ck(check_count==138 and len(allrecords)==9 and allrecords==C['raw_profiles'],'all138 checks and9 retained profiles')
# Recompute every published component from raw spans, grouping within each run first.
grouped={};baseline_total=profiled_total=0;fixture_stats=[]
for index,fixture in enumerate(plan['expected_fixtures']):
 bs=[runs[p['baseline']]['results'][index]['full_cycle_ms'] for p in plan['pairs']];ps=[runs[p['candidate']]['results'][index]['full_cycle_ms'] for p in plan['pairs']]
 b=statistics.median(bs);p=statistics.median(ps);baseline_total+=b;profiled_total+=p;published=C['fixtures'][index]
 ck(published['ordinary_full_cycles_ms']==bs and published['instrumented_full_cycles_ms']==ps,'all sample times retained')
 same(published['ordinary_median_ms'],b,'ordinary median');same(published['instrumented_median_ms'],p,'instrumented median')
 for actual,bb,pp in zip(published['paired_change_pct'],bs,ps):same(actual,100*(pp/bb-1),'pair perturbation')
 records=[runs[z['candidate']]['records'][index] for z in plan['pairs']]
 values={stage:[sum(s['wall_ms'] for s in rec['spans'] if s['stage']==stage) for rec in records] for stage in plan['stage_names']}
 values['transfer_host_ms']=[a+b for a,b in zip(values['dtoh_host_call'],values['dtoh_stream_wait'])];values['cpu_encode_scatter_restore_ms']=values['encode_scatter_restore_cpu'][:]
 values['optimistic_overlap_ceiling_ms']=[min(t,e) for t,e in zip(values['transfer_host_ms'],values['cpu_encode_scatter_restore_ms'])]
 values['measured_span_sum_ms']=[sum(x['wall_ms'] for x in rec['spans']) for rec in records];values['full_readback_before_logging_ms']=[rec['wall_ms_before_logging'] for rec in records]
 values['trace_timer_bookkeeping_residual_ms']=[a-b for a,b in zip(values['full_readback_before_logging_ms'],values['measured_span_sum_ms'])]
 values['outer_readback_minus_trace_ms']=[runs[z['candidate']]['results'][index]['readback_ms']-rec['wall_ms_before_logging'] for z,rec in zip(plan['pairs'],records)]
 ck(set(values)=={x['stage'] for x in published['components']},'component inventory')
 for name,raw in values.items():
  x=next(x for x in published['components'] if x['stage']==name);ck(x['all_profiled_ms']==raw and x['range_ms']==[min(raw),max(raw)],'raw component and range');median=statistics.median(raw);same(x['median_ms'],median,'component median');grouped[name]=grouped.get(name,0)+median
 for n,span in enumerate(published['ordered_spans']):
  raw=[z['spans'][n]['wall_ms'] for z in records];ck(span['all_profiled_ms']==raw and span['range_ms']==[min(raw),max(raw)],'ordered component raw');same(span['median_ms'],statistics.median(raw),'ordered component median')
 fixture_stats.append({'fixture_id':fixture,'ordinary_ms':bs,'instrumented_ms':ps,'paired_change_pct':[100*(pp/bb-1) for bb,pp in zip(bs,ps)]})
change=100*(profiled_total/baseline_total-1);ceiling=100*grouped['optimistic_overlap_ceiling_ms']/baseline_total;useful=abs(change)<=10
same(C['ordinary_sum_fixture_medians_ms'],baseline_total,'ordinary total');same(C['instrumented_sum_fixture_medians_ms'],profiled_total,'instrumented total');same(C['observed_outer_change_pct'],change,'outer change');same(C['optimistic_overlap_ceiling_pct_of_ordinary'],ceiling,'optimistic span ceiling')
for name,v in grouped.items():same(C['grouped_stage_sum_fixture_medians_ms'][name],v,'grouped medians');same(C['grouped_stage_fraction_of_ordinary_pct'][name],100*v/baseline_total,'ordinary denominator')
ck(C['diagnostic_usefulness_guard_pass']==useful and C['status']==('pass' if useful else 'inconclusive') and not C['possible_2pct_saving_established'] and not C['candidate_accepted'] and not C['deployment_changed'],'scoped diagnostic decision')
clean=read(R/'runs/D065-cleanup/report.json');ck(sha(R/'runs/D065-cleanup/report.json')=='4149eb3212b2ecec041403e50c07571da9b026fec7dbf0efa7d039097eb99f0f','cleanup exact')
ck(clean['source_before']['source_sha256']==expected and clean['source_after']['source_sha256']==base['source_sha256'] and clean['accepted_sources_restored'],'restoration custody')
for name,h in base['source_sha256'].items():ck(sha(REPO/name)==h,'restored accepted source '+name)
ck(any(x.is_file() and sha(x)==source['candidate_source_sha256'] for x in (R/'runs/D065-cleanup').iterdir()),'archived candidate bytes')
for name,v in plan['preexisting_target_artifacts'].items():ck(sha(REPO/name)==v['sha256'] and (REPO/name).stat().st_size==v['bytes'],'preserved preexisting PTX')
ck(sha(Path(r'X:\Dev\GTOpen\target\desktop-runtime\release\gto-server.exe'))==clean['live_executable_sha256']=='b7b808b8baff6b3a92c4f3cc8c54ee74ee2c0bb079a8ca68be4da9703f6b84bd','live executable unchanged')
ck(subprocess.check_output(['git','-C',r'X:\Dev\GTOpen','rev-parse','HEAD'],text=True).strip()=='ae823c8bd6d723c75e096da139fd638d7dd397eb','main HEAD unchanged')
ck(auth['at']<=act['at']<candidate['built_at']<inv['at']<=runs[order[0]]['report']['started_at']<runs[order[-1]]['report']['finished_at']<=done['at']<=clean['at'],'authorization/build/cohort/cleanup chronology')
report={'id':'D065','verdict':'PASS_SCOPED_DIAGNOSTIC_AUDIT','numerical_and_custody_pass':True,'all18_complete_non_timing_results_exact':True,'all138_convergence_checkpoints_exact':True,'all_normalized_stage_trajectories_exact':True,'profile_records':9,'ordered_spans':126,'ordinary_records':0,'ordinary_sum_fixture_medians_ms':baseline_total,'instrumented_sum_fixture_medians_ms':profiled_total,'outer_change_pct':change,'diagnostic_usefulness_guard_pass':useful,'grouped_host_span_medians_ms':grouped,'optimistic_measured_span_overlap_pct':ceiling,'all_six_samples':fixture_stats,'accepted_sources_restored':True,'candidate_accepted':False,'deployment_changed':False,'checks_passed':len(checks),'input_sha256':pins,'conclusion':'These observations do not justify an overlap-only candidate targeting at least2percent complete-cycle improvement: the deliberately optimistic min(transfer-related host,CPU encode/scatter/restore) estimate is below2percent before unmeasured startup/tail/contention/extra-buffer costs. This is an evidence-based no-go for that immediate direction, not an absolute hardware ceiling or proof of actual saving.','limits':['Host-call and wait spans do not isolate PCIe time; CPU write includes encoding,scatter and inactive restoration. Timer bookkeeping can appear in neighboring spans.','The10percent outer guard screens usefulness only and does not bound component bias, cache effects or alternative mechanisms. Grouped envelopes/components overlap.','Complete result/fingerprint and trajectory equality is verified from retained raw JSON; full CPU/device arrays were not retained for bytewise replay by this audit.','Reviewer only parsed/hashed evidence and read main HEAD; no script import, compiler,native,GPU,query or source/status/live changes. All candidate bytes and prior reviews remain preserved.']}
(O/'report.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf8')
(O/'summary.md').write_text(f'D065 scoped diagnostic audit passed. All18 complete non-timing results and138 checkpoints are exact;9 traces contain126 ordered spans. The fixed six samples, source/binary custody and restoration are verified.\n\nTransfer-related host spans total{grouped["transfer_host_ms"]:.4f}ms and CPU encoding/scatter/restore spans total{grouped["cpu_encode_scatter_restore_ms"]:.4f}ms using sums of per-fixture medians. Optimistic per-record overlap estimate:{ceiling:.10f}% of ordinary complete-cycle time. Outer perturbation:{change:.10f}%.\n\nThis does not justify an immediate overlap-only candidate targeting2% complete-cycle improvement. It is not an absolute hardware bound, measured saving or candidate acceptance. Accepted E020 and live executable are unchanged.\n',encoding='utf8')
(O/'manifest.json').write_text(json.dumps({'id':'D065-independent-review','artifact_sha256':{name:hashlib.sha256((O/name).read_bytes()).hexdigest() for name in ['audit.py','report.json','summary.md']},'candidate_accepted':False},indent=2)+'\n',encoding='utf8')
print(json.dumps({'verdict':report['verdict'],'report':sha(O/'report.json'),'manifest':sha(O/'manifest.json'),'checks':len(checks),'pins':len(pins),'transfer_host_ms':grouped['transfer_host_ms'],'cpu_encode_ms':grouped['cpu_encode_scatter_restore_ms'],'optimistic_pct':ceiling,'outer_pct':change}))
