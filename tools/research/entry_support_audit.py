"""Exact private-pair mass removed by entry pruning; no strategic outcomes."""
import hashlib
import json
from pathlib import Path
import numpy as np
import integrated_coverage as c

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    tree_path = ROOT/'research/preflop-evolution/conditional-hu-20260919/subtree.json'
    panels = {'ten': c.OUT/'panel-ab.json', 'report47': OUT/'report-47.json',
              'reserved10': c.OUT/'reserved.json', 'validation95': OUT/'validation-95.json'}
    tree = c.s.read(tree_path)
    weights = np.asarray(tree['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    weights /= weights.max(1)[:,None]
    assert np.all(np.isfinite(weights)) and np.all(weights >= 0)
    # The production research inputs are class based and therefore suit invariant.
    assert all(np.array_equal(weights[:,m],weights) for m in c.MAPS)
    legal = (c.MASKS[:,None] & c.MASKS[None,:]) == 0
    unpruned = weights[0,:,None]*weights[1,None,:]*legal
    thresholds = [0.,1e-7,1e-6,1e-5,1e-4,1e-3]
    selections = [(weights[0,:,None] >= t)&(weights[1,None,:] >= t) for t in thresholds]
    totals = {'full_deck':np.array([unpruned[s].sum() for s in selections])}
    for name,path in panels.items():
        panel = c.s.read(path)
        assert panel['suit_orbits'] is True
        q = np.array([r['weight'] for r in panel['boards']],dtype=float)
        q /= q.sum()
        masses = np.zeros(len(thresholds))
        for row,prob in zip(panel['boards'],q):
            mask = np.uint64(sum(1<<card for card in c.cards(row['board'])))
            alive = (c.MASKS & mask) == 0
            joint = unpruned*alive[:,None]*alive[None,:]
            # Scalar masses are unchanged by any of the 24 suit relabelings.
            masses += prob*np.array([joint[s].sum() for s in selections])
        totals[name] = masses
    rows = []
    for i,t in enumerate(thresholds):
        single = [float(w[(w<t)&(w>0)].sum()/w.sum()) for w in weights]
        removed = {name:float(1-m[i]/m[0]) for name,m in totals.items()}
        assert all(-1e-12 <= value <= 1 for value in removed.values())
        rows.append(dict(cutoff=t, supported_combos=[int(np.count_nonzero((w>=t)&(w>0))) for w in weights],
                         independent_seat_removed_mass=single, compatible_joint_removed_mass=removed))
    for name,m in totals.items():
        assert np.all(np.diff(m) <= 1e-8) and m[0] > 0
    selected = next(r for r in rows if r['cutoff']==1e-5)
    assert selected['supported_combos'] == [322,106]
    # For conditioning on retained support, TV is exactly the removed mass.
    retained = unpruned*selections[3]
    explicit_tv = float(abs(unpruned/unpruned.sum()-retained/retained.sum()).sum()/2)
    assert abs(explicit_tv-selected['compatible_joint_removed_mass']['full_deck']) < 1e-12
    inputs = [Path(__file__),Path(c.__file__),tree_path,*panels.values()]
    result = dict(registered_cutoff_unchanged=1e-5, full_deck_explicit_tv_check=explicit_tv,
                  rows=rows, selected=selected, reserved_strategic_outcomes_accessed=False,
                  interpretation='Exact chance/private-card accounting for the supplied entering ranges. Removed compatible joint mass equals total variation after conditioning on retained support. This does not test whether the original entering ranges are correct, does not bound equilibrium strategy changes, and does not validate the postflop approximation. Full-deck chance is constant over every compatible four-card deal. Panel scalar masses include board removal; suit invariance permits one representative per complete orbit.',
                  inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    output = OUT/'entry-support-audit.json'
    assert not output.exists()
    output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    print(json.dumps(selected,indent=2))


if __name__=='__main__':
    main()
