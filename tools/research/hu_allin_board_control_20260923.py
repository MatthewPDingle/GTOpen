"""Bounded CPU correctness/noise control for conditional preflop all-in labels.

Old fixed private-card fixture, exhaustive remaining boards, and predeclared
Monte Carlo prefixes. No learned policies, fresh strength test or training edits.
"""
import hashlib
import json
import math
from pathlib import Path
import subprocess
import time
import numpy as np
import psutil
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from hu_sampled_physical_dense_btn_jam_diagnosis_20260923 import showdown

OUT = ROOT/'research/preflop-evolution/blind-defense-20260922'
PREFIX = 'sampled-physical-allin-board-control-v1'
STORE = Path('S:/GTOpen-research')/PREFIX


def permute(c): return 4*(c//4)+(c%4+1)%4


def main():
    started = time.monotonic()
    def guard():
        assert idle() and time.monotonic()-started < 900
        assert psutil.virtual_memory().available >= 20_000_000_000
        assert psutil.disk_usage(str(STORE.parent)).free >= 40_000_000_000
    guard()
    parentpath = OUT/'sampled-physical-hybrid-gpu-control-v1-registration.json'
    parent = json.loads(parentpath.read_text())
    fixturepath = Path(parent['query_fixture']); fixture = json.loads(fixturepath.read_text())
    assert sha(fixturepath)==parent['inputs'][str(fixturepath)]
    old_deals = json.loads(fixture['batch_source'])['deals']; assert len(old_deals)==16
    exe = ROOT/'target/release/examples/hu_allin_board_reference.exe'
    paths = [Path(__file__),parentpath,fixturepath,exe,ROOT/'Cargo.lock',
        ROOT/'crates/solver/examples/hu_allin_board_reference.rs',ROOT/'crates/solver/src/evaluator.rs',
        ROOT/'tools/research/hu_sampled_physical_dense_btn_jam_diagnosis_20260923.py']
    registration = dict(inputs={str(p):sha(p) for p in paths},fixture_cases=16,
        replicates=32,largest_prefix=1024,prefixes=[1,16,64,256,1024],seed_base=93101,
        extra_controls=['swap players in first case','permute suits in first case','AA versus AA symmetry'],
        numpy_version=np.__version__,sampling='Independent PCG64 draws of five distinct cards from the 48-card remaining deck; each board is sorted. Replicate prefixes are shared, not independent comparisons.',
        scope='Conditional preflop all-in equity on 16 existing private-card fixtures. Exact enumeration provides the reference; Monte Carlo prefixes measure board-sampling error and cost on this fixture only. No policy optimization, solver performance claim, or poker-strength qualification.',
        maximum_seconds=900,production_modified=False)
    regpath = OUT/f'{PREFIX}-registration.json'; save(regpath,registration)
    assert not STORE.exists(); STORE.mkdir(); cases = []
    for i,deal in enumerate(old_deals):
        hole = deal[:4]; deck = [c for c in range(52) if c not in hole]
        rng = np.random.Generator(np.random.PCG64(registration['seed_base']+i))
        boards = [sorted(rng.choice(deck,5,replace=False).tolist()) for _ in range(32*1024)]
        cases.append(dict(private_cards=hole,sampled_boards=boards))
    first = cases[0]
    cases.append(dict(private_cards=first['private_cards'][2:]+first['private_cards'][:2],sampled_boards=first['sampled_boards']))
    cases.append(dict(private_cards=list(map(permute,first['private_cards'])),
        sampled_boards=[sorted(map(permute,b)) for b in first['sampled_boards']]))
    same_hole = [48,49,50,51]
    rng = np.random.Generator(np.random.PCG64(93119)); deck = list(range(48))
    cases.append(dict(private_cards=same_hole,sampled_boards=[sorted(rng.choice(deck,5,replace=False).tolist()) for _ in range(32*1024)]))
    inputpath = STORE/'input.json'; nativepath = STORE/'native.json'
    save(inputpath,dict(format=1,cases=cases)); child = None; error = None
    try:
        guard()
        with (STORE/'native.log').open('x') as log:
            child = subprocess.Popen([str(exe),str(inputpath),str(nativepath)],cwd=ROOT,
                stdout=log,stderr=subprocess.STDOUT,creationflags=subprocess.CREATE_NO_WINDOW)
            while child.poll() is None:
                time.sleep(2); guard()
        assert child.returncode==0, f'Native reference failed: {child.returncode}'
        native = json.loads(nativepath.read_text()); assert len(native)==19
        for i,row in enumerate(native):
            guard(); assert row['private_cards']==cases[i]['private_cards']
            assert row['exact_boards']==row['wins']+row['ties']+row['losses']==math.comb(48,5)
            assert row['equity']==(row['wins']+.5*row['ties'])/row['exact_boards']
            assert len(row['sampled_scores'])==32*1024 and set(row['sampled_scores']) <= {0,1,2}
            for j in range(64):
                winner = showdown(cases[i]['private_cards']+cases[i]['sampled_boards'][j])
                expected = 1 if winner<0 else 2 if winner==0 else 0
                assert row['sampled_scores'][j]==expected,(i,j)
        a,b,c,sym = native[0],native[16],native[17],native[18]
        assert (a['wins'],a['ties'],a['losses'])==(b['losses'],b['ties'],b['wins'])
        assert (a['wins'],a['ties'],a['losses'])==(c['wins'],c['ties'],c['losses'])
        assert all(x+y==2 for x,y in zip(a['sampled_scores'],b['sampled_scores']))
        assert a['sampled_scores']==c['sampled_scores']
        assert sym['wins']==sym['losses'] and sym['equity']==.5
        rows = []
        exact_variances = [(r['wins']+.25*r['ties'])/r['exact_boards']-r['equity']**2 for r in native[:16]]
        for count in registration['prefixes']:
            errors = []
            for row in native[:16]:
                values = np.asarray(row['sampled_scores'],dtype=float).reshape(32,1024)/2
                errors.extend((values[:,:count].mean(axis=1)-row['equity']).tolist())
            mse = math.fsum(e*e for e in errors)/len(errors)
            rows.append(dict(boards_per_label=count,replicate_labels=len(errors),
                rms_equity_error=math.sqrt(mse),mean_equity_error=math.fsum(errors)/len(errors),
                rms_200bb_call_value_error=398.5*math.sqrt(mse),
                theoretical_fixture_rms_equity_error=math.sqrt(math.fsum(exact_variances)/16/count)))
        for p,h in registration['inputs'].items(): assert sha(p)==h,p
        guard()
        result = dict(passed=True,registration_sha256=sha(regpath),
            artifacts={str(p):sha(p) for p in [inputpath,nativepath,STORE/'native.log']},
            exact_boards_enumerated=sum(r['exact_boards'] for r in native),
            exact_seconds=sum(r['exact_seconds'] for r in native),
            sampled_boards_evaluated=sum(len(r['sampled_scores']) for r in native),
            sample_seconds=sum(r['sample_seconds'] for r in native),
            independent_hand_enumeration_checks=19*64,player_swap_exact=True,suit_permutation_exact=True,
            symmetric_pair_equity_exact=True,prefix_results=rows,seconds=time.monotonic()-started,
            accuracy_qualified=False,production_modified=False,scope=registration['scope'])
        save(OUT/f'{PREFIX}-result.json',result)
        print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))
    except Exception as exc:
        error = str(exc); raise
    finally:
        if child is not None and child.poll() is None: child.terminate(); child.wait(timeout=20)
        save(OUT/f'{PREFIX}-status.json',dict(state='stopped' if error else 'complete',error=error,
            seconds=time.monotonic()-started,production_modified=False))


if __name__=='__main__': main()
