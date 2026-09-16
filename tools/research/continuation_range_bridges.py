"""Prospective range-diversity references, using training sources only."""
import collections
import hashlib
import numpy as np
import continuation_policy_refinement as study

OUT=study.ROOT/'research/preflop-evolution/continuation/range-bridges-20260916'
PARENTS={
    'train-six-modeled':('train-six-modeled-03','train-six-modeled-00'),
    'train-seven-open':('train-seven-open-03','train-seven-open-00'),
    'train-eight-equal':('train-eight-equal-02','train-eight-equal-00'),
    'train-eight-straddle':('train-eight-straddle-03','train-eight-straddle-00'),
}


def prepare():
    original=study.night.checked_manifest()
    fixtures=study.read(study.night.OUT/'fixtures.json')
    byid={c['id']:c for c in fixtures['cases']}
    cases=[]
    for family,(narrow_id,broad_id) in PARENTS.items():
        narrow=byid[narrow_id];broad=byid[broad_id]
        assert narrow['family']==broad['family']==family
        assert narrow['partition']==broad['partition']=='train'
        ds=[]
        for c in [narrow,broad]:
            w=np.array(c['weights']);ds.append(w/(w*study.pilot.COMBOS).sum(axis=1,keepdims=True))
        for fraction in [.25,.5,.75]:
            mixed=(1-fraction)*ds[0]+fraction*ds[1]
            weights,removed,added=study.night.clean_weights(mixed)
            text=lambda p:','.join(f'{study.pilot.LABELS[h]}:{v:.9f}' for h,v in enumerate(weights[p]) if v>0)
            for spr in [4.,10.,16.]:
                cases.append(dict(id=f'{family}-bridge-{int(fraction*100)}-spr{int(spr)}',family=family,partition='train',
                    positions=['OOP','IP'],weights=weights.tolist(),range_oop=text(0),range_ip=text(1),pot=20.,stack=20.*spr,
                    parents=[narrow_id,broad_id],broad_fraction=fraction,removed_mass_fraction=removed,probe_added_mass_fraction=added,
                    caveat='Synthetic interpolation of training-source range marginals; not a measured player population.'))
    assert len(cases)==36
    excluded={j['board'] for j in original['jobs']}
    for folder in [study.pilot.OUT,study.pilot.AUDIT,study.pilot.AUDIT/'extension',study.OUT/'development',study.OUT/'evaluation']:
        excluded.update(b['board'] for b in study.read(folder/'manifest.json')['boards'])
    groups=collections.defaultdict(list)
    for board,iso in study.read(study.pilot.AUDIT/'fixtures.json')['canonical_flops']:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    training=[];evaluation=[]
    for key,items in sorted(groups.items()):
        items.sort(key=lambda x:hashlib.sha256(('range-bridge-training-20260916'+x[0]).encode()).digest())
        training += [dict(board=b,iso_weight=i,stratum=key,inclusion_probability=4/len(items)) for b,i in items[:4]]
        remaining=items[4:]
        remaining.sort(key=lambda x:hashlib.sha256(('range-bridge-evaluation-20260916'+x[0]).encode()).digest())
        evaluation += [dict(board=b,iso_weight=i,stratum=key,inclusion_probability=10/len(remaining)) for b,i in remaining[:10]]
    assert len(training)==20 and len(evaluation)==50
    assert not {b['board'] for b in training}.intersection(b['board'] for b in evaluation)
    tests=[c for c in fixtures['cases'] if c['partition']=='test']
    assert len(tests)==8
    assert not {c['family'] for c in tests}.intersection(PARENTS)
    paths=[study.night.OUT/'fixtures.json',study.night.OUT/'candidate.json',study.night.OUT/'manifest.json',
        study.ROOT/original['binary_path'],study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json',
        study.OUT/'development/manifest.json',study.OUT/'evaluation/manifest.json',OUT/'README.md']
    inputs={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths}
    for partition,source,boards in [('training',cases,training),('evaluation',tests,evaluation)]:
        jobs=[]
        for b in boards:
            for c in source:
                size={'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
                config=dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(
                    starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=0,rake_cap=0,oop=[size]*3,ip=[size]*3,
                    max_raises=1,add_allin=False,allin_threshold=.85))
                jobs.append(dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=config))
        manifest=study.signed(dict(cases=source,boards=boards,jobs=jobs,partition=partition,inputs=inputs,
            binary_path=original['binary_path'],binary_sha256=original['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
            protocol='README.md; N03 training-range diversity. No evaluation solves before candidate freeze and training CV screen.'))
        study.freeze(OUT/partition/'manifest.json',manifest)
    print('Prepared 720 training references and 400 reserved evaluation references. No GPU work launched.')


if __name__=='__main__':prepare()
