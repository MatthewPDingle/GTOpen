"""Present the completed, independently reviewed study; never reads partial outcomes."""
import argparse
import hashlib
import json
import math
from pathlib import Path

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='river-matched-continuation-v1'
REG=OUT/(NAME+'-registration.json')
RESULT=OUT/(NAME+'-result.json')
REVIEW_REG=OUT/(NAME+'-review-v1-registration.json')
REVIEW=OUT/(NAME+'-independent-review-v1.json')
REPORT=OUT/'RIVER-MATCHED-CONTINUATION-FINDINGS.md'
REGISTERED_SHA='6b4b4dec4d0580d3aed5b3c2a38361eb91a58ab5dee778d929b919408ebbf14a'
ARMS=('A-baseline','A-river','B-baseline','B-river')
COMPARISONS=(
    ('newBB-v-oldBB-against-oldBTN','BB against baseline BTN'),
    ('newBB-v-oldBB-against-newBTN','BB against candidate BTN'),
    ('newBTN-v-oldBTN-against-oldBB','BTN against baseline BB'),
    ('newBTN-v-oldBTN-against-newBB','BTN against candidate BB'))
NAMES=tuple(f'{seed}:{name}' for seed in ('first','replication') for name,_ in COMPARISONS)

def read(path):return json.loads(path.read_bytes())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def number(value):
    assert math.isfinite(value)
    return f'{value:+.6f}'
def interval(row):return f"[{number(row['lower'])}, {number(row['upper'])}]"

def load_evidence():
    assert sha(REG)==REGISTERED_SHA
    reg,result,review_reg,review=[read(p) for p in (REG,RESULT,REVIEW_REG,REVIEW)]
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(REG)
    assert review['passed'] and review['source_result_sha256']==sha(RESULT)
    assert review['readback_registration_sha256']==sha(REVIEW_REG)
    assert review_reg['source_registration_sha256']==sha(REG)
    assert review_reg['source_result_sha256']==sha(RESULT)
    assert result['accuracy_qualified'] is False and review['accuracy_qualified'] is False
    assert reg['initial_iteration']==80 and reg['final_iteration']==110
    assert reg['test_deals']==review['deals']==result['evaluation']['deals']==16384
    assert reg['test_seed']==result['evaluation']['seed']==9294101
    assert review['batches']==512 and review['maximum_statistical_error']<1e-8
    store=Path(reg['store']);analysis=read(store/'analysis.json');secondary=read(store/'secondary-analysis.json')
    assert sha(store/'analysis.json')==result['evaluation']['analysis_sha256']
    assert sha(store/'secondary-analysis.json')==result['evaluation']['secondary_analysis_sha256']
    assert secondary==review['secondary_analysis'] and review['secondary_review']['passed']
    assert secondary['finite_sample_guarantee'] is False
    assert analysis['deals']==16384 and analysis['family_error_probability']==.05
    assert tuple(r['name'] for r in analysis['contrasts'])==NAMES
    assert tuple(r['name'] for r in secondary['contrasts'])==NAMES
    assert tuple(r['name'] for r in review['contrasts'])==NAMES
    assert tuple(r['name'] for r in review['secondary_review']['tail_diagnostics'])==NAMES
    for row,checked in zip(analysis['contrasts'],review['contrasts']):
        assert row['count']==16384
        assert all(row[k]==checked[k] for k in ('mean','lower','upper'))
    assert tuple(r['arm'] for r in result['training'])==ARMS
    assert tuple(r['arm'] for r in review['training']['arms'])==ARMS
    for recorded,checked in zip(result['training'],review['training']['arms']):
        assert recorded['completed']==110 and checked['updates']==30
        assert abs(recorded['training_seconds']-checked['full_update_seconds'])<1e-8
    assert [p['seed'] for p in review['training']['pairs']]==['A','B']
    return reg,result,review,analysis,secondary

