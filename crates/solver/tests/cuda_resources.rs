//! Read-only compiler diagnostics; counts are context, not optimization scores.
#![cfg(feature = "gpu")]
use cudarc::{driver::CudaContext, nvrtc::{compile_ptx_with_opts, CompileOptions}};

#[test]
#[ignore = "manual CUDA compiler resource inspection"]
fn cuda_resources() {
    let ctx = CudaContext::new(0).unwrap();
    let (major, minor) = ctx.compute_capability().unwrap();
    let arch: &'static str = Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    for (area, source, names) in [
        ("postflop", include_str!("../src/gpu/kernels.cu"), &[
            "down_action", "up_action", "up_action_eval", "up_show", "up_fold"
        ][..]),
        ("preflop", include_str!("../src/preflop/kernels.cu"), &[
            "pf_down", "pf_up", "pf_terminal", "pf_reach_mass"
        ][..]),
    ] {
        let ptx = compile_ptx_with_opts(source, CompileOptions {
            arch: Some(arch), ..Default::default()
        }).unwrap();
        let dir = std::path::Path::new(env!("CARGO_MANIFEST_DIR")).join("target/research-fixtures");
        std::fs::create_dir_all(&dir).unwrap();
        std::fs::write(dir.join(format!("{area}-latest.ptx")), ptx.to_src()).unwrap();
        let module = ctx.load_module(ptx).unwrap();
        let optional: &[&str] = if area == "preflop" {
            &["pf_terminal_2", "pf_terminal_6", "pf_terminal_8"]
        } else { &[] };
        for name in names.iter().chain(optional) {
            let f = match module.load_function(name) {
                Ok(f) => f,
                Err(_) if optional.contains(name) => continue,
                Err(err) => panic!("required kernel {name}: {err:?}"),
            };
            println!("METRIC_JSON {}", serde_json::json!({
                "metrics": {}, "area": area, "kernel": name,
                "registers": f.num_regs().unwrap(),
                "local_bytes_per_thread": f.local_size_bytes().unwrap(),
                "static_shared_bytes": f.shared_size_bytes().unwrap()
            }));
        }
    }
}
