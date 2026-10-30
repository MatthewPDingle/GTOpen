"""Verify retained scoring evidence from the pre-training logging failure."""
import hashlib
import json
from pathlib import Path
import numpy as np
from sampled_physical_root_evaluation_v1 import save,sha

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='stack-context-native-cycle-control-v1';STORE=Path('S:/GTOpen-research')/NAME
OUTPUT=OUT/(NAME+'-parity-readback.json')


def main():
    attempt=OUT/(NAME+'-parity-readback-attempt.json')
    if OUTPUT.exists() or attempt.exists():raise ValueError('Preserve existing parity readback')
    registration=OUT/(NAME+'-registration.json');failure=OUT/(NAME+'-failure.json')
    failed=json.loads(failure.read_bytes());reg=json.loads(registration.read_bytes())
    if 'FileExistsError' not in failed['error'] or 'stage(\'native-joint-cycle\')' not in failed['traceback']:
        raise ValueError('Expected verified pre-training logging failure')
    if (STORE/'cycle-1').exists() or (OUT/(NAME+'-result.json')).exists():raise ValueError('Unexpected native cycle artifacts')
    save(attempt,dict(reader_sha256=sha(__file__),registration_sha256=sha(registration),failure_sha256=sha(failure)))
    for p,h in reg['inputs'].items():
        if sha(p)!=h:raise ValueError('Registered inference source changed')
    records=[]
    for width in (362,387):
        for d in (20,40,60,100,150,200,400):
            path=STORE/f'parity-{width}-{d}.npz'
            with np.load(path,allow_pickle=False) as f:a={k:f[k] for k in f.files}
            if set(a)!={'cpu_raw','cuda_raw','cpu','cuda','reference','cpu_reach','cuda_reach','reference_reach'}:raise ValueError('Missing numeric evidence')
            count=len(json.loads(Path(f'S:/GTOpen-research/stack-context-model-control-v1/stack-{d}-queries.json').read_bytes())['observations'])
            if any(not np.isfinite(v).all() for v in a.values()):raise ValueError('Nonfinite parity evidence')
            if any(v.shape!=((count,) if 'reach' in k else (count,4)) for k,v in a.items()):raise ValueError('Wrong row coverage')
            errors=dict(raw=float(np.max(abs(a['cpu_raw']-a['cuda_raw']))),policy=float(np.max(abs(a['cpu']-a['cuda']))),
                reference=float(np.max(abs(a['cpu']-a['reference']))),reach=float(max(np.max(abs(a['cpu_reach']-a['cuda_reach'])),np.max(abs(a['cpu_reach']-a['reference_reach'])))))
            if max(errors.values())>1e-10 or not np.array_equal(a['cpu']>0,a['cuda']>0) or not np.array_equal(a['cpu']>0,a['reference']>0):raise ValueError('Saved parity mismatch')
            for k in ('cpu','cuda','reference'):
                if np.any(a[k]<0) or np.max(abs(a[k].sum(1)-1))>1e-12:raise ValueError('Invalid saved probabilities')
            records.append(dict(width=width,depth=d,rows=count,errors=errors,artifact=str(path),sha256=sha(path)))
    save(OUTPUT,dict(complete=True,passed=True,registration_sha256=sha(registration),failure_sha256=sha(failure),
        reader_sha256=sha(__file__),records=records,training_started=False,full_cycle_qualified=False,
        scope='Saved raw scores, complete policies, positive support and own-history reaches; no repeated GPU inference. V1 stopped before native collection.'))
    print(json.dumps(dict(passed=True,cases=len(records),maximum_error=max(max(r['errors'].values()) for r in records))))


if __name__=='__main__':main()
