use cudarc::{driver::{CudaContext,sys::{CUdevice_attribute as Attr,CUlimit}},nvrtc::Ptx};
fn main() {
    let path=std::env::args().nth(1).unwrap();
    let ctx=CudaContext::new(0).unwrap();
    assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");
    assert_eq!(ctx.compute_capability().unwrap(),(12,0));
    let shared_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK).unwrap();
    let thread_limit=ctx.attribute(Attr::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK).unwrap();
    let stack_before=ctx.get_limit(CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
    let heap_before=ctx.get_limit(CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
    // Only load a previously persisted PTX. No NVRTC compilation in this process.
    let module=ctx.load_module(Ptx::from_file(path)).unwrap();
    let stack_after=ctx.get_limit(CUlimit::CU_LIMIT_STACK_SIZE).unwrap();
    let heap_after=ctx.get_limit(CUlimit::CU_LIMIT_MALLOC_HEAP_SIZE).unwrap();
    for name in ["packet_quantize_i16","packet_quantize_u16"] {
        let f=module.load_function(name).unwrap();
        let registers=f.num_regs().unwrap();let local=f.local_size_bytes().unwrap();
        let shared=f.shared_size_bytes().unwrap();let max_threads=f.max_threads_per_block().unwrap();
        let occupancy=f.occupancy_max_active_blocks_per_multiprocessor(128,0,None).unwrap();
        println!("D151_RESOURCE {}",serde_json::json!({"kernel":name,"registers":registers,"local_bytes_per_thread":local,"static_shared_bytes":shared,"dynamic_shared_bytes":0,"max_threads":max_threads,"actual_block_threads":128,"occupancy_128_threads":occupancy,"device_shared_limit":shared_limit,"device_thread_limit":thread_limit,"context_stack_before":stack_before,"context_stack_after":stack_after,"context_heap_before":heap_before,"context_heap_after":heap_after,"kernel_launches":0,"NVRTC_compilations_in_load_process":0,"performance_measurement":false}));
    }
    drop(module);ctx.check_err().unwrap();
    println!("D151_LOAD_COMPLETE {}",serde_json::json!({"module_dropped":true,"context_error_check_pass":true,"kernel_launches":0}));
}
