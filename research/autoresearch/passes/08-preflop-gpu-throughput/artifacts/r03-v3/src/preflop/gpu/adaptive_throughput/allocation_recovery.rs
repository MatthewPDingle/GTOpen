//! R02: test-only, one-shot real CUDA allocation failure after partial construction.
use super::*;
use std::cell::{Cell,RefCell};
use serde_json::{json,Value};

thread_local! {
    static ARMED:Cell<bool> = const {Cell::new(false)};
    static EVENTS:RefCell<Vec<Value>> = const {RefCell::new(Vec::new())};
}

fn memory(ctx:&CudaContext)->Value {
    ctx.synchronize().unwrap();ctx.bind_to_thread().unwrap();
    assert!(ctx.has_async_alloc(),"R02 pool audit requires the actual async allocator");
    let(free,total)=ctx.mem_get_info().unwrap();
    let attr=|attribute| {
        let mut bytes=0u64;
        // The current device owns this pool; these two attributes return u64.
        unsafe {
            let pool=cudarc::driver::result::device::get_mem_pool(ctx.cu_device()).unwrap();
            cudarc::driver::result::mem_pool::get_attribute(pool,attribute,
                (&mut bytes as *mut u64).cast()).unwrap();
        }
        bytes
    };
    json!({"free":free,"total":total,
        "used":attr(sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_USED_MEM_CURRENT),
        "reserved":attr(sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_RESERVED_MEM_CURRENT)})
}

pub(in crate::preflop::gpu) fn after_partial_allocation(
    g:&PreflopGpu,work:usize,maps:usize,values:usize,narrow:bool,
)->Result<(),String> {
    if !ARMED.with(|x|x.replace(false)) {return Ok(());}
    assert!(work>0 && maps>0 && values==1 && g.research_exact_reuse.is_some());
    let at_failure=memory(&g._ctx);
    let total=at_failure["total"].as_u64().unwrap() as usize;
    let requested=1usize << 50;
    assert!(requested>total);
    // WDDM may overcommit beyond physical VRAM. Use a 1 PiB request, beyond
    // this device address space, and never initialize or access the allocation.
    // No host buffer is created; an unexpected success is dropped untouched.
    let error=unsafe {g.stream.alloc::<u8>(requested)}.unwrap_err();
    assert_eq!(error.0,sys::CUresult::CUDA_ERROR_OUT_OF_MEMORY);
    let description=e(error);
    EVENTS.with(|events|events.borrow_mut().push(json!({
        "narrow":narrow,"stage":"first_extra_values_buffer","work_entries":work,
        "map_entries":maps,"value_buffers":values,"value_entries":g.d_val.len(),
        "partial_extra_bytes":4*(work+maps+values*g.d_val.len()),
        "requested_bytes":requested,"memory":at_failure,"error":description
    })));
    Err(description)
}

fn rounds(g:&mut PreflopGpu,s:&mut PreflopSolver)->Vec<(Vec<u32>,Vec<u32>,Vec<u32>,Vec<u64>,Vec<u64>)> {
    let mut out=Vec::new();
    for _ in 0..3 {
        g.iterate(s).unwrap();let(gap,ev)=g.gaps_and_evs().unwrap();
        let(a,b,c)=super::tests::bits(g);
        out.push((a,b,c,gap.iter().map(|v|v.to_bits()).collect(),ev.iter().map(|v|v.to_bits()).collect()));
    }
    assert!(g.eval_graph.is_some());
    let before=super::tests::bits(g);let age=s.iteration;
    assert!(!g.try_iterate(s,Some(&AtomicBool::new(true))).unwrap());
    assert_eq!(super::tests::bits(g),before);assert_eq!(s.iteration,age);
    g.sync_to_cpu(s).unwrap();let(a,b)=s.arena_snapshot();
    assert_eq!(a.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.0);
    assert_eq!(b.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),before.1);
    out
}

#[test]
fn actual_partial_allocation_failure_recovers_without_leaking_or_changing_math() {
    struct Disarm;
    impl Drop for Disarm {fn drop(&mut self){ARMED.with(|x|x.set(false));}}
    let _disarm=Disarm;
    let ctx=CudaContext::new(0).unwrap();
    let mut baseline=super::tests::fixture(4);
    let pristine=baseline.arena_snapshot();
    let before=memory(&ctx);
    let mut normal=PreflopGpu::new(&baseline,2000).unwrap();
    let normal_bytes=memory(&ctx)["used"].as_u64().unwrap()-before["used"].as_u64().unwrap();
    assert!(normal_bytes>0);
    let layout=(normal.mw_batch,normal.use_eq_cache,normal.use_mw_compact);
    let expected=rounds(&mut normal,&mut baseline);drop(normal);
    assert_eq!(memory(&ctx)["used"],before["used"]);
    for narrow in [false,true] {
        let mut s=super::tests::fixture(4);let age=s.iteration;
        let before=memory(&ctx);EVENTS.with(|x|x.borrow_mut().clear());
        ARMED.with(|x|x.set(true));
        let (mut g,report)=PreflopGpu::adaptive_with_offsets(&s,2000,Ok(2_000_000_000),narrow).unwrap();
        assert!(!report.narrow_offsets,"fallback must report ordinary wide kernels");
        assert!(!ARMED.with(|x|x.get()));
        let events=EVENTS.with(|x|x.borrow().clone());assert_eq!(events.len(),1);
        assert_eq!(report.mode,"normal_gpu");
        assert!(report.fallback_reason.as_ref().unwrap().contains("CUDA_ERROR_OUT_OF_MEMORY"));
        assert_eq!(report.configured_budget_mb,2000);
        assert_eq!(s.iteration,age);assert_eq!(s.arena_snapshot(),pristine);
        let fallback_memory=memory(&ctx);
        assert_eq!(fallback_memory["used"].as_u64().unwrap(),before["used"].as_u64().unwrap()+normal_bytes,
            "only ordinary-engine buffers may remain after the failed optimized attempt");
        assert_eq!((g.mw_batch,g.use_eq_cache,g.use_mw_compact),layout);
        assert_eq!(rounds(&mut g,&mut s),expected);drop(g);
        let after_drop=memory(&ctx);assert_eq!(after_drop["used"],before["used"]);
        let mut s=super::tests::fixture(4);
        let mut retry=if narrow {PreflopGpu::new_research_narrow_cohorts(&s,2000).unwrap()}
            else {PreflopGpu::new_research_unrolled_cohorts(&s,2000).unwrap()};
        assert!(retry.research_cohorts.is_some());
        assert_eq!(rounds(&mut retry,&mut s),expected);drop(retry);
        let after_retry=memory(&ctx);assert_eq!(after_retry["used"],before["used"]);
        println!("R02_RECOVERY {}",json!({"narrow":narrow,"selection":report,"events":events,
            "before":before,"fallback_memory":fallback_memory,"after_drop":after_drop,"after_retry":after_retry,
            "normal_allocation_bytes":normal_bytes,"exact_rounds":3,"full_arenas_roots_gap_ev_equal":true,
            "captured_stop_sync_equal":true,"retry_optimized_succeeded":true,"point_lock_and_frozen_seat":true}));
    }
}
