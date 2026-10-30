"""Independent scalar aggregate checks and paired fixed-bank descriptions."""
import csv
import hashlib
import itertools
import json
import math
from pathlib import Path
import sys

import numpy as np
from hu_frozen_root_precision_20260926 import OUT, read, sha, values_from
from frozen_root_precision_summary_v1 import summarize

NAMES = ('first-old', 'first-new', 'repeat-old', 'repeat-new')
CONTRASTS = ('call_minus_fold', 'raise_minus_fold', 'raise_minus_call')


def moments(x):
    n = len(x)
    if not n:
        return dict(count=0, mean=None, standard_error=None)
    mean = math.fsum(x) / n
    se = math.sqrt(math.fsum((z - mean)**2 for z in x) / (n - 1) / n) if n > 1 else None
    return dict(count=n, mean=mean, standard_error=se)


def audit_and_compare(v, c, masses, analysis):
    """Recompute every aggregate from scalar per-deal contrasts, not saved SEs."""
    errors = []
    for b, bank in enumerate(analysis['banks']):
        se_terms = [[], [], []]
        covered, half_covered, disagreements = [], [], []
        for h in range(169):
            ids = [i for i, hand in enumerate(c) if int(hand) == h]
            row = bank['classes'][h]
            assert row['count'] == len(ids) and row['hand_class'] == h
            assert row['entry_mass'] == masses[h]
            if not ids:
                assert row['contrast_means'] is None and row['descriptive_standard_errors'] is None
                assert all(x['count'] == 0 and x['maximizing_non_jam_action'] is None for x in row['halves'])
                continue
            for k, (a, d) in enumerate(((1, 0), (2, 0), (2, 1))):
                m = moments([float(v[b, i, a] - v[b, i, d]) for i in ids])
                errors.append(abs(m['mean'] - row['contrast_means'][k]))
                if len(ids) > 1:
                    errors.append(abs(m['standard_error'] - row['descriptive_standard_errors'][k]))
                    se_terms[k].append(masses[h] * m['standard_error']**2)
                else:
                    assert row['descriptive_standard_errors'] is None
            if len(ids) > 1:
                covered.append(masses[h])
            winners = []
            for half in range(2):
                sub = [i for i in ids if i % 2 == half]
                assert row['halves'][half]['count'] == len(sub)
                if sub:
                    means = [math.fsum(float(v[b, i, a]) for i in sub) / len(sub) for a in range(3)]
                    winner = max(range(3), key=means.__getitem__)
                    assert winner == row['halves'][half]['maximizing_non_jam_action']
                    errors.extend(abs(x-y) for x, y in zip(means, row['halves'][half]['non_jam_action_means']))
                    winners.append(winner)
            if len(winners) == 2:
                half_covered.append(masses[h])
                if winners[0] != winners[1]:
                    disagreements.append(masses[h])
        mass = math.fsum(covered)
        if mass:
            rms = [math.sqrt(math.fsum(x) / mass) for x in se_terms]
            errors.extend(abs(x-y) for x, y in zip(rms, bank['rms_class_standard_error_on_covered_mass']))
        else:
            assert bank['rms_class_standard_error_on_covered_mass'] is None
        errors.extend((abs(mass-bank['standard_error_covered_entry_mass']),
                       abs(math.fsum(half_covered)-bank['half_comparison_covered_entry_mass']),
                       abs(math.fsum(disagreements)-bank['half_maximizer_disagreement_entry_mass'])))
    assert max(errors, default=0.) < 1e-9
    paired = []
    # Both players' continuation policies differ between these self-play banks.
    # Positive differences are not unilateral player gains or treatment wins.
    for old, new in itertools.combinations(range(4), 2):
        rows = []
        for h in range(169):
            ids = [i for i, hand in enumerate(c) if int(hand) == h]
            values = []
            for a, d in ((1, 0), (2, 0), (2, 1)):
                values.append(moments([float((v[new,i,a]-v[new,i,d])-(v[old,i,a]-v[old,i,d])) for i in ids]))
            rows.append(dict(hand_class=h, entry_mass=masses[h], contrasts=values))
        paired.append(dict(direction=f'{NAMES[new]} minus {NAMES[old]}', classes=rows))
    return dict(passed=True, maximum_scalar_error=max(errors, default=0.), paired_banks=paired,
                interpretation='Common-deal differences of fixed-continuation action contrasts; both policies change. Not unilateral gains, confidence intervals, training targets, or a best-response bound.')


