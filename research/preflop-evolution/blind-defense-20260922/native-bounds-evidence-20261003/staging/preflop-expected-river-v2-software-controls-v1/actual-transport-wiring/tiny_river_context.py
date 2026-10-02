import json,sys
from pathlib import Path
assert sys.argv[1:]==['--output-byte-limit=64000000']
source=Path(__file__).read_text();raw=sys.stdin.read();request=json.loads(raw)
print(json.dumps(dict(format=3,mode=request['mode'],context_source=source,request_source=raw,
    queries=dict(context_source=source,batch_source=raw),targets=[])))
sys.stderr.write('tiny software export\n')
