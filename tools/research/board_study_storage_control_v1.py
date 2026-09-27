"""Bounded new-directory compression and exact allocation accounting control."""
import hashlib
import json
from pathlib import Path
import time
from board_study_storage_v1 import create,measure,path_within_research
from ntfs_research_storage_v1 import allocated_bytes,attributes,COMPRESSED
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT

PREFIX='board-study-storage-control-v1'


def main():
    began=time.monotonic(); rp=OUT/f'{PREFIX}-registration.json'; assert not rp.exists()
    paths=[Path(__file__).resolve(),ROOT/'tools/research/board_study_storage_v1.py',ROOT/'tools/research/ntfs_research_storage_v1.py']
    inputs={str(p):sha(p) for p in paths}
    save(rp,dict(inputs=inputs,maximum_bytes=2_000_000,maximum_seconds=60,
        scope='New fixture directories only; no existing study changes.',production_modified=False))
    records=[]; rejected=0
    for p in ('S:/GTOpen-research','T:/GTOpen-research','S:/outside-research','relative-path'):
        try: path_within_research(p)
        except ValueError: rejected+=1
        else: raise AssertionError('Accepted outside or root path')
    for root in ('S:/GTOpen-research','T:/GTOpen-research'):
        folder=Path(root)/PREFIX; create(folder); assert attributes(folder)&COMPRESSED
        try: create(folder)
        except ValueError: rejected+=1
        else: raise AssertionError('Accepted existing directory')
        sub=folder/'nested'; sub.mkdir()
        files=[folder/'repeated.bin',sub/'varied.bin']
        data=[bytes(range(256))*1024,bytes.fromhex(hashlib.sha256(b'board storage control').hexdigest())*8192]
        for p,b in zip(files,data):
            with p.open('xb') as f: f.write(b)
            assert p.read_bytes()==b and attributes(p)&COMPRESSED
        result=measure(folder)
        assert result['logical_bytes']==sum(len(x) for x in data)
        assert result['allocated_file_bytes']==sum(allocated_bytes(p) for p in files)
        assert result['files']==result['compressed_files']==2
        records.append(dict(folder=str(folder),measurement=result,hashes={str(p):sha(p) for p in files}))
    for p,h in inputs.items(): assert sha(p)==h,p
    assert time.monotonic()-began<60
    result=dict(passed=True,registration_sha256=sha(rp),records=records,rejections=rejected,
        seconds=time.monotonic()-began,production_modified=False)
    save(OUT/f'{PREFIX}-result.json',result); print(json.dumps(result),flush=True)


if __name__=='__main__': main()
