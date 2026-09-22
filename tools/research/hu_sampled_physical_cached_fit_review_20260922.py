"""Read back cached-fit evidence without rerunning or changing the experiment."""
import json
from pathlib import Path
import numpy as np
from sampled_physical_checkpoint_v1 import read_object, model_document
from sampled_physical_root_evaluation_v1 import ROOT, sha, save

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-cached-fit-v1'


def main():
    paths = {s: OUT/f'{PREFIX}-{s}.json' for s in ('registration','status','result','review','weights')}
    evidence = {str(p): sha(p) for p in paths.values()}
    reg, status, result, review, weights = [json.loads(paths[s].read_text())
        for s in ('registration','status','result','review','weights')]
    assert status['state'] == 'complete' and status['exit_code'] == 0 and status['error'] is None
    assert review['passed'] and result['passed']
    assert review['registration_sha256'] == sha(paths['registration'])
    assert review['result_sha256'] == sha(paths['result'])
    assert result['weights_sha256'] == sha(paths['weights'])
    for p, h in reg['inputs'].items(): assert sha(p) == h, p
    objects = Path(reg['objects'])
    checkpoint = json.loads(read_object(objects, reg['checkpoint']))
    published = model_document(objects, checkpoint['next_model'])['networks']
    assert len(weights) == len(result['rows']) == len(published) == 2
    parameters = 0
    for player, (pair, row, original) in enumerate(zip(weights,result['rows'],published)):
        assert row['player'] == player
        assert set(pair) == {'reference','cached'}
        assert set(pair['reference']) == set(pair['cached']) == set(original)
        for name in original:
            a, b, c = [np.asarray(x[name], dtype=np.float64) for x in (pair['reference'],pair['cached'],original)]
            assert a.shape == b.shape == c.shape and np.isfinite(a).all()
            assert np.array_equal(a,b) and np.array_equal(a,c), (player,name)
            parameters += a.size
        for key in ('initial_loss_error','maximum_gradient_error','first_step_parameter_error',
                    'published_model_error','cached_reference_parameter_error','final_loss_error'):
            assert row[key] == 0, key
        assert row['reference_metric']['normalized_grouped_loss_after'] == row['cached_metric']['normalized_grouped_loss_after']
        assert abs(row['speedup'] - row['reference_seconds']/row['cached_seconds']) < 1e-12
    for p,h in evidence.items(): assert sha(p) == h
    document = dict(passed=True, source_hashes=evidence, registered_inputs_verified=len(reg['inputs']),
        parameters_per_pair_compared=parameters, exported_weights_exactly_equal=True,
        cached_seconds=sum(r['cached_seconds'] for r in result['rows']),
        reference_seconds=sum(r['reference_seconds'] for r in result['rows']),
        scope='Readback independently compares every exported parameter with both the reference fit and original published model. Gradient and timing values are execution evidence, not rerun here. No poker-quality claim.',
        production_modified=False)
    save(OUT/f'{PREFIX}-independent-review.json',document)
    print(json.dumps(document))


if __name__ == '__main__': main()
