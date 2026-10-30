"""CPU comparison on eight frozen parent reservoirs; never fits or scores a policy."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import argparse,gc,hashlib,json,sys,time
from pathlib import Path
import numpy as np
import psutil

ROOT=Path('T:/Dev/GTOpen');TOOLS=ROOT/'tools/research'
sys.path.append(str(TOOLS))
from sampled_visible_features_bulk_v1 import features as original
from sampled_visible_features_vector_v1 import features as candidate
from visible_summary_vector_control_v1 import control as synthetic_control
from bounded_parallel_evaluation_archive_v2 import production_available
from board_prefix_publication_v1 import atomic_json

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
NAME='visible-features-vector-control-v1'
REG=OUT/(NAME+'-registration.json');RESULT=OUT/(NAME+'-result.json')
PARENT='river-matched-training-pilot-v1'

def read(path):return json.loads(Path(path).read_bytes())
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def sources():
    rp=OUT/(PARENT+'-registration.json');ep=OUT/(PARENT+'-result.json');vp=OUT/(PARENT+'-independent-review-v2.json')
    reg,result,review=map(read,(rp,ep,vp))
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert review['passed'] and review['source_result_sha256']==sha(ep)
    paths=[rp,ep,vp,Path(__file__),Path(__file__).with_name('visible_summary_vector_v1.py'),
        Path(__file__).with_name('visible_summary_vector_control_v1.py'),Path(__file__).with_name('sampled_visible_features_vector_v1.py'),
        TOOLS/'sampled_visible_features_bulk_v1.py',TOOLS/'sampled_visible_poker_features_v1.py']
    fixtures=[]
    for arm in ('A-baseline','A-river','B-baseline','B-river'):
        folder=Path(reg['store'])/arm;progress=read(folder/'progress.json')
        assert progress['completed']==80
        cp=folder/'objects'/progress['checkpoint']['file'];assert sha(cp)==progress['checkpoint']['sha256']
        state=read(cp);paths.extend((folder/'progress.json',cp))
        for player,ref in enumerate(state['reservoirs']):
            path=folder/'objects'/ref['file'];assert sha(path)==ref['sha256']
            paths.append(path);fixtures.append(dict(arm=arm,player=player,path=str(path),sha256=ref['sha256']))
    return dict(inputs={str(path):sha(path) for path in paths},fixtures=fixtures,
        gpu_used=False,fit_performed=False,new_payoff_test_deals=0,
        reference='sampled_visible_features_bulk_v1.features',candidate='sampled_visible_features_vector_v1.features',
        equality='Exact shape, dtype and float32 bytes for every row of every grouped reservoir',
        maximum_seconds=600,maximum_own_rss_bytes=4_000_000_000,
        timing='One pair per fixture, alternating first implementation; descriptive only.',
        production_modified=False,accuracy_claim=False)

def main(run=False):
    spec=sources()
    if not run:
        print(json.dumps(dict(ready=True,fixtures=len(spec['fixtures']),gpu_used=False,training_modified=False)));return
    assert not REG.exists() and not RESULT.exists()
    assert production_available() and psutil.cpu_percent(interval=1)<55 and psutil.virtual_memory().available>28_000_000_000
    atomic_json(REG,spec);began=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic();assert now-began<600
        if now-last>2:
            assert production_available() and psutil.virtual_memory().available>24_000_000_000
            assert psutil.Process().memory_info().rss<4_000_000_000
            last=now
    synthetic_control();guard();rows=[]
    for index,fixture in enumerate(spec['fixtures']):
        guard();path=Path(fixture['path']);assert sha(path)==fixture['sha256']
        with np.load(path,allow_pickle=False) as data:
            _,first=np.unique(data['keys'],axis=0,return_index=True)
            active=data['active'][first].copy()
        observations=[dict(active_features=row.tolist()) for row in active]
        implementations=(('reference',original),('vector',candidate))
        if index%2:implementations=implementations[::-1]
        arrays={};timings={}
        for label,implementation in implementations:
            guard();start=time.monotonic();arrays[label]=implementation(observations);timings[label]=time.monotonic()-start
        assert arrays['reference'].dtype==arrays['vector'].dtype==np.float32
        assert arrays['reference'].shape==arrays['vector'].shape==(len(active),302)
        assert np.array_equal(arrays['reference'],arrays['vector'])
        assert arrays['reference'].tobytes()==arrays['vector'].tobytes()
        row=dict(arm=fixture['arm'],player=fixture['player'],rows=len(active),exact_features=True,
            reference_seconds=timings['reference'],vector_seconds=timings['vector'],
            observed_ratio=timings['reference']/timings['vector'],first=implementations[0][0])
        rows.append(row);print(json.dumps(row),flush=True)
        del arrays,observations,active,first;gc.collect();guard()
    for path,digest in spec['inputs'].items():assert sha(path)==digest,path
    result=dict(passed=True,registration_sha256=sha(REG),cases=rows,rows=sum(r['rows'] for r in rows),
        seconds=time.monotonic()-began,gpu_used=False,fit_performed=False,new_payoff_test_deals=0,
        exact_features=True,training_modified=False,accuracy_claim=False,
        next_requirement='Separate GPU full-length fitted-network parity and complete-update control after the active matched study; no active-run substitution.')
    atomic_json(RESULT,result)
    print(json.dumps(dict(passed=True,result=str(RESULT),rows=result['rows'])),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--run',action='store_true');main(p.parse_args().run)
