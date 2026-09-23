"""Compare compact exact matrices with complete physical-pair integration.

Old fixed policies and synthetic policies only; no reads of the active trial,
GPU use, strategic selection or modification to frozen evaluation sources.
"""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import json
import math
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from reboot_research_idle_v1 import idle
from preflop_allin_matrix_v1 import build,AllinMatrix
from finite_btn_response_v1 import integrate
from finite_bb_root_components_v1 import components

PREFIX='preflop-allin-matrix-control-v1'


def main():
    started=time.monotonic()
    def guard():assert idle() and psutil.virtual_memory().available>=20_000_000_000 and time.monotonic()-started<600
    guard();cache=load_complete_cache()
    crp=OUT/'complete-private-allin-cache-v2-registration.json';cr=read(crp)
    source_path=OUT/'bb-context-candidate.json';source=source_path.read_text();population=read(cr['population'])
    erp,epp,eap=[OUT/f'exhaustive-btn-response-v2-{s}.json' for s in ('registration','result','independent-review')]
    er,ep,ea=map(read,(erp,epp,eap))
    assert ea['passed'] and ea['result_sha256']==sha(epp) and ea['registration_sha256']==ep['registration_sha256']==sha(erp)
    inputs={str(p):sha(p) for p in (crp,source_path,Path(cr['population']),erp,epp,eap,Path(__file__),
        ROOT/'tools/research/preflop_allin_matrix_v1.py',ROOT/'tools/research/finite_btn_response_v1.py',
        ROOT/'tools/research/finite_bb_root_components_v1.py',ROOT/'tools/research/later_average_support_v1.py')}
    pairs={}
    for name in ('combined_269','visible_302'):
        p=Path(ep['candidates'][name]['policy_artifact']);policy=read(p)
        assert sha(p)==ep['candidates'][name]['policy_sha256'];inputs[str(p)]=sha(p)
        pairs[name]=(np.asarray(policy['root_probabilities']),np.asarray([float('nan') if x is None else x for x in policy['btn_call_probabilities']]))
    # Deterministic extremes and mixtures check unsupported classes and zero reach.
    pairs['zero-jam']=(np.tile([.5,.25,.25,0.],(169,1)),np.zeros(169))
    pairs['all-jam']=(np.tile([0.,0.,0.,1.],(169,1)),np.ones(169))
    rp=OUT/f'{PREFIX}-registration.json'
    reg=dict(inputs=inputs,maximum_seconds=600,policies=list(pairs),pairings='All 16 cross-pairings',
        scope='Exact endpoint implementation and timing control, not training or strategic improvement.',production_modified=False,gpu_used=False)
    save(rp,reg)
    began=time.perf_counter();document=build(source,population,cache.rows);build_seconds=time.perf_counter()-began
    mp=OUT/f'{PREFIX}-matrix.json';save(mp,document);matrix=AllinMatrix(read(mp),source)
    checks={};max_error=0.;reference_seconds=[];matrix_seconds=[]
    for bname,(root,_) in pairs.items():
        for tname,(_,call) in pairs.items():
            guard();t=time.perf_counter();btn=integrate(source,population,root,call,cache.rows)
            bb=components(source,population,root,call,cache.rows);reference_seconds.append(time.perf_counter()-t)
            t=time.perf_counter();actual=matrix.evaluate(root,call);matrix_seconds.append(time.perf_counter()-t)
            bb_gain=0.
            for c,row in enumerate(bb['classes']):
                f,j=row['fold_value_per_entry'],row['jam_value_per_entry']
                gain=(j-f)*root[c,0] if j>f else (f-j)*root[c,3];bb_gain+=gain
                expected=dict(bb_entries=row['entry_probability'],bb_fold_entries=f,bb_jam_entries=j,bb_class_gains=gain)
                r=btn['classes'][c]
                expected.update(btn_entries=r['entry_probability'],btn_jam_mass=r['jam_probability'],
                    btn_fold_entries=r['fold_value_per_entry'],btn_call_entries=r['call_value_per_entry'],btn_class_gains=r['gain_per_entry'])
                for k,v in expected.items():max_error=max(max_error,abs(float(actual[k][c])-v))
            max_error=max(max_error,abs(actual['bb_gain']-bb_gain),abs(actual['btn_gain']-btn['gains_per_entry']['best']))
            checks[f'{bname}/{tname}']=dict(bb_gain=actual['bb_gain'],btn_gain=actual['btn_gain'])
    assert max_error<1e-9
    # A BB player's own zero shove frequency does not erase counterfactual shove values.
    root,call=pairs['visible_302'];a=matrix.evaluate(root,call);b=matrix.evaluate(pairs['zero-jam'][0],call)
    assert np.array_equal(a['bb_jam_entries'],b['bb_jam_entries'])
    rejected=[]
    for label,fn in [('wrong-context',lambda:AllinMatrix(document,source+' ')),
                     ('bad-root',lambda:matrix.evaluate(root*2,call)),
                     ('unsupported-nan-on-supported-hand',lambda:matrix.evaluate(root,np.full(169,float('nan'))))]:
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError(label)
    for p,h in inputs.items():assert sha(p)==h,p
    guard();result=dict(passed=True,registration_sha256=sha(rp),matrix_artifact=str(mp),matrix_sha256=sha(mp),
        maximum_class_value_error_bb=max_error,cross_pairings=checks,build_seconds=build_seconds,
        matrix_bytes=mp.stat().st_size,reference_pairing_seconds=reference_seconds,matrix_pairing_seconds=matrix_seconds,
        timing_scope='Only endpoint arithmetic; excludes cache construction, policy inference and training. Single observations, not a full performance benchmark.',
        rejections=rejected,seconds=time.monotonic()-started,production_modified=False,gpu_used=False,accuracy_qualified=False)
    save(OUT/f'{PREFIX}-result.json',result);print(json.dumps({k:v for k,v in result.items() if k!='cross_pairings'}))


if __name__=='__main__':main()
