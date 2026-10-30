"""Join verified new labels with original TRAINING rows; retain arm membership."""
import os
os.environ.update(CUDA_VISIBLE_DEVICES='-1',OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
from pathlib import Path
import json
import time
import traceback
import numpy as np
from board_river_deal_coverage_common_v1 import *
from board_prefix_publication_v1 import atomic_json
from bounded_parallel_evaluation_archive_v2 import production_available


def main():
    began=time.monotonic();destination=OUT/(PREFIX+'-merged.json');reg=OUT/(PREFIX+'-merge-registration.json')
    assert not destination.exists() and not reg.exists() and not LOCK.exists() and not OTHER.exists();acquired=False
    try:
        with LOCK.open('x') as f:f.write(str(os.getpid()))
        acquired=True;assert production_available()
        selection_path=OUT/(PREFIX+'-selection.json');selection=read(selection_path);verify(selection['inputs'])
        old_proof_path=OUT/(OLD_PREFIX+'-readback.json');new_proof_path=OUT/(PREFIX+'-readback.json')
        proofs=[read(old_proof_path),read(new_proof_path)];sources=[]
        for proof in proofs:
            assert proof['passed'] and proof['complete'];p=Path(proof['dataset'])
            assert sha(p)==proof['dataset_sha256'];sources.append(p)
        assert str(sources[0])==selection['reused_dataset'] and sha(sources[0])==selection['reused_dataset_sha256']
        paths=sources+[selection_path,old_proof_path,new_proof_path,Path(__file__),PLAN,
            ROOT/'tools/research/board_river_deal_coverage_common_v1.py']
        hashes={str(p):sha(p) for p in paths}
        atomic_json(reg,dict(inputs=hashes,original_evaluation_included=False,new_cases=1344,
            reused_training_rows=1152,combined_rows=2496,created_unix=time.time(),production_modified=False))
        pieces=[]
        for i,p in enumerate(sources):
            with np.load(p,allow_pickle=False) as z:
                mask=~z['evaluation'] if i==0 else np.ones(len(z['evaluation']),dtype=bool)
                pieces.append({k:z[k][mask] for k in z.files})
        assert set(pieces[0])==set(pieces[1])
        arrays={k:np.concatenate([d[k] for d in pieces]) for k in pieces[0]}
        ids=arrays['case_ids'].tolist();assert len(ids)==len(set(ids))==2496
        assert set(ids)==set().union(*map(set,selection['memberships'].values()))
        for arm in ('dense','broad'):
            members=selection['memberships'][arm];arrays[arm]=np.isin(arrays['case_ids'],members)
            assert len(members)==len(set(members))==int(arrays[arm].sum())==1152
            assert not np.any(arrays[arm]&arrays['evaluation'])
            assert set(arrays['deal'][arrays[arm]])==set(range(64 if arm=='dense' else 192))
        assert int((arrays['dense']&arrays['broad']).sum())==384
        assert set(arrays['case_ids'][arrays['evaluation']])==set(selection['memberships']['evaluation'])
        assert int(arrays['evaluation'].sum())==576 and set(arrays['deal'][arrays['evaluation']])==set(range(192,224))
        counts={};equal=True
        for bank in (0,1):
            for actor in (0,1):
                for band,lo,hi in BANDS:
                    base=(arrays['actor']==actor)&(arrays['pot']>=lo)&(arrays['pot']<hi)&arrays['supported'][:,bank]
                    n={arm:int((base&arrays[arm]).sum()) for arm in ('dense','broad')}
                    equal=equal and n['dense']==n['broad'];counts[f'{bank}/{actor}/{band}']=n
        path=STORE/'combined-dataset.npz';assert not path.exists()
        with path.open('xb') as f:np.savez_compressed(f,**arrays);f.flush();os.fsync(f.fileno())
        with np.load(path,allow_pickle=False) as z:
            assert set(z.files)==set(arrays)
            for k in arrays:
                assert np.array_equal(z[k],arrays[k]) if arrays[k].dtype.kind=='U' else np.array_equal(z[k],arrays[k],equal_nan=True)
        verify(hashes);assert production_available() and time.monotonic()-began<120
        result=dict(passed=True,complete=True,registration_sha256=sha(reg),dataset=str(path),dataset_sha256=sha(path),
            rows=2496,dense_rows=1152,broad_rows=1152,fresh_evaluation_rows=576,
            unsupported_by_bank=(~arrays['supported']).sum(0).tolist(),equal_effective_actor_pot_counts=equal,
            effective_actor_pot_counts=counts,original_evaluation_included=False,seconds=time.monotonic()-began)
        atomic_json(destination,result);print(json.dumps(result),flush=True)
    except Exception as error:
        atomic_json(OUT/(PREFIX+'-merge-failure.json'),dict(error=repr(error),traceback=traceback.format_exc()));raise
    finally:
        if acquired and LOCK.read_text()==str(os.getpid()):LOCK.unlink()


if __name__=='__main__':main()
