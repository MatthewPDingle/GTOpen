//! Proposal only: copy into the isolated lab's solver/examples when approved.
//! No GPU, solver iterations, model generation, HTTP, or source-cache writes.
//! Usage: modeled_fixture SOURCE EQ_CACHE OUTPUT_ROOT OUTPUT MODE
//! MODE: fresh-coupled | fresh-legacy | resume | freeze-non-btn
use serde_json::{json, Value};
use solver::preflop::{equity::EquityTable, PreflopConfig, PreflopSolver, SeatProfile};
use std::{
    fs,
    io::{BufRead, BufReader, Write},
    path::{Path, PathBuf},
    sync::Arc,
};

fn header(path: &Path) -> Result<Value, String> {
    let mut f = BufReader::new(fs::File::open(path).map_err(|e| e.to_string())?);
    let mut magic = String::new();
    f.read_line(&mut magic).map_err(|e| e.to_string())?;
    if magic != "GTOPREFLOP1\n" && magic != "GTOPREFLOP2\n" {
        return Err("not a native preflop save".into());
    }
    let mut line = String::new();
    f.read_line(&mut line).map_err(|e| e.to_string())?;
    let h: Value = serde_json::from_str(&line).map_err(|e| e.to_string())?;
    if magic == "GTOPREFLOP2\n" && h.get("multiway_equity_model").is_none() {
        return Err("v2 header lacks model provenance".into());
    }
    Ok(h)
}

fn checked_output(root: &Path, output: &Path, source: &Path) -> Result<PathBuf, String> {
    let root = root.canonicalize().map_err(|e| e.to_string())?;
    let parent = output
        .parent()
        .ok_or("output needs a parent directory")?
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let output = parent.join(output.file_name().ok_or("output needs a filename")?);
    if !output.starts_with(&root)
        || output == source
        || output.exists()
        || PathBuf::from(format!("{}.tmp", output.display())).exists()
    {
        return Err(
            "output must be new, below the explicit research root, and distinct from source".into(),
        );
    }
    Ok(output)
}

