"""Synthetic preservation-gate controls; never reported as poker outcomes."""
import copy
import hashlib
import json
from pathlib import Path
import source_panel_comparison as comparison

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/representative-coverage-20260919'
source_path=ROOT/'research/preflop-evolution/integrated-coverage-20260919/panel-ab-result.json'
source=json.loads(source_path.read_text())
control=copy.deepcopy(source)
control['preflop_unchanged']=True
control['records'][-1]['evaluation']['postflop_gap_total']=0.
result=comparison.compare(source,control)
assert result['ev_change_bb']==[0.,0.]
assert result['original_full_gap_bb']==result['rebuilt_full_gap_bb']
mutations={
    'board_panel':lambda d:d['manifest'].__setitem__('bet_menu','75'),
    'chance_weights':lambda d:d['board_weights'].__setitem__(0,d['board_weights'][0]*1.01),
    'preflop_policy':lambda d:d['records'][-1]['evaluation']['preflop_policy'][0][0].__setitem__(0,.12345),
    'normalizer':lambda d:d.__setitem__('root_normalizer',d['root_normalizer']*1.01),
    'frequency':lambda d:d['records'][-1]['evaluation']['root_frequencies'].__setitem__(0,.12345),
    'hand_mass':lambda d:d['records'][-1]['evaluation']['hands'][0].__setitem__('root_mass',.12345),
}
rejected=[]
for name,mutate in mutations.items():
    altered=copy.deepcopy(control)
    mutate(altered)
    try:
        comparison.compare(source,altered)
    except AssertionError:
        rejected.append(name)
    else:
        raise AssertionError('Accepted changed '+name)
paths=[source_path,Path(__file__),Path(comparison.__file__)]
proof=dict(passed=True,synthetic_identity_accepted=True,rejected=rejected,
           strategic_reconstruction_performed=False,
           inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths})
with (OUT/'source-panel-comparison-controls.json').open('x') as f:
    json.dump(proof,f,indent=2)
print(json.dumps(proof))
