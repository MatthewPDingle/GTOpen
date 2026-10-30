"""Bounded river payoff audit and visible-only uniform-opponent comparison.

No training, hidden-card inputs, final-test scoring, or production changes.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import argparse
import concurrent.futures
import hashlib
import json
import multiprocessing
from pathlib import Path
import subprocess
import time
import traceback
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT, OUT, LOCK, OTHER, inputs, read, sha, verify
from board_later_fit_holdout_data_v1 import prepare
from weighted_reservoir_bulk_load_v1 import load
from sampled_visible_initialization_v1 import fresh_visible_network
from sampled_visible_features_bulk_v1 import features
from sampled_visible_poker_features_v1 import best_visible_rank
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

PREFIX = 'board-river-value-reference-v1'
EXE = ROOT/'target/release/examples/hu_river_value_reference_v1.exe'
CONTEXT = OUT/'bb-context-candidate.json'
POT_LABELS = ('under 10 bb', '10-50 bb', '50-100 bb', '100-200 bb', '200+ bb')
TOLERANCE = 1e-7


class Guard:
    def __init__(self): self.started = time.monotonic(); self.last = 0.
    def __call__(self):
        assert time.monotonic()-self.started < 1800, 'Thirty-minute diagnostic budget reached'
        if time.monotonic()-self.last < 2: return
        assert psutil.virtual_memory().available > 24_000_000_000
        assert production_available() and not OTHER.exists(), 'Another workload has priority'
        assert psutil.disk_usage('S:/').free > 5_000_000_000 and psutil.disk_usage('T:/').free > 1_000_000_000
        self.last = time.monotonic()


def native(mode, argument, rows=None, timeout=60):
    result = subprocess.run([str(EXE), mode, str(argument)],
        input=None if rows is None else json.dumps(rows.tolist() if isinstance(rows, np.ndarray) else rows).encode(),
        capture_output=True, timeout=timeout, creationflags=subprocess.CREATE_NO_WINDOW)
    if result.returncode: raise RuntimeError(result.stderr.decode(errors='replace'))
    return json.loads(result.stdout)


def identity(row):
    return (row['public_id'], row['actor'], row['phase'], tuple(row['history']))


def fixed_inputs():
    source, prepared, hashes = inputs()
    fit_path = OUT/'board-later-public-state-fit-v1-result.json'
    fit_registration = OUT/'board-later-public-state-fit-v1-registration.json'
    fit = read(fit_path); assert fit['passed'] and fit['complete']
    assert fit['registration_sha256'] == sha(fit_registration)
    verify(read(fit_registration)['inputs']); hashes.update(read(fit_registration)['inputs'])
    catalog_path = OUT/'board-later-public-state-catalog-v1.json'
    files = [Path(__file__), EXE, CONTEXT, catalog_path, fit_path, fit_registration,
        OUT/'BOARD-RIVER-REFERENCE-PLAN.md', ROOT/'crates/solver/examples/hu_river_value_reference_v1.rs',
        ROOT/'crates/solver/src/evaluator.rs', ROOT/'crates/solver/src/tree.rs', ROOT/'Cargo.lock',
        ROOT/'tools/research/bounded_parallel_evaluation_archive_v2.py']
    files += [ROOT/'crates/solver/examples/research_sampled'/n for n in ('state.rs','poker_reference_v1.rs','observation_v1.rs')]
    files += [ROOT/'crates/solver/examples/hu_board_hand_ranks_v1.rs',
              ROOT/'target/release/examples/hu_board_hand_ranks_v1.exe']
    for row in fit['datasets']:
        checkpoint = row['arms']['baseline']; assert sha(checkpoint['weights']) == checkpoint['weights_sha256']
        files.append(Path(checkpoint['weights']))
    hashes.update({str(p): sha(p) for p in files})
    return source, prepared, fit, read(catalog_path), hashes


def river_geometry(active, arity, catalog, native_rows):
    """Return exact public amounts and a mask selecting legal river call/fold states."""
    table = {identity(r): r for r in catalog['rows']}
    river = {identity(r): r for r in native_rows}
    expected = {k for k,r in table.items() if r['phase']==3 and r['action_kinds'][:2]==['fold','call']}
    assert set(river) == expected and len(river) == len(native_rows)
    unique, inverse = np.unique(np.column_stack((active[:,14:], arity)), axis=0, return_inverse=True)
    geometry = np.full((len(unique),3), np.nan)
    eligible = np.zeros(len(unique),dtype=bool)
    for i,u in enumerate(unique):
        phase = int(u[1])-135
        if phase != 3: continue
        history = [int(x)-(155+6*j) for j,x in enumerate(u[3:22])]
        assert all(0<=x<=5 for x in history)
        end = next((j for j,v in enumerate(history) if v==0),len(history)); assert not any(history[end:])
        key = (int(u[2])-139,int(u[0])-133,phase,tuple(history[:end]))
        original = table[key]; assert int(u[-1]) == original['legal_actions']
        if key not in river: continue
        r = river[key]; assert r['legal_actions']==original['legal_actions'] and r['call_ends_showdown']
        assert r['fold_index']==0 and r['call_index']==1
        for field in ('pot','amount_to_call','rake_fraction','rake_cap'):
            assert abs(r[field]-original[field])<1e-10
        p,c,rake = r['pot'],r['amount_to_call'],r['rake']
        assert np.allclose(r['endpoints_loss_tie_win'],[-c,(p+c-rake)/2-c,p-rake],rtol=0,atol=1e-9)
        geometry[i] = (p,c,rake); eligible[i] = True
    return eligible[inverse],geometry[inverse]


def visible_cards(active):
    """Only seven visible-card slots; never inspect targets or hidden deal keys."""
    assert active.ndim==2 and active.shape[1]==36 and np.all(active[:,15]==138)
    ranks = active[:,:14:2].astype(int)-np.arange(7)[None,:]*19
    suits = active[:,1:14:2].astype(int)-(np.arange(7)[None,:]*19+14)
    assert np.all((ranks>=0)&(ranks<13)) and np.all((suits>=0)&(suits<4))
    cards = (ranks*4+suits).astype(np.uint8)
    ordered = np.sort(cards,axis=1); assert np.all(np.diff(ordered.astype(int),axis=1)>0)
    cards[:,:2] = np.sort(cards[:,:2],axis=1); cards[:,2:] = np.sort(cards[:,2:],axis=1)
    return cards


def endpoints(geometry):
    p,c,r = geometry.T
    return np.column_stack((-c,(p+c-r)/2-c,p-r))


def endpoint_audit(delta, weights, geometry):
    expected = endpoints(geometry)
    residuals = np.abs(delta[:,None]-expected)
    outcomes = residuals.argmin(axis=1); error = residuals.min(axis=1)
    bins = np.searchsorted([10,50,100,200],geometry[:,0],side='right')
    def summarize(mask):
        n = int(mask.sum()); bad = mask & (error>TOLERANCE)
        return dict(rows=n,source_weight=float(weights[mask].sum()),
            maximum_endpoint_error_bb=float(error[mask].max()) if n else None,
            mismatches=int(bad.sum()),mismatched_source_weight=float(weights[bad].sum()),
            outcomes_loss_tie_win=[dict(rows=int((mask&(outcomes==i)).sum()),
                source_weight=float(weights[mask&(outcomes==i)].sum())) for i in range(3)])
    result = summarize(np.ones(len(delta),dtype=bool))
    result['pots'] = [dict(label=name,**summarize(bins==i)) for i,name in enumerate(POT_LABELS)]
    bad_indices = np.flatnonzero(error>TOLERANCE)
    result['first_mismatches'] = [dict(row=int(i),difference=float(delta[i]),
        endpoints=expected[i].tolist(),error=float(error[i])) for i in bad_indices[:10]]
    return result


def source_data(item, proof, guard):
    guard(); verify(item['inputs'])
    r = load(item['reservoir'],Path(item['context']).read_text(),guard=guard); n = r.size
    assert n==item['retained_examples'] and r.player==item['player']
    assert int(r.iterations[:n].max())==77 and abs(r.deal_weights[:n].sum()-item['retained_weight'])<1e-8
    parts,actual,split = prepare(r.active[:n],r.arity[:n],r.values[:n],r.deal_weights[:n])
    assert actual==proof; scale=parts['train']['scale']; del parts
    return r,split,scale


def one(item, proof, checkpoint, catalog, native_rows):
    began=time.monotonic(); guard=Guard(); r,split,scale=source_data(item,proof,guard); n=r.size
    eligible,geometry=river_geometry(r.active[:n],r.arity[:n],catalog,native_rows)
    audit={}
    for index,name in ((0,'train'),(1,'validation')):
        selected=eligible&(split==index)
        audit[name]=endpoint_audit(r.values[:n][selected,1]-r.values[:n][selected,0],
            r.deal_weights[:n][selected],geometry[selected])
    selected=eligible&(split==1); active=r.active[:n][selected]
    cards=visible_cards(active); guard()
    import torch
    torch.set_num_threads(1); assert not torch.cuda.is_initialized()
    assert sha(checkpoint['weights'])==checkpoint['weights_sha256']
    model=fresh_visible_network(item['fit_seed'])
    model.load_state_dict(torch.load(checkpoint['weights'],weights_only=True,map_location='cpu'))
    x=features([dict(active_features=row.tolist()) for row in active]); predictions=[]
    with torch.no_grad():
        for start in range(0,len(x),8192):
            guard(); scores=model(torch.from_numpy(x[start:start+8192])).numpy().astype(np.float64)
            predictions.append(scale*(scores[:,1]-scores[:,0]))
    verify(item['inputs']); assert sha(checkpoint['weights'])==checkpoint['weights_sha256']
    assert not torch.cuda.is_initialized()
    return dict(dataset=item['name'],audit=audit,cards=cards,geometry=geometry[selected],
        delta=r.values[:n][selected,1]-r.values[:n][selected,0],weights=r.deal_weights[:n][selected],
        network=np.concatenate(predictions),scale=scale,seconds=time.monotonic()-began,
        source_rows=n,eligible_validation_rows=int(selected.sum()),
        excluded_test_rows=int((split==2).sum()),rss_bytes=psutil.Process().memory_info().rss)


def python_counts(cards):
    hole=list(map(int,cards[:2])); board=list(map(int,cards[2:])); known=set(hole+board)
    own=best_visible_rank(hole+board); result=[0,0,0]
    for a in range(52):
        if a in known: continue
        for b in range(a+1,52):
            if b in known: continue
            rank=best_visible_rank([a,b]+board)
            result[0 if own>rank else 1 if own==rank else 2]+=1
    assert sum(result)==990; return result


def qualify(source,prepared,catalog,guard):
    began=time.monotonic(); guard()
    native_proof=native('control',CONTEXT); assert native_proof['passed']
    assert native_proof['known_deal_walk_records']>0 and native_proof['maximum_record_error_bb']<1e-9
    # Royal-flush nuts, royal board, quads, wheel, flush, full house, and mixed examples.
    fixtures=[[48,44,40,36,32,1,6],[1,6,32,36,40,44,48],
        [48,49,50,51,0,13,26],[48,1,4,9,14,19,40],
        [48,28,0,8,16,37,42],[48,49,50,44,45,0,5],
        [48,49,0,13,26,35,40],[2,15,20,29,34,41,48]]
    expected=[python_counts(f) for f in fixtures]
    assert expected[0]==[990,0,0] and expected[1]==[0,990,0]
    # A separate native exporter shares the evaluator, so this is an integration
    # check, not the independent scalar oracle used above.
    for cards,reference in zip(fixtures,expected):
        exported=subprocess.run([str(ROOT/'target/release/examples/hu_board_hand_ranks_v1.exe'),
            *map(str,cards[2:])],capture_output=True,check=True,timeout=15,
            creationflags=subprocess.CREATE_NO_WINDOW)
        ranks=json.loads(exported.stdout)['rows']; assert len(ranks)==1081
        own=next(r['rank'] for r in ranks if sorted(r['hand'])==sorted(cards[:2]))
        actual=[0,0,0]
        for r in ranks:
            if set(r['hand'])&set(cards[:2]):continue
            actual[0 if own>r['rank'] else 1 if own==r['rank'] else 2]+=1
        assert actual==reference
    variants=[]
    for cards in fixtures:
        variants += [cards,[cards[1],cards[0],*cards[:1:-1]],
            [c//4*4+(c%4+1)%4 for c in cards]]
    native_1=native('equities',1,variants); native_16=native('equities',16,variants)
    assert native_1['counts_win_tie_loss']==native_16['counts_win_tie_loss']
    assert native_1['counts_win_tie_loss']==[v for e in expected for v in [e]*3]
    invalid=subprocess.run([str(EXE),'equities','1'],input=b'[[0,0,1,2,3,4,5]]',
        capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW,timeout=15)
    assert invalid.returncode!=0 and b'Overlapping or invalid visible cards' in invalid.stderr
    # Exact weighted arithmetic and corrupt-label detection, separate from real labels.
    geom=np.array([[6.,2.,.4]]*3); delta=np.array([-2.,1.8,5.6]); w=np.array([1.,2.,3.])
    assert endpoint_audit(delta,w,geom)['mismatches']==0
    corrupt=delta.copy(); corrupt[0]+=.01
    assert endpoint_audit(corrupt,w,geom)['mismatches']==1
    assert abs(float(np.dot(w,delta**2)/w.sum())-17.426666666666666)<1e-12
    # Cards-only benchmark; no target prediction or outcome comparison on these rows.
    item=source['datasets'][0]; r,split,_=source_data(item,prepared['datasets'][0]['split'],guard)
    eligible,geometry=river_geometry(r.active[:r.size],r.arity[:r.size],catalog,native_proof['templates'])
    cards=visible_cards(r.active[:r.size][eligible&(split==1)])
    unique=np.unique(cards,axis=0)
    order=sorted(range(len(unique)),key=lambda i:hashlib.sha256(b'river-reference-prefix-v1\0'+unique[i].tobytes()).digest())
    prefix=unique[order[:256]]; assert len(prefix)==256
    guard(); start=time.monotonic(); benchmark=native('equities',16,prefix)
    wall=time.monotonic()-start
    assert all(sum(c)==990 for c in benchmark['counts_win_tie_loss'])
    # The full input cannot exceed all validation rows in the original split.
    maximum_rows=sum(d['split']['splits'][1]['examples'] for d in prepared['datasets'])
    estimated=max(wall,benchmark['seconds'])*maximum_rows/len(prefix)
    assert estimated<900, 'Enumeration estimate exceeds the predeclared diagnostic budget'
    verify(item['inputs'])
    return dict(passed=True,native=native_proof,independent_scalar_fixtures=len(fixtures),
        existing_native_export_fixtures=len(fixtures),
        exact_990_pairs=True,known_nuts_and_board_tie=True,card_order_and_suit_invariance=True,
        parallel_matches_serial=True,overlapping_cards_rejected=True,corrupt_label_rejected=True,
        one_contrast_weight_denominator=True,fixture_counts=expected,
        benchmark=dict(rows=len(prefix),cards_sha256=hashlib.sha256(prefix.tobytes()).hexdigest(),
            native_seconds=benchmark['seconds'],wall_seconds=wall,maximum_validation_rows=maximum_rows,
            conservative_extrapolated_seconds=estimated),heldout_loss_scored=False,
        seconds=time.monotonic()-began)


def prediction_metrics(delta,weights,network,uniform,pots):
    bins=np.searchsorted([10,50,100,200],pots,side='right')
    def summarize(mask):
        mass=float(weights[mask].sum()); energy=float(np.dot(weights[mask],delta[mask]**2))
        predictions={}
        for name,estimate in [('network',network),('uniform_opponent',uniform),('zero',np.zeros_like(delta))]:
            error=float(np.dot(weights[mask],(estimate[mask]-delta[mask])**2))
            predictions[name]=dict(squared_error_bb2=error,mse_bb2=error/mass if mass else None,
                error_relative_to_zero=error/energy if energy else None,
                weighted_mean_prediction_bb=float(np.dot(weights[mask],estimate[mask])/mass) if mass else None)
        return dict(rows=int(mask.sum()),source_weight=mass,target_energy_bb2=energy,
            weighted_mean_observed_difference_bb=float(np.dot(weights[mask],delta[mask])/mass) if mass else None,
            predictions=predictions)
    return dict(all=summarize(np.ones(len(delta),dtype=bool)),
        pots=[dict(label=name,**summarize(bins==i)) for i,name in enumerate(POT_LABELS)])


def main(mode):
    source,prepared,fit,catalog,hashes=fixed_inputs(); guard=Guard()
    if mode=='ready':
        print(json.dumps(dict(ready=True,datasets=4,no_cuda=True,final_test_closed=True))); return
    cp=OUT/(PREFIX+'-control.json'); rp=OUT/(PREFIX+'-registration.json'); destination=OUT/(PREFIX+'-result.json')
    assert not LOCK.exists() and not OTHER.exists(); acquired=False; pool=None
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True; guard(); cpu=psutil.cpu_percent(interval=1); assert cpu<50, 'Yield to competing CPU work'
        if mode=='control':
            assert not cp.exists(); proof=qualify(source,prepared,catalog,guard); verify(hashes)
            atomic_json(cp,dict(**proof,inputs=hashes))
            print(json.dumps({k:v for k,v in proof.items() if k not in ('native','fixture_counts')}),flush=True); return
        qualification=read(cp); assert qualification['passed'] and qualification['inputs']==hashes
        hashes[str(cp)]=sha(cp); assert not rp.exists() and not destination.exists()
        from global_research_inventory_v2 import measure
        inventory=measure(); guard()
        assert sum(r['allocated_file_bytes'] for r in inventory)+100_000_000<800_000_000_000
        registration=dict(inputs=hashes,datasets=source['datasets'],numeric_threads_per_worker=1,preparation_workers=4,
            native_equity_workers=16,native_batch_rows=4096,maximum_seconds=1800,maximum_retained_bytes=100_000_000,
            terminal_endpoint_tolerance_bb=TOLERANCE,endpoint_partitions=['train','validation'],
            comparison_partition='validation',reference='Uniform 990 physically legal opponent pairs, own cards and river only.',
            target='Recorded Call advantage minus Fold advantage; no common state-value or branch offset.',
            estimates=['Original 512-step network contrast restored to bb','Uniform-opponent equity times net matched pot minus incremental call','Zero difference'],
            metric='Original source-weighted squared contrast error / source-weight sum, in bb squared; no arity denominator.',
            mean='Equal-dataset mean, with each dataset and five pot buckets also reported.',
            pot_boundaries_bb=[10,50,100,200],no_training=True,new_deals=0,no_cuda=True,
            final_test_evaluated=False,production_modified=False,accuracy_qualified=False,
            scope='Reused diagnostic validation; uniform opponent omits incoming range and betting selection. No policy adoption.',
            storage_admission=inventory,cpu_admission_percent=cpu,created_unix=time.time(),
            pid=os.getpid(),process_created=psutil.Process().create_time())
        atomic_json(rp,registration)
        pool=concurrent.futures.ProcessPoolExecutor(max_workers=4,mp_context=multiprocessing.get_context('spawn'))
        futures=[]
        for item,prior,fitted in zip(source['datasets'],prepared['datasets'],fit['datasets']):
            assert item['name']==fitted['dataset']
            futures.append(pool.submit(one,item,prior['split'],fitted['arms']['baseline'],catalog,qualification['native']['templates']))
        rows=[]
        for future in futures:
            while True:
                guard()
                try:row=future.result(timeout=2);break
                except concurrent.futures.TimeoutError:pass
            rows.append(row)
            print(json.dumps(dict(dataset=row['dataset'],eligible_validation_rows=row['eligible_validation_rows'],
                mismatches=sum(a['mismatches'] for a in row['audit'].values()),seconds=row['seconds'])),flush=True)
        pool.shutdown(wait=True);pool=None
        if any(a['mismatches'] for row in rows for a in row['audit'].values()):
            atomic_json(OUT/(PREFIX+'-endpoint-failure.json'),dict(registration_sha256=sha(rp),
                datasets=[dict(dataset=r['dataset'],audit=r['audit']) for r in rows],
                passed=False,uniform_comparison_started=False,final_test_evaluated=False))
            raise ValueError('Stored endpoint mismatch; preserve evidence and investigate before comparison')
        all_cards=np.concatenate([r['cards'] for r in rows]); unique,inverse=np.unique(all_cards,axis=0,return_inverse=True)
        counts=[]; native_seconds=0.; start=time.monotonic()
        for at in range(0,len(unique),4096):
            guard(); value=native('equities',16,unique[at:at+4096],timeout=120)
            counts.extend(value['counts_win_tie_loss']); native_seconds+=value['seconds']
        counts=np.asarray(counts,dtype=np.int64); assert counts.shape==(len(unique),3) and np.all(counts.sum(axis=1)==990)
        equity=(counts[:,0]+counts[:,1]/2)/990; expanded=equity[inverse]
        records=[];offset=0
        for row in rows:
            n=len(row['delta']); p,c,rake=row['geometry'].T
            uniform=expanded[offset:offset+n]*(p+c-rake)-c;offset+=n
            metrics=prediction_metrics(row['delta'],row['weights'],row['network'],uniform,p)
            records.append({**{k:row[k] for k in ('dataset','audit','scale','seconds','source_rows','eligible_validation_rows','excluded_test_rows','rss_bytes')},'comparison':metrics})
        assert offset==len(all_cards)
        means={name:float(np.mean([r['comparison']['all']['predictions'][name]['mse_bb2'] for r in records]))
            for name in ('network','uniform_opponent','zero')}
        verify(hashes)
        result=dict(passed=True,complete=True,registration_sha256=sha(rp),datasets=records,
            equal_dataset_mse_bb2=means,uniform_change_from_network_percent=(means['uniform_opponent']/means['network']-1)*100,
            enumeration=dict(validation_rows=len(all_cards),unique_visible_card_sets=len(unique),
                opponent_pairs_per_set=990,total_pair_evaluations=len(unique)*990,native_seconds=native_seconds,
                wall_seconds=time.monotonic()-start,card_sets_sha256=hashlib.sha256(unique.tobytes()).hexdigest(),
                counts_sha256=hashlib.sha256(counts.tobytes()).hexdigest()),
            seconds=time.monotonic()-guard.started,final_test_evaluated=False,no_cuda=True,
            no_training=True,production_modified=False,accuracy_qualified=False)
        assert len(json.dumps(result).encode())+rp.stat().st_size+cp.stat().st_size<100_000_000
        atomic_json(destination,result)
        print(json.dumps(dict(complete=True,result=str(destination),means=means,seconds=result['seconds'])),flush=True)
    except Exception as error:
        failure=OUT/(PREFIX+'-failure.json')
        if not failure.exists():atomic_json(failure,dict(type=type(error).__name__,message=str(error),
            traceback=traceback.format_exc(),registration_exists=rp.exists(),seconds=time.monotonic()-guard.started))
        raise
    finally:
        if pool is not None:
            for p in list(pool._processes.values()):
                if p.is_alive():p.terminate()
            pool.shutdown(wait=True,cancel_futures=True)
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--mode',choices=('ready','control','run'),default='ready')
    main(parser.parse_args().mode)
