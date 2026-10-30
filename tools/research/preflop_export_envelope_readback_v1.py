"""Independent closed-form readback of frozen preflop export and planning results."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import hashlib
import json
import math
from pathlib import Path
import numpy as np
from board_prefix_publication_v1 import atomic_json

ROOT=Path('T:/Dev/GTOpen');OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
EXPORT='complete-preflop-bank-export-control-v1';SCREEN='preflop-proposal-envelope-screen-v1'
RESULT=OUT/'preflop-export-envelope-readback-v1.json'
SOURCE=Path('S:/GTOpen-research/weighted-complete-river-continuation-v1')

def read(p):return json.loads(Path(p).read_bytes())
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert not RESULT.exists()
    checked={};results=[]
    def check(p,h):
        p=str(p);assert sha(p)==h,p;checked[p]=h
    for name in (EXPORT,SCREEN):
        rp=OUT/(name+'-registration.json');p=OUT/(name+'-result.json');r=read(p)
        assert r['passed'] and r['registration_sha256']==sha(rp)
        check(rp,sha(rp));check(p,sha(p))
        for path,digest in read(rp)['inputs'].items():check(path,digest)
        for path,digest in r.get('artifacts',{}).items():check(path,digest)
        results.append(r)
    exported,screen=results;reg=read(OUT/(EXPORT+'-registration.json'))
    banks=[];maximum_policy=maximum_reach=0.
    for identity,row in zip(reg['bank_identities'],exported['banks']):
        assert identity['arm']==row['arm'];check(row['file'],row['sha256'])
        for ref in identity['played_models']:check(SOURCE/row['arm']/'objects'/ref['file'],ref['sha256'])
        d=read(row['file']);p=np.asarray(d['cpu_policy']);g=np.asarray(d['cuda_policy'])
        r=np.asarray(d['cpu_own_reach']);s=np.asarray(d['cuda_own_reach'])
        pe=float(np.max(abs(p-g)));re=float(np.max(abs(r-s)))
        assert pe==row['policy_max_absolute_error'] and re==row['own_reach_max_absolute_error']
        assert pe<reg['policy_absolute_tolerance'] and re<reg['own_reach_absolute_tolerance']
        maximum_policy=max(maximum_policy,pe);maximum_reach=max(maximum_reach,re)
        t={i:np.tile([1.,0.,0.,0.],(169,1)) for i in (0,3,6,9,12)}
        for entry,policy in zip(d['rows'],p):t[entry['node']][entry['hand_class']]=policy
        banks.append(t)
    matrix=read(OUT/'preflop-allin-matrix-control-v1-matrix.json')
    mass=np.asarray(matrix['class_mass']);allin=np.stack((matrix['bb_showdown_entries'],matrix['btn_showdown_entries']),axis=2)
    flop=[];terminal=[]
    for seed in (0,1):
        for b,t in ((0,0),(0,1),(1,0),(1,1)):
            bb,btn=banks[2*seed+b],banks[2*seed+t]
            p0=bb[0][:,None,:];p3=btn[3][None,:,:];p6=bb[6][:,None,:]
            p9=bb[9][:,None,:];p12=btn[12][None,:,:]
            f1=np.broadcast_to(p0[:,:,0],(169,169));f4=p0[:,:,2]*p3[:,:,0]
            f7=p0[:,:,2]*p3[:,:,2]*p6[:,:,0];f10=p0[:,:,2]*p3[:,:,3]*p9[:,:,0]
            f13=p0[:,:,3]*p12[:,:,0]
            c2=np.broadcast_to(p0[:,:,1],(169,169));c5=p0[:,:,2]*p3[:,:,1]
            c8=p0[:,:,2]*p3[:,:,2]*p6[:,:,1]
            j11=p0[:,:,2]*p3[:,:,3]*p9[:,:,1];j14=p0[:,:,3]*p12[:,:,1]
            assert np.max(abs(f1+f4+f7+f10+f13+c2+c5+c8+j11+j14-1.))<1e-12
            flop.append(c2+c5+c8)
            folds=(f1[:,:,None]*[-1.,1.5]+(f4+f13)[:,:,None]*[2.5,-2.]+(f7+f10)[:,:,None]*[-6.,6.5])
            terminal.append(np.sum(mass[:,:,None]*folds+(j11+j14)[:,:,None]*allin,axis=(0,1)))
    contrasts=((2,0,0),(3,1,0),(1,0,1),(3,2,1),(6,4,0),(7,5,0),(5,4,1),(7,6,1))
    widths=[];error=0.
    for (new,old,seat),record in zip(contrasts,screen['contrasts']):
        width=200.25*(flop[new]+flop[old]);widths.append(width)
        c=terminal[new][seat]-terminal[old][seat]+.25*np.sum(mass*(flop[new]-flop[old]))
        comparisons=((c,record['integrated_center']),
            (np.sum(mass*width),record['expected_half_width']),
            (np.sum(mass*flop[new]),record['new_postflop_probability']),
            (np.sum(mass*flop[old]),record['old_postflop_probability']))
        error=max(error,*[abs(float(a)-b) for a,b in comparisons])
    z=float(np.sum(mass*np.max(widths,axis=0)))
    error=max(error,abs(z-screen['global_candidate_half_width_Z']))
    additive=7*2*z*math.log(640)/(3*16383)
    error=max(error,abs(additive-screen['fixed_16384_deal_additive_bernstein_term']))
    assert error<1e-10
    atomic_json(RESULT,dict(passed=True,source_sha256=sha(__file__),verified_files=len(checked),
        inputs=checked,played_model_references_checked=440,preflop_policy_max_absolute_error=maximum_policy,
        own_reach_max_absolute_error=maximum_reach,closed_form_recompute_max_error=error,
        candidate_half_width_Z=z,fixed_16384_deal_additive_term=additive,
        new_training_deals=0,new_evaluation_deals=0,gpu_used=False,
        decision='Do not launch a fresh evaluation with this broad postflop-reach envelope. Its width remains unhelpfully large and exceeds the existing shared-mixture planning bound.',
        accuracy_claim=False,production_modified=False))
    print(json.dumps({k:v for k,v in read(RESULT).items() if k!='inputs'}),flush=True)

if __name__=='__main__':main()
