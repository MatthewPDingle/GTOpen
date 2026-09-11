"""Execute the already registered large128 queue; root owns the hardware slot."""
import sys
from run_small128_queue import run, LAB, ROOT, CACHE

if __name__ == '__main__':
    if sys.argv[1:] != ['--execute']:
        raise SystemExit('Explicit --execute required')
    config = ROOT/'research/autoresearch/passes/03-preflop-20260910/user-session.json'
    reference = ROOT/'target/autoresearch/preflop-20260910/target/research-convergence/extended-convergence-eight-compatible-a.gtop'
    for iterations, cap in ((50,240),(1000,1200)):
        name = f'preview128-eight-{iterations:03d}-a'
        native = LAB/f'target/research-preview/{name}.gtop'
        run(name, 'preflop_interactive_bench', [config,'coupled_preview128_v1',iterations,native,10], cap)
        run(f'quality-large128-{iterations:03d}-a', 'preflop_preview_quality_gpu',
            [native,reference,CACHE,23000],180)
