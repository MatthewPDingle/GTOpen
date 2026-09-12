"""Registered serial combined-quality runs and separate final saved audits."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

CASES = ((1024, 42), (64, 42), (256, 314159), (1024, 314159), (64, 314159), (256, 42))


def main():
    exe = LAB/'target/release/examples/convergence_normalized_pair.exe'
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    configs = list((HERE.parent/'05-preflop-convergence-20260911').rglob('six-solver.json'))
    if len(configs) != 1:
        raise RuntimeError('Expected exactly one registered six-solver fixture')
    cfg = configs[0]
    paths = HERE/'exploration-diagnostic-paths.json'
    for samples, seed in CASES:
        name = f'normalized-pair-quality-s{samples}-seed{seed}-v1'
        out = LAB/'target/convergence'/name
        run(name, [exe, cfg, paths, samples, seed, int(samples != 1024), out], 300, [exe, cfg, paths])
        result = out/'result.json'
        packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size, original_sha256=digest(result),
            gzip_sha256=digest(packed)), indent=2)+'\n', encoding='utf-8')
        saved = out/'final.gtop'
        run(name+'-audit', [audit, saved, paths, RAW/(name+'-audit.json')], 60, [audit, saved, paths])


if __name__ == '__main__':
    main()
