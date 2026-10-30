"""Freeze a resource-materiality audit; no solver candidate or historical rescue."""
import json, shutil, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT/'runs/accepted-E051'));import common_e051 as old
old.custody();assert not (ROOT/'gpu-run.lock').exists();old.ar.refuse_active(old.ar.live_status())
H=ROOT/'runs/D094-resource-materiality';assert not H.exists();H.mkdir()
sdk=ROOT/'runs/D085-cupti-activity/vendor/cuda_cudart/cuda_cudart-windows-x86_64-12.9.79-archive/include'
header=sdk/'cuda_occupancy.h';assert header.exists()
ref=old.read(ROOT/'runs/D085-cupti-activity/bootstrap.json')
package=ref['packages']['cuda_cudart']
assert any(v['sha256']==old.sha(header) for k,v in package['files'].items() if k.replace('\\','/').endswith('/include/cuda_occupancy.h'))
r=old.read(ROOT/'runs/E057-resource/report.json');P=old.read(ROOT/'runs/E057-resource/protocol.json')
shapes=[]
for name in P['shapes']:
    b,c=r['details'][name]['baseline'],r['details'][name]['candidate']
    assert b['registers']==38 and c['registers']==40 and all(b[k]==c[k] for k in ['dynamic_shared_bytes','static_shared_bytes','max_threads'])
    shapes.append({'name':name,'dynamic_bytes':b['dynamic_shared_bytes'],'static_bytes':b['static_shared_bytes'],'max_threads':b['max_threads']})
