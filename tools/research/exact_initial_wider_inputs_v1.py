"""Admit an audited exact-initial bank; control fixtures are explicitly separate."""
from pathlib import Path
import numpy as np
from later_average_support_v1 import OUT,read,weights,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha
from hu_exact_initial_fresh_exact_20260923 import load_bank,bank_args
from preflop_allin_matrix_v1 import AllinMatrix


def admitted(*,control=False):
    count=2 if control else 78
    train='exact-initial-fresh-control-v1' if control else 'exact-initial-fresh-pilot-v1'
    endpoint='exact-initial-fresh-exact-control-v1' if control else 'exact-initial-fresh-exact-v1'
    paths={key:OUT/f'{prefix}-{suffix}.json' for key,prefix,suffix in (
        ('tr',train,'registration'),('tp',train,'result'),('ts',train,'status'),
        ('rr',train,'readback-registration'),('ta',train,'independent-review'),
        ('er',endpoint,'registration'),('ep',endpoint,'result'),
        ('ea',endpoint,'independent-review'),('es',endpoint,'status'))}
    d={k:read(p) for k,p in paths.items()}
    assert d['tp']['passed'] and d['tp']['terminal'] and d['tp']['completed_iterations']==count
    assert d['tp']['registration_sha256']==sha(paths['tr'])
    assert d['ts']['state']=='complete' and d['ts']['error'] is None and d['ts']['exit_code']==0
    assert d['ta']['passed'] and d['ta']['completed_updates']==count
    assert d['ta']['source_registration_sha256']==sha(paths['tr']) and d['ta']['source_result_sha256']==sha(paths['tp'])
    assert d['ta']['readback_registration_sha256']==sha(paths['rr'])
    assert d['er']['count']==count and d['ep']['passed'] and d['ea']['passed']
    assert d['ep']['registration_sha256']==d['ea']['registration_sha256']==sha(paths['er'])
    assert d['ea']['result_sha256']==sha(paths['ep'])
    assert d['es']['state']=='complete' and d['es']['error'] is None
    assert d['tr']['control_only']==d['er']['control_only']==d['ep']['control_only']==d['ea']['control_only']==control
    if control: assert d['ep']['screening_passed'] is None
    else: assert d['ep']['screening_passed'] is True and all(d['ep']['gates'].values())
    assert d['tr']['config']['current_policy_inference']=='float64-widened-float32-weights-v1'
    inputs={**d['tr']['inputs'],**d['rr']['inputs'],**d['er']['inputs'],**d['ep']['artifacts']}
    inputs.update({str(p):sha(p) for p in paths.values()})
    cp=OUT/'bb-context-candidate.json';source=cp.read_text()
    matrix_paths=[OUT/f'preflop-allin-matrix-control-v1-{s}.json' for s in ('registration','result','independent-review')]
    mr,mp,ma=map(read,matrix_paths)
    assert ma['passed'] and ma['result_sha256']==sha(matrix_paths[1]) and ma['registration_sha256']==sha(matrix_paths[0])
    matrix_path=Path(mp['matrix_artifact']);assert sha(matrix_path)==mp['matrix_sha256']==ma['matrix_sha256']
    inputs.update(mr['inputs']);inputs.update({str(p):sha(p) for p in [*matrix_paths,matrix_path,cp,Path(__file__)]})
    prior=Path('T:/GTOpen-research/later-average-wider-recovery-v1/evaluation/response.json')
    old={s:OUT/f'later-average-wider-recovery-v1-{s}.json' for s in ('registration','result','independent-review','evaluation')}
    op,oa,oe=[read(old[s]) for s in ('result','independent-review','evaluation')]
    assert op['passed'] and oa['passed'] and oe['complete']
    assert op['registration_sha256']==oa['registration_sha256']==oe['registration_sha256']==sha(old['registration'])
    assert oa['evaluation_sha256']==sha(old['evaluation'])
    assert oe['result_sha256']==sha(prior.parent/'result.json')
    assert read(prior.parent/'result.json')['response_sha256']==sha(prior)
    inputs.update({str(p):sha(p) for p in [*old.values(),prior,prior.parent/'result.json']})
    for p,h in inputs.items():assert sha(p)==h,p
    models=load_bank(d['tr'],d['ta'],source,count)
    policy_path=Path(d['er']['store'])/'linear-policy.json';p=read(policy_path)
    assert d['ep']['artifacts'][str(policy_path)]==sha(policy_path)
    assert p['schedule']=='linear' and p['played_generations']==list(range(count)) and p['excluded_generation']==count
    assert p['weights']==weights('linear',count).tolist() and p['checkpoint']==d['tp']['final_checkpoint']
    root=np.asarray(p['root_probabilities']);calls=np.asarray([0. if x is None else x for x in p['btn_call_probabilities']])
    values=AllinMatrix(read(matrix_path),source).evaluate(root,calls)
    for row in d['ep']['pairings']['linear/linear']['bb_classes']:
        c=row['hand_class']
        for key,target in [('bb_entries','entry_probability'),('bb_fold_entries','fold_value_per_entry'),('bb_jam_entries','jam_value_per_entry')]:
            assert abs(values[key][c]-row[target])<1e-12
    exact=dict(context_sha256=sha(cp),baseline=root.tolist(),masses=values['bb_entries'].tolist(),
               fold_entries=values['bb_fold_entries'].tolist(),jam_entries=values['bb_jam_entries'].tolist())
    cache=load_complete_cache()
    return dict(models=models,context_path=cp,context_source=source,exact=exact,cache=cache,inputs=inputs,
        weights=weights('linear',count),checkpoint=d['tp']['final_checkpoint'],policy_sha256=sha(policy_path),
        count=count,bank_args=bank_args(source),control_only=control,
        prior_response_path=prior,prior_response_sha256=sha(prior))
