"""Run only after the first large corrected seed fails independent quality."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run


def main():
    from check_large_normalized_pair import verify
    original = verify(42)
    if original['combined_quality_passed']:
        raise RuntimeError('Original passed; advance to its registered second seed instead')
    name = 'large-averaging-dcfr-v1'
    exe = LAB/'target/release/examples/convergence_large_averaging.exe'
    cfg = HERE.parent/'03-preflop-20260910/user-session.json'
    paths = HERE/'broad-paths.json'
    plan = HERE/'LARGE_AVERAGING_DIAGNOSTIC_PLAN.md'
    fit = LAB/'cache/realization_fit.json'; equity = LAB/'cache/preflop_eq169.bin'
    reference = LAB/'target/convergence/large-normalized-pair-seed42-v1/final.gtop'
    out = LAB/'target/convergence'/name
    run(name, [exe, cfg, paths, out, 42, reference], 10800,
        [exe, cfg, paths, plan, fit, equity, reference], {'REALIZATION_FIT': str(fit)})
    result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
    packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
    (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
        original_bytes=result.stat().st_size, original_sha256=digest(result),
        gzip_sha256=digest(packed)), indent=2)+'\n', encoding='utf-8')
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    saved = out/'final.gtop'
    run(name+'-audit', [audit, saved, paths, RAW/(name+'-audit.json')], 300, [audit, saved, paths, equity])
    compare = LAB/'target/release/examples/convergence_compare_arenas.exe'
    run(name+'-compare', [compare, reference, saved, RAW/(name+'-compare.json')], 300,
        [compare, reference, saved, equity])
    from check_large_averaging import verify as verify_averaging
    (RAW/(name+'-verified.json')).write_text(
        json.dumps(verify_averaging(), indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
