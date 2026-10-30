"""Scalar check of generation-zero contribution without neural inference."""
import hashlib
import json
import math
from pathlib import Path
import time

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='initial-generation-share-v1'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic();maximum=0.
    def close(a,b):
        nonlocal maximum
        err=abs(a-b);assert math.isfinite(err) and err<1e-12
        maximum=max(maximum,err)
    rp,pp=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    reg,result=read(rp),read(pp);assert result['passed'] and result['registration_sha256']==sha(rp)
    for p,h in reg['inputs'].items():assert sha(p)==h
    # The sampled class masses are separately frozen by the parent diagnostic.
    parent=read(OUT/'paired-continuation-v1-registration.json')
    sampled=Path('T:/GTOpen-research/root-retained-wider-study-v1/evaluation/training-deals.json')
    assert parent['inputs'][str(sampled)]==sha(sampled)
    assert result['class_masses']==read(sampled)['original_class_masses']
    m=result['class_masses'];close(math.fsum(m),1.)
    for t,row in zip(reg['trials'],result['trials']):
        trial=read(t['result']);ref=row['initial_model_reference'];objects=Path(trial['store'])/'objects'
        # Immutable model object naming and payload identity are also checked
        # by the original published reference's path/sha256 fields.
        from sampled_visible_hybrid_checkpoint_v1 import read_object
        model=json.loads(read_object(objects,ref));assert model['generation']==ref['generation']==0
        base=model['exact_model']['base_model'];assert base['preflop_tables']==[None,None]
        state=model['integrated_root']['state'];assert state['completed_updates']==0 and not any(state['sample_counts'])
        for net in base['networks']:
            for key,values in net.items():assert all(v==(1. if key=='b2' else 0.) for v in values)
        policy=read(t['policy']);avg=policy['root_probabilities'];assert avg==row['average_probabilities']
        assert policy['weights']==[list(range(1,79))]*2
        assert row['initial_probabilities']==[[.25]*4 for _ in range(169)]
        for c in range(169):
            for a in range(4):close(.25/(3081*avg[c][a]),row['generation_zero_share'][c][a])
        for a,summary in enumerate(row['summary']):
            assert summary['action']==a
            for name,threshold in [('at_least_half',.5),('at_least_95_percent',.95),('all_within_1e12',1-1e-12)]:
                classes=[c for c in range(169) if .25/(3081*avg[c][a])>=threshold]
                got=summary['thresholds'][name]
                assert got['classes']==classes and got['count']==len(classes)
                close(math.fsum(m[c] for c in classes),got['incoming_class_mass'])
            close(.25/(3081*math.fsum(m[c]*avg[c][a] for c in range(169))),summary['actual_action_mass_from_initial_generation'])
    target=OUT/f'{PREFIX}-independent-review.json';assert not target.exists()
    value=dict(passed=True,result_sha256=sha(pp),registration_sha256=sha(rp),reader_sha256=sha(Path(__file__)),
        maximum_scalar_error=maximum,seconds=time.monotonic()-start,
        scope='Initial uniform network/table structure and all root-action contribution fractions reconstructed with scalar sums. Shares are root support accounting, not deeper-state inference or strategic accuracy.')
    target.write_text(json.dumps(value,separators=(',',':'))+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(value))


if __name__=='__main__':main()
