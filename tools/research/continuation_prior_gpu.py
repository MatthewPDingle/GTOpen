"""Cached N09 share matrices in the isolated anchored GPU research interface."""
import sys
from types import SimpleNamespace
import numpy as np
import continuation_recalibrated_priors as prior
import continuation_interface_reuse as runtime
import learned_interface as driver

study=prior.study
OUT=prior.OUT.parent/'recalibrated-priors-gpu-20260916'


def cached_shares(model):
    assert model['production_enabled'] is False and model['chance']=='compatible_pair'
    assert model['position_factors']==[.92,1.08] and model['blend']=='min(SPR/8,1)'
    q=np.array(model['class_base']);assert q.shape==(169,) and np.isfinite(q).all() and (q>0).all()
    _,eq=study.pilot.matrices()
    values=prior.shares(q,eq).astype(np.float32)
    assert np.isfinite(values).all() and (values>=0).all() and (values<=1).all()
    # The GPU's equity lookup is opponent-major; keep that storage convention.
    return values.transpose(0,2,1).reshape(-1)


def source(model,sha):
    values=cached_shares(model)
    def literal(value):
        text=format(float(value),'.9g')
        return text+('' if '.' in text or 'e' in text else '.0')+'f'
    declaration='__device__ const float prior_shares[57122] = {\n'+',\n'.join(
        ','.join(literal(v) for v in values[i:i+16]) for i in range(0,len(values),16))+'\n};\n'
    template=(study.ROOT/'tools/research/learned_interface_kernel.cu').read_text()
    marker=' // Unchanged frozen feature encoder and compatible-mass centering.'
    assert template.count(marker)==1
    prefix=template.split(marker)[0]
    prefix=prefix.replace('d[338],rankmass[26],qraw[338],mass[338],correction[338],desc[10],summary[16]',
        'd[338],rankmass[26]').replace('totals[2],prob,z,center,ez','totals[2],prob,z,ez')
    tail=''' // Candidate uses cached relative shares; no conditional-feature calculation.
 double blend=fmin(sprs[nd]/8.,1.);
 for(int h=threadIdx.x;h<169;h+=blockDim.x){double raw=0.,adjusted=0.;
  for(int j=0;j<169;j++){
   double weight=compatible(h,j)/combos(h)/combos(j)*d[(1-side)*169+j];
   raw+=weight*eq[j*169+h];
   adjusted+=weight*prior_shares[side*169*169+j*169+h];
  }
  double den=legal(h,d+(1-side)*169,rankmass+(1-side)*13);
  double share=raw+blend*(adjusted-raw);
  val[(size_t)slots[nd]*169+h]=(float)(prob/ez*(pots[nd]*share-inv[(size_t)nd*np+p]*den));
 }
}
'''
    return '// Frozen N09 model '+sha+'\n'+declaration+prefix+tail


def export():
    OUT.mkdir(exist_ok=True)
    path=prior.OUT/'candidate.json';freeze=study.read(prior.OUT/'candidate-freeze.json')
    assert study.pilot.sha(path)==freeze['sha256']
    generated=source(study.read(path),freeze['sha256']).encode()
    target=OUT/'interface.cu'
    if target.exists():assert target.read_bytes()==generated
    else:target.write_bytes(generated)
    paths=[path,prior.OUT/'candidate-freeze.json',target,runtime.BIN,
        study.ROOT/'tools/research/continuation_prior_gpu.py',study.ROOT/'tools/research/continuation_recalibrated_priors.py',
        study.ROOT/'tools/research/learned_interface.py',study.ROOT/'tools/research/learned_interface_kernel.cu',
        study.ROOT/'cache/preflop_eq169.bin',study.ROOT/'cache/realization_fit.json',
        study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop',OUT/'README.md']
    manifest=dict(files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
        production_enabled=False,cached_matrix_bytes=57122*4,
        scope='Isolated anchored legal-pair interface; N09 cached float32 shares at SPR 1..20, existing Balanced fallback elsewhere. Larger games retain approximate pair reset.')
    study.freeze(OUT/'manifest.json',manifest)
    return manifest


def oracle():
    export();assert study.read(prior.OUT/'evaluation.json')['accuracy_screen_passed']
    driver.OUT=OUT;driver.BIN=runtime.BIN
    driver.night=SimpleNamespace(OUT=prior.OUT)
    driver.fit=SimpleNamespace(**study.fit.__dict__);driver.fit.predict=prior.predict
    driver.command=lambda args,log:runtime.command(args,log)
    driver.oracle()
    export()  # Recheck all frozen model/source inputs after execution.


def benchmark():
    export();assert study.read(prior.OUT/'evaluation.json')['accuracy_screen_passed']
    assert study.read(OUT/'oracle-check.json')['passed']
    source_game=study.ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop'
    rows=[]
    for repeat,arms in enumerate([['original','candidate'],['candidate','original'],['original','candidate']]):
        for arm in arms:
            folder=OUT/f'repeat-{repeat}'/arm;folder.mkdir(parents=True,exist_ok=True)
            path=folder/'iteration-150.json'
            if not path.exists():runtime.command(['solve',source_game,folder,arm,100,OUT/'interface.cu'],folder/'run.log',optimized=arm=='candidate',warm=50)
            result=study.read(path)
            assert result['start_iteration']==50 and result['iteration']==150 and result['warmup_iterations']==50
            rows.append(dict(repeat=repeat,arm=arm,seconds_per_iteration=result['learning_seconds']/100,
                setup_seconds=result['setup_seconds'],warmup_seconds=result['warmup_seconds'],total_seconds=result['total_seconds'],
                surrogate_gap=sum(result['gaps']),sha256=study.pilot.sha(path)))
        original=runtime.save_parity.compare(runtime.OUT/f'repeat-{repeat}/original/policy.gtop',OUT/f'repeat-{repeat}/original/policy.gtop')
        study.night.dump(OUT/f'repeat-{repeat}/original-state-parity.json',original)
        assert original['all_numeric_entries_equal'],'Ordinary baseline changed'
        if repeat:
            deterministic=runtime.save_parity.compare(OUT/'repeat-0/candidate/policy.gtop',OUT/f'repeat-{repeat}/candidate/policy.gtop')
            study.night.dump(OUT/f'repeat-{repeat}/candidate-repeat-parity.json',deterministic)
            assert deterministic['all_numeric_entries_equal'],'Repeated fixed-work candidate results differ'
        print('N09 runtime repeat',repeat+1,'completed',flush=True)
    medians={arm:float(np.median([r['seconds_per_iteration'] for r in rows if r['arm']==arm])) for arm in ['original','candidate']}
    overhead=medians['candidate']/medians['original']-1
    study.night.dump(OUT/'timing.json',dict(repeats=rows,median_seconds_per_iteration=medians,overhead_vs_original=overhead,
        within_runtime_target=overhead<=.1,production_enabled=False,
        caveat='Fixed-work timing, not convergence speed. Range-dependent anchors and approximate multiway card removal remain; changed-policy validation is still required.'))


if __name__=='__main__':{'export':export,'oracle':oracle,'benchmark':benchmark}[sys.argv[1]]()
