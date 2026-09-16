"""Export a newly qualified shape predictor without modifying frozen studies."""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import continuation_policy_refinement as study
import continuation_interface_reuse as runtime
import learned_interface as oracle_driver


def expression(model):
    assert model['encoder']['kind']=='shape' and model['production_enabled'] is False
    names=model['feature_names'];assert len(names)==104 and len(set(names))==104
    mean=np.array(model['mean']);scale=np.array(model['scale']);weights=np.array(model['coef'])
    assert mean.shape==scale.shape==weights.shape==(104,)
    assert np.isfinite([mean,scale,weights]).all() and (scale>0).all()
    expressions={k:k for k in ['equity','pair','suited','high','low','gap','ace','connected','log_spr']}
    expressions.update(bias='1.0',equity2='(equity*equity)',equity_pair='(equity*pair)',equity_suited='(equity*suited)',
        ip='((double)s)',own_hand_mass='d[x]',opponent_same_class_mass='d[(1-s)*169+h]')
    for side,seat in [('own','s'),('opp','(1-s)')]:
        for i,label in enumerate(['pairs','suited','ranks','aces','connected']):expressions[side+'_'+label]=f'desc[{seat}*5+{i}]'
        for i,label in enumerate(['entropy','effective','maximum','top3','high_pairs','low_pairs','offsuit_broadway','suited_connected']):
            expressions[side+'_'+label]=f'summary[{seat}*8+{i}]'
    def term(name):
        if name in expressions:return expressions[name]
        assert '*' in name,('Unsupported feature',name)
        return '('+'*'.join(term(part) for part in name.split('*'))+')'
    coef=weights/scale;bias=-float(coef@mean)
    return format(bias,'.17g')+'\n'+''.join(f'+({v:.17g})*({term(n)})\n' for n,v in zip(names,coef))


def source(model,sha):
    template=(study.ROOT/'tools/research/learned_interface_kernel.cu').read_text()
    assert template.count('__FEATURE_EXPRESSION__')==1
    return '// Frozen model '+sha+'\n'+template.replace('__FEATURE_EXPRESSION__',expression(model))


def export(model_path,directory):
    model_path=Path(model_path).resolve();directory=Path(directory).resolve()
    assert model_path.name=='candidate.json'
    assert directory!=model_path.parent,'Use a separate integration directory'
    model=study.read(model_path)
    frozen=study.read(model_path.parent/'candidate-freeze.json')
    assert frozen['sha256']==study.pilot.sha(model_path)
    directory.mkdir(parents=True,exist_ok=True)
    generated=source(model,frozen['sha256'])
    path=directory/'interface.cu'
    if path.exists():assert path.read_bytes()==generated.encode(),'Frozen generated source changed'
    else:path.write_bytes(generated.encode())
    paths=[model_path,model_path.parent/'candidate-freeze.json',runtime.BIN,path,
        study.ROOT/'tools/research/continuation_candidate_export.py',study.ROOT/'tools/research/learned_interface.py',
        study.ROOT/'tools/research/learned_interface_kernel.cu',study.ROOT/'cache/preflop_eq169.bin',
        study.ROOT/'cache/realization_fit.json']
    manifest=dict(files={str(p.relative_to(study.ROOT)).replace('\\','/'):study.pilot.sha(p) for p in paths},
        production_enabled=False,scope='New frozen 104-feature predictor; existing anchored legal-pair interface; filtered ordinary work. Two-player physical chance only, approximate heads-up reset in larger games.')
    study.freeze(directory/'manifest.json',manifest)
    return model_path,directory,manifest


def oracle(model_path,directory):
    model_path,directory,manifest=export(model_path,directory)
    assert not runtime.guard.other_research() and not study.night.live_busy()
    # Replace this module's references only; never mutate the shared night
    # module or any old input/output file. The independent arithmetic stays
    # identical while it reads the new candidate from its own directory.
    oracle_driver.OUT=directory
    oracle_driver.BIN=runtime.BIN
    oracle_driver.night=SimpleNamespace(OUT=model_path.parent)
    oracle_driver.command=lambda args,log:runtime.command(args,log)
    oracle_driver.oracle()
    for path,sha in manifest['files'].items():assert study.pilot.sha(study.ROOT/path)==sha
    print('New candidate independent oracle completed; no deployment or runtime qualification follows.')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('mode',choices=['export','oracle'])
    parser.add_argument('model');parser.add_argument('output')
    args=parser.parse_args()
    {'export':export,'oracle':oracle}[args.mode](args.model,args.output)
