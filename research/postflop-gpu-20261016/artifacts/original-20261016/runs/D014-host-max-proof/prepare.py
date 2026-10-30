"""Copy exact oracle/corpus byte ranges; no checkout writes or GPU dependencies."""
from pathlib import Path
import hashlib
import json
import subprocess

HERE = Path(__file__).resolve().parent
REPO = Path(r"X:\Dev\GTOpen-gpu-research-20261016")
STORE = REPO / "crates/solver/src/store.rs"
PROOF = REPO / "crates/solver/tests/postflop_quantization_proof.rs"

def digest(data):
    return hashlib.sha256(data).hexdigest()

def copy_range(source, start, end, destination):
    blob = source.read_bytes()
    first, last = blob.index(start), blob.index(end, blob.index(start))
    piece = blob[first:last]
    (HERE / destination).write_bytes(piece)
    return {"source": str(source), "source_sha256": digest(blob),
            "start_byte": first, "end_byte_exclusive": last,
            "output": destination, "output_sha256": digest(piece), "bytes": len(piece)}

oracle = copy_range(STORE, b"/// Quantize `src` into i16 against", b"#[cfg(test)]", "baseline.rs")
corpus = copy_range(PROOF, b"struct Case {", b"#[test]", "corpus.rs")
constants = copy_range(PROOF, b"const SEED:", b"#[derive(Clone, Copy)]", "corpus_constants.rs")
manifest = {"diagnostic": "D014-host-max-proof", "oracle": oracle,
            "corpus": corpus, "corpus_constants": constants,
            "repo_head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip(),
            "rustc": subprocess.check_output(["rustc", "-Vv"], text=True),
            "compile_flags": ["--edition=2021", "-C", "opt-level=3", "-C", "codegen-units=1", "-C", "lto=thin"],
            "scope": "CPU encoder diagnostic only; no end-to-end performance claim"}
for name in ["candidate.rs", "prototype.rs", "prepare.py"]:
    manifest[name + "_sha256"] = digest((HERE / name).read_bytes())
(HERE / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
print(json.dumps(manifest, indent=2))
