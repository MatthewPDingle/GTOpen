"""Check typed exact policy evaluation and weighted averaging without CUDA."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1')
import copy
import time
from pathlib import Path
import numpy as np
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, hand_class
from sampled_visible_hybrid_checkpoint_v1 import read_object
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from sampled_visible_hybrid_policy_v1 import predict as base_predict
from exact_initial_hybrid_checkpoint_v1 import model_document
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from preflop_allin_matrix_v1 import AllinMatrix
from exact_initial_hybrid_policy_v1 import ExactInitialCpuBank64, predict
from reboot_research_idle_v1 import idle

PREFIX = 'exact-initial-policy-cpu-control-v1'


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic()-start < 300 and idle()
        assert psutil.virtual_memory().available > 20_000_000_000
    guard()
    import torch
    torch.set_num_threads(1)
    cp = OUT/'bb-context-candidate.json'
    source = cp.read_text()
    matrix_result = read(OUT/'preflop-allin-matrix-control-v1-result.json')
    matrix_path = Path(matrix_result['matrix_artifact'])
    matrix_hash = sha(matrix_path)
    assert matrix_hash == matrix_result['matrix_sha256']
    matrix = AllinMatrix(read(matrix_path), source)
    catalog_path = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog = catalog_path.read_text()
    prior_rp, prior_pp = [OUT/f'exact-initial-checkpoint-control-v1-{s}.json' for s in ('registration','result')]
    prior, passed = read(prior_rp), read(prior_pp)
    assert passed['passed'] and passed['registration_sha256'] == sha(prior_rp)
    objects = Path(prior['store'])
    checkpoint = __import__('json').loads(read_object(objects, passed['checkpoint']))
    model_args = dict(context_source=source, catalog_source=catalog,
                      matrix_sha256=matrix_hash, entry_mass=matrix.btn_mass)
    models = [model_document(objects, ref, **model_args) for ref in checkpoint['played_bank']]
    assert len(models) == 4
    query_path = Path('S:/GTOpen-research/wider-root-evaluation-control-v1/train-000000/queries.json')
    summary_path = query_path.parent/'summary.json'
    assert sha(query_path) == read(summary_path)['artifacts']['queries.json']
    queries = read(query_path)
    obs = queries['observations']
    hi = __import__('json').loads(source)['nodes'][0]['children'][3]+1
    response = np.array([o['actor']==1 and o['phase']==0 and int(o['hi'])==hi for o in obs])
    assert response.any() and all(obs[i]['own_history']==[] for i in np.flatnonzero(response))
    paths = [Path(__file__), ROOT/'tools/research/exact_initial_hybrid_policy_v1.py',
        ROOT/'tools/research/exact_initial_hybrid_checkpoint_v1.py',
        ROOT/'tools/research/exact_btn_policy_table_v1.py', cp, matrix_path, catalog_path,
        prior_rp, prior_pp, objects/passed['checkpoint']['file'], query_path, summary_path]
    paths.extend(objects/ref['file'] for ref in checkpoint['played_bank'])
    inputs = dict(prior['inputs'])
    inputs.update({str(p.resolve()):sha(p) for p in paths})
    rp = OUT/f'{PREFIX}-registration.json'
    save(rp, dict(inputs=inputs, maximum_seconds=300, weights=['equal','linear'],
        fixture='Historical base models with synthetic exact states; no jointly trained candidate.',
        gpu_used=False, operation='Single-model override and weighted first-response closed form; all other actual native rows and own-history weights must match the base bank.',
        production_modified=False, training_integration=False))
    class_probabilities = []
    single = []
    for model in models:
        guard()
        old_scores, old_p, old_coverage = base_predict(queries,model['base_model'],'cpu')
        scores, p, coverage = predict(queries,model,device='cpu',catalog_source=catalog,
                                    matrix_sha256=matrix_hash,entry_mass=matrix.btn_mass)
        assert np.array_equal(scores,old_scores) and coverage['base_table_rows']==old_coverage
        assert np.array_equal(p[~response],old_p[~response])
        state = ExactBtnRegrets.restore(model['exact_btn']['state'],context_sha256=sha(cp),entry_mass=matrix.btn_mass)
        classes = state.probabilities(np.full((169,2),.5))
        class_probabilities.append(classes)
        if model['generation']==0:
            assert np.array_equal(p,old_p) and coverage['exact_btn_rows']==0
        else:
            for i in np.flatnonzero(response):
                lo=int(obs[i]['lo']);c=hand_class([lo&63,(lo>>6)&63])
                assert np.array_equal(p[i],[*classes[c],0.,0.])
        single.append(coverage)
    averaged = []
    for name, sequence in [('equal',np.ones(4)),('linear',np.arange(1,5,dtype=float))]:
        weights=np.tile(sequence,(2,1))
        bank=ExactInitialCpuBank64(models,completed_iterations=4,weights_by_player=weights,**model_args)
        actual,support=bank.average(queries,guard=guard)
        old,support_old=VisibleHybridCpuBank64([d['base_model'] for d in models],context_source=source,weights_by_player=weights).average(queries,guard=guard)
        assert np.array_equal(actual[~response],old[~response])
        assert np.array_equal(support,support_old)
        target=np.average(np.stack(class_probabilities),axis=0,weights=sequence)
        maximum=0.
        for i in np.flatnonzero(response):
            lo=int(obs[i]['lo']);c=hand_class([lo&63,(lo>>6)&63])
            maximum=max(maximum,float(np.max(abs(actual[i]-[*target[c],0.,0.]))))
            assert support[i]==sequence.sum()
        assert maximum<1e-12 and np.max(abs(actual-old))>.01
        averaged.append(dict(weights=name,maximum_closed_form_error=maximum,
            outside_response_rows_unchanged=int((~response).sum()),own_history_weights_unchanged=True))
    rejected=[]
    def reject(label, fn):
        try:fn()
        except (ValueError,KeyError):rejected.append(label)
        else:raise AssertionError(f'Did not reject {label}')
    kwargs=dict(completed_iterations=4,weights_by_player=np.ones((2,4)),**model_args)
    reject('missing-played-model',lambda:ExactInitialCpuBank64(models[:-1],**kwargs))
    reject('reordered-models',lambda:ExactInitialCpuBank64([models[1],models[0],*models[2:]],**kwargs))
    next_doc=model_document(objects,checkpoint['next_model'],**model_args)
    reject('unplayed-next-model-included',lambda:ExactInitialCpuBank64([*models,next_doc],**kwargs))
    corrupt=copy.deepcopy(queries);corrupt['observations'][int(np.flatnonzero(response)[0])]['own_history']=[[0,1]]
    reject('impossible-own-history',lambda:bank.average(corrupt,guard=guard))
    for p,h in inputs.items():assert sha(p)==h
    guard()
    result=dict(passed=True,registration_sha256=sha(rp),single_model_coverage=single,
        averaging=averaged,rejected=rejected,seconds=time.monotonic()-start,
        gpu_used=False,cuda_execution_tested=False,training_integration=False,
        accuracy_qualified=False,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',result)
    print(result,flush=True)


if __name__=='__main__':main()
