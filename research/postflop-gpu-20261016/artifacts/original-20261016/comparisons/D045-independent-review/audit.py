from pathlib import Path
import json,hashlib,re,statistics,math,datetime,traceback
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');P=R/'runs/D045-sparse-event-diagnostic';O=R/'comparisons/D045-independent-review';inputs={}
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def pin(p,h=None):
 p=Path(p);v=digest(p)
 if h is not None:assert v==h,(str(p),v,h)
 inputs[str(p)]=v;return v
def read(p,h=None):pin(p,h);return json.loads(Path(p).read_text())
def put(n,x):
 with (O/n).open('x',encoding='utf-8',newline='\n') as f:f.write(x if isinstance(x,str) else json.dumps(x,indent=2,allow_nan=False)+'\n')
def markers(p,prefix):return [json.loads(l.split(prefix,1)[1]) for l in Path(p).read_text().splitlines() if prefix in l]
def run():
 assessment=read(R/'comparisons/D045-sparse-event-diagnostic/report.json','2d68da44be8de1324454bbc45f834e9b2f85baef01fa92a5f8e0c8a9e828e1c9')
 seal=read(P/'scripts-manifest.json','66bc61035bbee5308e7cc34281ffeb86d41f7ec4157a308b6d76741068d97e74')
 for n,h in seal['script_sha256'].items():pin(P/n,h)
 auth=read(P/'authorization.json','b1af7e7ae55efa0888db00323a9b34fc4b7060107f46a6aa82bbb9cc5d20f5d4')
 for n,h in auth['evidence_sha256'].items():pin(n,h)
 activation=read(P/'activation.json','3274663acff6824594fe5e25e1b0c11112a1426ed4a4f074a70fa3799ed57a07')
 protocol=read(P/'protocol.json');source=read(P/'source/source-manifest.json','0952fc2dde596ac297fd76398fa10e74ee00e46aa6f374359384046ceb3d15a8')
 for n,h in source['artifact_sha256'].items():pin(P/'source'/n,h)
 m=read(R/'binaries/D045-solver.manifest.json');binary=R/'binaries/D045-solver.exe';pin(binary,'7c8e2c45f9e2e28bca2bd0c8d9233ef80725525c72395c5e8c3c9b08485845a3')
 assert m['binary_sha256']==digest(binary)
 custody=read(O/'source-custody.json','92079bb9213fd91362b7e9a9075066c62b7acfb19fa2d64bb1e5d477c6532eda');assert custody['source_sha256']==m['source_sha256']
 accepted=read(R/'binaries/E020-postflop_autoresearch.manifest.json',seal['reference_sha256'][str(R/'binaries/E020-postflop_autoresearch.manifest.json')])['source_sha256']
 assert activation['source_before']['source_sha256']==accepted
 assert activation['source_after']['source_sha256']==m['source_sha256']
 assert len(accepted)==162 and len(m['source_sha256'])==163
 owned=source['candidate_sha256'];assert {n:h for n,h in m['source_sha256'].items() if n not in owned}=={n:h for n,h in accepted.items() if n not in owned}
 assert all(m['source_sha256'][n]==h for n,h in owned.items())
 assert activation['authorization_sha256']==digest(P/'authorization.json') and activation['main_or_live_modified'] is False
 before=read(R/'runs/D045-build/source-before.json');assert before['source_sha256']==m['source_sha256']
 for v in m['source_copies'].values():pin(v['path'],v['sha256'])
 for n,h in m['dependency_artifact_sha256'].items():pin(n,h)
 for key,hk in [('build_log','build_log_sha256'),('build_stderr_log','build_stderr_sha256'),('patch','patch_sha256')]:pin(m[key],m[hk])
 assert m['patch_sha256']==digest(P/'source/candidate.patch')
 be=read(R/'runs/D045-build/exit.json');env=read(R/'runs/D045-build/build-environment.json')
 assert be['returncode']==0 and be['error'] is None and be['cleanup'] is None
 assert env['target_previously_absent'] and env['compiler_override_absence']=={}
 records=[json.loads(x) for x in Path(m['build_log']).read_text().splitlines()]
 assert [x for x in records if x.get('reason')=='build-finished']==[{'reason':'build-finished','success':True}]
 ca=[x for x in records if x.get('reason')=='compiler-artifact' and x.get('executable') and x.get('target',{}).get('name')=='solver'];assert ca==[m['cargo_artifact']]
 assert ca[0]['fresh'] is False and ca[0]['features']==['gpu'] and ca[0]['profile']['test'] is True
 assert Path(ca[0]['executable']).is_relative_to(Path(m['target_dir'])) and digest(ca[0]['executable'])==digest(binary)
 assert ca[0]['target']['src_path']==str(Path(r'X:\Dev\GTOpen-gpu-research-20261016\crates\solver\src\lib.rs'))
 cuda=R/'runs/D037-showdown-cache-design/candidate/kernels.cu';pin(cuda,accepted['crates/solver/src/gpu/kernels.cu']);data=binary.read_bytes();assert cuda.read_bytes() in data and b'D045_EVENT_DIAGNOSTIC' in data
 inv=read(R/'runs/D045-execution/invocation.json');ee=read(R/'runs/D045-execution/exit.json');complete=read(R/'runs/D045-execution/complete.json');rr=read(R/'runs/D045R1/report.json')
 for n in ['stdout.log','stderr.log']:pin(R/'runs/D045-execution'/n)
 assert ee['returncode']==0 and ee['error'] is None and ee['cleanup'] is None and complete['native_test_pass']
 assert rr['returncode']==0 and rr['test_pass_count']==1 and rr['status']=='measured' and rr['accepted'] is False and rr['kind']=='diagnostic'
 assert rr['binary_sha256']==m['binary_sha256']==inv['binary_sha256'] and rr['binary_build_manifest']['data']==m and rr['binary_build_manifest']['sha256']==digest(R/'binaries/D045-solver.manifest.json')
 assert rr['provenance']['source_sha256']==m['source_sha256']==inv['source_sha256']
 assert inv['authorization_sha256']==m['probe_authorization_sha256']==digest(P/'authorization.json')
 assert m['probe_evidence_sha256']==auth['evidence_sha256'] and m['build_script_sha256']==digest(P/'build.py') and inv['script_sha256']==digest(P/'run.py')
 assert inv['protocol_sha256']==m['primary_protocol_sha256']==digest(P/'protocol.json')
 times=[auth['authorized_at'],activation['at'],be['at'],inv['at'],rr['process_started_at'],rr['finished_at'],ee['at']];assert times==sorted(times)
 assert rr['command']==[str(binary),protocol['test_filter'],'--nocapture','--test-threads=1','--ignored']
 for k,v in [('RAYON_NUM_THREADS','16'),('POSTFLOP_AUTORESEARCH_FIXTURE','rainbow'),('POSTFLOP_AUTORESEARCH_STORAGE','compressed'),('POSTFLOP_AUTORESEARCH_PROFILE','0')]:assert rr['environment'][k]==v
 raw=R/'runs/D045R1/stdout.log';pin(raw,rr['stdout_sha256']);txt=raw.read_text()
 assert re.findall(r'test result: ok\. (\d+) passed; (\d+) failed; (\d+) ignored; (\d+) measured; (\d+) filtered out;',txt)==[('1','0','0','0','88')]
 assert not any(s in txt for s in ['D045_CLEANUP_ERROR','D045_SOLVER_CLEANUP_ERROR','D045 invalid diagnostic','panicked at'])
 assert not (R/'runs/D045-execution/stderr.log').read_text().strip()
 rows=markers(raw,protocol['marker']);assert len(rows)==22 and [x['stage'] for x in rows]==protocol['expected_stage_order']
 assert rows==read(R/'comparisons/D045-sparse-event-diagnostic/parsed-records.json')
 groups={k:[x for x in rows if x['stage']==k] for k in set(x['stage'] for x in rows)}
 rawcheck=groups['raw_exact'];assert [x['iteration'] for x in rawcheck]==[140,160,180,200]
 oldreport=read(R/'runs/D033R1/report.json');oldraw=R/'runs/D033R1/stdout.log';pin(oldraw,oldreport['stdout_sha256']);oldrows=markers(oldraw,'D033_EVENT_DIAGNOSTIC ')
 assert rawcheck==[x for x in oldrows if x['stage']=='raw_exact']
 assert all(x['pass'] and x['before_exploitability'] and not x['cfv_scratch_compared'] and x['chunk_floats']==1048576 and x['peak_pairwise_snapshot_bytes']==8388608 for x in rawcheck)
 words=sum(a['entries'] for x in rawcheck for a in x['arrays']);assert words==4426132436==assessment['raw_f32_words_compared']
 assert [x['iteration'] for x in groups['warm_check']]==list(range(20,141,20)) and [x['iteration'] for x in groups['checkpoint_exact']]==[160,180,200]
 assert all(x['raw_and_compressed_pass'] for x in groups['checkpoint_exact'])
 helper=(P/'source/candidate-graph_device_events.rs').read_text();anchor=json.loads(re.search(r'const ANCHOR_JSON: &str = r#"(.*?)"#;',helper,re.S).group(1));conv=json.loads(re.search(r'const CONVERGENCE_JSON: &str = r#"(.*?)"#;',helper,re.S).group(1));expected={x['iteration']:x['exploit_bits'] for x in conv}
 assert {x['iteration']:x['exploit_bits'] for x in groups['warm_check']+groups['checkpoint_exact']}==expected
 full=groups['final_anchor_exact'][0]['state_fingerprint'];assert full==anchor['state_fingerprint']==assessment['final_state_fingerprint']
 for name in ['B038','E015C1','E020C1']:
  j=read(R/f'runs/{name}/report.json',seal['reference_sha256'][str(R/f'runs/{name}/report.json')]);f=next(x for x in j['results'] if x['fixture_id']=='rainbow');assert f['config']==anchor['config'] and f['state_fingerprint']==full
  assert {x['data']['iteration']:x['data']['exploit_bits'] for x in j['stages'] if x['data'].get('fixture_id')=='rainbow' and x['data']['stage']=='convergence_check'}==expected
 top=[x['topology'] for x in groups['graph']];assert [x['graph'] for x in top]==[0,1]
 for gi,g in enumerate(top):
  assert (g['original_kernel_nodes'],g['event_nodes'],g['total_nodes'],g['total_edges'])==(63,6,69,74)
  assert g['event_boundaries']==[19,20,29,30,34,35] and g['selected_ordinals']==[19,29,34]
  assert g['original_edges']==[[f'K{i}',f'K{i+1}'] for i in range(62)]
  assert g['added_edges']==[e for b in [19,20,29,30,34,35] for e in [[f'K{b-1}',f'E{b}'],[f'E{b}',f'K{b}']]]
  assert g['kernel_argument_setter_calls']==0 and [x['ordinal'] for x in g['kernel_descriptors']]==list(range(63))
  for s in [x for x in protocol['selector_rule']['resolved_selectors'] if x['graph']==gi]:
   d=g['kernel_descriptors'][s['ordinal']]['logical'];assert d=={k:s[k] for k in ['kernel','grid','block','shared_bytes']}
   assert min((x for x in g['kernel_descriptors'] if x['logical']['kernel']==s['kernel']),key=lambda x:(-math.prod(x['logical']['grid']),x['ordinal']))['ordinal']==s['ordinal']
 samples={};outer=[]
 for i,b in enumerate(groups['batch']):
  cp=[160,180,200][i];assert b['batch']==i and b['checkpoint']==cp and b['arm_order']==protocol['batch_arm_order'][i]
  for arm in ['native','instrumented']:
   x=b[arm];assert x['iterations']==20 and x['end_iteration']==cp and x['arm']==arm
   assert all(math.isfinite(x[k]) and x[k]>0 for k in ['device_batch_ms','host_batch_ms'])
  ins=b['instrumented'];assert ins['setup_upload_wait_excluded'] and 'final_replay_inter_graph_gap_ms' not in ins
  assert [x['graph'] for x in ins['final_replay_only']]==[0,1]
  for g in ins['final_replay_only']:
   assert g['iteration']==cp and [n['ordinal'] for n in g['nodes']]==[19,29,34] and 'family_ms' not in g and 'graph_envelope_ms' not in g
   for n in g['nodes']:
    d=top[g['graph']]['kernel_descriptors'][n['ordinal']]['logical'];assert n['logical']==d and n['kernel']==d['kernel'] and (n['start_boundary'],n['end_boundary'])==(n['ordinal'],n['ordinal']+1)
    assert math.isfinite(n['ms']) and n['ms']>=0 and n['near_resolution']==(n['ms']<=0.0005)
    samples.setdefault((g['graph'],n['ordinal'],n['kernel']),[]).append(n['ms'])
  x=b['native']['device_batch_ms'];y=ins['device_batch_ms'];pct=100*(y/x-1)
  outer.append({'checkpoint':cp,'order':b['arm_order'],'native_device_batch_ms':x,'instrumented_device_batch_ms':y,'native_host_batch_ms':b['native']['host_batch_ms'],'instrumented_host_batch_ms':ins['host_batch_ms'],'device_change_pct':pct,'abs_device_change_pct':abs(pct),'within_10pct':abs(pct)<=10})
 selected=[{'graph':k[0],'ordinal':k[1],'kernel':k[2],'descriptor':top[k[0]]['kernel_descriptors'][k[1]]['logical'],'samples':v,'median':statistics.median(v),'min':min(v),'max':max(v)} for k,v in sorted(samples.items())]
 assert len(samples)==6 and all(len(v)==3 for v in samples.values()) and selected==assessment['selected_launch_samples'] and outer==assessment['outer_batches']
 assert all(x['within_10pct'] for x in outer) and assessment['status']=='pass' and assessment['candidate_accepted'] is False and assessment['extension_allowed'] is False
 assert groups['complete'][0]['total_selected_intervals']==18 and groups['complete'][0]['accepted_performance_claim'] is False
 adm=groups['admission'][0];assert adm['dual_device_required_with_reserve']==2*adm['device_per_arm_payload_bytes']+adm['device_reserve_bytes']<=adm['device_free_bytes'];assert adm['host_additional_required']<=adm['host_free_after_spot_and_plan']
 assert len(list((R/'runs').glob('D045R*')))==1
 sm=read(R/'comparisons/D045-sparse-event-diagnostic/manifest.json')
 for n,h in sm['files'].items():pin(R/'comparisons/D045-sparse-event-diagnostic'/n,h)
 result={'id':'D045','verdict':'PASS_SCOPED_DIAGNOSTIC','source_entries':163,'native_invocations':1,'native_tests_passed':1,'native_tests_filtered':88,'markers':22,'selected_interval_count':18,'raw_words_compared':words,'raw_checkpoint_records_equal_immutable_D033':True,'raw_and_compressed_checkpoints':[140,160,180,200],'all10_exploit_anchors_exact':True,'full_state_fingerprint':full['hash'],'full_state_exploit_bits':full['exploit_bits'],'source_custody':digest(O/'source-custody.json'),'binary_sha256':m['binary_sha256'],'auth_to_terminal_chronology':times,'outer_batches':outer,'selected_launch_samples':selected,'candidate_accepted':False,'scope':'Six selected training launches at three final replays, not native family/fullsolve shares or speedup proof.','limitations':['The10%outer guard does not bound individual-node bias.','Graph0 up_show sample200 is1.543136ms and exceeds that sampled up_action; retain it, do not describe uniform per-sample rank.','Samples are final replays at distinct iterations, not20-replay means or independent repeated benchmark trials.','CFV scratch excluded; full raw bytes compared by native test in bounded buffers, not persisted.','Full compressed equality140 is inherited source-enforced before graph setup, without separate marker.'],'artifact_sha256':inputs}
 put('validation.json',result)
 lines=['# D045 independent terminal review','','PASS_SCOPED_DIAGNOSTIC. One fresh build and one fixed native invocation completed,1 test passed/88 filtered. Authorization, source activation, fresh compiler artifact, embedded E020 CUDA, frozen binary, logs and all163 active source entries match. Source custody was sealed before root restoration.','','All22 markers, four raw-before-evaluation checkpoints, full compressed-store comparisons, all10 exploit anchors and the complete original/E015/E020 final-state anchor pass. The four raw checkpoint records also equal immutable D033 records, covering4,426,132,436 paired float words. Fingerprint65fb2853a11f3acc; exploitbits4595130701932466176. Both graph topologies are exactly69 nodes/74 edges with six unique registered boundaries.','','Outer20-iteration device perturbations:5.160594%,5.642749%,5.309473%; all satisfy the unchanged absolute10% diagnostic guard. Every one of18 selected intervals is retained.','','| Selected launch | Median ms | Range ms |','|---|---:|---:|']
 for x in selected:lines.append(f"| Graph{x['graph']} {x['kernel']} ({x['ordinal']}) | {x['median']:.6f} | {x['min']:.6f}–{x['max']:.6f} |")
 lines.extend(['','The selected up_action median is largest in each graph. Graph0 up_show at iteration200 is1.543136ms, larger than that checkpoint\'s up_action; this variation is retained. These intervals may motivate a bounded source hypothesis, but do not quantify family shares, full-solve costs, universal rankings, native uninstrumented timing or a speedup. Passing the outer guard does not bound bias in an individual interval. No candidate is accepted and no extension is authorized.','','No build, native/GPU execution, source or dashboard edit was performed by this reviewer.'])
 put('summary.md','\n'.join(lines)+'\n')
 put('manifest.json',{'id':'D045-independent-review','status':'SEALED','artifact_sha256':{p.name:digest(p) for p in sorted(O.iterdir()) if p.is_file()},'diagnostic_only':True})
 print(json.dumps({'validation_sha256':digest(O/'validation.json'),'summary_sha256':digest(O/'summary.md'),'manifest_sha256':digest(O/'manifest.json'),'outer_abs_pct':[x['abs_device_change_pct'] for x in outer]}))
try:run()
except BaseException as e:
 put('audit-failure.json',{'error':repr(e),'traceback':traceback.format_exc(),'inputs_seen':inputs,'native_runs_by_reviewer':0});raise
