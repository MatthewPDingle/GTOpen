"""Fresh predeclared four-seed run; original failed screen stays immutable."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

CASES = (('control-before', 1024, 42), ('seed42', 64, 42), ('seed271828', 64, 271828),
         ('seed314159', 64, 314159), ('seed1618033', 64, 1618033), ('control-after', 1024, 42))


def main():
    exe = LAB/'target/release/examples/convergence_normalized_pair_tail.exe'
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg = HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    paths = HERE/'exploration-diagnostic-paths.json'
    plan = HERE/'NORMALIZED_PAIR_TAIL_PLAN.md'
    for tag, samples, seed in CASES:
        name = f'normalized-pair-tail-{tag}-v1'
        out = LAB/'target/convergence'/name
        run(name, [exe, cfg, paths, samples, seed, int(samples != 1024), out], 300, [exe, cfg, paths, plan])
        result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size, original_sha256=digest(result),
            gzip_sha256=digest(packed)), indent=2)+'\n', encoding='utf-8')
        saved = out/'final.gtop'
        run(name+'-audit', [audit, saved, paths, RAW/(name+'-audit.json')], 60, [audit, saved, paths])


if __name__ == '__main__':
    main()
