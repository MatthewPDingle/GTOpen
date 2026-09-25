"""Five-minute read-only hardware observation of the registered first trainer.

Never starts/stops a solve, changes affinity, or touches training artifacts.
Main-worker CPU counters exclude native child time. Device samples include all
GPU applications, so they are not attributed solely to this experiment.
"""
import json
import os
from pathlib import Path
import subprocess
import time
import psutil
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from later_average_support_v1 import OUT,read

PREFIX='later-action-hardware-sample-v1'
TRIAL='later-action-matched-first-v1'


def main():
    status=read(OUT/f'{TRIAL}-status.json');assert status['state']=='running'
    process=psutil.Process(status['worker_pid']);birth=process.create_time()
    args=process.cmdline()
    assert any(Path(a).name=='hu_later_action_matched_trial_20260925.py' for a in args)
    assert '--worker' in args and 'first' in args
    path=Path('T:/GTOpen-research')/TRIAL/'latest.json'
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(script_sha256=sha(Path(__file__)),training_registration_sha256=sha(OUT/f'{TRIAL}-registration.json'),
        worker_pid=process.pid,worker_created=birth,seconds=300,sample_interval_seconds=5,
        mutates_training=False,production_modified=False,
        scope='Read-only snapshots, main-worker CPU counters, and whole-device GPU activity. Excludes native-child CPU time and cannot isolate GPU activity from other applications.'))
    psutil.cpu_percent(interval=None)
    start=time.monotonic();rows=[];error=None
    def capture():
        assert process.create_time()==birth
        cpu=process.cpu_times();io=process.io_counters();vm=psutil.virtual_memory()
        gpu=subprocess.run(['nvidia-smi','--query-gpu=utilization.gpu,memory.used,memory.total,power.draw',
            '--format=csv,noheader,nounits'],capture_output=True,text=True,timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW)
        fields=gpu.stdout.strip().splitlines()[0].split(',') if gpu.returncode==0 and gpu.stdout.strip() else []
        def number(i):
            try:return float(fields[i].strip())
            except (ValueError,IndexError):return None
        children=[]
        for child in process.children(recursive=True):
            try:children.append(dict(pid=child.pid,name=child.name()))
            except psutil.NoSuchProcess:pass
        return dict(seconds=time.monotonic()-start,worker_cpu_seconds=cpu.user+cpu.system,
            worker_read_bytes=io.read_bytes,worker_write_bytes=io.write_bytes,worker_rss_bytes=process.memory_info().rss,
            host_cpu_percent=psutil.cpu_percent(interval=None),host_available_bytes=vm.available,
            gpu_utilization_percent=number(0),gpu_used_mib=number(1),gpu_total_mib=number(2),gpu_power_w=number(3),
            completed_updates=read(path)['completed_iterations'],native_children=children)
    try:
        rows.append(capture())
        while time.monotonic()-start<300:
            time.sleep(min(5,300-(time.monotonic()-start)))
            rows.append(capture())
    except BaseException as exc:
        error=repr(exc)
    elapsed=rows[-1]['seconds']-rows[0]['seconds'] if len(rows)>1 else 0
    def measured(key):return [r[key] for r in rows[1:] if r[key] is not None]
    def mean(key):
        values=measured(key);return sum(values)/len(values) if values else None
    result=dict(passed=error is None,error=error,registration_sha256=sha(rp),samples=rows,
        observed_seconds=elapsed,completed_updates=[rows[0]['completed_updates'],rows[-1]['completed_updates']] if rows else [],
        main_worker_mean_logical_cores=(rows[-1]['worker_cpu_seconds']-rows[0]['worker_cpu_seconds'])/elapsed if elapsed else None,
        whole_host_mean_cpu_percent=mean('host_cpu_percent'),whole_device_mean_gpu_percent=mean('gpu_utilization_percent'),
        whole_device_maximum_used_mib=max(measured('gpu_used_mib'),default=None),
        mean_device_power_w=mean('gpu_power_w'),production_modified=False,accuracy_qualified=False,
        scope='Observational sample, not a controlled throughput comparison. Main CPU excludes native children; GPU includes other applications.')
    save(OUT/f'{PREFIX}-result.json',result)
    print(json.dumps({k:v for k,v in result.items() if k!='samples'}))


if __name__=='__main__':main()
