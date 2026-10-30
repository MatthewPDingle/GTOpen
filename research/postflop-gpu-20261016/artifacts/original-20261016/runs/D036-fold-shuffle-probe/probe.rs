//! D036: standalone full-kernel and supplementary reduction differential; no timing.
use cudarc::{driver::{CudaContext, CudaFunction, CudaStream, LaunchConfig, PushKernelArg},
    nvrtc::{compile_ptx_with_opts, CompileOptions}};
use serde_json::{json, Value};
use std::{error::Error, fs::OpenOptions, io::{BufWriter, Write}, sync::Arc};

type Result<T> = std::result::Result<T, Box<dyn Error>>;
const GUARD: u32 = 0x4b123456;
const BASELINE: &str = include_str!("baseline.cu");
const CANDIDATE: &str = include_str!("candidate.cu");
const RAW_BASELINE: &str = include_str!("raw-baseline.cu");
const RAW_CANDIDATE: &str = include_str!("raw-candidate.cu");
const CORPUS: &str = include_str!("corpus.json");

fn fnv(bytes: impl IntoIterator<Item=u8>) -> String {
    let mut h = 0xcbf29ce484222325u64;
    for byte in bytes { h = (h ^ u64::from(byte)).wrapping_mul(0x100000001b3); }
    format!("{h:016x}")
}
fn hash_words(words: &[u32]) -> String { fnv(words.iter().flat_map(|x| x.to_le_bytes())) }
fn words(v: &Value) -> Vec<u32> { v.as_array().unwrap().iter().map(|v| u32::try_from(v.as_u64().unwrap()).unwrap()).collect() }
fn bits(v: &[f32]) -> Vec<u32> { v.iter().map(|v| v.to_bits()).collect() }
fn floats(v: &[u32]) -> Vec<f32> { v.iter().copied().map(f32::from_bits).collect() }
fn padded(mut v: Vec<u32>) -> Vec<u32> { if v.is_empty() { v.push(GUARD); } v }
fn emit(v: Value) -> Result<()> {
    let mut stdout = std::io::stdout().lock();
    writeln!(stdout, "D036_PROBE {}", v)?; stdout.flush()?; Ok(())
}
fn record(file: &mut BufWriter<std::fs::File>, v: Value) -> Result<()> {
    serde_json::to_writer(&mut *file, &v)?; file.write_all(b"\n")?; file.flush()?; Ok(())
}
fn exact(expected: &[u32], actual: &[u32], label: &str) -> Result<()> {
    if expected.len()!=actual.len() { return Err(format!("{label}: length mismatch").into()); }
    if let Some(i) = expected.iter().zip(actual).position(|(a,b)| a!=b) {
        return Err(format!("{label}: index {i}: expected {:08x}, actual {:08x}",expected[i],actual[i]).into());
    }
    Ok(())
}
fn guards(initial: &[u32], actual: &[u32], active: &[bool]) -> Result<()> {
    if initial.len()!=actual.len() || initial.len()!=active.len() { return Err("guard length mismatch".into()); }
    if let Some(i) = (0..initial.len()).find(|&i| !active[i] && initial[i]!=actual[i]) {
        return Err(format!("output guard changed at {i}").into());
    }
    Ok(())
}
fn finite(v: u32) -> bool { v & 0x7f800000 != 0x7f800000 }
fn nonfinite(v: &[u32]) -> Value {
    let examples: Vec<_> = v.iter().enumerate().filter(|(_,v)| !finite(**v)).take(16)
        .map(|(i,v)| json!({"index":i,"bits":format!("{v:08x}")})).collect();
    json!({"count":v.iter().filter(|&&v| !finite(v)).count(),"first_16":examples})
}
fn cpu_total(data: &[u32], block: usize) -> u32 {
    let mut partial = vec![0.0f32; block];
    for (lane, value) in partial.iter_mut().enumerate() {
        for i in (lane..data.len()).step_by(block) { *value += f32::from_bits(data[i]); }
    }
    let mut step = block/2;
    while step>0 {
        for lane in 0..step { partial[lane] += partial[lane+step]; }
        step >>= 1;
    }
    partial[0].to_bits()
}

