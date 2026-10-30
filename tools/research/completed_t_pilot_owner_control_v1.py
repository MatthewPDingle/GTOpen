"""Check the compactor exemption without starting a historical research worker."""
import json
import os
from pathlib import Path
from types import SimpleNamespace
import completed_t_pilot_raw_preservation_v2 as subject
from sampled_physical_root_evaluation_v1 import sha, save
from later_average_support_v1 import OUT


def main():
    me=os.getpid(); executable=str(Path(os.environ['SystemRoot'])/'System32/compact.exe')
    evidence=str(subject.BASE/subject.OWNERS[0]/'batch'/'queries.json')
    cases=[
        ('own compactor',me,[executable,'/C','/Q',evidence],True),
        ('another compactor',me+1,[executable,'/C','/Q',evidence],False),
        ('different executable',me,['elsewhere/compact.exe','/C','/Q',evidence],False),
        ('different operation',me,[executable,'/U','/Q',evidence],False),
        ('historical worker',me,['python','hu_root_retained_wider_study.py'],False),
        ('unrelated process',me+1,['python','unrelated.py'],True),
    ]
    original=subject.psutil.process_iter
    try:
        for name,parent,command,expected in cases:
            fake=SimpleNamespace(pid=me+1234,info=dict(pid=me+1234,ppid=parent,cmdline=command))
            subject.psutil.process_iter=lambda fields:[fake]
            try: subject.owners_idle(); accepted=True
            except AssertionError: accepted=False
            assert accepted==expected,name
    finally: subject.psutil.process_iter=original
    result=dict(passed=True,cases=[x[0] for x in cases],
        inputs={str(p):sha(p) for p in (Path(__file__).resolve(),Path(subject.__file__).resolve())},
        scope='Synthetic process-list ownership checks; actual copy compression is separate.',
        production_modified=False)
    path=OUT/'completed-t-pilot-owner-control-v1-result.json'; assert not path.exists()
    save(path,result); print(json.dumps(result),flush=True)


if __name__=='__main__': main()
