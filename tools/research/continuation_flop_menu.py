"""N21 fixed-model, paired nested-flop-menu validation. No fitting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import collections
import copy
import datetime as dt
import hashlib
import importlib.util
import msvcrt
import sys
from pathlib import Path
from types import SimpleNamespace
import numpy as np
import continuation_policy_transfer_optimized as transfer
import continuation_prediction_bounds as bounds

study=transfer.study
BASE=transfer.original.BASE
OUT=BASE/'flop-menu-20260916'
SOURCE=transfer.OUT/'N20'


def board_sample(fixtures,excluded):
    groups=collections.defaultdict(list)
    for board,iso in fixtures:
        if board in excluded:continue
        cards=[board[i:i+2] for i in range(0,6,2)]
        key=('paired' if len({c[0] for c in cards})<3 else 'unpaired')+'/'+str(len({c[1] for c in cards}))+'suits'
        groups[key].append((board,iso))
    assert len(groups)==5
    rows=[]
    for key,items in sorted(groups.items()):
        assert len(items)>=4
        items.sort(key=lambda b:hashlib.sha256(('flop-menu-20260916-N21'+b[0]).encode()).digest())
        rows += [dict(board=b,iso_weight=i,stratum=key,inclusion_probability=4/len(items)) for b,i in items[:4]]
    assert len(rows)==len({r['board'] for r in rows})==20
    return rows


def config(case,board,menu):
    assert menu in ['control','expanded']
    size={'bet':[{'PotPct':50}],'donk':[{'PotPct':50}],'raise':[{'PotPct':100}]}
    streets=[copy.deepcopy(size) for _ in range(3)]
    if menu=='expanded':
        for action in ['bet','donk']:streets[0][action]=[{'PotPct':p} for p in [33,50,75]]
    return dict(board=board,range_oop=case['range_oop'],range_ip=case['range_ip'],tree=dict(
        starting_pot=case['pot'],effective_stack=case['stack'],rake_pct=0,rake_cap=0,
        oop=copy.deepcopy(streets),ip=copy.deepcopy(streets),max_raises=1,add_allin=False,allin_threshold=.85))


def gate(rows):
    assert len(rows)==8 and len({r['case'] for r in rows})==8
    return all(np.isfinite([r['mae_pct_pot']['candidate'],r['mae_pct_pot']['balanced'],r['regression_vs_previous']]).all()
        and r['mae_pct_pot']['candidate']<=.85*r['mae_pct_pot']['balanced'] and r['regression_vs_previous']<=.1 for r in rows)


def idle():
    transfer.adapter().require_idle()
    for p in transfer.original.queue.processes():
        command=(p['CommandLine'] or '').lower()
        if p['ProcessId']!=os.getpid() and p['Name'].lower() in ['python.exe','pythonw.exe']:
            assert not any(t in command for t in ['continuation_full_precision.py run','continuation_policy_stability.py run',
                'continuation_flop_menu.py run','continuation_qualified_gpu_queue.py']), 'Another research controller owns the GPU'


def adapter():
    spec=importlib.util.spec_from_file_location('_flop_menu_reference',transfer.original.bridge.__file__)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    module.OUT=OUT;module.other_research=lambda:(idle() or [])
    return module


def prepare():
    transfer.selection('N20')
    if (OUT/'prospective/manifest.json').exists():return adapter().checked('prospective')
    assert not list((OUT/'prospective/jobs').glob('*.json'))
    source=transfer.adapter().adapter(SOURCE).checked('prospective')
    assert len(source['cases'])==4
    fixtures=study.pilot.AUDIT/'fixtures.json'
    hashes=dict(source['inputs'])
    excluded=set()
    paths=list(BASE.rglob('manifest.json'))+[study.pilot.OUT/'manifest.json',study.pilot.AUDIT/'manifest.json',study.pilot.AUDIT/'extension/manifest.json']
    for path in sorted(set(paths)):
        if OUT in path.parents:continue
        m=study.read(path)
        excluded.update(b['board'] for b in m.get('boards',[]) if isinstance(b,dict) and 'board' in b)
        excluded.update(j['board'] for j in m.get('jobs',[]) if 'board' in j)
        hashes[str(path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
    for path in [Path(__file__),OUT/'README.md',fixtures,SOURCE/'candidate.json',SOURCE/'candidate-freeze.json',
                 study.ROOT/'tools/research/continuation_prediction_bounds.py',
                 study.ROOT/'tools/research/continuation_nonlinear_residual.py']:
        hashes[str(path.resolve().relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
    boards=board_sample(study.read(fixtures)['canonical_flops'],excluded)
    cases=[];jobs=[]
    for original in source['cases']:
        for menu in ['control','expanded']:
            c=dict(copy.deepcopy(original),id=original['id']+'-'+menu,family=menu,source_case=original['id'],menu=menu)
            cases.append(c)
    for b in boards:
        for c in cases:jobs.append(dict(**b,case=c['id'],id=c['id']+'-'+b['board'],config=config(c,b['board'],c['menu'])))
    manifest=study.signed(dict(cases=cases,boards=boards,jobs=jobs,partition='prospective',inputs=hashes,
        binary_path=source['binary_path'],binary_sha256=source['binary_sha256'],target_gap_pct=.1,max_iterations=2000,
        protocol='N21 README.md; unchanged predictor, paired nested flop menus, all eight context/menu combinations must pass.'))
    study.freeze(OUT/'candidate.json',study.read(SOURCE/'candidate.json'))
    study.freeze(OUT/'prospective/manifest.json',manifest)
    study.freeze(OUT/'candidate-freeze.json',dict(sha256=study.pilot.sha(OUT/'candidate.json'),
        frozen_at=study.night.now(),evaluation_manifest_id=manifest['id'],references_at_freeze=0,production_enabled=False))
    return manifest


def evaluate():
    runner=adapter();m=runner.checked('prospective');contexts=runner.contexts('prospective')
    frozen=study.read(OUT/'candidate-freeze.json');sha=study.pilot.sha(OUT/'candidate.json')
    assert frozen['references_at_freeze']==0 and frozen['evaluation_manifest_id']==m['id'] and frozen['sha256']==sha
    stamp=dt.datetime.fromisoformat(frozen['frozen_at']).timestamp();hashes={}
    for job in m['jobs']:
        path=OUT/'prospective/jobs'/f"{job['id']}.json"
        assert path.stat().st_mtime>=stamp
        hashes[str(path.relative_to(study.ROOT)).replace('\\','/')]=study.pilot.sha(path)
    assert len(hashes)==160
    runner.contexts=lambda partition:contexts
    runner.study=SimpleNamespace(**study.__dict__);runner.study.fit=SimpleNamespace(**study.fit.__dict__)
    previous=study.fit.predict
    runner.study.fit.predict=lambda c,model:bounds.shrunk.network.predict(c,model) if model.get('kind')=='shrunk_nonlinear_residual' else previous(c,model)
    runner.study.night=SimpleNamespace(**study.night.__dict__)
    def write(path,value):
        if path.name=='evaluation.json':
            value['accuracy_screen_passed']=gate(value['cases'])
            value['caveat']='Fixed-model sensitivity to nested flop menus on20 fresh matched boards. No fitting, untouched-context or full-game convergence claim.'
        study.night.dump(path,value)
    runner.study.night.dump=write
    result=runner.evaluate()
    model=study.read(OUT/'candidate.json')
    physical=[bounds.inspect(c,bounds.shrunk.network.predict(c,model)) for c in contexts]
    changes=[]
    for source in sorted({c['case']['source_case'] for c in contexts}):
        a,b=[next(c for c in contexts if c['case']['source_case']==source and c['case']['menu']==menu) for menu in ['control','expanded']]
        np.testing.assert_array_equal(a['mass'],b['mass'])
        w=a['mass']*((a['observed']>0)&(b['observed']>0));w/=w.sum()
        changes.append(dict(source_case=source,weighted_absolute_reference_change_pct_pot=float((w*np.abs(a['residual']-b['residual'])).sum()*100)))
    study.night.dump(OUT/'reference-audit.json',dict(checked_at=study.night.now(),audited_references=len(hashes),
        reference_hashes=hashes,all_references_after_freeze=True,physical_predictions=physical,
        physical_bounds_passed=all(r['passed'] for r in physical),menu_reference_changes=changes,
        candidate_sha256=sha,manifest_id=m['id'],production_enabled=False))
    return result


def run():
    idle()
    assert study.read(SOURCE/'evaluation.json')['accuracy_screen_passed']
    audit=study.read(SOURCE/'reference-audit.json')
    assert audit['audited_references']==200 and audit['physical_bounds_passed']
    assert study.read(BASE/'full-precision-20260916/status.json')['stage']=='checks_complete'
    if not list((OUT/'prospective/jobs').glob('*.json')):
        assert (transfer.original.bridge.DEADLINE-dt.datetime.now(dt.timezone.utc)).total_seconds()>=5400
    OUT.mkdir(parents=True,exist_ok=True)
    with (OUT/'run.lock').open('a+b') as lock:
        lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
        try:
            prepare();adapter().run_partition('prospective');r=evaluate()
            study.night.dump(OUT/'status.json',dict(stage='complete',accuracy_screen_passed=r['accuracy_screen_passed'],production_enabled=False,updated=study.night.now()))
        finally:
            lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_UNLCK,1)


if __name__=='__main__':{'prepare':prepare,'run':run,'evaluate':evaluate}[sys.argv[1]]()
