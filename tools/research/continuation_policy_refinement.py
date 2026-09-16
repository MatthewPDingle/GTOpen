"""Prospective targeted-data experiment; isolated from the live application."""
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'
import collections
import copy
import hashlib
import json
import msvcrt
import subprocess
import sys
import time

import numpy as np
import continuation_overnight as night
import continuation_overnight_fit as fit
import learned_interface_reference as prior
import range_value_pilot as pilot
from continuation_checkpoint import same_job

ROOT = pilot.ROOT
OUT = ROOT/'research/preflop-evolution/continuation/policy-refinement-20260916'


def read(path):
    return json.loads(path.read_text())


def freeze(path, value):
    if path.exists():
        assert read(path) == value, f'Frozen artifact changed: {path}'
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        night.dump(path, value)


def signed(value):
    return dict(value, id=hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest())


def checked(partition):
    m = read(OUT/partition/'manifest.json')
    assert signed({k:v for k,v in m.items() if k != 'id'}) == m
    for path, digest in m['inputs'].items():
        assert pilot.sha(ROOT/path) == digest, f'Input changed: {path}'
    return m


def prepare():
    old = prior.checked()
    original = night.checked_manifest()
    fixtures = read(night.OUT/'fixtures.json')
    excluded = {j['board'] for j in original['jobs']}
    for directory in [pilot.OUT, pilot.AUDIT, pilot.AUDIT/'extension']:
        excluded.update(b['board'] for b in read(directory/'manifest.json')['boards'])
    groups = collections.defaultdict(list)
    for board, iso in read(pilot.AUDIT/'fixtures.json')['canonical_flops']:
        if board in excluded:
            continue
        cards = [board[i:i+2] for i in range(0,6,2)]
        key = ('paired' if len({c[0] for c in cards}) < 3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    devboards = []
    for key, items in sorted(groups.items()):
        items.sort(key=lambda x:hashlib.sha256(('anchored-interface-20260916'+x[0]).encode()).digest())
        devboards += [dict(board=b, iso_weight=i, stratum=key, inclusion_probability=20/len(items)) for b,i in items[:20]]
    oldboards = {b['board'] for b in old['boards']}
    devset = {b['board'] for b in devboards}
    assert oldboards <= devset and len(devset) == 100
    testboards = []
    for key, items in sorted(groups.items()):
        remaining = [(b,i) for b,i in items if b not in devset]
        remaining.sort(key=lambda x:hashlib.sha256(('policy-refinement-evaluation-20260916'+x[0]).encode()).digest())
        testboards += [dict(board=b, iso_weight=i, stratum=key, inclusion_probability=10/len(remaining)) for b,i in remaining[:10]]
    assert len(testboards) == 50 and not devset.intersection(b['board'] for b in testboards)
    devcases = [dict(c, family='train-eight-straddle', partition='train') for c in old['cases']]
    # Fixed feature-based selection: deepest available straddled held-out case,
    # and deepest BB-as-OOP case in the other held-out family.
    tests = [c for c in fixtures['cases'] if c['id'] in ['test-seven-straddle-00','test-eight-open-01']]
    assert len(tests) == 2
    assert not {c['family'] for c in tests}.intersection(c['family'] for c in fixtures['cases'] if c['partition']=='train')
    inputs = {str(p.relative_to(ROOT)).replace('\\','/'):pilot.sha(p) for p in [
        night.OUT/'candidate.json', night.OUT/'manifest.json', night.OUT/'fixtures.json',
        prior.OUT/'manifest.json', prior.study.OUT/'candidate/iteration-250.json',
        ROOT/'cache/preflop_eq169.bin', ROOT/'cache/realization_fit.json', ROOT/old['binary_path']]}
    protocol = dict(
        hypothesis='Adding two policy-induced blind-call ranges improves the fixed predictor on fresh boards from other source families.',
        development='100 nested boards per case, including 20 already observed. Development results are not independent validation.',
        evaluation='50 disjoint fresh boards per case. Source families excluded from all fitting; case identities were used in historical evaluation, so this is prospective board evaluation rather than pristine new-context validation.',
        selection='test-seven-straddle-00: deepest available held-out straddled case. test-eight-open-01: deepest BB-as-OOP case from the other held-out family. Chosen from input features, not new outcomes.',
        fit=dict(encoder='shape',alpha=.1,original_training_cases=24,added_cases=2,selection='One fixed fit; no hyperparameter search or adjustment after evaluation.'),
        gate='Each evaluation case: at least 15% lower compatible-mass-weighted MAE than original Balanced and no more than 5% greater MAE than the frozen previous candidate. Report paired bootstrap intervals; a point pass alone does not justify deployment.',
        scope='Zero-rake heads-up, fixed 50% bet and 100% raise menu. No live application changes, no full preflop convergence claim.',
        sampling='Five texture strata. Inverse-inclusion and suit-isomorphism weights with legal-pair hand mass. Board pool excludes earlier studies; no claim of an unbiased all-1755-flop estimate.',
        training_uncertainty='Bootstrap intervals condition on fitted models; they do not include training or source-family uncertainty.')
    freeze(OUT/'protocol.json', protocol)
    inputs[str((OUT/'protocol.json').relative_to(ROOT)).replace('\\','/')] = pilot.sha(OUT/'protocol.json')
    for partition, cases, boards in [('development',devcases,devboards),('evaluation',tests,testboards)]:
        jobs = []; reused = []
        for b in boards:
            for c in cases:
                size = {'bet':[{'PotPct':50}],'raise':[{'PotPct':100}],'donk':[{'PotPct':50}]}
                config = dict(board=b['board'],range_oop=c['range_oop'],range_ip=c['range_ip'],tree=dict(
                    starting_pot=c['pot'],effective_stack=c['stack'],rake_pct=0,rake_cap=0,
                    oop=[size]*3,ip=[size]*3,max_raises=1,add_allin=False,allin_threshold=.85))
                j = dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=config)
                if partition=='development' and b['board'] in oldboards:
                    path = prior.OUT/'jobs'/f"{j['id']}.json"
                    r = read(path)
                    assert same_job(r['job']['config'],config) and r['manifest_id']==old['id'] and r['target_met']
                    reused.append(dict(job=j,source=str(path.relative_to(ROOT)).replace('\\','/'),sha256=pilot.sha(path)))
                else:
                    jobs.append(j)
        m = signed(dict(cases=cases,boards=boards,jobs=jobs,reused=reused,inputs=inputs,
            binary_path=old['binary_path'],binary_sha256=old['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
            partition=partition,protocol=protocol))
        freeze(OUT/partition/'manifest.json',m)
    print('Frozen 160 fresh development + 100 fresh evaluation references; 40 prior results reused with new sampling weights.',flush=True)


def contexts(partition):
    m = checked(partition); counts, eq = pilot.matrices(); result = []
    for case in m['cases']:
        rows = []
        for j in m['jobs']:
            if j['case'] != case['id']:
                continue
            r = read(OUT/partition/'jobs'/f"{j['id']}.json")
            assert r['manifest_id']==m['id'] and same_job(r['job'],j) and r['target_met']
            rows.append(r)
        for source in m['reused']:
            if source['job']['case'] != case['id']:
                continue
            path = ROOT/source['source']; assert pilot.sha(path)==source['sha256']
            r = copy.deepcopy(read(path))
            assert same_job(r['job']['config'],source['job']['config']) and r['target_met']
            r['job'] = source['job']  # Derived analysis only; source file stays immutable.
            rows.append(r)
        assert len(rows)==len(m['boards'])
        c = pilot.context(case,counts,eq)
        residual, observed, unadjusted = pilot.aggregate(case,rows)
        c.update(case=case,residual=residual,observed=observed,unadjusted=unadjusted,rows=rows,
                 base_x=c['x'].copy(),base_names=list(c['names']))
        result.append(c)
    return result


def train():
    if (OUT/'candidate-freeze.json').exists():
        assert pilot.sha(OUT/'candidate.json')==read(OUT/'candidate-freeze.json')['sha256']
        return
    assert not list((OUT/'evaluation/jobs').glob('*.json')), 'Evaluation results predate candidate freeze'
    original = fit.load_cases('train'); added = contexts('development')
    assert len(original)==24 and len(added)==2
    cases = original+added
    model = fit.fit(cases,'shape',.1)
    model.update(schema=2,manifest_id=checked('development')['id'],production_enabled=False,
        training_case_ids=[c['case']['id'] for c in cases],training_families=sorted({c['case']['family'] for c in cases}),
        label='One fixed targeted-data revision; compatible-pair weighted policy EV with equity control variate.')
    freeze(OUT/'candidate.json',model)
    freeze(OUT/'candidate-freeze.json',dict(sha256=pilot.sha(OUT/'candidate.json'),frozen_at=night.now(),
        evaluation_manifest_id=checked('evaluation')['id'],evaluation_completed_jobs=0))
    print('Candidate frozen before new evaluation references.',flush=True)


def run_partition(partition):
    m = checked(partition)
    if partition=='evaluation':
        f = read(OUT/'candidate-freeze.json')
        assert f['sha256']==pilot.sha(OUT/'candidate.json') and f['evaluation_manifest_id']==m['id']
    env = dict(os.environ)
    env['PATH'] = str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    directory = OUT/partition
    while True:
        done = [j for j in m['jobs'] if (directory/'jobs'/f"{j['id']}.json").exists()]
        for j in done:
            r = read(directory/'jobs'/f"{j['id']}.json")
            assert r['target_met'] and r['manifest_id']==m['id'] and same_job(r['job'],j)
        night.dump(OUT/'status.json',dict(stage=partition,completed=len(done),total=len(m['jobs']),updated=night.now()))
        if len(done)==len(m['jobs']):
            return
        if night.live_busy():
            night.dump(OUT/'status.json',dict(stage='deferred',partition=partition,completed=len(done),total=len(m['jobs']),reason='Live application busy',updated=night.now()))
            print('Live application busy; safe to resume this checkpoint later.',flush=True)
            raise SystemExit(3)
        with (directory/f'batch-{len(done):03d}.log').open('a') as log:
            subprocess.run([str(ROOT/m['binary_path']),str(directory/'manifest.json'),'4'],cwd=ROOT,env=env,
                stdout=log,stderr=subprocess.STDOUT,check=True)
        print(partition, min(len(done)+4,len(m['jobs'])),'/',len(m['jobs']),flush=True)


def compare(partition):
    cases = contexts(partition)
    old = read(night.OUT/'candidate.json'); model = read(OUT/'candidate.json')
    assert pilot.sha(OUT/'candidate.json')==read(OUT/'candidate-freeze.json')['sha256']
    results = []
    for c in cases:
        pred = fit.predict(c,model); previous = fit.predict(c,old)
        errors = pilot.metrics(c,pred); errors['previous'] = pilot.metrics(c,previous)['candidate']
        boot = fit.bootstrap(c,pred); oldboot = fit.bootstrap(c,previous)
        quality = fit.quality(c); target = c['raw']+c['residual']
        mask = c['observed']>0; weight = c['mass']*mask; weight /= weight.sum()
        hands = []
        for p,h in zip(*np.where(mask)):
            hands.append(dict(position=c['case']['positions'][p],hand=pilot.LABELS[h],mass=float(weight[p,h]),
                reference=float(target[p,h]),balanced=float(c['balanced'][p,h]),previous=float(previous[p,h]),candidate=float(pred[p,h]),
                br_gain_pct_pot=float(quality[p,h]),
                weighted_error_change=float(weight[p,h]*(abs(pred[p,h]-target[p,h])-abs(previous[p,h]-target[p,h])))))
        results.append(dict(case=c['case']['id'],family=c['case']['family'],positions=c['case']['positions'],boards=len(c['rows']),
            spr=c['case']['stack']/c['case']['pot'],mae_pct_pot=errors,
            improvement_vs_balanced=1-errors['candidate']/errors['balanced'],improvement_vs_previous=1-errors['candidate']/errors['previous'],
            paired_90_improvement_ci={name:np.quantile(1-boot['candidate']/base,[.05,.95]).tolist()
                for name,base in [('balanced',boot['balanced']),('previous',oldboot['candidate'])]},
            screen_pass=errors['candidate']<=.85*errors['balanced'] and errors['candidate']<=1.05*errors['previous'],
            candidate_pot_sum=float((pred*c['mass']).sum()),reference_cv_pot_sum=float((target*c['mass']).sum()),
            negative_predictions=[dict(player=int(p),hand=pilot.LABELS[h],value=float(pred[p,h]),mass=float(c['mass'][p,h])) for p,h in zip(*np.where(pred<0))],
            max_reference_gap_pct=max(r['gap_pct'] for r in c['rows']),
            max_gpu_gap_pct=max(r['gpu_gap_pct'] for r in c['rows']),
            max_reference_accounting_error_bb=max(abs(sum(r['means_bb'])-c['case']['pot']) for r in c['rows']),
            probes=[h for h in hands if h['hand'] in night.PROBES],
            largest_regressions=sorted(hands,key=lambda h:h['weighted_error_change'],reverse=True)[:12],
            largest_improvements=sorted(hands,key=lambda h:h['weighted_error_change'])[:12]))
    value = dict(partition=partition,candidate_sha256=pilot.sha(OUT/'candidate.json'),cases=results,
        all_screen_pass=all(r['screen_pass'] for r in results),production_enabled=False,
        caveat='Development cases are in-sample. Evaluation families are excluded from fitting, but case identities were evaluated historically. Bootstrap conditions on the fixed models and does not capture source-family or training uncertainty.')
    night.dump(OUT/f'{partition}-comparison.json',value)
    print(json.dumps([dict(case=r['case'],mae_pct_pot=r['mae_pct_pot'],screen_pass=r['screen_pass']) for r in results]),flush=True)
    return value


def run():
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0); lock.write(b'0'); lock.flush(); lock.seek(0)
        msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            run_partition('development')
            train()
            compare('development')
            run_partition('evaluation')
            result = compare('evaluation')
            night.dump(OUT/'status.json',dict(stage='complete',updated=night.now(),accuracy_screen_passed=result['all_screen_pass'],production_enabled=False))
        finally:
            lock.seek(0); msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':
    {'prepare':prepare,'run':run,'train':train,'compare':lambda:compare(sys.argv[2])}[sys.argv[1]]()
