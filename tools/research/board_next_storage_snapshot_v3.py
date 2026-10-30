"""Inventory quiescent evidence and reserve the active evaluator's full budget."""
import json
import os
from pathlib import Path
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT, sha, save
from later_average_support_v1 import OUT, read
from hu_root_retained_storage_admitted_study_20260924 import stable_file, inventory_error
from ntfs_research_storage_v1 import allocated_bytes
from bounded_parallel_evaluation_archive_v2 import production_available


def main():
    began=time.monotonic()
    psutil.Process().nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
    result_path=OUT/'board-next-study-storage-snapshot-v3.json'
    assert not result_path.exists()
    regpath=OUT/'weighted-complete-evaluation-study-v1-registration.json'
    reg=read(regpath); excluded=Path(reg['store']).resolve()
    assert excluded==Path('S:/GTOpen-research/weighted-complete-evaluation-study-v1')
    status=read(OUT/'weighted-complete-evaluation-study-v1-status.json')
    process=psutil.Process(status['pid']); created=process.create_time()
    assert status['state']=='running' and process.is_running()
    assert any('weighted_complete_evaluation_study_v2.py' in x for x in process.cmdline())
    preserved=OUT/'completed-t-pilot-raw-preservation-v2-independent-review.json'
    assert read(preserved)['passed']
    inputs={str(p):sha(p) for p in (Path(__file__).resolve(),regpath,preserved,
        ROOT/'tools/research/hu_root_retained_storage_admitted_study_20260924.py',
        ROOT/'tools/research/ntfs_research_storage_v1.py',
        ROOT/'tools/research/board_matched_prefix_v2.py',
        ROOT/'tools/research/weighted_gpu_throughput_control_v1.py',
        OUT/'board-training-pipeline-queue-v2-registration.json')}
    rows=[]; last_probe=0.
    for root in (Path('S:/GTOpen-research'),Path('T:/GTOpen-research'),ROOT/'research'):
        assert root.is_dir() and not root.lstat().st_file_attributes&0x400
        logical=allocated=count=0
        for folder,dirs,files in os.walk(root,followlinks=False,onerror=inventory_error):
            now=time.monotonic(); assert now-began<600
            if now-last_probe>2:
                assert production_available(); last_probe=now
            for name in list(dirs):
                p=Path(folder)/name
                assert not p.lstat().st_file_attributes&0x400,str(p)
                if p==excluded: dirs.remove(name)
            for name in files:
                p=Path(folder)/name
                try:
                    stable_file(p)
                    logical+=p.stat().st_size; allocated+=allocated_bytes(p); count+=1
                except FileNotFoundError:
                    assert p.suffix=='.tmp' or p.name.startswith('.partial-')
        rows.append(dict(root=str(root),files=count,logical_bytes=logical,allocated_file_bytes=allocated))
    for p,h in inputs.items(): assert sha(p)==h,p
    assert process.is_running() and process.create_time()==created
    reservations=dict(active_evaluation=reg['maximum_output_bytes'],queued_gpu_control=6_000_000_000,
        planned_two_arm_prefix=4_000_000_000,planned_throughput_control=2_000_000_000,
        metadata_and_headroom=2_000_000_000)
    total=sum(x['allocated_file_bytes'] for x in rows)
    projected=total+sum(reservations.values())
    report=dict(inputs=inputs,roots=rows,total_excluding_active_evaluation=total,
        excluded_active_store=str(excluded),active_process=dict(pid=process.pid,created=created),
        reserved_bytes=reservations,projected_total_bytes=projected,ceiling_bytes=800_000_000_000,
        projected_headroom_bytes=800_000_000_000-projected,controls_fit=projected<=800_000_000_000,
        full_78_generation_study_admitted=False,seconds=time.monotonic()-began,
        scope='Storage snapshot only; actual launches repeat all scientific, resource and source checks.',
        production_modified=False)
    save(result_path,report)
    print(json.dumps({k:v for k,v in report.items() if k not in ('inputs','roots')}),flush=True)


if __name__=='__main__': main()
