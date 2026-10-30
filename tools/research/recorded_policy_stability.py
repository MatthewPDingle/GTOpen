"""Describe saved checkpoint policy changes; never extrapolate beyond them."""
import hashlib
import json
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'
SOURCES={'10 flops':ROOT/'research/preflop-evolution/integrated-coverage-20260919/panel-ab-result.json',
         '47 flops':OUT/'report47-full-result.json'}


def analyze(data):
    records=data['records']
    reference=records[-1]['evaluation']['hands']
    labels=[r['hand'] for r in reference]
    mass=np.asarray([r['root_mass'] for r in reference])
    assert abs(mass.sum()-1)<1e-7
    checkpoint=[]
    for r in records:
        e=r['evaluation']
        assert labels==[h['hand'] for h in e['hands']]
        assert max(abs(mass-np.asarray([h['root_mass'] for h in e['hands']])))<1e-10
        policy=np.asarray([h['strategy'] for h in e['hands']])
        assert np.isfinite(policy).all() and np.all((policy>=0)&(policy<=1))
        assert max(abs(policy[mass>0].sum(1)-1))<1e-10
        assert max(abs(mass@policy-e['root_frequencies']))<1e-8
        checkpoint.append(dict(iteration=r['iteration'],frequencies=e['root_frequencies'],gap_bb=e['gap_total']))
    intervals=[]
    for a,b in zip(records,records[1:]):
        p=np.asarray([h['strategy'] for h in a['evaluation']['hands']])
        q=np.asarray([h['strategy'] for h in b['evaluation']['hands']])
        tv=abs(q-p).sum(1)/2
        weighted=float(mass@tv)
        aggregate=float(abs(mass@q-mass@p).sum()/2)
        assert weighted>=aggregate-1e-10
        rows=[dict(hand=hand,root_mass=float(w),tv=float(v),weighted_tv=float(w*v))
              for hand,w,v in zip(labels,mass,tv)]
        intervals.append(dict(start=a['iteration'],end=b['iteration'],weighted_hand_tv=weighted,
                              aggregate_frequency_tv=aggregate,hands=rows))
    return dict(checkpoints=checkpoint,intervals=intervals)


def main():
    results={name:analyze(json.loads(p.read_text())) for name,p in SOURCES.items()}
    paths=[*SOURCES.values(),Path(__file__)]
    output=dict(sources=results,
                interpretation='Changes between recorded root hand-class policies under each source\'s fixed entering distribution. TV is the fraction of action probability mass moved. It is not an EV error, confidence interval, independent validation or proof of stability after the final checkpoint. No extra solve was run.',
                inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
    with (OUT/'recorded-policy-stability.json').open('x') as f:
        json.dump(output,f,indent=2,allow_nan=False)
    lines=['# Recorded training-panel policy stability','',output['interpretation'],'',
           '| Source | Checkpoint interval | Weighted hand-policy TV | Aggregate frequency TV |',
           '|---|---|---:|---:|']
    for name,r in results.items():
        for row in r['intervals']:
            lines.append(f'| {name} | {row["start"]} to {row["end"]} | {row["weighted_hand_tv"]*100:.4f}% | {row["aggregate_frequency_tv"]*100:.4f}% |')
    for name,r in results.items():
        lines+=['',f'## {name}: recorded action frequencies','',
                '| Iteration | Fold | Call | 4-bet | Jam | Full gap (bb) |','|---:|---:|---:|---:|---:|---:|']
        for row in r['checkpoints']:
            lines.append(f'| {row["iteration"]} | '+' | '.join(f'{v*100:.4f}%' for v in row['frequencies'])+f' | {row["gap_bb"]:.6f} |')
        late=r['intervals'][-1]
        lines+=['','Largest weighted hand changes in the final recorded interval:','',
                '| Hand | Entering mass | Hand-policy TV | Weighted contribution |','|---|---:|---:|---:|']
        for h in sorted(late['hands'],key=lambda h:h['weighted_tv'],reverse=True)[:10]:
            lines.append(f'| {h["hand"]} | {h["root_mass"]*100:.3f}% | {h["tv"]*100:.3f}% | {h["weighted_tv"]*100:.4f}% |')
    lines+=['','The 2,000-step results have no later checkpoint. Their small within-panel deviation '
            'gaps therefore do not demonstrate that every mixed frequency has stopped moving. '
            'These observations do not change the frozen transfer sources or justify extending a '
            'selected source after observing its test outcomes. Between-panel sensitivity and '
            'same-panel reconstruction remain separate questions.']
    (OUT/'recorded-policy-stability.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({name:{k:v for k,v in r['intervals'][-1].items() if k!='hands'} for name,r in results.items()}))


if __name__=='__main__':
    main()
