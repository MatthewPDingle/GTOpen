import ast,json,shutil,subprocess,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();assert not(ROOT/'gpu-run.lock').exists();h.ar.refuse_active(h.ar.live_status())
S=ROOT/'runs/E104-source';schema=h.read(S/'schema.json');assert schema['original9sourceprefix_exact'] and len(schema['helper_copy_projections'])==8 and all(x['exact_reverse_projection'] for x in schema['helper_copy_projections']);assert schema['frame_bytes']==3008
H=ROOT/'runs/D207-resident-resource';H.mkdir(exist_ok=False);shutil.copyfile(S/'candidate-kernels.cu',H/'candidate.cu');dirs=[];files=[Path(__file__),ROOT/'runs/E104-prepare-source.py',S/'schema.json',S/'source-review.json',S/'baseline-kernels.cu',S/'candidate-kernels.cu',S/'preparer-r1.py',S/'preparation-r1.json',ROOT/'runs/D206-resident-phase-model/protocol.json',ROOT/'runs/D206-resident-phase-model/protocol-r2.json',ROOT/'runs/D206-resident-phase-model/pre-reader-review.json',ROOT/'runs/D206-resident-phase-model/history.json',ROOT/'runs/D206-resident-phase-model/execution/complete.json',ROOT/'comparisons/D206-resident-phase-model/report.json',ROOT/'runs/D205-terminal-checkpoint/report.json',ROOT/'epoch/common.py']
for folder in ['D203-runtime-header-bootstrap','D203-cccl-header-bootstrap']:
 r=ROOT/'runs'/folder;R=h.read(r/'report.json');dirs.append(R['include_directory']);files.extend([r/'protocol.json',r/'report.json'])
 for row in R['selected_files']:
  p=r/'package'/row['path'];h.pin(p,row['sha256']);files.append(p)
(H/'includes.json').write_text(json.dumps(dirs,indent=2),encoding='utf-8',newline='\n')
prior=ROOT/'runs/E102-resource';old=h.read(prior/'report.json')
for arch in ['compute_120','compute_75']:
 p=prior/'execution'/('baseline-'+arch+'.ptx');h.pin(p,old['ptx_sha256']['baseline-'+arch]);shutil.copyfile(p,H/('baseline-'+arch+'.ptx'))
