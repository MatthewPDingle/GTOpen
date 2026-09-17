//! Standalone research probe. Does not link the shallow model into the server.
#[cfg(not(feature="gpu"))]
fn main() { panic!("Build with --features gpu"); }

#[cfg(feature="gpu")]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use cudarc::driver::{CudaContext, LaunchConfig, PushKernelArg};
    use serde_json::{json,Value};
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3 {return Err("shallow_probe FIXTURES KERNEL OUTPUT".into());}
    let input:Value=serde_json::from_slice(&std::fs::read(&args[0])?)?;
    let coefficients:Vec<f64>=serde_json::from_value(input["model"]["coefficients"].clone())?;
    if coefficients.len()!=18 {return Err("18 frozen coefficients required".into());}
    let mut sprs=Vec::new();let mut raw=Vec::new();let mut mass=Vec::new();let mut endpoint=Vec::new();let mut cpu=Vec::new();
    for f in input["fixtures"].as_array().ok_or("fixtures")? {
        let spr=f["spr"].as_f64().ok_or("spr")?;
        let r:Vec<f64>=serde_json::from_value(f["raw"].clone())?;
        let m:Vec<f64>=serde_json::from_value(f["mass"].clone())?;
        let e:Vec<f64>=serde_json::from_value(f["endpoint"].clone())?;
        if r.len()!=338 || m.len()!=338 || e.len()!=338 {return Err("338 values required".into());}
        let at=spr.clamp(0.2,0.75);let mut residual=vec![0.;338];
        for x in 0..338 {
            let h=x%169;let q=r[x]-0.5;let pos=if x<169 {-1.}else{1.};
            let pair=if h/13==h%13 {1.}else{0.};let suit=if h/13>h%13 {1.}else{0.};
            let fs=[q,q*q,q*q*q,pos,pos*q,pair,suit,pair*q,suit*q];
            residual[x]=(0..9).map(|k|fs[k]*(coefficients[k]+at.ln_1p()*coefficients[k+9])).sum::<f64>()*at/(1.+at);
        }
        let center=residual.iter().zip(&m).map(|(v,w)|v*w).sum::<f64>()/2.;
        let mut scale=1f64;
        for x in 0..338 {residual[x]-=center;let v=residual[x];
            if v>0. {scale=scale.min((1.+at-r[x])/v);}
            if v<0. {scale=scale.min((r[x]+at)/(-v));}
        }
        let t=((spr-0.75)/0.25).clamp(0.,1.);let t=t*t*(3.-2.*t);
        cpu.push((0..338).map(|x|(1.-t)*(r[x]+scale*residual[x]*(spr/0.2).min(1.))+t*e[x]).collect::<Vec<_>>());
        sprs.push(spr);raw.extend(r);mass.extend(m);endpoint.extend(e);
    }
    let ctx=CudaContext::new(0).map_err(|e|format!("{e:?}"))?;let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().map_err(|e|format!("{e:?}"))?;
    let arch: &'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let source=std::fs::read_to_string(&args[1])?;
    let ptx=cudarc::nvrtc::compile_ptx_with_opts(source,cudarc::nvrtc::CompileOptions{arch:Some(arch),..Default::default()}).map_err(|e|format!("{e:?}"))?;
    let module=ctx.load_module(ptx).map_err(|e|format!("{e:?}"))?;let function=module.load_function("shallow_probe").map_err(|e|format!("{e:?}"))?;
    let ds=stream.clone_htod(&sprs).map_err(|e|format!("{e:?}"))?;let dr=stream.clone_htod(&raw).map_err(|e|format!("{e:?}"))?;
    let dm=stream.clone_htod(&mass).map_err(|e|format!("{e:?}"))?;let de=stream.clone_htod(&endpoint).map_err(|e|format!("{e:?}"))?;
    let mut output=stream.alloc_zeros::<f64>(raw.len()).map_err(|e|format!("{e:?}"))?;
    unsafe {stream.launch_builder(&function).arg(&ds).arg(&dr).arg(&dm).arg(&de).arg(&mut output)
        .launch(LaunchConfig{grid_dim:(sprs.len() as u32,1,1),block_dim:(256,1,1),shared_mem_bytes:0}).map_err(|e|format!("{e:?}"))?;}
    let gpu=stream.clone_dtoh(&output).map_err(|e|format!("{e:?}"))?;
    let results:Vec<_>=cpu.into_iter().enumerate().map(|(i,c)|json!({"cpu":c,"gpu":gpu[i*338..(i+1)*338]})).collect();
    std::fs::write(&args[2],serde_json::to_vec_pretty(&json!({"results":results,"research_only":true}))?)?;
    Ok(())
}
