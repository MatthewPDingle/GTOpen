//! Standalone parity probe for the joint-chance push/fold reference game.
#[cfg(not(feature="gpu"))]
fn main(){panic!("Build with --features gpu");}

#[cfg(feature="gpu")]
fn main()->Result<(),Box<dyn std::error::Error>> {
    use cudarc::driver::{CudaContext,LaunchConfig,PushKernelArg};
    use serde_json::{json,Value};
    let args:Vec<_>=std::env::args().skip(1).collect();
    assert_eq!(args.len(),3,"FIXTURES KERNEL OUTPUT");
    assert!(!std::path::Path::new(&args[2]).exists(),"preserve evidence");
    let input:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let fixtures=input["fixtures"].as_array().ok_or("fixtures")?;
    let iterations=input["iterations"].as_i64().ok_or("iterations")? as i32;
    let mut av=Vec::<f32>::new();let mut bv=Vec::<f32>::new();
    for f in fixtures {
        let a:Vec<f32>=serde_json::from_value(f["a"].clone())?;
        let b:Vec<f32>=serde_json::from_value(f["b"].clone())?;
        assert_eq!(a.len(),169);assert_eq!(b.len(),169*169);av.extend(a);bv.extend(b);
    }
    let ctx=CudaContext::new(0).map_err(|e|format!("{e:?}"))?;let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().map_err(|e|format!("{e:?}"))?;
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let source=std::fs::read_to_string(&args[1])?;let start=std::time::Instant::now();
    let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(|e|format!("{e:?}"))?;
    let compile_seconds=start.elapsed().as_secs_f64();
    let module=ctx.load_module(ptx).map_err(|e|format!("{e:?}"))?;
    let function=module.load_function("compatible_cfr").map_err(|e|format!("{e:?}"))?;
    let da=stream.clone_htod(&av).map_err(|e|format!("{e:?}"))?;
    let db=stream.clone_htod(&bv).map_err(|e|format!("{e:?}"))?;
    let mut output=stream.alloc_zeros::<f32>(fixtures.len()*338).map_err(|e|format!("{e:?}"))?;
    stream.synchronize().map_err(|e|format!("{e:?}"))?;let start=std::time::Instant::now();
    unsafe {stream.launch_builder(&function).arg(&da).arg(&db).arg(&mut output).arg(&iterations)
        .launch(LaunchConfig{grid_dim:(fixtures.len() as u32,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(|e|format!("{e:?}"))?;}
    stream.synchronize().map_err(|e|format!("{e:?}"))?;let execution_seconds=start.elapsed().as_secs_f64();
    let policy=stream.clone_dtoh(&output).map_err(|e|format!("{e:?}"))?;
    let result=json!({"iterations":iterations,"compile_seconds":compile_seconds,"execution_seconds":execution_seconds,
        "policies":policy.chunks(338).collect::<Vec<_>>(),"research_only":true});
    std::fs::write(&args[2],serde_json::to_vec_pretty(&result)?)?;
    Ok(())
}
