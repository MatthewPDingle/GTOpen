"""Separate causal probe: complete zero-probability hands with best responses."""
import shutil
from pathlib import Path
import numpy as np
import continuation_exact_game as game
import continuation_exact_game_robust as robust

ORIGINAL = game.OUT
OUT = ORIGINAL.with_name('exact-game-offsupport-20260917')
original_exact = game.exact
COUNTS = {'queries': 0, 'zero_probability_hand_actions_changed': 0,
          'largest_conditional_value_change': 0., 'largest_on_distribution_ev_change': 0.}


def completed_exact(c, x, y):
    values, (bet, call), gap, fallback = original_exact(c, x, y)
    COUNTS['queries'] += 1
    if fallback:
        return values, (bet, call), gap, fallback
    x, y = game.normalize(x), game.normalize(y)
    bet, call = bet.copy(), call.copy()
    before = game.continuation_matrix(c, bet, call)
    # Only genuinely zero own probability. No small-positive cutoff or smoothing.
    for hand in np.flatnonzero(x == 0):
        choices = []
        for action in [0., 1.]:
            p = bet.copy(); p[hand] = action
            choices.append(float((game.continuation_matrix(c, p, call)*game.LEGAL)[hand] @ y))
        best = float(np.argmax(choices))
        COUNTS['zero_probability_hand_actions_changed'] += int(best != bet[hand])
        bet[hand] = best
    for hand in np.flatnonzero(y == 0):
        choices = []
        for action in [0., 1.]:
            q = call.copy(); q[hand] = action
            choices.append(float(x @ (-game.continuation_matrix(c, bet, q)*game.LEGAL)[:, hand]))
        best = float(np.argmax(choices))
        COUNTS['zero_probability_hand_actions_changed'] += int(best != call[hand])
        call[hand] = best
    after = game.continuation_matrix(c, bet, call)
    w = x[:, None]*y[None, :]*game.LEGAL
    change = abs(float(np.sum(w*(after-before))))
    assert change < 1e-12, change
    COUNTS['largest_on_distribution_ev_change'] = max(COUNTS['largest_on_distribution_ev_change'], change)
    mass0, mass1 = game.LEGAL@y, game.LEGAL.T@x
    updated = np.array([
        np.divide((after*game.LEGAL)@y, mass0, out=np.zeros(3), where=mass0>0),
        np.divide((-after*game.LEGAL).T@x, mass1, out=np.zeros(3), where=mass1>0)])
    COUNTS['largest_conditional_value_change'] = max(COUNTS['largest_conditional_value_change'],
                                                    float(np.max(np.abs(updated-values))))
    return updated, (bet, call), gap, fallback


def run():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'freeze.json').exists()
    shutil.copyfile(ORIGINAL/'PROTOCOL.md', OUT/'BASE-PROTOCOL.md')
    game.OUT = OUT
    game.linprog = robust.robust_linprog
    game.exact = completed_exact
    original_write = game.write

    def recorded_write(name, value):
        if name == 'freeze.json':
            more = [Path(__file__), Path(robust.__file__), OUT/'BASE-PROTOCOL.md',
                    ORIGINAL.with_name('exact-game-robust-20260917')/'freeze.json',
                    ORIGINAL.with_name('exact-game-robust-20260917')/'exact_cutoff.json',
                    game.ROOT/'tools/research/test_continuation_exact_game_offsupport.py']
            value['inputs'].update({str(p.relative_to(game.ROOT)): game.sha(p) for p in more})
            value['lp_method'] = 'highs-ipm'
            value['lp_options'] = robust.OPTIONS
        original_write(name, value)

    game.write = recorded_write
    game.run()
    game.write('offsupport-diagnostic.json', COUNTS)


if __name__ == '__main__':
    run()
