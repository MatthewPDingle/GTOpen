"""Scalar arithmetic, rejection atomicity and recovery control; no training."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
import math
from pathlib import Path
import time
import numpy as np
from board_root_accumulator_v1 import BoardRootRegrets, TARGET, digest
from board_fixed_policy_control_v1 import ROOT, OUT, read, save, sha
from weighted_root_accumulator_v1 import WeightedRootRegrets

PREFIX = 'board-root-accumulator-control-v1'


def fixture(state, generation):
    plan = state.plan()
    rng = np.random.default_rng(9280000+generation)
    p = rng.random((169, 4)); p /= p.sum(1)[:, None]
    exact = rng.normal(0, 15, (169, 4)); exact[:, 0] = -1
    values = rng.normal(0, 30, (len(plan['boards']), 169, 4)); values[:, :, (0, 3)] = 0
    model = digest(dict(synthetic_model=generation))
    e = dict(format=1, method=TARGET, generation=generation,
        plan_sha256=digest(plan), context_sha256=state.config['context_sha256'],
        matrix_sha256=state.config['matrix_sha256'], model_sha256=model,
        played_policy_sha256=digest(p.tolist()), exact_terms_sha256=digest(exact.tolist()),
        draws=[dict(draw_index=i, board=board, model_sha256=model,
                    tree_sha256=digest(dict(synthetic_tree=i, generation=generation)),
                    policy_recipe_sha256=digest(dict(synthetic_policy=i, generation=generation)),
                    values=x.tolist(), values_sha256=digest(x.tolist()))
               for i, (board, x) in enumerate(zip(plan['boards'], values))])
    return plan, e, p, exact, values


def main():
    started = time.monotonic()
    rp = OUT/f'{PREFIX}-registration.json'; result_path = OUT/f'{PREFIX}-result.json'
    assert not rp.exists() and not result_path.exists()
    paths = [Path(__file__), ROOT/'tools/research/board_root_accumulator_v1.py',
             ROOT/'tools/research/weighted_root_accumulator_v1.py',
             OUT/'BOARD-PRECISION-REPEAT-DECISION.md']
    save(rp, dict(inputs={str(p):sha(p) for p in paths},
        scope='Synthetic root-state mechanism only; no native targets, network fits or full training checkpoint.',
        cases=3, generations=3, budgets=[1,512,4096], boards=[1,4,16], maximum_seconds=60))
    errors = []; rejections = []; legacy_rejections = 0
    for budget, boards in zip([1,512,4096], [1,4,16]):
        mass = np.arange(1.,170.); mass /= mass.sum()
        state = BoardRootRegrets(context_sha256='a'*64, matrix_sha256='b'*64,
            entry_mass=mass.tolist(), physical_budget=budget, boards_per_generation=boards, board_seed=9280100)
        scalar_regrets = [[0.]*4 for _ in range(169)]
        restored = None
        external_rng = np.random.default_rng(777)
        for generation in range(3):
            plan,e,p,exact,values = fixture(state,generation)
            # Independent scalar reconstruction, not the candidate reducer.
            scalar_delta = []
            for c in range(169):
                q = [float(exact[c,a])+math.fsum(float(v[c,a]) for v in values)/boards for a in range(4)]
                baseline = math.fsum(float(p[c,a])*q[a] for a in range(4))
                row = [budget*float(mass[c])*(q[a]-baseline) for a in range(4)]
                scalar_delta.append(row)
                for a in range(4):scalar_regrets[c][a] += row[a]
            before = state.document(); external_before = copy.deepcopy(external_rng.bit_generator.state)
            corruptions = []
            def corrupt(name, change):
                pp,ee,prob,ex = copy.deepcopy(plan),copy.deepcopy(e),p.copy(),exact.copy()
                change(pp,ee,prob,ex);corruptions.append((name,pp,ee,prob,ex))
            corrupt('missing draw',lambda pp,ee,prob,ex:ee['draws'].pop())
            corrupt('wrong draw index',lambda pp,ee,prob,ex:ee['draws'][0].update(draw_index=1))
            corrupt('wrong cards',lambda pp,ee,prob,ex:ee['draws'][0].update(board=[0,0,1,2,3]))
            corrupt('wrong generation',lambda pp,ee,prob,ex:ee.update(generation=generation+1))
            corrupt('wrong context',lambda pp,ee,prob,ex:ee.update(context_sha256='c'*64))
            corrupt('wrong model',lambda pp,ee,prob,ex:ee['draws'][0].update(model_sha256='c'*64))
            corrupt('stale plan',lambda pp,ee,prob,ex:pp.update(parent_state_sha256='c'*64))
            corrupt('changed values',lambda pp,ee,prob,ex:ee['draws'][0]['values'][0].__setitem__(1,999.))
            corrupt('nonfinite value',lambda pp,ee,prob,ex:ee['draws'][0]['values'][0].__setitem__(1,float('nan')))
            corrupt('changed exact',lambda pp,ee,prob,ex:ex.__setitem__((0,1),999.))
            corrupt('changed policy',lambda pp,ee,prob,ex:prob.__setitem__((0,1),1.))
            def nonvariable(pp,ee,prob,ex):
                ee['draws'][0]['values'][0][0] = 1.
                ee['draws'][0]['values_sha256'] = digest(ee['draws'][0]['values'])
            corrupt('fold board contribution',nonvariable)
            for name,pp,ee,prob,ex in corruptions:
                try:state.step(pp,ee,played_policy=prob,exact_terms=ex)
                except (ValueError,KeyError,TypeError):pass
                else:raise AssertionError('Accepted '+name)
                assert state.document()==before and external_rng.bit_generator.state==external_before
                assert state.plan()==plan
                rejections.append(name)
            delta=state.step(plan,e,played_policy=p,exact_terms=exact)
            errors.append(float(np.max(abs(delta-np.array(scalar_delta)))))
            errors.append(float(np.max(abs(state.regrets-np.array(scalar_regrets)))))
            assert errors[-1]<1e-9 and errors[-2]<1e-9
            if restored is not None:
                assert restored.plan()==plan
                restored.step(plan,e,played_policy=p,exact_terms=exact)
                assert restored.document()==state.document()
            # Plain JSON round trip, then require identical next chance and policy.
            restored=BoardRootRegrets.restore(json.loads(json.dumps(state.document())),expected_config=state.config)
            assert restored.plan()==state.plan()
            assert np.array_equal(restored.probabilities(p),state.probabilities(p))
            assert np.max(abs(state.probabilities(p).sum(1)-1))<1e-12
            try:WeightedRootRegrets.restore(state.document(),context_sha256='a'*64,matrix_sha256='b'*64)
            except ValueError:legacy_rejections+=1
            else:raise AssertionError('Legacy weighted reader admitted board state')
        for kind in ('seal','counter','method','history','config'):
            doc=state.document()
            if kind=='seal':doc['regret_sums'][0][0]+=1
            else:
                if kind=='counter':doc['board_draws']+=1
                if kind=='method':doc['method']='source-deal-weighted-bb-root-regrets-v1'
                if kind=='history':doc['history'][1]['generation']=0
                if kind=='config':doc['config']['board_seed']+=1
                doc.pop('state_sha256');doc['state_sha256']=digest(doc)
            try:BoardRootRegrets.restore(doc,expected_config=state.config)
            except ValueError:rejections.append('checkpoint '+kind)
            else:raise AssertionError('Accepted corrupted checkpoint '+kind)
    reg=read(rp)
    for path,h in reg['inputs'].items():assert sha(path)==h,path
    elapsed=time.monotonic()-started;assert elapsed<60
    result=dict(passed=True,registration_sha256=sha(rp),cases=3,updates=9,
        maximum_scalar_error=max(errors),atomic_target_rejections=108,checkpoint_rejections=15,
        legacy_reader_rejections=legacy_rejections,common_recovery_continuations=6,
        rejected_mutations=len(rejections),seconds=elapsed,training_admitted=False,
        production_modified=False,accuracy_qualified=False,
        limitations='Synthetic numerical state control. Full training transaction, native-target admission and model reader remain to implement.')
    assert len(rejections)==123 and legacy_rejections==9
    save(result_path,result);print(json.dumps(result))


if __name__=='__main__':main()
