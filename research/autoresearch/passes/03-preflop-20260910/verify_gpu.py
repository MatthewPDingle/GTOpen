"""Compare frozen GPU runs to their original control without altering evidence."""
import json
from pathlib import Path
HERE=Path(__file__).resolve().parent
runs=[json.loads(s) for s in (HERE/'events.jsonl').read_text().splitlines()]
runs=[r for r in runs if r.get('returncode')==0 and r.get('rows')]
def key(r):
 init=next(x for x in r['rows'] if x['phase']=='init')
 return (r['fixture_sha256'],r['iterations'],init['model'],init['start_iteration'])
def result(r): return next(x for x in r['rows'] if x['phase']=='result')
controls={key(r):r for r in runs if r['id'].startswith('baseline-')}
out=[]
for r in runs:
 if key(r) not in controls: continue
 a=controls[key(r)]; x,y=result(a),result(r)
 same={f:x[f]==y[f] for f in ['arena_hash','iteration','gaps','evs']}
 out.append({'run':r['id'],'control':a['id'],'exact':all(same.values()),'checks':same})
(HERE/'gpu-parity.json').write_text(json.dumps(out,indent=2)+'\n')
failed=[r['run'] for r in out if not r['exact']]
print(f'{len(out)} GPU runs compared; mismatches: {failed}')
if failed: raise SystemExit(1)
