from pathlib import Path
import difflib, hashlib, json

HERE = Path(__file__).resolve().parent
before = (HERE / 'preflop_convergence_control.rs').read_text(encoding='utf-8')
after = before.replace('equity::EquityTable, gpu::PreflopGpu, PreflopSolver', 'equity::EquityTable, gpu::PreflopGpu, PreflopSolver, RealizationFit')
after = after.replace('fn learning_gap(', '''fn start_summary(s: &PreflopSolver) -> serde_json::Value {
    let profiles = serde_json::to_vec(&s.seat_profiles).expect("validated profile serialization");
    json!({"config":s.cfg,"iteration":s.iteration,"model":s.multiway_equity_model(),
        "hero":s.hero,"frozen":s.seat_frozen,"live_seats":s.live_seats(),
        "profiles_json_bytes":profiles.len(),
        "profiles_fnv1a64":format!("{:016x}",hash_bytes(0xcbf29ce484222325, &profiles))})
}
fn learning_gap(''', 1)
anchor = '    let input_hash = file_hash(&input)?;\n'
replacement = anchor + '''    // Native saves retain the realization mode but not the fitted table.
    // Require an explicit frozen path even for a raw fixture, so the paired
    // environment is fully declared and no CWD fallback is involved.
    let fit_env = std::env::var("REALIZATION_FIT")
        .map_err(|_| "set REALIZATION_FIT to the frozen calibration artifact")?;
    let fit_path = fs::canonicalize(&fit_env).map_err(|e|format!("REALIZATION_FIT: {e}"))?;
    RealizationFit::load(fit_path.to_str().ok_or("non-UTF8 fit path")?)?;
    let fit_hash = file_hash(&fit_path)?;
'''
assert after.count(anchor) == 1
after = after.replace(anchor, replacement)
after = after.replace('"harness":"convergence-control-v1"', '"harness":"convergence-control-v2"')
after = after.replace('"start_state":state(&s),', '"start_state":start_summary(&s),\n        "realization_fit_path":fit_path,"realization_fit_fnv1a64":fit_hash,')
anchor = '    if file_hash(&input)? != input_hash || file_hash(cache)? != cache_hash { return Err("frozen input/cache changed during trajectory".into()); }'
replacement = '''    if file_hash(&input)? != input_hash || file_hash(cache)? != cache_hash || file_hash(&fit_path)? != fit_hash {
        return Err("frozen input/equity cache/calibration changed during trajectory".into());
    }'''
assert after.count(anchor) == 1
after = after.replace(anchor,replacement)
rel = 'crates/solver/examples/preflop_convergence_control.rs'
(HERE/'preflop_convergence_control_v2.rs').write_text(after,encoding='utf-8',newline='\n')
(HERE/'provenance-v2.patch').write_text(''.join(difflib.unified_diff(before.splitlines(True),after.splitlines(True),'a/'+rel,'b/'+rel)),encoding='utf-8',newline='\n')
(HERE/'provenance-v2-manifest.json').write_text(json.dumps({'v1_sha256':hashlib.sha256(before.encode()).hexdigest(),'v2_sha256':hashlib.sha256(after.encode()).hexdigest(),'status':'proposal only, not compiled or run'},indent=2)+'\n',encoding='utf-8')
