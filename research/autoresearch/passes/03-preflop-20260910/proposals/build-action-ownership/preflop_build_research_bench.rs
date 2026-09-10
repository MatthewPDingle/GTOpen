//! Frozen build/load harness proposal. One timed operation per process; no GPU.
//! CLI: INPUT MODE EQ_CACHE FIT_CACHE OUTPUT_ROOT ROUNDTRIP_OUTPUT
//! MODE: fresh-from-config | load. All output paths must be new research paths.
use serde::Serialize;
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver, SeatProfile};
use std::{
    fs,
    io::{BufRead, BufReader, Read, Write},
    path::{Path, PathBuf},
    sync::Arc,
    time::Instant,
};

struct Digest(u64);
impl Digest {
    fn new() -> Self {
        Self(0xcbf29ce484222325)
    }
    fn bytes(&mut self, bytes: &[u8]) {
        for b in bytes {
            self.0 = (self.0 ^ u64::from(*b)).wrapping_mul(0x100000001b3);
        }
    }
    fn hex(&self) -> String {
        format!("{:016x}", self.0)
    }
}
impl Write for Digest {
    fn write(&mut self, bytes: &[u8]) -> std::io::Result<usize> {
        self.bytes(bytes);
        Ok(bytes.len())
    }
    fn flush(&mut self) -> std::io::Result<()> {
        Ok(())
    }
}
fn typed_hash<T: Serialize>(value: &T) -> Result<String, String> {
    let mut hash = Digest::new();
    serde_json::to_writer(&mut hash, value).map_err(|e| e.to_string())?;
    Ok(hash.hex())
}
fn bytes_hash(bytes: &[u8]) -> String {
    let mut d = Digest::new();
    d.bytes(bytes);
    d.hex()
}

fn read_header<R: BufRead>(r: &mut R) -> Result<Value, String> {
    let mut magic = [0u8; 12];
    r.read_exact(&mut magic).map_err(|e| e.to_string())?;
    if &magic != b"GTOPREFLOP1\n" && &magic != b"GTOPREFLOP2\n" {
        return Err("not a native preflop save".into());
    }
    let mut line = Vec::new();
    r.read_until(b'\n', &mut line).map_err(|e| e.to_string())?;
    if line.last() != Some(&b'\n') {
        return Err("unterminated native header".into());
    }
    let h: Value = serde_json::from_slice(&line).map_err(|e| e.to_string())?;
    if &magic == b"GTOPREFLOP2\n" && h.get("multiway_equity_model").is_none() {
        return Err("v2 model provenance missing".into());
    }
    Ok(h)
}
fn file_header(path: &Path) -> Result<Value, String> {
    read_header(&mut BufReader::new(
        fs::File::open(path).map_err(|e| e.to_string())?,
    ))
}
fn checked_output(root: &Path, path: &Path, input: &Path) -> Result<PathBuf, String> {
    let root = root.canonicalize().map_err(|e| e.to_string())?;
    let parent = path
        .parent()
        .ok_or("output needs a parent")?
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let out = parent.join(path.file_name().ok_or("output needs a filename")?);
    if !out.starts_with(root)
        || out == input
        || out.exists()
        || PathBuf::from(format!("{}.tmp", out.display())).exists()
    {
        return Err("output must be new, beneath research root, and distinct from input".into());
    }
    Ok(out)
}