cpp=r'''#define NOMINMAX
#include <windows.h>
#include <cuda.h>
#include <cuda_occupancy.h>
#include <iostream>
#include <cstdlib>
static void need(bool yes,const char* label){if(!yes){std::cerr<<"D094_ERROR "<<label<<std::endl;std::exit(2);}}
template<class F> F sym(HMODULE m,const char* name){auto f=reinterpret_cast<F>(GetProcAddress(m,name));need(f!=nullptr,name);return f;}
struct Shape {const char* name;int dynamic_bytes;int static_bytes;int max_threads;};
int main(){
 auto driver=LoadLibraryExW(L"nvcuda.dll",nullptr,LOAD_LIBRARY_SEARCH_SYSTEM32);need(driver!=nullptr,"load system NVIDIA driver");
 auto init=sym<decltype(&cuInit)>(driver,"cuInit");auto get=sym<decltype(&cuDeviceGet)>(driver,"cuDeviceGet");auto attr=sym<decltype(&cuDeviceGetAttribute)>(driver,"cuDeviceGetAttribute");auto name=sym<decltype(&cuDeviceGetName)>(driver,"cuDeviceGetName");auto version=sym<decltype(&cuDriverGetVersion)>(driver,"cuDriverGetVersion");
 need(init(0)==CUDA_SUCCESS,"cuInit");CUdevice dev;need(get(&dev,0)==CUDA_SUCCESS,"cuDeviceGet");char gpu[256]={};need(name(gpu,sizeof(gpu),dev)==CUDA_SUCCESS,"cuDeviceGetName");int drv=0;need(version(&drv)==CUDA_SUCCESS,"cuDriverGetVersion");
 auto query=[&](CUdevice_attribute a){int v=-1;need(attr(&v,a,dev)==CUDA_SUCCESS,"cuDeviceGetAttribute");return v;};
 cudaOccDeviceProp p;
 p.computeMajor=query(CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MAJOR);p.computeMinor=query(CU_DEVICE_ATTRIBUTE_COMPUTE_CAPABILITY_MINOR);p.maxThreadsPerBlock=query(CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK);p.maxThreadsPerMultiprocessor=query(CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_MULTIPROCESSOR);p.regsPerBlock=query(CU_DEVICE_ATTRIBUTE_MAX_REGISTERS_PER_BLOCK);p.regsPerMultiprocessor=query(CU_DEVICE_ATTRIBUTE_MAX_REGISTERS_PER_MULTIPROCESSOR);p.warpSize=query(CU_DEVICE_ATTRIBUTE_WARP_SIZE);p.sharedMemPerBlock=query(CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK);p.sharedMemPerMultiprocessor=query(CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_MULTIPROCESSOR);p.numSms=query(CU_DEVICE_ATTRIBUTE_MULTIPROCESSOR_COUNT);p.sharedMemPerBlockOptin=query(CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK_OPTIN);p.reservedSharedMemPerBlock=query(CU_DEVICE_ATTRIBUTE_RESERVED_SHARED_MEMORY_PER_BLOCK);
 need(p.computeMajor==12&&p.computeMinor==0&&p.warpSize==32,"registered compute12.0 device");
 int quantum=0,subparts=0;need(cudaOccRegAllocationGranularity(&quantum,&p)==CUDA_OCC_SUCCESS,"register quantum");need(cudaOccSubPartitionsPerMultiprocessor(&subparts,&p)==CUDA_OCC_SUCCESS,"subpartitions");
 std::cout<<"D094_DEVICE {\"gpu\":\""<<gpu<<"\",\"driver_api_version\":"<<drv<<",\"major\":"<<p.computeMajor<<",\"minor\":"<<p.computeMinor<<",\"warp_size\":"<<p.warpSize<<",\"max_threads_block\":"<<p.maxThreadsPerBlock<<",\"max_threads_sm\":"<<p.maxThreadsPerMultiprocessor<<",\"regs_block\":"<<p.regsPerBlock<<",\"regs_sm\":"<<p.regsPerMultiprocessor<<",\"shared_block\":"<<p.sharedMemPerBlock<<",\"shared_sm\":"<<p.sharedMemPerMultiprocessor<<",\"num_sms\":"<<p.numSms<<",\"shared_block_optin\":"<<p.sharedMemPerBlockOptin<<",\"reserved_shared_block\":"<<p.reservedSharedMemPerBlock<<",\"register_quantum_per_warp\":"<<quantum<<",\"register_subpartitions\":"<<subparts<<",\"kernel_launches\":0}"<<std::endl;
 Shape shapes[]={__SHAPES__};cudaOccDeviceState state;
 for(auto shape:shapes){for(int regs:{38,40}){cudaOccFuncAttributes f;f.maxThreadsPerBlock=shape.max_threads;f.numRegs=regs;f.sharedSizeBytes=shape.static_bytes;f.numBlockBarriers=1;
  for(int threads=1;threads<=1024;threads++){cudaOccResult r{};need(cudaOccMaxActiveBlocksPerMultiprocessor(&r,&p,&f,&state,threads,shape.dynamic_bytes)==CUDA_OCC_SUCCESS,"occupancy calculation");
   std::cout<<"D094_ALLOC {\"shape\":\""<<shape.name<<"\",\"nominal_registers\":"<<regs<<",\"threads\":"<<threads<<",\"dynamic_bytes\":"<<shape.dynamic_bytes<<",\"allocated_registers_block\":"<<r.allocatedRegistersPerBlock<<",\"allocated_shared_block\":"<<r.allocatedSharedMemPerBlock<<",\"active_blocks_sm\":"<<r.activeBlocksPerMultiprocessor<<",\"limit_factors\":"<<r.limitingFactors<<",\"limit_regs\":"<<r.blockLimitRegs<<",\"limit_shared\":"<<r.blockLimitSharedMem<<",\"limit_warps\":"<<r.blockLimitWarps<<",\"limit_blocks\":"<<r.blockLimitBlocks<<",\"limit_barriers\":"<<r.blockLimitBarriers<<"}\n";
  }
 }}
 std::cout<<"D094_COMPLETE {\"rows\":20480,\"kernel_launches\":0,\"solver_executions\":0,\"performance_measured\":false}"<<std::endl;FreeLibrary(driver);
}
'''
cpp=cpp.replace('__SHAPES__',','.join('{"'+s['name']+'",'+','.join(str(s[k]) for k in ['dynamic_bytes','static_bytes','max_threads'])+'}' for s in shapes))
(H/'probe.cpp').write_text(cpp,encoding='utf-8',newline='\n')
old.save(H/'proposal.json',{'id':'D094-resource-materiality','at':old.now(),'scope':'Audit resource prefilter against actual allocation granularity. No solver source/candidate change, CUDA kernel launch, historical candidate rescue or speed claim.','basis':'User requests >=1% complete-cycle gain without material tradeoffs. A nominal register increase may fit the same rounded warp allocation. CUDA12.9.79 occupancy header explicitly handles compute12.x and computes rounded allocatedRegistersPerBlock. Validate its model against all60 retained driver occupancy observations and every1..1024thread count at all10geometries.','references':[{'url':'https://docs.nvidia.com/cuda/cuda-c-best-practices-guide/index.html#calculating-occupancy','use':'NVIDIA distinguishes nominal registers from rounded allocation and occupancy; allocation granularity varies by compute capability.'},{'official_package_url':package['url'],'package_sha256':package['sha256'],'header':str(header),'header_sha256':old.sha(header),'cc12_quantum_function':'cudaOccRegAllocationGranularity','allocation_formula':'cudaOccMaxBlocksPerMultiprocessorRegsLimit rounds nominal registers*warpSize to the per-warp allocation granularity, then multiplies by ceil(threads/warpSize).'}],'frozen_checks':['Current registered GPUcompute12.0,warp32 and known GPU name.','20,480 complete SDK model rows:10shapes x2reported register counts x1024thread counts, no exclusions.','Root independently computes register allocation from queried quantum/warp and checks both arms equal for every shape/block.','At64/128/256threads, all60 model occupancies must match retained driver queries. Also require all modeled shared allocations, launch feasibility and register/shared/warp/block/barrier limits identical.','Only after every check passes may a prospective filter use same allocation quantum instead of nominal count alone. Spills/shared/global/host/capacity/performance/accuracy/compatibility gates remain unchanged.','E057 and every prior rejection retain their original outcomes. No automatic reopening or candidate variant. No production adoption from this audit.'],'reviewer':'Root audit, not an external independent review','source_activated':False,'gpu_kernel_launches':0,'solver_executions':0,'performance_measured':False})
print(json.dumps({'path':str(H),'sdk_header_sha256':old.sha(header),'shapes':len(shapes),'rows':20480,'source_activated':False}),flush=True)
