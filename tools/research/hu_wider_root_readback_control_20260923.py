"""Exercise scalable scalar readback against completed control plus corruptions."""
from pathlib import Path
import time
from unittest.mock import patch
import psutil
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
import wider_root_readback_v1 as reader

PREFIX='wider-root-readback-control-v1'


def main():
    start=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start<180 and psutil.virtual_memory().available>20_000_000_000
    guard()
    oldrp=OUT/'wider-root-evaluation-control-v1-registration.json'
    oldpp=OUT/'wider-root-evaluation-control-v1-result.json'
    oldap=OUT/'wider-root-evaluation-control-v1-independent-review.json'
    reg,outer,audit=[read(p) for p in (oldrp,oldpp,oldap)]
    assert outer['passed'] and audit['passed'] and audit['registration_sha256']==outer['registration_sha256']==sha(oldrp)
    assert audit['result_sha256']==sha(oldpp)
    for p,h in reg['inputs'].items():assert sha(p)==h
    folder=Path(reg['store']);assert sha(folder/'result.json')==outer['result_sha256']
    cp=OUT/'bb-context-candidate.json';rp=OUT/f'{PREFIX}-registration.json';assert not rp.exists()
    paths=[Path(__file__),ROOT/'tools/research/wider_root_readback_v1.py',oldrp,oldpp,oldap,cp,folder/'result.json']
    inputs=dict(reg['inputs']);inputs.update({str(p):sha(p) for p in paths})
    mutations=['interval-mean','stability-disagreement','response-choice','native-payoff','stored-residual','test-rng','class-count']
    save(rp,dict(inputs=inputs,control_store=str(folder),mutations=mutations,maximum_seconds=180,gpu_used=False,
        scope='Read-only reconstruction of completed CPU control and deliberate in-memory corruption rejection; no candidate assessment.'))
    args=(cp,folder,reg['config'],reg['exact'],reg['cache_sha256'],guard)
    result=reader.review(*args)
    original=reader.read;rejected=[]
    for mutation in mutations:
        triggered=[]
        def corrupt(path):
            value=original(path);path=Path(path)
            if mutation=='interval-mean' and path==folder/'result.json':
                value['intervals']['trained-response']['mean']+=1;triggered.append(True)
            elif mutation=='stability-disagreement' and path.name=='training-stability.json':
                value['disagreeing_classes']+=1;triggered.append(True)
            elif mutation=='response-choice' and path.name=='response.json':
                value['selected_actions'][0]=(value['selected_actions'][0]+1)%4;triggered.append(True)
            elif mutation=='native-payoff' and path==folder/'train-000000/native.json':
                value['profiles'][1]['deals'][0]['values'][0]+=.1;triggered.append(True)
            elif mutation=='stored-residual' and path==folder/'test-000000/residuals.json':
                value['values']['trained-response'][0]+=.1;triggered.append(True)
            elif mutation=='test-rng' and path.name=='test-start.json':
                value['initial_rng']={};triggered.append(True)
            elif mutation=='class-count' and path==folder/'result.json':
                value['training_counts'][0]+=1;triggered.append(True)
            return value
        try:
            with patch.object(reader,'read',corrupt):reader.review(*args)
        except AssertionError:
            assert triggered;rejected.append(mutation)
        else:raise AssertionError(f'Failed to reject {mutation}')
    assert rejected==mutations
    for p,h in inputs.items():assert sha(p)==h,p
    guard()
    result.update(registration_sha256=sha(rp),corruption_cases_rejected=rejected,seconds=time.monotonic()-start,
        gpu_used=False,source_evaluation_unchanged=True)
    save(OUT/f'{PREFIX}-result.json',result);print(result)


if __name__=='__main__':main()
