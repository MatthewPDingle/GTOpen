"""Target-adapter invariants on an already-inspected training subbatch."""
import copy
import json
import math
from pathlib import Path
from showdown_root_targets_v1 import derive
from showdown_control_reference_v1 import score
from hu_frozen_root_precision_20260926 import OUT,ROOT,read,sha,save


def main():
    folder=Path('T:/GTOpen-research/later-action-matched-first-v1/iteration-0017/batch-00')
    paths=[folder/f'{n}.json' for n in ('integrated-targets','queries','policies')]
    cp=OUT/'showdown-root-control-coefficients-v1.json'
    source,queries,policies=[read(p) for p in paths];coefs=read(cp)
    before=copy.deepcopy(source);batch=json.loads(queries['batch_source'])
    scores=dict(format=1,input_source=json.dumps(dict(format=1,deals=batch['deals'])),twice_bb_share=[score(d) for d in batch['deals']])
    corrected=derive(source,queries,policies,scores,coefs)
    assert source==before and corrected['method']!=source['method']
    zero=copy.deepcopy(coefs);zero['call_raise_coefficients']=[[0.,0.] for _ in range(169)]
    identity=derive(source,queries,policies,scores,zero)
    for original,unchanged,new in zip(source['bb_root_corrections'],identity['bb_root_corrections'],corrected['bb_root_corrections']):
        assert original['action_values']==unchanged['action_values']
        assert new['action_values'][0]==original['action_values'][0]
        assert new['action_values'][3]==original['action_values'][3]
    # Integrate only the correction over all three possible showdown shares.
    # Exact conditional probabilities make its expectation zero for each pair.
    alternatives=[]
    for outcome in range(3):
        altered=dict(scores,twice_bb_share=[outcome]*len(batch['deals']))
        alternatives.append(derive(source,queries,policies,altered,coefs))
    maximum=0.
    for i,count in enumerate(batch['allin_counts']):
        probabilities=[count[k]/count['boards'] for k in ('losses','ties','wins')]
        old=source['bb_root_corrections'][i]
        for key in ('action_values','advantages'):
            for action in range(4):
                expected=math.fsum(p*d['bb_root_corrections'][i][key][action] for p,d in zip(probabilities,alternatives))
                maximum=max(maximum,abs(expected-old[key][action]))
    assert maximum<1e-10
    bad=copy.deepcopy(scores);doc=json.loads(bad['input_source']);doc['deals'][0][0]=doc['deals'][0][1];bad['input_source']=json.dumps(doc)
    try:derive(source,queries,policies,bad,coefs)
    except ValueError:pass
    else:raise AssertionError('Changed card binding accepted')
    save(OUT/'showdown-root-target-control-v1-derived.json',corrected)
    sources=paths+[cp,ROOT/'tools/research/showdown_root_targets_v1.py',ROOT/'tools/research/showdown_control_reference_v1.py',Path(__file__).resolve()]
    save(OUT/'showdown-root-target-control-v1-result.json',dict(passed=True,rows=len(batch['deals']),
        source_sha256={str(p):sha(p) for p in sources},maximum_expected_target_error=maximum,
        zero_coefficient_identity=True,fold_and_exact_jam_unchanged=True,source_unmodified=True,changed_cards_rejected=True,
        training_integrated=False,production_modified=False,
        scope='Root-target adapter only; theoretical correction expectation checked with saved exact private-pair counts. No new training or range accuracy claim.'))
    print(json.dumps(dict(passed=True,rows=len(batch['deals']),maximum_expected_target_error=maximum)))


if __name__=='__main__':main()
