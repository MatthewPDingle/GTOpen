import pathlib,json,hashlib,re,datetime,math
R=pathlib.Path(r'S:\GTOpen-research\postflop-gpu-20261016');W=pathlib.Path(r'X:\Dev\GTOpen-gpu-research-20261016');P=R/'runs/D043-opponent-action-resource';O=R/'comparisons/D043-independent-review'
inputs={}
def sha(p):
 p=pathlib.Path(p);v=hashlib.sha256(p.read_bytes()).hexdigest();inputs[str(p)]=v;return v
def rd(p):sha(p);return json.loads(pathlib.Path(p).read_text(encoding='utf-8-sig'))
def pin(p,h):assert sha(p)==h,str(p)
def dt(s):return datetime.datetime.fromisoformat(s.replace('Z','+00:00'))
def fnv(b):
 h=0xcbf29ce484222325
 for c in b:h=((h^c)*0x100000001b3)&0xffffffffffffffff
 return f'{h:016x}'
def entries(p):
 s=p.read_text();out={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',s):
  start=s.index('{',m.end());depth=1;j=start+1
  while depth:depth+=(s[j]=='{')-(s[j]=='}');j+=1
  out[m.group(1)]=s[m.start():j]
 return out
pin(P/'prepared-manifest.json','12ffce1846947e3997f7e43edb2a2fb7161147516b161147c4f94cc874e01ac5')
M=rd(P/'prepared-manifest.json');Q=rd(P/'protocol.json');C=rd(P/'report.json');X=rd(P/'execution-manifest.json');start=rd(P/'execution-started.json');auth=rd(P/'root-execution-review.json')
assert C['prepared_manifest_sha256']==X['prepared_manifest_sha256']==auth['prepared_manifest_sha256']==sha(P/'prepared-manifest.json')
pin(P/'protocol.json',M['protocol_sha256']);assert C['protocol_sha256']==M['protocol_sha256']
for n,h in M['artifact_sha256'].items():pin(P/n,h)
assert X['input_sha256_before']==C['input_sha256_after']==M['artifact_sha256']
for n,v in M['references'].items():pin(v['path'],v['sha256']);pin(P/n,v['sha256'])
for v in M['dependency_rlibs'].values():pin(v['path'],v['sha256']);assert pathlib.Path(v['path']).stat().st_size==v['bytes']
for n,h in X['nvrtc_dll_sha256'].items():pin(pathlib.Path(X['nvrtc_directory'])/n,h)
pin(X['rustc_executable'],X['rustc_executable_sha256']);pin(P/'probe.exe',C['binary_sha256'])
review=R/'comparisons/D043-source-review/report.json';pin(review,auth['source_review_sha256']);pin(R/'runs/D042-zero-proof-diagnostic/cleanup.json',auth['D042_cleanup_sha256'])
assert auth['D042_native_cohort_terminal'] and Q['kernel_launches']==Q['solver_executions']==0
for name in ['baseline','candidate']:
 b=(P/f'{name}.cu').read_bytes();s=M['source_variants'][name];assert len(b)==s['bytes'] and sha(P/f'{name}.cu')==s['sha256'] and fnv(b)==s['fnv1a64']
assert (P/'candidate.cu').read_bytes()==(P/'baseline.cu').read_bytes()+(P/'appended-opponent-entry.cu').read_bytes()
probe=(P/'probe.rs').read_text();assert 'launch_builder(' not in probe and '.launch(' not in probe and 'cuLaunchKernel' not in probe and probe.count('CudaContext::new(')==1
commands=rd(P/'commands.json');rc=rd(P/'rustc.command.json');pc=rd(P/'probe.command.json')
assert C['commands']==[rc,pc] and rc['args']==X['compile_command']==commands['rustc_command_run_by_runner'] and pc['args']==commands['resource_probe_command_run_by_runner']
for c in [rc,pc]:assert c['returncode']==0 and c['cleanup'] is None and c['timeout_seconds']==600 and c['cwd']==str(P)
assert dt(start['at'])<=dt(rc['started_at']) and dt(rc['started_at'])+datetime.timedelta(seconds=rc['elapsed_seconds'])<=dt(pc['started_at'])
assert all((P/n).read_bytes()==b'' for n in ['rustc.stderr.log','rustc.stdout.log','probe.stderr.log'])
lines=(P/'probe.stdout.log').read_text().splitlines();assert len(lines)==5 and all(l.startswith('D043_RESOURCE ') for l in lines)
rows=[json.loads(l.split(' ',1)[1]) for l in lines];assert rows==C['records'] and rows[-1]==C['complete']
assert [v['stage'] for v in rows]==['device','resource','resource','resource','complete']
dev=rows[0];assert dev['device']=='NVIDIA GeForce RTX 5090' and dev['architecture']=='compute_120' and (dev['nvrtc_major'],dev['nvrtc_minor'])==(12,9)
b,control,new=rows[1:4];assert [(v['source_variant'],v['kernel']) for v in rows[1:4]]==[(x['variant'],x['kernel']) for x in Q['resource_rows']]
for v in rows[1:4]:
 source=M['source_variants'][v['source_variant']];assert v['source_bytes']==source['bytes'] and v['source_fnv1a64']==source['fnv1a64'] and v['block_threads']==128 and v['dynamic_shared_bytes']==0
 assert v['kernel_launches']==v['solver_executions']==0 and not v['performance_measurement'] and v['numerical_validation']=='not executed'
 assert v['fits_queried_default_shared_and_thread_limits'] and v['occupancy_warps_per_sm_128']==4*v['occupancy_blocks_per_sm_128']
fields=['registers','local_bytes_per_thread','static_shared_bytes','max_threads_per_block','occupancy_blocks_per_sm_128']
assert [b[k] for k in fields]==[control[k] for k in fields]==[66,64,0,896,7]
assert [new[k] for k in fields]==[40,0,0,1024,12]
reduction=100*(b['registers']-new['registers'])/b['registers'];gate={'zero_local_bytes':new['local_bytes_per_thread']==0,'register_reduction_at_least_25pct':reduction>=Q['resource_prerequisite']['minimum_register_reduction_percent'],'strictly_more_active_blocks_per_sm':new['occupancy_blocks_per_sm_128']>b['occupancy_blocks_per_sm_128'],'supports128threads':new['max_threads_per_block']>=128}
assert gate==C['resource_prerequisite_checks'] and all(gate.values())==C['material_resource_prerequisite_pass'];assert math.isclose(reduction,C['register_reduction_percent'])
base=entries(P/'baseline.ptx');cand=entries(P/'candidate.ptx');assert len(base)==9 and set(cand)==set(base)|{'up_action_opponent'}
same={k:base[k]==cand[k] for k in base};assert all(same.values()) and same==C['original_entry_ptx_byte_equality']
for label,e in [('baseline-up_action',base['up_action']),('candidate-up_action',cand['up_action']),('candidate-up_action_opponent',cand['up_action_opponent'])]:
 assert (P/(label+'.ptx')).read_text()==e+'\n' and hashlib.sha256(e.encode()).hexdigest()==C['ptx'][label]['entry_sha256']
assert '.local ' not in cand['up_action_opponent'] and 'ld.local' not in cand['up_action_opponent'] and 'st.local' not in cand['up_action_opponent']
assert C['kernel_launches']==C['solver_executions']==0 and not C['performance_measurement'] and C['numerical_validation']=='not executed' and not C['candidate_accepted']
assert rows[-1]['resource_rows']==3 and not rows[-1]['candidate_accepted']
protected=M['protected_checkout_sha256'];assert len(protected)==162
assert protected==rd(P/'source-accepted-binary-manifest.json')['source_sha256']
for n,h in protected.items():pin(W/n,h)
for p in P.iterdir():
 if p.is_file():sha(p)
result={'id':'D043-independent-review','at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'verdict':'PASS_COMPILER_RESOURCE_PREREQUISITE_ONLY','raw_markers':5,'resource_rows':3,'device':dev['device'],'architecture':dev['architecture'],'nvrtc_version':[12,9],'original_entry_ptx_exact':same,'original_resources':{k:b[k] for k in fields},'opponent_resources':{k:new[k] for k in fields},'register_reduction_pct':reduction,'prespecified_gate':gate,'resource_gate_pass':all(gate.values()),'commands_terminal':[rc,pc],'all162_checkout_sources_match_accepted_E020':True,'kernel_launches':0,'solver_executions':0,'numerical_proof':False,'performance_claim':False,'allowed_next_step':'Consider one separately authorized production candidate, preserving fixed complete-cycle and exactness qualification; no automatic implementation, acceptance or deployment.','limits':['PTX equality applies to the nine old entries, not runtime proof of the new entry','Theoretical occupancy and local-byte reduction are not measured speed','Host actor partition and routing do not exist in this probe; later full splitting adds20 launches per paired flop iteration and all planning/JIT/capture cost remains in score','E005/E014 and older preflop grouped-opponent regressions remain counterevidence; no gain projection'],'review_actions':'File-only audit; no build, native probe, solver, GPU or checkout edits','input_sha256':inputs}
with (O/'validation.json').open('x',encoding='utf-8',newline='\n') as f:json.dump(result,f,indent=2);f.write('\n')
print(json.dumps({k:result[k] for k in ['verdict','raw_markers','resource_rows','register_reduction_pct','resource_gate_pass','all162_checkout_sources_match_accepted_E020']},indent=2));print(sha(O/'validation.json'))