// Stream the actual native round-trip arenas, including optional hero backups.
// Do not use arena_snapshot: it clones both multi-gigabyte arenas into RAM.
fn arena_file_hash(path: &Path) -> Result<(Value, Value), String> {
    let mut r = BufReader::new(fs::File::open(path).map_err(|e| e.to_string())?);
    let h = read_header(&mut r)?;
    let count = if h.get("hero_backup").is_some_and(|x| !x.is_null()) {
        4
    } else {
        2
    };
    let mut combined = Digest::new();
    let mut arrays = Vec::new();
    let mut buffer = vec![0u8; 1024 * 1024];
    for index in 0..count {
        let mut word = [0u8; 8];
        r.read_exact(&mut word).map_err(|e| e.to_string())?;
        let elements = u64::from_le_bytes(word);
        let mut remaining = elements.checked_mul(4).ok_or("arena byte overflow")?;
        let mut digest = Digest::new();
        let mut nonzero_bytes = 0u64;
        combined.bytes(&word);
        while remaining > 0 {
            let take = remaining.min(buffer.len() as u64) as usize;
            r.read_exact(&mut buffer[..take])
                .map_err(|e| e.to_string())?;
            digest.bytes(&buffer[..take]);
            combined.bytes(&buffer[..take]);
            nonzero_bytes += buffer[..take].iter().filter(|&&b| b != 0).count() as u64;
            remaining -= take as u64;
        }
        arrays.push(json!({"index":index,"elements":elements,"hash":digest.hex(),"nonzero_bytes":nonzero_bytes}));
    }
    let mut extra = [0u8; 1];
    if r.read(&mut extra).map_err(|e| e.to_string())? != 0 {
        return Err("unexpected bytes after native arenas".into());
    }
    Ok((
        h,
        json!({"combined_hash":combined.hex(),"arrays":arrays,"hash_algorithm":"FNV-1a64 over exact native bytes; combined includes array lengths","buffer_bytes":buffer.len()}),
    ))
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 7 {
        return Err("usage: INPUT MODE EQ_CACHE FIT_CACHE OUTPUT_ROOT ROUNDTRIP_OUTPUT".into());
    }
    let input = Path::new(&args[1])
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let mode = args[2].as_str();
    if !matches!(mode, "fresh-from-config" | "load") {
        return Err("unknown mode".into());
    }
    let output = checked_output(Path::new(&args[5]), Path::new(&args[6]), &input)?;
    let eq_path = Path::new(&args[3])
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let fit_path = Path::new(&args[4])
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let eq_bytes = fs::read(&eq_path).map_err(|e| e.to_string())?;
    let fit_bytes = fs::read(&fit_path).map_err(|e| e.to_string())?;
    if eq_bytes.len() != 4 + 169 * 169 * 4 {
        return Err("invalid equity cache size".into());
    }
    let samples = u32::from_le_bytes(eq_bytes[..4].try_into().unwrap());
    if samples == 0 {
        return Err("zero-sample cache".into());
    }
    for bytes in eq_bytes[4..].chunks_exact(4) {
        let x = f32::from_le_bytes(bytes.try_into().unwrap());
        if !x.is_finite() || !(0.0..=1.0).contains(&x) {
            return Err("invalid equity cache value".into());
        }
    }
    let _: Value = serde_json::from_slice(&fit_bytes).map_err(|e| e.to_string())?;
    std::env::set_var("REALIZATION_FIT", &fit_path);
    // Never let load_or_build write the pinned source cache.
    let private_cache = output.with_extension("equity.bin");
    let mut file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&private_cache)
        .map_err(|e| e.to_string())?;
    file.write_all(&eq_bytes).map_err(|e| e.to_string())?;
    drop(file);
    let eq = Arc::new(EquityTable::load_or_build(
        private_cache.to_str().ok_or("non-UTF8 cache path")?,
        samples,
    ));
    if fs::read(&private_cache).map_err(|e| e.to_string())? != eq_bytes {
        return Err("private equity cache changed".into());
    }

    let mut prefix = [0u8; 12];
    let native = fs::File::open(&input)
        .map_err(|e| e.to_string())?
        .read_exact(&mut prefix)
        .is_ok()
        && (&prefix == b"GTOPREFLOP1\n" || &prefix == b"GTOPREFLOP2\n");
    if mode == "load" && !native {
        return Err("load mode requires native .gtop input".into());
    }
    // Input JSON parsing is setup, not part of the fresh constructor benchmark.
    let cfg = if mode == "fresh-from-config" {
        let value = if native {
            file_header(&input)?
        } else {
            serde_json::from_slice(&fs::read(&input).map_err(|e| e.to_string())?)
                .map_err(|e| e.to_string())?
        };
        Some(
            serde_json::from_value::<PreflopConfig>(value.get("config").unwrap_or(&value).clone())
                .map_err(|e| e.to_string())?,
        )
    } else {
        None
    };

    let started = Instant::now();
    let s = if let Some(cfg) = cfg {
        PreflopSolver::new(cfg, eq)?
    } else {
        PreflopSolver::load_game(input.to_str().ok_or("non-UTF8 input")?, eq)?
    };
    let operation_ms = started.elapsed().as_secs_f64() * 1000.0;
    if s.cfg.realization == "calibrated" && (s.fit.is_none() || !s.realization_note.is_empty()) {
        return Err("pinned calibrated fit was not loaded".into());
    }
    println!(
        "BUILD_BENCH {}",
        json!({"phase":"timed","mode":mode,"operation_ms":operation_ms,
        "nodes":s.nodes.len(),"iteration":s.iteration,"model":s.multiway_equity_model()})
    );

    // Everything below is untimed verification, never counted as build/load work.
    let topology = topology_and_action_storage(&s);
    let config_hash = typed_hash(&s.cfg)?;
    let profile_hash = typed_hash(&s.seat_profiles)?;
    let save_start = Instant::now();
    s.save_game(output.to_str().ok_or("non-UTF8 output")?)?;
    let verification_save_ms = save_start.elapsed().as_secs_f64() * 1000.0;
    let (saved, arenas) = arena_file_hash(&output)?;
    let saved_cfg: PreflopConfig =
        serde_json::from_value(saved["config"].clone()).map_err(|e| e.to_string())?;
    let saved_profiles: Vec<Option<SeatProfile>> =
        serde_json::from_value(saved["seat_profiles"].clone()).map_err(|e| e.to_string())?;
    let mut saved_locks: Vec<(u32, Vec<f32>)> =
        serde_json::from_value(saved["point_locks"].clone()).map_err(|e| e.to_string())?;
    saved_locks.sort_by_key(|(node, _)| *node);
    let point_lock_hash = typed_hash(&saved_locks)?;
    if typed_hash(&saved_cfg)? != config_hash
        || typed_hash(&saved_profiles)? != profile_hash
        || saved["iteration"] != json!(s.iteration)
        || saved["seat_frozen"] != json!(s.seat_frozen)
        || saved["hero"] != json!(s.hero)
        || saved["multiway_equity_model"]
            .as_str()
            .unwrap_or("legacy_product")
            != s.multiway_equity_model()
    {
        return Err("native round-trip identity changed".into());
    }
    if mode == "fresh-from-config"
        && (s.iteration != 0
            || s.seat_profiles.iter().any(Option::is_some)
            || arenas["arrays"]
                .as_array()
                .unwrap()
                .iter()
                .any(|a| a["nonzero_bytes"] != json!(0)))
    {
        return Err("fresh constructor did not produce unmodeled zero arenas".into());
    }
    if fs::read(&eq_path).map_err(|e| e.to_string())? != eq_bytes
        || fs::read(&fit_path).map_err(|e| e.to_string())? != fit_bytes
    {
        return Err("pinned source cache changed during run".into());
    }
    println!(
        "BUILD_BENCH {}",
        json!({"phase":"verified","mode":mode,"input":input,
        "operation_ms":operation_ms,"topology":topology,"typed_config_hash":config_hash,
        "typed_profile_hash":profile_hash,"typed_hash_algorithm":"FNV-1a64 of native typed serde JSON",
        "native_arenas":arenas,"iteration":s.iteration,"frozen":s.seat_frozen,"hero":s.hero,
        "point_lock_hash":point_lock_hash,"point_lock_count":saved_locks.len(),
        "hero_backup_meta":saved["hero_backup"],"pre_hero_frozen":saved["pre_hero_frozen"],
        "model":s.multiway_equity_model(),"roundtrip_path":output,
        "roundtrip_bytes":fs::metadata(&output).map_err(|e|e.to_string())?.len(),
        "untimed_verification_save_ms":verification_save_ms,"equity_cache":eq_path,
        "equity_cache_hash":bytes_hash(&eq_bytes),"equity_samples":samples,
        "fit_cache":fit_path,"fit_cache_hash":bytes_hash(&fit_bytes),
        "fresh_mode_note":"constructor only: source config retained, profiles/model/iteration from a native input are not transported"})
    );
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("build benchmark refused: {e}");
        std::process::exit(1);
    }
}

