"""Guarded serial fixed-state diagnostics; run only after the large job ends."""
import gzip
import json
from run07 import HERE, LAB, RAW, digest, run


def main():
    exe = LAB/'target/release/examples/convergence_conditional_sampling.exe'
    paths = HERE/'exploration-diagnostic-paths.json'
    for samples, seed in ((64, 42), (64, 314159), (1024, 42)):
        source_name = f'particle-quality-s{samples}-seed{seed}-norm1-v1'
        source = LAB/'target/convergence'/source_name/'final.gtop'
        name = f'conditional-sampling-s{samples}-seed{seed}-v1'
        out = LAB/'target/convergence'/name
        out.mkdir(exist_ok=False)
        result = out/'result.json'
        run(name, [exe, source, paths, result], 900, [exe, source, paths])
        packed = RAW/(name+'-result.json.gz')
        packed.write_bytes(gzip.compress(result.read_bytes(), mtime=0))
        (RAW/(name+'-result-envelope.json')).write_text(json.dumps(dict(
            original_bytes=result.stat().st_size,
            original_sha256=digest(result), gzip_sha256=digest(packed)),
            indent=2)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
