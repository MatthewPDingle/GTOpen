"""Prepare, execute and independently evaluate the small GPU parity gate."""
import os
import subprocess
import sys
import numpy as np
import card_compatible_hu as ref
import wizard_continuation_study as s

OUT=ref.OUT
BINARY=s.ROOT/'target/release/examples/card_compatible_hu_gpu.exe'


def run():
    assert not (OUT/'gpu-fixtures.json').exists(),'Preserve registered inputs'
    result=s.read(OUT/'results.json')
    for path,digest in result['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    counts,_,_,_=ref.card_pairs()
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    fixtures=[]
    for row in result['results']:
        _,a,b,_=ref.game(np.array(row['weights']),counts,eq,row['pot'],row['hero_add'],row['opponent_add'])
        fixtures.append(dict(name=row['name'],a=a.tolist(),b=b.ravel().tolist()))
    paths=[BINARY,OUT/'reference.cu',OUT/'GPU-PROTOCOL.md',OUT/'results.json',s.ROOT/'crates/solver/examples/card_compatible_hu_gpu.rs',s.ROOT/'tools/research/card_compatible_hu_gpu.py']
    s.write(OUT/'gpu-fixtures.json',dict(fixtures=fixtures,iterations=1000,inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths}))
    assert s.idle()[0],'Production is busy; leave registered job for review'
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    subprocess.run([str(BINARY),str(OUT/'gpu-fixtures.json'),str(OUT/'reference.cu'),str(OUT/'gpu-policies.json')],env=env,cwd=s.ROOT,check=True)
    review()


def review():
    fixtures=s.read(OUT/'gpu-fixtures.json')
    for path,digest in fixtures['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    gpu=s.read(OUT/'gpu-policies.json');cpu=s.read(OUT/'results.json')
    assert gpu['iterations']==1000 and len(gpu['policies'])==len(fixtures['fixtures'])
    rows=[]
    for f,policy,r in zip(fixtures['fixtures'],gpu['policies'],cpu['results']):
        p=np.array(policy);assert p.shape==(338,) and np.isfinite(p).all() and (p>=0).all() and (p<=1).all()
        a=np.array(f['a']);b=np.array(f['b']).reshape(169,169)
        gap,value=ref.gap_value(a,b,p[:169],p[169:]);error=abs(value-r['exact']['value_bb'])
        assert gap<=.001 and error<=gap+1e-7,(f['name'],gap,error)
        old=np.r_[r['compatible_policies']['hero_jam'],r['compatible_policies']['opponent_call']]
        rows.append(dict(name=f['name'],gap_bb=gap,value_bb=value,lp_value_error_bb=error,max_policy_difference=float(abs(old-p).max())))
    s.write(OUT/'gpu-review.json',dict(results=rows,compile_seconds=gpu['compile_seconds'],execution_seconds=gpu['execution_seconds'],
        note='Three-block correctness prototype only; no full-tree speed or memory claim.'))
    print(rows)


if __name__=='__main__':{'run':run,'review':review}[sys.argv[1]]()
