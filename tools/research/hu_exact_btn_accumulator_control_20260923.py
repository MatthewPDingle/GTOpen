"""Compare exact BTN updates with scalar population expectation of sampled visits."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import math
from pathlib import Path
import time
import numpy as np
import psutil
from later_average_support_v1 import OUT,read,load_complete_cache
from sampled_physical_root_evaluation_v1 import ROOT,sha,save,hand_class
from preflop_allin_matrix_v1 import AllinMatrix
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from reboot_research_idle_v1 import idle

PREFIX='exact-btn-accumulator-control-v1'
GENERATIONS=(0,25,51,77)


def main():
    start=time.monotonic();last=[0.]
    def guard():
        assert time.monotonic()-start<120
        if time.monotonic()-last[0]>2:
            assert idle() and psutil.virtual_memory().available>20_000_000_000;last[0]=time.monotonic()
    guard();inputs={}
    def admit(path):path=Path(path);inputs[str(path)]=sha(path);return read(path)
    ap=admit(OUT/'allin-generation-attribution-v1-result.json')
    arpath=OUT/'allin-generation-attribution-v1-registration.json';ar=admit(arpath)
    aa=admit(OUT/'allin-generation-attribution-v1-independent-review.json')
    assert aa['passed'] and aa['result_sha256']==sha(OUT/'allin-generation-attribution-v1-result.json')
    assert ap['registration_sha256']==sha(arpath)
    gp=next(Path(p) for p in ap['artifacts'] if Path(p).name=='visible_302-generation-policies.json')
    assert sha(gp)==ap['artifacts'][str(gp)];old=admit(gp)['policies'];catalog=admit(ar['catalog'])['native_observations']
    mr,mp,ma=[admit(OUT/f'preflop-allin-matrix-control-v1-{s}.json') for s in ('registration','result','independent-review')]
    assert ma['passed'] and ma['result_sha256']==sha(OUT/'preflop-allin-matrix-control-v1-result.json')
    matrix_path=Path(mp['matrix_artifact']);assert sha(matrix_path)==mp['matrix_sha256']==ma['matrix_sha256']
    cp=OUT/'bb-context-candidate.json';context=admit(cp);source=cp.read_text();matrix=AllinMatrix(admit(matrix_path),source)
    cache=load_complete_cache();cr=admit(OUT/'complete-private-allin-cache-v2-registration.json');population=admit(cr['population'])
    for p in (Path(__file__),ROOT/'tools/research/exact_btn_regret_accumulator_v1.py',ROOT/'tools/research/preflop_allin_matrix_v1.py'):
        inputs[str(p)]=sha(p)
    rp=OUT/f'{PREFIX}-registration.json'
    save(rp,dict(inputs=inputs,generations=list(GENERATIONS),synthetics=['zero-jam','all-jam','reach-weighting-reversal'],
        maximum_seconds=120,production_modified=False,gpu_used=False,
        scope='Pure expected-update/accumulator control on old fixed policies; not a trained candidate or deployed table.'))
    state=ExactBtnRegrets(sha(cp),matrix.btn_mass);scalar=np.zeros((169,2));maximum=0.;checks=[]
    root_node=context['nodes'][0];jam_node=context['nodes'][root_node['children'][3]]
    folded,called=[context['nodes'][i] for i in jam_node['children']]
    rake=called['pot']*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    net=called['pot']-rake;fold_value=folded['leaf']['utilities'][1]
    for index,name in enumerate([*GENERATIONS,'zero-jam','all-jam'],1):
        guard();root=np.zeros((169,4));calls=np.full(169,np.nan)
        if isinstance(name,int):
            for row,p in zip(catalog,old[name]):
                if row['player']==0:root[row['hand_class']]=p
                else:calls[row['hand_class']]=p[1]
        else:
            root[:,3 if name=='all-jam' else 0]=1.;calls[matrix.btn_mass>0]=.37
        exact=matrix.evaluate(root,calls);before=state.regrets.copy()
        delta=state.step(index,calls,exact['btn_jam_mass'],exact['btn_fold_entries'],exact['btn_call_entries'])
        pieces=[[[] for _ in range(2)] for _ in range(169)];reach=[[] for _ in range(169)]
        for j,row in enumerate(population['rows']):
            if j%4096==0:guard()
            cards=row['private_cards'];b,t=hand_class(cards[:2]),hand_class(cards[2:]);label=cache.rows[tuple(cards)]
            mass=row['probability']*root[b,3];reach[t].append(mass)
            call_value=(label['losses']*(net-called['invested'][1])+label['ties']*(net/2-called['invested'][1])-label['wins']*called['invested'][1])/label['boards']
            baseline=(1-calls[t])*fold_value+calls[t]*call_value
            for a,q in enumerate((fold_value,call_value)):pieces[t][a].append(mass*(q-baseline))
        expected=np.zeros((169,2))
        for c in np.flatnonzero(matrix.btn_mass>0):
            for a in range(2):expected[c,a]=math.fsum(pieces[c][a])/matrix.btn_mass[c]
        maximum=max(maximum,float(np.max(abs(expected-delta))));scalar+=expected
        assert np.max(abs(scalar-state.regrets))<1e-9
        if name=='zero-jam':assert np.array_equal(before,state.regrets) and not np.any(delta)
        saved=state.document();restored=ExactBtnRegrets.restore(saved,context_sha256=sha(cp),entry_mass=matrix.btn_mass)
        assert restored.document()==saved
        fallback=np.full((169,2),.5);p=state.probabilities(fallback)
        assert np.all(p>=0) and np.max(abs(p.sum(1)-1))<1e-12
        assert np.array_equal(p[matrix.btn_mass==0],fallback[matrix.btn_mass==0])
        checks.append(dict(policy=str(name),maximum_increment_error=float(np.max(abs(expected-delta))),
            reachable_classes=int(np.count_nonzero(exact['btn_jam_mass'])),sampled_records_added=0))
    # A rare +100 call opportunity must not outweigh a common -2 opportunity.
    mass=np.zeros(169);mass[0]=1.;toy=ExactBtnRegrets('0'*64,mass);call=np.full(169,.5)
    for i,(r,q) in enumerate(((.01,100.),(1.,-2.)),1):
        reach=np.zeros(169);reach[0]=r;pay=np.zeros(169);pay[0]=r*q
        toy.step(i,call,reach,np.zeros(169),pay)
    correct=toy.probabilities(np.full((169,2),.5))[0].tolist()
    assert correct==[1.,0.] and np.argmax(np.array([-50.,50.])+[1.,-1.])==1
    rejected=[];stable=state.document();last_step=state.steps
    exact=matrix.evaluate(root,calls)
    def reject(label,fn):
        try:fn()
        except ValueError:rejected.append(label)
        else:raise AssertionError(f'Did not reject {label}')
        assert state.document()==stable
    reject('duplicate-update',lambda:state.step(last_step,calls,exact['btn_jam_mass'],exact['btn_fold_entries'],exact['btn_call_entries']))
    reject('reach-outside-population',lambda:state.step(last_step+1,calls,matrix.btn_mass+1.,exact['btn_fold_entries'],exact['btn_call_entries']))
    reject('zero-reach-nonzero-payoff',lambda:state.step(last_step+1,calls,np.zeros(169),exact['btn_fold_entries'],exact['btn_call_entries']))
    reject('nonfinite-payoff',lambda:state.step(last_step+1,calls,exact['btn_jam_mass'],np.full(169,np.nan),exact['btn_call_entries']))
    reject('changed-context',lambda:ExactBtnRegrets.restore(stable,context_sha256='1'*64,entry_mass=matrix.btn_mass))
    changed=matrix.btn_mass.copy();a,b=np.flatnonzero(changed>0)[:2];d=changed[b]/10;changed[a]+=d;changed[b]-=d
    reject('changed-population',lambda:ExactBtnRegrets.restore(stable,context_sha256=sha(cp),entry_mass=changed))
    for p,h in inputs.items():assert sha(p)==h,p
    guard();assert maximum<1e-9
    result=dict(passed=True,registration_sha256=sha(rp),policies=checks,maximum_scalar_increment_error_bb=maximum,
        maximum_cumulative_error_bb=float(np.max(abs(scalar-state.regrets))),reach_weighted_toy_policy=correct,
        naive_unweighted_toy_policy=[0.,1.],invalid_cases_rejected=rejected,checkpoint_roundtrips=6,
        seconds=time.monotonic()-start,gpu_used=False,training_integration=False,production_modified=False,
        limitation='Certifies pure update arithmetic and reach weighting, not a complete trainer, poker convergence or actual variance improvement.')
    save(OUT/f'{PREFIX}-result.json',result);print(result)


if __name__=='__main__':main()
