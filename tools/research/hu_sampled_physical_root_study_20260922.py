"""Predeclare, bind, and run the first fresh-deal physical-pilot evaluation.

Preparation draws no deals. Running requires an independent review of the
pilot's terminal state and its final published iteration boundary.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

import psutil

from loopback_research_validation import idle
from sampled_physical_checkpoint_v1 import read_object, verify_bank
from sampled_physical_root_evaluation_v1 import ROOT, sha, save, run

OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-root-study-v1'
STORE = Path('S:/GTOpen-research') / PREFIX
PILOT_PREFIX = 'sampled-physical-pilot-gpu-v1'
PILOT_STORE = Path('S:/GTOpen-research') / PILOT_PREFIX
LOCK = OUT / (PREFIX + '.running')


def output(suffix):
    return OUT / (PREFIX + '-' + suffix + '.json')


def status(value):
    path = output('status')
    temporary = path.with_suffix('.tmp')
    save(temporary, value)
    temporary.replace(path)


def prepare():
    assert idle() and not STORE.exists()
    control = OUT / 'sampled-physical-root-evaluation-control-v1-review.json'
    control_reg = OUT / 'sampled-physical-root-evaluation-control-v1-registration.json'
    reviewed = json.loads(control.read_text())
    assert reviewed['passed'] and reviewed['registration_sha256'] == sha(control_reg)
    prior = json.loads(control_reg.read_text())
    # Reuse the verified implementation dependency list but exclude the tiny
    # source models and control checkpoint. The real bank is bound at admission.
    paths = [Path(p) for p in prior['inputs'] if Path(p).is_relative_to(ROOT)
             and ('tools' in Path(p).parts or 'crates' in Path(p).parts or 'target' in Path(p).parts)]
    paths += [Path(__file__), control, control_reg, OUT / 'bb-context-candidate.json',
              OUT / (PILOT_PREFIX + '-registration.json')]
    config = dict(training_deals=8192, evaluation_deals=16384, batch_size=16,
                  minimum_training_deals=16, train_seed=49101, test_seed=49102)
    reg = dict(id=PREFIX, inputs={str(p): sha(p) for p in paths},
               context=str(OUT / 'bb-context-candidate.json'), config=config,
               source_selection='Last fully published pilot checkpoint after its terminal outcome is independently reviewed. Use every played generation; exclude the unused next model. No choice by test results.',
               allowed_outcomes='Completed 128-iteration pilot, or independently verified execution-budget stop with at least one fully published iteration. Other failures require separate diagnosis; no automatic admission.',
               required_review_fields=['passed', 'pilot_status_sha256', 'pilot_latest_sha256',
                                       'completed_iterations', 'checkpoint', 'all_published_iterations_verified',
                                       'budget_exhaustion_verified'],
               maximum_seconds=7200, host_reserve_bytes=20_000_000_000,
               disk_reserve_bytes=40_000_000_000, maximum_store_bytes=30_000_000_000,
               store=str(STORE), chance='full_deck compatible private pairs, uniform remaining runout',
               comparisons=['trained-response', 'always-fold', 'always-call', 'always-raise', 'always-jam'],
               interval='One final look at 16384 complete paired test deals; 5% family error across five fixed comparisons. No intermediate significance stop.',
               stopping='Complete fixed sample counts or stop at two hours, production activity, reserve violation or failure. No retries or automatic extension; unfinished evaluation is not a completed strength result.',
               scope='Restricted BB root-deviation evaluation of the frozen physical pilot bank against its frozen opponent. Fixed incoming ranges and later behavior, limited betting menu, earlier folded cards omitted. No best-response upper bound, joint-equilibrium or general-tree qualification.',
               device='cpu', threads=2, no_gpu=True, production_modified=False)
    save(output('registration'), reg)
    print(json.dumps(dict(prepared=True, registration=str(output('registration')), config=config)))


def verify_inputs(reg):
    for path, expected in reg['inputs'].items():
        assert sha(path) == expected, path


def bind(reg, review_path):
    verify_inputs(reg)
    review_path = Path(review_path)
    review = json.loads(review_path.read_text())
    assert all(k in review for k in reg['required_review_fields'])
    assert review['passed'] is True and review['all_published_iterations_verified'] is True
    status_path = OUT / (PILOT_PREFIX + '-status.json')
    latest_path = PILOT_STORE / 'latest.json'
    assert sha(status_path) == review['pilot_status_sha256']
    assert sha(latest_path) == review['pilot_latest_sha256']
    ps = json.loads(status_path.read_text())
    assert ps['state'] in ('complete', 'stopped')
    assert ps['state'] == 'complete' or review['budget_exhaustion_verified'] is True
    # The terminal status is published only after the worker exits. Also wait
    # for the training controller to release its GPU lock before admission.
    assert not (ROOT / 'research/preflop-evolution/representative-coverage-20260919/running.lock').exists()
    latest = json.loads(latest_path.read_text())
    assert latest['checkpoint'] == review['checkpoint']
    assert latest['completed_iterations'] == review['completed_iterations'] > 0
    objects = PILOT_STORE / 'checkpoint-objects'
    checkpoint = json.loads(read_object(objects, latest['checkpoint']))
    assert checkpoint['completed_iterations'] == latest['completed_iterations']
    assert checkpoint['config'] == latest['config']
    verify_bank(objects, checkpoint['completed_iterations'], checkpoint['played_bank'], checkpoint['next_model'])
    bound = dict(reg, objects=str(objects), checkpoint=latest['checkpoint'],
                 protocol_sha256=sha(output('registration')), pilot_review=str(review_path),
                 pilot_review_sha256=sha(review_path), pilot_status_sha256=sha(status_path),
                 pilot_latest_sha256=sha(latest_path), selected_iterations=latest['completed_iterations'])
    bound['inputs'] = dict(reg['inputs'])
    for p in [review_path, status_path, latest_path, objects / latest['checkpoint']['file']]:
        bound['inputs'][str(p)] = sha(p)
    for reference in [*checkpoint['played_bank'], checkpoint['next_model']]:
        bound['inputs'][str(objects / reference['file'])] = sha(objects / reference['file'])
    save(output('admission'), bound)
    return bound


def worker(reg):
    started = time.monotonic()
    last = 0.

    def guard():
        nonlocal last
        now = time.monotonic()
        if now - last >= 2:
            assert now - started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
            assert shutil.disk_usage(STORE.parent).free >= reg['disk_reserve_bytes']
            last = now

    verify_inputs(reg)
    result = run(reg, STORE, guard)
    verify_inputs(reg)
    assert result['terminal']
    save(output('result'), result)


def execute(review_path):
    reg = json.loads(output('registration').read_text())
    assert idle() and not STORE.exists() and not LOCK.exists()
    assert psutil.virtual_memory().available >= reg['host_reserve_bytes']
    assert shutil.disk_usage(STORE.parent).free >= reg['disk_reserve_bytes'] + reg['maximum_store_bytes']
    admission = bind(reg, review_path)
    child = None; error = None; samples = []; last_resource = 0.
    with LOCK.open('x') as stream: stream.write(str(os.getpid()))
    started = time.monotonic()
    try:
        env = os.environ.copy()
        env.update(CUDA_VISIBLE_DEVICES='', OMP_NUM_THREADS='2', PYTHONUNBUFFERED='1')
        status(dict(state='running', controller_pid=os.getpid(), production_modified=False))
        with (OUT / (PREFIX + '.log')).open('x') as log:
            child = subprocess.Popen([sys.executable, str(Path(__file__)), '--worker', str(output('admission'))],
                                     cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                                     creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                elapsed = time.monotonic() - started
                assert elapsed < reg['maximum_seconds'] and idle(), 'Execution deadline or production activity'
                if elapsed - last_resource >= 10:
                    host = psutil.virtual_memory().available; disk = shutil.disk_usage(STORE.parent).free
                    used = sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file()) if STORE.exists() else 0
                    completed = len(list(STORE.glob('*/summary.json'))) if STORE.exists() else 0
                    samples.append(dict(seconds=elapsed, free_host_bytes=host, free_disk_bytes=disk,
                                        store_bytes=used, completed_batches=completed))
                    assert host >= reg['host_reserve_bytes'] and disk >= reg['disk_reserve_bytes']
                    assert used <= reg['maximum_store_bytes']
                    status(dict(state='running', controller_pid=os.getpid(), completed_batches=completed,
                                seconds=elapsed, production_modified=False))
                    last_resource = elapsed
        assert child.returncode == 0, f'Evaluation worker failed: {child.returncode}'
        verify_inputs(admission)
        result = json.loads(output('result').read_text())
        assert result['terminal'] and result['completed_training_deals'] == reg['config']['training_deals']
        assert result['completed_evaluation_deals'] == reg['config']['evaluation_deals']
    except Exception as exc:
        error = str(exc)
        raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try: p.terminate()
                except psutil.NoSuchProcess: pass
            child.terminate(); child.wait(timeout=20)
        status(dict(state='stopped' if error else 'complete', error=error,
                    exit_code=child.returncode if child else None, seconds=time.monotonic() - started,
                    store=str(STORE), production_modified=False))
        save(output('resources'), samples)
        assert LOCK.read_text().strip() == str(os.getpid())
        LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--prepare', action='store_true')
    action.add_argument('--run', action='store_true')
    action.add_argument('--worker')
    parser.add_argument('--pilot-review')
    args = parser.parse_args()
    if args.prepare: prepare()
    elif args.worker: worker(json.loads(Path(args.worker).read_text()))
    else:
        assert args.pilot_review, 'Independent terminal pilot review required'
        execute(args.pilot_review)
