"""Recompute saved fitter-control numeric differences without new model fitting."""
import hashlib
import json
from pathlib import Path
import time
import numpy as np

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
STORE=Path('S:/GTOpen-research/stack-context-fitter-control-v1')
PREFIX='stack-context-fitter-control-v1'


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def write(path,value):
    with path.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,sort_keys=True,allow_nan=False,indent=2);stream.write('\n')


def main():
    target=OUT/(PREFIX+'-readback.json');attempt=OUT/(PREFIX+'-readback-attempt.json')
    assert not target.exists() and not attempt.exists()
    regpath=OUT/(PREFIX+'-registration.json');resultpath=OUT/(PREFIX+'-result.json')
    reg=json.loads(regpath.read_bytes());result=json.loads(resultpath.read_bytes())
    write(attempt,dict(source_sha256=sha(__file__),result_sha256=sha(resultpath),started_unix=time.time()))
    started=time.monotonic()
    try:
        assert result['passed'] and result['complete'] and result['registration_sha256']==sha(regpath)
        identities={str(regpath):sha(regpath),str(resultpath):sha(resultpath)}
        for records in (reg['inputs'],result['artifacts']):
            for path,expected in records.items():
                assert sha(path)==expected,path
                identities[path]=expected
        assert len(result['cases'])==4 and {(c['width'],c['actor']) for c in result['cases']}=={(w,a) for w in (362,387) for a in (0,1)}
        records=[]
        for case in result['cases']:
            stem=f"{case['width']}-p{case['actor']}"
            path=STORE/(stem+'-raw.npz');assert str(path) in identities
            with np.load(path,allow_pickle=False) as arrays:
                assert set(arrays.files)=={'cpu','gpu','gradient_cpu','gradient_gpu','fitted_cpu','fitted_gpu'}
                errors={}
                for left,right,field in (('cpu','gpu','forward_error'),('gradient_cpu','gradient_gpu','gradient_error'),
                                         ('fitted_cpu','fitted_gpu','fitted_error')):
                    a,b=arrays[left],arrays[right]
                    assert a.shape==b.shape and np.isfinite(a).all() and np.isfinite(b).all()
                    if 'gradient' not in left:assert a.shape==(case['rows'],4)
                    error=float(np.max(abs(a-b)))
                    assert error==case[field] and error<=reg['raw_absolute_tolerance']
                    errors[field]=error
            path=STORE/(stem+'-networks.json');assert str(path) in identities
            models=json.loads(path.read_bytes());assert models['direct']==models['captured']
            for mode in ('direct','captured'):
                net=models[mode];width=case['width']
                shapes={'w0':64*width,'b0':64,'w1':4096,'b1':64,'w2':256,'b2':4}
                assert set(net)==set(shapes)
                for name,size in shapes.items():
                    assert len(net[name])==size and np.isfinite(net[name]).all()
                metrics=models[mode+'_metrics']
                assert metrics['objective_sha256']==case['objective_sha256'] and metrics['steps']==256
                assert metrics['normalized_grouped_loss_before']==case['loss_before'] and metrics['normalized_grouped_loss_after']==case['loss_after']
            records.append(dict(width=case['width'],actor=case['actor'],raw_errors=errors,
                                exact_exported_network=True,direct_optimizer_seconds=models['direct_metrics']['optimizer_seconds'],
                                captured_optimizer_seconds=models['captured_metrics']['optimizer_seconds']))
        assert all(row==result['repeat_fit_memory'][0] for row in result['repeat_fit_memory']) and len(result['repeat_fit_memory'])==3
        report=dict(complete=True,passed=True,source_sha256=sha(__file__),identities=identities,cases=records,
                    seconds=time.monotonic()-started,scientific_training=False,accuracy_qualified=False,
                    scope='Saved numeric arrays and exported networks independently rechecked, without fitting or inference.',
                    limitations=['Reported scalar losses, allocator plateau and RNG checks are retained runtime evidence; this readback does not independently rerun those operations.'])
    except Exception as error:
        report=dict(complete=False,passed=False,error=repr(error),seconds=time.monotonic()-started,retry_allowed=False)
    write(target,report);print(json.dumps({k:report[k] for k in ('complete','passed','seconds')}))
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
