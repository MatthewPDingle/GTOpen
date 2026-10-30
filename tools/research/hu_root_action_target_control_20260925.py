"""Control a separately typed integrated-root target adapter on saved fixtures."""
import copy
import json
import math
from pathlib import Path
import time
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from action_integrated_root_targets_v1 import derive,digest,METHOD


def main():
    start=time.monotonic()
    prefix='root-action-target-control-v1'
    result_path=OUT/f'{prefix}-result.json';assert not result_path.exists()
    paths=[OUT/f'root-action-integration-v1-{s}.json' for s in ('registration','result','independent-review')]
    reg,completed,review=map(read,paths)
    assert completed['passed'] and review['passed']
    assert completed['registration_sha256']==review['registration_sha256']==sha(paths[0])
    assert review['result_sha256']==sha(paths[1])
    inputs={str(p):sha(p) for p in [*paths,Path(__file__),ROOT/'tools/research/action_integrated_root_targets_v1.py']}
    for p,h in {**reg['inputs'],**completed['artifacts']}.items():assert sha(p)==h,p
    rp=OUT/f'{prefix}-registration.json';assert not rp.exists()
    save(rp,dict(inputs=inputs,scope='No fitting; derive integrated root targets on all eight admitted fixtures, preserve exact jam values and sampled inputs, reject mismatched transports and malformed outputs.'))
    artifacts={};maxerror=0.;rejected=[];count=0
    for fi,fixture in enumerate(reg['fixtures']):
        assert time.monotonic()-start<600
        source=Path(fixture['source']);folder=Path(reg['store'])/f'fixture-{fi:02d}'
        args=[read(source/'queries.json'),read(source/'policies.json'),read(source/'derived-targets.json'),
              read(folder/'profiles.json'),read(folder/'full-values.json')]
        before=list(map(digest,args));result=derive(*args)
        assert before==list(map(digest,args)) and result['method']==METHOD
        assert result['identity']['root_estimator']==METHOD
        assert len(result['bb_root_corrections'])==64
        for i,row in enumerate(result['bb_root_corrections']):
            old=args[2]['bb_root_corrections'][i];p=args[1]['policies'][old['query']]['probabilities']
            expected=[args[4]['profiles'][a+1]['deals'][i]['values'][0] for a in range(4)]
            expected[3]=old['exact_conditional_jam_value']
            assert expected==row['action_values']
            error=abs(sum(p[a]*row['advantages'][a] for a in range(4)))
            assert error<1e-9;maxerror=max(maxerror,error)
            assert row['hand_class']==old['hand_class']
            count+=1
        ap=OUT/f'{prefix}-fixture-{fi:02d}.json';save(ap,result);artifacts[str(ap)]=sha(ap)
        if fi==0:
            def reject(name, mutate):
                changed=copy.deepcopy(args);mutate(changed)
                try:derive(*changed)
                except (ValueError,KeyError,IndexError,TypeError):rejected.append(name)
                else:raise AssertionError('Accepted invalid '+name)
            reject('old query format',lambda a:a[0].update(format=2))
            reject('different physical batch',lambda a:a[3].update(batch_source='{}'))
            reject('different context',lambda a:a[3].update(context_source='{}'))
            reject('stale policy digest',lambda a:a[2].update(policies_sha256='0'*64))
            reject('failed cashflow check',lambda a:a[4].update(maximum_forward_cashflow_error=.1))
            reject('missing action profile',lambda a:a[3]['profiles'].pop())
            reject('missing native deal',lambda a:a[4]['profiles'][1]['deals'].pop())
            reject('changed native deal order',lambda a:a[4]['profiles'][1]['deals'][0].update(deal_index=3))
            reject('changed baseline value',lambda a:a[4]['profiles'][0]['deals'][0]['values'].__setitem__(0,999.))
            reject('nonfinite exact jam',lambda a:a[2]['bb_root_corrections'][0].update(exact_conditional_jam_value=float('nan')))
            later=next(i for i,o in enumerate(args[0]['observations']) if o['phase']!=0)
            reject('changed later policy',lambda a:a[3]['profiles'][1]['policies'][later].update(probabilities=[1.,0.,0.,0.]))
    for p,h in inputs.items():assert sha(p)==h,p
    output=dict(passed=True,registration_sha256=sha(rp),artifacts=artifacts,
        root_targets=count,rejected_inputs=rejected,maximum_centering_error=maxerror,
        seconds=time.monotonic()-start,production_modified=False,accuracy_qualified=False,
        scope='Adapter correctness and separation only. This has not trained or qualified an integrated-root model.')
    save(result_path,output);print({k:v for k,v in output.items() if k!='artifacts'})


if __name__=='__main__':main()
