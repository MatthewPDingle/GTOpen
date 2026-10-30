use cudarc::driver::CudaContext;
use std::{ffi::c_void,fs::OpenOptions,io::Write,path::PathBuf};
#[path="nvrtc13.rs"]mod nvrtc13;
#[link(name="kernel32")]
extern "system"{fn GetModuleHandleW(name:*const u16)->*mut c_void;}
fn modules()->serde_json::Value{
    let mut result=serde_json::Map::new();
    for name in ["nvrtc64_130_0.dll","nvrtc-builtins64_130.dll","nvrtc64_130_0.alt.dll"]{
        let text:Vec<u16>=name.encode_utf16().chain(Some(0)).collect();let present=!unsafe{GetModuleHandleW(text.as_ptr())}.is_null();result.insert(name.into(),serde_json::json!(present));
    }
    serde_json::Value::Object(result)
}
fn main(){
    let out=PathBuf::from(std::env::args_os().nth(1).unwrap());std::fs::create_dir(&out).unwrap();
    let directory=PathBuf::from(std::env::args_os().nth(2).unwrap());assert!(directory.is_absolute());
    let source=include_str!("kernels.cu");let expected=include_str!("expected-candidate.ptx");let before=modules();assert!(before.as_object().unwrap().values().all(|v|v==false));
    // Unsupported architecture declines before library acquisition,even with a valid path.
    std::env::set_var("GTOPEN_POSTFLOP_NVRTC13_DIR",&directory);assert!(nvrtc13::try_compile("compute_86",source).is_none());assert_eq!(modules(),before);
    // An explicitly absent private installation declines without loading a library.
    std::env::set_var("GTOPEN_POSTFLOP_NVRTC13_DIR",out.join("absent-private-runtime"));assert!(nvrtc13::try_compile("compute_120",source).is_none());assert_eq!(modules(),before);
    let ctx=CudaContext::new(0).unwrap();assert_eq!(ctx.name().unwrap(),"NVIDIA GeForce RTX 5090");assert_eq!(ctx.compute_capability().unwrap(),(12,0));
    std::env::set_var("GTOPEN_POSTFLOP_NVRTC13_DIR",&directory);
    let ptx=nvrtc13::try_compile("compute_120",source).expect("actual private13runtime required");assert_eq!(ptx.to_src(),expected,"every generated PTX byte");
    let after_success=modules();
    let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("actual-runtime.ptx")).unwrap();file.write_all(ptx.to_src().as_bytes()).unwrap();file.sync_all().unwrap();drop(file);drop(ptx);
    // Expected negative API control: syntax error must destroy its owned program and decline.
    assert!(nvrtc13::try_compile("compute_120","this is deliberately invalid CUDA source").is_none());let after_error=modules();
    // CString rejection also owns no compiler program and leaves the module state unchanged.
    assert!(nvrtc13::try_compile("compute_120","invalid\0source").is_none());assert_eq!(modules(),after_error);
    ctx.check_err().unwrap();drop(ctx);
    let report=serde_json::json!({"unsupported_target_declines":true,"missing_private_runtime_declines":true,"actual_runtime_PTX_exact":true,"expected_syntax_error_declines":true,"embedded_NUL_declines":true,"before_modules":before,"after_success_modules":after_success,"after_error_modules":after_error,"NVRTC_successful_source_compilations":1,"NVRTC_expected_invalid_program_compilations":1,"application_kernel_launches":0,"solver_executions":0,"performance_samples":0});
    let mut file=OpenOptions::new().create_new(true).write(true).open(out.join("native.json")).unwrap();file.write_all(serde_json::to_string_pretty(&report).unwrap().as_bytes()).unwrap();file.sync_all().unwrap();
    println!("D167_RUNTIME {report}");std::io::stdout().flush().unwrap();
}
