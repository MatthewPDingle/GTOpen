import json,os,sys,time
from pathlib import Path
import psutil
mode=sys.argv[1];out=Path(sys.argv[2]);aux=Path(sys.argv[3]) if len(sys.argv)>3 else None
if mode=='quiet-large':out.write_bytes(b'x'*4096)
elif mode=='combined':
    out.write_bytes(b'd'*600);sys.stdout.buffer.write(b'o'*400);sys.stderr.buffer.write(b'e'*400)
elif mode=='immediate':out.write_bytes(b'immediate direct')
elif mode=='missing':pass
elif mode=='fail':
    out.write_bytes(b'partial-direct');sys.stderr.write('fixture nonzero\n');sys.exit(7)
elif mode=='wait':
    out.write_bytes(b'partial-before-stop');sys.stdout.write('ready\n');sys.stdout.flush()
    while True:time.sleep(.02)
else:
    if mode=='stdin':out.write_bytes(sys.stdin.buffer.read())
    elif mode=='modify-source':out.write_bytes(b'direct-before-source-refusal');aux.write_bytes(b'changed source')
    elif mode!='stdio':out.write_bytes(b'genuine direct output\n')
    me=psutil.Process();parent=psutil.Process(os.getppid())
    print(json.dumps(dict(pid=os.getpid(),creation_time=me.create_time(),parent_pid=parent.pid,
        parent_creation_time=parent.create_time(),observed_cmdline=me.cmdline(),
        executable=me.exe(),cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'))))
