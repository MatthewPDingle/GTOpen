"""Descriptive all-class report after independently verified root-action replay.

The sample is reused. Sample-maximizing root actions are diagnostics, never a
qualified best response, exploitability bound or a fresh statistical discovery.
"""
import csv
import hashlib
import io
import json
import math
from pathlib import Path

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='board-root-action-replay-v1'
ACTIONS=('fold','call','raise','jam')
RANKS='23456789TJQKA'


def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def label(c):
    row,col=divmod(c,13)
    return RANKS[max(row,col)]+RANKS[min(row,col)]+('' if row == col else 's' if row > col else 'o')


def paired(row,a,b):
    if a == b:return 0.,0.
    for pair in row['paired_BB_differences']:
        if (pair['action_a'],pair['action_b']) == (ACTIONS[a],ACTIONS[b]):
            return pair['mean_a_minus_b'],pair['standard_error']
        if (pair['action_a'],pair['action_b']) == (ACTIONS[b],ACTIONS[a]):
            return -pair['mean_a_minus_b'],pair['standard_error']
    raise ValueError('Missing paired difference')


def main():
    registration=OUT/(PREFIX+'-registration.json');replay_path=OUT/(PREFIX+'-replay.json')
    audit_path=OUT/'board-root-action-replay-readback-v1-result.json'
    audit_registration=OUT/'board-root-action-replay-readback-v1-registration.json'
    reg,replay,audit=read(registration),read(replay_path),read(audit_path)
    assert replay['replay_finished'] and audit['passed'] and audit['complete']
    assert replay['registration_sha256'] == audit['source_registration_sha256'] == sha(registration)
    assert audit['source_replay_sha256'] == sha(replay_path)
    assert audit['readback_registration_sha256'] == sha(audit_registration)
    for p,h in read(audit_registration)['inputs'].items():assert sha(p) == h,p
    summary_path=Path(reg['store'])/'summary.json';roots_path=Path(reg['root_stability_path'])
    assert sha(summary_path) == replay['summary_sha256'] and sha(roots_path) == reg['inputs'][str(roots_path)]
    summary,roots=read(summary_path),read(roots_path)
    assert summary['deals'] == audit['deals'] == 65536 and len(summary['profiles']) == 8
    weights=roots['entry_masses'];assert len(weights) == 169 and abs(sum(weights)-1) < 1e-10
    counts=[r['evaluation_count'] for r in summary['profiles'][0]['classes']]
    assert sum(counts) == 65536 and counts == audit['class_evaluation_counts']
    rows=[];profiles=[]
    for p,profile in enumerate(summary['profiles']):
        assert len(profile['classes']) == 169
        observed_gain=0.;mixed=0.;pure_means=[0.]*4
        for c,row in enumerate(profile['classes']):
            n=row['evaluation_count'];assert n == counts[c] and row['native_class_index'] == c
            assert n > 0,'Missing class: report must explicitly handle it instead of dropping it'
            prob=row['root_probabilities'];q=[v[0] for v in row['action_means']]
            se=[v[0] for v in row['action_standard_errors']]
            selected=max(range(4),key=lambda a:q[a])
            current=math.fsum(x*y for x,y in zip(prob,q))
            assert abs(current-row['original_mixture_means'][0]) < 1e-10
            gain=max(q)-current;assert gain >= -1e-10
            observed_gain+=n/65536*gain;mixed+=n/65536*current
            for a in range(4):pure_means[a]+=n/65536*q[a]
            rows.append(dict(profile=profile['name'],native_class_index=c,hand=label(c),evaluation_count=n,
                entry_mass=weights[c],root_probabilities=prob,BB_action_means=q,BB_action_standard_errors=se,
                paired_BB_differences=row['paired_BB_differences'],original_BB_mean=current,
                sample_maximizing_action=ACTIONS[selected],sample_selected_root_gain=gain))
        assert abs(mixed-profile['overall']['original_mixture_means'][0]) < 1e-10
        assert max(abs(pure_means[a]-profile['overall']['action_means'][a][0]) for a in range(4)) < 1e-10
        profiles.append(dict(name=profile['name'],mixed_BB_mean=mixed,pure_BB_means=pure_means,
            sample_selected_root_gain=observed_gain))
    first,second=summary['profiles'][3]['classes'],summary['profiles'][7]['classes']
    disagreements=[];tv=0.;categories={}
    for c,(one,two) in enumerate(zip(first,second)):
        pa,pb=one['root_probabilities'],two['root_probabilities']
        tv+=weights[c]*sum(abs(a-b) for a,b in zip(pa,pb))/2
        a=max(range(4),key=lambda k:pa[k]);b=max(range(4),key=lambda k:pb[k])
        if a == b:continue
        d1,e1=paired(one,a,b);d2,e2=paired(two,a,b)
        category=('each_favors_own' if d1 > 0 and d2 < 0 else
            'each_favors_other' if d1 < 0 and d2 > 0 else
            'both_favor_first' if d1 > 0 and d2 > 0 else
            'both_favor_second' if d1 < 0 and d2 < 0 else 'exact_tie_present')
        categories.setdefault(category,dict(classes=0,entry_mass=0.))
        categories[category]['classes']+=1;categories[category]['entry_mass']+=weights[c]
        disagreements.append(dict(hand=label(c),native_class_index=c,evaluation_count=counts[c],entry_mass=weights[c],
            first_dominant=ACTIONS[a],replication_dominant=ACTIONS[b],
            first_value_difference=d1,first_paired_SE=e1,replication_value_difference=d2,replication_paired_SE=e2,
            category=category))
    assert abs(tv-roots['comparisons']['candidate_cross_seed']['entry_weighted_total_variation']) < 1e-12
    evidence=[registration,replay_path,audit_path,audit_registration,summary_path,roots_path,Path(__file__)]
    report=dict(format=1,deals=65536,classes=169,profiles=profiles,all_hand_rows=rows,
        candidate_cross_seed_TV=tv,dominant_action_disagreements=disagreements,descriptive_sign_categories=categories,
        evaluation_count_range=[min(counts),max(counts)],exploratory=True,accuracy_qualified=False,
        scope='Root actions varied, complete averaged later behavior fixed, same existing evaluation sample.',
        caution='Sample maxima are upward-selected diagnostics. Paired SEs are descriptive; no multiplicity-adjusted discoveries. Different runs have different opponents and later behavior.',
        inputs={str(p):sha(p) for p in evidence})
    raw=json.dumps(report,indent=2,allow_nan=False)+'\n'
    table=io.StringIO(newline='');writer=csv.writer(table)
    writer.writerow(['profile','hand','evaluation_count','entry_mass',*[f'{a}_probability' for a in ACTIONS],
        *[f'{a}_BB_mean' for a in ACTIONS],*[f'{a}_BB_SE' for a in ACTIONS],
        'original_BB_mean','sample_maximizing_action','sample_selected_root_gain'])
    for r in rows:writer.writerow([r['profile'],r['hand'],r['evaluation_count'],r['entry_mass'],
        *r['root_probabilities'],*r['BB_action_means'],*r['BB_action_standard_errors'],
        r['original_BB_mean'],r['sample_maximizing_action'],r['sample_selected_root_gain']])
    lines=['# Root-action values under the retained complete policies','',
        'All 65,536 previously evaluated deals passed replay and independent readback. This is an exploratory diagnostic of the restricted 200bb BB-versus-BTN-2bb-open spot, with 0.5bb dead money and 5% rake capped at 2bb.', '',
        'These results vary only the first BB action; later play remains fixed. They are not a full best response or a demonstration of accurate ranges. The eight original registered payoff comparisons remain inconclusive.', '',
        f'All 169 classes and eight crossed profiles are included. Evaluation counts range from {min(counts)} to {max(counts)} deals per class. Counts measure evaluation coverage, not the unavailable per-hand training support.', '',
        '## Sample-selected root changes','',
        'The following diagnostic chooses the highest observed BB value separately for each class on this same sample. The resulting gains are upward-selected and have not been independently validated; they must not be called exploitability or measured improvement. Units are bb per entry to this restricted spot, not bb/100.', '',
        '| Complete profile | Original BB value | Sample-selected root gain |','| --- | ---: | ---: |']
    for p in profiles:lines.append(f"| {p['name']} | {p['mixed_BB_mean']:.4f} | {p['sample_selected_root_gain']:.4f} |")
    lines+=['','## Why the candidate runs disagree','',
        f'The candidate root ranges differ in their dominant action for {len(disagreements)} classes; entry-weighted total variation is {tv*100:.2f}%. For those classes, compare the two dominant actions under each run\'s own complete policies:', '',
        '| Signs of the observed value difference | Classes | Incoming mass |','| --- | ---: | ---: |']
    labels=dict(each_favors_own='Each run values its own dominant action higher',each_favors_other='Each run values the other action higher',
        both_favor_first='Both runs value the first run\'s action higher',both_favor_second='Both runs value the replication\'s action higher',exact_tie_present='At least one exact tie')
    for name,data in categories.items():lines.append(f"| {labels[name]} | {data['classes']} | {data['entry_mass']*100:.2f}% |")
    lines+=['','These categories use point-estimate signs, without a significance claim. Both opponent behavior and the BB\'s later behavior differ between runs, so this comparison cannot isolate which continuation causes a difference. All paired differences and descriptive standard errors are retained in the JSON report.', '',
        '## Illustrative hands','',
        'These examples were chosen from earlier range concerns. The full table includes all hands, including unfavorable cases. Values below follow fold / call / raise / jam; probabilities show the already evaluated average policy.', '',
        '| Hand | Deals | First policy (%) | First BB values | Replication policy (%) | Replication BB values |',
        '| --- | ---: | --- | --- | --- | --- |']
    bylabel={label(c):c for c in range(169)}
    for hand in ('AA','KK','QQ','JJ','TT','99','88','AQs','AJs','ATs','KQs','KQo','98s','76s'):
        c=bylabel[hand];one,two=first[c],second[c]
        policy=lambda r:' / '.join(f'{x*100:.1f}' for x in r['root_probabilities'])
        values=lambda r:' / '.join(f'{x[0]:.2f}' for x in r['action_means'])
        lines.append(f'| {hand} | {counts[c]} | {policy(one)} | {values(one)} | {policy(two)} | {values(two)} |')
    lines+=['','## Evidence and limits','',
        '- [All hand classes and paired differences](board-root-action-all-classes-v1.json).',
        '- [Flat all-hand table](board-root-action-all-classes-v1.csv).',
        '- [Independent readback](board-root-action-replay-readback-v1-result.json).',
        '- No new deals, new training, production deployment or fresh accuracy qualification.',
        '- Preflop all-ins use the existing conditional equity calculation; ordinary postflop outcomes use sampled boards.',
        '- The verifier shares the original poker evaluator. It independently checks retained inputs and arithmetic, not poker-engine correctness.',
        '- Next-step selection requires reviewing this full result; any proposed gain needs fresh, specified validation.','']
    outputs={'board-root-action-all-classes-v1.json':raw,'board-root-action-all-classes-v1.csv':table.getvalue(),
        'BOARD-ROOT-ACTION-VALUE-FINDINGS.md':'\n'.join(lines)}
    for name in outputs:assert not (OUT/name).exists(),name
    for name,value in outputs.items():
        with (OUT/name).open('x',encoding='utf-8',newline='') as f:f.write(value)
    print(json.dumps(dict(profiles=profiles,categories=categories,dominant_disagreements=len(disagreements),
        files={n:sha(OUT/n) for n in outputs})))


if __name__ == '__main__':main()
