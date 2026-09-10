from pathlib import Path
import difflib
import hashlib
import json

out = Path(__file__).parent
repo = Path(r'T:\Dev\GTOpen\target\autoresearch\preflop-20260910')
source = repo / 'crates/solver/examples/preflop_research_bench.rs'
raw = source.read_bytes()
expected = '357dfa690981df26dc7e8a872c58addfeb598b45adda7c97957a087822359de4'
assert hashlib.sha256(raw).hexdigest() == expected, 'Frozen harness differs; stop rather than silently derive another control.'
old = raw.decode('utf-8').replace('\r\n','\n')
new = old.replace('//! Frozen pass-3 harness: isolated fixed-state timings, never calls the app API.',
                  '//! Separate frozen budget-control harness derived from pass3; never calls the app API.\n//! Usage: preflop_budget_control INPUT ITERATIONS BUDGET_MB [--legacy]')
helper = '''fn memory_probe(context: &Option<Arc<cudarc::driver::CudaContext>>, stage: &str) {
    if let Some(ctx) = context {
        match ctx.mem_get_info() {
            Ok((free, total)) => println!("GPU_MEMORY {}", json!({
                "stage":stage,"free_bytes":free,"total_bytes":total,
                "used_bytes":total.saturating_sub(free),
                "scope":"CUDA driver free/total snapshot, not an OS residency or eviction measurement"
            })),
            Err(err) => println!("GPU_MEMORY {}", json!({"stage":stage,"query_error":format!("{err:?}")})),
        }
    }
}
'''
new = new.replace('fn main() {\n',helper+'fn main() {\n')
new = new.replace('    let input = &args[1];\n', '''    assert!(args.len() >= 4, "usage: INPUT ITERATIONS BUDGET_MB [--legacy]");
    let input = &args[1];
''')
new = new.replace('    let count: u32 = args[2].parse().unwrap();\n', '''    let count: u32 = args[2].parse().unwrap();
    assert!((1..=8).contains(&count), "bounded control requires 1..8 iterations");
    let budget: u64 = args[3].parse().unwrap();
    assert!([19000,21000,23000].contains(&budget), "control budget must be 19000,21000,23000 decimal MB");
    let memory_ctx = if std::env::var("PREFLOP_GPU_MEMORY_PROBE").as_deref() == Ok("1") {
        let t = Instant::now();
        let ctx = cudarc::driver::CudaContext::new(0).unwrap();
        println!("GPU_MEMORY {}",json!({"stage":"probe_context_created","ms":t.elapsed().as_secs_f64()*1000.0}));
        Some(ctx)
    } else { None };
    let roundtrip = format!("target/research-budget-control-roundtrip-{budget}.gtop");
''')
anchor = '    let t = Instant::now();\n    let mut g = PreflopGpu::new(&s, 23000).unwrap();'
assert new.count(anchor) == 1
new = new.replace(anchor, '''    memory_probe(&memory_ctx,"before_gpu_constructor");
    let t = Instant::now();
    let mut g = PreflopGpu::new(&s, budget).unwrap();''')
new = new.replace('    let init_ms = t.elapsed().as_secs_f64() * 1000.;\n',
                  '    let init_ms = t.elapsed().as_secs_f64() * 1000.;\n    memory_probe(&memory_ctx,"after_gpu_constructor");\n')
new = new.replace('"phase":"init","nodes":',
                  '"phase":"init","budget_mb":budget,"harness":"budget-control-v1","memory_probe":memory_ctx.is_some(),"nodes":')
new = new.replace('    let t = Instant::now();\n    let (gaps, evs) = g.gaps_and_evs().unwrap();',
                  '    memory_probe(&memory_ctx,"after_iterations");\n    let t = Instant::now();\n    let (gaps, evs) = g.gaps_and_evs().unwrap();')
new = new.replace('    let check_ms = t.elapsed().as_secs_f64() * 1000.;\n',
                  '    let check_ms = t.elapsed().as_secs_f64() * 1000.;\n    memory_probe(&memory_ctx,"after_check");\n')
new = new.replace('    drop(regret); drop(strategy); drop(g);\n',
                  '    drop(regret); drop(strategy); drop(g);\n    memory_probe(&memory_ctx,"after_gpu_drop");\n')
assert new.count('"target/research-roundtrip.gtop"') == 3
new = new.replace('"target/research-roundtrip.gtop"','&roundtrip')
new = new.replace('"phase":"result","iteration":','"phase":"result","budget_mb":budget,"harness":"budget-control-v1","iteration":')
(out / 'preflop_budget_control.rs').write_text(new,encoding='utf-8',newline='\n')
derived = ''.join(difflib.unified_diff(old.splitlines(True),new.splitlines(True),
    fromfile='frozen/preflop_research_bench.rs',tofile='proposal/preflop_budget_control.rs'))
(out / 'derivation.diff').write_text(derived,encoding='utf-8',newline='\n')
newpath='crates/solver/examples/preflop_budget_control.rs'
addfile=''.join(difflib.unified_diff([],new.splitlines(True),fromfile='/dev/null',tofile=f'b/{newpath}'))
cargo_path=repo/'crates/solver/Cargo.toml'
cargo_raw=cargo_path.read_bytes()
cargo=cargo_raw.decode('utf-8').replace('\r\n','\n')
assert 'name = "preflop_budget_control"' not in cargo
updated=cargo.rstrip()+'\n\n[[example]]\nname = "preflop_budget_control"\nrequired-features = ["gpu"]\n'
manifest_patch=''.join(difflib.unified_diff(cargo.splitlines(True),updated.splitlines(True),
    fromfile='a/crates/solver/Cargo.toml',tofile='b/crates/solver/Cargo.toml'))
(out/'add-budget-harness.patch').write_text(addfile+manifest_patch,encoding='utf-8',newline='\n')
assert source.read_bytes()==raw and cargo_path.read_bytes()==cargo_raw
(out/'manifest.json').write_text(json.dumps({
    'derived_from':str(source),'frozen_source_sha256':expected,
    'proposal_harness_sha256':hashlib.sha256((out/'preflop_budget_control.rs').read_bytes()).hexdigest(),
    'cargo_baseline_sha256':hashlib.sha256(cargo_raw).hexdigest(),
    'scope':'Separate example proposal; original frozen harness and active source unchanged. No build/hardware execution.',
},indent=2)+'\n',encoding='utf-8')
print('Separate frozen-derived budget harness proposal generated; original and active source untouched.')
