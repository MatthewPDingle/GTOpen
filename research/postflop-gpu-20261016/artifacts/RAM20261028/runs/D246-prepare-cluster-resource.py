import ast,json,shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
h.custody();h.ar.refuse_active(h.ar.live_status());assert not(ROOT/'gpu-run.lock').exists();q=h.read(ROOT/'runs/D245-cluster-capability/report.json');assert q['attributes']['CLUSTER_LAUNCH']==1 and q['all_queries_successful']
H=ROOT/'runs/D246-cluster-resource';H.mkdir(exist_ok=False);parent=ROOT/'runs/D204-cooperative-resource';shutil.copyfile(parent/'includes.json',H/'includes.json')
cuda='''#include <cooperative_groups.h>
namespace cg = cooperative_groups;
typedef unsigned int u32;
extern "C" __global__ void __cluster_dims__(2, 1, 1) d246_cluster_transport(
    const u32* __restrict__ source, u32* output, u32 n, u32 base)
{
    extern __shared__ u32 scratch[];
    cg::cluster_group cluster = cg::this_cluster();
    const u32 block = blockIdx.x;
    const u32 rank = cluster.block_rank();
    for (u32 i = threadIdx.x; i < n; i += blockDim.x)
        scratch[i] = source[(unsigned long long)base + (unsigned long long)block * n + i];
    cluster.sync();
    u32* peer = cluster.map_shared_rank(scratch, rank ^ 1u);
    for (u32 i = threadIdx.x; i < n; i += blockDim.x)
        output[(unsigned long long)base + (unsigned long long)block * n + i] = peer[i];
    // All remote readers finish before any producer block can exit.
    cluster.sync();
}
'''
(H/'primitive.cu').write_bytes(cuda.encode('utf-8'))
rust='''use cudarc::{driver::{CudaContext,LaunchConfig,sys::{CUdevice_attribute as DA,CUfunction_attribute_enum as FA}},nvrtc::{compile_ptx_with_opts,CompileOptions}};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn emit(v:serde_json::Value){println!("D246_RESOURCE {v}");std::io::stdout().flush().unwrap();}
fn main(){let out=PathBuf::from(std::env::args().nth(1).unwrap());let paths:Vec<String>=serde_json::from_str(include_str!("includes.json")).unwrap();
 let ptx=compile_ptx_with_opts(include_str!("primitive.cu"),CompileOptions{arch:Some("compute_120"),include_paths:paths,..Default::default()}).unwrap();let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("primitive-compute_120.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.sync_all().unwrap();
 let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));assert_eq!(ctx.attribute(DA::CU_DEVICE_ATTRIBUTE_CLUSTER_LAUNCH).unwrap(),1);let stream=ctx.new_stream().unwrap();let before=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();let m=ctx.load_module(ptx).unwrap();let f=m.load_function("d246_cluster_transport").unwrap();let after=ctx.get_limit(cudarc::driver::sys::CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
 let dimensions=[f.get_attribute(FA::CU_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_WIDTH).unwrap(),f.get_attribute(FA::CU_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_HEIGHT).unwrap(),f.get_attribute(FA::CU_FUNC_ATTRIBUTE_REQUIRED_CLUSTER_DEPTH).unwrap()];assert_eq!(dimensions,[2,1,1]);
 for threads in [32,64,128,256]{for shared in [4u32,26520]{let cfg=LaunchConfig{grid_dim:(8,1,1),block_dim:(threads,1,1),shared_mem_bytes:shared};let clusters=f.occupancy_max_active_clusters(cfg,&stream).unwrap();emit(serde_json::json!({"stage":"resource","threads":threads,"dynamic_shared_bytes_per_block":shared,"required_cluster_dimensions":dimensions,"active_clusters":clusters,"registers":f.num_regs().unwrap(),"local_bytes_per_thread":f.local_size_bytes().unwrap(),"static_shared_bytes":f.shared_size_bytes().unwrap(),"max_threads":f.max_threads_per_block().unwrap(),"stack_before":before,"stack_after":after,"device_shared_limit":ctx.attribute(DA::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap(),"application_kernels":0}));}}
 drop(f);drop(m);drop(stream);ctx.check_err().unwrap();drop(ctx);emit(serde_json::json!({"stage":"complete","compile_variants":1,"application_kernels":0,"solver_or_speed_samples":0}));}
'''
(H/'probe.rs').write_bytes(rust.encode('utf-8'));old=h.read(parent/'protocol.json');cmd=[x.replace(str(parent),str(H))for x in old['rustc_command']]
headers=[Path(p)for p in old['input_sha256']if'/include/'in p.replace('\\','/')];assert headers and all(p.is_relative_to(ROOT)for p in headers)
files=[Path(__file__),ROOT/'runs/D246-execute-cluster-resource.py',ROOT/'runs/D245-cluster-capability/report.json',ROOT/'runs/D245-cluster-capability/source-review.json',ROOT/'epoch/common.py',parent/'protocol.json']+[p for p in H.iterdir()if p.is_file()]+headers+[p for p in(ROOT/'reference/accepted-e080-deps').iterdir()if p.is_file()]
h.save(H/'source-review.json',{'at':h.now(),'scope':'Standalone integer-bit transport primitive only, no poker/CFR shader orsolver candidate. Eachfixed2blockcluster initializes own perblockshared words from disjoint immutableglobalinputs; afterclusterpublication barrier it readspeer(ownrank XOR1),writes own disjoint global span,thenclusterlifetime barrier beforeproducerexit. uinttransport includesallf32bitpayloads withoutfloatingarithmetic. Emptyloops stillparticipate bothbarriers. No globalgrid barrier/cooperativelaunch/residentgridform.','compiler':'ExactNVRTC12.9/privatealreadychecksumverifiedCUDA12.9runtime+CCCLheaders fromD203,defaultoptions andonecompute120target. No SDK/DLL/install/globalPATH/acceptedsource change. Primitive hardwarefeature only; no otherarchitecture correctness claimed.','resource_gate':'Requiredcluster2/1/1actualfunctionattrs; all8threads/shared combinations defaultfit, no localmemory,positiveactiveclusters,unchangedcontextstack. Resourcepass onlyadmitstheoriginal132case/eager+4graphreplay standalone transport controls. Intended mappedremote operand andbothclusterbarriers mustsurvivePTX beforeapplicationkernels.','failure':'Any realresource/intendedfeature/numerical/lifetime/graphfailurecloses thisfixedprimitive/lead withoutsource/width/flags/alternativeprimitive rescue. Mechanicalcompiler/binding/observer defects preserveoriginalsources/errors andcompletednativecases neverrepeat. No speed/optimizer gain fromfeatureproof.'})
files.append(H/'source-review.json');h.save(H/'protocol.json',{'id':'D246','at':h.now(),'status':'FROZEN_PRE_COMPILER_AND_MODULE_ONLY_QUERY','rustc_command':cmd,'GPU_uuid':q['GPU_uuid'],'input_sha256':{str(p):h.sha(p)for p in files},'expected_resource_rows':8,'required_free_bytes':8*1024**3,'scope':'OneRustcompiler/oneNVRTC120/module-onlyprocess.Noapplicationkernel,counter,solver,speed,sourceactivation.NoGPUcandidateyet.'})
for name in ['protocol.json','source-review.json']:
 p=H/name;dst=h.ar.DASHBOARD/'evidence'/H.name/name;dst.parent.mkdir(parents=True,exist_ok=True);assert not dst.exists();shutil.copyfile(p,dst)
 with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
 s=h.read(h.ar.STATUS);s['experiments'].append({'id':'D246','title':'Native cluster shared-memory primitive','kind':'diagnostic','status':'staged','accepted':False,'measurement_epoch':'RAM20261028','stage':'Compiler/resource prerequisiteready','reason':'Actualdevicecluster supportpassed. Exact standalone2blockpeer-wordtransport,publicationandlifetimebarriers;checkrealfunctionrequired dimensions/defaultfit/activeclusters beforeoriginal132raw/graph cases. No solver/speedclaim.','evidence':[{'label':n,'url':'evidence/'+H.name+'/'+n}for n in ['protocol.json','source-review.json']]});s.update(updated_at=h.now(),active_experiment='D246',stage='Cluster primitive compiler/resource prerequisite',activity='Isolated native feature feasibility; E080 solver/source/live unchanged.');h.ar.atomic_json(h.ar.STATUS,s)
print(h.sha(H/'protocol.json'),flush=True)
