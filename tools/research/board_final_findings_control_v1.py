"""Synthetic report checks, plus read-only historical timing schema checks.

No new policy training, fresh test deals, or candidate payoff inspection.
"""
import argparse
import contextlib
import copy
import importlib.util
import io
import json
import tempfile
from pathlib import Path


def main(module_path, out, result_path):
    spec = importlib.util.spec_from_file_location('report_under_test',module_path)
    report = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(report)
    assert not result_path.exists()
    p = [[[1.,0.,0.,0.] for _ in range(169)],[[0.,1.,0.,0.] for _ in range(169)],
         [[0.,0.,1.,0.] for _ in range(169)],[[0.,1.,0.,0.] for _ in range(169)]]
    comparisons = {}
    for name,a,b in (('baseline_cross_seed',0,2),('candidate_cross_seed',1,3),
                     ('first_matched_change',0,1),('replication_matched_change',2,3)):
        tv = [.5*sum(abs(x-y) for x,y in zip(p[a][c],p[b][c])) for c in range(169)]
        comparisons[name] = dict(entry_weighted_total_variation=tv[0],class_total_variation=tv,
            classes_with_different_most_frequent_action=169 if tv[0] else 0)
    roots = dict(policy_order=list(report.POLICIES),action_order=list(report.ACTIONS),
        root_probabilities=p,entry_masses=[1/169]*169,aggregate_action_frequencies=[bank[0] for bank in p],
        comparisons=comparisons,candidate_minus_baseline_variation=-1.)
    analysis = dict(deals=65536,control_only=False,family_error_probability=.05,units='bb per entry',
        interval_method='two-sided bounded empirical Bernstein; Bonferroni over eight contrasts and one final look',
        contrasts=[dict(name=name,count=65536,mean=mean,lower=mean-.5,upper=mean+.5,standard_error=.1)
                   for name,mean in zip(report.CONTRASTS,(1.,-1.,0.,0.,0.,0.,0.,0.))])
    report.validate_outcomes(analysis,roots)
    classes = report.class_table(roots)
    assert len(classes) == len({r['hand'] for r in classes}) == 169
    assert {i:classes[i]['hand'] for i in (0,1,13,154,155,167,168)} == {
        0:'22',1:'32o',13:'32s',154:'KK',155:'AKo',167:'AKs',168:'AA'}
    rejected = []
    mutations = (
        ('missing unfavorable contrast',lambda a,r:a['contrasts'].pop(1)),
        ('changed contrast order',lambda a,r:a['contrasts'].reverse()),
        ('different sample count',lambda a,r:a['contrasts'][0].update(count=32)),
        ('missing hand class',lambda a,r:r['root_probabilities'][0].pop()),
        ('wrong stability sign',lambda a,r:r.update(candidate_minus_baseline_variation=1.)),
        ('mismatched aggregate',lambda a,r:r['aggregate_action_frequencies'][0].__setitem__(0,.5)),
        ('nan probability',lambda a,r:r['root_probabilities'][0][0].__setitem__(0,float('nan'))),
        ('different interval method',lambda a,r:a.update(interval_method='ordinary standard error')),
    )
    for name,mutate in mutations:
        a,r = copy.deepcopy(analysis),copy.deepcopy(roots)
        mutate(a,r)
        try:
            report.validate_outcomes(a,r)
        except ValueError:
            rejected.append(name)
        else:
            raise AssertionError('Invalid report accepted: '+name)
    inputs = {str(module_path):report.sha(module_path),str(Path(__file__)):report.sha(__file__)}
    costs = []
    for arm in report.ARMS[::2]:
        rp = out/f'weighted-training-readback-parallel-v1-w4-{arm}-0078-registration.json'
        reg = report.read(rp);inputs[str(rp)] = report.sha(rp)
        metrics = []
        for folder in reg['folders']:
            mp = Path(folder)/'metrics.json'
            assert report.sha(mp) == reg['inputs'][str(mp)]
            metrics.append(report.read(mp))
        value = report.cost_summary(arm,metrics)
        assert value['updates'] == 78 and value['residual_board_wait_seconds'] is None
        costs.append(value)
    resources = dict(arms=costs,observed_candidate_boundary_peak_allocated_bytes=1_000_000_000,
        candidate_allocation_limit_bytes=2_000_000_000,candidate_final_allocated_bytes=1_000_000_000,
        control_final_allocated_bytes=1_000_000_000)
    text = report.render(analysis,roots,dict(batches=2048,observations=12345,maximum_statistical_error=0.),resources)
    assert 'positive gains in **1**' in text and 'negative gains in **1**' in text and '**6 inconclusive**' in text
    assert all(text.count(name) == 1 for name in report.CONTRASTS)
    assert '**-100.00 percentage points**' in text and '9281101' in text and '9278101' not in text
    assert 'not total compute' in text and 'not evidence of equivalence' in text
    with tempfile.TemporaryDirectory() as directory:
        report.OUT = Path(directory)
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            report.main()
        readiness = json.loads(output.getvalue())
        assert not readiness['prerequisites_present'] and not readiness['payoffs_opened']
        assert list(report.OUT.iterdir()) == []
        try:
            report.main(True)
        except ValueError:
            pass
        else:
            raise AssertionError('Incomplete audit gate accepted')
        assert list(report.OUT.iterdir()) == []
    result = dict(passed=True,inputs=inputs,synthetic_only=True,candidate_payoffs_opened=False,
        report_outputs_written=False,classes_checked=169,contrasts_checked=8,rejections=rejected,
        historical_cost_arms_checked=[x['arm'] for x in costs],missing_prerequisites_rejected=True,
        production_modified=False)
    with result_path.open('x',encoding='utf-8') as stream:
        json.dump(result,stream,indent=2,allow_nan=False);stream.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'inputs'}),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--result',type=Path,required=True)
    a = parser.parse_args();main(a.module,a.out,a.result)
