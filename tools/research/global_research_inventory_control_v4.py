"""Read-only paired comparison of the frozen and optimized full inventories."""
import hashlib
import json
import os
from pathlib import Path
import time
import traceback
import psutil
from board_prefix_publication_v1 import atomic_json
from weighted_learning_cuda_control_20260927 import LOCK,OTHER
from bounded_parallel_evaluation_archive_v2 import production_available
import global_research_inventory_v2 as old
import global_research_inventory_v3 as new

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
RESULT=OUT/'global-research-inventory-v3-control-v2.json'
REG=OUT/'global-research-inventory-v3-registration-v2.json'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not LOCK.exists() and not OTHER.exists() and not RESULT.exists() and not REG.exists()
    assert production_available() and psutil.virtual_memory().available>28_000_000_000
    sources=[Path(__file__),Path(old.__file__),Path(new.__file__),ROOT/'tools/research/global_research_inventory_control_v3.py']
    spec=dict(pre_scan_correction='Earlier control failed syntax parsing before scans or registration; rename reserved keyword and version evidence paths.',inputs={str(p):sha(p) for p in sources},order=['original_v2','candidate_v3','candidate_v3_repeat'],
        maximum_seconds=1800,no_research_artifact_mutation=True,maximum_new_evidence_bytes=1_000_000,
        pass_condition='Exact root/count/logical/allocation equality across all three scans plus fail-closed controls',
        speed_claim='Observed end-to-end inventory times, not solver throughput',production_modified=False)
    atomic_json(REG,spec)
    with LOCK.open('x') as f:f.write(str(os.getpid()))
    began=time.monotonic()
    try:
        records=[]
        for name,module in (('original_v2',old),('candidate_v3',new),('candidate_v3_repeat',new)):
            assert time.monotonic()-began<1800 and psutil.virtual_memory().available>24_000_000_000
            start=time.monotonic();rows=module.measure()
            records.append(dict(name=name,seconds=time.monotonic()-start,rows=rows))
            print(json.dumps(dict(stage=name,seconds=records[-1]['seconds'],files=sum(r['files'] for r in rows))),flush=True)
        assert records[0]['rows']==records[1]['rows']==records[2]['rows'],'Quiescent inventory mismatch'
        negative=[]
        def refuse(name,call):
            try:call()
            except (AssertionError,FileNotFoundError,NotADirectoryError):negative.append(name)
            else:raise AssertionError('Should refuse '+name)
        refuse('activity_unavailable',lambda:new.measure(roots=[],activity=lambda:False))
        refuse('relative_root',lambda:new.measure(roots=[Path('research')]))
        refuse('file_instead_of_directory',lambda:new.measure(roots=[Path(__file__)]))
        refuse('missing_root',lambda:new.measure(roots=[OUT/'nonexistent-inventory-control-v3']))
        # Simulate directory-entry reparse metadata without creating any junctions.
        class FakeStat:
            st_file_attributes=0x400;st_reparse_tag=0xa0000003;st_size=0
        class FakeDir:
            path=str(OUT/'synthetic-directory-link');name='synthetic-directory-link'
            def is_dir(self,follow_symlinks=False):return True
            def stat(self,follow_symlinks=False):return FakeStat()
        class FakeScan:
            def __enter__(self):return iter([FakeDir()])
            def __exit__(self,*args):pass
        actual=new.os.scandir
        try:
            new.os.scandir=lambda folder:FakeScan()
            refuse('directory_reparse',lambda:new.measure(roots=[OUT]))
        finally:new.os.scandir=actual
        for p,h in spec['inputs'].items():assert sha(p)==h
        result=dict(passed=True,registration_sha256=sha(REG),scans=records,negative_controls=negative,
            elapsed_seconds=time.monotonic()-began,original_seconds=records[0]['seconds'],
            candidate_seconds=[r['seconds'] for r in records[1:]],
            speedup=[records[0]['seconds']/r['seconds'] for r in records[1:]],
            file_allocation_equal=True,existing_artifacts_modified=False,production_modified=False)
        atomic_json(RESULT,result)
        print(json.dumps({k:v for k,v in result.items() if k!='scans'}),flush=True)
    except BaseException as e:
        atomic_json(OUT/'global-research-inventory-v3-interruption-v2.json',dict(error=repr(e),traceback=traceback.format_exc(),complete=False))
        raise
    finally:
        assert LOCK.read_text()==str(os.getpid());LOCK.unlink()

if __name__=='__main__':main()
