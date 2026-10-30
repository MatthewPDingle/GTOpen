use cudarc::nvrtc::{compile_ptx_with_opts, CompileOptions};
use std::{fs::OpenOptions,io::Write,path::PathBuf};
fn main() {
    let out=PathBuf::from(std::env::args().nth(1).unwrap());
    for arch in ["compute_120","compute_75"] {
        let ptx=compile_ptx_with_opts(include_str!("packet.cu"), CompileOptions {
            arch:Some(arch), ftz:Some(false), prec_div:Some(true),
            use_fast_math:Some(false), ..Default::default()
        }).unwrap();
        let mut f=OpenOptions::new().create_new(true).write(true).open(out.join(format!("packet-{arch}.ptx"))).unwrap();
        f.write_all(ptx.to_src().as_bytes()).unwrap();f.sync_all().unwrap();
        println!("D151_COMPILE {}",serde_json::json!({"arch":arch,"PTX_bytes":ptx.to_src().len(),"compile_flags":{"ftz":false,"prec_div":true,"fast_math":false},"GPU_context_created":false,"kernel_launches":0}));
    }
}
