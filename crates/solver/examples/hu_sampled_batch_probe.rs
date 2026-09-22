//! Isolated sampled-CFR batch qualification. Never linked into production.
#[cfg(not(feature = "gpu"))]
fn main() { panic!("Research probe requires --features gpu"); }

#[cfg(feature = "gpu")]
fn main() -> Result<(), Box<dyn std::error::Error>> {
    use cudarc::driver::{CudaContext, LaunchConfig, PushKernelArg};
    use serde_json::{json, Value};
    let args:Vec<_>=std::env::args().skip(1).collect();
    if args.len()!=3{return Err("fixture kernel output".into());}
    if std::path::Path::new(&args[2]).exists(){return Err("output already exists".into());}
    let input:Value=serde_json::from_slice(&std::fs::read(&args[0]).map_err(|e| format!("{e:?}"))?).map_err(|e| format!("{e:?}"))?;
    let ints=|v:&Value| -> Vec<i32> {v.as_array().unwrap().iter().map(|x|x.as_i64().unwrap() as i32).collect()};
    let floats=|v:&Value| -> Vec<f64> {v.as_array().unwrap().iter().map(|x|x.as_f64().unwrap()).collect()};
    let nn=input["node_count"].as_i64().unwrap() as i32;
    assert!(nn>0&&nn<=128);
    let actors=ints(&input["actors"]);let arity=ints(&input["arity"]);
    let children:Vec<i32>=input["children"].as_array().unwrap().iter().flat_map(&ints).collect();
    let offsets=ints(&input["action_offsets"]);let ni=offsets.len()-1;let states=*offsets.last().unwrap() as usize;
    assert_eq!(actors.len(),nn as usize);assert_eq!(arity.len(),nn as usize);assert_eq!(children.len(),nn as usize*3);
    for n in 0..nn as usize{assert!((0..=3).contains(&arity[n]));
        for a in 0..arity[n] as usize{assert!(children[n*3+a]>n as i32&&children[n*3+a]<nn);}}
    for o in offsets.windows(2){assert!(o[1]>o[0]&&o[1]-o[0]<=3);}
    let ctx=CudaContext::new(0).map_err(|e| format!("{e:?}"))?;let stream=ctx.default_stream();
    let (major,minor)=ctx.compute_capability().map_err(|e| format!("{e:?}"))?;
    let arch:&'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let ptx=cudarc::nvrtc::compile_ptx_with_opts(std::fs::read_to_string(&args[1]).map_err(|e| format!("{e:?}"))?,
        cudarc::nvrtc::CompileOptions{arch:Some(arch),fmad:Some(false),..Default::default()}).map_err(|e| format!("{e:?}"))?;
    let module=ctx.load_module(ptx).map_err(|e| format!("{e:?}"))?;let traverse=module.load_function("sampled_traverse").map_err(|e| format!("{e:?}"))?;
    let reduce=module.load_function("sampled_reduce").map_err(|e| format!("{e:?}"))?;
    let da=stream.clone_htod(&actors).map_err(|e| format!("{e:?}"))?;let dn=stream.clone_htod(&arity).map_err(|e| format!("{e:?}"))?;
    let dc=stream.clone_htod(&children).map_err(|e| format!("{e:?}"))?;let doff=stream.clone_htod(&offsets).map_err(|e| format!("{e:?}"))?;
    let mut results=vec![];
    for case in input["cases"].as_array().unwrap(){
        let initial=floats(&case["initial_regret"]);assert_eq!(initial.len(),states);
        let mut oldr=stream.clone_htod(&initial).map_err(|e| format!("{e:?}"))?;let mut olda=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;
        for (round,r) in case["rounds"].as_array().unwrap().iter().enumerate(){
            let samples=r["samples"].as_array().unwrap();let ns=samples.len() as i32;
            let players:Vec<i32>=samples.iter().map(|s|s["player"].as_i64().unwrap() as i32).collect();
            let weights:Vec<f64>=samples.iter().map(|s|s["weight"].as_f64().unwrap()).collect();
            let info:Vec<i32>=samples.iter().flat_map(|s|ints(&s["infos"])).collect();
            let choice:Vec<i32>=samples.iter().flat_map(|s|ints(&s["choice"])).collect();
            let utility:Vec<f64>=samples.iter().flat_map(|s|floats(&s["utilities"])).collect();
            let policy=floats(&r["policy"]);let csr=ints(&r["csr_offsets"]);let entries=ints(&r["csr_entries"]);
            assert_eq!(policy.len(),states);assert_eq!(csr.len(),ni+1);assert_eq!(*csr.last().unwrap() as usize,entries.len());
            assert_eq!(info.len(),ns as usize*nn as usize);assert_eq!(choice.len(),info.len());assert_eq!(utility.len(),info.len());
            for s in 0..ns as usize{assert!((0..=1).contains(&players[s])&&weights[s]>0.&&weights[s].is_finite());
                for n in 0..nn as usize{if arity[n]>0{let i=info[s*nn as usize+n] as usize;assert!(i<ni);
                    assert_eq!(offsets[i+1]-offsets[i],arity[n]);assert!((0..arity[n]).contains(&choice[s*nn as usize+n]));}}}
            for i in 0..ni{assert!(csr[i]<=csr[i+1]);for j in csr[i]..csr[i+1]{let e=entries[j as usize] as usize;
                assert!(e<info.len());assert_eq!(info[e],i as i32);}}
            let dp=stream.clone_htod(&players).map_err(|e| format!("{e:?}"))?;let dw=stream.clone_htod(&weights).map_err(|e| format!("{e:?}"))?;let di=stream.clone_htod(&info).map_err(|e| format!("{e:?}"))?;
            let dchoice=stream.clone_htod(&choice).map_err(|e| format!("{e:?}"))?;let du=stream.clone_htod(&utility).map_err(|e| format!("{e:?}"))?;let ds=stream.clone_htod(&policy).map_err(|e| format!("{e:?}"))?;
            let dcsr=stream.clone_htod(&csr).map_err(|e| format!("{e:?}"))?;let de=stream.clone_htod(&entries).map_err(|e| format!("{e:?}"))?;
            let oldr_before=stream.clone_dtoh(&oldr).map_err(|e| format!("{e:?}"))?;let olda_before=stream.clone_dtoh(&olda).map_err(|e| format!("{e:?}"))?;
            let mut rd=stream.alloc_zeros::<f64>(info.len()*3).map_err(|e| format!("{e:?}"))?;let mut av=stream.alloc_zeros::<f64>(info.len()*3).map_err(|e| format!("{e:?}"))?;
            let mut delta=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;let mut inc=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;
            let mut nr=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;let mut na=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;
            let mut np=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;let mut ap=stream.alloc_zeros::<f64>(states).map_err(|e| format!("{e:?}"))?;
            let count=ni as i32;let mut first:Option<Vec<Vec<f64>>>=None;
            for repeat in 0..2{
                unsafe{stream.launch_builder(&traverse).arg(&ns).arg(&nn).arg(&da).arg(&dn).arg(&dc)
                    .arg(&dp).arg(&di).arg(&dchoice).arg(&doff).arg(&ds).arg(&du).arg(&mut rd).arg(&mut av)
                    .launch(LaunchConfig::for_num_elems(ns as u32)).map_err(|e| format!("{e:?}"))?;
                    stream.launch_builder(&reduce).arg(&count).arg(&nn).arg(&doff).arg(&dcsr).arg(&de)
                    .arg(&dw).arg(&rd).arg(&av).arg(&oldr).arg(&olda).arg(&mut delta).arg(&mut inc)
                    .arg(&mut nr).arg(&mut na).arg(&mut np).arg(&mut ap)
                    .launch(LaunchConfig::for_num_elems(ni as u32)).map_err(|e| format!("{e:?}"))?;}
                let got=vec![stream.clone_dtoh(&delta).map_err(|e| format!("{e:?}"))?,stream.clone_dtoh(&inc).map_err(|e| format!("{e:?}"))?,stream.clone_dtoh(&nr).map_err(|e| format!("{e:?}"))?,
                    stream.clone_dtoh(&na).map_err(|e| format!("{e:?}"))?,stream.clone_dtoh(&np).map_err(|e| format!("{e:?}"))?,stream.clone_dtoh(&ap).map_err(|e| format!("{e:?}"))?];
                if repeat==0{first=Some(got);}else{for(a,b)in first.as_ref().unwrap().iter().flatten().zip(got.iter().flatten()){
                    assert_eq!(a.to_bits(),b.to_bits(),"nondeterministic repeat");}}
            }
            assert_eq!(stream.clone_dtoh(&ds).map_err(|e| format!("{e:?}"))?,policy,"policy mutated within batch");
            assert_eq!(stream.clone_dtoh(&oldr).map_err(|e| format!("{e:?}"))?,oldr_before);assert_eq!(stream.clone_dtoh(&olda).map_err(|e| format!("{e:?}"))?,olda_before);
            let names=["expected_delta","expected_average_increment","expected_regret","expected_average","expected_next_policy","expected_normalized_average"];
            let mut errors=serde_json::Map::new();
            for (name,actual)in names.iter().zip(first.as_ref().unwrap()){
                let wanted=floats(&r[*name]);let err=actual.iter().zip(&wanted).map(|(a,b)|(a-b).abs()).fold(0f64,f64::max);
                assert!(actual.iter().all(|x|x.is_finite())&&err<1e-10,"{name} error {err}");errors.insert(name.to_string(),json!(err));}
            results.push(json!({"rake":case["rake"],"round":round,"samples":ns,"maximum_errors":errors,
                "repeat_bit_exact":true,"frozen_input_policy_preserved":true,"old_state_preserved":true}));
            oldr=nr;olda=na;
        }
    }
    std::fs::write(&args[2],serde_json::to_vec_pretty(&json!({"passed":true,"results":results,
        "poker_trainer":false,"convergence_claim":false,"precision":"f64, fmad disabled", "reduction":"stable CSR order; no atomic addition"})).map_err(|e| format!("{e:?}"))?).map_err(|e| format!("{e:?}"))?;
    Ok(())
}
