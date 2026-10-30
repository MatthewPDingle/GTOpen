"""CPU-only split-volume audit control using the previously audited two-update pilot."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import ast
import json
from pathlib import Path
import shutil
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from frozen_iteration_history_v1 import FrozenHistory,verify_snapshot
from later_action_history_audit_v1 import audit_history

PREFIX='split-history-readback-control-v1'
PILOT='later-action-joint-control-v1'
DEST=Path('S:/GTOpen-research')/PREFIX
CAP=350_000_000


def main():
    started=time.monotonic();last=0.
    def guard():
        nonlocal last
        now=time.monotonic()
        assert now-started<900
        if now-last>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000
            assert shutil.disk_usage('S:/').free>40_000_000_000+CAP
            last=now
    guard();assert not DEST.exists()
    import torch
    torch.set_num_threads(1);assert not torch.cuda.is_available()
    rp,pp,ar,ap=[OUT/f'{PILOT}-{s}.json' for s in
                  ('registration','result','readback-registration','independent-review')]
    reg,result,auditreg,audit=map(read,(rp,pp,ar,ap))
    assert result['passed'] and result['terminal'] and audit['passed']
    assert result['completed_iterations']==audit['completed_updates']==2
    assert result['registration_sha256']==audit['source_registration_sha256']==sha(rp)
    assert audit['source_result_sha256']==sha(pp) and audit['readback_registration_sha256']==sha(ar)
    copyrp=OUT/'checkpoint-volume-copy-control-v1-registration.json'
    copypp=OUT/'checkpoint-volume-copy-control-v1-result.json'
    copied=read(copypp);assert copied['passed'] and copied['registration_sha256']==sha(copyrp)
    copied_objects=Path('S:/GTOpen-research/checkpoint-volume-copy-control-v1/objects')
    source=Path(result['store']);iteration_source=source/'iteration-0002'
    artifacts={str(p):sha(p) for p in sorted(iteration_source.rglob('*')) if p.is_file()}
    logical=sum(Path(p).stat().st_size for p in artifacts)
    assert logical<CAP
    original=FrozenHistory([dict(first=1,last=2,store=str(source),objects=str(source/'objects'))],2)
    original_snapshot=original.snapshot(maximum_bytes=1_000_000_000,guard=guard)
    # The numerical reconstruction loop is an exact AST copy. Only evidence
    # locations and the bounded iteration count are changed around that loop.
    oldpath=ROOT/'tools/research/hu_later_action_training_review_20260925.py'
    newpath=ROOT/'tools/research/later_action_history_audit_v1.py'
    def iteration_loop(path):
        candidates=[n for n in ast.walk(ast.parse(path.read_text())) if isinstance(n,ast.For)
                    and isinstance(n.target,ast.Name) and n.target.id=='iteration']
        assert len(candidates)==1
        return candidates[0]
    old,new=iteration_loop(oldpath),iteration_loop(newpath)
    # Old first statement sets folder and second reads metrics. New first sets
    # folder + object root; the metrics statement and every subsequent statement
    # must be structurally identical, including all numerical assertions.
    assert ast.dump(ast.Module(body=old.body[1:],type_ignores=[]))==ast.dump(ast.Module(body=new.body[1:],type_ignores=[]))
    live_rp=OUT/'later-action-matched-replication-v1-registration.json'
    admission=read(live_rp)['storage_admission']
    projected=admission['projected_allocated_bytes']+250_000_000+CAP
    assert projected<=admission['limit_bytes']==800_000_000_000
    inputs={**reg['inputs'],**{p:h for p,h in auditreg['inputs'].items() if Path(p).suffix in ('.py','.rs','.exe')}}
    paths=[rp,pp,ar,ap,copyrp,copypp,live_rp,Path(__file__).resolve(),oldpath,newpath,
           ROOT/'tools/research/frozen_iteration_history_v1.py',
           ROOT/'tools/research/immutable_checkpoint_copy_v1.py']
    inputs.update({str(p):sha(p) for p in paths})
    for p,h in inputs.items():guard();assert sha(p)==h,p
    registration=OUT/f'{PREFIX}-registration.json'
    save(registration,dict(inputs=inputs,source_snapshot=original_snapshot,
        copied_iteration_files=artifacts,destination=str(DEST),copy_cap_bytes=CAP,
        projected_allocated_bytes=projected,maximum_seconds=900,gpu_used=False,
        numerical_loop_ast_equal=True,production_modified=False,live_trial_modified=False,
        scope='Copy pilot update 2 to S and independently reconstruct updates 1 and 2 across volumes. Match prior complete scalar audit. No new training or resumed live trial.'))
    try:
        DEST.mkdir();target=DEST/'iteration-0002';target.mkdir()
        for name,h in artifacts.items():
            guard();old=Path(name)
            assert not old.is_symlink() and not old.is_junction() and sha(old)==h
            new=target/old.relative_to(iteration_source);new.parent.mkdir(parents=True,exist_ok=True)
            with old.open('rb') as src,new.open('xb') as dst:
                shutil.copyfileobj(src,dst,1024*1024);dst.flush();os.fsync(dst.fileno())
            assert sha(new)==h
        history=FrozenHistory([
            dict(first=1,last=1,store=str(source),objects=str(source/'objects')),
            dict(first=2,last=2,store=str(DEST),objects=str(copied_objects))],2)
        snapshot=history.snapshot(maximum_bytes=1_000_000_000,guard=guard)
        save(OUT/f'{PREFIX}-evidence.json',snapshot)
        review=audit_history(result['config'],history,expected_checkpoint=result['final_checkpoint'],guard=guard)
        keys=('completed_updates','bb_roots_reconstructed','postflop_targets_reconstructed',
              'insertion_counts','maximum_root_state_error','maximum_target_error','maximum_policy_error')
        for key in keys:assert review[key]==audit[key],(key,review[key],audit[key])
        assert review['complete_training_history'] and review['planned_updates']==2
        verify_snapshot(snapshot,guard);verify_snapshot(original_snapshot,guard)
        for p,h in inputs.items():guard();assert sha(p)==h,p
        answer=dict(passed=True,registration_sha256=sha(registration),review=review,
            numerical_loop_ast_equal=True,original_audit_summary_exact=True,
            copied_logical_bytes=logical,seconds=time.monotonic()-started,
            original_files_unchanged=True,gpu_used=False,live_trial_modified=False,
            production_modified=False,resumed_training_qualified=False,
            scope='Storage routing and independent complete pilot audit passed; actual continuation and production strength remain unqualified.')
        save(OUT/f'{PREFIX}-result.json',answer);print(json.dumps(answer),flush=True)
    except BaseException as exc:
        save(OUT/f'{PREFIX}-failure.json',dict(error=repr(exc),seconds=time.monotonic()-started,
            registration_sha256=sha(registration),gpu_used=False,live_trial_modified=False))
        raise


if __name__=='__main__':main()
