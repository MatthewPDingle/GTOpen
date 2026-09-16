"""Fixed N06 candidate repeat on N03 training data, with two unchanged gates."""
import continuation_nonlinear_residual as network
import continuation_bridge_run as bridge
import numpy as np

study=network.study
OUT=study.ROOT/'research/preflop-evolution/continuation/nonlinear-expanded-20260916'


def screen():
    original=study.fit.load_cases('train')+study.contexts('development')
    extra=bridge.contexts('training')
    cases=original+extra
    assert len(original)==26 and len(cases)==62
    assert all(c['case']['partition']=='train' for c in cases)
    families=sorted({c['case']['family'] for c in cases});assert len(families)==4
    sources=['tools/research/continuation_nonlinear_expanded.py','tools/research/continuation_nonlinear_residual.py',
        'research/preflop-evolution/continuation/nonlinear-expanded-20260916/README.md',
        str((network.OUT/'training-screen.json').relative_to(study.ROOT)),
        str((bridge.OUT/'training/manifest.json').relative_to(study.ROOT))]
    study.freeze(OUT/'implementation-freeze.json',dict(inputs={p:study.pilot.sha(study.ROOT/p) for p in sources},production_enabled=False))
    prior=study.read(network.OUT/'training-screen.json')['scores'][0]
    assert sorted(r['case'] for r in prior['cases'])==sorted(c['case']['id'] for c in original)
    scores=[]
    for width,penalty in [(0,0),(8,.01),(8,.1),(16,.01),(16,.1)]:
        rows=[]
        for family in families:
            training=[c for c in cases if c['case']['family']!=family]
            model=network.fit(training,width,penalty) if width else dict(base=study.fit.fit(training,'shape',.1),networks=[])
            for c in original:
                if c['case']['family']==family:
                    rows.append(dict(case=c['case']['id'],family=family,clipped_mass_fraction=network.inputs(c,model['base'])[1],
                        **study.pilot.metrics(c,network.predict(c,model))))
            print('Finished',width,penalty,family,flush=True)
        means={f:float(np.mean([r['candidate'] for r in rows if r['family']==f])) for f in families}
        scores.append(dict(width=width,output_penalty=penalty,cases=rows,family_means=means,mean=float(np.mean(list(means.values())))))
        study.night.dump(OUT/'progress.json',dict(completed_choices=len(scores),scores=scores,production_enabled=False))
    controls={'same_expanded_data':scores[0],'prior_26_case_data':prior}
    for score in scores:
        score['comparisons']={key:dict(improvement=1-score['mean']/control['mean'],
            worst_family_ratio=max(score['family_means'][f]/control['family_means'][f] for f in families))
            for key,control in controls.items()}
        score['eligible']=all(r['improvement']>=.05 and r['worst_family_ratio']<=1.05 for r in score['comparisons'].values())
    eligible=[r for r in scores[1:] if r['eligible']]
    winner=min(eligible,key=lambda r:r['mean']) if eligible else None
    study.freeze(OUT/'training-screen.json',dict(training_cases=62,validation_cases=26,scores=scores,selected=winner,
        production_enabled=False,note='Training-family selection only; both controls must pass.'))
    if winner:
        model=network.fit(cases,winner['width'],winner['output_penalty'])
        model.update(training_case_ids=[c['case']['id'] for c in cases],training_families=families,
            selection_sha256=study.pilot.sha(OUT/'training-screen.json'))
        study.freeze(OUT/'candidate.json',model)
        study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),frozen_at=study.night.now(),
            prospective_references_generated=0))
    print('Selected:',None if winner is None else [winner['width'],winner['output_penalty']],flush=True)


if __name__=='__main__':screen()