fn raw_checks(stream: &Arc<CudaStream>, funcs: &[CudaFunction;2], corpus: &Value,
    raw: &mut BufWriter<std::fs::File>) -> Result<usize> {
    let cases = corpus["raw_cases"].as_array().unwrap();
    let mut input=Vec::new(); let mut offsets=Vec::new(); let mut lengths=Vec::new();
    for case in cases {
        input.extend([GUARD;7]); offsets.push(input.len() as u32);
        let data=words(&case["bits"]); lengths.push(data.len() as u32); input.extend(data); input.extend([GUARD;7]);
    }
    let d_data=stream.clone_htod(&floats(&input))?;
    let d_offsets=stream.clone_htod(&offsets)?; let d_lengths=stream.clone_htod(&lengths)?;
    let count=cases.len() as u32;
    let initial=vec![GUARD;2+3*cases.len()+2];
    let mut active=vec![false;initial.len()]; for i in 0..cases.len() { active[2+3*i]=true; }
    for block in [128,16,32,64,256] {
        let mut outputs=Vec::new();
        for (variant,function) in ["baseline","candidate"].into_iter().zip(funcs) {
            let mut out=stream.clone_htod(&initial)?;
            unsafe { stream.launch_builder(function).arg(&d_data).arg(&d_offsets).arg(&d_lengths)
                .arg(&count).arg(&mut out).launch(LaunchConfig { grid_dim:(count+2,1,1), block_dim:(block,1,1), shared_mem_bytes:0 })?; }
            let actual=stream.clone_dtoh(&out)?;
            let unchanged=bits(&stream.clone_dtoh(&d_data)?);
            let read_offsets=stream.clone_dtoh(&d_offsets)?; let read_lengths=stream.clone_dtoh(&d_lengths)?;
            stream.synchronize()?;
            record(raw,json!({"scope":"raw_total","variant":variant,"block":block,"output_bits":actual}))?;
            exact(&input,&unchanged,"raw input immutable")?; exact(&offsets,&read_offsets,"raw offsets immutable")?;
            exact(&lengths,&read_lengths,"raw lengths immutable")?; guards(&initial,&actual,&active)?;
            outputs.push(actual);
        }
        let mut required=0usize; let mut optional_mismatches=0usize;
        for (i,case) in cases.iter().enumerate() {
            let a=outputs[0][2+3*i]; let b=outputs[1][2+3*i];
            let cpu=cpu_total(&words(&case["bits"]),block as usize);
            let required_case=case["required"].as_bool().unwrap();
            record(raw,json!({"scope":"raw_total_case","id":case["id"],"block":block,"required":required_case,
                "baseline_bits":a,"candidate_bits":b,"cpu_same_tree_bits":cpu,"baseline_finite":finite(a),"candidate_finite":finite(b)}))?;
            exact(&[a],&[b],"raw candidate including overflow")?;
            if required_case {
                if !finite(a) || !finite(b) || !finite(cpu) { return Err(format!("Required raw case nonfinite: {} block{block}",case["id"]).into()); }
                exact(&[a],&[b],"raw candidate")?; exact(&[cpu],&[a],"raw CPU same-tree oracle")?; required+=1;
            } else if a!=b { optional_mismatches+=1; }
        }
        emit(json!({"stage":"raw_total_exact","block":block,"required_cases":required,"optional_cases":cases.len()-required,
            "optional_bit_mismatches":optional_mismatches,"baseline_hash":hash_words(&outputs[0]),"candidate_hash":hash_words(&outputs[1]),
            "input_immutable":true,"guards_checked":initial.len()-cases.len(),"baseline_nonfinite":nonfinite(&outputs[0]),
            "candidate_nonfinite":nonfinite(&outputs[1]),"performance_measurement":false}))?;
    }
    Ok(10)
}

