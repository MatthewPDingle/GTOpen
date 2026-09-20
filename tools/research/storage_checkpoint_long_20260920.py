"""Fresh-process whole-study resume: exact full state plus scientific trajectory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import psutil
from loopback_research_validation import idle
from storage_phase_run_20260920 import ROOT,OUT,EVIDENCE,SUB,read,sha
LABEL='checkpoint-long-v1'
CAP=16*1024**3

def same_files(a,b):
    names=sorted(p.name for p in a.iterdir());assert names==sorted(p.name for p in b.iterdir())
    for name in names:
        assert (a/name).stat().st_size==(b/name).stat().st_size,name
        with (a/name).open('rb') as x,(b/name).open('rb') as y:
            while True:
                first=x.read(4*1024**2);second=y.read(4*1024**2);assert first==second,name
                if not first:break
    return dict(files=len(names),bytes=sum((a/n).stat().st_size for n in names),all_bytes_equal=True)

class Run:
    def __init__(self):
        self.runtime=read(OUT/'checkpoint-v1-runtime-freeze.json');self.exe=Path(self.runtime['exe'])
        self.identity=Path(self.runtime['identity']);self.started=time.monotonic()
        self.root=Path('S:/GTOpen-research')/LABEL;assert not self.root.exists();self.root.mkdir()
        self.written=1024**2 # Conservative allowance for the already completed tiny format probe.
        self.status=dict(step='starting',pid=os.getpid(),created=psutil.Process().create_time(),completed=[],checkpoint_bytes_written=self.written)
        self.results={}
        old=read(OUT/'reuse-download-v1-ram-result.json')['storage'];self.storage=old
        subtree=read(SUB);nodes=subtree['nodes']
        f64s=3*sum(len(n['children'])*1326 for n in nodes if n['kind']==0)+2*1326+1+3
        self.snapshot_bound=sum(e['bytes'] for e in old['entries'])+8*f64s+72*len(old['entries'])+32+1024**2+16
        self.verify()
    def verify(self):
        for p,h in self.runtime['inputs'].items():assert sha(ROOT/p)==h,p
        assert sha(self.exe)==self.runtime['exe_sha256'] and sha(self.identity)==self.runtime['identity_sha256']
        assert time.monotonic()-self.started<6000,'Qualification observation budget expired; inspect, do not restart'
    def report(self):
        self.status['checkpoint_bytes_written']=self.written
        (OUT/f'{LABEL}-status.json').write_text(json.dumps(self.status,indent=2));print(json.dumps(self.status),flush=True)
    def run(self,name,target,resume=None,save=None,copy=None,expected_error=None):
        self.verify();assert idle()
        planned=sum(p is not None for p in [save,copy])*self.snapshot_bound
        assert self.written+planned<=CAP and shutil.disk_usage(self.root).free>=max(40_000_000_000,planned+5_000_000_000)
        scratch=self.root/(name+'-parking');assert not scratch.exists();scratch.mkdir()
        destination=OUT/f'{LABEL}-{name}-result.json';assert not destination.exists()
        env=os.environ.copy()
        for k in ['GTO_RESUME_CHECKPOINT','GTO_SAVE_CHECKPOINT','GTO_RESTORED_COPY','GTO_CHECKPOINT_FORMAT_ROOT']:env.pop(k,None)
        env.update(GTO_SSD_STUDY_DIR=str(scratch),GTO_STORAGE_RAM_BYTES=str(2**63),GTO_STORAGE_WRITE_CAP='0',
            GTO_STUDY_IDENTITY_FILE=str(self.identity),GTO_CHECKPOINT_WRITE_CAP=str(self.snapshot_bound),
            GTO_RESEARCH_MAX_SECONDS='900',GTO_RESEARCH_PROTOCOL=str((OUT/'RESUMABLE-STUDY-PROTOCOL.md').relative_to(ROOT)))
        for k,p in [('GTO_RESUME_CHECKPOINT',resume),('GTO_SAVE_CHECKPOINT',save),('GTO_RESTORED_COPY',copy)]:
            if p is not None:env[k]=str(p)
        existing={p for p in [save,copy] if p is not None and p.exists()}
        self.status['step']=name;self.report()
        proc=subprocess.run([sys.executable,'tools/research/loopback_research_validation.py',str(self.exe),LABEL+'-'+name,
            str(SUB.relative_to(ROOT)),str((OUT/'connected-three.json').relative_to(ROOT)),str(destination.relative_to(ROOT)),str(target)],cwd=ROOT,env=env)
        for p in [save,copy]:
            if p is not None and p.exists() and p not in existing:self.written+=sum(f.stat().st_size for f in p.iterdir() if f.is_file())
        self.report();assert self.written<=CAP
        self.verify();guard=read(EVIDENCE/f'{LABEL}-{name}-status.json')
        samples=read(EVIDENCE/f'{LABEL}-{name}-resources.json')
        assert min(s['free_host_bytes'] for s in samples)>=20_000_000_000 and min(s['free_gpu_bytes'] for s in samples)>=3_000_000_000
        log=(EVIDENCE/f'{LABEL}-{name}.log').read_text()
        if expected_error is not None:
            assert proc.returncode!=0 and guard['exit_code']==101 and guard['error']=='Research exited 101',guard
            errors=[expected_error] if isinstance(expected_error,str) else expected_error
            assert any(e.lower() in log.lower() for e in errors),name+': did not reject for intended reason'
            # Never count production activity, timeout, resource failure or a training panic as a format rejection.
            assert 'iteration_complete' not in log or name=='existing-complete'
            self.status['completed'].append(name);self.report();return dict(rejected=True,expected_error=expected_error,guard_seconds=guard['seconds'])
        assert proc.returncode==0 and guard['exit_code']==0 and guard['error'] is None
        r=read(destination);start=0 if resume is None else read(resume/'index.json')['iteration']
        assert r['resumed_iteration']==start and r['records'][-1]['iteration']==target
        assert r['manifest']==read(OUT/'connected-three.json')
        reference=read(OUT/'long-ram-v1-resident-result.json')
        for k in ['boards','board_weights','suit_orbits','root_normalizer','entry_cutoff']:assert r[k]==reference[k]
        for record in r['records']:
            for baseline in reference['records']:
                if record['iteration']==baseline['iteration']:assert record['evaluation']==baseline['evaluation'],name
        assert r['storage']['workspace_bytes']==self.storage['workspace_bytes']
        assert len(r['storage']['entries'])==len(self.storage['entries'])
        for entry,old in zip(r['storage']['entries'],self.storage['entries']):
            assert entry['bytes']==old['bytes'] and not entry['disk'] and entry['read_bytes']==entry['write_bytes']==0
            assert entry['gpu_transfer_bytes']==3*(target-start)*entry['bytes']
        self.results[name]=dict(result_sha256=sha(destination),guard_seconds=guard['seconds'],resumed_iteration=start,target=target)
        self.status['completed'].append(name);self.report();return r

def main():
    assert read(OUT/'checkpoint-v1-review.json')['passed']
    assert read(OUT/'checkpoint-v1-status.json')['step']=='complete-format-and-20-iteration-qualified'
    for d in [OUT,EVIDENCE]:assert not (d/'running.lock').exists()
    assert idle();run=Run()
    frozen=dict(inputs={str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),OUT/'checkpoint-v1-review.json',
        OUT/'checkpoint-v1-runtime-freeze.json',ROOT/'tools/research/storage_checkpoint_negative_20260920.py']},
        runtime=run.runtime,maximum_checkpoint_write_bytes=CAP,snapshot_upper_bound_bytes=run.snapshot_bound)
    with (OUT/f'{LABEL}-freeze.json').open('x') as f:json.dump(frozen,f,indent=2)
    with (OUT/'running.lock').open('x') as f:f.write(str(os.getpid()))
    try:
        full=run.root/'full-final';run.run('full',500,save=full)
        exact={}
        for point in [100,37]:
            saved=run.root/f'at-{point}';copy=run.root/f'reloaded-{point}';final=run.root/f'final-from-{point}'
            first=run.run(f'prefix-{point}',point,save=saved)
            second=run.run(f'resume-{point}',500,resume=saved,save=final,copy=copy)
            assert first['records'][-1]['evaluation']==second['records'][0]['evaluation']
            exact[str(point)]=dict(restored=same_files(saved,copy),final=same_files(full,final))
        from storage_checkpoint_negative_20260920 import negative_controls
        negative=negative_controls(run)
        for p,h in frozen['inputs'].items():assert sha(ROOT/p)==h,p
        run.verify()
        review=dict(passed=True,split_points=[100,37],all_scientific_checkpoints_exact=True,full_raw_records=exact,
            runs=run.results,negative_controls=negative,checkpoint_bytes_written=run.written,maximum_checkpoint_write_bytes=CAP,
            production_ready=False,broad_study_qualified=False,
            scope='Three-board exact process-exit/resume through 500, including raw canonical and preflop bits. No broad accuracy claim.')
        with (OUT/f'{LABEL}-review.json').open('x') as f:json.dump(review,f,indent=2)
        run.status['step']='complete-fresh-process-resume-qualified'
    except Exception as e:run.status.update(step='stopped-for-review',error=repr(e));raise
    finally:run.report();(OUT/'running.lock').unlink()

if __name__=='__main__':main()
