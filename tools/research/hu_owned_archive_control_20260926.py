"""Qualify compact retention on copies of new control artifacts; originals stay intact."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='2',OMP_NUM_THREADS='2')
import copy
from pathlib import Path
import sys
import time
import uuid
from hu_paired_continuation_support_20260925 import launch,guard_for
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from hu_action_integrated_exact_20260925 import bank_args
from showdown_root_checkpoint_v1 import restore_checkpoint
from owned_research_archive_v1 import pack,unpack,retire,encoded

PREFIX='owned-research-archive-control-v1'
STORE=Path('S:/GTOpen-research')/PREFIX


def worker(reg):
    guard=guard_for(reg,gpu=False);guard();started=time.monotonic()
    source=read(OUT/'showdown-training-integration-control-v1-result.json')
    assert source['passed']
    STORE.mkdir();token=uuid.uuid4().hex
    save(STORE/'archive-owner.json',dict(format=1,token=token,purpose='new-research-scratch-v1'))
    rows=[];rejected=[]
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError('Accepted '+label)
    for label,original in [('batch',Path(source['store'])/'iteration-0002'/'batch-00'),('objects',Path(source['store'])/'objects')]:
        guard();folder=STORE/label;folder.mkdir()
        names=[];hashes={}
        for file in sorted(original.iterdir()):
            if not file.is_file():continue
            assert sha(file)==source['artifacts'][str(file)]
            (folder/file.name).write_bytes(file.read_bytes());names.append(file.name);hashes[file.name]=sha(file)
        path=STORE/(label+'.xz');start=time.monotonic()
        manifest=pack(folder,names,path,root=STORE,token=token,guard=guard)
        seconds=time.monotonic()-start
        restored=unpack(path,manifest,guard=guard)
        assert set(restored)==set(names)
        for key,data in restored.items():assert data==(original/key).read_bytes()
        bad=copy.deepcopy(manifest);bad['packed_sha256']='0'*64
        reject('changed compressed hash '+label,lambda:unpack(path,bad,guard=guard))
        bad=copy.deepcopy(manifest);bad['members'][0]['sha256']='0'*64
        reject('changed member manifest '+label,lambda:unpack(path,bad,guard=guard))
        reject('wrong owner '+label,lambda:retire(folder,path,manifest,root=STORE,token='wrong',guard=guard))
        reject('outside ownership '+label,lambda:retire(original,path,manifest,root=STORE,token=token,guard=guard))
        # One changed duplicate must block retirement of every source member.
        first=folder/names[0];first.write_bytes(first.read_bytes()+b' ')
        reject('changed raw scratch '+label,lambda:retire(folder,path,manifest,root=STORE,token=token,guard=guard))
        assert all((folder/n).exists() for n in names)
        first.write_bytes((original/names[0]).read_bytes())
        retire(folder,path,manifest,root=STORE,token=token,guard=guard)
        assert not list(folder.iterdir())
        for key in names:assert sha(original/key)==hashes[key]
        rows.append(dict(label=label,members=len(names),raw_bytes=sum(i['bytes'] for i in manifest['members']),
            packed_bytes=manifest['packed_bytes'],roundtrip_seconds=seconds,archive=str(path),manifest_sha256=sha(path.with_suffix('.xz.json'))))
        if label=='objects':
            # Exercise the real checkpoint loader after full lossless restoration.
            for key,data in restored.items():
                with (folder/key).open('xb') as f:f.write(data)
            args=bank_args((OUT/'bb-context-candidate.json').read_text())
            state=restore_checkpoint(folder,source['final_checkpoint'],config=source['config'],**args)
            assert state['completed_iterations']==2 and state['next_model']==source['steps'][-1]['next_model']
            assert state['root_regret_state'].counts.sum()==128
    for p,h in reg['inputs'].items():guard();assert sha(p)==h,p
    result=dict(passed=True,terminal=True,registration_sha256=sha(OUT/f'{PREFIX}-registration.json'),
        rows=rows,rejections=rejected,originals_unchanged=True,checkpoint_restored_after_archival=True,
        store=str(STORE),artifacts={str(p):sha(p) for p in STORE.rglob('*') if p.is_file()},
        seconds=time.monotonic()-started,production_modified=False,
        scope='Lossless retention qualification on owned copies only. No new training or poker-quality claim.')
    save(OUT/f'{PREFIX}-result.json',result);print(result,flush=True)


if __name__=='__main__':
    if sys.argv[1:]==['--worker']:worker(read(OUT/f'{PREFIX}-registration.json'))
    else:
        assert sys.argv[1:]==['--run']
        p=OUT/'showdown-training-integration-control-v1-result.json';r=read(p)
        launch(Path(__file__).resolve(),PREFIX,dict(extra_inputs=[str(p)],store=str(STORE),
            source_result_sha256=sha(p),scope='Own-copy archival and checkpoint restoration only'),cap=150_000_000,seconds=600)
