"""Independent E018 terminal evidence audit; no builds, GPU calls or dashboard writes."""
import csv, hashlib, json, math, re, statistics
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
OUT=Path(__file__).parent
PAIRS=[('B056','E018R1'),('B057','E018R2'),('B058','E018R3')]
ORDER=['B056','E018R1','E018R2','B057','B058','E018R3']
FIXTURES=['rainbow','two-tone','river']
TIMINGS={'build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms','fingerprint_ms_excluded'}
COMPONENTS=['build_ms','init_ms','solve_ms','readback_ms','full_cycle_ms']
UNIT_NAMES=['game::tests::vram_estimate_counts_unused_child_mapping_entries',
 'gpu::plan::tests::child_mapping_handles_generic_menus_and_rejects_invalid_physical_slots',
 'gpu::plan::tests::river_bounds_match_strength_comparisons',
 'gpu::tests::paired_reach_reuse_matches_full_sweeps_across_lifecycle',
 'gpu::tests::paired_reach_reuse_preserves_raw_player1_and_standalone_refresh',
 'gpu::tests::shared_evaluation_matches_independent_sweeps',
 'gpu::tests::tight_f32_budget_preserves_warm_and_queried_inactive_state']
CAPACITY='gpu::continuation_capacity::tests::child_mapping_matches_observed_metadata_for_turn_and_river'
checked={}
def sha(path,expected=None):
 p=Path(path);h=hashlib.sha256(p.read_bytes()).hexdigest()
 if expected is not None:assert h==expected.lower(),str(p)
 checked[str(p)]=h;return h
def read(path):
 sha(path);return json.loads(Path(path).read_text(encoding='utf-8-sig'))
def smap(m):return {k.replace('\\','/'):v.lower() for k,v in m.get('source_sha256',m.get('hashes')).items()}
def load(ident):
 p=ROOT/'runs'/ident;r=read(p/'report.json');assert r['id']==ident and r['status']=='measured' and r['returncode']==0
 sha(p/'stdout.log',r['stdout_sha256']);raw=(p/'stdout.log').read_text(encoding='utf-8-sig')
 sha(r['command'][0],r['binary_sha256']);ref=r['binary_build_manifest'];sha(ref['path'],ref['sha256']);m=read(ref['path']);assert m==ref['data'] and ref['binary_hash_verified'] and m['binary_sha256']==r['binary_sha256']
 s=re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',raw);assert len(s)==1
 counts=list(map(int,s[0]));assert counts[0]==r['test_pass_count'] and counts[1]==0
 return r,raw,m,counts
def named_ok(raw,name):
 m=re.search(r'^test '+re.escape(name)+r' \.\.\.(.*?)(?=^test [\w:]|^test result:|\Z)',raw,re.M|re.S)
 assert m and re.search(r'\bok\s*$',m[1]),name
def close(a,b):assert math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-9),(a,b)
def gain(b,c):return (b-c)/b*100
def stamp(s):return datetime.fromisoformat(s.replace('Z','+00:00'))
def save(name,data):
 with (OUT/name).open('x',encoding='utf-8',newline='\n') as f:json.dump(data,f,indent=2);f.write('\n')