fn full_checks(stream: &Arc<CudaStream>, funcs: &[CudaFunction;2], corpus: &Value,
    raw: &mut BufWriter<std::fs::File>) -> Result<(usize,usize,usize)> {
    let mut launches=0usize; let mut required_words=0usize; let mut nonzero_words=0usize;
    for scenario in corpus["full_scenarios"].as_array().unwrap() {
        let id=scenario["id"].as_str().unwrap();
        let nh_p=scenario["nh_p"].as_i64().unwrap() as i32;
        let nh_o=scenario["nh_o"].as_i64().unwrap() as i32;
        let nh_max=scenario["nh_max"].as_i64().unwrap() as i32;
        let start=scenario["start"].as_i64().unwrap() as i32;
        let count=scenario["count"].as_i64().unwrap() as i32;
        let meta=scenario["node_meta"].as_array().unwrap();
        let owner:Vec<i32>=meta.iter().map(|v|v["owner"].as_i64().unwrap() as i32).collect();
        let twin:Vec<u32>=meta.iter().map(|v|v["twin_bits"].as_u64().unwrap() as u32).collect();
        let tlose:Vec<u32>=meta.iter().map(|v|v["tlose_bits"].as_u64().unwrap() as u32).collect();
        let nodes=words(&scenario["nodes"]); let rsrc0=words(&scenario["rsrc0"]); let rsrc1=words(&scenario["rsrc1"]);
        let reach0=words(&scenario["reach0_bits"]); let reach1=words(&scenario["reach1_bits"]);
        let pc1=padded(words(&scenario["pc1"])); let pc2=padded(words(&scenario["pc2"]));
        let off=words(&scenario["card_off"]); let idx=padded(words(&scenario["card_idx"]));
        let same=padded(words(&scenario["same_p"])); let slots=words(&scenario["cfv_slot"]);
        let d_nodes=stream.clone_htod(&nodes)?; let d_owner=stream.clone_htod(&owner)?;
        let d_twin=stream.clone_htod(&floats(&twin))?; let d_tlose=stream.clone_htod(&floats(&tlose))?;
        let d_rsrc0=stream.clone_htod(&rsrc0)?; let d_rsrc1=stream.clone_htod(&rsrc1)?;
        let d_reach0=stream.clone_htod(&floats(&reach0))?; let d_reach1=stream.clone_htod(&floats(&reach1))?;
        let d_pc1=stream.clone_htod(&pc1)?; let d_pc2=stream.clone_htod(&pc2)?;
        let d_off=stream.clone_htod(&off)?; let d_idx=stream.clone_htod(&idx)?;
        let d_same=stream.clone_htod(&same)?; let d_slots=stream.clone_htod(&slots)?;
        let initial=vec![GUARD;scenario["cfv_words"].as_u64().unwrap() as usize];
        let mut active=vec![false;initial.len()]; let mut required=active.clone();
        for &node in &nodes[start as usize..(start+count) as usize] {
            for hand in 0..nh_p as usize {
                let at=slots[node as usize] as usize*nh_max as usize+hand;
                assert!(!active[at],"distinct CFV ownership"); active[at]=true;
                required[at]=meta[node as usize]["required"].as_bool().unwrap();
            }
        }
        for block in [128,16,32,64,256] { for p in [0i32,1] {
            // Separate zero-count cases on the first scenario test uniform early return.
            let counts=if id=="n0-own1" { vec![count,0] } else { vec![count] };
            for actual_count in counts {
                let actual_active=if actual_count==0 { vec![false;active.len()] } else { active.clone() };
                let mut outputs=Vec::new();
                for (variant,function) in ["baseline","candidate"].into_iter().zip(funcs) {
                    let mut d_out=stream.clone_htod(&floats(&initial))?;
                    unsafe { stream.launch_builder(function).arg(&d_nodes).arg(&start).arg(&actual_count).arg(&p)
                        .arg(&d_owner).arg(&d_twin).arg(&d_tlose).arg(&d_rsrc0).arg(&d_rsrc1)
                        .arg(&d_reach0).arg(&d_reach1).arg(&d_pc1).arg(&d_pc2).arg(&d_off).arg(&d_idx)
                        .arg(&d_same).arg(&d_slots).arg(&mut d_out).arg(&nh_p).arg(&nh_o).arg(&nh_max)
                        .launch(LaunchConfig {grid_dim:(actual_count as u32+2,1,1),block_dim:(block,1,1),shared_mem_bytes:nh_o as u32*4})?; }
                    launches+=1;
                    let out=bits(&stream.clone_dtoh(&d_out)?);
                    record(raw,json!({"scope":"full_up_fold","scenario":id,"p":p,"block":block,"count":actual_count,
                        "variant":variant,"output_bits":out}))?;
                    guards(&initial,&out,&actual_active)?;
                    macro_rules! unchanged { ($host:expr,$device:expr,$name:expr) => {
                        exact($host,&stream.clone_dtoh($device)?,$name)?;
                    }; }
                    unchanged!(&nodes,&d_nodes,"nodes");
                    if stream.clone_dtoh(&d_owner)?!=owner { return Err("owner input changed".into()); }
                    exact(&twin,&bits(&stream.clone_dtoh(&d_twin)?),"twin")?;
                    exact(&tlose,&bits(&stream.clone_dtoh(&d_tlose)?),"tlose")?;
                    unchanged!(&rsrc0,&d_rsrc0,"rsrc0"); unchanged!(&rsrc1,&d_rsrc1,"rsrc1");
                    exact(&reach0,&bits(&stream.clone_dtoh(&d_reach0)?),"reach0")?;
                    exact(&reach1,&bits(&stream.clone_dtoh(&d_reach1)?),"reach1")?;
                    unchanged!(&pc1,&d_pc1,"pc1"); unchanged!(&pc2,&d_pc2,"pc2");
                    unchanged!(&off,&d_off,"card_off"); unchanged!(&idx,&d_idx,"card_idx");
                    unchanged!(&same,&d_same,"same_p"); unchanged!(&slots,&d_slots,"cfv_slot");
                    stream.synchronize()?;
                    outputs.push(out);
                }
                let mut checked=0usize; let mut nonzero=0usize; let mut changed=0usize; let mut optional_mismatches=0usize;
                let mut a_optional=Vec::new(); let mut b_optional=Vec::new();
                for i in 0..initial.len() {
                    if !actual_active[i] { continue; }
                    let a=outputs[0][i]; let b=outputs[1][i];
                    exact(&[a],&[b],&format!("full up_fold {id} p{p} block{block} word{i}, including overflow"))?;
                    if required[i] {
                        if !finite(a) || !finite(b) { return Err(format!("Required full output nonfinite: {id},p{p},block{block},index{i}").into()); }
                        exact(&[a],&[b],&format!("full up_fold {id} p{p} block{block} word{i}"))?;
                        checked+=1;
                        if a!=initial[i] { changed+=1; if a & 0x7fffffff !=0 { nonzero+=1; } }
                    } else { a_optional.push(a); b_optional.push(b); if a!=b {optional_mismatches+=1;} }
                }
                if checked>0 && changed==0 {return Err(format!("No required active output changed from stale guard: {id}").into());}
                required_words+=checked; nonzero_words+=nonzero;
                emit(json!({"stage":"full_fold_exact","scenario":id,"p":p,"block":block,"count":actual_count,
                    "nh_p":nh_p,"nh_o":nh_o,"dynamic_shared_bytes":nh_o*4,"required_words":checked,
                    "required_nonzero_words_excluding_stale_guard":nonzero,"required_changed_words":changed,
                    "optional_bit_mismatches":optional_mismatches,
                    "baseline_hash":hash_words(&outputs[0]),"candidate_hash":hash_words(&outputs[1]),
                    "optional_baseline_nonfinite":nonfinite(&a_optional),"optional_candidate_nonfinite":nonfinite(&b_optional),
                    "guard_words_checked_per_variant":initial.len()-actual_active.iter().filter(|&&b|b).count(),
                    "all_input_buffers_bitwise_immutable":true,"performance_measurement":false}))?;
            }
        }}
    }
    if nonzero_words==0 {return Err("No nonzero required full-kernel outputs; vacuous proof".into());}
    Ok((launches,required_words,nonzero_words))
}

