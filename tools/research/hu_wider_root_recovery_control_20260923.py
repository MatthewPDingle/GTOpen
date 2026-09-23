"""Compare recovered transport with an already completed fixed-count control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2', OMP_NUM_THREADS='2')
import copy
import json
import shutil
import time
from pathlib import Path
from unittest.mock import patch
import psutil
from later_average_support_v1 import OUT, read, load_complete_cache, weights
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from sampled_visible_hybrid_checkpoint_v1 import model_document, verify_bank
from sampled_visible_hybrid_cpu64_v1 import VisibleHybridCpuBank64
from reboot_research_idle_v1 import idle
import wider_root_recovery_v1 as recovery
from wider_root_readback_v1 import review

PREFIX = 'wider-root-recovery-control-v1'
STORE = Path('T:/GTOpen-research') / PREFIX


def main():
    start = time.monotonic()
    def guard():
        assert time.monotonic() - start < 1800 and idle()
        assert psutil.virtual_memory().available > 20_000_000_000
        assert shutil.disk_usage('T:/').free > 40_000_000_000
    guard()
    rp = OUT / f'{PREFIX}-registration.json'
    assert not STORE.exists() and not rp.exists()
    source_rp = OUT / 'wider-root-evaluation-control-v1-registration.json'
    source_pp = OUT / 'wider-root-evaluation-control-v1-result.json'
    audit_path = OUT / 'wider-root-readback-control-v1-result.json'
    reg, done, audit = map(read, (source_rp, source_pp, audit_path))
    assert done['passed'] and audit['passed'] and done['registration_sha256'] == sha(source_rp)
    for p, h in reg['inputs'].items():
        assert sha(p) == h
    source = Path(reg['store'])
    assert sha(source / 'result.json') == done['result_sha256']
    old_result = read(source / 'result.json')
    manifest = recovery.capture(source, reg['config'], guard)
    # Deliberately withhold the last two complete test batches to exercise
    # genuine inference/native evaluation after the reused prefix.
    omitted = sorted(n for n in manifest['batches'] if n.startswith('test-'))[-2:]
    for n in omitted:
        del manifest['batches'][n]
    manifest['completed_deals']['test'] -= reg['config']['batch_size'] * 2
    cp = OUT / 'bb-context-candidate.json'
    context = cp.read_text()
    objects = Path('S:/GTOpen-research/sampled-visible-hybrid-allin-control-v1/checkpoint-objects')
    checkpoint_path = objects / reg['checkpoint']['file']
    assert sha(checkpoint_path) == reg['checkpoint']['sha256']
    checkpoint = read(checkpoint_path)
    verify_bank(objects, 4, checkpoint['played_bank'], checkpoint['next_model'], context_source=context)
    docs = [model_document(objects, r, context_source=context) for r in checkpoint['played_bank']]
    bank = VisibleHybridCpuBank64(docs, context_source=context, weights_by_player=weights('linear', 4))
    cache = load_complete_cache()
    assert cache.sha256 == reg['cache_sha256']
    inputs = dict(reg['inputs'])
    for p in (Path(__file__), Path(recovery.__file__), source_rp, source_pp,
              audit_path, source / 'result.json', ROOT / 'tools/research/wider_root_readback_v1.py'):
        inputs[str(p.resolve())] = sha(p)
    save(rp, dict(inputs=inputs, manifest=manifest, store=str(STORE),
        recomputed_batches=omitted, maximum_seconds=1800, gpu_used=False,
        operation='Recover 28 batches, recompute two held-out transport batches, compare every result field except elapsed timings and independently replay all artifacts. Test three corruption rejections.',
        accuracy_qualified=False, production_modified=False))
    STORE.mkdir(parents=True)
    result, transport = recovery.run(cp, bank, cache, reg['exact'], reg['config'],
                                    STORE / 'evaluation', guard, manifest)
    for key in old_result:
        if key not in ('seconds', 'phase_timings'):
            assert result[key] == old_result[key], key
    assert transport['computed_batches'] == omitted and len(transport['reused_batches']) == 28
    checked = review(cp, STORE / 'evaluation', reg['config'], reg['exact'], cache.sha256, guard)
    assert checked['passed']
    rejected = []
    for mutation in ('root-hash', 'batch-hash', 'chance-mismatch'):
        changed = copy.deepcopy(manifest)
        if mutation == 'root-hash':
            changed['root_files']['response.json'] = '0' * 64
        elif mutation == 'batch-hash':
            changed['batches']['train-000000']['query-batch.json'] = '0' * 64
        original_read = recovery.read
        def corrupt(path):
            value = original_read(path)
            if mutation == 'chance-mismatch' and Path(path) == source / 'train-000000/query-batch.json':
                value['batch_id'] += '-wrong'
            return value
        try:
            with patch.object(recovery, 'read', corrupt):
                recovery.run(cp, bank, cache, reg['exact'], reg['config'],
                             STORE / mutation, guard, changed)
        except AssertionError:
            rejected.append(mutation)
        else:
            raise AssertionError(f'Failed to reject {mutation}')
    for p, h in inputs.items():
        assert sha(p) == h
    guard()
    evidence = dict(passed=True, registration_sha256=sha(rp), transport=transport,
        original_nontiming_result_fields_identical=True, independent_readback=checked,
        corruptions_rejected=rejected, seconds=time.monotonic()-start,
        gpu_used=False, accuracy_qualified=False, production_modified=False)
    save(OUT / f'{PREFIX}-result.json', evidence)
    print(dict(passed=True, seconds=evidence['seconds'], corruptions_rejected=rejected), flush=True)


if __name__ == '__main__':
    main()
