"""Reopen storage-control fixtures after Windows has settled compression."""
import json
from pathlib import Path
import time
from board_study_storage_v1 import measure
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read


def main():
    began=time.monotonic(); prefix='board-study-storage-readback-v1'
    rp0=OUT/'board-study-storage-control-v1-registration.json'
    result_path=OUT/'board-study-storage-control-v1-result.json'
    original=read(result_path)
    assert original['passed'] and original['registration_sha256']==sha(rp0)
    inputs=dict(read(rp0)['inputs'])
    inputs.update({str(p):sha(p) for p in (rp0,result_path,Path(__file__).resolve())})
    for p,h in inputs.items(): assert sha(p)==h,p
    rp=OUT/f'{prefix}-registration.json'; assert not rp.exists()
    save(rp,dict(inputs=inputs,scope='Read-only reopening of four fixture files; no compression or rewriting.',
                 maximum_seconds=60,production_modified=False))
    records=[]
    for row in original['records']:
        folder=Path(row['folder'])
        assert {str(p) for p in folder.rglob('*') if p.is_file()}==set(row['hashes'])
        for p,h in row['hashes'].items(): assert sha(p)==h,p
        current=measure(folder)
        assert current['logical_bytes']==row['measurement']['logical_bytes']
        assert current['files']==current['compressed_files']==2
        assert current['allocated_file_bytes']<current['logical_bytes']
        records.append(dict(folder=str(folder),initial=row['measurement'],settled=current,
                            source_hashes=row['hashes']))
    for p,h in inputs.items(): assert sha(p)==h,p
    assert time.monotonic()-began<60
    value=dict(passed=True,registration_sha256=sha(rp),source_result_sha256=sha(result_path),records=records,
        seconds=time.monotonic()-began,production_modified=False,
        conclusion='Byte-identical fixtures occupy less space after settlement. Immediate allocation can equal logical size; do not pre-credit compression savings.')
    save(OUT/f'{prefix}-result.json',value); print(json.dumps(value),flush=True)


if __name__=='__main__':main()
