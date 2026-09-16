"""Read-only hand-level convergence diagnostic for N03 training references."""
import numpy as np
import continuation_bridge_run as bridge


def audit():
    manifest=bridge.checked('training');rows=[];hands=[];thresholds=[1.,5.,10.]
    for job in manifest['jobs']:
        path=bridge.OUT/'training/jobs'/f"{job['id']}.json"
        if not path.exists():continue
        reference=bridge.study.read(path);bridge.validate_reference(reference,job,manifest)
        pot=job['config']['tree']['starting_pot'];gap=0.;tails={t:0. for t in thresholds}
        for side,holdings in enumerate(reference['hands']):
            for holding in holdings:
                mass=holding['pair_mass']/reference['pair_mass']
                gain=max(0,holding['br_ev_bb']-holding['ev_bb'])/pot*100
                gap+=mass*gain/2
                for threshold in thresholds:tails[threshold]+=mass*(gain>threshold)/2
                hands.append(dict(job=job['id'],side=side,hand=holding['hand'],br_gain_pct_pot=gain,
                    own_range_mass_fraction=mass))
        rows.append(dict(job=job['id'],reconstructed_gap_pct=gap,reported_gap_pct=reference['gap_pct'],tail_mass=tails))
    assert rows
    result=dict(checked_at=bridge.study.night.now(),manifest_id=manifest['id'],references=len(rows),planned=len(manifest['jobs']),
        complete=len(rows)==len(manifest['jobs']),
        max_gap_reconstruction_difference=max(abs(r['reconstructed_gap_pct']-r['reported_gap_pct']) for r in rows),
        mean_tail_mass_by_threshold={str(t):float(np.mean([r['tail_mass'][t] for r in rows])) for t in thresholds},
        worst_hand_values=sorted(hands,key=lambda h:h['br_gain_pct_pot'],reverse=True)[:10],production_enabled=False,
        caveat='Training references only. Tail fractions weight each completed reference and player equally; not an all-flop population estimate. Best-response gain diagnoses solve quality, not model prediction error or a rigorous per-hand value-error bound.')
    bridge.study.night.dump(bridge.OUT/'partial-hand-quality.json',result)
    print('Audited',len(rows),'references; mass above 1% pot BR gain:',result['mean_tail_mass_by_threshold']['1.0'],flush=True)
    return result


if __name__=='__main__':audit()
