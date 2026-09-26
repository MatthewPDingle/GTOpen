"""Qualify archived model/checkpoint access on owned copies of a completed control."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',CUDA_VISIBLE_DEVICES='-1')
import hashlib
import json
from pathlib import Path
import time
import uuid
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read
from reboot_research_idle_v1 import idle
from owned_research_archive_v1 import pack,unpack,retire
from archived_checkpoint_objects_v1 import ReadOnlyCheckpointObjects
from showdown_root_checkpoint_v1 import restore_checkpoint,validate_model
from hu_action_integrated_exact_20260925 import bank_args

PREFIX='archived-checkpoint-objects-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def main():
    start=time.monotonic()
    def guard():
        assert idle() and time.monotonic()-start<300
        if STORE.exists():assert sum(p.stat().st_size for p in STORE.rglob('*') if p.is_file())<40_000_000
    guard();rp,dest=[OUT/f'{PREFIX}-{s}.json' for s in ('registration','result')]
    assert not rp.exists() and not dest.exists() and not STORE.exists()
    sp=OUT/'showdown-training-integration-control-v1-result.json';source=read(sp)
    ap=OUT/'showdown-training-integration-control-v1-independent-review.json';audit=read(ap)
    assert source['passed'] and audit['passed'] and audit['source_result_sha256']==sha(sp)
    original=Path(source['store'])/'objects';files=sorted(p for p in original.iterdir() if p.is_file())
    for p in files:assert sha(p)==source['artifacts'][str(p)]
    inputs={str(p):sha(p) for p in [sp,ap,*files,Path(__file__).resolve(),
        ROOT/'tools/research/archived_checkpoint_objects_v1.py',ROOT/'tools/research/owned_research_archive_v1.py']}
    save(rp,dict(inputs=inputs,store=str(STORE),maximum_output_bytes=40_000_000,
        maximum_seconds=300,gpu_used=False,scope='Completed-control copies only; live training originals remain untouched.'))
    rejected=[]
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError('Accepted '+label)
    try:
        STORE.mkdir();token=uuid.uuid4().hex
        save(STORE/'archive-owner.json',dict(format=1,token=token,purpose='new-research-scratch-v1'))
        case=STORE/'case';case.mkdir();objects=case/'objects';objects.mkdir()
        original_hashes={p.name:sha(p) for p in files}
        for p in files:
            with (objects/p.name).open('xb') as f:f.write(p.read_bytes())
        before=ReadOnlyCheckpointObjects(objects,guard=guard)
        for name,h in original_hashes.items():assert hashlib.sha256(before.read(dict(file=name,sha256=h))).hexdigest()==h
        archive=case/'objects.xz'
        manifest=pack(objects,list(original_hashes),archive,root=STORE,token=token,guard=guard)
        assert unpack(archive,manifest,guard=guard)=={p.name:p.read_bytes() for p in files}
        retire(objects,archive,manifest,root=STORE,token=token,guard=guard)
        assert not list(objects.iterdir())
        receipt=dict(format=1,purpose='completed-owned-checkpoint-retention-v1',passed=True,
            originals_retired=True,objects_directory=str(objects.absolute()),archive=archive.name,
            manifest_sha256=sha(archive.with_suffix('.xz.json')),original_hashes=original_hashes,
            source_result_sha256=sha(sp),source_review_sha256=sha(ap))
        save(case/'objects-retention.json',receipt)
        after=ReadOnlyCheckpointObjects(objects,guard=guard)
        for p in files:assert after.read(dict(file=p.name,sha256=sha(p)))==p.read_bytes()
        args=bank_args((OUT/'bb-context-candidate.json').read_text())
        checkpoint=json.loads(after.read(source['final_checkpoint']))
        assert checkpoint['completed_iterations']==2
        models=[]
        for ref in [*checkpoint['played_bank'],checkpoint['next_model']]:
            doc=json.loads(after.read(ref));validate_model(doc,**args);models.append(doc)
        assert [m['generation'] for m in models]==[0,1,2]
        name=files[0].name
        reject('wrong object hash',lambda:after.read(dict(file=name,sha256='0'*64)))
        reject('path traversal',lambda:after.read(dict(file='../'+name,sha256=original_hashes[name])))
        conflict=objects/name;conflict.write_bytes(b'conflict')
        reject('plain and archived conflict',lambda:ReadOnlyCheckpointObjects(objects,guard=guard))
        assert conflict.resolve().parent==objects.resolve() and conflict.resolve().is_relative_to(STORE.resolve())
        conflict.unlink()
        restored=STORE/'restored-objects';restored.mkdir()
        for name,h in original_hashes.items():
            with (restored/name).open('xb') as f:f.write(after.read(dict(file=name,sha256=h)))
        state=restore_checkpoint(restored,source['final_checkpoint'],config=source['config'],**args)
        assert state['completed_iterations']==2 and state['next_model']==checkpoint['next_model']
        assert state['played_bank']==checkpoint['played_bank'] and sum(state['root_regret_state'].counts)==128
        # The same verified archive also backs these newly extracted duplicates.
        retire(restored,archive,manifest,root=STORE,token=token,guard=guard)
        assert not list(restored.iterdir())
        for p,h in inputs.items():guard();assert sha(p)==h,p
        result=dict(passed=True,registration_sha256=sha(rp),store=str(STORE),objects_verified=len(files),
            raw_bytes=sum(p.stat().st_size for p in files),packed_bytes=manifest['packed_bytes'],
            models_validated=[0,1,2],real_checkpoint_restored=True,checkpoint_iteration=2,
            source_result_sha256=sha(sp),source_review_sha256=sha(ap),rejections=rejected,
            artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},seconds=time.monotonic()-start,
            live_training_files_modified=False,legacy_files_modified=False,gpu_used=False,production_modified=False,
            scope='Byte-identical archived immutable-object reads and actual checkpoint restore on newly owned copies. Full-arm archival still requires a completed arm and independent audit.')
        save(dest,result);print(json.dumps({k:v for k,v in result.items() if k!='artifacts'}))
    except BaseException as exc:
        save(dest,dict(passed=False,error=repr(exc),registration_sha256=sha(rp),seconds=time.monotonic()-start))
        raise


if __name__=='__main__':main()