def self_test():
    v = np.zeros((4,4,4)); v[:,:,0] = -1; v[:,:,1] = [0,2,4,6]; v[:,:,2] = 3
    v[:,:,3] = [10,-10,20,-20]
    c = np.zeros(4, dtype=int); masses = [1.] + [0.]*168
    baseline = summarize(v,c,masses)
    result = audit_and_compare(v,c,masses,baseline)
    assert result['passed']
    row = baseline['banks'][0]['classes'][0]
    assert row['contrast_means'] == [4.,4.,0.]
    assert abs(row['descriptive_standard_errors'][0] - math.sqrt(5/3)) < 1e-12
    assert baseline['banks'][0]['half_maximizer_disagreement_entry_mass'] == 1.
    assert row['halves'][0]['maximizing_non_jam_action'] == 2
    assert row['halves'][1]['maximizing_non_jam_action'] == 1
    assert all(x['mean'] == 0 and x['standard_error'] == 0 for p in result['paired_banks'] for x in p['classes'][0]['contrasts'])
    # Ensure covariance of paired observations is retained and jam is excluded.
    v[1,:,1] += 2
    v[:,:,3] = 1e6
    changed = audit_and_compare(v,c,masses,summarize(v,c,masses))
    assert changed['paired_banks'][0]['classes'][0]['contrasts'][0]['mean'] == 2
    assert changed['paired_banks'][0]['classes'][0]['contrasts'][0]['standard_error'] == 0
    assert summarize(v,c,masses)['banks'][0] == baseline['banks'][0]
    bad = json.loads(json.dumps(baseline)); bad['banks'][0]['rms_class_standard_error_on_covered_mass'][0] += .1
    try:
        audit_and_compare(np.array([v[0]]*4),c,masses,bad)
    except AssertionError:
        pass
    else:
        raise AssertionError('Must reject corrupted aggregate')
    return dict(passed=True, checks=['analytic means and standard errors','fixed parity split','missing-class uncertainty','paired covariance','jam exclusion','aggregate tamper rejection'])


def main(prefix):
    assert prefix in ('frozen-root-precision-control-v1','frozen-root-precision-study-v1')
    rp=OUT/f'{prefix}-registration.json'; sp=OUT/f'{prefix}-result.json'; vp=OUT/f'{prefix}-readback.json'
    reg=read(rp); result=read(sp); review=read(vp)
    assert read(OUT/f'{prefix}-status.json')['state']=='complete'
    assert result['passed'] and result['registration_sha256']==sha(rp)
    assert review['passed'] and review['source_result_sha256']==sha(sp)
    for p,h in reg['inputs'].items(): assert sha(p)==h,p
    assert [x['source'] for x in result['jobs']]==reg['sources']
    assert [x['index'] for x in result['jobs']]==list(range(len(reg['sources'])))
    v,c=values_from(reg,result['jobs'])
    ap=Path(reg['store'])/'analysis.json'; assert sha(ap)==result['analysis_sha256']
    masses=read(OUT/'later-action-final-root-stability.json')['entry_masses']
    doc=audit_and_compare(v,c,masses,read(ap))
    doc.update(source_result_sha256=sha(sp),source_readback_sha256=sha(vp),
               analysis_sha256=sha(ap),reviewer_sha256=sha(Path(__file__)),
               rows=len(c),control_only=result['control_only'],fresh_deals=False)
    with (OUT/f'{prefix}-aggregate-audit.json').open('x') as f:
        json.dump(doc,f,separators=(',',':'),allow_nan=False)
    print(json.dumps({k:v for k,v in doc.items() if k!='paired_banks'}))


if __name__=='__main__':
    if sys.argv[1:]==['--self-test']:
        print(json.dumps(self_test()))
    else:
        main(sys.argv[1])
