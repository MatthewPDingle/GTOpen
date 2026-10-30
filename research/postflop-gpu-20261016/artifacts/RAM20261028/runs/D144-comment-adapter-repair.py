import sys, re, json, shutil, urllib.request
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'epoch'))
import common as h
H = ROOT / 'runs/D144-incidence'
h.custody()
assert h.read(H / 'execution/rustc.exit.json')['returncode'] == 1
assert not (H / 'output').exists() and not (ROOT / 'runs/D144R1').exists()
original = (H / 'probe.rs').read_text(encoding='utf-8')
revised, count = re.subn(r'^//!', '//', original, flags=re.MULTILINE)
assert count == 7
(H / 'probe-r2.rs').write_text(revised, encoding='utf-8', newline='\n')
review = {'at': h.now(), 'failure': 'Rust E0753: copied inner documentation comments followed the standalone prefix items.', 'correction': 'Convert exactly seven leading //! documentation lines to // comments. Keep original source, compiler output, protocol and scripts. Revised executor/reader use fresh compiler output and bookkeeping paths.', 'original_source_sha256': h.sha(H / 'probe.rs'), 'revised_source_sha256': h.sha(H / 'probe-r2.rs'), 'original_protocol_sha256': h.sha(H / 'protocol.json'), 'failed_compiler_exit_sha256': h.sha(H / 'execution/rustc.exit.json'), 'solver_or_GPU_children_started': 0, 'scientific_inputs_code_sequence_sample_count_changed': False}
h.save(H / 'comment-adapter-review.json', review)
P = h.read(H / 'protocol.json')
P.update(at=h.now(), revision=2, supersedes_protocol_sha256=h.sha(H / 'protocol.json'))
cmd = P['rustc_command']
cmd[1] = str(H / 'probe-r2.rs')
cmd[-1] = str(H / 'probe-r2.exe')
cmd += ['--crate-name', 'd144_control']
for name in ['execute', 'audit']:
    script = ROOT / f'runs/D144-{name}.py'
    compile(script.read_text(encoding='utf-8'), str(script), 'exec')
    P['input_sha256'][str(script)] = h.sha(script)
for p in [Path(__file__), H / 'protocol.json', H / 'probe-r2.rs', H / 'comment-adapter-review.json', ROOT / 'runs/D144-execute-before-comment-adapter.py', ROOT / 'runs/D144-audit-before-comment-adapter.py', H / 'execution/rustc.stderr.log', H / 'execution/rustc.exit.json']:
    P['input_sha256'][str(p)] = h.sha(p)
h.save(H / 'protocol-r2.json', P)
for p in [H / 'protocol-r2.json', H / 'comment-adapter-review.json']:
    key = H.name + '/' + p.name
    dst = h.ar.DASHBOARD / 'evidence' / key
    assert not dst.exists()
    shutil.copyfile(p, dst)
    with urllib.request.urlopen(h.ar.LIVE + '/research/postflop-gpu-20261016/evidence/' + key, timeout=20) as response:
        assert response.read() == p.read_bytes()
print(h.sha(H / 'protocol-r2.json'), flush=True)
