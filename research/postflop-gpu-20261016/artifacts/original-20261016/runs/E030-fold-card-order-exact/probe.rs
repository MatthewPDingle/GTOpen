//! E030: actual complete-up_fold card-task-order differential; no timing.
use cudarc::{driver::{CudaContext, CudaFunction, CudaStream, LaunchConfig, PushKernelArg},
    nvrtc::{compile_ptx_with_opts, CompileOptions}};
use serde_json::{json, Value};
use std::{ fs::OpenOptions, io::{BufWriter, Write}, sync::Arc};

#[derive(Debug)]
struct ProbeError(String);
impl std::fmt::Display for ProbeError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.write_str(&self.0)
    }
}
impl std::error::Error for ProbeError {}
impl From<cudarc::driver::DriverError> for ProbeError {
    fn from(value: cudarc::driver::DriverError) -> Self { Self(format!("CUDA driver: {value:?}")) }
}
impl From<cudarc::nvrtc::CompileError> for ProbeError {
    fn from(value: cudarc::nvrtc::CompileError) -> Self { Self(format!("NVRTC compiler: {value:?}")) }
}
impl From<std::io::Error> for ProbeError {
    fn from(value: std::io::Error) -> Self { Self(format!("I/O: {value}")) }
}
impl From<serde_json::Error> for ProbeError {
    fn from(value: serde_json::Error) -> Self { Self(format!("JSON: {value}")) }
}
impl From<String> for ProbeError {
    fn from(value: String) -> Self { Self(value) }
}
impl From<&str> for ProbeError {
    fn from(value: &str) -> Self { Self(value.to_owned()) }
}
type Result<T> = std::result::Result<T, ProbeError>;
const GUARD: u32 = 0x4b123456;
const BASELINE: &str = include_str!("baseline.cu");
const CANDIDATE: &str = include_str!("candidate.cu");
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
    writeln!(stdout, "E030_DIRECT_EXACT {}", v)?; stdout.flush()?; Ok(())
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
fn full_checks(stream: &Arc<CudaStream>, funcs: &[CudaFunction;2], corpus: &Value,
    raw: &mut BufWriter<std::fs::File>) -> Result<Value> {
    let mut launches=0usize; let mut required_words=0usize; let mut nonzero_words=0usize;
    let mut active_words=0usize; let mut guard_words=0usize; let mut input_words=0usize;
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
        let off_base=words(&scenario["card_off"]); let off_candidate=words(&scenario["candidate_card_off"]);
        let idx=padded(words(&scenario["card_idx"]));
        let same=padded(words(&scenario["same_p"])); let slots=words(&scenario["cfv_slot"]);
        let d_nodes=stream.clone_htod(&nodes)?; let d_owner=stream.clone_htod(&owner)?;
        let d_twin=stream.clone_htod(&floats(&twin))?; let d_tlose=stream.clone_htod(&floats(&tlose))?;
        let d_rsrc0=stream.clone_htod(&rsrc0)?; let d_rsrc1=stream.clone_htod(&rsrc1)?;
        let d_reach0=stream.clone_htod(&floats(&reach0))?; let d_reach1=stream.clone_htod(&floats(&reach1))?;
        let d_pc1=stream.clone_htod(&pc1)?; let d_pc2=stream.clone_htod(&pc2)?;
        let d_off_base=stream.clone_htod(&off_base)?; let d_off_candidate=stream.clone_htod(&off_candidate)?;
        let d_idx=stream.clone_htod(&idx)?;
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
                    let (off,d_off)=if variant=="baseline" {(&off_base,&d_off_base)} else {(&off_candidate,&d_off_candidate)};
                    let mut d_out=stream.clone_htod(&floats(&initial))?;
                    unsafe { stream.launch_builder(function).arg(&d_nodes).arg(&start).arg(&actual_count).arg(&p)
                        .arg(&d_owner).arg(&d_twin).arg(&d_tlose).arg(&d_rsrc0).arg(&d_rsrc1)
                        .arg(&d_reach0).arg(&d_reach1).arg(&d_pc1).arg(&d_pc2).arg(d_off).arg(&d_idx)
                        .arg(&d_same).arg(&d_slots).arg(&mut d_out).arg(&nh_p).arg(&nh_o).arg(&nh_max)
                        .launch(LaunchConfig {grid_dim:(actual_count as u32+2,1,1),block_dim:(block,1,1),shared_mem_bytes:nh_o as u32*4})?; }
                    launches+=1;
                    let out=bits(&stream.clone_dtoh(&d_out)?);
                    // Retain the output and all readback hashes before any equality check.
                    let owner_bits:Vec<u32>=owner.iter().map(|&v|v as u32).collect();
                    let mut inputs:Vec<(&str,Vec<u32>,Vec<u32>)>=Vec::new();
                    macro_rules! gather { ($host:expr,$actual:expr,$name:expr) => {
                        inputs.push(($name,($host).to_vec(),$actual));
                    }; }
                    gather!(&nodes,stream.clone_dtoh(&d_nodes)?,"nodes");
                    gather!(&owner_bits,stream.clone_dtoh(&d_owner)?.into_iter().map(|v|v as u32).collect(),"owner");
                    gather!(&twin,bits(&stream.clone_dtoh(&d_twin)?),"twin");
                    gather!(&tlose,bits(&stream.clone_dtoh(&d_tlose)?),"tlose");
                    gather!(&rsrc0,stream.clone_dtoh(&d_rsrc0)?,"rsrc0");
                    gather!(&rsrc1,stream.clone_dtoh(&d_rsrc1)?,"rsrc1");
                    gather!(&reach0,bits(&stream.clone_dtoh(&d_reach0)?),"reach0");
                    gather!(&reach1,bits(&stream.clone_dtoh(&d_reach1)?),"reach1");
                    gather!(&pc1,stream.clone_dtoh(&d_pc1)?,"pc1");
                    gather!(&pc2,stream.clone_dtoh(&d_pc2)?,"pc2");
                    gather!(off,stream.clone_dtoh(d_off)?,"card_off");
                    gather!(&idx,stream.clone_dtoh(&d_idx)?,"card_idx");
                    gather!(&same,stream.clone_dtoh(&d_same)?,"same_p");
                    gather!(&slots,stream.clone_dtoh(&d_slots)?,"cfv_slot");
                    stream.synchronize()?;
                    assert_eq!(inputs.len(),14);
                    let input_records:Vec<Value>=inputs.iter().map(|(name,a,b)|json!({"name":name,"words":a.len(),
                        "expected_fnv1a64":hash_words(a),"actual_fnv1a64":hash_words(b)})).collect();
                    record(raw,json!({"scope":"full_up_fold","scenario":id,"p":p,"block":block,"count":actual_count,
                        "variant":variant,"output_bits":out,"input_readbacks":input_records}))?;
                    guards(&initial,&out,&actual_active)?;
                    for (name,expected,actual) in &inputs {
                        if expected!=actual {
                            record(raw,json!({"scope":"input_mismatch","scenario":id,"p":p,"block":block,"count":actual_count,
                                "variant":variant,"name":name,"expected_bits":expected,"actual_bits":actual}))?;
                        }
                        exact(expected,actual,name)?;
                        input_words+=expected.len();
                    }
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
                active_words+=actual_active.iter().filter(|&&v|v).count();
                guard_words+=2*(initial.len()-actual_active.iter().filter(|&&v|v).count());
                emit(json!({"stage":"full_fold_exact","scenario":id,"p":p,"block":block,"count":actual_count,
                    "nh_p":nh_p,"nh_o":nh_o,"dynamic_shared_bytes":nh_o*4,"required_words":checked,
                    "active_words":actual_active.iter().filter(|&&v|v).count(),"device_input_buffer_checks":28,
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
    Ok(json!({"comparison_pairs":launches/2,"kernel_launches":launches,"active_words_per_arm":active_words,
        "required_finite_words_per_arm":required_words,"required_nonzero_words":nonzero_words,
        "output_guard_checks_both_arms":guard_words,"input_buffer_checks_both_arms":launches*14,"input_word_checks_both_arms":input_words}))
}

fn validate_corpus(corpus:&Value) -> Result<()> {
    assert_eq!(corpus["guard_bits"].as_u64(),Some(GUARD as u64));
    let scenarios=corpus["full_scenarios"].as_array().unwrap();assert_eq!(scenarios.len(),17);
    for scenario in scenarios {
        let off=words(&scenario["card_off"]);let packed=words(&scenario["candidate_card_off"]);let idx=words(&scenario["card_idx"]);
        let nh_o=scenario["nh_o"].as_u64().unwrap() as usize;let nh_p=scenario["nh_p"].as_u64().unwrap() as usize;
        assert_eq!(off.len(),53);assert_eq!(packed.len(),105);assert_eq!(&packed[..53],off.as_slice());
        assert_eq!(off[0],0);assert!(off.windows(2).all(|w|w[0]<=w[1]));assert_eq!(off[52] as usize,idx.len());assert_eq!(idx.len(),2*nh_o);
        let mut order:Vec<u32>=(0..52).collect();order.sort_by_key(|&card|(std::cmp::Reverse(off[card as usize+1]-off[card as usize]),card));
        assert_eq!(&packed[53..],order.as_slice());let mut permutation=packed[53..].to_vec();permutation.sort_unstable();assert_eq!(permutation,(0..52).collect::<Vec<u32>>());
        let hands=scenario["opponent_hands"].as_array().unwrap();assert_eq!(hands.len(),nh_o);
        for card in 0..52 {
            let expected:Vec<u32>=hands.iter().enumerate().filter(|(_,h)|h.as_array().unwrap().iter().any(|v|v.as_u64()==Some(card))).map(|(i,_)|i as u32).collect();
            assert_eq!(&idx[off[card as usize] as usize..off[card as usize+1] as usize],expected.as_slice());
        }
        assert_eq!(scenario["own_hands"].as_array().unwrap().len(),nh_p);
        for key in ["pc1","pc2","same_p"] {assert_eq!(words(&scenario[key]).len(),nh_p);}
        for key in ["reach0_bits","reach1_bits"] {assert!(words(&scenario[key]).iter().all(|&v|finite(v)));}
        assert_eq!(scenario["start"].as_u64(),Some(2));assert_eq!(scenario["count"].as_u64(),Some(56));
        assert!(scenario["nh_max"].as_u64().unwrap() as usize>=nh_p.max(nh_o));
    }
    Ok(())
}
fn run() -> Result<()> {
    // Host verifier injections are not native numerical cases.
    if exact(&[1],&[0],"injected bit").is_ok() {return Err("bit mismatch self-test failed".into());}
    if guards(&[GUARD],&[0],&[false]).is_ok() {return Err("guard mismatch self-test failed".into());}
    let corpus:Value=serde_json::from_str(CORPUS)?;validate_corpus(&corpus)?;
    emit(json!({"stage":"harness_checks","expected_bit_injection_rejected":true,"guard_injection_rejected":true,
        "metadata_validated":true,"full_scenarios":17,"baseline_offset_words":53,"candidate_offset_words":105,
        "corpus_fnv1a64":fnv(CORPUS.bytes()),"counts_as_gpu_numerical_case":false}))?;
    let ctx=CudaContext::new(0)?;let stream=ctx.new_stream()?;
    let device=ctx.name()?;if device!="NVIDIA GeForce RTX 5090" {return Err(format!("wrong device {device}").into());}
    let (major,minor)=ctx.compute_capability()?;if (major,minor)!=(12,0) {return Err("wrong architecture".into());}
    let shared_limit=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_SHARED_MEMORY_PER_BLOCK)?;
    let thread_limit=ctx.attribute(cudarc::driver::sys::CUdevice_attribute::CU_DEVICE_ATTRIBUTE_MAX_THREADS_PER_BLOCK)?;
    let mut modules=Vec::new();let mut resources=Vec::new();
    for (variant,source) in [("baseline",BASELINE),("candidate",CANDIDATE)] {
        let ptx=compile_ptx_with_opts(source,CompileOptions {arch:Some("compute_120"),..Default::default()})?;
        let mut file=OpenOptions::new().write(true).create_new(true).open(format!("{variant}.ptx"))?;
        file.write_all(ptx.to_src().as_bytes())?;file.flush()?;
        let module=ctx.load_module(ptx)?;let function=module.load_function("up_fold")?;
        for block in [128,16,32,64,256] {
            assert!(function.max_threads_per_block()?>=block && thread_limit>=block);
            for scenario in corpus["full_scenarios"].as_array().unwrap() {
                assert!(function.shared_size_bytes()? as usize+4*scenario["nh_o"].as_u64().unwrap() as usize<=shared_limit as usize);
            }
        }
        resources.push(json!({"variant":variant,"source_fnv1a64":fnv(source.bytes()),"source_bytes":source.len(),
            "registers":function.num_regs()?,"local_bytes_per_thread":function.local_size_bytes()?,"static_shared_bytes":function.shared_size_bytes()?,
            "max_threads_per_block":function.max_threads_per_block()?,"scope":"capacity metadata only; no resource nonregression gate"}));
        modules.push(module);
    }
    emit(json!({"stage":"device","device":device,"architecture":"compute_120","production_block":128,"tested_blocks":[128,16,32,64,256],
        "max_shared_bytes_per_block_default":shared_limit,"max_threads_per_block":thread_limit,"resources":resources,
        "compile_options":"architecture only; all other production defaults","performance_measurement":false}))?;
    let full=[modules[0].load_function("up_fold")?,modules[1].load_function("up_fold")?];
    let file=OpenOptions::new().write(true).create_new(true).open("raw-results.jsonl")?;let mut raw=BufWriter::new(file);
    let totals=full_checks(&stream,&full,&corpus,&mut raw)?;raw.flush()?;stream.synchronize()?;ctx.check_err()?;
    drop(full);drop(modules);stream.synchronize()?;ctx.check_err()?;
    emit(json!({"stage":"complete","totals":totals,"required_exact":true,"all_observed_gpu_bits_exact":true,
        "production_block":128,"supplementary_blocks":[16,32,64,256],"input_immutability":true,"output_guards":true,
        "overflow_reported_separately":true,"nan_input_payload_guarantee":false,"raw_kernel_launches":0,
        "solver_executions":0,"performance_measurement":false,"candidate_accepted":false}))?;Ok(())
}
fn main() {
    if let Err(error)=run() {
        let _=emit(json!({"stage":"invalid","error":error.to_string(),"performance_measurement":false}));
        eprintln!("E030 direct invalid: {error}"); std::process::exit(1);
    }
}
