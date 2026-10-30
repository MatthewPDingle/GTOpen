"""CPU-only arithmetic checks with synthetic payoffs, never scientific labels."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from stack_context_matched_analysis_v1 import context_analysis,finish,quantile_linear,DEPTHS,DEALS
from crossed_complete_policy_comparison_v1 import CONTRAST_NAMES

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-context-matched-analysis-check-v1'


def main():
    output=OUT/(NAME+'-result.json');attempt=OUT/(NAME+'-attempt.json')
    if output.exists() or attempt.exists():
        raise ValueError('Completed or started check must not be repeated')
    module=Path(__file__).with_name('stack_context_matched_analysis_v1.py')
    with attempt.open('x') as stream:
        json.dump(dict(check_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                       module_sha256=hashlib.sha256(module.read_bytes()).hexdigest()),stream)
    started=time.monotonic(); contexts=[];expected=[]
    for depth in DEPTHS:
        values=np.empty((DEALS,2,4,2)); expected_contrasts=[]
        common=np.linspace(-.01,.01,DEALS)*depth
        gains=[]
        for seed in range(2):
            bb_gain=(.2+.01*seed)*depth + common/10
            btn_gain=(.15+.01*seed)*depth - common/10
            gains.extend([bb_gain,bb_gain,btn_gain,btn_gain])
            for pairing,(bb,btn) in enumerate(((0,0),(0,1),(1,0),(1,1))):
                value=common+bb*bb_gain-btn*btn_gain
                values[:,seed,pairing,0]=value
                values[:,seed,pairing,1]=.5-value
        row=context_analysis(values,depth=depth,dead_money=.5)
        for column,truth in zip(row['contrasts'],gains):
            assert abs(column['mean']-float(np.mean(truth)))<1e-9
            assert abs(column['sample_variance']-float(np.var(truth,ddof=1)))<1e-9
            assert abs(column['negative_deal_fraction']-np.mean(truth<0))<1e-12
            assert abs(column['paired_loss_95_bb']-float(np.quantile(-truth,.95,method='linear')))<1e-10
        contexts.append(row);expected.append([float(np.mean(gain))/depth for gain in gains])
    result=finish(contexts)
    assert result['registered_policy_improvement_criterion_met']
    assert np.max(abs(np.array([row['mean'] for row in result['equal_depth_normalized_gains']])-np.mean(expected,axis=0)))<1e-12
    assert result['simultaneous_family_alpha']==.05 and not result['preflop_accuracy_qualified']
    adverse=copy.deepcopy(contexts)
    adverse[0]['contrasts'][0].update(mean=-.001,lower=-.1,upper=.1)
    assert not finish(adverse)['registered_policy_improvement_criterion_met']
    inconclusive=copy.deepcopy(contexts)
    for context in inconclusive:
        context['contrasts'][0]['lower']=-context['depth']
    assert not finish(inconclusive)['registered_policy_improvement_criterion_met']
    rejected=0
    for changed in (contexts[:-1],contexts+[contexts[0]], [contexts[0]]*len(DEPTHS)):
        try:finish(changed)
        except ValueError:rejected+=1
        else:raise AssertionError('Incomplete coverage accepted')
    for key,value in (('family_error_probability',.05),('deals',2048),('profile_order',[])):
        changed=copy.deepcopy(contexts);changed[0][key]=value
        try:finish(changed)
        except ValueError:rejected+=1
        else:raise AssertionError('Changed design accepted')
    try:context_analysis(np.zeros((32,2,4,2)),depth=20,dead_money=.5)
    except ValueError:rejected+=1
    else:raise AssertionError('Interim look accepted')
    assert quantile_linear([1,2,3,10],.5)==2.5
    with output.open('x') as stream:
        json.dump(dict(complete=True,passed=True,seconds=time.monotonic()-started,contexts=len(contexts),
            contrasts=len(CONTRAST_NAMES)*len(contexts),negative_cases=rejected,
            matches_independent_numpy_means_variances_quantiles=True,positive_adverse_inconclusive_gates=True,
            inputs=json.loads(attempt.read_text()),new_poker_deals=False,new_labels=False,new_fits=False),stream)
    print(json.dumps(dict(passed=True,seconds=time.monotonic()-started,negative_cases=rejected)))


if __name__=='__main__':main()