fn run() -> Result<(), String> {
    let args: Vec<String> = std::env::args().collect();
    if args.len() != 6 {
        return Err("usage: SOURCE EQ_CACHE OUTPUT_ROOT OUTPUT MODE".into());
    }
    let source = Path::new(&args[1])
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let out = checked_output(Path::new(&args[3]), Path::new(&args[4]), &source)?;
    let mode = args[5].as_str();
    if !matches!(
        mode,
        "fresh-coupled" | "fresh-legacy" | "resume" | "freeze-non-btn"
    ) {
        return Err("unknown fixture mode".into());
    }
    let h = header(&source)?;
    let cfg: PreflopConfig =
        serde_json::from_value(h["config"].clone()).map_err(|e| e.to_string())?;
    let profiles: Vec<Option<SeatProfile>> =
        serde_json::from_value(h["seat_profiles"].clone()).map_err(|e| e.to_string())?;
    let frozen: Vec<bool> =
        serde_json::from_value(h["seat_frozen"].clone()).map_err(|e| e.to_string())?;
    let buttons: Vec<usize> = cfg
        .positions
        .iter()
        .enumerate()
        .filter_map(|(i, p)| (p == "BTN").then_some(i))
        .collect();
    if buttons.len() != 1 || profiles.len() != cfg.positions.len() || frozen.len() != profiles.len()
    {
        return Err("fixture needs one BTN and matching seat arrays".into());
    }
    let btn = buttons[0];
    if profiles[btn].is_some() || frozen[btn] {
        return Err("source BTN must be a learning solver seat".into());
    }
    for (i, profile) in profiles.iter().enumerate() {
        if i == btn {
            continue;
        }
        let site = h["seat_profiles"][i]["response"]["source_stats"]["dataset"]["site"].as_str();
        if profile.is_none() || site != Some("Ignition NL10 regular") {
            return Err(format!(
                "seat {i} is not an existing Ignition NL10 Pool-derived profile"
            ));
        }
    }
    if !h["hero"].is_null() || !h["hero_backup"].is_null() || !h["pre_hero_frozen"].is_null() {
        return Err("hero-mode fixture requires a separate explicit design".into());
    }
    let locks = h["point_locks"].as_array().ok_or("missing point_locks")?;
    if !locks.is_empty() {
        return Err("point-locked fixture requires a separate explicit design".into());
    }
    let original_model = h["multiway_equity_model"]
        .as_str()
        .unwrap_or("legacy_product");

    // Validate then privately copy the cache: load_or_build may otherwise write
    // the source cache on a failed load. Native construction stays unmodified.
    let bytes = fs::read(&args[2]).map_err(|e| e.to_string())?;
    if bytes.len() != 4 + 169 * 169 * 4 {
        return Err("invalid equity-cache length".into());
    }
    let samples = u32::from_le_bytes(bytes[..4].try_into().unwrap());
    if samples == 0 {
        return Err("zero-sample equity cache".into());
    }
    let values: Vec<f32> = bytes[4..]
        .chunks_exact(4)
        .map(|x| f32::from_le_bytes(x.try_into().unwrap()))
        .collect();
    if values
        .iter()
        .any(|x| !x.is_finite() || !(0.0..=1.0).contains(x))
    {
        return Err("invalid equity-cache value".into());
    }
    let private_cache = out.with_extension("equity.bin");
    let mut cache_file = fs::OpenOptions::new()
        .write(true)
        .create_new(true)
        .open(&private_cache)
        .map_err(|e| e.to_string())?;
    cache_file.write_all(&bytes).map_err(|e| e.to_string())?;
    drop(cache_file);
    let eq = Arc::new(EquityTable::load_or_build(
        private_cache.to_str().ok_or("non-UTF8 cache")?,
        samples,
    ));
    if fs::read(&private_cache).map_err(|e| e.to_string())? != bytes {
        return Err("private equity cache changed unexpectedly".into());
    }
    let mut s = if mode.starts_with("fresh-") {
        if frozen.iter().any(|x| *x) {
            return Err("cannot rebuild frozen strategies from a header".into());
        }
        let mut s = PreflopSolver::new(cfg.clone(), eq)?;
        s.set_multiway_equity_model(if mode == "fresh-coupled" {
            "coupled_deck_v1"
        } else {
            "legacy_product"
        })?;
        s.set_table(frozen.clone(), profiles.clone())?;
        s
    } else {
        PreflopSolver::load_game(source.to_str().ok_or("non-UTF8 source")?, eq)?
    };
    if s.cfg.realization == "calibrated" && s.fit.is_none() {
        return Err(
            "calibrated realization fit unavailable; use a lab CWD with pinned caches".into(),
        );
    }
    if mode == "freeze-non-btn" {
        if s.iteration == 0 {
            return Err("freeze requires a previously solved same-model source".into());
        }
        // Freeze via native API, retaining exact profiles. This pins adaptive
        // branches to their current averages; fixed profile branches stay fixed.
        // keep avoids resetting BTN's initial arenas; label this a derived control.
        s.set_table_keep((0..s.n).map(|i| i != btn).collect(), profiles.clone())?;
    }
    if serde_json::to_value(&s.cfg).map_err(|e| e.to_string())? != h["config"]
        || serde_json::to_value(&s.seat_profiles).map_err(|e| e.to_string())?
            != serde_json::to_value(&profiles).map_err(|e| e.to_string())?
    {
        return Err("config or typed policies changed".into());
    }
    if !mode.starts_with("fresh-") && s.multiway_equity_model() != original_model {
        return Err("learned arenas must retain their original payoff model".into());
    }
    let report = json!({"mode":mode,"source":source,"output":out,
        "model":s.multiway_equity_model(),"source_model":original_model,
        "iteration":s.iteration,"source_iteration":h["iteration"],"nodes":s.nodes.len(),
        "btn":btn,"frozen":s.seat_frozen,"profiles_preserved":true,
        "starting_arenas":if mode.starts_with("fresh-") {"new zero arenas"} else {"native source arenas"},
        "freeze_note":if mode=="freeze-non-btn" {"adaptive branches pinned using native set_table_keep; profile policies unchanged"} else {"none"}});
    s.save_game(out.to_str().ok_or("non-UTF8 output")?)?;
    let saved = header(&out)?;
    // Compare native typed values to native typed values. JSON Value's f32
    // serializer promotes to f64, whereas the save writer prints shortest f32
    // decimals; comparing those different intermediate forms causes false fails.
    let saved_profiles: Vec<Option<SeatProfile>> =
        serde_json::from_value(saved["seat_profiles"].clone()).map_err(|e| e.to_string())?;
    if serde_json::to_value(&saved_profiles).map_err(|e| e.to_string())?
        != serde_json::to_value(&profiles).map_err(|e| e.to_string())?
        || saved["seat_profiles"] != h["seat_profiles"]
        || saved["config"] != h["config"]
        || saved["iteration"] != json!(s.iteration)
        || saved["seat_frozen"] != json!(s.seat_frozen)
        || saved["point_locks"] != h["point_locks"]
        || !saved["hero"].is_null()
        || !saved["hero_backup"].is_null()
        || !saved["pre_hero_frozen"].is_null()
        || saved["multiway_equity_model"].as_str().unwrap_or("legacy_product")
            != s.multiway_equity_model()
    {
        return Err("saved fixture preservation check failed".into());
    }
    println!("FIXTURE {}", report);
    Ok(())
}
fn main() {
    if let Err(e) = run() {
        eprintln!("fixture refused: {e}");
        std::process::exit(1);
    }
}
