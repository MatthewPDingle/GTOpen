"""Guarded matched learning screen; all prerequisites are terminal first."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run

CASES = ((42, False), (42, True), (314159, True), (314159, False))


def case_name(seed, average):
    return f'average-opponents-seed{seed}-avg{int(average)}-v1'


def main():
    for name in ('average-opponents-numerical-v1', 'average-opponents-normalized-compat-v1',
                 'average-opponents-exploration-compat-v1', 'average-opponents-pair-compat-v1',
                 'average-opponents-native-compat-v1', 'average-opponents-build-v1'):
        p = json.loads((RAW/(name+'-exit.json')).read_text())
        if p['returncode'] != 0 or p['reason'] is not None:
            raise RuntimeError('Prerequisite failed: '+name)
    exe = LAB/'target/release/examples/convergence_average_opponents.exe'
    audit = LAB/'target/release/examples/convergence_audit_paths.exe'
    cfg = HERE.parent/'05-preflop-convergence-20260911/six-solver.json'
    paths = HERE/'exploration-diagnostic-paths.json'
    plan = HERE/'AVERAGE_OPPONENT_SCREEN_PLAN.md'
    equity = LAB/'cache/preflop_eq169.bin'; fit = LAB/'cache/realization_fit.json'
    for seed, average in CASES:
        name = case_name(seed, average)
        out = LAB/'target/convergence'/name
        run(name, [exe, cfg, paths, 64, seed, int(average), out], 300,
            [exe, cfg, paths, plan, equity, fit], {'REALIZATION_FIT': str(fit)})
        result = out/'result.json'; packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size, original_sha256=digest(result),
            gzip_sha256=digest(packed)), indent=2)+'\n', encoding='utf-8')
        saved = out/'final.gtop'
        run(name+'-audit', [audit, saved, paths, RAW/(name+'-audit.json')], 60,
            [audit, saved, paths, equity])
    from check_average_opponent_screen import verify
    result = verify()
    (RAW/'average-opponents-screen-verified.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}), flush=True)


if __name__ == '__main__':
    main()
