"""Independent saved-array arithmetic audit. No model import or inference."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
                  PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
from pathlib import Path
import numpy as np

OUT = Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME = 'stack-board-boundary-diagnostic-v1'
DEST = OUT / (NAME + '-readout.json')


def read(p):
    return json.loads(Path(p).read_bytes())


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    rp, resultp = (OUT / (NAME + suffix + '.json') for suffix in ('-registration', '-result'))
    registration, result = read(rp), read(resultp)
    assert result['complete'] and result['diagnostic_only']
    assert not result['new_training'] and not result['old_study_verification_passed']
    assert result['registration_sha256'] == sha(rp)
    assert not (OUT / 'stack-board-balanced-learning-v1-readback-v1.json').exists()
    checked = {str(p): sha(p) for p in (Path(__file__).resolve(), rp, resultp)}
    for mapping in (registration['inputs'], result['evidence']):
        for path, digest in mapping.items():
            assert sha(path) == digest, path
            checked[path] = digest
    evidence_path = next(p for p in result['evidence'] if p.endswith('paired-target-evidence.npz'))
    with np.load(evidence_path, allow_pickle=False) as saved:
        data = {k: saved[k].copy() for k in saved.files}
    cuda_path = next(p for p in result['evidence'] if p.endswith('cuda-target-raw.npz'))
    with np.load(cuda_path, allow_pickle=False) as saved:
        assert np.array_equal(saved['raw'], data['gpu_raw'])
        assert np.all(saved['coverage'] == 1)
        assert np.array_equal(saved['card_indices'], np.r_[np.arange(51*1081, 52*1081), np.arange(101*1081, 102*1081)])
    assert data['cpu_raw'].shape == data['gpu_raw'].shape == (70, 2162, 2)
    ids = registration['target_board_indices']
    assert ids == [51, 101] and np.array_equal(data['board_indices'], np.repeat(ids, 1081))
    counts = []
    for i, board in enumerate(ids):
        with np.load(registration['boards'][board]['file'], allow_pickle=False) as saved:
            selection = slice(i*1081, (i+1)*1081)
            assert np.array_equal(saved['hands'], data['hands'][selection])
            assert np.array_equal(saved['canonical_cards'], data['canonical_cards'][selection])
            counts.append(saved['counts'].copy())
    counts = np.concatenate(counts)
    assert np.all(counts.sum(axis=1) == 990)
    # Rebuild prices directly from the saved native public document, without
    # calling the diagnostic's feature adapter or probability converter.
    public_file = next(p for p in registration['public_files'] if p.endswith('stack-40-public.json'))
    document = read(public_file)
    public = {int(row['hi']): row for row in document['public_states']}
    economics, delta = [], []
    for hi in data['public_hi']:
        row = public[int(hi)]
        assert row['phase'] == 3 and [a['kind'] for a in row['actions']] == ['fold', 'call']
        pot, cost, rate, cap = (row[k] for k in ('pot', 'call_cost', 'rake_fraction', 'rake_cap'))
        rake = min(cap, rate*(pot+cost)) if cap > 0 else rate*(pot+cost)
        net = pot + cost - rake
        economics.append([40, net, cost, row['actor'], cost/net])
        delta.append((counts[:, 0]*(net-cost) + counts[:, 1]*(net/2-cost) - counts[:, 2]*cost)/990)
    delta = np.asarray(delta)
    assert np.array_equal(economics, data['economics'])
    assert np.allclose(delta, data['call_advantage_bb'], rtol=0, atol=1e-12)
    eligible = np.abs(delta) > .004
    assert np.array_equal(eligible, data['eligible'])
    rebuilt = {}
    for engine in ('cpu', 'gpu'):
        raw = data[engine + '_raw'].astype(np.float64)
        positive = np.clip(raw, 0, None)
        total = positive[..., 0] + positive[..., 1]
        probability = np.empty(total.shape)
        active = total > 0
        probability[active] = positive[..., 1][active]/total[active]
        probability[~active] = (raw[..., 1][~active] > raw[..., 0][~active]).astype(float)
        assert np.array_equal(probability, data[engine + '_probability'])
        loss = np.where(delta > 0, delta*(1-probability), -delta*probability)
        assert np.allclose(loss, data[engine + '_loss_bb'], rtol=0, atol=1e-12)
        wrong = eligible & ((probability >= .5) != (delta > 0))
        rebuilt[engine] = dict(raw=raw, probability=probability, loss=loss, wrong=wrong)
    disagreements = (rebuilt['cpu']['probability'] >= .5) != (rebuilt['gpu']['probability'] >= .5)
    assert np.array_equal(disagreements, data['disagreement'])
    assert int(disagreements.sum()) == result['summary']['disagreement_count'] == 2
    cases = []
    for state, card in np.argwhere(disagreements):
        c, g = (rebuilt[e]['raw'][state, card] for e in ('cpu', 'gpu'))
        assert np.all(c < 0) and np.all(g < 0)
        assert (c[1] > c[0]) != (g[1] > g[0])
        entry = next(r for r in result['disagreements'] if r['state'] == state and r['board_index'] == data['board_indices'][card])
        assert entry['hand'] == data['hands'][card].tolist()
        assert entry['raw']['cpu'] == c.tolist() and entry['raw']['gpu'] == g.tolist()
        cases.append(dict(board_index=int(data['board_indices'][card]), state=int(state),
            public_hi=str(int(data['public_hi'][state])), hand=data['hands'][card].tolist(),
            raw_cpu=c.tolist(), raw_gpu=g.tolist(), cpu_score_order_margin=float(c[1]-c[0]),
            gpu_score_order_margin=float(g[1]-g[0]), both_engines_nonpositive=True,
            cpu_call_probability=float(rebuilt['cpu']['probability'][state, card]),
            gpu_call_probability=float(rebuilt['gpu']['probability'][state, card]),
            reference_call_advantage_bb=float(delta[state, card]),
            learned_cpu_call_value_bb=float(c[1]*40), learned_gpu_call_value_bb=float(g[1]*40),
            learned_cpu_fold_value_bb=float(c[0]*40), learned_gpu_fold_value_bb=float(g[0]*40),
            reference_fold_value_bb=0.0))
    boards = []
    for i, row in enumerate(result['summary']['boards']):
        sl = slice(i*1081, (i+1)*1081)
        assert int(eligible[:, sl].sum()) == row['eligible']
        for engine in ('cpu', 'gpu'):
            assert int(rebuilt[engine]['wrong'][:, sl].sum()) == row[engine + '_errors'] == row['old_' + engine + '_errors']
            assert abs(float(rebuilt[engine]['loss'][:, sl].mean()) - row[engine + '_mean_loss_bb']) < 1e-12
        original = next(r for r in registration['original_target_metrics'] if r['board_index'] == row['board_index'])
        boards.append(dict(board_index=row['board_index'], exact_historical_counts_reproduced=True,
            gpu_mean_loss_change_from_original_bb=row['gpu_mean_loss_bb'] - original['mean_regret_bb']))
    findings = dict(complete=True, saved_array_checks_passed=True, inputs=checked,
        rows_audited=int(disagreements.size), boards=boards, cases=cases,
        mechanism='Nonpositive-score fallback chooses the larger score; CPU/CUDA numerical differences reverse that order.',
        scope='Two selected boards in one fixed 40bb river context, chosen after a verification failure.',
        original_raw_predictions_retained=False, original_study_readback_passed=False,
        interpretation='New raw scores explain the reproduced count differences. They cannot prove original raw outputs were bitwise identical.',
        new_inference=False, new_training=False, full_preflop_accuracy_qualified=False)
    with DEST.open('x', encoding='utf-8', newline='\n') as stream:
        json.dump(findings, stream, indent=2, allow_nan=False)
        stream.write('\n')
    print(json.dumps(dict(complete=True, rows=findings['rows_audited'], cases=cases, boards=boards, result=str(DEST))))


if __name__ == '__main__':
    main()
