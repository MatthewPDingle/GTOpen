"""Post-result, CPU-only saved-history diagnostic; no training or policy selection."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import hashlib
import json
import math
import multiprocessing
from pathlib import Path
import time
import numpy as np
import psutil
from board_root_accumulator_v1 import BoardRootRegrets
from board_training_policy_v1 import probabilities
from later_action_root_trajectory_20260926 import average, tv
from preflop_allin_matrix_v1 import AllinMatrix
from showdown_root_trajectory_20260927 import safe_read_only_resources

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'board-root-trajectory-v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(path):
    return json.loads(path.read_text())


def publish(path, value):
    raw = json.dumps(value, separators=(',', ':'), allow_nan=False).encode()
    assert len(raw) < 32_000_000, 'Bound new diagnostic output'
    with path.open('xb') as stream:
        stream.write(raw)


def scalar_policy(regrets, generation, fallback):
    assert len(regrets) == len(fallback) == 169
    if generation == 0:
        assert all(all(x == 0 for x in row) for row in regrets)
        return fallback
    result = []
    for row in regrets:
        assert len(row) == 4 and all(math.isfinite(x) for x in row)
        positive = [max(0., x) for x in row]
        total = math.fsum(positive)
        result.append([x/total for x in positive] if total else
                      [float(a == max(range(4), key=row.__getitem__)) for a in range(4)])
    return result


def summarize(policies, mass, expected):
    assert len(policies) == 79 and len(mass) == 169
    assert all(math.isfinite(w) and w > 0 for w in mass)
    assert abs(math.fsum(mass)-1) < 1e-12
    for rows in policies:
        assert len(rows) == 169
        for row in rows:
            assert len(row) == 4 and all(math.isfinite(x) and 0 <= x <= 1 for x in row)
            assert abs(math.fsum(row)-1) < 1e-12
    complete = average(policies, list(range(78)))
    error = max(abs(a-b) for p,q in zip(complete,expected,strict=True) for a,b in zip(p,q,strict=True))
    assert error < 1e-12, 'Saved played average differs from evaluated bank'
    windows = [average(policies, list(range(a,b))) for a,b in ((0,26),(26,52),(52,78))]
    steps = [dict(generation=g,weighted_policy_step_tv=tv(policies[g-1],policies[g],mass),
        cumulative_average_tv_to_complete=tv(average(policies,list(range(g))),complete,mass)) for g in range(1,79)]
    return dict(played_average_max_error=error,first_middle_window_tv=tv(windows[0],windows[1],mass),
        middle_last_window_tv=tv(windows[1],windows[2],mass),
        final_current_vs_played_average_tv=tv(policies[78],complete,mass),
        mean_step_tv_last_26=math.fsum(r['weighted_policy_step_tv'] for r in steps[52:])/26,
        played_action_frequencies=[math.fsum(w*p[a] for w,p in zip(mass,complete)) for a in range(4)],
        updates=steps,windows=windows,
        classes=[dict(native_class_index=c,entry_mass=mass[c],played_probabilities=complete[c],
            first_middle_window_tv=tv([windows[0][c]],[windows[1][c]],[1.]),
            middle_last_window_tv=tv([windows[1][c]],[windows[2][c]],[1.]),
            final_current_vs_played_average_tv=tv([policies[78][c]],[complete[c]],[1.])) for c in range(169)])


def controls():
    mass=[1/169]*169
    uniform=[[.25]*4 for _ in range(169)]
    policies=[[[.25]*4 for _ in range(169)] for _ in range(79)]
    policies[78]=[[0.,0.,0.,1.] for _ in range(169)]
    result=summarize(policies,mass,uniform)
    assert abs(result['final_current_vs_played_average_tv']-.75)<1e-12
    assert result['middle_last_window_tv']==0
    assert scalar_policy([[-2.,-1.,-1.,-3.]]*169,1,uniform)[0]==[0.,1.,0.,0.]
    assert scalar_policy([[1.,3.,-1.,0.]]*169,1,uniform)[0]==[.25,.75,0.,0.]
    assert scalar_policy([[0.]*4]*169,0,uniform)==uniform
    policies=[[[1.,0.,0.,0.] if g<39 else [0.,1.,0.,0.] for _ in range(169)] for g in range(79)]
    expected=[[780/3081,2301/3081,0.,0.] for _ in range(169)]
    result=summarize(policies,mass,expected)
    assert abs(result['windows'][1][0][1]-598/1027)<1e-12
    for broken in ('endpoint_in_average','malformed_policy'):
        try:
            if broken=='endpoint_in_average': summarize(policies,mass,[[0.,1.,0.,0.]]*169)
            else:
                bad=[[[.25]*4 for _ in range(169)] for _ in range(79)];bad[5][2][0]=.5
                summarize(bad,mass,uniform)
        except AssertionError: pass
        else: raise AssertionError('Failed to reject '+broken)
    return dict(passed=True,source_sha256=sha(Path(__file__)),
        checks=['unplayed_endpoint_excluded','original_generation_weighting','window_weights',
                'deterministic_negative_tie','positive_regret_mixture','initial_fallback',
                'wrong_average_rejected','malformed_policy_rejected'],new_deals=0,gpu_used=False)


def inspect(job):
    identity, expected, mass, source, catalog_source, matrix_path, objects = job
    start=time.monotonic();inputs={}
    def guard():
        assert time.monotonic()-start<1500 and psutil.virtual_memory().available>24_000_000_000
    def object_read(reference):
        path=Path(objects)/reference['file']
        assert path.resolve().parent==Path(objects).resolve()
        raw=path.read_bytes();assert hashlib.sha256(raw).hexdigest()==reference['sha256']
        inputs[str(path)]=reference['sha256'];return json.loads(raw)
    checkpoint=object_read(identity['checkpoint'])
    assert checkpoint['completed_iterations']==78 and checkpoint['played_bank']==identity['model_references']
    assert checkpoint['next_model']==identity['unplayed_excluded']
    cfg=identity['root_config']
    assert cfg==checkpoint['config']['board_root'] and cfg['boards_per_generation']==4 and cfg['physical_budget']==512
    assert max(abs(x-y) for x,y in zip(cfg['entry_mass'],mass,strict=True))<1e-12
    catalog=json.loads(catalog_source)
    root_obs={r['hand_class']:r['observation'] for r in catalog['native_observations'] if r['player']==0}
    assert set(root_obs)==set(range(169)) and all(not o['own_history'] for o in root_obs.values())
    args=dict(catalog_source=catalog_source,matrix_sha256=sha(matrix_path),
              entry_mass=AllinMatrix(read(matrix_path),source).btn_mass,root_config=cfg)
    policies=[];regrets=[];worst=0.;previous_history=[]
    for g,ref in enumerate([*identity['model_references'],identity['unplayed_excluded']]):
        guard();doc=object_read(ref)
        assert doc['generation']==ref['generation']==g and doc['policy_type']=='board-root-stratified-postflop-poker-v1'
        root=BoardRootRegrets.restore(doc['board_root_state'],expected_config=cfg)
        assert root.steps==g and root.history[:len(previous_history)]==previous_history
        previous_history=root.history
        if g==0:
            fallback,_=probabilities(dict(context_source=source,observations=[root_obs[c] for c in range(169)]),
                                     doc,device='cpu',**args)
        direct=root.probabilities(fallback)
        scalar=scalar_policy(root.regrets.tolist(),g,fallback.tolist())
        error=max(abs(a-b) for p,q in zip(scalar,direct) for a,b in zip(p,q))
        worst=max(worst,error);assert error<1e-12
        policies.append(scalar);regrets.append(root.regrets.tolist())
    return dict(arm=identity['arm'],inputs=inputs,seconds=time.monotonic()-start,
        maximum_scalar_runtime_error=worst,policies_by_generation=policies,
        regrets_by_generation=regrets,board_draws=312,**summarize(policies,mass,expected))


def main(mode):
    if mode=='control':
        result=controls();publish(OUT/f'{PREFIX}-control.json',result);print(json.dumps(result));return
    assert mode=='run'
    started=time.monotonic();inputs={}
    def bound(path):
        inputs[str(path)]=sha(path);return read(path)
    assert safe_read_only_resources() and psutil.cpu_percent(interval=1)<60
    def guard():
        assert time.monotonic()-started<1800 and safe_read_only_resources()
    control=bound(OUT/f'{PREFIX}-control.json')
    assert control['passed'] and control['source_sha256']==sha(Path(__file__))
    evaluation=bound(OUT/'weighted-complete-board-root-study-v1-result.json')
    review=bound(OUT/'weighted-complete-board-root-study-v1-independent-review.json')
    assert evaluation['passed'] and evaluation['complete'] and review['passed']
    assert review['source_result_sha256']==sha(OUT/'weighted-complete-board-root-study-v1-result.json')
    store=Path(evaluation['store']);identities=bound(store/'bank-identities.json');roots=bound(store/'root-stability.json')
    assert sha(store/'bank-identities.json')==evaluation['bank_identities_sha256']
    assert sha(store/'root-stability.json')==evaluation['root_stability_sha256']
    old=bound(OUT/'weighted-root-trajectory-v1-result.json');oldreg=bound(OUT/'weighted-root-trajectory-v1-registration.json')
    assert old['passed'] and old['registration_sha256']==sha(OUT/'weighted-root-trajectory-v1-registration.json')
    for path,h in oldreg['inputs'].items(): guard();assert sha(Path(path))==h,path
    oldeval=bound(OUT/'weighted-complete-evaluation-control-v1-result.json');oldstore=Path(oldeval['store'])
    oldids=bound(oldstore/'bank-identities.json');oldroots=bound(oldstore/'root-stability.json')
    assert sha(oldstore/'bank-identities.json')==oldeval['bank_identities_sha256']
    assert sha(oldstore/'root-stability.json')==oldeval['root_stability_sha256']
    historical=[]
    for here,there in ((0,1),(2,3)):
        assert identities[here]['arm']==oldids[there]['arm']==old['findings'][there]['arm']
        assert identities[here]['model_references']==oldids[there]['model_references']
        assert roots['entry_masses']==oldroots['entry_masses']
        assert max(abs(x-y) for p,q in zip(roots['root_probabilities'][here],oldroots['root_probabilities'][there]) for x,y in zip(p,q))<1e-12
        historical.append(old['findings'][there])
    context_path=OUT/'bb-context-candidate.json';source=context_path.read_text();inputs[str(context_path)]=sha(context_path)
    catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    catalog_source=catalog_path.read_text();inputs[str(catalog_path)]=sha(catalog_path)
    matrix_path=OUT/'preflop-allin-matrix-control-v1-matrix.json';bound(matrix_path)
    plan=OUT/'BOARD-ROOT-TRAJECTORY-FOLLOWUP-PLAN.md';inputs[str(plan)]=sha(plan)
    for path in Path(__file__).parent.glob('*.py'):inputs[str(path)]=sha(path)
    registration=OUT/f'{PREFIX}-registration.json'
    publish(registration,dict(inputs=inputs,workers=2,maximum_seconds=1800,maximum_output_bytes=32_000_000,
        new_deals=0,gpu_used=False,post_result_exploratory=True,windows=[[0,26],[26,52],[52,78]],
        models='All saved states 0-78; evaluated average uses played states 0-77 only.'))
    jobs=[(identities[i],roots['root_probabilities'][i],roots['entry_masses'],source,catalog_source,matrix_path,
          str(Path('S:/GTOpen-research/board-root-matched-prefix-v1')/identities[i]['arm']/'objects')) for i in (1,3)]
    pool=concurrent.futures.ProcessPoolExecutor(max_workers=2,mp_context=multiprocessing.get_context('spawn'))
    try:
        futures=[pool.submit(inspect,j) for j in jobs];candidates=[]
        for future in futures:
            while True:
                guard()
                try:candidates.append(future.result(timeout=5));break
                except concurrent.futures.TimeoutError:pass
    except BaseException:
        for process in list(pool._processes.values()):
            if process.is_alive():process.terminate()
        raise
    finally:pool.shutdown(wait=True,cancel_futures=True)
    a,b=[r['policies_by_generation'] for r in candidates];mass=roots['entry_masses']
    cross=dict(played_prefixes=[dict(played_generations=n,weighted_tv=tv(average(a,list(range(n))),average(b,list(range(n))),mass)) for n in range(1,79)],
        windows=[dict(generations=[lo,hi-1],weighted_tv=tv(average(a,list(range(lo,hi))),average(b,list(range(lo,hi))),mass)) for lo,hi in ((0,26),(26,52),(52,78))])
    assert abs(cross['played_prefixes'][-1]['weighted_tv']-roots['comparisons']['candidate_cross_seed']['entry_weighted_total_variation'])<1e-12
    for path,h in inputs.items():guard();assert sha(Path(path))==h,path
    for candidate in candidates:
        for path,h in candidate['inputs'].items():guard();assert sha(Path(path))==h,path
    destination=OUT/f'{PREFIX}-result.json'
    publish(destination,dict(passed=True,registration_sha256=sha(registration),historical_controls=historical,
        candidates=candidates,candidate_cross_seed_trajectory=cross,seconds=time.monotonic()-started,
        gpu_used=False,new_deals=0,production_modified=False,accuracy_qualified=False,
        interpretation_pending=True,unplayed_generation_78_diagnostic_only=True))
    print(json.dumps(dict(passed=True,result=str(destination),seconds=time.monotonic()-started,
                         all_generations=79,all_classes=169,interpretation_pending=True)),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['control','run'])
    main(parser.parse_args().mode)