rust='''use cudarc::{driver::{CudaContext,CudaFunction,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
#[repr(C)]struct E104Args{
'''+''.join(' '+x['name']+':u64,\n' for x in schema['pointer_fields'])+''.join(' '+x+':i32,\n' for x in schema['scalar_fields'])+''' spans:[[[u32;2];64];5],
}
#[repr(C)]struct ProposedHostState{function:Option<CudaFunction>,blocks:u32,shared:u32}
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"D207_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 assert_eq!(std::mem::size_of::<E104Args>(),3008);assert_eq!(std::mem::align_of::<E104Args>(),8);assert_eq!(std::mem::offset_of!(E104Args,spans),444);
 let out=PathBuf::from(std::env::args().nth(1).unwrap());let paths:Vec<String>=serde_json::from_str(include_str!("includes.json")).unwrap();let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert_eq!(ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_COOPERATIVE_LAUNCH).unwrap(),1);
 let baseline_wrapper=std::mem::size_of::<solver::gpu::GpuSolver>();let state_bytes=std::mem::size_of::<ProposedHostState>();assert_eq!((baseline_wrapper,state_bytes),(4448,24));
 emit(serde_json::json!({"stage":"typed_layout","parameter_bytes":std::mem::size_of::<E104Args>(),"parameter_alignment":std::mem::align_of::<E104Args>(),"span_offset":std::mem::offset_of!(E104Args,spans),"baseline_host_wrapper_bytes":baseline_wrapper,"proposed_host_state_bytes":state_bytes,"prospective_wrapper_total_bytes":baseline_wrapper+state_bytes,"actual_candidate_host_not_yet_built":true,"application_kernels":0}));
 let old_names=["copy_root","down_action","down_chance","up_fold","up_show","up_chance","up_action","copy_span","up_action_eval"];
 for variant in ["baseline","candidate"]{
  let ptx=if variant=="baseline"{Ptx::from_src(include_str!("baseline-compute_120.ptx"))}else{
   let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_120"),include_paths:paths.clone(),..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_120.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();p
  };
  let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let module=ctx.load_module(ptx).unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let mut names=old_names.to_vec();if variant=="candidate"{names.push("e104_train");}
  for name in names{
   let f=module.load_function(name).unwrap();let dynamic=match name{"up_fold"=>1326*4,"up_show"|"e104_train"=>1326*20,_=>0};let occ=f.occupancy_max_active_blocks_per_multiprocessor(128,dynamic,None).unwrap();
   emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":name,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"dynamic_shared_bytes":dynamic,"max_threads":f.max_threads_per_block().unwrap(),"fixed_block_threads":128,"resident_blocks_per_SM_worst1326":occ,"SM_count":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT).unwrap(),"device_shared_limit":ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"context_stack_before":before,"context_stack_after":after,"application_kernels":0}));
  }
  drop(module);ctx.check_err().unwrap();
 }
 let p=compile_ptx_with_opts(include_str!("candidate.cu"),CompileOptions{arch:Some("compute_75"),include_paths:paths,..Default::default()}).unwrap();let mut f=OpenOptions::new().create_new(true).write(true).open(out.join("candidate-compute_75.ptx")).unwrap();f.write_all(p.to_src().as_bytes()).unwrap();f.sync_all().unwrap();drop(f);ctx.check_err().unwrap();drop(ctx);
 emit(serde_json::json!({"stage":"complete","candidate_compile_variants":2,"reused_baseline_PTX":true,"resource_rows":19,"application_kernels":0,"solver_or_speed_samples":0}));
}
'''
(H/'probe.rs').write_text(rust,encoding='utf-8',newline='\n')
execute='''import json,re,shutil,sys
from pathlib import Path
H=Path(__file__).resolve().parent;ROOT=H.parent.parent;sys.path.insert(0,str(ROOT/'epoch'));import common as h
assert len(sys.argv)==2;P=h.read(H/'protocol.json')
def verify():
 h.pin(H/'protocol.json',sys.argv[1]);h.custody()
 for p,d in P['input_sha256'].items():h.pin(p,d)
def entries(path):
 text=path.read_text();out={}
 for m in re.finditer(r'\\.visible\\s+\\.entry\\s+(\\w+)\\(',text):
  a=text.index('{',m.end());end=a+1;depth=1
  while depth:
   if text[end]=='{':depth+=1
   elif text[end]=='}':depth-=1
   end+=1
  out[m[1]]=text[m.start():end]
 return out
def norm(s):
 s=re.sub(r'\\$L__BB\\d+_(\\d+)',r'$L__BB_FUNCTION_\\1',s);s=re.sub(r'__local_depot\\d+','__local_depot_FUNCTION',s);return re.sub(r'\\$L__func_(begin|end)\\d+',r'$L__func_\\1_FUNCTION',s)
verify();O=H/'execution';O.mkdir(exist_ok=False)
with h.ar.exclusive_lock(ROOT/'gpu-run.lock'):
 h.ar.refuse_active(h.ar.live_status());assert shutil.disk_usage(ROOT).free>=P['required_free_bytes'];h.child(P['rustc_command'],O,'rustc',600);verify();h.save(O/'binary.json',{'sha256':h.sha(H/'probe.exe')});h.child([str(H/'probe.exe'),str(O)],O,'probe',600);verify()
markers=[json.loads(x.split('D207_RESOURCE ',1)[1]) for x in (O/'probe.stdout.log').read_text().splitlines() if 'D207_RESOURCE ' in x];assert len(markers)==21 and markers[0]['stage']=='typed_layout' and markers[-1]['stage']=='complete';rows={(x['variant'],x['kernel']):x for x in markers[1:-1]};assert len(rows)==19
gates={};comparisons={};headers={}
for arch in ['compute_120','compute_75']:
 b=entries(H/('baseline-'+arch+'.ptx'));c=entries(O/('candidate-'+arch+'.ptx'));assert set(b)==set(P['original_entries']) and set(c)==set(b)|{'e104_train'}
 comparisons[arch]={name:norm(b[name])==norm(c[name]) for name in b};gates[arch+':original9entries_exact']=all(comparisons[arch].values());header=c['e104_train'].split('{',1)[0];headers[arch]=header;gates[arch+':one3008byte_aligned_parameter']=header.count('.param ')==1 and bool(re.search(r'\\.align\\s+8\\s+\\.b8\\s+\\w+\\[3008\\]',header))
oldkeys=['registers','local_bytes_per_thread','static_shared_bytes','dynamic_shared_bytes','max_threads','resident_blocks_per_SM_worst1326','context_stack_before','context_stack_after']
gates['original9_actual_resources_exact']=all(all(rows['baseline',name][k]==rows['candidate',name][k] for k in oldkeys) for name in P['original_entries'])
r=rows['candidate','e104_train'];gates.update({'no_local_beyond_original_training_max64':r['local_bytes_per_thread']<=64,'fixed128_supported':r['max_threads']>=128,'fits_default_worst_shared':r['static_shared_bytes']+r['dynamic_shared_bytes']<=r['device_shared_limit'],'positive_fixed128_worst_occupancy':r['resident_blocks_per_SM_worst1326']>0,'no_default_stack_growth':r['context_stack_after']<=r['context_stack_before'],'exact_typed_frame':markers[0]['parameter_bytes']==3008 and markers[0]['parameter_alignment']==8 and markers[0]['span_offset']==444,'prospective_host_state_le32bytes':markers[0]['proposed_host_state_bytes']<=32})
passed=all(gates.values());h.save(H/'report.json',{'id':'D207','at':h.now(),'status':'pass_resident_shader_compiler_resource_prerequisites' if passed else 'closed_resident_shader_compiler_resource_prerequisite_failure','protocol_sha256':sys.argv[1],'gates':gates,'original_entry_comparisons':comparisons,'new_entry_headers':headers,'resource_rows':list(rows.values()),'typed_layout':markers[0],'candidate_PTX_sha256':{a:h.sha(O/('candidate-'+a+'.ptx')) for a in ['compute_120','compute_75']},'all_owned_compiler_native_children_terminal':True,'application_kernels':0,'solver_or_speed_samples':0,'candidate_accepted':False,'scope':'Shader-only compilation/typed3008Bframe andactualresources. Hostintegrationnotbuilt. Fusedregs/shared/residencycostsreported, not dismissed; eligibility basedactualfusedentry needed. No FP/raw/barrier/fullsolver/material/capacity/performanceadmission from pass. Exactform closeson genuinefailure,no helper/width/gridthreshold/source/flags/sample rescue.'});h.save(O/'complete.json',{'at':h.now(),'all_owned_children_terminal':True,'report_sha256':h.sha(H/'report.json'),'application_kernels':0});verify();print(json.dumps({'status':'pass' if passed else 'closed','failed_gates':[k for k,v in gates.items() if not v],'fused_resources':r,'typed_layout':markers[0]}),flush=True)
'''
ast.parse(execute);(H/'execute.py').write_text(execute,encoding='utf-8',newline='\n')
deps=ROOT/'reference/accepted-e080-deps';cmd=['rustc',str(H/'probe.rs'),'--edition=2021','-C','opt-level=3','-C','codegen-units=1','-C','lto=thin','-L','dependency='+str(deps)]
for name,file in [('solver','libsolver-e2d3113d740308c1.rlib'),('cudarc','libcudarc-ba3140064b5903a3.rlib'),('serde_json','libserde_json-83a0670a02a34a4d.rlib')]:cmd+=['--extern',name+'='+str(deps/file)]
cmd+=['-o',str(H/'probe.exe')];files += [p for p in H.iterdir() if p.is_file()]+[p for p in deps.iterdir() if p.is_file()]
original=['copy_root','down_action','down_chance','up_fold','up_show','up_chance','up_action','copy_span','up_action_eval']
h.save(H/'protocol.json',{'id':'D207','at':h.now(),'status':'FROZEN_PRE_RESIDENT_SHADER_COMPILER_AND_MODULE_ONLY_PROCESS','rustc_command':cmd,'original_entries':original,'required_free_bytes':64*1024**3,'input_sha256':{str(p):h.sha(p) for p in files},'scope':'ExactlyoneRustcompiler/oneprivateGPUmodule-onlyhelper,2newNVRTC12.9candidate120/75withonlyfrozenvendorinclude_paths,originalbaselinePTXreusednotrecompiled. Sourceoriginal9prefixexact,new8helpercopiesprojectionexact,newcooperativetrainentry. Nohostsourceactivation orapplicationkernels.','fixed_gates':'Original9normalizedPTX/ABIandactualresourcesexact;newoneparamalign8/3008BmatchesRustCframeoffset444. Actual128threads/maxthread/defaultsharedworst26520/positiveoccupancy/stackunchanged,localbytes<=64originalmax. ProposedhoststateOptionfunction+2u32size<=32isdeclaredcostonly,actualhostbuildsizeof/capacitystillrequired. Recordallfusedregister/shared/residency/codemodule/JITcosts withoutneutralityclaim.','failure':'Any genuineABI/entry/resourcefailureclosesexact128/cooperative/fulltraining/frame/eligibility/phase/helper/grid/flag/sourceformwithoutrescue. Mechanicalpre-appcompileradaptererrorsretainedandseparatelyrepairablebeforedependentmeasurements. Noappkernels/fullsolver/gainadmitted bypass; allraw/ordinary/complete1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative/applicationgatesremain.'})
evidence=[]
for folder,names in [(ROOT/'runs/D206-resident-phase-model',['protocol.json','protocol-r2.json','history.json','pre-reader-review.json']),(ROOT/'comparisons/D206-resident-phase-model',['report.json']),(S,['schema.json','source-review.json','preparation-r1.json']),(H,['protocol.json'])]:
 for name in names:
  p=folder/name;key=folder.relative_to(ROOT).as_posix()+'/'+name;dst=h.ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True)
  if dst.exists():assert dst.read_bytes()==p.read_bytes()
  else:shutil.copyfile(p,dst)
  with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+key,timeout=20) as response:assert response.read()==p.read_bytes()
  evidence.append({'label':folder.name+' '+name,'url':'evidence/'+key})
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D206','title':'Resident traversal complete original phase ownership model','kind':'diagnostic','status':'measured','accepted':False,'measurement_epoch':'RAM20261028','stage':'All6original plans/3.8Mstructuralchecks passed','reason':'Alloriginalflatphaseworklists/CFV/reach/learningintervalownership and3wholeactualGPUchildframes checked;allphasesinput/outputdisjoint. CTAbarrierrequiredaftereachhelperbefore scratchreuse. No newnative/CUDA or timing.','evidence':evidence[:5]});s['experiments'].append({'id':'E104','title':'Resident cooperative training traversal shader prototype','kind':'candidate','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'OfftreeCFRshader;hostintegrationandallrawpending','correctness':'integer_model_and_helper_source_projection_only','reason':'Original9CUDAprefixand8helperreverseprojections exact; explicitworkindex/CTAbarrier/phasegridbarriers,52pointer/3008Bimmutableframe. NewCFRnumerics/resources/speedstillunproven.','evidence':evidence[5:8]});s['experiments'].append({'id':'D207','title':'Resident training shader typed ABI and compiler resources','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Frozen2targetNVRTCandactualmodule/resourcegate','reason':'Original9PTX/resourcesmustexact,new3008Bframe/defaultlimits/local<=64/positive128occupancy. Noapplicationkernels,sourceactivationorgain.','evidence':evidence[8:]});s.update(updated_at=h.now(),active_experiment='D207',stage='Resident training compiler/resource prerequisite',activity='6planownershipmodelpassed3,795,605checks. OneofftreeE104shaderpreserveshelperarithmeticandphaseorder;compile/resourcegatebeforeanyCFRGPUexecution. E080/16/defaultaffinity stayslive.');h.ar.atomic_json(h.ar.STATUS,s)
ledger=h.REPO/'research/postflop-gpu-20261016/experiments.md'
with ledger.open('a',encoding='utf-8',newline='\n') as f:f.write('\n\n### D206 original phase ownership and E104 resident shader/D207 gate\n\nPreviousgoalturnprogressedD202actualsupport,D203privatevendorheaders,D204compile/resources,D205256fullrawbarrier/graphcases;allchildren terminal,no speedgainclaimed. Currentcustody/idle/locksverified. D206 hashesall6originalD183metadatafilesand3actualD201GPUchildframes.3,795,605structuralchecks pass: originalphasepartition/levelspans,actorreach/flat chanceoutputuniqueowners/inputdisjointness,CFVoutput/inputdisjointness,childadjacencylevels,persistentlearningintervals/bounds/signeddomains. Originalnonemptyphasecounts62/62/26(on) and62/62/26(off),countsnotheadroom. D183timingsexcluded. Pre-readerLevelSpanstructcountparserfixretainedbeforeanymodelinputread,nooutcomechange.\n\nE104shaderonlysource b2d85e584258e2791ded758284541e42defb34e1318e2b1f7d25bbb2c19a8f13 retainsoriginal9CUDAbyteprefixand8helperbodyexactreverseprojections. Appendedhelpercopieschangeonlydeviceinline linkage/explicitwholeworkindex/templateforwarding. Persistentglobal128threadCTAgrid-stridesoriginalnode/flat-edgework,CTAbarrieraftereachitem beforeblockscratchreuse,all-gridbarrierafteroriginalnonemptyphases;uniformphaseconditions andhelperreturnsstaywithinwrapper. Originalphase/math/arity/locks/p1reuseandall evaluation/rootcopy/quality unchanged. Pre-freezesignatureparsercommentparenthesiserrorretained,correctedbeforecandidatecompile. No application/kernel/numerical/speedclaim.\n\n52pointer/7i32/5x64spanimmutable __grid_constant__frame3008Balign8,spanoffset444;NVIDIAprimaryparameterdocsrecorded. ProposedhostOptionfunction+grid/shared24B/<=32declaredbeforeoutcome,actualhostintegration/wrappersize/capacitynotyetbuilt; no numericfieldexceptionorpostobservedD197waiver. Fixedlatereligibility128/<=64levels/actualcoopsupport/defaultlimits/largestphase>=SM;grid=min(largestphase,actualresident*SM),originalfallbackbeforeworkandprofiling. Newgraphargument/stack/module/header/JIT/register/shared/local costsrealandmustqualify.\n\nD207 freezesoneRustcompiler/module-onlyprocess,2candidateNVRTC12.9target120/75withfrozenvendorheaders;originalbaselinePTXreused. Original9normalizedPTX/ABI/actualresourcesmustexact,newone3008BparammatchesRustCframe,local<=64(originaltrainingmax),defaultsharedworst26520plusstatic,128supported/positiveoccupancy,stackunchanged. Reportfusedresourcewarnings,nophysicalneutralityorheadroomclaim. Anygenuinefailureclosesexactformwithouthelper/grid/width/threshold/flags/source/sample rescue. AllCFRraw/ordinary/full1%strictfixture/fresh16/broad/material/capacity/holdout/cumulative/applicationgatesremain;no productionactivation.\n')
subprocess.run(['git','add','--','research/postflop-gpu-20261016/experiments.md'],cwd=h.REPO,check=True);subprocess.run(['git','commit','-m','research: freeze resident training shader after full phase ownership proof'],cwd=h.REPO,check=True)
print(h.sha(H/'protocol.json'),flush=True)
