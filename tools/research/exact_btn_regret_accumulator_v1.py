"""Exact counterfactual sums for BTN's first response to a BB root shove.

Separate research state, not a sampled reservoir or format-1 preflop table.
Every update integrates reach once. No live trainer currently imports this.
"""
import re
import numpy as np


def vector(value):
    a=np.asarray(value,dtype=np.float64)
    if a.shape!=(169,) or not np.isfinite(a).all():raise ValueError('169 finite class slots required')
    return a


class ExactBtnRegrets:
    def __init__(self,context_sha256,entry_mass):
        if not isinstance(context_sha256,str) or not re.fullmatch('[0-9a-f]{64}',context_sha256):
            raise ValueError('Fixed context identity required')
        mass=vector(entry_mass)
        if np.min(mass)<0 or abs(mass.sum()-1)>1e-12:raise ValueError('Normalized incoming class population required')
        self.context_sha256=context_sha256;self.mass=mass.copy();self.steps=0
        self.regrets=np.zeros((169,2));self.reach=np.zeros(169)

    def step(self,iteration,call_probability,jam_mass,fold_entries,call_entries):
        if type(iteration) is not int or iteration!=self.steps+1:raise ValueError('One sequential update per played generation required')
        call=np.asarray(call_probability,dtype=np.float64)
        supported=self.mass>0
        if call.shape!=(169,) or not np.isfinite(call[supported]).all() or np.any(call[supported]<0) or np.any(call[supported]>1):
            raise ValueError('Valid current played BTN policy required on incoming classes')
        call=np.where(supported,call,0.)
        reach,fold,pay=[vector(x) for x in (jam_mass,fold_entries,call_entries)]
        if np.min(reach)<0 or np.any(reach>self.mass+1e-12):raise ValueError('Shove reach must be part of incoming class mass')
        if np.any(reach[~supported]) or np.any(fold[reach==0]) or np.any(pay[reach==0]):
            raise ValueError('Absent or zero-reach classes cannot contribute payoff')
        values=np.stack([fold,pay],axis=1)
        sigma=np.stack([1-call,call],axis=1)
        baseline=np.sum(sigma*values,axis=1)
        delta=np.zeros((169,2));conditional_reach=np.zeros(169)
        # These entries already contain the opponent's reach. Divide only by
        # fixed incoming BTN class mass, never by current shove reach here.
        delta[supported]=(values[supported]-baseline[supported,None])/self.mass[supported,None]
        conditional_reach[supported]=reach[supported]/self.mass[supported]
        new=self.regrets+delta;total=self.reach+conditional_reach
        if not np.isfinite(new).all() or not np.isfinite(total).all():raise ValueError('Counterfactual accumulator overflow')
        if np.max(abs(np.sum(sigma*delta,axis=1)))>1e-10:raise ValueError('Own-policy centring identity failed')
        self.regrets=new;self.reach=total;self.steps=iteration
        return delta.copy()

    def probabilities(self,fallback):
        p=np.asarray(fallback,dtype=np.float64)
        if p.shape!=(169,2) or not np.isfinite(p).all() or np.min(p)<0 or np.max(abs(p.sum(1)-1))>1e-12:
            raise ValueError('Normalized fold/call fallback required')
        p=p.copy()
        for c in np.flatnonzero(self.reach>0):
            positive=np.maximum(self.regrets[c],0.)
            if positive.sum()>0:p[c]=positive/positive.sum()
            else:p[c]=[float(a==int(np.argmax(self.regrets[c]))) for a in range(2)]
        return p

    def document(self):
        return dict(format=1,method='exact-btn-first-response-counterfactual-v1',context_sha256=self.context_sha256,
            entry_mass=self.mass.tolist(),completed_updates=self.steps,regret_sums=self.regrets.tolist(),
            conditional_reach_sums=self.reach.tolist(),sampled_observations_added=0,
            meaning='Sum of exact per-incoming-class counterfactual regrets; opponent reach included once. Not conditional per-visit means.')

    @classmethod
    def restore(cls,document,*,context_sha256,entry_mass):
        result=cls(context_sha256,entry_mass)
        if document.get('format')!=1 or document.get('method')!='exact-btn-first-response-counterfactual-v1' or document.get('context_sha256')!=context_sha256:
            raise ValueError('Unknown accumulator or changed context')
        if not np.array_equal(vector(document['entry_mass']),result.mass):raise ValueError('Changed incoming population')
        steps=document['completed_updates'];regrets=np.asarray(document['regret_sums'],dtype=np.float64);reach=vector(document['conditional_reach_sums'])
        if type(steps) is not int or steps<0 or regrets.shape!=(169,2) or not np.isfinite(regrets).all():raise ValueError('Invalid accumulator state')
        if document['sampled_observations_added']!=0 or np.min(reach)<0 or np.max(reach)>steps+1e-10:
            raise ValueError('Invalid update/reach accounting')
        if np.any(regrets[reach==0]) or np.any(reach[result.mass==0]):raise ValueError('No counterfactual regret without reach')
        result.steps=steps;result.regrets=regrets.copy();result.reach=reach.copy();return result
