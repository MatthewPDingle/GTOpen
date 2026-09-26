"""Non-GPU preparation checks; never admits an incomplete trial for evaluation."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import json
from pathlib import Path
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read,load_complete_cache
from hu_paired_continuation_support_20260925 import LOCK
from retain_completed_showdown_arm_20260926 import run as retain_arm
from reboot_research_idle_v1 import idle
from owned_columnar_evaluation_archive_v1 import ColumnarEvaluationReader
from hu_showdown_complete_evaluation_review_v2_20260926 import verify_batch
from hu_showdown_complete_evaluation_v2_20260926 import run,PREFIXES


def main():
    started=time.monotonic()
    def guard():assert idle() and time.monotonic()-started<240
    guard();prefix='showdown-evaluation-preflight-v2'
    rp,destination=[OUT/f'{prefix}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not destination.exists()
    status=read(OUT/'showdown-matched-training-v1-status.json')
    process=psutil.Process(status['worker_pid'])
    assert process.is_running() and any('hu_showdown_matched_training_20260926.py' in a for a in process.cmdline())
    assert '--worker' in process.cmdline() and status['state']=='running'
    owner=LOCK.read_bytes()
    scripts=[ROOT/'tools/research'/name for name in ('showdown_root_policy_shared_v1.py',
        'hu_showdown_complete_evaluation_v2_20260926.py','hu_showdown_complete_evaluation_review_v2_20260926.py',
        'retain_completed_showdown_arm_20260926.py','compact_showdown_bank_v2.py')]
    source_result=OUT/'columnar-evaluation-archive-control-v1-result.json';control=read(source_result)
    assert control['passed']
    inputs={str(p):sha(p) for p in [*scripts,Path(__file__).resolve(),source_result,
                                  OUT/'SHOWDOWN-COMPLETE-EVALUATION-PLAN.md']}
    save(rp,dict(inputs=inputs,maximum_seconds=240,gpu_used=False,
                 scope='Syntax, live-lock refusal, and scalar batch checker on previously inspected evidence. Full-bank GPU and end-to-end study qualification pending.'))
    try:
        for path in scripts:compile(path.read_text(),str(path),'exec')
        refused=[]
        for mode in ('control','study'):
            expected=PREFIXES[mode]
            assert not (OUT/f'{expected}-registration.json').exists()
            assert not (Path('S:/GTOpen-research')/expected).exists()
            try:run(mode)
            except AssertionError:refused.append(mode)
            else:raise AssertionError('Evaluation bypassed the live research lock')
            assert not (OUT/f'{expected}-registration.json').exists()
            assert not (Path('S:/GTOpen-research')/expected).exists()
        case=Path('S:/GTOpen-research/showdown-matched-training-v1')/status['arm']
        assert not (case/'objects-retention-intent.json').exists()
        try:retain_arm(status['arm'])
        except AssertionError:refused.append('live-arm-retention')
        else:raise AssertionError('Retention bypassed live worker lock')
        assert not (case/'objects-retention-intent.json').exists()
        assert LOCK.read_bytes()==owner and process.is_running()
        store=Path(control['store']);name='test-000000'
        reader=ColumnarEvaluationReader(store,{name:control['manifest_sha256']},guard=guard)
        batch=reader.read_json(store/name/'query-batch.json')
        context=reader.read_json(store/name/'queries.json')['context_source']
        values,observations,digest=verify_batch(reader,store/name,batch,context,load_complete_cache())
        assert len(values)==control['scalar_reader_deals']==32
        assert observations==control['scalar_reader_observations']==14528
        assert digest==control['original_summary_sha256']
        for p,h in inputs.items():assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),compiled_sources=len(scripts),
            refused_while_training=refused,training_worker_pid=process.pid,original_lock_preserved=True,
            scalar_reader_deals=len(values),scalar_reader_observations=observations,
            original_summary_sha256=digest,seconds=time.monotonic()-started,gpu_used=False,
            fresh_deals_sampled=0,production_modified=False,full_bank_qualified=False,
            scope='Preparation checks only. Fresh comparison remains gated on complete audited training and full-bank control.')
        save(destination,result);print(json.dumps(result))
    except BaseException as exc:
        save(destination,dict(passed=False,error=repr(exc),registration_sha256=sha(rp),seconds=time.monotonic()-started))
        raise


if __name__=='__main__':main()
