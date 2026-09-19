"""Certify the existing experimental two-player interface against an independent LP."""
import os
import subprocess
import sys
import numpy as np
import card_compatible_hu as ref
import wizard_continuation_study as s

OUT=ref.OUT
BINARY=s.ROOT/'target/release/examples/card_compatible_interface_audit.exe'
KERNEL=s.ROOT/'research/preflop-evolution/continuation/learned-interface-20260916/interface.cu'


def run():
    assert not (OUT/'interface-freeze.json').exists(),'Preserve evidence'
    assert s.idle()[0],'Production is busy'
    paths=[BINARY,KERNEL,OUT/'INTERFACE-PROTOCOL.md',s.ROOT/'tools/research/card_compatible_interface_audit.py',
           s.ROOT/'crates/solver/examples/card_compatible_interface_audit.rs',
           s.ROOT/'crates/solver/src/preflop/gpu/learned_interface.rs',
           s.ROOT/'crates/solver/src/preflop/gpu.rs',s.ROOT/'crates/solver/src/preflop/mod.rs',
           s.ROOT/'crates/solver/src/preflop/kernels.cu',s.ROOT/'cache/preflop_eq169.bin']
    s.write(OUT/'interface-freeze.json',dict(inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths}))
    env=dict(os.environ);env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    subprocess.run([str(BINARY),str(OUT/'interface-policies.json'),str(KERNEL)],env=env,cwd=s.ROOT,check=True)
    review()


def review():
    frozen=s.read(OUT/'interface-freeze.json')
    for path,digest in frozen['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    counts,_,_,_=ref.card_pairs()
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    rows=[];oracles={}
    for row in s.read(OUT/'interface-policies.json')['results']:
        stack=row['stack'];x=np.array(row['hero_jam']);y=np.array(row['opponent_call'])
        assert np.isfinite(x).all() and np.isfinite(y).all()
        assert ((x>=0)&(x<=1)).all() and ((y>=0)&(y<=1)).all()
        if stack not in oracles:
            _,a,b,_=ref.game(np.ones((2,169)),counts,eq,3.,stack-1,stack-2)
            _,_,lp=ref.exact(a,b);oracles[stack]=(a,b,lp)
        a,b,lp=oracles[stack];gap,value=ref.gap_value(a,b,x,y)
        result=dict(stack=stack,iteration=row['iteration'],gap_bb=gap,value_bb=value,lp=lp,
            value_error_bb=abs(value-(row['gpu_evs'][0]+1)),gap_error_bb=abs(gap-sum(row['gpu_gaps'])),
            conservation_error_bb=abs(sum(row['gpu_evs'])))
        assert max(result[k] for k in ['value_error_bb','gap_error_bb','conservation_error_bb'])<=.0001,result
        if row['iteration']==10000:assert gap<=.001,result
        rows.append(result);print(result)
    s.write(OUT/'interface-review.json',dict(results=rows,passed=True,
        note='Existing zero-rake HU research interface passed independent minimax checks. Not validation of multiway reset or learned postflop values.'))
    lines=['# Existing research interface passes independent equilibrium check','',
        'The earlier legal-pair interface passes the new independent LP certificate on all four heads-up push/fold fixtures. No application changes were needed. Learned continuation pricing was disabled.',
        '', '| Stack | Iterations | Independently measured gap | GPU value reconstruction error | GPU gap reconstruction error |',
        '|---|---:|---:|---:|---:|']
    for r in rows:lines.append(f"| {r['stack']:g} | {r['iteration']} | {r['gap_bb']:.8f} | {r['value_error_bb']:.8f} | {r['gap_error_bb']:.8f} |")
    lines+=['','Every 10,000-iteration result passes the preregistered 0.001-chip gap gate. Native GPU values and gaps agree with independent reconstruction within 0.0001 chip. Total net utility is conserved within that tolerance.',
        '', 'This validates the existing GPU down/up traversal with card-compatible fold and showdown values in this restricted two-player game. It is stronger than simply verifying a fixed terminal equity calculation. It does not validate earlier multiplayer actions, the heads-up chance reset inside a larger tree, nonzero rake, learned continuation values, or general full-game convergence.',
        '', 'The ordinary CPU query functions still use independent-class chance. Their outputs are deliberately marked as belonging to a different model. Experimental saves would also retain ordinary metadata; none were written. These are concrete integration gaps that must be resolved before deployment.',
        '', '[Protocol](INTERFACE-PROTOCOL.md) · [Input hashes](interface-freeze.json) · [GPU output](interface-policies.json) · [Independent review](interface-review.json)']
    (OUT/'INTERFACE-RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


if __name__=='__main__':{'run':run,'review':review}[sys.argv[1]]()
