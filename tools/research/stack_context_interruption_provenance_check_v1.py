"""Synthetic trajectory corruption tests, with no scientific computation."""
import copy
import hashlib
import json
from pathlib import Path
import time
import psutil
import stack_context_interruption_provenance_v1 as proof

NAME='stack-context-interruption-provenance-check-v1'


def fixture():
    amendment='a'*64;progress={};rows=[]
    for arm,cycle in proof.CYCLES.items():
        updates=[]
        for i in range(1,65):
            cp=dict(file=f'{arm}-{i}.json',sha256=hashlib.sha256(f'{arm}:{i}'.encode()).hexdigest())
            row=dict(cycle=i,checkpoint=cp,recovered_without_scientific_repeat=(i==cycle or arm=='A-relative' and i==2))
            if i==cycle:row.update(interruption_recovery_amendment_sha256=amendment,recovery_action=proof.ACTIONS[arm])
            updates.append(row)
        p=dict(registration_sha256='r'*64,completed_cycles=64,checkpoint=updates[-1]['checkpoint'],updates=updates)
        progress[arm]=p
        prefix=dict(p,completed_cycles=cycle,checkpoint=updates[cycle-1]['checkpoint'],updates=updates[:cycle])
        rows.append(dict(arm=arm,cycle=cycle,checkpoint=updates[cycle-1]['checkpoint'],action=proof.ACTIONS[arm],
            progress_sha256=proof.publication_sha(prefix),all_preinterruption_bytes_preserved_in_archives=True))
    outcome=dict(complete=True,passed=True,boundaries=proof.CYCLES,amendment_sha256=amendment,arms=rows,
        original_parallel_v2_compatible=True,full_training_complete=False,scientific_evaluation_complete=False,production_modified=False)
    return progress,outcome,amendment


def main():
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS);began=time.monotonic()
    result_path=proof.OUT/(NAME+'-result.json');assert not result_path.exists()
    p,o,a=fixture();assert len(proof.validate_prefixes(p,o,amendment_sha256=a))==4
    rejected=[]
    def reject(label,mutate):
        x,y=copy.deepcopy(p),copy.deepcopy(o);mutate(x,y)
        try:proof.validate_prefixes(x,y,amendment_sha256=a)
        except (ValueError,KeyError,IndexError):rejected.append(label)
        else:raise AssertionError('Accepted '+label)
    reject('failed result',lambda x,y:y.update(passed=False))
    reject('partial result',lambda x,y:y.update(complete=False))
    reject('changed boundary',lambda x,y:y.update(boundaries=dict(proof.CYCLES,**{'B-relative':4})))
    reject('changed amendment',lambda x,y:y.update(amendment_sha256='b'*64))
    reject('incorrect accuracy claim',lambda x,y:y.update(scientific_evaluation_complete=True))
    reject('missing arm',lambda x,y:x.pop('B-relative'))
    reject('duplicate outcome',lambda x,y:y['arms'].__setitem__(1,copy.deepcopy(y['arms'][0])))
    reject('reordered cycle',lambda x,y:x['A-baseline']['updates'][3].update(cycle=5))
    reject('arbitrary new retry',lambda x,y:x['A-baseline']['updates'][7].update(recovered_without_scientific_repeat=True))
    reject('recovery extended',lambda x,y:x['A-relative']['updates'][4].update(interruption_recovery_amendment_sha256=a))
    reject('missing recovery record',lambda x,y:x['B-baseline']['updates'][3].pop('recovery_action'))
    reject('wrong recovered action',lambda x,y:x['A-relative']['updates'][3].update(recovery_action=proof.ACTIONS['A-baseline']))
    reject('changed complete prefix',lambda x,y:x['A-baseline']['updates'][0].update(additional_field='changed'))
    reject('missing preserved bytes',lambda x,y:y['arms'][0].update(all_preinterruption_bytes_preserved_in_archives=False))
    reject('changed recovered checkpoint',lambda x,y:y['arms'][0].update(checkpoint={'file':'substitution','sha256':'0'*64}))
    assert len(rejected)==15
    inputs={str(q):proof.sha(q) for q in (Path(__file__).resolve(),Path(proof.__file__).resolve(),proof.REG,proof.AUDIT)}
    value=dict(complete=True,passed=True,seconds=time.monotonic()-began,inputs=inputs,
        synthetic_64_cycle_metadata=True,rejected=rejected,actual_terminal_training_reviewed=False,
        actual_recovery_readback_outstanding=True,scientific_deals=0,fits=0,native_calls=0,gpu=False)
    with result_path.open('x',encoding='utf-8') as f:json.dump(value,f,sort_keys=True)
    print(json.dumps(value),flush=True)


if __name__=='__main__':main()
