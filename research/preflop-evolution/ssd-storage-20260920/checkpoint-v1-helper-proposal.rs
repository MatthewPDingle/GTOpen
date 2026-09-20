//! Unapplied research example helper. Whole-study snapshots for RAM-backed training.
//! The process must exit on any restore error; partially imported state is not usable.
use super::Game;
use serde_json::{json,Value};
use std::{fs::{self,File,OpenOptions},io::{Read,Write,BufWriter},path::Path};

const MAGIC:u64=0x47544f434b503031;
fn err(s:&str)->String{s.to_owned()}
fn checksum(bytes:&[u8])->u64{bytes.iter().fold(0xcbf29ce484222325,|h,b|(h^u64::from(*b)).wrapping_mul(0x100000001b3))}
fn file_checksum(path:&Path)->Result<u64,String>{
    let mut f=File::open(path).map_err(|e|e.to_string())?;let mut buffer=[0u8;65536];let mut h=0xcbf29ce484222325u64;
    loop {let n=f.read(&mut buffer).map_err(|e|e.to_string())?;if n==0 {break;}
        for b in &buffer[..n]{h=(h^u64::from(*b)).wrapping_mul(0x100000001b3);}}
    Ok(h)
}
fn bounded_json(path:&Path)->Result<Value,String>{
    if fs::metadata(path).map_err(|e|e.to_string())?.len()>1024*1024{return Err(err("Oversized checkpoint index/identity"));}
    serde_json::from_slice(&fs::read(path).map_err(|e|e.to_string())?).map_err(|e|e.to_string())
}
fn write_new(path:&Path,bytes:&[u8])->Result<(),String>{
    let mut f=OpenOptions::new().write(true).create_new(true).open(path).map_err(|e|e.to_string())?;
    f.write_all(bytes).and_then(|_|f.sync_all()).map_err(|e|e.to_string())
}
pub(super) fn identity(subtree:&Path,manifest:&Path)->Result<Value,String>{
    let path=std::env::var("GTO_STUDY_IDENTITY_FILE").map_err(|_|err("Explicit externally verified SHA identity required"))?;
    let external=bounded_json(Path::new(&path))?;
    for key in ["executable_sha256","source_manifest_sha256","subtree_sha256","boards_sha256"] {
        let s=external[key].as_str().ok_or_else(||err("Incomplete external identity"))?;
        if s.len()!=64 || !s.bytes().all(|c|c.is_ascii_hexdigit()){return Err(err("Invalid SHA identity"));}
    }
    Ok(json!({"format":"gtopen-research-ram-checkpoint-v1","external_sha256":external,
        "executable_fnv64":file_checksum(&std::env::current_exe().map_err(|e|e.to_string())?)?,
        "subtree_fnv64":file_checksum(subtree)?,"boards_fnv64":file_checksum(manifest)?,
        "algorithm":"explicit-cfrplus-canonical-ram-v1","entry_cutoff_bits":(0.00001f64).to_bits()}))
}
fn raw_bytes(values:&[f64])->&[u8]{
    assert!(cfg!(target_endian="little"));
    unsafe{std::slice::from_raw_parts(values.as_ptr().cast(),values.len()*8)}
}
fn write_preflop(path:&Path,iteration:u32,values:&[f64])->Result<u64,String>{
    let payload=raw_bytes(values);let hash=checksum(payload);
    let mut f=BufWriter::new(OpenOptions::new().write(true).create_new(true).open(path).map_err(|e|e.to_string())?);
    for x in [MAGIC,u64::from(iteration),values.len() as u64,hash]{f.write_all(&x.to_le_bytes()).map_err(|e|e.to_string())?;}
    f.write_all(payload).and_then(|_|f.flush()).and_then(|_|f.get_ref().sync_all()).map_err(|e|e.to_string())?;
    Ok(hash)
}
fn read_preflop(path:&Path,iteration:u32,len:usize,hash:u64)->Result<Vec<f64>,String>{
    let mut f=File::open(path).map_err(|e|e.to_string())?;
    if f.metadata().map_err(|e|e.to_string())?.len()!=32+len as u64*8{return Err(err("Preflop record size mismatch"));}
    for expected in [MAGIC,u64::from(iteration),len as u64,hash]{
        let mut b=[0u8;8];f.read_exact(&mut b).map_err(|e|e.to_string())?;
        if u64::from_le_bytes(b)!=expected{return Err(err("Preflop record header mismatch"));}
    }
    let mut result=vec![0f64;len];assert!(cfg!(target_endian="little"));
    let payload=unsafe{std::slice::from_raw_parts_mut(result.as_mut_ptr().cast::<u8>(),len*8)};
    f.read_exact(payload).map_err(|e|e.to_string())?;
    if checksum(payload)!=hash{return Err(err("Preflop checksum mismatch"));}
    if result.iter().any(|v|!v.is_finite()){return Err(err("Nonfinite preflop state"));}
    Ok(result)
}
impl Game {
    fn checkpoint_values(&self)->Vec<f64>{
        self.regrets.iter().chain(&self.sums).chain(&self.sigma).flat_map(|n|n.iter().flatten()).copied()
            .chain(self.weights.iter().flatten().copied()).chain(std::iter::once(self.z)).chain(self.board_weights.iter().copied()).collect()
    }
    fn checkpoint_shape(&self)->Value{
        json!({"preflop":self.regrets.iter().map(|n|n.iter().map(Vec::len).collect::<Vec<_>>()).collect::<Vec<_>>(),
            "weights":self.weights.iter().map(Vec::len).collect::<Vec<_>>(),"boards":self.boards,
            "continuation_counts":self.continuations.iter().map(Vec::len).collect::<Vec<_>>()})
    }
    pub(super) fn checkpoint_save(&self,root:&Path,completed:u32,identity:&Value)->Result<(),String>{
        if completed==0 || self.continuations.iter().flatten().any(|c|c.gpu.disk_backed){return Err(err("Snapshot requires completed RAM-backed study"));}
        let values=self.checkpoint_values();
        let count=self.continuations.iter().map(Vec::len).sum::<usize>();
        let payload=self.continuations.iter().flatten().map(|c|c.gpu.storage_bytes).sum::<u64>()+values.len() as u64*8;
        let cap:u64=std::env::var("GTO_CHECKPOINT_WRITE_CAP").map_err(|_|err("Explicit checkpoint write budget required"))?
            .parse().map_err(|_|err("Invalid checkpoint budget"))?;
        // Include record headers and a bounded one-MiB index plus completion marker.
        if payload+count as u64*72+32+1024*1024+16>cap{return Err(err("Checkpoint write budget exceeded"));}
        fs::create_dir(root).map_err(|e|e.to_string())?;
        let mut entries=vec![];
        for (key,c) in self.continuations.iter().flatten().enumerate(){
            entries.push(c.gpu.checkpoint_export(root,key as u64,completed)?);
        }
        let hash=write_preflop(&root.join("preflop.bin"),completed,&values)?;
        let reopened=read_preflop(&root.join("preflop.bin"),completed,values.len(),hash)?;
        if raw_bytes(&reopened)!=raw_bytes(&values){return Err(err("Preflop reopen changed bits"));}
        let index=json!({"identity":identity,"iteration":completed,"shape":self.checkpoint_shape(),
            "preflop_hash":hash,"entries":entries,"payload_bytes":payload});
        let encoded=serde_json::to_vec(&index).map_err(|e|e.to_string())?;
        if encoded.len()>1024*1024{return Err(err("Checkpoint index exceeds budget"));}
        write_new(&root.join("index.json"),&encoded)?;
        if fs::read(root.join("index.json")).map_err(|e|e.to_string())?!=encoded{return Err(err("Index reopen mismatch"));}
        // Every record was independently reloaded and checked before this final publication.
        write_new(&root.join("complete"),format!("{:016x}",checksum(&encoded)).as_bytes())?;
        println!("STUDY_CHECKPOINT {}",json!({"saved":root,"iteration":completed,"payload_bytes":payload}));
        Ok(())
    }
    pub(super) fn checkpoint_load(&mut self,root:&Path,identity:&Value)->Result<u32,String>{
        let marker=root.join("complete");
        if fs::metadata(&marker).map_err(|e|e.to_string())?.len()!=16{return Err(err("Incomplete checkpoint"));}
        let mark=fs::read(&marker).map_err(|e|e.to_string())?;
        let index=bounded_json(&root.join("index.json"))?;
        let encoded=fs::read(root.join("index.json")).map_err(|e|e.to_string())?;
        if mark!=format!("{:016x}",checksum(&encoded)).as_bytes(){return Err(err("Checkpoint index checksum mismatch"));}
        if index["identity"]!=*identity || index["shape"]!=self.checkpoint_shape(){return Err(err("Checkpoint identity or rebuilt shape mismatch"));}
        let raw=index["iteration"].as_u64().ok_or_else(||err("Missing checkpoint iteration"))?;
        if raw==0 || raw>=u32::MAX as u64{return Err(err("Invalid checkpoint iteration"));}
        let t=raw as u32;let expected=self.checkpoint_values();
        let hash=index["preflop_hash"].as_u64().ok_or_else(||err("Missing preflop checksum"))?;
        let values=read_preflop(&root.join("preflop.bin"),t,expected.len(),hash)?;
        let learned=self.regrets.iter().flat_map(|n|n.iter()).map(Vec::len).sum::<usize>()*3;
        if raw_bytes(&values[learned..])!=raw_bytes(&expected[learned..]){return Err(err("Fixed weights or normalizer changed"));}
        let entries:Vec<[u64;8]>=serde_json::from_value(index["entries"].clone()).map_err(|e|e.to_string())?;
        let count=self.continuations.iter().map(Vec::len).sum::<usize>();
        if entries.len()!=count{return Err(err("Missing or unexpected continuation record"));}
        let mut expected_files=std::collections::BTreeSet::from(["index.json".to_owned(),"complete".to_owned(),"preflop.bin".to_owned()]);
        for key in 0..count {expected_files.insert(format!("entry-{key}-generation-0.bin"));}
        let mut found=std::collections::BTreeSet::new();
        for item in fs::read_dir(root).map_err(|e|e.to_string())? {
            let item=item.map_err(|e|e.to_string())?;
            if !item.file_type().map_err(|e|e.to_string())?.is_file(){return Err(err("Unexpected non-file checkpoint entry"));}
            found.insert(item.file_name().to_str().ok_or_else(||err("Invalid checkpoint filename"))?.to_owned());
        }
        if found!=expected_files{return Err(err("Missing or unexpected checkpoint file"));}
        let payload=self.continuations.iter().flatten().map(|c|c.gpu.storage_bytes).sum::<u64>()+values.len() as u64*8;
        if index["payload_bytes"].as_u64()!=Some(payload){return Err(err("Checkpoint payload accounting mismatch"));}
        for (key,(c,descriptor)) in self.continuations.iter_mut().flatten().zip(entries).enumerate(){
            c.gpu.checkpoint_import(root,key as u64,t,descriptor)?;
        }
        let mut it=values[..learned].iter();
        for state in [&mut self.regrets,&mut self.sums,&mut self.sigma]{for n in state {for a in n {for v in a {*v=*it.next().unwrap();}}}}
        assert!(it.next().is_none());
        println!("STUDY_CHECKPOINT {}",json!({"restored":root,"iteration":t,"payload_bytes":payload}));
        Ok(t)
    }
}
