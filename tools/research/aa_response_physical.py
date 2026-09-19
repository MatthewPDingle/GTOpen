"""Freeze, run and summarize the physical TT/AKo response audit."""
import subprocess
import sys
import numpy as np
from scipy.stats import t as student
import aa_joint_response_study as study
import conditional_hu_audit as c
s=study.s
OUT=study.OUT
BINARY=s.ROOT/'target/release/examples/aa_response_physical.exe'
HISTORY=s.OUT/'fold-history.json'
POLICY=c.OUT/'compatible_fresh.json'


def prepare():
    assert not (OUT/'physical-freeze.json').exists()
    paths=[BINARY,HISTORY,POLICY,OUT/'PHYSICAL-PROTOCOL.md',
        s.ROOT/'tools/research/aa_response_physical.py',s.ROOT/'crates/solver/examples/aa_response_physical.rs']
    s.write(OUT/'physical-freeze.json',dict(inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths}))


def checked():
    data=s.read(OUT/'physical-freeze.json')
    for path,digest in data['inputs'].items():assert s.sha(s.ROOT/path)==digest,path


def run():
    checked();assert s.idle()[0],'Production busy'
    subprocess.run([str(BINARY),str(HISTORY),str(POLICY),str(OUT/'physical-batches.json')],cwd=s.ROOT,check=True)
    review()


def review():
    checked();raw=s.read(OUT/'physical-batches.json');fixtures=s.read(OUT/'fixtures.json')
    g=c.Game(s.read(c.OUT/'subtree.json'),True)
    policy={int(i):np.array(v) for i,v in s.read(POLICY)['records'][-1]['policy'].items()}
    records=[];cut=student.ppf(.975,39)
    for hand in ['TT','AKo']:
        h=fixtures['labels'].index(hand)
        batches=[b for b in raw['batches'] if b['hand']==hand];assert len(batches)==40
        components=np.array([b['sums'] for b in batches])
        for q in study.FRACTIONS:
            reach=policy[0][3].copy();reach[168]=1-q
            mass=g.conditional[1][h]@reach
            cache=float((g.payoffs[1,11][h]-g.payoffs[1,10][h])@reach/mass)
            values=[];influences=[]
            for mode,label in enumerate(raw['modes']):
                parts=components[:,mode]
                likelihood=parts[:,0,0]+(1-q)*parts[:,1,0]
                win=parts[:,0,2]+(1-q)*parts[:,1,2]
                sumsq=parts[:,0,1]+(1-q)**2*parts[:,1,1]
                equity=win.sum()/likelihood.sum()
                influence=397.5*(win-equity*likelihood)/likelihood.mean()
                se=float(influence.std(ddof=1)/np.sqrt(40));value=float(397.5*equity-182.)
                values.append(value);influences.append(influence)
                records.append(dict(hand=hand,q=q,mode=label,call_ev_bb=value,se_bb=se,
                    ci95_bb=[value-cut*se,value+cut*se],effective_samples=float(likelihood.sum()**2/sumsq.sum()),
                    cached_two_hand_ev_bb=cache))
            difference=values[1]-values[0]
            se=float((influences[1]-influences[0]).std(ddof=1)/np.sqrt(40))
            records[-1]['paired_fold_effect_bb']=difference
            records[-1]['paired_fold_effect_ci95_bb']=[difference-cut*se,difference+cut*se]
    s.write(OUT/'physical-review.json',dict(results=records,draws_per_hand=raw['draws_per_hand'],
        note='Batch delta-method Monte Carlo intervals with t39 critical value. Physical holdings and shared boards; fixed ranges, no cached equities in samples.'))
    print([r for r in records if r['q']==0])


if __name__=='__main__':{'prepare':prepare,'run':run,'review':review}[sys.argv[1]]()
