"""Read-only proof that the original trial and its supervisor are terminal."""
from pathlib import Path
import psutil
from later_average_support_v1 import OUT,read


def assert_original_stopped():
    status=read(OUT/'later-action-matched-replication-v1-status.json')
    pipeline=read(OUT/'later-action-pipeline-v1-status.json')
    assert status['state']=='stopped' and status['error'] is not None
    assert pipeline['state']=='stopped' and pipeline['error'] is not None
    programs={'hu_later_action_replication_concurrent_20260925.py','hu_later_action_pipeline_20260925.py'}
    for proc in psutil.process_iter(['cmdline']):
        command=proc.info['cmdline'] or []
        assert not any(Path(s).name in programs for s in command),'Original controller or worker still live'
    return status,pipeline