def render(reg,result,review,analysis,secondary):
    primary=analysis['contrasts'];positive=sum(r['lower']>0 for r in primary)
    negative=sum(r['upper']<0 for r in primary)
    lines=['# Matched river continuation: verified findings','',
        f'Primary bounded intervals: {positive} positive, {negative} negative and '
        f'{8-positive-negative} inconclusive fixed contrasts. All eight comparisons appear below.', '',
        'This is an equal-update, single-context comparison of two training methods, each with '
        'two independent training seeds. It does not establish robust preflop accuracy, a '
        'best-response bound, or a production-ready model.', '',
        'Each arm continued from boundary 80 to 110. The final evaluation used 16,384 fresh '
        'common physical deals and the complete played banks 0–109; fitted model 110 was excluded. '
        'The original two-update pilot is retained separately. No test-based stopping or '
        'selection of a favorable seed or seat was used.', '',
        '## Playing-strength comparisons','',
        'Positive values favor replacing the named player with the candidate against the '
        'specified fixed opponent. Units are **bb per entry**, not bb/100 played hands. '
        'The primary intervals have the registered 5% family error allocation. The separate '
        'normal intervals are exploratory approximations: rare tails can invalidate nominal '
        'coverage, and neither analysis accounts for uncertainty across training seeds.', '',
        '| Seed | Player replacement | Mean | Paired SE | Primary bounded interval | Exploratory normal interval |',
        '| --- | --- | ---: | ---: | --- | --- |']
    for i,(row,approx) in enumerate(zip(primary,secondary['contrasts'])):
        seed='A' if i<4 else 'B';label=COMPARISONS[i%4][1]
        lines.append(f"| {seed} | {label} | {number(row['mean'])} | {row['standard_error']:.6f} | {interval(row)} | {interval(approx)} |")
    lines+=['','Point estimates by seed are reported separately; matching signs alone do not '
        'prove improvement. The two comparisons for a seat share data and are not independent replications.','',
        '## Learning cost','',
        'These are the thirty new training-pipeline updates only. The timer includes '
        'pipeline startup, targets, fitting and checkpoint publication. It excludes the '
        'outer checkpoint restore/readback after each update, between-update cleanup, '
        'parent copying, admission, final evaluation and independent review. These sums '
        'are not total elapsed training or research time. Order, caching and other desktop '
        'activity can affect them. GPU wait is the separately recorded training-loop '
        'counter; do not subtract it to infer pure compute time. This is not an equal-time test.','',
        '| Seed / method | Updates | Training pipeline time (min) | Average pipeline seconds/update | Recorded GPU wait (s) |',
        '| --- | ---: | ---: | ---: | ---: |']
    for arm in review['training']['arms']:
        elapsed=arm['full_update_seconds']
        lines.append(f"| {arm['arm']} | {arm['updates']} | {elapsed/60:.2f} | {elapsed/arm['updates']:.2f} | {arm['reported_external_gpu_wait_seconds']:.2f} |")
    for pair in review['training']['pairs']:
        lines+=['',f"Seed {pair['seed']}: candidate/baseline training-pipeline time ratio **{pair['candidate_over_baseline_wall_ratio']:.3f}×**."]
    lines+=['','## Changes reaching preflop decisions','',
        'These describe differences between individual fitted models, not measured gains. '
        'Entry-weighted total variation summarizes the BB action mix; the BTN column is '
        'the largest action-probability difference for its exact first-shove response. '
        'The evaluated average contains all played models, not just the last model.','',
        '| Seed | Model | Evaluated? | BB weighted difference (%) | BTN maximum difference (percentage points) |',
        '| --- | ---: | --- | ---: | ---: |']
    for pair in review['training']['pairs']:
        for model in pair['models']:
            included='yes' if model['included_in_evaluated_bank'] else 'no — unplayed'
            lines.append(f"| {pair['seed']} | {model['generation']} | {included} | {100*model['root_policy_entry_weighted_tv']:.4f} | {100*model['exact_btn_policy_max_difference']:.4f} |")
    lines+=['','## Tail diagnostics and verification','',
        'A large contribution from a few deals makes the exploratory normal intervals '
        'less reassuring. These diagnostics do not certify normal coverage.','',
        '| Seed | Player replacement | Largest squared deviation (%) | Largest ten (%) | Third absolute standardized moment |',
        '| --- | --- | ---: | ---: | ---: |']
    for i,row in enumerate(review['secondary_review']['tail_diagnostics']):
        seed='A' if i<4 else 'B';label=COMPARISONS[i%4][1]
        lines.append(f"| {seed} | {label} | {100*row['largest_centered_square_fraction']:.3f} | {100*row['ten_largest_centered_squares_fraction']:.3f} | {row['third_absolute_standardized_moment']:.3f} |")
    lines+=['',f"Independent readback covered {review['batches']:,} batches and {review['observations']:,} "
        f"observations. Maximum scalar-statistic discrepancy: {review['maximum_statistical_error']:.3g}. "
        'It also checked complete checkpoints, parent continuity, source deals, archive '
        'identities, policy crossings and cashflows. It reuses the qualified native engine; '
        'it is not a second poker engine or independent neural implementation.','',
        f"Stored study allocation: {result['storage']['allocated_file_bytes']/1e9:.3f} GB "
        f"({result['storage']['logical_bytes']/1e9:.3f} GB logical).",'',
        '## Decision still required','',
        'Assess consistency across both seeds and seats alongside computational cost. '
        'A favorable exploratory result can motivate confirmation and an equal-time comparison. '
        'Mixed directions, regressions or excessive cost argue against adopting this treatment. '
        'Additional stack, rake, sizing and multiway contexts remain necessary. No automatic '
        'promotion or deployment follows from this report.','',
        '## Authenticated evidence','']
    for path in (REG,RESULT,REVIEW_REG,REVIEW):
        lines.append(f'- [{path.name}]({path.name}); SHA256 `{sha(path)}`.')
    lines+=['','See [the prospectively frozen plan](RIVER-MATCHED-CONTINUATION-PLAN.md).','']
    return '\n'.join(lines)

def main(write=False):
    missing=[p.name for p in (REG,RESULT,REVIEW_REG,REVIEW) if not p.exists()]
    if missing:
        print(json.dumps(dict(ready=False,pending=missing,partial_outcomes_read=False)));return
    text=render(*load_evidence())
    if write:
        if REPORT.exists():assert REPORT.read_text(encoding='utf-8')==text,'Existing report differs; use a new revision'
        else:
            with REPORT.open('x',encoding='utf-8',newline='\n') as stream:stream.write(text)
    print(json.dumps(dict(ready=True,report=str(REPORT),written=write,accuracy_qualified=False)))

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true')
    main(parser.parse_args().write)
