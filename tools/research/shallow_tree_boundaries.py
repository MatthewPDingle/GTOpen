"""Extra native tree-level checks; the frozen candidate is never modified."""
import hashlib
import json
import numpy as np
import shallow_native_study as native


def run():
    native.checked();folder=native.OUT/'boundary-fixtures'
    fixtures=native.read(folder/'fixtures.json')['fixtures'];results=[]
    for i,f in enumerate(fixtures):
        out=folder/str(i);out.mkdir(exist_ok=True)
        native.parity(folder/f['file'],out/'tree.json',out)
        tree=native.read(out/'tree.json')
        leaf=next(n for n in tree['nodes'] if n['path']==[2,2,2,1])
        spr=min(tree['config']['stack']-v for v in leaf['invested'])/leaf['pot']
        assert abs(spr-f['target_spr'])<1e-12
        result=native.read(out/'shallow.json')
        flat=np.concatenate([np.array([h['action_values_counterfactual_bb'] for h in row['hands']]).ravel() for row in result['rows']])
        results.append(dict(spr=spr,values=flat.tolist(),checks=native.read(out/'parity.json')['checks']))
    changes={}
    for boundary in [.2,.75,1.]:
        rows=[r['values'] for r in results if abs(r['spr']-boundary)<2e-7]
        changes[str(boundary)]=float(np.ptp(rows,axis=0).max())
        assert changes[str(boundary)]<2e-5,changes
    inputs=[folder/'fixtures.json',native.ROOT/'crates/solver/examples/shallow_boundary_seed.rs',
            native.ROOT/'target/shallow-research/release/examples/shallow_boundary_seed.exe']
    native.write(native.OUT/'tree-boundary-check.json',dict(passed=True,fixtures=len(fixtures),results=results,
        max_counterfactual_boundary_change_bb=changes,
        input_sha256={p.relative_to(native.ROOT).as_posix():native.previous.pilot.sha(p) for p in inputs},
        production_enabled=False))
    print('Native tree boundary checks passed',changes,flush=True)


if __name__=='__main__':run()
