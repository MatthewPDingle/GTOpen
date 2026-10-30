"""Exploratory exact-mean showdown controls on completed archived fixed policies."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import hashlib
import json
import subprocess
from pathlib import Path
import time
import numpy as np
import psutil
from archived_evaluation_reader_v1 import ArchivedEvaluationReader
from exact_flop_rank_controls_v1 import crossfit
from showdown_control_reference_v1 import score
EVENTS=('showdown_share_minus_exact_private_pair_mean',)
from hu_frozen_root_precision_20260926 import ROOT,OUT,LOCK,OTHER,sha,read,save,values_from
from hu_frozen_root_action_control_v2_20260926 import cls
from hu_root_retained_storage_admitted_study_20260924 import measure,LIMIT,METADATA_RESERVE
from reboot_research_idle_v1 import idle

EXE=ROOT/'target/release/examples/hu_board_outcomes_v1.exe'
PREFIX='archived-showdown-control-diagnostic-v1'
SOURCE='frozen-root-precision-study-v1'


def main():
    started=time.monotonic();store=Path('S:/GTOpen-research')/PREFIX
    assert idle() and not LOCK.exists() and not OTHER.exists() and not store.exists()
    result_path=OUT/f'{SOURCE}-result.json';reg_path=OUT/f'{SOURCE}-registration.json'
    result=read(result_path);reg=read(reg_path);audit_path=OUT/f'{SOURCE}-aggregate-audit.json';audit=read(audit_path)
    assert read(OUT/f'{SOURCE}-status.json')['state']=='complete' and result['passed']
    assert audit['passed'] and audit['source_result_sha256']==sha(result_path)
    assert result['registration_sha256']==sha(reg_path)
    assert audit['source_readback_sha256']==sha(OUT/f'{SOURCE}-readback.json')
    assert audit['reviewer_sha256']==sha(ROOT/'tools/research/frozen_root_precision_audit_20260926.py')
    for p,h in reg['inputs'].items():assert sha(p)==h,p
    test_path=OUT/'showdown-score-control-v1-result.json';test=read(test_path)
    assert test['passed'] and test['all_native_scores_match_reference']
    for p,h in test['inputs'].items():assert sha(p)==h,p
    paths=[Path(__file__),ROOT/'tools/research/exact_flop_rank_controls_v1.py',result_path,reg_path,audit_path,test_path,
           OUT/'SHOWDOWN-CONTROL-VARIATE-DIAGNOSTIC-PLAN.md',Path(reg['source_result']),EXE,
           ROOT/'tools/research/showdown_control_reference_v1.py',ROOT/'crates/solver/examples/hu_board_outcomes_v1.rs',
           ROOT/'tools/research/archived_evaluation_reader_v1.py',ROOT/'tools/research/sampled_evidence_archive_v1.py',
           ROOT/'tools/research/hu_frozen_root_precision_20260926.py',OUT/'later-action-final-root-stability.json']
    inventory=measure();cap=50_000_000
    assert sum(x['allocated_file_bytes'] for x in inventory)+cap+METADATA_RESERVE<=LIMIT
    admission=dict(inputs={str(p.resolve()):sha(p) for p in paths},store=str(store),output_cap=cap,maximum_seconds=1800,
                   storage_inventory=inventory,exact_features=list(EVENTS),ridge_sum_penalty=1.,minimum_fit_count=20,
                   halves='Original global index parity; fit on opposite half',fresh_deals=False,production_modified=False)
    store.mkdir();save(OUT/f'{PREFIX}-registration.json',admission)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    error=None
    def guard():
        assert idle() and not OTHER.exists() and time.monotonic()-started<1800
        assert psutil.virtual_memory().available>=20_000_000_000
        assert sum(p.stat().st_size for p in store.iterdir() if p.is_file())<=cap
    try:
        guard();v,c=values_from(reg,result['jobs']);assert v.shape==(4,65536,4)
        source=read(reg['source_result']);reader=ArchivedEvaluationReader(source['store'],source['archive_manifest_hashes'],external_files=[],guard=guard)
        deals=[];exact=[];source_hashes={}
        for job in result['jobs']:
            guard();name=job['source'];path=Path(source['store'])/name/'conditional-batch.json'
            raw=reader.read_bytes(path)
            source_hashes[name]=hashlib.sha256(raw).hexdigest();batch=json.loads(raw)
            assert len(batch['deals'])==len(batch['allin_counts'])==32
            for cards,counts in zip(batch['deals'],batch['allin_counts']):
                assert len(cards)==9 and len(set(cards))==9 and cls(cards[:2])==int(c[len(deals)])
                assert counts['private_cards']==cards[:4] and counts['boards']==1712304
                assert all(type(counts[k])==int and counts[k]>=0 for k in ('wins','ties','losses','boards'))
                assert counts['wins']+counts['ties']+counts['losses']==counts['boards']
                deals.append(cards);exact.append((counts['wins']+.5*counts['ties'])/counts['boards'])
            if (job['index']+1)%512==0:print(json.dumps(dict(card_batches=job['index']+1)),flush=True)
        save(store/'cards.json',dict(format=1,deals=deals))
        cp=subprocess.run([str(EXE),str(store/'cards.json'),str(store/'showdown.json')],cwd=ROOT,timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        assert cp.returncode==0,cp.stderr[-1000:]
        native=read(store/'showdown.json');assert native['input_source']==(store/'cards.json').read_text()
        scores=native['twice_bb_share'];assert len(scores)==65536 and all(type(v)==int and 0<=v<=2 for v in scores)
        for i,deal in enumerate(deals):
            if i%512==0:guard()
            assert score(deal)==scores[i]
        x=np.zeros((65536,8));x[:,0]=np.asarray(scores)/2-np.asarray(exact)
        with (store/'exact-equities.npy').open('xb') as f:np.save(f,np.asarray(exact),allow_pickle=False)
        with (store/'centered-features.npy').open('xb') as f:np.save(f,x,allow_pickle=False)
        masses=read(OUT/'later-action-final-root-stability.json')['entry_masses'];banks=[];normal_error=0.
        for b in range(4):
            guard();y=np.stack([v[b,:,1]-v[b,:,0],v[b,:,2]-v[b,:,0],v[b,:,2]-v[b,:,1]],axis=1)
            corrected,beta,counts=crossfit(x,y,c);rows=[];raw_weighted=np.zeros(3);fixed_weighted=np.zeros(3)
            for hand in range(169):
                ids=np.flatnonzero(c==hand);raw_var=y[ids].var(0,ddof=1);fixed_var=corrected[ids].var(0,ddof=1)
                raw_weighted+=masses[hand]*raw_var;fixed_weighted+=masses[hand]*fixed_var
                # Check the fitted normal equations independently of the solver.
                for half in range(2):
                    train=ids[ids%2!=half]
                    if len(train)>=20:
                        xx=x[train]-x[train].mean(0);yy=y[train]-y[train].mean(0)
                        residual=(xx.T@xx+np.eye(8))@beta[hand,half]-xx.T@yy
                        normal_error=max(normal_error,float(np.max(abs(residual))))
                rows.append(dict(hand_class=hand,count=len(ids),entry_mass=masses[hand],
                    original_means=y[ids].mean(0).tolist(),corrected_means=corrected[ids].mean(0).tolist(),
                    original_variances=raw_var.tolist(),corrected_variances=fixed_var.tolist(),
                    variance_ratios=[float(a/z) if z>0 else None for a,z in zip(fixed_var,raw_var)],
                    fit_counts=counts[hand].tolist(),coefficient_norms=[float(np.linalg.norm(k)) for k in beta[hand]]))
            with (store/f'coefficients-{b}.npy').open('xb') as f:np.save(f,beta,allow_pickle=False)
            banks.append(dict(bank=b,classes=rows,weighted_original_variances=raw_weighted.tolist(),
                weighted_corrected_variances=fixed_weighted.tolist(),weighted_variance_ratios=(fixed_weighted/raw_weighted).tolist()))
        assert normal_error<1e-8
        for p,h in admission['inputs'].items():assert sha(p)==h,p
        doc=dict(passed=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),banks=banks,
            feature_sha256=sha(store/'centered-features.npy'),cards_sha256=sha(store/'cards.json'),
            native_sha256=sha(store/'showdown.json'),exact_equity_sha256=sha(store/'exact-equities.npy'),
            all_native_scores_match_reference=True,coefficient_sha256=[sha(store/f'coefficients-{b}.npy') for b in range(4)],
            source_card_artifact_hashes=source_hashes,maximum_normal_equation_error=normal_error,
            seconds=time.monotonic()-started,storage_bytes=sum(p.stat().st_size for p in store.iterdir()),
            exploratory=True,accuracy_qualified=False,production_modified=False,
            limitations='Previously inspected cards and outcomes; full-board showdown control only; descriptive cross-fitted variance only. Corrected observations share fitted coefficients; no independent-sample confidence guarantee. No training improvement or better poker play established.')
        save(OUT/f'{PREFIX}-result.json',doc)
        print(json.dumps(dict(passed=True,weighted_variance_ratios=[b['weighted_variance_ratios'] for b in banks],seconds=doc['seconds'])))
    except BaseException as exc:error=repr(exc);raise
    finally:
        assert LOCK.read_text().strip()==str(os.getpid());LOCK.unlink()
        save(OUT/f'{PREFIX}-status.json',dict(state='failed' if error else 'complete',error=error,seconds=time.monotonic()-started))


if __name__=='__main__':main()
