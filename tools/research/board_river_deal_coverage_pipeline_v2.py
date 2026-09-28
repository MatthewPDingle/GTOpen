"""Serial continuation of the already registered study; no data or model changes."""
import os
os.environ['PYTHONDONTWRITEBYTECODE']='1'
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time
import traceback
import psutil
from board_river_deal_coverage_common_v1 import ROOT,OUT,STORE,PREFIX,LOCK,OTHER,read,sha,verify
from board_prefix_publication_v1 import atomic_json
from research_progress_replace_v1 import progress_json

RESULT=OUT/(PREFIX+'-collection.json')
PIPELINE=OUT/(PREFIX+'-pipeline.json')
PROGRESS=OUT/(PREFIX+'-pipeline-recovery-v1-status.json')


def publish(value):
    result=progress_json(PROGRESS,dict(pid=os.getpid(),updated_unix=time.time(),**value))
    if not result['published']:print(json.dumps(dict(progress_update_deferred=True,**result)),flush=True)


def main(collector_pid):
    began=time.monotonic();folder=STORE/'pipeline-recovery-v1';assert not folder.exists() and not PIPELINE.exists()
    scripts=['board_river_deal_coverage_readback_v1.py','board_river_deal_coverage_merge_v1.py',
        'board_river_deal_coverage_fit_v1.py','board_river_deal_coverage_evaluate_v1.py','board_river_deal_coverage_report_v1.py']
    paths=[ROOT/'tools/research'/name for name in scripts]
    hashes={str(p):sha(p) for p in paths+[Path(__file__),ROOT/'tools/research/research_progress_replace_v1.py',ROOT/'tools/research/board_river_deal_coverage_resume_v1.py']}
    registration=OUT/(PREFIX+'-pipeline-recovery-v1-registration.json');assert not registration.exists()
    process=None
    if not RESULT.exists():
        process=psutil.Process(collector_pid)
        assert 'board_river_deal_coverage_resume_v1.py' in ' '.join(process.cmdline())
        assert process.is_running();identity=dict(pid=collector_pid,created=process.create_time())
    else:identity=dict(pid=collector_pid,already_completed=True)
    folder.mkdir()
    atomic_json(registration,dict(inputs=hashes,collector=identity,created_unix=time.time(),
        sequence=['readback','merge','fit','evaluate','report'],maximum_seconds=9000,
        changes_to_registered_experiment=False,production_modified=False))
    completed=[]
    try:
        publish(dict(stage='waiting for verified collection completion',completed_stages=[]))
        while process is not None:
            try:live=process.is_running() and process.create_time()==identity['created']
            except psutil.NoSuchProcess:live=False
            if not live:break
            assert time.monotonic()-began<7200,'Collection observation deadline; do not restart collector'
            time.sleep(2)
        recovery=read(OUT/(PREFIX+'-resume-result-v1.json'))
        assert recovery['passed'] and recovery['complete'] and recovery['collection_sha256']==sha(RESULT)
        assert recovery['registration_sha256']==sha(OUT/(PREFIX+'-resume-registration-v1.json'))
        result=read(RESULT)
        assert result['passed'] and result['complete'] and len(result['routes'])==1344
        assert result['registration_sha256']==sha(OUT/(PREFIX+'-collection-registration.json'))
        assert not LOCK.exists() and not OTHER.exists()
        stages=[('readback',scripts[0],[],600,'readback'),('merge',scripts[1],[],120,'merged'),
            ('fit',scripts[2],['--mode','fit'],3600,'frozen-models'),
            ('evaluate',scripts[3],['--mode','evaluate'],600,'evaluation'),('report',scripts[4],[],180,'report-readback')]
        for stage,script,args,timeout,proof_name in stages:
            verify(hashes);assert time.monotonic()-began<9000 and not LOCK.exists() and not OTHER.exists()
            proof_path=OUT/(PREFIX+'-'+proof_name+'.json');assert not proof_path.exists()
            publish(dict(stage=stage,completed_stages=completed));print(json.dumps(dict(starting=stage)),flush=True)
            started=time.monotonic()
            log=folder/(stage+'.log')
            with log.open('x',encoding='utf-8') as output:
                child=subprocess.run([sys.executable,'-B',str(ROOT/'tools/research'/script),*args],cwd=str(ROOT),
                    stdout=output,stderr=subprocess.STDOUT,text=True,timeout=timeout,creationflags=subprocess.CREATE_NO_WINDOW)
            assert child.returncode==0,f'{stage} failed; inspect {log}'
            proof=read(proof_path);assert proof['passed']
            assert proof['complete']
            completed.append(dict(stage=stage,seconds=time.monotonic()-started,proof=str(proof_path),proof_sha256=sha(proof_path),log_sha256=sha(log)))
            print(json.dumps(completed[-1]),flush=True)
        verify(hashes)
        record=dict(passed=True,complete=True,registration_sha256=sha(registration),stages=completed,
            seconds=time.monotonic()-began,production_modified=False)
        atomic_json(PIPELINE,record);publish(dict(stage='completed; analysis review pending',completed_stages=completed))
    except Exception as error:
        failure=dict(error=repr(error),traceback=traceback.format_exc(),completed_stages=completed,seconds=time.monotonic()-began)
        atomic_json(OUT/(PREFIX+'-pipeline-recovery-v1-failure.json'),failure)
        publish(dict(stage='stopped; inspect failure before continuing',completed_stages=completed,error=repr(error)))
        raise


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--collector-pid',type=int,required=True)
    main(parser.parse_args().collector_pid)
