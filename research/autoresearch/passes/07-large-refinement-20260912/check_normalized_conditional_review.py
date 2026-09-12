"""Fill the missing conditional audit of previously rejected normalized runs."""
from check_root_repair import checked_local
from check_joint import *


def verify():
    paths=json.loads((HERE/'exploration-diagnostic-paths.json').read_text());cases=[]
    for seed in (42,314159):
        for mode in (0,1):
            n=f'normalized-regret-six-{seed}-{mode}-v1';p=read(n+'-conditional-review-exit.json')
            require(p['returncode']==0 and p['reason'] is None,'Incomplete review')
            prior=read(n+'-result.json');audit=read(n+'-conditional-review.json')
            require(prior['samples']==64 and prior['schedule']=='gamma15' and prior['seed']==seed and prior['normalized_regret'] is bool(mode),'Wrong archived experiment')
            passed=checked_local(audit['rows'],paths);last=prior['checks'][-1]
            require(last['full_reference_samples']==1024 and abs(sum(last['gaps'])-last['gap'])<1e-12,'Invalid archived full check')
            cases.append(dict(seed=seed,normalized=bool(mode),iteration=prior['iteration'],gap=last['gap'],conditional_passes=passed,
                              global_qualified=prior['converged_twice'],combined_qualified=prior['converged_twice'] and passed==6))
    return dict(evidence_verified=True,cases=cases,scope='Read-only additional quality audit; original rejection retained, no new learning or qualified speedup')


if __name__=='__main__':print(json.dumps(verify(),indent=2))
