"""Read-only one-action deviations at the previously registered N19 paths."""
from pathlib import Path
import sys
import continuation_chance_control as control

study = control.study
OUT = control.BASE/'late-frontier-20260916'


def run():
    control.idle()
    assert not OUT.exists(), 'Inspect existing partial/completed audit before restarting'
    OUT.mkdir()
    paths = [Path(__file__), control.KERNEL, control.transfer.original.runtime.BIN]
    for arm in ['original', 'candidate']:
        paths += [control.BASE/f'policy-stability-20260916/{arm}/1500/{name}'
                  for name in ['policy.gtop', 'iteration-1500.json']]
    inputs = {str(p.resolve().relative_to(study.ROOT)).replace('\\', '/'):study.pilot.sha(p) for p in paths}
    study.freeze(OUT/'input-freeze.json', dict(registered_at=study.night.now(), inputs=inputs,
                 scope='Same17 N19 paths, one-action deviations with average continuation. Overlapping gains are not additive full best-response gaps.', production_enabled=False))
    rows = []
    for arm in ['original', 'candidate']:
        source = control.BASE/f'policy-stability-20260916/{arm}/1500/policy.gtop'
        output = OUT/f'{arm}.json'
        control.idle()
        control.transfer.original.runtime.command(['evaluate', source, output, arm, control.KERNEL], OUT/f'{arm}.log', optimized=True, warm=0)
        snapshot = study.read(control.BASE/f'policy-stability-20260916/{arm}/1500/iteration-1500.json')
        result = study.read(output)
        assert result['model'] == arm and result['iteration'] == 1500
        assert sorted(r['path'] for r in result['rows']) == sorted(r['path'] for r in snapshot['views'])
        for node in result['rows']:
            assert not node['forced_or_frozen']
            contributions = []
            for h in node['hands']:
                q = h['action_values_counterfactual_bb']; sigma = h['average_probabilities']
                loss = sum((max(q)-v)*p for v,p in zip(q,sigma))*h['actor_reach']
                contributions.append(dict(class_index=h['class_index'], gain_bb=loss))
            gain = sum(h['gain_bb'] for h in contributions)
            assert abs(gain-node['full_parent_one_step_gain_bb']) < 1e-10
            rows.append(dict(arm=arm, path=node['path'], position=node['position'],
                             gain_bb=gain, largest_hand_contributions=sorted(contributions,key=lambda x:x['gain_bb'],reverse=True)[:5]))
    for p,h in inputs.items(): assert study.pilot.sha(study.ROOT/p) == h,p
    study.freeze(OUT/'result.json', dict(checked_at=study.night.now(), rows=rows, inputs_unchanged=True,
        output_hashes={p.name:study.pilot.sha(p) for p in OUT.glob('*.json')}, production_enabled=False,
        caveat='One-action deviations at17 selected nodes only. Gains overlap and must not be summed as full exploitability. Values remain frozen learned or approximate Balanced continuation.'))
    for arm in ['original','candidate']:
        print(arm, sorted([r for r in rows if r['arm']==arm],key=lambda r:r['gain_bb'],reverse=True)[:3], flush=True)


if __name__ == '__main__': run()
