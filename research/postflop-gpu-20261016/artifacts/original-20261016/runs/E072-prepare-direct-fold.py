"""Freeze full raw fold controls on original and shifted card-index spans."""
from pathlib import Path
import copy,json,shutil,sys
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016');sys.path.insert(0,str(R/'runs/accepted-E051-live-20261018'));import common_e051_live as c
c.custody();assert not(R/'gpu-run.lock').exists();H=R/'runs/E072-direct-fold';H.mkdir();ref=R/'runs/E070-direct-kernel-controls/inputs/up-fold'
audit=R/'runs/D117-fold-PTX-audit/report.json';a=c.read(audit);assert a['status']=='pass_static_count_false_positive_audit_admit_raw_numerical_controls'and all(a['amended_prerequisite_gates'].values())and a['source_candidate_unchanged']
for p,h in a['input_sha256'].items():c.pin(p,h)
P0=c.read(ref/'preparation.json')
for name,h in P0['input_sha256'].items():c.pin(ref/name,h)
old=c.read(ref/'corpus.json');corpus=copy.deepcopy(old);scenarios=corpus['full_scenarios'];count=len(scenarios)
for source in old['full_scenarios']:
 s=copy.deepcopy(source);s['id']+='-card-index-base17';s['card_off']=[x+17 for x in s['card_off']];s['card_idx']=[0x4b123456]*17+s['card_idx'];s['card_index_base']=17;scenarios.append(s)
for case in old['cases']:
 v=copy.deepcopy(case);v['id']=len(corpus['cases']);v['scenario_index']+=count;corpus['cases'].append(v)
assert len(corpus['cases'])==360 and len(scenarios)==34
corpus.update(id='E072-fold-raw-controls',case_count=360,kernel_launches_if_executed=720,original_corpus_sha256=c.sha(ref/'corpus.json'),ABI='Identical21arguments, original i32player pointer in both arms. No packed metadata.',coverage_addition='Every original180case is repeated on a distinct span-base17scenario. The new E072kernel is unexecuted before this fixed360case campaign. Cacheprefix/all/fallback,0/127/128/129/1326hand boundaries,count0,own0,bothplayers,16/32/64/128/256threads,finite/overflow nonfinite values,full raw immutable device images and guard words.')
c.save(H/'corpus.json',corpus)
probe=(ref/'probe.rs').read_text(encoding='utf-8').replace('E070','E072').replace('cases.len(),180','cases.len(),360').replace('full_actual_immutable_images":15','full_actual_immutable_images":14')
line='  let attrs:Vec<u16>=owner.iter().map(|&p|{assert!((0..=255).contains(&p));(p as u16)<<8}).collect();\n';assert probe.count(line)==1;probe=probe.replace(line,'')
for old,new in [(',attrs.iter().map(|&x|x as u32).collect()',''),('let dattrs=stream.clone_htod(&attrs).unwrap();',''),('if label=="baseline"{launch.arg(&dp);}else{launch.arg(&dattrs);}','launch.arg(&dp);'),(',stream.clone_dtoh(&dattrs).unwrap().iter().map(|&x|x as u32).collect()','')]:assert probe.count(old)==1;probe=probe.replace(old,new)
assert 'attrs'not in probe and 'cases.len(),360'in probe
with(H/'probe.rs').open('x',encoding='utf-8',newline='\n')as out:out.write(probe)
resource=R/'runs/E072-resource'
for arm in ['baseline','candidate']:shutil.copyfile(resource/'execution'/f'{arm}-compute_120.ptx',H/(arm+'.ptx'))
decoder=(R/'runs/E070-direct-kernel-controls/scripts/audit_raw.py').read_text(encoding='utf-8').replace('E070','E072')
old=', s["cfv_slot"],\n            [m["owner"] << 8 for m in meta]]';assert decoder.count(old)==1;decoder=decoder.replace(old,', s["cfv_slot"]]')
assert decoder.count('fields = 15 if family == "up-fold" else 13')==1;decoder=decoder.replace('fields = 15 if family == "up-fold" else 13','fields = 14 if family == "up-fold" else 13')
compile(decoder,str(H/'audit_raw.py'),'exec')
with(H/'audit_raw.py').open('x',encoding='utf-8',newline='\n')as out:out.write(decoder)
for p in [H/'baseline.ptx',H/'candidate.ptx']:assert c.sha(p)==c.read(resource/'report.json')['ptx_sha256'][p.stem+'-compute_120']
c.save(H/'preparation.json',{'at':c.now(),'status':'source_prepared_no_compile_or_GPU','input_sha256':{p.name:c.sha(p)for p in [H/'corpus.json',H/'probe.rs',H/'baseline.ptx',H/'candidate.ptx']},'candidate_CUDA_sha256':c.sha(R/'runs/E072-source/candidate.cu'),'immutable_device_images_per_case_per_arm':14,'original_packed_metadata_removed':True,'kernel_ABI_unchanged':True,'full_outputs_and_inputs_guards_required':True})
cmd=P0['rustc_command'];cmd=[str(H/'probe.rs')if x==cmd[1]else(str(H/'probe.exe')if x==cmd[-1]else x)for x in cmd]
inputs=[Path(__file__),audit,R/'runs/D117-fold-PTX-audit.py',resource/'report.json',resource/'protocol.json',R/'runs/E072-source/candidate.cu',R/'runs/E072-direct-fold-execute.py',R/'runs/accepted-E051-live-20261018/common_e051_live.py',R/'runs/accepted-E051-live-20261018/protected-main.json',*[p for p in H.iterdir()if p.is_file()]]
pins={str(p):c.sha(p)for p in inputs}
for p,h in c.read(resource/'protocol.json')['input_sha256'].items():
 if '\\build\\release\\deps\\'in p:c.pin(p,h);pins[p]=h
P={'id':'E072-direct-fold','at':c.now(),'status':'FROZEN_PRE_COMPILE_AND_GPU_NUMERICAL','command':cmd,'input_sha256':pins,'cases':360,'kernel_launches':720,'shader_candidate_sha256':c.sha(R/'runs/E072-source/candidate.cu'),'resource_assessment_amendment':{'path':str(audit),'sha256':c.sha(audit)},'original_resource_rejection_preserved':True,'raw_output_directory':str(H/'execution/raw'),'minimum_free_S_bytes':66*1024**3,'peak_output_reservation_bytes':4*1024**3,'rule':'Exactly one compiler and one360case/720launch numerical process. Same PTX modules for all cases. Full actual immutable14buffer images,all output bytes and active/guard classifications exact between baseline/candidate; finite/nonzero outputs required when declared. All native results replayed from raw records. Preserve any failure, no exclusions/extensions/source/cachewidth/threshold variants or numerical retries. No source activation, solver or speed measurement.','scope_limits':'Declared constructed corpus on thisRTX5090, no universal NaNpayload/input/layout or whole-solver/cold-start/speed claim. Broader original/F32/state/save/resume/continuation/material/holdout/cumulative remain required after complete-solve screens.','candidate_accepted':False}
c.save(H/'protocol.json',P);print({'direct_protocol_sha256':c.sha(H/'protocol.json'),'cases':360,'launches':720,'GPU_executions_so_far':0},flush=True)
