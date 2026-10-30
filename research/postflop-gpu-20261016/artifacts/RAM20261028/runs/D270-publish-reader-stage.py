import shutil,sys,urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'epoch'));import common as h
H=ROOT/'runs/D270-actual-metadata-CPU';p=H/'reader-repair-protocol.json';dest=h.ar.DASHBOARD/'evidence'/H.name/p.name
shutil.copyfile(p,dest)
with urllib.request.urlopen(h.ar.LIVE+'/research/postflop-gpu-20261016/evidence/'+H.name+'/'+p.name,timeout=20)as z:assert z.read()==p.read_bytes()
with h.ar.exclusive_lock(h.ar.STATUS.with_suffix('.lock'),timeout=3):
    s=h.read(h.ar.STATUS);e=next(x for x in s['experiments']if x['id']=='E115')
    e.update(updated_at=h.now(),stage='18 native CPU cases complete; additive full reader replay',correctness='Native18 cases pass; whole-output readback pending corrected action-kind/eligibility oracle',reason='Original reader mistook positive child count for action kind; chance nodes are patched to52. Native source also shows original full-arena5% rule makes only two-tone iso-on eligible. Original16/2 forecast retained as unmet. Corrected reader derives action kind/CPU physical offsets/compact predicate from all immutable original plans, retaining all18 cases/53fields/23arrays/every record/canary. No source/predicate/case change or native rerun. No candidate GPU/speed samples.')
    e['evidence'].append({'label':'Read-only reader repair and preserved forecast failure','url':'evidence/'+H.name+'/'+p.name})
    s.update(updated_at=h.now(),stage='Metadata layout: complete retained-output replay',activity='All18 actual CPU cases completed once; corrected read-only whole-output replay running. Fixed candidate predicate remains unchanged and applies only to compact layouts. E080 remains live; no new qualified gain.')
    h.ar.atomic_json(h.ar.STATUS,s)
print('Reader repair protocol and retained-output stage HTTP byte-verified.',flush=True)
