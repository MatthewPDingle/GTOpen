"""Freeze one asynchronous showdown staging design and a no-launch resource screen."""
import difflib,json,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/small-gain-confirmation-plan'));import common as old
ar=old.ar;old.custody();ar.refuse_active(ar.live_status());assert not (ROOT/'gpu-run.lock').exists()
D=ROOT/'runs/E050-source';D.mkdir();path=old.REPO/'crates/solver/src/gpu/kernels.cu';base=path.read_text(encoding='utf-8')
start=base.index('extern "C" __global__ void up_show(');end=base.index('// Up sweep, chance nodes:',start)
body=base[start:end];candidate_body=body.replace('    extern __shared__ char shraw[];','''#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 800
    extern __shared__ __align__(4) char shraw[];
#else
    extern __shared__ char shraw[];
#endif''',1)
loads='''    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) ro_sh[j] = ro_g[j];
    for (int j = threadIdx.x; j < 2 * m_o; j += blockDim.x)
        card_pos_sh[j] = o_card_pos[card_base + j];'''
zero='''    // zero my full cfv span (hands missing from this river's sorted list stay 0)
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;'''
assert candidate_body.count(loads)==candidate_body.count(zero)==1
async_copy='''#if defined(__CUDA_ARCH__) && __CUDA_ARCH__ >= 800
    // Copy exact words to disjoint, four-byte-aligned shared destinations.
    // Complete every issuing thread's copies before the block-wide barrier.
    for (int j = threadIdx.x; j < nh_o; j += blockDim.x) {
        u32 dst = (u32)__cvta_generic_to_shared(ro_sh + j);
        asm volatile("cp.async.ca.shared.global [%0], [%1], 4;"
            :: "r"(dst), "l"(ro_g + j) : "memory");
    }
    for (int j = threadIdx.x; j < 2 * m_o; j += blockDim.x) {
        u32 dst = (u32)__cvta_generic_to_shared(card_pos_sh + j);
        asm volatile("cp.async.ca.shared.global [%0], [%1], 4;"
            :: "r"(dst), "l"(o_card_pos + card_base + j) : "memory");
    }
    // This output clear is independent of the pending input copies. All
    // terminal rows are disjoint and present hands are overwritten later.
    for (int i = threadIdx.x; i < nh_p; i += blockDim.x)
        cfv[(u64)cfv_slot[n] * nh_max + i] = 0.f;
    asm volatile("cp.async.wait_all;" ::: "memory");
#else
'''+loads+'''
#endif'''
candidate_body=candidate_body.replace(loads,async_copy,1)
candidate_body=candidate_body.replace(zero,'#if !defined(__CUDA_ARCH__) || __CUDA_ARCH__ < 800\n'+zero+'\n#endif',1)
candidate=base[:start]+candidate_body+base[end:]
assert candidate[:start]==base[:start] and candidate[candidate.index('// Up sweep, chance nodes:'):]==base[end:]
(D/'baseline.cu').write_bytes(path.read_bytes());(D/'candidate.cu').write_bytes(candidate.replace('\n','\r\n').encode('utf-8'))
(D/'candidate.patch').write_text(''.join(difflib.unified_diff(base.splitlines(True),candidate.splitlines(True),fromfile='crates/solver/src/gpu/kernels.cu',tofile='crates/solver/src/gpu/kernels.cu')),encoding='utf-8')
review={'id':'D081-showdown-async-staging-source','at':old.now(),'root_source_review_only':True,'proposal':'One fixed4-byte cp.async.ca global-to-shared staging on sm80+, overlapping the existing full output zero fill, wait_all plus original CTA barrier before any shared read. Original old-architecture path retained.','scope':'up_show only, same ABI/shape/shared byte count/arrays/float expressions and exact reduction and correction order. No host/plan/evaluator change.','safety':['Global f32/u32 buffers and all offsets are4byte aligned. Dynamic shared base explicitly aligned4, all offsets multiples4.','Thread-strided j destinations are unique within each array. Reach and card-position arrays occupy disjoint ranges. No shared source is read before per-thread wait_all and original block barrier.','Full CFV clear moves before the first barrier only onsm80+. Terminal CFV rows are owned separately by the existing planner; up_show reads no CFV data. Present outputs are written after existing later CTA barriers.','Zero/empty and tail cases issue no out-of-bounds loads. Each thread waits its own copies; uniform CTA barrier publishes all completed results.','Inline asm volatile memory clobbers prevent unmodelled hidden-memory optimization across copy/wait boundaries. No extra atomic/event/buffer or floating reassociation.'],'evidence_limits':['Prior up_show host/device traces are perturbed family envelopes, not a removable-work bound or performance prediction.','Actual compiled attributes, old-architecture fallback PTX, raw poisoned-input/full-output controls and complete-cycle timings remain prerequisites.','No variant/width/cache-qualifier sweep after resource or timing outcome.'],'references':[{'title':'NVIDIA PTX8.8 non-bulk cp.async and completion','url':'https://docs.nvidia.com/cuda/archive/12.9.1/parallel-thread-execution/index.html#data-movement-and-conversion-instructions-cp-async'},{'title':'NVIDIA CUDA12.9 inline assembly memory clobbers','url':'https://docs.nvidia.com/cuda/archive/12.9.1/inline-ptx-assembly/index.html#incorrect-optimization'}],'novelty':'No cp.async/pipeline_memcpy/shared async staging hit in scoped retained postflop patches/reviews/README/ledger. Distinct from E031 extra shared card-offset cache and E008 scan recurrence rewrite; neither is composed here.','source_sha256':{'baseline':old.sha(D/'baseline.cu'),'candidate':old.sha(D/'candidate.cu')},'candidate_accepted':False}
old.save(D/'source-review.json',review)
old.save(D/'manifest.json',{'id':'E050','at':old.now(),'owned':{'crates/solver/src/gpu/kernels.cu':{'base':str(D/'baseline.cu'),'base_sha256':old.sha(D/'baseline.cu'),'candidate':str(D/'candidate.cu'),'candidate_sha256':old.sha(D/'candidate.cu')}},'source_review_sha256':old.sha(D/'source-review.json'),'production_activated':False,'compiler_native_gpu_runs':0})
H=ROOT/'runs/E050-resource';H.mkdir()
for n in ['baseline.cu','candidate.cu']:(H/n).write_bytes((D/n).read_bytes())
probe=r'''use cudarc::{driver::{CudaContext,sys::CUdevice_attribute as Attr},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write};
fn emit(v:serde_json::Value){let mut o=std::io::stdout().lock();writeln!(o,"E050_RESOURCE {v}").unwrap();o.flush().unwrap();}
fn main(){
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
 let (major,minor)=ctx.compute_capability().unwrap();assert_eq!((major,minor),(12,0));
 let actual:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
 let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
 let block_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
 emit(serde_json::json!({"stage":"device","device":ctx.name().unwrap(),"architecture":actual,"shared_limit":shared_limit,"block_limit":block_limit,"kernel_launches":0}));
 let shapes=[("rainbow_p0",319u32,314u32),("rainbow_p1",257,252),("two_tone_p0",320,315),("two_tone_p1",258,253),("river_p0",280,280),("river_p1",233,233),("wide_turn",1128,1081),("full_hand_upper_bound",1326,1326),("empty_sorted_opponent",319,0),("single_sorted_opponent",319,1)];
 for arch in [actual,"compute_75"] {
  for (variant,source) in [("baseline",include_str!("baseline.cu")),("candidate",include_str!("candidate.cu"))]{
   let ptx=compile_ptx_with_opts(source,CompileOptions{arch:Some(arch),..Default::default()}).unwrap();
   let mut file=OpenOptions::new().create_new(true).write(true).open(format!("{variant}-{arch}.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.flush().unwrap();file.sync_all().unwrap();drop(file);
   if arch==actual {
    let module=ctx.load_module(ptx).unwrap();let f=module.load_function("up_show").unwrap();
    let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
    for (shape,nh_o,m) in shapes {
     let dynamic=4*nh_o+16*m;
     let occupancy:Vec<_>=[64u32,128,256].into_iter().map(|t|(t,f.occupancy_max_active_blocks_per_multiprocessor(t,dynamic as usize,None).unwrap())).collect();
     emit(serde_json::json!({"stage":"resource","variant":variant,"kernel":"up_show","shape":shape,"registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":dynamic,"max_threads":max_threads,"actual_block_threads":128,"occupancy_by_threads":occupancy,"fits_default_limits":shared+dynamic as i32<=shared_limit&&max_threads>=128&&block_limit>=128,"kernel_launches":0,"performance_measurement":false}));
    }
    drop(f);drop(module);ctx.check_err().unwrap();
   }
  }
 }
 ctx.check_err().unwrap();emit(serde_json::json!({"stage":"complete","resource_rows":20,"compile_variants":4,"kernel_launches":0,"solver_executions":0,"performance_measurement":false,"candidate_accepted":false}));
}
'''
(H/'probe.rs').write_text(probe,encoding='utf-8')
template=ROOT/'runs/E048-resource'
script=(template/'execute.py').read_text(encoding='utf-8').replace('E048','E050')
a=script.index(" assert len(markers)==6");z=script.index(" report={",a)
script=script[:a]+''' assert len(markers)==22 and markers[0]['stage']=='device' and markers[-1]['stage']=='complete'
 rows={(x['variant'],x['shape']):x for x in markers[1:-1]};assert len(rows)==20
 actual='compute_120'
 be,ce=entries(OUT/f'baseline-{actual}.ptx'),entries(OUT/f'candidate-{actual}.ptx')
 bf,cf=entries(OUT/'baseline-compute_75.ptx'),entries(OUT/'candidate-compute_75.ptx')
 assert set(be)==set(ce)==set(bf)==set(cf)==set(P['expected_entries'])
 unchanged=[k for k in be if be[k]==ce[k]]
 gates={'other8_entries_exact':set(unchanged)==set(be)-{'up_show'},'all9_sm75_fallback_entries_exact':bf==cf,'async_copies_emitted':ce['up_show'].count('cp.async.ca.shared.global')==2 and 'cp.async.wait_all;' in ce['up_show'],'fallback_has_no_async':all('cp.async.' not in text for text in cf.values())}
 details={};abi={}
 for shape in P['shapes']:
  b,c=rows['baseline',shape],rows['candidate',shape]
  kg={'registers_not_increased':c['registers']<=b['registers'],'local_not_increased':c['local_bytes_per_thread']<=b['local_bytes_per_thread'],'static_shared_not_increased':c['static_shared_bytes']<=b['static_shared_bytes'],'dynamic_shared_exact':c['dynamic_shared_bytes']==b['dynamic_shared_bytes'],'max_threads_not_reduced':c['max_threads']>=b['max_threads'],'fits_default_limits':b['fits_default_limits'] and c['fits_default_limits'],'occupancy_not_reduced':all(bt==ct and cn>=bn for (bt,bn),(ct,cn) in zip(b['occupancy_by_threads'],c['occupancy_by_threads'])) and len(c['occupancy_by_threads'])==3}
  details[shape]={'baseline':b,'candidate':c,'gates':kg};gates.update({shape+':'+k:v for k,v in kg.items()})
 def signature(text):
  return re.findall(r'\\.param\\s+\\.(u[0-9]+)((?:\\s+\\.ptr\\s+\\.align\\s+[0-9]+)?)\\s+up_show_param_([0-9]+)',text.split('{',1)[0])
 abi={'baseline':signature(be['up_show']),'candidate':signature(ce['up_show'])}
 gates['abi_exact']=abi['baseline']==abi['candidate'] and len(abi['baseline'])==P['up_show_parameter_count']
''' +script[z:]
script=script.replace("old.sha(OUT/(v+'.ptx'))","old.sha(OUT/(v+'-compute_120.ptx'))")
(H/'execute.py').write_text(script,encoding='utf-8')
prior=old.read(template/'protocol.json')
parameter_count=len(body.split('{',1)[0].split('(',1)[1].split(')',1)[0].split(','))
assert parameter_count==27
p={'id':'E050-resource','at':old.now(),'status':'FROZEN_PRE_EXECUTION_NO_LAUNCH','source_manifest_sha256':old.sha(D/'manifest.json'),'changed_entries':['up_show'],'shapes':['rainbow_p0','rainbow_p1','two_tone_p0','two_tone_p1','river_p0','river_p1','wide_turn','full_hand_upper_bound','empty_sorted_opponent','single_sorted_opponent'],'up_show_parameter_count':parameter_count,'gpu_uuid':prior['gpu_uuid'],'expected_entries':prior['expected_entries']}
p['rustc_command']=[x.replace('E048-resource','E050-resource') for x in prior['rustc_command']]
p['input_sha256']={k:v for k,v in prior['input_sha256'].items() if Path(k).suffix in ['.rlib','.lib'] or Path(k).name in ['common.py','postflop_autoresearch.py','protected-main.json']}
p['input_sha256'].update({str(x):old.sha(x) for x in [H/'execute.py',H/'probe.rs',H/'baseline.cu',H/'candidate.cu',D/'manifest.json',D/'source-review.json']})
p['fixed_gates']='No register/local/static/dynamic increase, no maxthreads/occupancy loss at all10dynamic shapes and64/128/256threads; exact ABI, other8entries, entire9entry sm75fallback and emitted4byte async with wait_all. No launch or performance work if any gate fails. No variant rescue.'
old.save(H/'protocol.json',p)
published={}
for directory in [D,H]:
 for src in directory.rglob('*'):
  if not src.is_file():continue
  key=directory.name+'/'+src.relative_to(directory).as_posix();dst=ar.DASHBOARD/'evidence'/key;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();dst.write_bytes(src.read_bytes())
  with urllib.request.urlopen('http://127.0.0.1:43735/research/postflop-gpu-20261016/evidence/'+key,timeout=15) as response:assert response.read()==src.read_bytes()
  published[key]=old.sha(src)
old.save(H/'pre-execution-publication.json',{'at':old.now(),'http_verified_files':len(published),'artifact_sha256':published})
with ar.exclusive_lock(ar.STATUS.with_suffix('.lock'),timeout=3):
 st=old.read(ar.STATUS);assert not any(x['id']=='E050' for x in st['experiments']);st['experiments'].append({'id':'E050','kind':'candidate','title':'Asynchronous exact-word showdown staging','status':'running','stage':'Frozen no-launch compiler/resource gate','reason':'One4byte async copy design; original float/reduction order and pre-sm80 path preserved. No register/shared/occupancy increase allowed. No performance claim.','evidence':[{'label':'D081/E050 source review','url':'evidence/E050-source/source-review.json'},{'label':'E050 resource protocol','url':'evidence/E050-resource/protocol.json'}]});st.update(state='running',stage='E050 compiler/resource prerequisite',activity='Exact4byte async input copies may overlap existing output clear. No numerical or timing run yet.',updated_at=ar.now());ar.atomic_json(ar.STATUS,st)
old.custody();print(json.dumps({'candidate_sha256':old.sha(D/'candidate.cu'),'resource_protocol_sha256':old.sha(H/'protocol.json'),'published':len(published)}),flush=True)
