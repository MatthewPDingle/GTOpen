"""Post-hoc checkpoint trajectories; no training or acceptance-rule changes."""
import json
import time

from hu_sampled_neural_residual_diagnostic_20260922 import (
    ROOT, OUT, sha, save, restricted_response, local_deviations,
)
from hu_sampled_convergence_fixture_20260922 import evaluate
from loopback_research_validation import idle
from pathlib import Path

PREFIX = 'sampled-neural-residual-trajectory-v1'


def main():
    assert idle()
    prior_registration = OUT / 'sampled-neural-residual-v1-registration.json'
    prior_result = OUT / 'sampled-neural-residual-v1-result.json'
    registration = json.loads(prior_registration.read_text())
    previous = json.loads(prior_result.read_text())
    assert previous['passed'] and previous['registration_sha256'] == sha(prior_registration)
    for name, digest in registration['inputs'].items():
        assert sha(ROOT / name) == digest, name
    paths = [ROOT / name for name in registration['inputs']]
    paths += [Path(__file__), prior_registration, prior_result]
    frozen = {p.relative_to(ROOT).as_posix(): sha(p) for p in paths}
    reg = OUT / (PREFIX + '-registration.json')
    save(reg, dict(
        inputs=frozen, maximum_seconds=120, no_training=True, no_gpu=True,
        scope='Post-hoc trajectories of the two completed finite no-rake seed-17 runs; not physical poker or a new acceptance test.',
        selection='All saved checkpoints, both players, every information set. Highlighted information IDs 6 and 21 were selected after inspecting final GPU errors.',
        methods='Reconstruct exact full and restricted best responses and one-information-set deviations at every checkpoint. Preserve all existing stopping decisions.',
        production_modified=False,
    ))
    started = time.monotonic()
    data = json.loads((OUT / 'sampled-convergence-v1-fixture.json').read_text())
    stages = [('public_card_decisions', {2, 3, 6, 7}),
              ('add_later_preflop', {2, 3, 5, 6, 7, 8}),
              ('add_root', {n for n, arity in enumerate(data['arity']) if arity})]
    runs = []
    for device in ('cpu', 'gpu'):
        result = json.loads((OUT / f'sampled-neural-mean-{device}-v1-case0-seed17.json').read_text())
        assert result['terminal']
        checkpoints = []
        for checkpoint in result['checkpoints']:
            policy = checkpoint['average_policy']
            evaluated = evaluate(data, policy, 0)
            assert abs(evaluated['gap'] - checkpoint['evaluation']['gap']) < 1e-12
            players = []
            for player in (0, 1):
                base = restricted_response(data, policy, 0, player, set())
                assert abs(base - evaluated['ev'][player]) < 1e-11
                value = base
                decomposition = []
                for label, nodes in stages:
                    next_value = restricted_response(data, policy, 0, player, nodes)
                    assert next_value >= value - 1e-11
                    decomposition.append(dict(stage=label, additional_gain=next_value-value))
                    value = next_value
                assert abs(value - evaluated['best_response'][player]) < 1e-11
                players.append(dict(player=player, full_best_response_gain=value-base,
                                    decomposition=decomposition,
                                    local_deviations=local_deviations(data, policy, 0, player)))
            assert abs(sum(p['full_best_response_gain'] for p in players) - evaluated['gap']) < 1e-11
            checkpoints.append(dict(iteration=checkpoint['iteration'], gap=evaluated['gap'], players=players))
            assert idle() and time.monotonic()-started < 120
        final = next(r for r in previous['runs'] if r['device'] == device)
        assert checkpoints[-1]['players'] == [
            {k: v for k, v in player.items() if k != 'largest_single_information_gain'}
            for player in final['players']
        ]
        highlights = []
        for checkpoint in checkpoints:
            rows = [r for p in checkpoint['players'] for r in p['local_deviations']
                    if r['information_id'] in (6, 21)]
            highlights.append(dict(iteration=checkpoint['iteration'], rows=rows))
        runs.append(dict(device=device, checkpoints=checkpoints, exploratory_highlights=highlights))
    for name, digest in frozen.items():
        assert sha(ROOT / name) == digest, name
    save(OUT / (PREFIX + '-result.json'), dict(
        passed=True, inputs_verified=len(frozen), registration_sha256=sha(reg), runs=runs,
        seconds=time.monotonic()-started,
        warning='Local gains overlap; do not add them. Decomposition is order-dependent. Highlight selection is post-hoc. Trajectories do not isolate the cause of learning fluctuations.',
        physical_poker_convergence_qualified=False, production_modified=False,
    ))
    print(json.dumps(dict(passed=True, checkpoints=sum(len(r['checkpoints']) for r in runs),
                          seconds=time.monotonic()-started)))


if __name__ == '__main__':
    main()
