import pathlib,json,hashlib,datetime,collections,re
ROOT=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');P=ROOT/'runs/D037-showdown-cache-resource';OUT=ROOT/'comparisons/D037-independent-review';REPO=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016')
checks=collections.Counter();files={}
def ck(value,label):
 if not value:raise AssertionError(label)
 checks[label]+=1
def sha(p):
 p=pathlib.Path(p);k=str(p)
 if k not in files:files[k]={'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}
 return files[k]['sha256']
def load(p):sha(p);return json.loads(pathlib.Path(p).read_text())
def pin(p,h):ck(sha(p)==h,'artifact_hash')
def fnv(data):
 h=0xcbf29ce484222325
 for b in data:h=((h^b)*0x100000001b3)&0xffffffffffffffff
 return f'{h:016x}'
M=load(P/'prepared-manifest.json');PR=load(P/'protocol.json');X=load(P/'execution-manifest.json');R=load(P/'report.json');A=load(P/'allocation-provenance.json')
pin(P/'prepared-manifest.json','783bce1a84f29c90ef77175e9028898247e9ee4b7f9c8ec76da99c28e6eadf63')
for n,h in M['artifact_sha256'].items():pin(P/n,h)
for d in M['dependency_rlibs'].values():pin(d['path'],d['sha256'])
for n,h in M['protected_checkout_sha256'].items():pin(REPO/n,h)
for n,h in X['nvrtc_dll_sha256'].items():pin(pathlib.Path(X['nvrtc_directory'])/n,h)
ck(X['input_sha256_before']==R['input_sha256_after']==M['artifact_sha256'],'unchanged_all_input_hashes')
for d in [X,R,load(P/'execution-started.json')]:ck(d['prepared_manifest_sha256']==sha(P/'prepared-manifest.json'),'sealed_manifest_link')
pin(P/'probe.exe',R['binary_sha256']);ck(not (P/'failure.json').exists(),'no_failed_attempt')
for n in ['rustc.stdout.log','rustc.stderr.log','probe.stderr.log']:ck((P/n).stat().st_size==0,'empty_success_errorlogs')
cmds=[load(P/'rustc.command.json'),load(P/'probe.command.json')];ck(cmds==R['commands'],'commands_raw_report_equal')
ck(len(cmds)==2 and all(c['returncode']==0 and c['cleanup'] is None and c['timeout_seconds']==600 for c in cmds),'one_compile_one_native_terminal_success')
ck(cmds[0]['args']==X['compile_command'] and cmds[1]['args']==[str(P/'probe.exe')],'exact_compiler_binary_invocations')
ck(datetime.datetime.fromisoformat(cmds[1]['started_at'])>=datetime.datetime.fromisoformat(cmds[0]['started_at'])+datetime.timedelta(seconds=cmds[0]['elapsed_seconds']),'compile_terminal_before_native')
source=(P/'probe.rs').read_text();ck(source.count('CudaContext::new(')==1,'single_context')
ck(not re.search(r'launch_builder|\.launch\s*\(|cuLaunch|LaunchConfig|CudaStream|<<<|set_attribute|set_shared_mem|cuFuncSet',source),'no_launch_or_resource_mutation_api')
ck(source.count('compile_ptx_with_opts(source,CompileOptions {arch:Some(arch),..Default::default()})')==1,'same_arch_only_nvrtc_options')
rows=[]
for line in (P/'probe.stdout.log').read_text().splitlines():
 ck(line.startswith('D037_RESOURCE '),'raw_marker_prefix');rows.append(json.loads(line[len('D037_RESOURCE '):]))
ck(rows==R['records'],'raw_marker_report_equality');ck([x['stage'] for x in rows]==['device']+['resource']*14+['complete'],'exact16_marker_order');ck(rows[-1]==R['complete'],'terminal_complete')
dev=rows[0];ck(dev['device']=='NVIDIA GeForce RTX 5090' and dev['architecture']=='compute_120','actual_device_arch')
ck((dev['max_shared_bytes_per_block_default'],dev['max_shared_bytes_per_block_optin'],dev['max_shared_bytes_per_multiprocessor'],dev['max_threads_per_block'])==(49152,101376,102400,1024),'reported_device_limits')
shapes=M['resource_shapes'];ck(shapes==PR['resource_shapes']==A['resource_shapes'] and len(shapes)==7,'same_prespecified_seven_shapes')
summary=[]
for vi,variant in enumerate(['baseline','candidate']):
 s=(P/(variant+'.cu')).read_bytes();v=M['source_variants'][variant]
 ck(sha(P/(variant+'.cu'))==v['sha256'] and len(s)==v['bytes'] and fnv(s)==v['fnv1a64'],'source_variant_identity')
 for i,shape in enumerate(shapes):
  row=rows[1+vi*7+i];factor=8 if variant=='baseline' else 16;dynamic=4*shape['nh_o']+factor*shape['m_max']
  ck(row['source_variant']==variant and row['shape']==shape['id'],'fixed_shape_variant_order')
  ck(row['nh_o']==shape['nh_o'] and row['max_valid_opponent_hands']==shape['m_max'],'shape_input_counts')
  ck(row['dynamic_shared_bytes']==shape[variant+'_dynamic_bytes']==dynamic,'independent_shared_formula')
  ck(row['static_shared_bytes']==1040 and row['static_plus_dynamic_shared_bytes']==1040+dynamic,'static_dynamic_total')
  ck(row['block_threads']==128 and row['max_threads_per_block']==1024 and row['local_bytes_per_thread']==0 and row['registers']==(40 if variant=='baseline' else 38),'function_resources')
  expected=(5 if variant=='baseline' else 3) if shape['id']=='full_hand_upper_bound' else 12
  ck(row['occupancy_blocks_per_sm_128']==expected and row['occupancy_warps_per_sm_128']==expected*4,'reported_occupancy')
  ck(row['fits_queried_default_shared_and_thread_limits'] and 1040+dynamic<dev['max_shared_bytes_per_block_default'] and expected>0,'screened_resource_feasibility')
  ck(row['source_bytes']==len(s) and row['source_fnv1a64']==v['fnv1a64'],'runtime_cuda_identity')
  ck(row['kernel_launches']==0 and row['solver_executions']==0 and row['numerical_validation']=='not executed' and not row['performance_measurement'],'resource_only_scope')
  summary.append({k:row[k] for k in ['source_variant','shape','shape_scope','nh_o','max_valid_opponent_hands','dynamic_shared_bytes','static_plus_dynamic_shared_bytes','registers','local_bytes_per_thread','occupancy_blocks_per_sm_128']})
ck(not R['candidate_accepted'] and not R['performance_measurement'] and R['kernel_launches']==0 and R['solver_executions']==0 and R['numerical_validation']=='not executed','report_no_numerical_performance_acceptance_claim')
# Shape provenance: closed observed rainbow descriptors and independently anchored river hands.
pin(A['anchor_path'],A['anchor_sha256']);anchor=load(A['anchor_path']);fixtures={x['fixture_id']:x for x in anchor['fixtures']}
ck(fixtures['river']['hands']==A['river_hands']==[233,280] and fixtures['river']['config']['board']==A['river_board']=='Ks7h2dQhTc','river_anchor_counts_board')
ck(fixtures['rainbow']['hands']==[257,319],'rainbow_anchor_counts')
pin(P/'source-game.rs',A['source_game_sha256']);game=(P/'source-game.rs').read_text();ck('2 => vec![Some(eval_board(&[]))]' in game and 'if h.mask & extra_mask != 0' in game,'river_empty_extra_mask_invariant_source')
show=load(P/'source-D033-show-launches.json');oldreport=load(ROOT/'runs/D033R1/report.json');pin(ROOT/'runs/D033R1/stdout.log',oldreport['stdout_sha256'])
graphs=[]
for line in (ROOT/'runs/D033R1/stdout.log').read_text().splitlines():
 if 'D033_EVENT_DIAGNOSTIC ' in line:
  d=json.loads(line.split('D033_EVENT_DIAGNOSTIC ',1)[1])
  if d['stage']=='graph':
   t=d['topology'];graphs.append({'graph':t['graph'],'show_nodes':[x for x in t['kernel_descriptors'] if x['logical']['kernel']=='up_show']})
ck(show['graphs']==graphs,'closed_D033_show_metadata_exact_extraction')
census=load(P/'source-census-summary.json');ck(census['source_anchor_sha256']==sha(A['anchor_path']) and census['base_hands']==fixtures['rainbow']['hands'],'census_anchor_link')
for player in [0,1]:
 row=shapes[player];observed=show['graphs'][player]['show_nodes'];ck(len(observed)==6 and all(x['logical']['shared_bytes']==row['baseline_dynamic_bytes'] and x['logical']['block']==[128,1,1] for x in observed),'observed_rainbow_allocation')
 ck((row['baseline_dynamic_bytes']-4*row['nh_o'])//8==row['m_max']==census['players'][player]['m_o']['max'],'rainbow_max_count_derived_from_observed_bytes')
ck(not A['two_tone_specific_occupancy_queried'],'two_tone_not_claimed')
def entries(text):
 result={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',text):
  beg=text.index('{',m.end());end=beg+1;depth=1
  while depth:depth+=(text[end]=='{')-(text[end]=='}');end+=1
  result[m.group(1)]=text[m.start():end]
 return result
ptx={v:entries((P/(v+'.ptx')).read_text()) for v in ['baseline','candidate']}
ck(set(ptx['baseline'])==set(ptx['candidate']) and len(ptx['baseline'])==9,'same_nine_ptx_entrypoints')
for name in ptx['baseline']:
 if name!='up_show':ck(ptx['baseline'][name]==ptx['candidate'][name] and R['other_entry_ptx_byte_equality'][name],'other_eight_ptx_entries_byte_exact')
for variant in ptx:
 code=ptx[variant]['up_show'];ck(hashlib.sha256(code.encode()).hexdigest()==R['ptx'][variant]['entry_sha256'],'up_show_entry_hash');ck(code+'\n'==(P/(variant+'-up_show.ptx')).read_text(),'saved_entry_excerpt_exact')
for p in P.iterdir():
 if p.is_file():sha(p)
report={'id':'D037-independent-resource-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS bounded no-launch resource/provenance diagnostic; numerical and performance tests remain pending','resource_probe_pass':True,'prepared_manifest_sha256':sha(P/'prepared-manifest.json'),'binary_sha256':sha(P/'probe.exe'),'checks':dict(checks),'check_assertions':sum(checks.values()),'resource_rows':summary,'raw_markers':16,'one_compile_one_native_terminal':True,'zero_launch_source_confirmed':True,'all8_other_ptx_entries_byte_identical':True,'shape_provenance':'Rainbow from exact closed D033 graph-descriptor extraction and immutable hand counts; river from immutable final-board hands and empty-extra-mask invariant;1326 conservative bound and empty/single synthetic shapes. Two-tone-specific occupancy not queried.','wide_shape_risk':{'shape':'full_hand_upper_bound','scope':'conservative1326-count capacity bound, not a real river plan','baseline_blocks_per_sm':5,'candidate_blocks_per_sm':3,'block_occupancy_drop_pct':40.0,'baseline_total_shared_bytes':16952,'candidate_total_shared_bytes':27560,'interpretation':'Material theoretical residency reduction to retain as a wide-range risk; neither a measured runtime regression nor grounds for a speed claim'},'screened_launch_limits':'All recorded128-thread shapes have positive theoretical occupancy and static+dynamic shared bytes below49152 default shared/block; no opt-in mutation needed for these shapes. No actual kernel launch has established runtime success.','source_custody':'All5 protected accepted checkout hashes remain unchanged at audit time; outside-checkout candidate retained separately','execution_durations_not_solver_performance':{'rustc_seconds':cmds[0]['elapsed_seconds'],'probe_process_seconds':cmds[1]['elapsed_seconds']},'limits':['No kernel launches, numerical comparisons, solver solves, speed measurements or acceptance','Static PTX/resources do not prove dynamic savings or unchanged floating-point outputs','Resource-feasible screened shapes permit considering separately reviewed E020 native validation; full correctness/performance and broader range risk remain open'],'actions':'Read-only input analysis and new additive review files; no compiler/GPU/production/status edits','artifacts':files}
with (OUT/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(report,f,indent=2);f.write('\n')
print(json.dumps({'verdict':report['verdict'],'checks':sum(checks.values()),'artifacts':len(files),'validation_sha256':sha(OUT/'validation.json')},indent=2))