fn run() -> Result<()> {
    // Harness checks only; these injected failures are not CUDA numerical cases.
    if exact(&[1],&[0],"injected bit").is_ok() {return Err("bit mismatch self-test failed".into());}
    if guards(&[GUARD],&[0],&[false]).is_ok() {return Err("guard mismatch self-test failed".into());}
    let corpus:Value=serde_json::from_str(CORPUS)?;
    if corpus["guard_bits"].as_u64()!=Some(GUARD as u64) {return Err("wrong guard".into());}
    emit(json!({"stage":"harness_checks","expected_bit_injection_rejected":true,"guard_injection_rejected":true,
        "corpus_fnv1a64":fnv(CORPUS.bytes()),"counts_as_gpu_numerical_case":false}))?;
    let ctx=CudaContext::new(0)?;
    let stream=ctx.new_stream()?;
    let device=ctx.name()?; if device!="NVIDIA GeForce RTX 5090" {return Err(format!("wrong device {device}").into());}
    let (major,minor)=ctx.compute_capability()?; if (major,minor)!=(12,0) {return Err("wrong architecture".into());}
    let arch: &'static str=Box::leak(format!("compute_{major}{minor}").into_boxed_str());
    let mut modules=Vec::new();
    for (variant,source) in [("baseline",BASELINE),("candidate",CANDIDATE),("raw-baseline",RAW_BASELINE),("raw-candidate",RAW_CANDIDATE)] {
        let ptx=compile_ptx_with_opts(source,CompileOptions {arch:Some(arch),..Default::default()})?;
        let mut file=OpenOptions::new().write(true).create_new(true).open(format!("{variant}.ptx"))?;
        file.write_all(ptx.to_src().as_bytes())?; file.flush()?;
        let module=ctx.load_module(ptx)?;
        if !variant.starts_with("raw-") {
            let f=module.load_function("up_fold")?;
            for nh_o in [0u32,257,319,1326] {
                emit(json!({"stage":"resource","source_variant":variant,"source_fnv1a64":fnv(source.bytes()),
                    "source_bytes":source.len(),"kernel":"up_fold","device":device,"architecture":arch,
                    "compile_options":"architecture only; all other CompileOptions default, matching accepted production",
                    "registers":f.num_regs()?,"local_bytes_per_thread":f.local_size_bytes()?,"static_shared_bytes":f.shared_size_bytes()?,
                    "block_threads":128,"nh_o":nh_o,"dynamic_shared_bytes":nh_o*4,
                    "occupancy_blocks_per_sm_128":f.occupancy_max_active_blocks_per_multiprocessor(128,(nh_o*4) as usize,None)?,
                    "scope":"theoretical occupancy/resources only","performance_measurement":false}))?;
            }
        }
        modules.push(module);
    }
    let full=[modules[0].load_function("up_fold")?,modules[1].load_function("up_fold")?];
    let raw_funcs=[modules[2].load_function("raw_total")?,modules[3].load_function("raw_total")?];
    let file=OpenOptions::new().write(true).create_new(true).open("raw-results.jsonl")?;
    let mut raw=BufWriter::new(file);
    let raw_launches=raw_checks(&stream,&raw_funcs,&corpus,&mut raw)?;
    let (full_launches,required_words,nonzero_words)=full_checks(&stream,&full,&corpus,&mut raw)?;
    raw.flush()?; stream.synchronize()?; ctx.check_err()?;
    drop(raw_funcs); drop(full); drop(modules);
    stream.synchronize()?; ctx.check_err()?;
    emit(json!({"stage":"complete","required_exact":true,"all_observed_gpu_bits_exact":true,
        "all_raw_case_pairs":corpus["raw_cases"].as_array().unwrap().len()*5,
        "required_raw_case_pairs":corpus["raw_cases"].as_array().unwrap().iter().filter(|v|v["required"]==true).count()*5,
        "full_case_pairs":full_launches/2,"required_full_output_words":required_words,"required_nonzero_words":nonzero_words,
        "kernel_launches":raw_launches+full_launches,"raw_kernel_launches":raw_launches,"full_kernel_launches":full_launches,
        "fallback_blocks":[16,32,64,256],"specialized_block":128,"input_immutability":true,"output_guards":true,
        "optional_overflow_reported_separately":true,"nan_input_payload_guarantee":false,
        "solver_executions":0,"performance_measurement":false,"candidate_accepted":false}))?;
    Ok(())
}
fn main() {
    if let Err(error)=run() {
        let _=emit(json!({"stage":"invalid","error":error.to_string(),"performance_measurement":false}));
        eprintln!("D036 invalid: {error}"); std::process::exit(1);
    }
}
