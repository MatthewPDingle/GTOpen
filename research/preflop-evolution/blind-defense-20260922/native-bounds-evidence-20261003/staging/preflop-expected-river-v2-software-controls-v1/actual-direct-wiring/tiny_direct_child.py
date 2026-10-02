import json,os,sys
from pathlib import Path
import psutil
assert sys.argv[-1]=='--output-byte-limit=64000000'
mode=sys.argv[1];path=Path(sys.argv[-2]);path.write_bytes((mode+' direct software output\n').encode())
p=psutil.Process();parent=p.parent()
print(json.dumps(dict(mode=mode,argv=p.cmdline(),pid=p.pid,parent_pid=parent.pid,
    creation_time=p.create_time(),parent_creation_time=parent.create_time(),cuda=os.environ.get('CUDA_VISIBLE_DEVICES'))))
