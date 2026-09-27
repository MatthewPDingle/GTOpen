"""Check real saved seals and reject corrupted seals or inaccurate calculations."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', CUDA_VISIBLE_DEVICES='-1')
import copy
import json
from pathlib import Path
import time
from threadpoolctl import threadpool_limits
from later_average_support_v1 import OUT, read
from sampled_physical_root_evaluation_v1 import sha
from sampled_visible_hybrid_checkpoint_v1 import read_object
from board_training_readback_support_v1 import prepare_readback
from board_readback_identity_v2 import verify_identity
from board_prefix_publication_v1 import atomic_json


def main():
    began = time.monotonic(); records = []; rejected = 0
    regpath = OUT/'board-training-pipeline-control-v1-registration.json'; reg = read(regpath)
    for p,h in reg['inputs'].items(): assert sha(p) == h,p
    store = Path(reg['store']); cp = OUT/'bb-context-candidate.json'
    mp = OUT/'preflop-allin-matrix-control-v1-matrix.json'
    cat = Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    physical = Path('S:/GTOpen-research/board-root-components-control-v1/preflop-catalog.json')
    paths = [regpath,cp,mp,cat,physical,*Path(__file__).parent.glob('*.py')]
    def reject(payload, independent, evidence):
        nonlocal rejected
        try: verify_identity(payload, independent, evidence)
        except ValueError: rejected += 1
        else: raise AssertionError('Corrupted evidence accepted')
    for i in (1,2):
        folder = store/f'generation-{i:04d}'
        metric = read(folder/'metrics.json'); evidence = read(folder/'board-generation-evidence.json')
        modelpath = store/'objects'/metric['used_model']['file']
        payload = dict(model_source=read_object(store/'objects',metric['used_model']).decode(),
            context_source=cp.read_text(), catalog_source=cat.read_text(), physical_catalog_source=physical.read_text(),
            matrix_source=mp.read_text(), root_config=reg['config']['board_root'])
        with threadpool_limits(limits=1): independent = prepare_readback(payload)
        proof = verify_identity(payload, independent, evidence)
        saved = read(store/'objects'/metric['checkpoint']['file'])
        trained = read_object(store/'objects',saved['next_model'])
        history = json.loads(trained)['board_root_state']['history'][-1]
        assert all(proof[k] == history[k] for k in ('played_policy_sha256','exact_terms_sha256','delta_sha256'))
        records.append(dict(generation=i,**proof))
        paths.extend((folder/'metrics.json',folder/'board-generation-evidence.json',modelpath,
                      store/'objects'/metric['checkpoint']['file'],store/'objects'/saved['next_model']['file']))
        for key in ('played_policy_sha256','exact_terms_sha256'):
            bad = copy.deepcopy(evidence); bad[key] = '0'*64; reject(payload,independent,bad)
        bad = copy.deepcopy(independent); bad['pre'][0][0,0] += 1e-6; reject(payload,bad,evidence)
        bad = copy.deepcopy(independent); bad['exact_scalar'][0,2] += 1e-6; reject(payload,bad,evidence)
    assert rejected == 8
    result = dict(passed=True, inputs={str(p):sha(p) for p in paths}, actual_generations=2,
        corruption_rejections=rejected, records=records, seconds=time.monotonic()-began,
        original_numerical_tolerance=1e-10, producer_reconstruction_used_only_for_byte_seals=True,
        gpu_used=False, refit_performed=False, production_modified=False)
    atomic_json(OUT/'board-readback-identity-control-v2-result.json',result)
    print(json.dumps(result | {'inputs':len(result['inputs'])}),flush=True)


if __name__ == '__main__': main()
