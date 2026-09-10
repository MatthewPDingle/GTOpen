from pathlib import Path
import difflib, hashlib, json, subprocess

HERE = Path(__file__).resolve().parent
ROOT = Path('T:/Dev/GTOpen/target/autoresearch/preflop-20260910')
REL = 'crates/solver/examples/preflop_module_resources.rs'
source = (HERE/'preflop_module_resources.rs').read_text(encoding='utf-8')
cargo_path = ROOT/'crates/solver/Cargo.toml'
cargo = cargo_path.read_text(encoding='utf-8')
assert 'name = "preflop_module_resources"' not in cargo
updated = cargo.rstrip()+'\n\n[[example]]\nname = "preflop_module_resources"\nrequired-features = ["gpu"]\n'
patch = ''.join(difflib.unified_diff([],source.splitlines(True),'/dev/null','b/'+REL))
patch += ''.join(difflib.unified_diff(cargo.splitlines(True),updated.splitlines(True),'a/crates/solver/Cargo.toml','b/crates/solver/Cargo.toml'))
(HERE/'add-module-resources.patch').write_text(patch,encoding='utf-8',newline='\n')
kernel = 'crates/solver/src/preflop/kernels.cu'
original = subprocess.check_output(['git','show',f'1b8fc3f:{kernel}'],cwd=ROOT)
manifest = {'status':'proposal only; not compiled or run','harness_sha256':hashlib.sha256((HERE/'preflop_module_resources.rs').read_bytes()).hexdigest(),
    'original_revision':subprocess.check_output(['git','rev-parse','1b8fc3f'],cwd=ROOT).decode().strip(),
    'original_kernel_sha256':hashlib.sha256(original).hexdigest(),
    'observed_current_revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
    'observed_current_kernel_sha256':hashlib.sha256((ROOT/kernel).read_bytes()).hexdigest(),
    'cargo_sha256':hashlib.sha256(cargo_path.read_bytes()).hexdigest()}
(HERE/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
assert cargo_path.read_text(encoding='utf-8') == cargo
