"""Admit the fully audited linear output for separate wider evaluation."""
import numpy as np
from pathlib import Path
from later_average_support_v1 import OUT,read,weights,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha
from hu_later_average_exact_evaluation_20260923 import load_bank
from preflop_allin_matrix_v1 import AllinMatrix


def admitted():
    paths={name:OUT/f'{name}.json' for name in (
        'later-average-study-v1-registration','later-average-study-v1-result','later-average-study-v1-status',
        'later-average-fresh-pilot-v1-registration','later-average-fresh-pilot-v1-independent-review',
        'later-average-exact-v1-registration','later-average-exact-v1-result','later-average-exact-v1-independent-review',
        'later-average-exact-v1-status')}
    documents={k:read(p) for k,p in paths.items()}
    sr=documents['later-average-study-v1-result'];ss=documents['later-average-study-v1-status']
    assert sr['passed'] and sr['screening_passed'] and not sr['accuracy_qualified']
    assert ss['state']=='complete' and ss['error'] is None and ss['stages']==sr['stages']
    assert [s['stage'] for s in sr['stages']]==['training','training-audit','exact-evaluation','exact-audit']
    assert all(s['exit_code']==0 for s in sr['stages'])
    assert sr['registration_sha256']==sha(paths['later-average-study-v1-registration'])
    tr=documents['later-average-fresh-pilot-v1-registration'];ta=documents['later-average-fresh-pilot-v1-independent-review']
    assert ta['passed'] and ta['terminal_complete'] and not ta['control_only'] and ta['completed_iterations']==78
    assert ta['source_registration_sha256']==sha(paths['later-average-fresh-pilot-v1-registration'])
    er=documents['later-average-exact-v1-registration'];ep=documents['later-average-exact-v1-result'];ea=documents['later-average-exact-v1-independent-review']
    assert ep['passed'] and ep['screening_passed'] and ea['passed'] and er['count']==78 and not er['control_only']
    assert ea['result_sha256']==sha(paths['later-average-exact-v1-result'])
    assert ep['registration_sha256']==ea['registration_sha256']==sha(paths['later-average-exact-v1-registration'])
    assert documents['later-average-exact-v1-status']['state']=='complete'
    inputs={**documents['later-average-study-v1-registration']['inputs'],**tr['inputs'],**ta['evidence_hashes'],**er['inputs'],**ep['artifacts']}
    inputs.update({str(p):sha(p) for p in paths.values()})
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    matrix_paths=[OUT/f'preflop-allin-matrix-control-v1-{s}.json' for s in ('registration','result','independent-review')]
    mr,mp,ma=map(read,matrix_paths)
    assert ma['passed'] and ma['result_sha256']==sha(matrix_paths[1]) and ma['registration_sha256']==sha(matrix_paths[0])
    matrix_path=Path(mp['matrix_artifact']);assert sha(matrix_path)==mp['matrix_sha256']==ma['matrix_sha256']
    inputs.update(mr['inputs']);inputs.update({str(p):sha(p) for p in [*matrix_paths,matrix_path,cp,Path(__file__)]})
    for p,h in inputs.items():assert sha(p)==h,p
    models=load_bank(tr,ta,source,78)
    policy_path=Path(er['store'])/'linear-policy.json';p=read(policy_path)
    assert ep['artifacts'][str(policy_path)]==sha(policy_path)
    assert p['schedule']=='linear' and p['played_generations']==list(range(78)) and p['excluded_generation']==78
    assert p['weights']==weights('linear',78).tolist() and p['checkpoint']==ta['checkpoint']
    root=np.asarray(p['root_probabilities']);call=np.asarray([0. if x is None else x for x in p['btn_call_probabilities']])
    values=AllinMatrix(read(matrix_path),source).evaluate(root,call)
    for row in ep['pairings']['linear/linear']['bb_classes']:
        c=row['hand_class']
        for key,target in [('bb_entries','entry_probability'),('bb_fold_entries','fold_value_per_entry'),('bb_jam_entries','jam_value_per_entry')]:
            assert abs(values[key][c]-row[target])<1e-12
    exact=dict(context_sha256=sha(cp),baseline=root.tolist(),masses=values['bb_entries'].tolist(),
        fold_entries=values['bb_fold_entries'].tolist(),jam_entries=values['bb_jam_entries'].tolist())
    cache=load_complete_cache()
    return dict(models=models,context_path=cp,context_source=source,exact=exact,cache=cache,inputs=inputs,
        weights=weights('linear',78),checkpoint=ta['checkpoint'],policy_sha256=sha(policy_path))
