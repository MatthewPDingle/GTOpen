"""Descriptive equal-work policy comparison; no training or acceptance changes."""
import json
import math
from pathlib import Path
import continuation_policy_transfer_optimized as transfer

study=transfer.study
OUT=transfer.OUT/'N20'


def run():
    original=study.read(OUT/'original/iteration-500.json')
    candidate=study.read(OUT/'candidate/iteration-500.json')
    rows=study.read(OUT/'strategy-comparison.json')
    assert original['iteration']==candidate['iteration']==rows['iterations']==500
    assert original['config']==candidate['config']
    lookup={tuple(n['path']):n for n in rows['nodes']}
    results=[]
    for n in rows['nodes']:
        assert len(n['actions'])==len(n['original_frequencies'])==len(n['candidate_frequencies'])
        for arm in ['original','candidate']:
            frequencies=n[arm+'_frequencies']
            assert all(math.isfinite(v) and 0<=v<=1 for v in frequencies)
            assert abs(sum(frequencies)-1)<1e-5
        raises=[]
        for depth,action in enumerate(n['path']):
            prefix=lookup[tuple(n['path'][:depth])]
            label=prefix['actions'][action]
            if label!='Fold':
                assert label.startswith('Raise'), 'Unrecognized decision context; preserve full action history'
                raises.append(prefix['actor']+' '+label)
        situation='First in' if not raises else 'After '+', '.join(raises)
        r=dict(actor=n['actor'],path=n['path'],situation=situation)
        for group in ['Fold','Call','Raise','3-bet','All-in']:
            r[group]={arm:100*sum(f for a,f in zip(n['actions'],n[arm+'_frequencies']) if a.startswith(group)) for arm in ['original','candidate']}
        r['KQo']=n['probes'].get('KQo')
        results.append(r)
    gaps={arm:sum(s['gaps']) for arm,s in [('original',original),('candidate',candidate)]}
    assert all(math.isfinite(v) and v>=0 for v in gaps.values())
    result=dict(checked_at=study.night.now(),iteration=500,rows=results,gap_total_bb=gaps,production_enabled=False,
        sources={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in [
            OUT/'original/iteration-500.json',OUT/'candidate/iteration-500.json',OUT/'strategy-comparison.json',Path(__file__).resolve()]},
        caveat='Equal work is not equal solution quality. These descriptive frequencies are not an accuracy comparison, a GTO Wizard comparison or converged ranges. Gaps freeze the range-dependent continuation values.')
    study.night.dump(OUT/'strategy-diagnostic.json',result)
    lines=['# Equal-work strategy diagnostic (N20)','',result['caveat'],'',
        f"At 500 iterations the ordinary path has summed frozen-value gap **{gaps['original']:.6f} bb**, "
        f"versus **{gaps['candidate']:.6f} bb** for the candidate. This raises an unresolved time-to-stability concern; "
        'the roughly 6% per-iteration overhead is not a demonstrated solve-time overhead.', '',
        'The candidate reduces calling in several blind/straddle contexts. Wider calling alone is not an accuracy criterion. '
        'The separately registered N19 trajectory and independent reference values are needed to interpret these changes.', '',
        'All frequencies below are percentages, shown as ordinary -> candidate. UTG is the posted straddle in this configuration; '
        'the first voluntary actor is UTG1. Intervening actions in the response rows are folds.', '',
        '| Actor | Situation | Fold | Call | Raise / 3-bet |', '|---|---|---:|---:|---:|']
    fmt=lambda a,b:f'{a:.2f} -> {b:.2f}'
    for r in results:
        opening=r['situation']=='First in';g='Raise' if opening else '3-bet'
        lines.append(f"| {r['actor']} | {r['situation']} | {fmt(**dict(a=r['Fold']['original'],b=r['Fold']['candidate']))} | "
            f"{fmt(r['Call']['original'],r['Call']['candidate']) if not opening else '-'} | {fmt(r[g]['original'],r[g]['candidate'])} |")
    lines += ['', '## KQo in blind and straddle response nodes','',
        '| Actor | Situation | Ordinary call | Candidate call |','|---|---|---:|---:|']
    for n,r in zip(rows['nodes'],results):
        if r['actor'] not in ['BB','UTG'] or r['situation']=='First in':continue
        indices=[i for i,a in enumerate(n['actions']) if a.startswith('Call')]
        assert len(indices)==1
        i=indices[0]
        lines.append(f"| {r['actor']} | {r['situation']} | {100*r['KQo']['original'][i]:.2f}% | {100*r['KQo']['candidate'][i]:.2f}% |")
    lines += ['', 'The entire strategy comparison, source hashes and all prespecified hand probes remain in the adjacent JSON artifacts.']
    (OUT/'STRATEGY-DIAGNOSTIC.md').write_text('\n'.join(lines)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(dict(iteration=500,gap_total_bb=gaps,nodes=len(results))),flush=True)


if __name__=='__main__':run()
