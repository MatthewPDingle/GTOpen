"""Exact all-in equity cache for the existing 39,936-deal training schedule.

Single CPU worker; no GPU allocation and no alteration of any running trial.
Player roles remain fixed. Only suit permutations and within-hand card order
are quotiented out, preserving physical card compatibility.
"""
import itertools
import json
from pathlib import Path
import subprocess
import time
import uuid
import psutil
from loopback_research_validation import idle
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX='sampled-physical-allin-training-cache-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
PERMUTATIONS=list(itertools.permutations(range(4)))


def canonical(hole):
    assert len(hole)==len(set(hole))==4 and all(type(c) is int and 0<=c<52 for c in hole)
    return min(tuple(sorted(4*(c//4)+p[c%4] for c in hole[:2])+
                     sorted(4*(c//4)+p[c%4] for c in hole[2:])) for p in PERMUTATIONS)


def main():
    started=time.monotonic(); last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        if now-last>=2:
            assert now-started<7200 and idle(), 'Cache deadline or production activity'
            assert psutil.virtual_memory().available>=20_000_000_000
            assert psutil.disk_usage(str(STORE.parent)).free>=40_000_000_000
            last=now
    guard()
    controlpath=OUT/'sampled-physical-allin-board-control-v1-independent-review.json'
    control=json.loads(controlpath.read_text()); assert control['passed']
    for p,h in control['inputs'].items(): assert sha(p)==h,p
    trainpath=OUT/'sampled-physical-dense-pilot-v1-registration.json'; train=json.loads(trainpath.read_text())
    reviewpath=OUT/'sampled-physical-dense-pilot-v1-independent-review.json'; review=json.loads(reviewpath.read_text())
    assert review['passed'] and review['terminal_complete'] and review['completed_iterations']==78
    assert review['source_registration_sha256']==sha(trainpath)
    for p,h in review['evidence_hashes'].items(): assert sha(p)==h,p
    for p,h in train['inputs'].items(): assert sha(ROOT/p)==h,p
    resultpath=OUT/'sampled-physical-dense-pilot-v1-result.json'; training=json.loads(resultpath.read_text())
    contextpath=OUT/'bb-context-candidate.json'; context=contextpath.read_text()
    sampler=PhysicalDeals(context,mode='full_deck',seed=train['config']['sampler_seed'])
    keys=set(); source_batches={}
    for step in training['steps']:
        for part in step['subbatches']:
            guard()
            path=Path(train['store'])/f"iteration-{step['iteration']:04d}"/f"batch-{part['chunk']:02d}"/'batch.json'
            assert sha(path)==part['artifacts']['batch.json']; source_batches[str(path)]=sha(path)
            batch=json.loads(path.read_text()); assert batch['deals']==sampler.sample(64)['deals']
            keys.update(canonical(d[:4]) for d in batch['deals'])
    keys=sorted(keys); assert sampler.draws==39936 and len(keys)==23891
    # Suit relabelings must map to precisely the same role-preserving key.
    for hole in keys[:64]:
        for p in PERMUTATIONS:
            assert canonical([4*(c//4)+p[c%4] for c in hole])==hole
        assert canonical([hole[1],hole[0],hole[3],hole[2]])==hole
    exe=ROOT/'target/release/examples/hu_allin_board_reference.exe'
    paths=[Path(__file__),controlpath,trainpath,reviewpath,resultpath,contextpath,exe,
           ROOT/'crates/solver/examples/hu_allin_board_reference.rs',ROOT/'crates/solver/src/evaluator.rs',
           ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py',
           *map(Path,control['inputs'])]
    registration=dict(inputs={str(p):sha(p) for p in paths},source_batches=source_batches,
        training_deals=39936,unique_role_preserving_suit_keys=len(keys),batch_size=20,
        maximum_seconds=7200,host_reserve_bytes=20_000_000_000,disk_reserve_bytes=40_000_000_000,
        scope='Exact conditional all-in equity for the fixed historical training schedule. Enumerate all 48 choose 5 remaining boards per physical private-card key, modulo suit symmetry and card order within each player. No policy, payoff protocol, current experiment or production changes. This is a future-label cache, not a trained model or convergence result.',
        production_modified=False)
    regpath=OUT/f'{PREFIX}-registration.json'; save(regpath,registration)
    assert not STORE.exists(); STORE.mkdir(); save(STORE/'keys.json',keys)
    records=[]; rows=[]; child=None; error=None; native_seconds=0.
    def status(state):
        path=OUT/f'{PREFIX}-status.json'; temporary=path.with_name(path.name+'.'+uuid.uuid4().hex+'.tmp')
        save(temporary,dict(state=state,error=error,controller_pid=psutil.Process().pid,
            child_pid=child.pid if child is not None and child.poll() is None else None,
            completed_keys=len(rows),total_keys=len(keys),seconds=time.monotonic()-started,
            production_modified=False)); temporary.replace(path)
    try:
        status('running')
        with (STORE/'native.log').open('x') as log:
            for offset in range(0,len(keys),20):
                guard(); folder=STORE/f'batch-{offset:05d}'; folder.mkdir()
                selected=keys[offset:offset+20]
                cases=[dict(private_cards=h,sampled_boards=[[c for c in range(52) if c not in h][:5]]) for h in selected]
                inputpath=folder/'input.json'; nativepath=folder/'native.json'; save(inputpath,dict(format=1,cases=cases))
                child=subprocess.Popen([str(exe),str(inputpath),str(nativepath)],cwd=ROOT,stdout=log,
                    stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
                status('running')
                while child.poll() is None: time.sleep(.25); guard()
                assert child.returncode==0, f'Native cache batch {offset} failed'
                outputs=json.loads(nativepath.read_text()); assert len(outputs)==len(selected)
                for case,native in zip(cases,outputs):
                    assert native['private_cards']==list(case['private_cards'])
                    assert native['wins']+native['ties']+native['losses']==native['exact_boards']==1712304
                    assert native['equity']==(native['wins']+.5*native['ties'])/1712304
                    w=showdown(list(case['private_cards'])+case['sampled_boards'][0])
                    assert native['sampled_scores']==[1 if w<0 else 2 if w==0 else 0]
                    rows.append(dict(private_cards=native['private_cards'],wins=native['wins'],
                        ties=native['ties'],losses=native['losses'],boards=native['exact_boards']))
                    native_seconds+=native['exact_seconds']
                records.append(dict(offset=offset,artifacts={str(p):sha(p) for p in [inputpath,nativepath]}))
                status('running')
                if offset%500==0: print(json.dumps(dict(completed_keys=len(rows),total_keys=len(keys))),flush=True)
        assert [tuple(r['private_cards']) for r in rows]==keys
        cachepath=STORE/'cache.json'; save(cachepath,dict(format=1,player_roles_fixed=True,rows=rows))
        for p,h in registration['inputs'].items(): assert sha(p)==h,p
        for p,h in source_batches.items(): assert sha(p)==h,p
        guard()
        save(OUT/f'{PREFIX}-result.json',dict(passed=True,registration_sha256=sha(regpath),
            keys_artifact=str(STORE/'keys.json'),keys_sha256=sha(STORE/'keys.json'),
            cache_artifact=str(cachepath),cache_sha256=sha(cachepath),batches=records,
            completed_keys=len(rows),training_deals=39936,exact_boards=len(rows)*1712304,
            independent_sampled_winner_checks=len(rows),native_exact_seconds=native_seconds,
            seconds=time.monotonic()-started,production_modified=False,accuracy_qualified=False,
            scope=registration['scope']))
    except Exception as exc:
        error=str(exc); raise
    finally:
        if child is not None and child.poll() is None: child.terminate(); child.wait(timeout=20)
        status('stopped' if error else 'complete')


if __name__=='__main__': main()
