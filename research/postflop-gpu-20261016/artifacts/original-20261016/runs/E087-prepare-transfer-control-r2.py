import sys,json,difflib,shutil
from pathlib import Path
R=Path(r'S:\GTOpen-research\postflop-gpu-20261016')
sys.path.insert(0,str(R/'runs/accepted-E080-live-20261018'));import common_e080_live as old
old.custody()
S=R/'runs/E087-source';H=R/'runs/E087-transfer-control'
old.pin(S/'manifest.json','be19dfb9ba29339bc0cc44deb35e36cb396e8e067962a196351f22982452f165')
assert H.is_dir() and not list(H.iterdir())
def put(p,t):p.write_bytes(t.encode())
prior=R/'runs/D134-zero-init-fences-r2'
oldmod=(prior/'baseline/mod.rs').read_text(encoding='utf-8')
shim=oldmod[oldmod.index('pub mod plan {'):oldmod.index('\nmod arena;')]
assert 'full_arena_adapter' in shim
validator=oldmod[oldmod.index('impl GpuSolver {\n    pub fn d134_validate'):].replace('d134_validate','e087_validate').replace('D134','E087')
observer=(R/'runs/E087-arena-observer.rs').read_text(encoding='utf-8')
drain=r'''
pub(super) fn e087_drain(stream:&Arc<CudaStream>)->serde_json::Value {
    let n=16384usize;
    let expected:Vec<f32>=(0..n).map(|i|f32::from_bits(0x3f000000+(i as u32)*13)).collect();
    let device=stream.clone_htod(&expected).unwrap();
    let mut pinned=super::PinnedBuf::new(stream.context(),n).unwrap();
    stream.synchronize().unwrap();
    stream.memcpy_dtoh(&device,pinned.as_mut_slice()).unwrap();
    let injected=cudarc::driver::DriverError(cudarc::driver::sys::CUresult::CUDA_ERROR_INVALID_VALUE);
    let expected_error=super::e(injected);
    let error=finish_bounded_copy(stream,Err(injected)).unwrap_err();
    assert_eq!(error,expected_error);
    assert_eq!(pinned.as_slice().iter().map(|v|v.to_bits()).collect::<Vec<_>>(),
               expected.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
    let hook=std::panic::take_hook();std::panic::set_hook(Box::new(|_|{}));
    let mut reached_ready=false;
    let unwind=std::panic::catch_unwind(std::panic::AssertUnwindSafe(||{
        stream.memcpy_dtoh(&device,pinned.as_mut_slice()).unwrap();
        finish_bounded_copy(stream,Ok(())).unwrap();
        reached_ready=true;panic!("intentional post-ready CPU unwind");
    }));
    std::panic::set_hook(hook);assert!(reached_ready&&unwind.is_err());
    let mut again=unsafe{stream.alloc::<f32>(n)}.unwrap();
    let copy=stream.memcpy_htod(pinned.as_slice(),&mut again);
    finish_bounded_copy(stream,copy).unwrap();
    let actual=stream.clone_dtoh(&again).unwrap();stream.synchronize().unwrap();
    assert_eq!(actual.iter().map(|v|v.to_bits()).collect::<Vec<_>>(),
               expected.iter().map(|v|v.to_bits()).collect::<Vec<_>>());
    serde_json::json!({"queued_valid_DMA_before_reported_error_drained":true,
        "original_reported_copy_error_priority_exact":true,
        "post_ready_CPU_unwind_caught":true,"staging_reuse_after_drain_exact":true,
        "actual_words":n,"real_hardware_failure_injected":false,
        "atomic_rollback_claim":false,"performance_measurement":false})
}
'''
for arm in ['baseline','candidate']:
 d=H/arm;d.mkdir()
 src=(S/arm/'mod.rs').read_text(encoding='utf-8')
 assert src.count('pub mod plan;')==1
 assert src.count('plan.use_full_action_arenas(&solver.spot);')==1
 adapted=src.replace('pub mod plan;',shim).replace('plan.use_full_action_arenas(&solver.spot);','plan::full_arena_adapter(&mut plan, &solver.spot);')
 assert adapted.replace(shim,'pub mod plan;').replace('plan::full_arena_adapter(&mut plan, &solver.spot);','plan.use_full_action_arenas(&solver.spot);')==src
 suffix=r'''
impl GpuSolver {
    pub fn e087_info(&self)->serde_json::Value {
        serde_json::json!({"pinned_words":self.h_staging.len,
          "pinned_request_bytes":self.h_staging.len*4,
          "wrapper_bytes":std::mem::size_of::<Self>(),
          "layout_bytes":std::mem::size_of::<ArenaLayout>(),
          "device_arena_words":[self.d_regrets[0].len(),self.d_regrets[1].len()],
          "performance_measurement":false})
    }
}
pub fn e087_manual(s:&mut Solver,stream:&Arc<CudaStream>,p:usize,full:bool,prechecked:bool,out:&std::path::Path,id:&str)->serde_json::Value {
    arena::e087_manual(s,stream,p,full,prechecked,out,id)
}
'''
 if arm=='candidate':suffix+='\npub fn e087_drain(stream:&Arc<CudaStream>)->serde_json::Value {arena::e087_drain(stream)}\n'
 put(d/'mod.rs',adapted+'\n'+validator+'\n'+suffix)
 obs=observer.replace('// CONTROL_CAPACITY','let capacity=layout.len;' if arm=='baseline' else 'let capacity=layout.prepare_bounded(solver,p,257).unwrap();')
 for tag,device in [('FIRST','device'),('REPEAT','device'),('SECOND','second')]:
  download=(f'let len={device}.len();stream.memcpy_dtoh(&{device},&mut staging.as_mut_slice()[..len]).unwrap();stream.synchronize().unwrap();layout.write(solver,p,which,&staging.as_slice()[..len]);'
     if arm=='baseline' else f'layout.download(stream,solver,p,which,&{device},staging.as_mut_slice()).unwrap();')
  obs=obs.replace('// CONTROL_DOWNLOAD_'+tag,download)
 obs=obs.replace('// CONTROL_CLEANUP','layout.discard_bounded();' if arm=='candidate' else '')
 obs=obs.replace('// CANDIDATE_DRAIN_OBSERVER',drain if arm=='candidate' else '')
 assert '// CONTROL_' not in obs
 arena=(S/arm/'arena.rs').read_text(encoding='utf-8');put(d/'arena.rs',arena+'\n'+obs)
 assert (d/'arena.rs').read_text(encoding='utf-8').startswith(arena+'\n')
 put(d/'production-adapter.patch',''.join(difflib.unified_diff(src.splitlines(True),adapted.splitlines(True),fromfile='production',tofile='public-plan-adapter')))
 shutil.copyfile(old.REPO/'crates/solver/src/gpu/kernels.cu',d/'kernels.cu')
capture=(prior/'probe.rs').read_text(encoding='utf-8')
capture=capture[capture.index('pub trait Word'):capture.index('fn zero_source')]
probe=(R/'runs/E087-transfer-probe.rs').read_text(encoding='utf-8').replace('// D134_CAPTURE_HELPERS',capture)
put(H/'probe.rs',probe)
shutil.copyfile(prior/'bench_spot.json',H/'bench_spot.json')
print(str(H),flush=True)