def main():
 comparison=read(ROOT/'comparisons/E018-three-pair-comparison/report.json')
 design=read(ROOT/'runs/E018-design-r2/manifest.json');sources=design['candidate_source_sha256'];assert len(sources)==5
 sums=read(ROOT/'runs/E018-design-r2/checksums.json')
 for n,h in sums.items():sha(ROOT/'runs/E018-design-r2'/n,h)
 for rel,h in sources.items():sha(ROOT/'runs/E018-build/source'/Path(rel).name,h)
 sha(ROOT/'runs/E018-build/candidate.patch',design['patch_sha256'])
 primary=read(ROOT/'binaries/E018-postflop_autoresearch.manifest.json');candidate_map=smap(primary)
 builds={}
 for name in ['postflop_autoresearch','solver','continuation-tests']:
  m=read(ROOT/'binaries'/f'E018-{name}.manifest.json');assert smap(m)==candidate_map
  sha(ROOT/'binaries'/f'E018-{name}.exe',m['binary_sha256']);sha(m['build_log'],m['build_log_sha256'])
  sha(m.get('build_stderr_log',m.get('build_stderr')),m['build_stderr_sha256'])
  records=[json.loads(line) for line in Path(m['build_log']).read_text().splitlines()]
  assert [x for x in records if x.get('reason')=='build-finished']==[{'reason':'build-finished','success':True}]
  assert all(candidate_map[k]==v for k,v in sources.items())
  builds[name]={'binary_sha256':m['binary_sha256'],'built_at':m['built_at'],'command':m['build_command'],'source_entries':len(candidate_map)}
 assert 'preflop-research' in builds['continuation-tests']['command']
 assert 'gpu' in builds['postflop_autoresearch']['command']
 tests={};all_reports={}
 for ident,names,expected in [('V018-unit',UNIT_NAMES,[86,0,4]),('V018-capacity',[CAPACITY],[1,0,0])]:
  r,raw,m,counts=load(ident);assert counts[:3]==expected
  for n in names:named_ok(raw,n)
  assert smap(m)==candidate_map and r['provenance']['source_sha256']==candidate_map
  if ident=='V018-capacity':assert r['command'][1]==CAPACITY and 'preflop-research' in m['build_command']
  all_reports[ident]=r;tests[ident]={'counts':dict(zip(['passed','failed','ignored','measured','filtered'],counts)),'named_passes':names,'binary_sha256':r['binary_sha256'],'run_source_entries_verified':len(candidate_map)}
 reports={};raws={};maps={}
 for ident in ORDER:
  r,raw,m,counts=load(ident);assert counts[0]==1 and r['command'][1:]==['postflop_complete_cycle','--nocapture','--test-threads=1','--ignored']
  rows=[json.loads(line.split('AUTORESEARCH_RESULT ',1)[1]) for line in raw.splitlines() if 'AUTORESEARCH_RESULT ' in line]
  assert rows==r['results'] and [v['fixture_id'] for v in rows]==FIXTURES
  for value in rows:
   assert value['target_met'] and value['target_pct']==0.3 and value['check_every']==20 and value['max_iterations']==400
   assert value['storage']=='compressed' and value['runtime_nvrtc_jit_included'] and value['flushed_progress_logging_included']
   assert all(math.isfinite(value[k]) and value[k]>0 for k in TIMINGS)
  reports[ident]=r;all_reports[ident]=r;raws[ident]=rows;maps[ident]=smap(m)
 ref=reports[ORDER[0]];env=ref['environment']
 assert env['RAYON_NUM_THREADS']=='16' and env['POSTFLOP_AUTORESEARCH_STORAGE']=='compressed' and env['POSTFLOP_AUTORESEARCH_FIXTURE'] is None and env['POSTFLOP_AUTORESEARCH_PROFILE']=='0'
 def gpu(r):
  assert r['telemetry_before']['gpu']['returncode']==0
  return [row[:4] for row in csv.reader(r['telemetry_before']['gpu']['stdout'].splitlines(),skipinitialspace=True)]
 frozen=read(ROOT/'baseline-manifest.json');frozen_map=smap(frozen)
 for ident,r in reports.items():
  assert r['environment']==env and gpu(r)==gpu(ref)
  for i,v in enumerate(raws[ident]):assert {k:x for k,x in v.items() if k not in TIMINGS}=={k:x for k,x in raws[ORDER[0]][i].items() if k not in TIMINGS},(ident,i)
  for name in ['bench_spot.json','crates/solver/tests/postflop_autoresearch.rs']:
   assert maps[ident][name]==frozen_map[name]==r['provenance']['benchmark_sha256'][name].lower()
  if ident.startswith('E018'):assert r['provenance']['source_sha256']==candidate_map
 for column,cohort in enumerate(['baseline','candidate']):
  ids=[pair[column] for pair in PAIRS];assert comparison['cohorts'][cohort]['run_ids']==ids
  assert len({reports[i]['binary_sha256'] for i in ids})==1 and len({reports[i]['binary_build_manifest']['sha256'] for i in ids})==1
  assert all(maps[i]==maps[ids[0]] for i in ids)
  expected=design['base_source_sha256'] if column==0 else sources
  assert all(maps[i][k]==h for i in ids for k,h in expected.items())
 changes=sorted(k for k in set(maps['B056'])|set(maps['E018R1']) if maps['B056'].get(k)!=maps['E018R1'].get(k))
 assert changes==sorted(sources),changes
 protocol=read(ROOT/'runs/E018-primary-plan/protocol.json');assert protocol['order']==['V018-unit','V018-capacity']+ORDER
 assert protocol['pairs']==[{'baseline':b,'candidate':c} for b,c in PAIRS] and protocol['exclusions']==[]
 for name,h in protocol['scripts'].items():sha(ROOT/'runs'/name,h)
 assert sorted(all_reports,key=lambda i:stamp(all_reports[i]['started_at']))==protocol['order']
 gaps=[]
 for before,after in zip(protocol['order'],protocol['order'][1:]):
  delta=(stamp(all_reports[after]['started_at'])-stamp(all_reports[before]['finished_at'])).total_seconds();assert delta>=0
  gaps.append({'before':before,'after':after,'gap_seconds':delta})
 for name,b in builds.items():assert stamp(b['built_at'])<=stamp(all_reports['V018-unit']['started_at'])
 fixture_rows=[];paired=[]
 for i,fixture in enumerate(FIXTURES):
  b=[raws[x][i]['full_cycle_ms'] for x,y in PAIRS];c=[raws[y][i]['full_cycle_ms'] for x,y in PAIRS]
  bm,cm=statistics.median(b),statistics.median(c);reg=[-gain(x,y) for x,y in zip(b,c)];medreg=-gain(bm,cm);repeat=sum(x>3 for x in reg);failed=medreg>3 and repeat>=2
  cr=comparison['fixtures'][i];gr=comparison['performance']['fixture_regression_guard']['fixtures'][i]
  close(cr['baseline']['full_cycle_ms']['median_ms'],bm);close(cr['candidate']['full_cycle_ms']['median_ms'],cm);close(gr['median_regression_pct'],medreg)
  for x,y in zip(gr['paired_regression_pct'],reg):close(x,y)
  assert gr['repetitions_above_3pct']==repeat and gr['required_repetitions']==2 and gr['repeatable_material_regression']==failed
  components={k:{'baseline_median_ms':statistics.median(raws[x][i][k] for x,y in PAIRS),'candidate_median_ms':statistics.median(raws[y][i][k] for x,y in PAIRS),'paired_candidate_minus_baseline_ms':[raws[y][i][k]-raws[x][i][k] for x,y in PAIRS]} for k in COMPONENTS}
  for k,d in components.items():close(cr['baseline'][k]['median_ms'],d['baseline_median_ms']);close(cr['candidate'][k]['median_ms'],d['candidate_median_ms'])
  fixture_rows.append({'fixture_id':fixture,'baseline_raw_ms':b,'candidate_raw_ms':c,'baseline_median_ms':bm,'candidate_median_ms':cm,'gain_pct':gain(bm,cm),'paired_regression_pct':reg,'repetitions_over_3pct':repeat,'guard_failed':failed,'components':components})
 for (b,c),published in zip(PAIRS,comparison['pairs']):
  bt=sum(v['full_cycle_ms'] for v in raws[b]);ct=sum(v['full_cycle_ms'] for v in raws[c]);close(published['baseline_full_cycle_ms'],bt);close(published['candidate_full_cycle_ms'],ct);close(published['observed_gain_pct'],gain(bt,ct))
  assert published['baseline_id']==b and published['candidate_id']==c
  for i,f in enumerate(FIXTURES):close(published['fixture_gain_pct'][f],gain(raws[b][i]['full_cycle_ms'],raws[c][i]['full_cycle_ms']))
  paired.append({'baseline':b,'candidate':c,'gain_pct':gain(bt,ct),'component_candidate_minus_baseline_ms':{k:sum(v[k] for v in raws[c])-sum(v[k] for v in raws[b]) for k in COMPONENTS}})
 bs=sum(x['baseline_median_ms'] for x in fixture_rows);cs=sum(x['candidate_median_ms'] for x in fixture_rows);g=gain(bs,cs);pf=comparison['performance']
 close(pf['baseline_full_cycle_ms'],bs);close(pf['candidate_full_cycle_ms'],cs);close(pf['observed_gain_pct'],g)
 assert pf['aggregate_gate_met']==(g>=2) and pf['fixture_regression_guard']['failed']==any(x['guard_failed'] for x in fixture_rows)
 assert g<2 and not any(x['guard_failed'] for x in fixture_rows) and comparison['decision']=='rejected' and not comparison['accepted'] and not comparison['deployed'] and comparison['excluded_runs']==[]
 refusal=read(ROOT/'runs/E018-prelaunch-refusal/record.json');assert refusal['native_launches']==0 and refusal['timing_samples']==0 and refusal['run_order_changes']==[]
 assert refusal['all_planned_run_directories_absent']==protocol['order'];sha(ROOT/'runs/E018-primary.py',refusal['primary_script_sha256'])
 assert refusal['feature_binary_sha256']==builds['continuation-tests']['binary_sha256'];assert stamp(refusal['at'])<stamp(all_reports['V018-unit']['started_at'])
 adapter=read(ROOT/'runs/E018-primary-assessment/comparison-adapter.json')
 assert adapter['logical_candidate']=='E018' and adapter['measured_candidate']=='E018R1' and adapter['timing_exclusions']==[]
 for key in ['source_patch','design_patch','alias_patch']:sha(adapter[key],adapter['all_patch_sha256'])
 assert adapter['all_patch_sha256']==design['patch_sha256']
 invocation=read(ROOT/'runs/E018-primary-assessment/invocation.json');assert invocation['returncode']==0
 assert invocation['command'][invocation['command'].index('--candidate-id')+1]=='E018R1'
 assert '--warm-cache-cohort' in invocation['command'] and '--reject' in invocation['command']
 assessment=read(ROOT/'runs/E018-primary-assessment/stdout.log');assert assessment['decision']=='rejected' and assessment['performance']==pf
 assert (ROOT/'runs/E018-primary-assessment/stderr.log').read_bytes()==b'';sha(ROOT/'runs/E018-primary-assessment/stderr.log')
 sha(ROOT/'runs/E018-assess.py');assert not (ROOT/'runs/E018').exists()
 for sub in ['E018-source-review','E018-source-review-r2']:
  for p in sorted((ROOT/'comparisons'/sub).iterdir()):
   if p.is_file():sha(p)
 for item in comparison['preserved_artifacts']:sha(item['path'],item['sha256'])
 result={'candidate':'E018','audit_verdict':'PASS_rejection_confirmed','created_at':datetime.now(timezone.utc).isoformat(),'builds':builds,'tests':tests,
 'raw_fixture_records_checked':18,'all_complete_nontiming_records_exact':True,'excluded_record_keys_are_only_timing':sorted(TIMINGS),'source_changes':changes,
 'candidate_runtime_source_entries_verified_per_run':len(candidate_map),'candidate_and_validation_source_runs_verified':5,
 'pairs':paired,'chronological_run_order':protocol['order'],'gaps':gaps,'fixtures':fixture_rows,
 'performance':{'baseline_ms':bs,'candidate_ms':cs,'gain_pct':g,'aggregate_gate_met':False,'fixture_guard_failed':False,'decision':'rejected'},
 'paired_mean_component_candidate_minus_baseline_ms':{k:statistics.mean(p['component_candidate_minus_baseline_ms'][k] for p in paired) for k in COMPONENTS},
 'operational_notes':['Initial invocation was refused by an existing GPU lock before run-directory creation/native launch; refusal is an operator record sourced from root tool output, without separately preserved stderr.',
 'All scripts, planned IDs, order and paired identities remained unchanged; neither measured samples nor timing components were excluded/replaced.',
 'Logical E018 row maps to actual measured E018R1; build/design/alias patches match. Assessment invocation returned0, empty stderr; no dry-run recovery was recorded.',
 'Comparison labels this a warm-cache cohort. Runtime NVRTC/JIT remains included; cache temperature was not reset or proved identical, and no cold-start qualification follows.'],
 'limits':['No independent GPU/build/test execution by this reviewer; only read/hash/arithmetic analysis and new audit artifacts.',
 'Complete-state runtime exactness covers three compressed primary fixtures. Unit lifecycle comparisons share the candidate up kernel and do not substitute for immutable original menu/F32/saved-state/resume references.',
 'Broader original F32/menu/save/resume, extra GPU equivalence and continuation paging/storage qualification were not run after failed performance screen; no general compatibility/deployment claim.',
 'Component differences are descriptive; independent medians need not add, and neither opcode reductions nor timing deltas prove a cause.',
 'Aggregate below2percent determines rejection; no significance claim or further rescue runs recommended.'],
 'checked_artifacts':checked}
 save('validation.json',result)
 lines=['# E018 independent terminal review','','**Audit PASS; rejection confirmed.** Sum of per-fixture medians is '+f'{bs:.4f} -> {cs:.4f} ms ({g:.6f}% observed gain), below the unchanged 2% gate. No fixture triggers the repeatable >3% regression guard.','',
 '| Fixture | E015 median ms | E018 median ms | Observed gain | Paired regressions >3% |','|---|---:|---:|---:|---:|']
 for x in fixture_rows:lines.append(f"| {x['fixture_id']} | {x['baseline_median_ms']:.4f} | {x['candidate_median_ms']:.4f} | {x['gain_pct']:.6f}% | {x['repetitions_over_3pct']}/3 |")
 lines+=['','All 18 raw complete non-timing result objects match across the six runs, including every state fingerprint, root value/exploitability field, stop, configuration and workload setting. Only the six established timing fields were removed. Raw markers also equal their report copies. Frozen evaluator/workload hashes, native binaries, manifests, build logs and patches verify. Exactly the five reviewed production files differ from E015; all 162 build-source entries match runtime provenance for the three candidates and two validation runs.','',
 'Both builds completed before validation/timing. V018-unit: **86 passed, 4 ignored, zero failed**; all seven focused mapping/estimate/lifecycle/evaluation/tight-budget tests were located in stdout. The two printed invalid-slot panics are deliberate caught negative cases followed by ok. V018-capacity: **one passed**, covering the turn and river, uploaded mapping equality, planned/observed payload and exactly-once byte accounting.','',
 'Observed order matches the prospective protocol: V018-unit, V018-capacity, B056, E018R1, E018R2, B057, B058, E018R3. Adjacent timing runs have gaps of zero or one second at report timestamp precision. Pairs remain B056/R1, B057/R2, B058/R3. All six have the same registered environment and GPU/driver identity.','',
 'The first invocation was refused while the feature build held gpu-run.lock. The runner acquires this lock before creating a run directory or calling the native launch path; the operator record reports all planned IDs absent and zero native launches/samples. Its evidence origin is root tool output; a separate raw stderr transcript was not saved. The unchanged script was rerun after the build completed. No measured sample was replaced or excluded.','',
 'The comparison used measured E018R1 while E018 remains the logical dashboard row. Build, r2 design and E018R1 alias patches are byte-identical. Preserved assessment invocation/stdout/stderr verify successful publication; stderr is empty and no dry-run correction is recorded. The warm-cache label does not subtract runtime NVRTC/JIT or establish controlled cache temperature/cold-start behavior.','']
 means=result['paired_mean_component_candidate_minus_baseline_ms'];lines.append('Descriptive paired-total means, candidate minus baseline: '+', '.join(f'{k} {means[k]:+.4f} ms' for k in COMPONENTS)+'. These are not the primary median statistic and do not identify a causal bottleneck.')
 lines+=['','**Scope limit:** failed primary performance stops qualification. No broader immutable-original F32, saved-state/menu/resume or continuation paging/storage controls were run for E018. Existing unit comparisons sharing the candidate up kernel are useful lifecycle checks but cannot independently validate that changed kernel. This review confirms the measured rejection and scoped exactness; it makes no general compatibility, accepted-gain or deployment claim.','',
 'This reviewer performed no build, GPU execution, source edit or dashboard update. Preserved binaries and source archives remain authoritative after checkout restoration.']
 with (OUT/'summary.md').open('x',encoding='utf-8',newline='\n') as f:f.write('\n'.join(lines)+'\n')
 save('manifest.json',{'id':'E018-independent-review','status':'sealed','created_at':datetime.now(timezone.utc).isoformat(),'files':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(OUT.iterdir()) if p.is_file()},'input_artifact_count':len(checked),'no_gpu_or_build_execution':True,'no_dashboard_or_source_edits':True})
 print(json.dumps({'audit_verdict':result['audit_verdict'],'performance':result['performance'],'component_means':means,'fixtures':[{k:x[k] for k in ['fixture_id','baseline_median_ms','candidate_median_ms','gain_pct']} for x in fixture_rows],'checked_artifacts':len(checked),'validation_sha256':hashlib.sha256((OUT/'validation.json').read_bytes()).hexdigest(),'summary_sha256':hashlib.sha256((OUT/'summary.md').read_bytes()).hexdigest()},indent=2))
if __name__=='__main__':main()
