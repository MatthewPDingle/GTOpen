"""Does the AA call value survive material inclusion in the calling range?"""
import copy
import hashlib
import json
import sys
import wizard_continuation_study as s
import wizard_continuation_precision as p
import wizard_continuation_floor as floor
from wizard_fourbet_continuation import prices

PARENT=s.OUT
OUT=PARENT/'aa-range-sensitivity'


def prepare():
    parent=s.checked();f=s.read(PARENT/'fixtures.json');case,=f['cases']
    labels=[h['hand'] for h in case['balanced']['hands'][0]];aa=labels.index('AA')
    counts=[6 if len(h)==2 else 4 if h.endswith('s') else 12 for h in labels]
    original_mass=sum(w*c for w,c in zip(case['weights'][0],counts))
    OUT.mkdir(exist_ok=True)
    for weight in (.25,1.):
        dest=OUT/('quarter' if weight==.25 else 'full');dest.mkdir(exist_ok=True)
        assert not (dest/'manifest.json').exists(),'Preserve registered experiment'
        modified=copy.deepcopy(case);modified['weights'][0][aa]=weight
        modified['range_oop']=','.join(f'{h}:{w:.9f}' for h,w in zip(labels,modified['weights'][0]) if w>0)
        modified['balanced']=prices(modified['weights'],case['pot'],case['stack'],labels)
        modified['aa_weight']=weight
        modified['aa_combo_mass_fraction']=6*weight/(original_mass+6*(weight-case['weights'][0][aa]))
        mf=copy.deepcopy(f);mf['cases']=[modified];s.write(dest/'fixtures.json',mf)
        jobs=copy.deepcopy(parent['jobs'])
        for j in jobs:j['config']['range_oop']=modified['range_oop']
        inputs=[p.BINARY,PARENT/'manifest.json',dest/'fixtures.json',OUT/'PROTOCOL.md',
            s.ROOT/'tools/research/wizard_aa_range_sensitivity.py',s.ROOT/'tools/research/wizard_continuation_floor.py',
            s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'cache/realization_fit.json']
        m=dict(parent_manifest_id=parent['id'],boards=parent['boards'],jobs=jobs,target_gap_pct=.05,max_iterations=5000,
            probe_br_gain_limit_bb=.05,aa_weight=weight,aa_combo_mass_fraction=modified['aa_combo_mass_fraction'],
            added_mass_fraction=6*(weight-case['weights'][0][aa])/original_mass,
            inputs={x.relative_to(s.ROOT).as_posix():s.sha(x) for x in inputs})
        m['id']=hashlib.sha256(json.dumps(m,sort_keys=True).encode()).hexdigest();s.write(dest/'manifest.json',m)
        print(dest.name,modified['aa_combo_mass_fraction'])


def run():
    for name in ('quarter','full'):
        floor.OUT=OUT/name
        # Existing runner enforces the live-app idle guard, process lock,
        # immutable inputs and strict global plus all-probe convergence gates.
        floor.run()
        result=s.read(floor.OUT/'summary.json')
        result['note']='Paired direct estimates with only AA made materially more frequent in the OOP calling range. Postflop policies adapt. Preflop opponent policy and all other hand weights fixed. Not an equilibrium preflop strategy.'
        result['aa_weight']=floor.checked()['aa_weight']
        result['aa_combo_mass_fraction']=floor.checked()['aa_combo_mass_fraction']
        for row in result['results']:row['material_aa_range_bb']=row.pop('higher_floor_bb')
        s.write(floor.OUT/'summary.json',result)
    s.write(OUT/'status.json',dict(stage='ready_for_review',completed=160))


if __name__=='__main__':
    try:{'prepare':prepare,'run':run}[sys.argv[1]]()
    except Exception as error:
        if sys.argv[1]=='run':s.write(OUT/'status.json',dict(stage='failed',error=str(error)))
        raise
