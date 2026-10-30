"""Bounded CPU profiling of immutable final-trial data; no training changes."""
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

PREFIX = 'saved-preparation-profile-v1'
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'
CAP = 10_000_000


def worker(reg):
    import numpy as np
    from action_integrated_checkpoint_v1 import restore_checkpoint
    from sampled_physical_fit_v1 import grouped_rows
    from sampled_visible_initialization_v1 import features
    from hu_action_integrated_fresh_review_20260925 import base_predict
    from sampled_visible_hybrid_checkpoint_v1 import read_object
    started = time.monotonic()
    result = read(reg['trial_result']); registration = read(reg['trial_registration'])
    store = Path(registration['store']); objects = store/'objects'
    source = Path(reg['context']).read_text(); catalog = Path(reg['catalog']).read_text()
    matrix = read(reg['matrix']); metrics = read(store/'iteration-0078/metrics.json')
    profiler = cProfile.Profile(); phases = []

    def phase(name, fn):
        began = time.monotonic(); profiler.enable()
        try: value = fn()
        finally: profiler.disable()
        phases.append(dict(name=name,seconds=time.monotonic()-began))
        print(json.dumps(phases[-1]),flush=True)
        return value

    state = phase('restore_final_checkpoint', lambda: restore_checkpoint(objects,
        result['final_checkpoint'],config=registration['config'],context_source=source,
        catalog_source=catalog,matrix_sha256=sha(reg['matrix']),
        entry_mass=np.asarray(matrix['class_mass']).sum(axis=0)))
    summaries = []
    for player, reservoir in enumerate(state['reservoirs']):
        grouped = phase(f'player_{player}_grouping',lambda: grouped_rows(reservoir))
        x = phase(f'player_{player}_visible_features',lambda: features(
            [dict(active_features=row.tolist()) for row in grouped['active']]))
        expected = metrics['fits'][player]
        assert len(x)==expected['grouped_observations']
        assert grouped['denominator']==expected['legal_target_count']
        assert grouped['scale']==expected['advantage_scale']
        summaries.append(dict(player=player,rows=len(x),feature_bytes=x.nbytes,
            features_sha256=hashlib.sha256(x.tobytes()).hexdigest()))
        del x, grouped
    part=store/'iteration-0078/batch-00'
    query=phase('parse_one_native_query_batch',lambda: read(part/'queries.json'))
    model=json.loads(read_object(objects,metrics['used_model']))
    _, policies, _=phase('cpu_base_predict_one_native_batch',lambda:
        base_predict(query,model['exact_model']['base_model'],'cpu'))
    stream=io.StringIO()
    pstats.Stats(profiler,stream=stream).strip_dirs().sort_stats('cumulative').print_stats(45)
    text=stream.getvalue(); assert len(text.encode())<CAP
    (OUT/f'{PREFIX}-cprofile.txt').write_text(text,encoding='utf-8',newline='\n')
    for path,digest in reg['inputs'].items(): assert sha(path)==digest,path
    save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        phases=phases,feature_summaries=summaries,batch_observations=len(query['observations']),
        predicted_rows=len(policies),profile_sha256=sha(OUT/f'{PREFIX}-cprofile.txt'),
        seconds=time.monotonic()-started,production_modified=False,gpu_used=False,
        scope='Instrumented saved-data CPU preparation profile. No optimization, new learning, fresh validation or end-to-end speedup claim.'))


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
    inputs=dict(read(tr)['inputs']);inputs.update({str(p):sha(p) for p in paths})
    for path,digest in inputs.items():assert sha(path)==digest,path
    roots=measure();assert sum(x['allocated_file_bytes'] for x in roots)+CAP+2_000_000_000<=800_000_000_000
    reg=dict(inputs=inputs,trial_registration=str(tr),trial_result=str(result),
        context=str(paths[4]),matrix=str(paths[5]),catalog=str(paths[6]),storage_inventory=roots,
        maximum_seconds=600,maximum_output_bytes=CAP,production_modified=False,gpu_used=False,
        selection='Last completed replication checkpoint: maximal retained dataset. One batch (78/00) for inference; no candidate selection.')
    save(rp,reg);child=None;error=None;started=time.monotonic()
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    try:
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'--worker'],
                cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                assert time.monotonic()-started<600 and idle() and not OTHER.exists()
                assert psutil.virtual_memory().available>=20_000_000_000
                assert shutil.disk_usage('T:/').free>=40_000_000_000
                assert sum(p.stat().st_size for p in OUT.glob(PREFIX+'*') if p.is_file())<=CAP
                try:child.wait(timeout=5)
                except subprocess.TimeoutExpired:pass
        assert child.returncode==0, 'Profile failed; preserve log'
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
