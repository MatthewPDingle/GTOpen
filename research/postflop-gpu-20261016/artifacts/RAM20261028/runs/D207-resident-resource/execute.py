import json,re,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
 text=path.read_text();out={}
 for m in re.finditer(r'\.visible\s+\.entry\s+(\w+)\(',text):
  a=text.index('{',m.end());end=a+1;depth=1
  while depth:
   if text[end]=='{':depth+=1
   elif text[end]=='}':depth-=1
   end+=1
  out[m[1]]=text[m.start():end]
 return out
def norm(s):
 s=re.sub(r'\$L__BB\d+_(\d+)',r'$L__BB_FUNCTION_\1',s);s=re.sub(r'__local_depot\d+','__local_depot_FUNCTION',s);return re.sub(r'\$L__func_(begin|end)\d+',r'$L__func_\1_FUNCTION',s)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('D207_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text().splitlines() if 'D207_RESOURCE ' in x];assert len(markers)==21 and markers[0]['stage']=='typed_layout' and markers[-1]['stage']=='complete';rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==19
gates={};comparisons={};headers={}
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));assert set(b)==set(P['original_entries']) and set(c)==set(b)|{'e104_train'}
 comparisons[arch]={name:norm(b[name])==norm(c[name]) for name in b};gates[arch+':original9entries_exact']=all(comparisons[arch].values());header=c['e104_train'].split('{',1)[0];headers[arch]=header;gates[arch+':one3008byte_aligned_parameter']=header.count('.param ')==1 and bool(re.search(r'\.align\s+8\s+\.b8\s+\w+\[3008\]',header))
oldkeys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','resident_blocks_per_SM_worst1326','context_stack_before','context_stack_after']
gates['original9_actual_resources_exact']=all(all(rows['baseline',name][k]==rows['candidate',name][k] for k in oldkeys) for name in P['original_entries'])
r=rows['candidate','e104_train'];gates.update({'no_local_beyond_original_training_max64':r['local_bytes_per_thread']<=64,'fixed128_supported':r['max_threads']>=128,'fits_default_worst_shared':r['static_shared_bytes']+r['dynamic_shared_bytes']<=r['device_shared_limit'],'positive_fixed128_worst_occupancy':r['resident_blocks_per_SM_worst1326']>0,'no_default_stack_growth':r['context_stack_after']<=r['context_stack_before'],'exact_typed_frame':markers[0]['parameter_bytes']==3008 and markers[0]['parameter_alignment']==8 and markers[0]['span_offset']==444,'prospective_host_state_le32bytes':markers[0]['proposed_host_state_bytes']<=32})
passed=all(gates.values());h.save(H/'report.json',{'id':'D207','at':h.now(),'status':'pass_resident_shader_compiler_resource_prerequisites' if passed else 'closed_resident_shader_compiler_resource_prerequisite_failure','protocol_sha256':sys.argv[1],'gates':gates,'original_entry_comparisons':comparisons,'new_entry_headers':headers,'resource_rows':list(rows.values()),'typed_layout':markers[0],'candidate_PTX_sha256':{a:h.sha(O/('candidate-'+a+'.ptx')) for a in ['compute_120','compute_75']},'all_owned_compiler_native_children_terminal':True,'application_kernels':0,'solver_or_speed_samples':0,'candidate_accepted':False,'scope':'Shader-only compilation/typed3008Bframe andactualresources. Hostintegrationnotbuilt. Fusedregs/shared/residencycostsreported, not dismissed; eligibility basedactualfusedentry needed. No FP/raw/barrier/fullsolver/material/capacity/performanceadmission from pass. Exactform closeson genuinefailure,no helper/width/gridthreshold/source/flags/sample rescue.'});h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'application_kernels':0});verify();print(json.dumps({'status':'pass' if passed else 'closed','failed_gates':[k for k,v in gates.items() if not v],'fused_resources':r,'typed_layout':markers[0]}),flush=True)
