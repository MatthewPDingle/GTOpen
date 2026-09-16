"""Numerically checked interior-point LP backend; original experiment unchanged."""
import shutil
from pathlib import Path
import continuation_exact_game as game

ORIGINAL = game.OUT
OUT = ORIGINAL.with_name('exact-game-robust-20260917')
OPTIONS = {'dual_feasibility_tolerance': 1e-10, 'primal_feasibility_tolerance': 1e-10,
           'ipm_optimality_tolerance': 1e-12, 'presolve': False}
original_linprog = game.linprog


def robust_linprog(*args, **kwargs):
    assert 'options' not in kwargs
    kwargs['method'] = 'highs-ipm'
    return original_linprog(*args, options=OPTIONS, **kwargs)


def run():
    OUT.mkdir(exist_ok=True)
    assert not (OUT/'freeze.json').exists()
    shutil.copyfile(ORIGINAL/'PROTOCOL.md', OUT/'PROTOCOL.md')
    game.OUT = OUT
    game.linprog = robust_linprog
    original_write = game.write

    def recorded_write(name, value):
        if name == 'freeze.json':
            more = [Path(__file__), OUT/'REPAIR.md', ORIGINAL/'freeze.json',
                    ORIGINAL/'integration-gate.json', ORIGINAL/'full_cfr.json',
                    ORIGINAL/'exact_cutoff.json',
                    ORIGINAL.with_name('exact-game-precision-20260917')/'freeze.json',
                    game.ROOT/'tools/research/continuation_exact_game_precision.py']
            value['inputs'].update({str(p.relative_to(game.ROOT)): game.sha(p) for p in more})
            value['lp_method'] = 'highs-ipm'
            value['lp_options'] = OPTIONS
        original_write(name, value)

    game.write = recorded_write
    game.run()


if __name__ == '__main__':
    run()
