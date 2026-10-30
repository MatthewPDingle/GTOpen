use cudarc::nvrtc::{compile_ptx_with_opts,CompileOptions,Ptx};
use std::{fs::OpenOptions,io::Write,sync::OnceLock,time::Instant};
fn main() {
    let output=std::env::args().nth(1).unwrap();
    let start=Instant::now();
    let arch:&'static str=Box::leak(format!("compute_{}{}",12,0).into_boxed_str());
    static PTX:OnceLock<Result<Ptx,String>>=OnceLock::new();
    let ptx=PTX.get_or_init(||compile_ptx_with_opts(include_str!("kernels.cu"),CompileOptions{arch:Some(arch),..Default::default()}).map_err(|err|format!("cuda: {err:?}"))).clone().unwrap();
    let acquisition_ns=u64::try_from(start.elapsed().as_nanos()).unwrap();
    let mut file=OpenOptions::new().create_new(true).write(true).open(output).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.sync_all().unwrap();
    println!("D158_COLD {}",serde_json::json!({"cold_acquisition_ns":acquisition_ns,"architecture":arch,"compile_options":"arch:Some(compute_120),all_other_Default; exact accepted call","PTX_bytes":ptx.to_src().len(),"explicit_GPU_context_or_kernel_calls":0,"scope":"Fresh process first OnceLock acquisition including NVRTC library acquisition/compilation and Ptx clone; output writing outside clock. Standalone CPU observation,no solver/context and no overlap model or speed score."}));
}
