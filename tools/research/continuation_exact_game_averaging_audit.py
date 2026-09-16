"""Reproduce and independently verify the original accumulated-policy anomaly."""
import datetime as dt
import json
from pathlib import Path
import numpy as np
import continuation_exact_game as game


def main():
    original = game.OUT
    out = original.with_name('exact-game-extension-20260917')
    expected = json.loads((original/'exact_cutoff.json').read_text())['rows'][-1]
    solver = game.CFR(game.exact)  # Original default LP backend, not the repaired backend.
    for _ in range(5000):
        solver.step()
    average = solver.average()
    rebuilt = game.complete_upper(average)
    both = {}
    for label, policy, claim in [('averaged_all_rounds',average,expected['accumulated_full_policy']),
                                  ('resolved_at_average_upper',rebuilt,expected['full_game'])]:
        result = game.measure(policy)
        for key, value in result.items():
            assert abs(value-claim[key]) < 1e-12
        br = sum(float(game.CFR().walk(0,np.ones((2,3)),policy,br=p)[p].sum()) for p in [0,1])
        assert abs(br-result['nashconv']) < 1e-12
        both[label] = {'metrics': result, 'policy': policy.tolist(), 'recursive_br_sum': br}
    record = {'checked_at': dt.datetime.now(dt.timezone.utc).isoformat(),
              'inputs': {str(p.relative_to(game.ROOT)): game.sha(p)
                         for p in [Path(game.__file__),Path(__file__),original/'exact_cutoff.json']},
              'results': both, 'production_enabled': False}
    (out/'averaging-audit.json').write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8',newline='\n')
    print('Original 0.21334 versus 0.00387 anomaly reproduced; both full policies retained and independently verified')


if __name__ == '__main__':
    main()
