"""One large corrected run, saved audit and independent verification."""
import gzip
import json
import sys
from run07 import HERE, LAB, RAW, digest, run


def main(seed=42):
    from check_large_normalized_pair import verify
    if seed not in (42, 314159):
        raise RuntimeError('Unregistered seed')
    if seed == 314159 and not verify(42)['combined_quality_passed']:
        raise RuntimeError('First seed did not qualify; do not advance')
    name = f'large-normalized-pair-seed{seed}-v1'
    exe = LAB/'target/release/examples/convergence_large_normalized_pair.exe'
    cfg = HERE.parent/'03-preflop-20260910/user-session.json'
    paths = HERE/'broad-paths.json'
    plan = HERE/'LARGE_NORMALIZED_PAIR_PLAN.md'
    fit = LAB/'cache/realization_fit.json'
    equity = LAB/'cache/preflop_eq169.bin'
    out = LAB/'target/convergence'/name
    run(name, [exe, cfg, paths, out, seed], 10800, [exe, cfg, paths, plan, fit, equity],
        {'REALIZATION_FIT': str(fit)})
    result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
    packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
    (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
        original_bytes=result.stat().st_size, original_sha256=digest(result),
        gzip_sha256=digest(packed)), indent=2)+'\n', encoding='utf-8')
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    saved = out/'final.gtop'
    run(name+'-audit', [audit, saved, paths, RAW/(name+'-audit.json')], 300, [audit, saved, paths, equity])
    verified = verify(seed)
    (RAW/(name+'-verified.json')).write_text(json.dumps(verified, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in verified.items() if k != 'checks'}), flush=True)


if __name__ == '__main__':
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 42)
