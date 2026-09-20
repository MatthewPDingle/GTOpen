"""Freeze the qualified Rust JSON reader's values without changing input bytes."""
import json
from pathlib import Path
import struct
import subprocess
from storage_phase_run_20260920 import ROOT, OUT, read, sha


def bits(x):
    return struct.unpack('<Q', struct.pack('<d', x))[0]


def expected_manifest():
    review = read(OUT/'weighted-input-readback-v1-review.json')
    for p, digest in review['inputs_sha256'].items():
        assert sha(ROOT/p) == digest, p
    actual = read(OUT/'weighted-input-readback-v1.json')
    source = read(OUT/'expansion-train-112-chance-weight-v1.json')
    exe = ROOT/'target/qualified-paging/storage-json-input-probe.exe'
    observed = json.loads(subprocess.check_output(
        [str(exe), str(OUT/'expansion-train-112-chance-weight-v1.json')], text=True))
    assert observed == actual
    artifacts = [json.loads(line) for line in (OUT/'checkpoint-v1-build.log').read_text().splitlines()
                 if line.startswith('{')]
    artifact = [a for a in artifacts if a.get('reason') == 'compiler-artifact'
                and a['target']['name'] == 'serde_json']
    assert len(artifact) == 1 and artifact[0]['features'] == ['default', 'std']
    library = ROOT/'target/ssd-connected-research/release/deps/libserde_json-83a0670a02a34a4d.rlib'
    assert library.resolve() in [Path(p).resolve() for p in artifact[0]['filenames']]
    assert {k:v for k,v in source.items() if k != 'boards'} == {
        k:v for k,v in actual['manifest'].items() if k != 'boards'}
    assert len(source['boards']) == len(actual['manifest']['boards']) == len(actual['weight_bits']) == 112
    differences = []
    for original, parsed, raw in zip(source['boards'], actual['manifest']['boards'], actual['weight_bits']):
        assert {k:v for k,v in original.items() if k != 'weight'} == {
            k:v for k,v in parsed.items() if k != 'weight'}
        assert bits(parsed['weight']) == raw and parsed['weight'] > 0
        differences.append(abs(bits(original['weight'])-raw))
    assert sum(d != 0 for d in differences) == review['weights_differ'] == 13
    assert max(differences) == review['maximum_weight_ulp_difference'] == 1
    return actual['manifest']


if __name__ == '__main__':
    expected_manifest()
    print('Qualified parser readback reproduced; only 13 weight values differ by one binary64 ULP.')