// Copy into the benchmark example; invoke AFTER stopping the build/load timer.
// No tree-sized serialization or extra arena copies.
fn topology_and_action_storage(s: &solver::preflop::PreflopSolver) -> serde_json::Value {
    struct Digest(u64);
    impl Digest {
        fn bytes(&mut self, bytes: &[u8]) {
            for b in bytes {
                self.0 = (self.0 ^ u64::from(*b)).wrapping_mul(0x100000001b3);
            }
        }
        fn number(&mut self, value: u64) {
            self.bytes(&value.to_le_bytes());
        }
        fn text(&mut self, value: &str) {
            self.number(value.len() as u64);
            self.bytes(value.as_bytes());
        }
    }
    let mut hash = Digest(0xcbf29ce484222325);
    let mut action_nodes = 0usize;
    let mut edges = 0usize;
    let mut vec_bytes = 0usize;
    let mut string_len = 0usize;
    let mut string_capacity = 0usize;
    hash.number(s.nodes.len() as u64);
    for (i, node) in s.nodes.iter().enumerate() {
        for value in [
            node.kind as u64,
            node.actor as u64,
            node.child_start as u64,
            node.live as u64,
            node.winner as u64,
            node.data_off as u64,
            node.aggressor as u64,
            node.bucket as u64,
            node.raises as u64,
            node.raised as u64,
            node.pot.to_bits(),
        ] {
            hash.number(value);
        }
        hash.number(node.invested.len() as u64);
        for value in &node.invested {
            hash.number(value.to_bits());
        }
        hash.number(node.r.len() as u64);
        for value in &node.r {
            hash.number(value.to_bits() as u64);
        }
        hash.number(node.posf.len() as u64);
        for value in &node.posf {
            hash.number(value.to_bits() as u64);
        }
        hash.number(node.actions.len() as u64);
        if !node.actions.is_empty() {
            action_nodes += 1;
        }
        vec_bytes += node.actions.capacity() * std::mem::size_of::<solver::preflop::PAction>();
        for (a, action) in node.actions.iter().enumerate() {
            hash.text(&action.kind);
            hash.number(action.to.to_bits());
            hash.text(&action.label);
            hash.number(s.child(i, a) as u64);
            string_len += action.kind.len() + action.label.len();
            string_capacity += action.kind.capacity() + action.label.capacity();
            edges += 1;
        }
    }
    assert_eq!(
        edges + 1,
        s.nodes.len(),
        "native tree must have one incoming edge per non-root node"
    );
    serde_json::json!({"topology_hash":format!("{:016x}",hash.0),"nodes":s.nodes.len(),
        "action_nodes":action_nodes,"edges":edges,"action_vec_capacity_bytes":vec_bytes,
        "action_string_len_bytes":string_len,"action_string_capacity_bytes":string_capacity,
        "action_retained_bytes":vec_bytes+string_capacity})
}
