"""Independent scalar label reconstruction; publish fixed arrays for paired fits."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from concurrent.futures import ProcessPoolExecutor
import hashlib
import io
import json
import math
from pathlib import Path
import time
import traceback
import numpy as np
import psutil
from board_river_deal_coverage_common_v1 import ROOT,OUT,LOCK,OTHER,PREFIX,STORE,CONTEXT,read,sha,verify
from board_river_deal_coverage_archive_v1 import read_archive
from board_river_opponent_reach_review_v1 import independent_entry
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available


def check_one(item):
    selected,route=item;case_id=selected['case_id'];mp=STORE/'cases'/(case_id+'.manifest.json')
    assert sha(mp)==route['manifest_sha256'];manifest=read(mp);assert manifest['archive_sha256']==route['archive_sha256']
    values=read_archive(STORE/'cases'/(case_id+'.zip'),manifest)
    record=json.loads(values['record.json']);doc=json.loads(values['export.json']);obs=doc['queries']['observations']
    assert record['case']==selected and record['export_sha256']==hashlib.sha256(values['export.json']).hexdigest()
    assert record['policies_sha256']==hashlib.sha256(values['policies.npz']).hexdigest()
    assert record['registration_sha256']==sha(OUT/(PREFIX+'-collection-registration.json'))
    assert doc['context_source']==CONTEXT.read_text() and doc['request_source'].encode()==values['request.json']
    target=doc['target'];q=target['query_index'];hero=target['actor'];entry=independent_entry();g=doc['geometry']
    assert obs[q]['active_features']==selected['active_features']
    endpoints=(-g['amount_to_call'],(g['pot']-g['amount_to_call']-g['rake'])/2,g['pot']-g['rake'])
    with np.load(io.BytesIO(values['policies.npz']),allow_pickle=False) as z:arrays={k:z[k] for k in z.files}
    maximum=0.;rows=[]
    def close(a,b):
        nonlocal maximum
        if b is None:assert a is None;return
        err=abs(a-b);maximum=max(maximum,err);assert err<1e-9*max(1.,abs(b)),(a,b)
    for bank_index,r in enumerate(record['records']):
        bank=r['bank'];assert bank==('A','B')[bank_index];p=arrays['policy_'+bank]
        assert p.shape==(len(obs),4) and np.isfinite(p).all() and np.all(p>=0)
        assert max(abs(p.sum(1)-1))<1e-12
        for i,o in enumerate(obs):assert not np.any(p[i,o['n']:])
        raw=[];payoffs=[];outcomes=[];own=None
        for pair in doc['pairs']:
            h=o=1.
            for i,a,n in pair['path']:
                assert obs[i]['n']==n and 0<=a<n
                if obs[i]['actor']==hero:h*=float(p[i,a])
                else:o*=float(p[i,a])
            if own is None:own=h
            else:assert own==h
            raw.append(entry[1-hero][tuple(pair['cards'])]*o)
            outcomes.append(pair['outcome_loss_tie_win']);payoffs.append(endpoints[outcomes[-1]])
        total=math.fsum(raw);supported=total>0;hero_entry=entry[hero][tuple(sorted(target['cards'][:2]))]
        conditional=r['conditional'];assert conditional['supported']==supported
        assert conditional['hero_on_path']==(own>0 and hero_entry>0)
        close(conditional['hero_own_likelihood'],own);close(conditional['hero_entry_weight'],hero_entry)
        close(conditional['opponent_posterior_mass'],total);close(r['target_own_reach'],own*3081)
        assert np.max(abs(p[q]-r['original_policy']))<1e-12
        if not supported:
            assert r['labels'] is None and conditional['call_minus_fold_bb'] is None
            rows.append(dict(supported=False,on_path=conditional['hero_on_path'],initial_share=r['initial_share'],original_policy=r['original_policy']))
            continue
        posterior=np.array([m/total for m in raw]);close(float(np.max(abs(posterior-arrays['posterior_'+bank]))),0.)
        delta=math.fsum(m*y for m,y in zip(raw,payoffs))/total
        variance=math.fsum(m*(y-delta)**2 for m,y in zip(raw,payoffs))/total
        close(conditional['call_minus_fold_bb'],delta);close(r['labels']['exact'],delta)
        close(r['labels']['single_sample_variance'],variance);close(r['labels']['mean16_variance'],variance/16)
        ones=[];sixteens=[]
        # Reconstruct the specified seed and draws without the label helper.
        for repeat,sample in enumerate(r['labels']['samples']):
            seed=int.from_bytes(hashlib.sha256(f'9289964|{case_id}|{bank}|{repeat}'.encode()).digest()[:16],'big')
            assert str(seed)==sample['seed'] and sample['repetition']==repeat
            # Sampling uses the saved, hash-checked vector. The independently
            # normalized vector above may differ by last-bit summation order.
            rng=np.random.Generator(np.random.PCG64(seed));draws=rng.choice(990,size=16,replace=True,p=arrays['posterior_'+bank])
            assert draws.tolist()==sample['opponent_indices'] and all(raw[i]>0 for i in draws)
            one=payoffs[draws[0]];sixteen=math.fsum(payoffs[i] for i in draws)/16
            close(sample['one'],one);close(sample['sixteen'],sixteen);ones.append(one);sixteens.append(sixteen)
        rows.append(dict(supported=True,on_path=conditional['hero_on_path'],initial_share=r['initial_share'],
            delta=delta,variance=variance,sample1=ones,sample16=sixteens,original_policy=r['original_policy']))
    return dict(case=selected,rows=rows,maximum_scalar_error=maximum,queries=len(obs))


def main():
    began=time.monotonic();registration=OUT/(PREFIX+'-readback-registration.json');destination=OUT/(PREFIX+'-readback.json')
    assert not registration.exists() and not destination.exists() and not LOCK.exists() and not OTHER.exists();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available() and psutil.virtual_memory().available>24_000_000_000
        result_path=OUT/(PREFIX+'-collection.json');selection_path=OUT/(PREFIX+'-selection.json')
        result=read(result_path);selection=read(selection_path);reg=OUT/(PREFIX+'-collection-registration.json')
        assert result['passed'] and result['complete'] and result['registration_sha256']==sha(reg);verify(read(reg)['inputs'])
        assert list(result['routes'])==[c['case_id'] for c in selection['cases']]
        sources=[Path(__file__),result_path,selection_path,reg,CONTEXT,ROOT/'tools/research/board_river_deal_coverage_archive_v1.py',
            ROOT/'tools/research/board_river_opponent_reach_review_v1.py',ROOT/'tools/research/board_river_deal_coverage_common_v1.py']
        hashes={str(p):sha(p) for p in sources};workers=8 if psutil.cpu_percent(interval=1)<50 else 2
        atomic_json(registration,dict(inputs=hashes,workers=workers,maximum_seconds=600,
            scope='Independent scalar entry, posterior, expectation, variance and seeded-sample readback; native poker outcomes reused.',
            final_evaluation_scored=False))
        checks=[];last=0.
        with ProcessPoolExecutor(max_workers=workers) as pool:
            for checked in pool.map(check_one,((c,result['routes'][c['case_id']]) for c in selection['cases'])):
                assert time.monotonic()-began<600
                if time.monotonic()-last>2:
                    assert production_available() and not OTHER.exists();last=time.monotonic()
                checks.append(checked)
        n=len(checks);assert n==selection['selected_cases']
        arrays=dict(active=np.array([c['case']['active_features'] for c in checks],dtype=np.int16),
            actor=np.array([c['case']['actor'] for c in checks],dtype=np.int8),
            deal=np.array([c['case']['deal_index'] for c in checks],dtype=np.int16),
            evaluation=np.array([c['case']['split']=='evaluation' for c in checks]),
            case_ids=np.array([c['case']['case_id'] for c in checks]),
            arity=np.array([c['case']['n'] for c in checks],dtype=np.int8),
            pot=np.array([c['case']['pot'] for c in checks]),delta=np.full((n,2),np.nan),
            sample1=np.full((n,2,3),np.nan),sample16=np.full((n,2,3),np.nan),variance=np.full((n,2),np.nan),
            supported=np.zeros((n,2),dtype=bool),on_path=np.zeros((n,2),dtype=bool),
            initial_share=np.full((n,2),np.nan),original_policy=np.zeros((n,2,4)))
        for i,check in enumerate(checks):
            for bank,row in enumerate(check['rows']):
                arrays['supported'][i,bank]=row['supported'];arrays['on_path'][i,bank]=row['on_path']
                arrays['initial_share'][i,bank]=np.nan if row['initial_share'] is None else row['initial_share']
                arrays['original_policy'][i,bank]=row['original_policy']
                if row['supported']:
                    for key in ('delta','sample1','sample16','variance'):arrays[key][i,bank]=row[key]
        dataset=STORE/'verified-dataset.npz';assert not dataset.exists()
        with dataset.open('xb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
        with np.load(dataset,allow_pickle=False) as z:
            assert set(z.files)==set(arrays)
            for key in arrays:
                assert np.array_equal(z[key],arrays[key],equal_nan=True) if arrays[key].dtype.kind!='U' else np.array_equal(z[key],arrays[key])
        verify(hashes)
        proof=dict(passed=True,complete=True,registration_sha256=sha(registration),cases=n,dataset=str(dataset),dataset_sha256=sha(dataset),
            rows_by_split=dict(train=int((~arrays['evaluation']).sum()),evaluation=int(arrays['evaluation'].sum())),
            unsupported_by_bank=(~arrays['supported']).sum(0).tolist(),zero_hero_reach_by_bank=(~arrays['on_path']).sum(0).tolist(),
            maximum_scalar_error=max(x['maximum_scalar_error'] for x in checks),observations=sum(x['queries'] for x in checks),
            workers=workers,seconds=time.monotonic()-began,training_started=False,final_evaluation_scored=False,gpu_used=False)
        atomic_json(destination,proof);print(json.dumps(proof),flush=True)
    except Exception as e:
        atomic_json(OUT/(PREFIX+'-readback-failure.json'),dict(error=repr(e),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
