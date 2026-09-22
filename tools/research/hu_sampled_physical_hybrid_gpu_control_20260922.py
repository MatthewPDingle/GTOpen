"""Prepared old-fixture CPU/CUDA equivalence control; no poker-quality claim."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_physical_preflop_table_v1 import Table, average
from sampled_physical_hybrid_checkpoint_v1 import POLICY_TYPE, validate_model
from sampled_physical_hybrid_gpu_bank_v1 import HybridCudaBank, prepare_tables
from sampled_physical_deals_v1 import digest
from sampled_batch_protocol_v2 import policy_document

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-hybrid-gpu-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX
LOCK = ROOT/'research/preflop-evolution/representative-coverage-20260919/running.lock'
OTHER = ROOT/'research/preflop-evolution/symmetric-bridge-20260919/running.lock'


def output(suffix): return OUT/f'{PREFIX}-{suffix}.json'


def verify(reg):
    for p,h in reg['inputs'].items(): assert sha(p) == h,p


def prepare():
    assert idle() and not STORE.exists()
    preregpath = OUT/'sampled-physical-preflop-table-control-v1-registration.json'
    prereqpath = OUT/'sampled-physical-preflop-table-control-v1-result.json'
    prereg = json.loads(preregpath.read_text()); prereq = json.loads(prereqpath.read_text())
    assert prereq['passed'] and prereq['registration_sha256'] == sha(preregpath)
    verify(prereg)
    for p,h in prereq['artifacts'].items(): assert sha(p) == h,p
    queries = json.loads(Path(prereg['fixture']).read_text()); context = queries['context_source']
    old_models = json.loads((OUT/'sampled-physical-preflop-table-control-v1-models.json').read_text())
    models = [dict(format=2,policy_type=POLICY_TYPE,context_sha256=digest(context),generation=i,
        networks=m['networks'],advantage_scales=[1.,1.],preflop_tables=m['tables']) for i,m in enumerate(old_models)]
    for m in models: validate_model(m,context)
    save(output('models'),models)
    paths = [*map(Path,prereg['inputs']),*map(Path,prereq['artifacts']),preregpath,prereqpath,
        Path(__file__),output('models'),ROOT/'tools/research/sampled_physical_hybrid_checkpoint_v1.py',
        ROOT/'tools/research/sampled_physical_hybrid_gpu_bank_v1.py',
        ROOT/'target/release/examples/hu_sampled_profile_evaluation.exe']
    reg = dict(inputs={str(p):sha(p) for p in paths},query_fixture=prereg['fixture'],
        context=str(OUT/'bb-context-candidate.json'),batch=str(OUT/'sampled-batch-bridge-v2-batch.json'),
        models=str(output('models')),weights=[[1.,2.,3.],[3.,2.,1.]],source_generations=[0,77,78],
        maximum_seconds=600,policy_tolerance=1e-4,support_tolerance=1e-3,payoff_tolerance_bb=1e-3,
        scope='Synthetic three-generation old-fixture transport control, using fixed old pilot networks and retained tables. Generation labels 0/1/2 are fixture ordering only. No new training, study test outcomes or poker-quality claim.',
        production_modified=False)
    save(output('registration'),reg)
    tables = [[None if d is None else Table(d,context) for d in m['preflop_tables']] for m in models]
    ids,values,mask = prepare_tables(queries,tables,context)
    base = np.zeros((len(queries['observations']),4))
    for i,o in enumerate(queries['observations']): base[i,:o['n']] = 1/o['n']
    for m,pair in enumerate(tables):
        expected = base.copy()
        for table in pair:
            if table is not None: expected,_ = table.apply(queries['observations'],expected)
        reconstructed = base.copy()
        reconstructed[ids] = np.where(mask[m,:,None],values[m],reconstructed[ids])
        assert np.array_equal(reconstructed,expected)
    verify(reg)
    preparation = dict(passed=True,lookup_matches_reference_exactly=True,preflop_queries=len(ids),
        overridden_rows=mask.sum(1).tolist(),registration_sha256=sha(output('registration')),
        gpu_execution_tested=False,production_modified=False)
    save(output('preparation'),preparation); print(json.dumps(preparation))


def worker(reg):
    import torch
    torch.set_num_threads(2); torch.use_deterministic_algorithms(True)
    torch.backends.cuda.matmul.allow_tf32 = False; torch.backends.cudnn.allow_tf32 = False
    started = time.monotonic(); last = 0.
    def guard():
        nonlocal last
        now = time.monotonic()
        if now-last >= 2:
            assert now-started < reg['maximum_seconds'] and idle()
            assert psutil.virtual_memory().available >= 20_000_000_000
            assert torch.cuda.mem_get_info()[0] >= 3_000_000_000
            assert shutil.disk_usage(STORE.parent).free >= 40_000_000_000
            last = now
    verify(reg); guard(); STORE.mkdir(exist_ok=False)
    queries = json.loads(Path(reg['query_fixture']).read_text()); context = Path(reg['context']).read_text()
    documents = json.loads(Path(reg['models']).read_text())
    models = [dict(networks=d['networks'],tables=d['preflop_tables']) for d in documents]
    cpu_rng = torch.get_rng_state().clone(); gpu_rng = torch.cuda.get_rng_state().clone()
    cpu,cpu_support = average(queries,models,reg['weights'],context_source=context,device='cpu',guard=guard)
    bank = HybridCudaBank(documents,reg['weights'],context_source=context,models_per_chunk=8,guard=guard)
    gpu,gpu_support = bank.average(queries,guard=guard)
    policy_error = float(np.max(np.abs(cpu-gpu))); support_error = float(np.max(np.abs(cpu_support-gpu_support)))
    assert policy_error <= reg['policy_tolerance'] and support_error <= reg['support_tolerance']
    assert np.array_equal(cpu_support==0,gpu_support==0)
    chunks = []
    for size in (1,2):
        bank.chunk = size; other,other_support = bank.average(queries,guard=guard)
        error = float(np.max(np.abs(other-gpu))); reach_error = float(np.max(np.abs(other_support-gpu_support)))
        assert error <= reg['policy_tolerance'] and reach_error <= reg['support_tolerance']
        chunks.append(dict(chunk_size=size,maximum_policy_error=error,maximum_support_error=reach_error))
    profilepath = STORE/'profiles.json'; nativepath = STORE/'native.json'
    save(profilepath,dict(format=1,context_source=context,batch_source=queries['batch_source'],profiles=[
        dict(name=name,policies=policy_document(queries,p)['policies']) for name,p in (('cpu',cpu),('gpu',gpu))]))
    guard(); done = subprocess.run([str(ROOT/'target/release/examples/hu_sampled_profile_evaluation.exe'),
        reg['context'],reg['batch'],str(profilepath),str(nativepath)],cwd=ROOT,capture_output=True,
        text=True,timeout=120,creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode == 0,done.stderr[-2000:]
    native = json.loads(nativepath.read_text()); profiles = {p['name']:p for p in native['profiles']}
    a = np.asarray([d['values'] for d in profiles['cpu']['deals']]); b = np.asarray([d['values'] for d in profiles['gpu']['deals']])
    payoff_error = float(np.max(np.abs(a-b))); assert payoff_error <= reg['payoff_tolerance_bb']
    assert native['maximum_forward_cashflow_error'] < 1e-8 and native['maximum_conservation_error'] < 1e-8
    assert torch.equal(cpu_rng,torch.get_rng_state()) and torch.equal(gpu_rng,torch.cuda.get_rng_state())
    policies_path = STORE/'comparison.json'; save(policies_path,dict(cpu=cpu.tolist(),gpu=gpu.tolist(),
        cpu_support=cpu_support.tolist(),gpu_support=gpu_support.tolist()))
    verify(reg); guard()
    save(output('result'),dict(passed=True,registration_sha256=sha(output('registration')),
        maximum_policy_error=policy_error,maximum_support_error=support_error,chunk_checks=chunks,
        maximum_payoff_error_bb=payoff_error,observations=len(cpu),rng_unchanged=True,
        artifacts={str(p):sha(p) for p in (profilepath,nativepath,policies_path)},seconds=time.monotonic()-started,
        accuracy_qualified=False,production_modified=False,scope=reg['scope']))


def execute():
    reg = json.loads(output('registration').read_text()); verify(reg)
    prepared = json.loads(output('preparation').read_text())
    assert prepared['passed'] and prepared['registration_sha256'] == sha(output('registration'))
    assert idle() and not LOCK.exists() and not OTHER.exists() and not STORE.exists()
    child = None; error = None
    with LOCK.open('x') as f: f.write(str(os.getpid()))
    started = time.monotonic()
    try:
        env = os.environ.copy(); env.update(CUBLAS_WORKSPACE_CONFIG=':4096:8',OMP_NUM_THREADS='2',PYTHONUNBUFFERED='1')
        with (OUT/f'{PREFIX}.log').open('x') as log:
            child = subprocess.Popen([sys.executable,str(Path(__file__)),'--worker',str(output('registration'))],
                cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2)
                assert time.monotonic()-started < reg['maximum_seconds'] and idle(), 'Deadline or production activity'
        assert child.returncode == 0, 'Read worker log; no automatic retry'
        verify(reg); result = json.loads(output('result').read_text()); assert result['passed']
        for p,h in result['artifacts'].items(): assert sha(p) == h,p
        save(output('review'),dict(passed=True,result_sha256=sha(output('result')),
            registration_sha256=sha(output('registration')),production_modified=False))
    except Exception as exc:
        error = str(exc); raise
    finally:
        if child is not None and child.poll() is None:
            for p in reversed(psutil.Process(child.pid).children(recursive=True)):
                try:p.terminate()
                except psutil.NoSuchProcess:pass
            child.terminate(); child.wait(timeout=20)
        save(output('status'),dict(state='failed' if error else 'complete',error=error,
            exit_code=child.returncode if child else None,seconds=time.monotonic()-started,production_modified=False))
        assert LOCK.read_text().strip() == str(os.getpid()); LOCK.unlink()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--prepare',action='store_true'); action.add_argument('--run',action='store_true'); action.add_argument('--worker')
    args = parser.parse_args()
    if args.prepare:prepare()
    elif args.worker:worker(json.loads(Path(args.worker).read_text()))
    else:execute()
