"""Read-only original-solve arena inspection; no CPU performance comparison."""
from run07 import *

if __name__ == '__main__':
    for name in ('default-solver-tests-v1', 'gpu-equivalence-tests-v1'):
        record = json.loads((RAW / (name + '-exit.json')).read_text())
        if record['returncode'] or record['reason']:
            raise RuntimeError('Correctness checks must pass: ' + name)
    run('arena-diagnostics-build-v1', ['cargo', 'build', '--release', '-p', 'solver',
        '--features', 'preflop-research', '--example', 'convergence_diagnostics'])
    exe = LAB / 'target/release/examples/convergence_diagnostics.exe'
    paths = json.loads((HERE / 'broad-paths.json').read_text())
    if not isinstance(paths, list) or len(paths) != 27:
        raise RuntimeError('Expected the registered 27 paths')
    summary = {}
    for variant, saved in [('native', 'eight-native-a'),
                           ('sampled', 'followup-eight-gamma15-s64-42')]:
        source = LAB / 'target/convergence' / saved / 'final.gtop'
        nodes = {}
        # Existing diagnostic accepts six paths. Last batch overlaps earlier
        # paths; deduplicate by exact path after inspecting all 27.
        for batch, start in enumerate((0, 6, 12, 18, 21)):
            name = f'original-{variant}-arena-v1-{batch}'
            audit = RAW / (name + '-paths.json')
            output = RAW / (name + '.json')
            audit.write_text(json.dumps({'rows': [
                {'candidate': {'path': p}} for p in paths[start:start+6]
            ]}, indent=2) + '\n', encoding='utf-8')
            run(name, [exe, source, audit, output], 180, [source, audit])
            for node in json.loads(output.read_text())['nodes']:
                nodes[tuple(node['path'])] = node
        if len(nodes) != 27:
            raise RuntimeError('Incomplete diagnostic coverage')
        summary[variant] = [{
            'path': n['path'],
            'opponent_mass': n['average_counterfactual_prefix_mass'],
            'current_fallback_hands': sum(h['current_uniform_fallback'] for h in n['hands']),
            'average_fallback_hands': sum(h['average_uniform_fallback'] for h in n['hands']),
            'positive_tiny_regret_hands': sum(0 < h['positive_regret_sum'] <= 1e-12 for h in n['hands']),
            'positive_tiny_average_hands': sum(0 < h['strategy_sum'] <= 1e-12 for h in n['hands']),
            'min_positive_regret_sum': min((h['positive_regret_sum'] for h in n['hands'] if h['positive_regret_sum'] > 0), default=None),
            'min_positive_strategy_sum': min((h['strategy_sum'] for h in n['hands'] if h['strategy_sum'] > 0), default=None)
        } for n in nodes.values()]
    (RAW / 'original-arena-summary-v1.json').write_text(
        json.dumps(summary, indent=2) + '\n', encoding='utf-8')
