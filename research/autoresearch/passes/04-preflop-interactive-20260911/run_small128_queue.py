"""Execute the registered small128 and preview-prefix conditional queue serially.

Root starts this only after the active API/hardware job has completed. Every
child has the existing read-only live-work and hard deadline guard. No UI writes.
"""
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
LAB = ROOT / 'target/autoresearch/preflop-interactive-20260911'
GATES = HERE / 'proposals/quality-gates'
CACHE = LAB / 'cache/preflop_eq169.bin'
BINARIES = json.loads((HERE/'research-examples-h-manifest.json').read_text())
EXES = {row['name']: row for row in BINARIES['binaries']}


def run(name, executable, args, cap):
    row = EXES[executable]
    with Path(row['path']).open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    if digest != row['sha256']:
        raise RuntimeError(f'Frozen research binary changed: {executable}')
    print(f'START {name}', flush=True)
    result = subprocess.run([sys.executable, str(HERE/'guarded_run.py'),
        '--timeout', str(cap), name, row['path'], *map(str,args)],
        cwd=ROOT, capture_output=True, text=True)
    with (HERE/'raw'/f'{name}-driver.txt').open('x') as stream:
        stream.write(result.stdout)
        stream.write(result.stderr)
    if result.returncode:
        raise RuntimeError(f'{name} failed; preserved driver and guard logs')
    print(f'PASS {name}', flush=True)


def main():
    if sys.argv[1:] != ['--execute']:
        raise SystemExit('Explicit --execute required; root must first finish other hardware work')
    for iteration in (50, 1000):
        native = LAB/f'target/research-preview/preview64-eight-{iteration:03d}-a.gtop'
        protocol = HERE/f'proposals/early-preview/conditional-preview64-{iteration}-paths-a.json'
        with native.open('rb') as stream:
            digest = hashlib.file_digest(stream, 'sha256').hexdigest()
        if digest != json.loads(protocol.read_text())['input_sha256']:
            raise RuntimeError('Conditional input changed')
        name = f'conditional-preview64-{iteration}-full-a'
        run(name, 'preflop_conditional_large_research', [native, protocol,
            HERE/'raw'/f'{name}.json', 'refine-preview-full', 120, 100], 180)

    cases = [
        ('development', 'three-solver-development', 'reference-development-a/checkpoint-020.gtop', LAB/'target/research-preview/development-paths.json', 180),
        ('fixed-frozen', 'four-fixed-frozen-holdout', 'small-four-fixed-frozen-holdout-coupled_deck_v1-a/checkpoint-420.gtop', GATES/'herding128-native-constraint-paths.json', 300),
        ('adaptive', 'three-adaptive-holdout', 'small-three-adaptive-holdout-coupled_deck_v1-a/checkpoint-040.gtop', GATES/'herding128-native-constraint-paths.json', 300),
    ]
    for label, case, reference, paths, cap in cases:
        name = f'small128-{label}-primary-a'
        out = LAB/'target/research-preview'/name
        run(name, 'preflop_preview_small', [GATES/'corpus.json', case,
            'coupled_preview128_v1', CACHE, out, 4], cap)
        saves = sorted(out.glob('checkpoint-*.gtop'))
        if not saves:
            raise RuntimeError(f'No native checkpoints from {name}')
        for save in saves:
            run(f'quality-{name}-{save.stem}', 'preflop_preview_quality',
                [save, LAB/'target/research-preview'/reference, CACHE, 4, paths], 120)

    name = 'small128-development-fixed500-a'
    out = LAB/'target/research-preview'/name
    run(name, 'preflop_preview_small', [GATES/'corpus.json', 'three-solver-development',
        'coupled_preview128_v1', CACHE, out, 4, '--fixed-iterations=500'], 180)
    for iteration in (100,500):
        run(f'quality-small128-fixed-{iteration}-a', 'preflop_preview_quality',
            [out/f'checkpoint-{iteration:03d}.gtop', LAB/'target/research-preview/fixed-development-coupled_deck_v1-a/checkpoint-500.gtop',
             CACHE, 4, LAB/'target/research-preview/development-paths.json'], 120)


if __name__ == '__main__':
    main()
