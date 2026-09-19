"""Monte Carlo conditioning on six observed folds, with policies fixed."""
import time
import numpy as np
import wizard_continuation_study as s


def estimate(t):
    # Sufficient statistics: mass, squared mass, fold/call/jam four-bet
    # responses, jam call probability numerator, jam action value numerator.
    return np.r_[t[2:5]/t[0],t[5:7]/t[0]]


def run():
    dest=s.OUT/'folded-card-audit.json';assert not dest.exists(),'Preserve completed evidence'
    history=s.read(s.OUT/'fold-history.json');a=s.read(s.OUT/'premium-branches.json')
    root=history['path'];node=lambda suffix:next(n for n in a['nodes'] if n['path']==root+suffix)
    sigma4=np.array(node([2])['view']['strategy']).reshape(3,169)
    sigmajam=np.array(node([3])['view']['strategy']).reshape(2,169)
    probs={r['actor']:np.array(r['probabilities']) for r in history['actions']}
    assert len(probs)==8 and set(probs)==set(range(8))
    assert np.allclose(probs[2],node([])['view']['reaches_all'][2],atol=1e-6)
    assert all(r['label']=='Fold' for r in history['actions'][2:])
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    deck=np.array([c for c in range(52) if c not in (48,49)],dtype=np.int16)
    seats=[0,2,3,4,5,6,7];n=50000;row=np.arange(n);batches=[];start=time.monotonic()
    for batch in range(40):
        rng=np.random.default_rng(19092600+batch)
        cards=np.broadcast_to(deck,(n,50)).copy()
        # Partial Fisher-Yates: ordered deals without replacement.
        for i in range(14):
            j=rng.integers(i,50,size=n);tmp=cards[:,i].copy()
            cards[:,i]=cards[row,j];cards[row,j]=tmp
        dealt=cards[:,:14]
        assert (np.diff(np.sort(dealt,axis=1),axis=1)>0).all()
        x,y=dealt[:,::2],dealt[:,1::2];hi=np.maximum(x//4,y//4);lo=np.minimum(x//4,y//4)
        cls=np.where((x%4==y%4)|(hi==lo),hi*13+lo,lo*13+hi)
        lj=cls[:,seats.index(2)];live=probs[2][lj];folded=live.copy()
        for k,seat in enumerate(seats):
            if seat!=2:folded*=probs[seat][cls[:,k]]
        metrics=[]
        for w in (live,folded):
            call=sigmajam[1,lj]
            value=(1-call)*27.5+call*(397.5*eq[168,lj]-194)
            metrics.append(np.r_[w.sum(),w@w,sigma4[:,lj]@w,w@call,w@value])
        batches.append(metrics)
    b=np.array(batches);total=b.sum(axis=0);rows=[];replicas=[]
    labels=['fourbet_fold','fourbet_call','fourbet_jam','jam_call','jam_ev_bb']
    for i,name in enumerate(('two_live_hands','including_six_folds')):
        point=estimate(total[i]);jk=np.array([estimate(total[i]-r[i]) for r in b]);replicas.append(jk)
        se=np.sqrt(39/40*((jk-jk.mean(axis=0))**2).sum(axis=0))
        rows.append(dict(mode=name,estimates=dict(zip(labels,point.tolist())),monte_carlo_se=dict(zip(labels,se.tolist())),
            effective_samples=float(total[i,0]**2/total[i,1])))
    delta=estimate(total[1])-estimate(total[0]);jk=replicas[1]-replicas[0]
    se=np.sqrt(39/40*((jk-jk.mean(axis=0))**2).sum(axis=0))
    analytic=next(r for r in s.read(s.OUT/'premium-card-audit.json')['results'] if r['weighting']=='compatible')
    truth=np.r_[analytic['fourbet_reply_probabilities'],analytic['jam_call_probability'],analytic['jam_bb']]
    errors=estimate(total[0])-truth
    baseline_se=np.array(list(rows[0]['monte_carlo_se'].values()))
    assert (np.abs(errors)<5*baseline_se+1e-5).all(),(errors,baseline_se)
    result=dict(draws=2000000,batches=40,seed_rule='19092600 + batch index',hero_cards=[48,49],results=rows,
        fold_conditioning_change=dict(zip(labels,delta.tolist())),paired_monte_carlo_se=dict(zip(labels,se.tolist())),
        two_hand_analytic_errors=dict(zip(labels,errors.tolist())),elapsed_seconds=time.monotonic()-start,
        source_hashes={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in [s.OUT/'fold-history.json',s.OUT/'premium-branches.json',s.OUT/'premium-card-audit.json',s.OUT/'folded-card-protocol.md',s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'tools/research/wizard_folded_cards.py']},
        limitation='Conditions on physical hole cards and observed folds using frozen policies; showdown uses sampled two-hand class equity, so folded-card effects on board outcomes are NOT included. No policy adaptation. Monte Carlo errors exclude model and equity-cache uncertainty.')
    s.write(dest,result)
    print(result)


if __name__=='__main__':run()
