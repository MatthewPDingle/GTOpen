import sys, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D270-actual-metadata-CPU';P=h.read(H/'protocol.json')
for p,d in P['input_sha256'].items():h.pin(p,d)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/protocol.json',timeout=20)as z:assert z.read()==(H/'protocol.json').read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E115')
    e.update(updated_at=h.now(),stage='Actual production metadata: full crate CPU replay',correctness='D267 model and actual host types pass; D270 actual helper replay running',reason='Frozen18 actual-crate CPU cases across all6 original full plans: original captured locks, exceptional scalar bits and real capability selection. Whole53-field plans/23 projected arrays/full arena records/capacities/canaries retained for root replay. No candidate GPU or speed samples.')
    e['evidence'].append({'label':'Frozen actual production CPU replay','url':'evidence/'+H.name+'/protocol.json'})
    s.update(updated_at=h.now(),state='running',goal_status='active',active_experiment='E115',stage='Metadata layout: actual production CPU replay',activity='D270 compiling/running original18 fixed CPU cases and complete raw reader. No candidate GPU/speed samples yet; E080/GPU/compressed/16/default affinity remains live. All original1%/fixture/fresh16/material/holdout/cumulative/app gates remain.')
    h.ar.atomic_json(h.ar.STATUS,s)
print('D270 frozen replay protocol and stage published.',flush=True)
