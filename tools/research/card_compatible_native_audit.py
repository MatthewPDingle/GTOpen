"""Compare unmodified GPU engine policies against both independent LP oracles."""
import os
import subprocess
import sys
import numpy as np
import card_compatible_hu as ref
import wizard_continuation_study as s

OUT=ref.OUT
BINARY=s.ROOT/'target/release/examples/card_compatible_native_audit.exe'


def run():
    assert not (OUT/'native-freeze.json').exists(),'Preserve registered evidence'
    assert s.idle()[0],'Production is busy'
    paths=[BINARY,OUT/'NATIVE-PROTOCOL.md',s.ROOT/'tools/research/card_compatible_native_audit.py',
           s.ROOT/'crates/solver/examples/card_compatible_native_audit.rs',
           s.ROOT/'crates/solver/src/preflop/mod.rs',s.ROOT/'crates/solver/src/preflop/gpu.rs',
           s.ROOT/'crates/solver/src/preflop/kernels.cu',s.ROOT/'cache/preflop_eq169.bin']
    s.write(OUT/'native-freeze.json',dict(inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths}))
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    subprocess.run([str(BINARY),str(OUT/'native-policies.json')],env=env,cwd=s.ROOT,check=True)
    review()


def review():
    frozen=s.read(OUT/'native-freeze.json')
    for path,digest in frozen['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    counts,combos,_,_=ref.card_pairs();independent=combos[:,None]*combos[None,:]
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    rows=[];oracles={}
    for row in s.read(OUT/'native-policies.json')['results']:
        stack=row['stack'];x=np.array(row['hero_jam']);y=np.array(row['opponent_call'])
        assert np.isfinite(x).all() and np.isfinite(y).all()
        assert ((x>=0)&(x<=1)).all() and ((y>=0)&(y<=1)).all()
        if stack not in oracles:
            oracles[stack]={}
            for name,chance in [('independent',independent),('compatible',counts)]:
                _,a,b,_=ref.game(np.ones((2,169)),chance,eq,3.,stack-1,stack-2)
                xl,yl,lp=ref.exact(a,b)
                oracles[stack][name]=(a,b,lp,xl,yl)
        result=dict(stack=stack,iteration=row['iteration'],models={})
        for name,(a,b,lp,xl,yl) in oracles[stack].items():
            gap,value=ref.gap_value(a,b,x,y)
            result['models'][name]=dict(gap_bb=gap,value_bb=value,lp=lp,
                hero_jam_percent=float(100*(combos/1326)@xl),opponent_call_policy=yl.tolist())
        model=result['models']['independent']
        result['cpu_value_error_bb']=abs(model['value_bb']-(row['cpu_evs'][0]+1))
        result['gpu_value_error_bb']=abs(model['value_bb']-(row['gpu_evs'][0]+1))
        result['cpu_gap_error_bb']=abs(model['gap_bb']-sum(row['cpu_gaps']))
        result['gpu_gap_error_bb']=abs(model['gap_bb']-sum(row['gpu_gaps']))
        assert max(result[k] for k in ['cpu_value_error_bb','gpu_value_error_bb','cpu_gap_error_bb','gpu_gap_error_bb'])<=.0001,result
        rows.append(result)
        print(stack,row['iteration'],'independent gap',model['gap_bb'],'compatible gap',result['models']['compatible']['gap_bb'])
    s.write(OUT/'native-review.json',dict(results=rows,passed=True,
        note='Existing engine verified against independent-class oracle; compatible-game evaluation is model sensitivity, not a production patch.'))
    lines=['# Existing GPU engine: independently reproduced','',
        'All eight exported policies passed independent value and best-response-gap reconstruction within 0.0001 chip. This isolates a chance-model difference, rather than a CPU/GPU disagreement. Production remains unchanged.','',
        '| Stack | Iterations | Native-model gap | Compatible-model gap | Native-policy compatible value | Compatible minimax value |',
        '|---|---:|---:|---:|---:|---:|']
    for r in rows:
        a=r['models']['independent'];b=r['models']['compatible']
        lines.append(f"| {r['stack']:g} | {r['iteration']} | {a['gap_bb']:.6f} | {b['gap_bb']:.6f} | {b['value_bb']:.6f} | {b['lp']['value_bb']:.6f} |")
    lines+=['','Units are the configured chip units (posts 1 and 2), not straddle-normalized big blinds. Values add back the SB post to make folding worth zero. Chance counts are exact; cached class equities remain sampled.',
        '', 'These uniform-range, heads-up push/fold trees are deliberately small. They do not measure full-tree performance, model the saved eight-player game, or establish that a similarly small root gap implies accurate rare-branch ranges.',
        '', '[Frozen protocol](NATIVE-PROTOCOL.md) · [Inputs](native-freeze.json) · [Native outputs](native-policies.json) · [Independent review](native-review.json)']
    (OUT/'NATIVE-RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':{'run':run,'review':review}[sys.argv[1]]()
