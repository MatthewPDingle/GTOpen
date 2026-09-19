"""Decoded quality checks and independent physical flop pair-mass audit."""
import sys
import numpy as np
import aa_joint_response_study as t


def main():
    m=t.checked();partial='--partial' in sys.argv
    fixtures=t.s.read(t.OUT/'fixtures.json');labels=fixtures['labels']
    hands=[(a,b) for a in range(52) for b in range(a+1,52)]
    masks=np.array([(1<<a)|(1<<b) for a,b in hands],dtype=np.uint64)
    classes=np.array([max(a//4,b//4)*13+min(a//4,b//4) if a%4==b%4 or a//4==b//4 else min(a//4,b//4)*13+max(a//4,b//4) for a,b in hands])
    max_mass_error=max_mean_error=max_gain=0.;done=0;digests={}
    for j in m['jobs']:
        path=t.OUT/'jobs'/(j['id']+'.json')
        if not path.exists():
            assert partial,j['id']
            continue
        r=t.s.read(path);t.validate(r,j,m)
        board=j['board'];boardmask=np.uint64(sum(1<<(4*'23456789TJQKA'.index(board[i])+'cdhs'.index(board[i+1])) for i in range(0,6,2)))
        available=(masks&boardmask)==0
        weights=[]
        for p,key in enumerate(['range_oop','range_ip']):
            parsed={h:float(v) for term in j['config'][key].split(',') for h,v in [term.split(':')]}
            # The actual parser stores weights as float32.
            perclass=np.array([parsed.get(h,0) for h in labels],dtype=np.float32).astype(float)
            weights.append(perclass[classes]*available)
        aa=(classes==168)&available
        valid=(masks[aa,None]&masks[None,:])==0
        expected=float(weights[0][aa]@(valid@weights[1]))
        actual=next(h['pair_mass'] for h in r['hands'][0] if h['hand']=='AA')
        relative=abs(actual-expected)/max(expected,1e-20)
        assert relative<2e-6,(j['id'],expected,actual)
        max_mass_error=max(max_mass_error,relative)
        for p,rows in enumerate(r['hands']):
            mean=sum(h['pair_mass']*h['ev_bb'] for h in rows)/sum(h['pair_mass'] for h in rows)
            error=abs(mean-r['means_bb'][p]);assert error<1e-6
            max_mean_error=max(max_mean_error,error)
        decoded={h['hand']:h for h in r['hands'][0]}
        expected_probes=[h for h in fixtures['probes'] if not (len(h)==2 and board[::2].count(h[0])==3)]
        assert set(expected_probes)<=decoded.keys()
        gains=[decoded[h]['br_ev_bb']-decoded[h]['ev_bb'] for h in expected_probes]
        assert max(gains)<=.05+1e-9
        max_gain=max(max_gain,max(gains));done+=1
        digests[j['id']]=t.s.sha(path)
    result=dict(completed=done,total=len(m['jobs']),max_aa_pair_mass_relative_error=max_mass_error,
        max_mean_reconstruction_error_bb=max_mean_error,max_decoded_probe_br_gain_bb=max_gain,
        manifest_id=m['id'],result_hashes=digests)
    if not partial:t.s.write(t.OUT/'validation.json',result)
    print({k:v for k,v in result.items() if k!='result_hashes'})


if __name__=='__main__':main()
