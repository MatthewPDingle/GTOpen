"""Bulk visible-feature equivalence and paired saved-data timing; no training changes."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import cProfile
import hashlib
import io
import json
from pathlib import Path
import pstats
import shutil
import subprocess
import sys
import time
import psutil
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_root_retained_storage_admitted_study_20260924 import measure
from reboot_research_idle_v1 import idle

PREFIX = 'visible-features-bulk-control-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
CAP = 10_000_000


def worker(reg):
    import numpy as np
    import statistics
    from action_integrated_checkpoint_v1 import restore_checkpoint
    from sampled_physical_fit_v1 import grouped_rows
    from sampled_visible_initialization_v1 import features as reference
    from sampled_visible_features_bulk_v1 import features as candidate
    started=time.monotonic()
    result=read(reg['trial_result']);registration=read(reg['trial_registration'])
    assert all(result['config'][k]==v for k,v in registration['config'].items())
    store=Path(registration['store']);source=Path(reg['context']).read_text()
    matrix=read(reg['matrix'])
    state=restore_checkpoint(store/'objects',result['final_checkpoint'],config=result['config'],
        context_source=source,catalog_source=Path(reg['catalog']).read_text(),
        matrix_sha256=sha(reg['matrix']),entry_mass=np.asarray(matrix['class_mass']).sum(axis=0))
    rng=np.random.default_rng(2026092501)
    starts=[v for i in range(7) for v in (19*i,19*i+14)]+[133,135,139]+[155+6*i for i in range(19)]
    def sample(phase,history_length=None):
        cards=rng.choice(52,size=2+(0,3,4,5)[phase],replace=False).tolist();values=[]
        for i in range(7):values.extend([cards[i]//4,cards[i]%4] if i<len(cards) else [13,4])
        count=int(rng.integers(0,20)) if history_length is None else history_length
        values += [int(rng.integers(2)),phase,int(rng.integers(16))]+rng.integers(1,6,size=count).tolist()+[0]*(19-count)
        active=[s+x for s,x in zip(starts,values)];rng.shuffle(active);return active
    synthetic=[dict(active_features=sample(i%4)) for i in range(6000)]
    assert reference(synthetic).tobytes()==candidate(synthetic).tobytes()
    assert reference([]).shape==candidate([]).shape==(0,302)
    x=sorted(sample(0,0));bad=[]
    for label,fn in [('short',lambda a:a[:-1]),('long',lambda a:a+[0]),
        ('duplicate',lambda a:[a[1],*a[1:]]),('bool',lambda a:[True,*a[1:]]),
        ('float',lambda a:[float(a[0]),*a[1:]]),('numpy-int',lambda a:[np.int64(a[0]),*a[1:]]),
        ('large',lambda a:[2**80,*a[1:]]),('negative',lambda a:[-1,*a[1:]])]:bad.append((label,fn(x.copy())))
    for label,index,value in [('group',0,14),('missing-card',0,13),('future-board',15,136),('history-gap',35,264)]:
        row=x.copy();row[index]=value;bad.append((label,row))
    row=x.copy();row[2]=19+row[0];row[3]=33+(row[1]-14);bad.append(('duplicate-card',row))
    for label,row in bad:
        for builder in (reference,candidate):
            try:builder([dict(active_features=row)])
            except (ValueError,TypeError,IndexError,AssertionError):pass
            else:raise AssertionError((label,builder.__module__))
    expected=read(OUT/'saved-preparation-profile-v2-result.json')['feature_summaries']
    summaries=[]
    datasets=[]
    for player,reservoir in enumerate(state['reservoirs']):
        before=time.monotonic();grouped=grouped_rows(reservoir)
        datasets.append((f'player-{player}',grouped['active'],expected[player]['features_sha256'],time.monotonic()-before))
    native=read(store/'iteration-0078/batch-00/queries.json')
    datasets.append(('native-batch-78-00',np.asarray([o['active_features'] for o in native['observations']]),None,None))
    for name,active,known,group_seconds in datasets:
        times={'reference':[],'candidate':[]};digest=None
        # Three paired runs, alternate order; allocation and observation conversion
        # are included. Hashing/byte verification are outside timed sections.
        for repeat in range(3):
            order=[('reference',reference),('candidate',candidate)]
            if repeat%2:order.reverse()
            for label,builder in order:
                before=time.monotonic()
                output=builder([dict(active_features=row.tolist()) for row in active])
                times[label].append(time.monotonic()-before)
                assert output.dtype==np.float32 and output.shape==(len(active),302)
                actual=hashlib.sha256(output.tobytes()).hexdigest()
                if digest is None:digest=actual
                assert actual==digest and (known is None or actual==known)
                del output
        row=dict(dataset=name,rows=len(active),grouping_seconds=group_seconds,seconds=times,
            median_feature_speedup=statistics.median(times['reference'])/statistics.median(times['candidate']),
            features_sha256=digest,byte_identical=True)
        summaries.append(row);print(json.dumps(row),flush=True)
    for path,digest in reg['inputs'].items():assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        synthetic_cases=6000,invalid_cases=[x[0] for x in bad],datasets=summaries,
        seconds=time.monotonic()-started,production_modified=False,gpu_used=False,
        scope='Saved-data feature equivalence and uninstrumented paired timing only. No new trained candidate, range accuracy result, fitter integration or end-to-end speedup claim.'))


def main():
    if sys.argv[1:]==['--worker']:
        worker(read(OUT/f'{PREFIX}-registration.json'));return
    assert sys.argv[1:]==['--run'] and idle()
    assert not LOCK.exists() and not OTHER.exists()
    rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    trial='action-integrated-replication-v1'
    tr=OUT/f'{trial}-registration.json'; result=OUT/f'{trial}-result.json'
    audit=OUT/f'{trial}-independent-review.json'
    assert read(result)['terminal'] and read(audit)['passed']
    assert read(audit)['source_result_sha256']==sha(result)
    assert read(OUT/'action-integrated-comparison-continuation-v1-result.json')['passed']
    paths=[Path(__file__).resolve(),tr,result,audit,OUT/'bb-context-candidate.json',
        OUT/'preflop-allin-matrix-control-v1-matrix.json',
        Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')]
    paths.extend([ROOT/'tools/research/sampled_visible_features_bulk_v1.py',
        OUT/'saved-preparation-profile-v2-result.json',
        ROOT/'tools/research/hu_saved_preparation_profile_20260925.py',
        OUT/'saved-preparation-profile-v1-registration.json',OUT/'saved-preparation-profile-v1-status.json',
        OUT/'saved-preparation-profile-v1.log'])
    inputs=dict(read(tr)['inputs']);inputs.update({str(p):sha(p) for p in paths})
    for path,digest in inputs.items():assert sha(path)==digest,path
    roots=measure();assert sum(x['allocated_file_bytes'] for x in roots)+CAP+2_000_000_000<=800_000_000_000
    reg=dict(inputs=inputs,trial_registration=str(tr),trial_result=str(result),
        context=str(paths[4]),matrix=str(paths[5]),catalog=str(paths[6]),storage_inventory=roots,
        maximum_seconds=900,maximum_output_bytes=CAP,production_modified=False,gpu_used=False,
        selection='Last completed replication checkpoint: maximal retained dataset. One batch (78/00) for inference; no candidate selection.')
    save(rp,reg);child=None;error=None;started=time.monotonic()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                assert time.monotonic()-started<900 and idle() and not OTHER.exists()
                assert psutil.virtual_memory().available>=20_000_000_000
                assert shutil.disk_usage('T:/').free>=40_000_000_000
                assert sum(p.stat().st_size for p in OUT.glob(PREFIX+'*') if p.is_file())<=CAP
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0, 'Feature control failed; preserve log'
        assert read(OUT/f'{PREFIX}-result.json')['passed']
    except BaseException as exc:
        error=repr(exc);raise
    finally:
        if child is not None and child.poll() is None:
            child.terminate();child.wait(timeout=15)
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,
            production_modified=False))


if __name__=='__main__':main()
