"""Best-effort progress-only publication under transient Windows reader locks.

Durable result, archive and completion markers must keep their strict writer.
Only sharing/access PermissionError from the final replace is retryable here;
serialization, flush, disk-full and all other IO errors remain fatal.
"""
import json
import os
from pathlib import Path
import time
import uuid


def progress_json(path,value,*,attempts=8,delay=.05,_replace=os.replace,_sleep=time.sleep):
    path=Path(path)
    assert os.name=='nt' and path.name.endswith('-status.json')
    assert type(attempts) is int and 1<=attempts<=20 and 0<=delay<=1
    temporary=path.with_name(f'.partial-{path.name}-{uuid.uuid4().hex}')
    with temporary.open('x',encoding='utf-8',newline='\n') as stream:
        json.dump(value,stream,separators=(',',':'),allow_nan=False)
        stream.write('\n');stream.flush();os.fsync(stream.fileno())
    for attempt in range(attempts):
        try:
            _replace(temporary,path)
            return dict(published=True,attempts=attempt+1)
        except PermissionError as error:
            if attempt+1==attempts:
                return dict(published=False,attempts=attempts,preserved=str(temporary),error=repr(error))
            _sleep(delay)

