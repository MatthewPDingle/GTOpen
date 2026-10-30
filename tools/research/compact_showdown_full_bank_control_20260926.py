"""CPU-only complete played-bank admission against saved played initial policies.

Runs per completed audited arm. GPU and later-action inference qualification is
separate, and this control is not an accuracy or payoff evaluation.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import sys
import time
import numpy as np
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from compact_showdown_bank_v2 import load_bank
from hu_action_integrated_exact_20260925 import bank_args
from action_integrated_policy_v1 import ActionIntegratedCpuBank64
from showdown_root_policy_v1 import ShowdownRootCpuBank64


def readiness(label):
    reg=read(OUT/'showdown-matched-training-v1-registration.json')
    assert label in [a['name'] for a in reg['arms']]
    case=Path(reg['store'])/label
    paths=[case/'result.json',OUT/f'showdown-training-readback-v2-{label}-0078-result.json']
    missing=[str(p) for p in paths if not p.exists()]
    if missing:return dict(ready=False,missing=missing)
    final,audit=map(read,paths)
    ready=(final.get('completed_iterations')==78 and final.get('final_restore_verified') is True
           and audit.get('passed') is True and audit.get('complete_arm') is True
           and audit.get('completed_updates')==78 and audit.get('arm')==label)
    return dict(ready=ready,missing=[])


def main(label):
    assert readiness(label)['ready'], 'Complete arm and independent readback required'
    started=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started<900
        assert psutil.virtual_memory().available>=20_000_000_000
    guard();prefix=f'compact-showdown-full-bank-{label}-v1'
    rp,dest=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not dest.exists()
    tr=OUT/'showdown-matched-training-v1-registration.json';reg=read(tr)
    arm=next(a for a in reg['arms'] if a['name']==label);case=Path(reg['store'])/label
    paths=[tr,case/'result.json',OUT/f'showdown-training-readback-v2-{label}-0078-result.json',
        OUT/f'showdown-training-readback-v2-{label}-0078-registration.json',Path(__file__).resolve()]
    for name in ['compact_showdown_bank_v2.py','archived_checkpoint_objects_v1.py',
                 'action_integrated_policy_v1.py','showdown_root_policy_v1.py']:
        paths.append(ROOT/'tools/research'/name)
    policies=[case/f'iteration-{i:04d}/current-initial-policy.json' for i in range(1,79)]
    inputs={str(p):sha(p) for p in [*paths,*policies]}
    save(rp,dict(inputs=inputs,arm=label,completed=78,maximum_seconds=900,
        gpu_used=False,scope='All played generations; independent saved initial-policy average only.'))
    try:
        args=bank_args((OUT/'bb-context-candidate.json').read_text())
        models,weights,identity=load_bank(OUT,label,completed=78,
            purpose='implementation-control',bank_args=args,guard=guard)
        final=read(case/'result.json')
        assert identity['checkpoint']==final['final_checkpoint'] and identity['model_references']==final['played_bank']
        assert final['config']==arm['config'] and final['name']==label
        assert not identity['evaluation_qualified'] and identity['excluded_generation']==78
        assert [d['generation'] for d in models]==list(range(78))
        assert np.array_equal(weights,np.tile(np.arange(1,79),(2,1)))
        catalog=json.loads(args['catalog_source'])['native_observations']
        query=dict(context_source=args['context_source'],observations=[r['observation'] for r in catalog])
        assert len(catalog)==265 and all(o['own_history']==[] for o in query['observations'])
        cls=ShowdownRootCpuBank64 if arm['treatment']=='corrected' else ActionIntegratedCpuBank64
        bank=cls(models,completed_iterations=78,weights_by_player=weights,**args)
        actual,reach=bank.average(query,guard=guard)
        expected=np.zeros_like(actual)
        for generation,path in enumerate(policies):
            guard();frozen=read(path)
            assert frozen['used_model']==identity['model_references'][generation]
            for row_index,row in enumerate(catalog):
                h=row['hand_class']
                p=frozen['root'][h] if row['player']==0 else [1-frozen['calls'][h],frozen['calls'][h],0,0]
                expected[row_index]+=(generation+1)*np.asarray(p)/3081
        error=float(np.max(abs(actual-expected)))
        assert error<1e-10 and np.array_equal(reach,np.full(265,3081.))
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),arm=label,bank_identity=identity,
            played_generations=78,excluded_generation=78,observations=265,maximum_policy_error=error,
            own_action_reach_sum=3081,seconds=time.monotonic()-started,gpu_used=False,
            accuracy_qualified=False,later_action_inference_qualified=False,production_modified=False,
            scope='Complete audited CPU bank admission and initial-policy average against saved played policies. Full-bank GPU/later-action and fresh payoff comparison remain pending.')
        save(dest,result);print(json.dumps({k:v for k,v in result.items() if k!='bank_identity'}))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp)))
        raise


if __name__=='__main__':
    if len(sys.argv)==3 and sys.argv[1]=='--check-ready':print(json.dumps(readiness(sys.argv[2])))
    else:
        assert len(sys.argv)==2
        main(sys.argv[1])
