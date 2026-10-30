#define NOMINMAX
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
 Shape shapes[]={{"rainbow_p0",6300,1040,1024},{"rainbow_p1",5060,1040,1024},{"two_tone_p0",6320,1040,1024},{"two_tone_p1",5080,1040,1024},{"river_p0",5600,1040,1024},{"river_p1",4660,1040,1024},{"wide_turn",21808,1040,1024},{"full_hand_upper_bound",26520,1040,1024},{"empty_sorted_opponent",1276,1040,1024},{"single_sorted_opponent",1292,1040,1024}};cudaOccDeviceState state;
 for(auto shape:shapes){for(int regs:{38,40}){cudaOccFuncAttributes f;f.maxThreadsPerBlock=shape.max_threads;f.numRegs=regs;f.sharedSizeBytes=shape.static_bytes;f.numBlockBarriers=1;
  for(int threads=1;threads<=1024;threads++){cudaOccResult r{};need(cudaOccMaxActiveBlocksPerMultiprocessor(&r,&p,&f,&state,threads,shape.dynamic_bytes)==CUDA_OCC_SUCCESS,"occupancy calculation");
   std::cout<<"D094_ALLOC {\"shape\":\""<<shape.name<<"\",\"nominal_registers\":"<<regs<<",\"threads\":"<<threads<<",\"dynamic_bytes\":"<<shape.dynamic_bytes<<",\"allocated_registers_block\":"<<r.allocatedRegistersPerBlock<<",\"allocated_shared_block\":"<<r.allocatedSharedMemPerBlock<<",\"active_blocks_sm\":"<<r.activeBlocksPerMultiprocessor<<",\"limit_factors\":"<<r.limitingFactors<<",\"limit_regs\":"<<r.blockLimitRegs<<",\"limit_shared\":"<<r.blockLimitSharedMem<<",\"limit_warps\":"<<r.blockLimitWarps<<",\"limit_blocks\":"<<r.blockLimitBlocks<<",\"limit_barriers\":"<<r.blockLimitBarriers<<"}\n";
  }
 }}
 std::cout<<"D094_COMPLETE {\"rows\":20480,\"kernel_launches\":0,\"solver_executions\":0,\"performance_measured\":false}"<<std::endl;FreeLibrary(driver);
}
