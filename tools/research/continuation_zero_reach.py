"""N31 read-only current/average zero-reach branch audit; no fitting or GPU work."""
import datetime as dt
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[2]
BASE = ROOT/'research/preflop-evolution/continuation'
OUT = BASE/'zero-reach-20260916'
BIN = ROOT/'target/learned-interface-filtered/release/examples/continuation_zero_reach.exe'

def read(p): return json.loads(p.read_text())
def write(p,v): p.write_text(json.dumps(v,indent=2)+'\n',encoding='utf-8',newline='\n')
def sha(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()

def run():
    assert dt.datetime.now(dt.timezone.utc)<dt.datetime(2026,9,16,20,49,2,tzinfo=dt.timezone.utc)
    assert not OUT.exists(), 'Refuse to overwrite partial or completed audit'
    OUT.mkdir()
    cases=[]
    for arm in ['original','candidate']:
        cases.append((f'eight-{arm}',BASE/f'policy-stability-20260916/{arm}/1500/policy.gtop'))
    for stack in [40,100]:
        for arm in ['original','balanced','candidate']:
            cases.append((f'hu{stack}-{arm}',BASE/f'heads-up-settling-20260916/{stack}/{arm}/1500/policy.gtop'))
    paths=read(BASE/'current-policy-20260916/paths.json')
    write(OUT/'paths.json',[r['candidate']['path'] for r in paths['rows']])
    write(OUT/'empty-paths.json',[])
    inputs=[Path(__file__),BIN,ROOT/'crates/solver/examples/continuation_zero_reach.rs',
            ROOT/'crates/solver/src/preflop/mod.rs',ROOT/'crates/solver/src/preflop/convergence_quality.rs',
            ROOT/'cache/preflop_eq169.bin',ROOT/'cache/realization_fit.json',
            BASE/'full-precision-20260916/double/interface.cu',OUT/'paths.json',OUT/'empty-paths.json']
    inputs += [p for _,p in cases]
    inputs += [BASE/f'current-policy-20260916/{arm}.json' for arm in ['original','candidate']]
    hashes={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in inputs}
    write(OUT/'input-freeze.json',dict(registered_at=dt.datetime.now(dt.timezone.utc).isoformat(),inputs=hashes,
          hypothesis='Does positivity gating switch learned/Balanced continuation between current and average strategies?',
          scope='Read-only CPU f32 reconstruction; no labels, payoffs, policy changes or production access.'))
    rows=[]
    for name,source in cases:
        path_file=OUT/('paths.json' if name.startswith('eight') else 'empty-paths.json')
        target=OUT/f'{name}.json'
        with (OUT/f'{name}.log').open('w',encoding='utf-8',newline='\n') as log:
            subprocess.run([str(BIN),str(source),str(path_file),str(target)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
        data=read(target)
        validation=0.
        if name.startswith('eight'):
            old=read(BASE/f"current-policy-20260916/{name.split('-')[1]}.json")
            for selected in data['selected']:
                expected=next(n for n in old['nodes'] if n['path']==selected['path'])
                for mode in ['current','average']:
                    validation=max(validation,max(abs(x-y) for x,y in zip(selected[mode],expected[f'{mode}_prefix_mass_by_seat'])))
            assert validation<1e-6,validation
        row={k:data[k] for k in ['eligible_hu_terminals','current_learned_enabled','average_learned_enabled','current_own_zero_positive_opponents','average_own_zero_positive_opponents']}
        row.update(case=name,flipped_terminals=len(data['flips']),selected_mass_validation_max=validation,
                   maximum_current_counterfactual_mass=max((t['current_counterfactual_mass'] for f in data['flips'] for t in f['traversers']),default=0.))
        rows.append(row);print(json.dumps(row),flush=True)
    for p,expected in hashes.items(): assert sha(ROOT/p)==expected,p
    write(OUT/'result.json',dict(rows=rows,inputs_unchanged=True,production_enabled=False,
          output_hashes={f'{name}.json':sha(OUT/f'{name}.json') for name,_ in cases},
          caveat='CPU-reconstructed reach positivity at one checkpoint. Independent-class counterfactual mass is a diagnostic, not legal-card reach, additive gap attribution or evidence that a flip is incorrect.'))

if __name__=='__main__':run()
