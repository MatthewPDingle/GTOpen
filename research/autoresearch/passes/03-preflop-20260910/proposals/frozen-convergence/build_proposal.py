from pathlib import Path
import difflib, hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = Path('T:/Dev/GTOpen/target/autoresearch/preflop-20260910')
rel = 'crates/solver/examples/preflop_convergence_control.rs'
source = (HERE / 'preflop_convergence_control.rs').read_text(encoding='utf-8')
cargo_path = ROOT / 'crates/solver/Cargo.toml'
cargo = cargo_path.read_text(encoding='utf-8')
assert 'name = "preflop_convergence_control"' not in cargo
new_cargo = cargo.rstrip() + '\n\n[[example]]\nname = "preflop_convergence_control"\nrequired-features = ["gpu"]\n'
patch = ''.join(difflib.unified_diff([], source.splitlines(True), '/dev/null', 'b/' + rel))
patch += ''.join(difflib.unified_diff(cargo.splitlines(True), new_cargo.splitlines(True), 'a/crates/solver/Cargo.toml', 'b/crates/solver/Cargo.toml'))
(HERE / 'add-convergence-harness.patch').write_text(patch, encoding='utf-8', newline='\n')
files = ['crates/server/src/main.rs', 'crates/solver/src/preflop/mod.rs', 'crates/solver/src/preflop/save.rs', 'crates/solver/src/preflop/equity.rs', 'crates/solver/Cargo.toml']
manifest = {'status': 'proposal; not compiled or run', 'source_sha256': {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}, 'proposal_sha256': hashlib.sha256((HERE / 'preflop_convergence_control.rs').read_bytes()).hexdigest()}
(HERE / 'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
assert cargo_path.read_text(encoding='utf-8') == cargo
