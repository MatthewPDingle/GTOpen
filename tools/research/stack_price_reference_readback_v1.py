"""Verify reference artifacts and exact-rational prices without rerunning workers."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import numpy as np
from stack_price_reference_v1 import call_advantage
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
STORE=Path('S:/GTOpen-research/stack-price-reference-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
RESULT=OUT/'stack-price-reference-control-v1-readback-v1.json'
def read(p): return json.loads(Path(p).read_bytes())
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not RESULT.exists()
    path=OUT/'stack-price-reference-control-v1-result.json';r=read(path)
    rp=OUT/'stack-price-reference-control-v1-registration.json';reg=read(rp)
    assert r['passed'] and r['complete'] and r['registration_sha256']==sha(rp)
    checked={}
    def check(p,h):
        assert sha(p)==h,p
        checked[str(p)]=h
    check(path,sha(path));check(rp,sha(rp))
    for p,h in reg['inputs'].items(): check(p,h)
    for p,h in r['artifacts'].items(): check(p,h)
    pairs=holdings=0
    boards=[]
    for i,row in enumerate(r['boards']):
        board=read(STORE/f'board-{i}-reference.json');native=read(STORE/f'board-{i}-native-counts.json')
        assert row['board']==board['board']==reg['probe_boards'][i]
        assert row['canonical_group']==board['canonical_group']==reg['probe_board_groups'][i]
        assert board['probe_only'] and board['exclude_from_future_fit_and_test']
        assert board['counts_win_tie_loss']==native['counts_win_tie_loss']
        counts=np.asarray(board['counts_win_tie_loss'],dtype=np.int64)
        assert counts.shape==(1081,3) and np.all(counts>=0) and np.all(counts.sum(1)==990)
        assert counts[:,0].sum()==counts[:,2].sum()
        holdings+=len(counts);pairs+=int(counts.sum());boards.append(counts)
    assert holdings==r['independently_ranked_holdings'] and pairs==r['enumerated_directed_private_pairs']
    checks=states=0;maximum=0.;F=lambda x:Fraction(str(x))
    for depth in reg['fitting_depths']:
        public=read(GEOMETRY/f'stack-{depth}-public.json')
        selected=[o for o in public['public_states'] if o['phase']==3 and [a['kind'] for a in o['actions']]==['fold','call']]
        record=next(row for row in r['contexts'] if row['stack']==depth)
        assert len(selected)==record['states'];states+=len(selected)
        for row in selected:
            p,c,rate,cap=(F(row[k]) for k in ('pot','call_cost','rake_fraction','rake_cap'))
            rake=min(cap,rate*(p+c)) if cap else rate*(p+c)
            for counts in boards:
                subset=counts[[0,360,720,1080]]
                actual=call_advantage(subset,row)
                for (w,t,l),value in zip(subset,actual):
                    expected=(Fraction(int(w),990)+Fraction(int(t),1980))*(p+c-rake)-c
                    maximum=max(maximum,abs(float(expected)-value));checks+=1
    assert states==r['native_terminal_states'] and states*12*1081==r['call_values_checked']
    assert maximum<1e-9 and not r['heldout_depth_labels_read'] and not r['training_started']
    assert r['owned_workers']['active_processes']==0
    atomic_json(RESULT,dict(passed=True,source_sha256=sha(__file__),inputs=checked,verified_files=len(checked),
        native_terminal_states=states,independently_ranked_holdings=holdings,enumerated_directed_private_pairs=pairs,
        rational_cashflow_comparisons=checks,maximum_rational_error_bb=float(maximum),
        probe_only=True,heldout_depth_labels_read=False,gpu_used=False,training_started=False,
        full_preflop_accuracy_qualified=False,production_modified=False))
    print(json.dumps({k:v for k,v in read(RESULT).items() if k!='inputs'}),flush=True)

if __name__=='__main__': main()
