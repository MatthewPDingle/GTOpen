"""Policy-independent class-pair matrices for the fixed all-in endpoints.

This groups already exact physical-pair probabilities and payouts. It does not
replace either player's incoming range, invent hole-card frequencies, or supply
postflop values. Full-population provenance and class-constant policies must be
certified by the caller. No training code imports this implementation.
"""
import hashlib
import json
import math
import numpy as np
from finite_btn_response_v1 import integrate
from sampled_physical_root_evaluation_v1 import hand_class


def build(source,population,cache_rows):
    # Existing checked validation includes role ordering, uniqueness, normalized
    # finite mass, complete integer board counts and terminal economics.
    integrate(source,population,np.full((169,4),.25),np.full(169,.5),cache_rows)
    context=json.loads(source);root=context['nodes'][0]
    jam=context['nodes'][root['children'][3]]
    folded,called=[context['nodes'][i] for i in jam['children']]
    root_fold=context['nodes'][root['children'][0]]
    if root_fold['leaf']['type']!='fold':raise ValueError('BB fold terminal required')
    rake=called['pot']*context['rake_fraction']
    if context['rake_cap']>0:rake=min(rake,context['rake_cap'])
    net=called['pot']-rake
    mass=np.zeros((169,169));bb=np.zeros_like(mass);btn=np.zeros_like(mass)
    for row in population['rows']:
        cards=row['private_cards'];b,t=hand_class(cards[:2]),hand_class(cards[2:])
        label=cache_rows[tuple(cards)];p=row['probability'];n=label['boards']
        bvalue=-called['invested'][0]+net*(label['wins']+.5*label['ties'])/n
        tvalue=-called['invested'][1]+net*(label['losses']+.5*label['ties'])/n
        mass[b,t]+=p;bb[b,t]+=p*bvalue;btn[b,t]+=p*tvalue
    conserved=called['pot']-sum(called['invested'])-rake
    if abs(math.fsum(mass.ravel())-1)>1e-12 or np.max(abs(bb+btn-mass*conserved))>1e-11:
        raise ValueError('Matrix probability or cashflow identity failed')
    return dict(format=1,context_sha256=hashlib.sha256(source.encode()).hexdigest(),
        class_mass=mass.tolist(),bb_showdown_entries=bb.tolist(),btn_showdown_entries=btn.tolist(),
        bb_fold=float(root_fold['leaf']['utilities'][0]),bb_uncontested=float(folded['leaf']['utilities'][0]),
        btn_fold=float(folded['leaf']['utilities'][1]),conserved_showdown_total=conserved,
        canonical_population_rows=len(population['rows']),
        scope='Fixed population and terminal economics; class-constant first-own-action all-in policies only.')


class AllinMatrix:
    def __init__(self,document,source):
        if document['format']!=1 or document['context_sha256']!=hashlib.sha256(source.encode()).hexdigest():
            raise ValueError('Matrix context or format mismatch')
        self.mass,self.bb,self.btn=[np.asarray(document[k],dtype=np.float64) for k in
                                   ('class_mass','bb_showdown_entries','btn_showdown_entries')]
        if any(x.shape!=(169,169) or not np.isfinite(x).all() for x in (self.mass,self.bb,self.btn)):
            raise ValueError('Finite 169-by-169 matrices required')
        if np.min(self.mass)<0 or abs(math.fsum(self.mass.ravel())-1)>1e-12:
            raise ValueError('Normalized nonnegative class-pair mass required')
        self.bb_mass=self.mass.sum(1);self.btn_mass=self.mass.sum(0)
        self.bb_fold=float(document['bb_fold']);self.bb_win=float(document['bb_uncontested']);self.btn_fold=float(document['btn_fold'])
        if not all(math.isfinite(x) for x in (self.bb_fold,self.bb_win,self.btn_fold)):
            raise ValueError('Finite fold payouts required')
        if np.max(abs(self.bb+self.btn-self.mass*document['conserved_showdown_total']))>1e-11:
            raise ValueError('Class-pair cashflow identity failed')

    def evaluate(self,root,btn_call):
        root=np.asarray(root,dtype=np.float64);call=np.asarray(btn_call,dtype=np.float64)
        if root.shape!=(169,4) or not np.isfinite(root).all() or np.min(root)<0 or np.max(abs(root.sum(1)-1))>1e-12:
            raise ValueError('Normalized BB policies required for all classes')
        if call.shape!=(169,):raise ValueError('169 BTN class slots required')
        supported=self.btn_mass>0
        if not np.isfinite(call[supported]).all() or np.any(call[supported]<0) or np.any(call[supported]>1):
            raise ValueError('Finite valid BTN call probabilities required on supported classes')
        # Only truly absent incoming classes may have an undefined probability.
        call=np.where(supported,call,0.)
        bb_jam=self.mass@(1-call)*self.bb_win+self.bb@call
        bb_fold=self.bb_mass*self.bb_fold
        bb_gains=(root[:,0]+root[:,3])*np.maximum(bb_fold,bb_jam)-root[:,0]*bb_fold-root[:,3]*bb_jam
        jam_mass=self.mass.T@root[:,3]
        btn_call_entries=self.btn.T@root[:,3];btn_fold_entries=jam_mass*self.btn_fold
        btn_base=(1-call)*btn_fold_entries+call*btn_call_entries
        btn_gains=np.maximum(btn_fold_entries,btn_call_entries)-btn_base
        if np.min(bb_gains)<-1e-10 or np.min(btn_gains)<-1e-10:
            raise ValueError('Restricted best-response gains cannot be negative')
        return dict(bb_gain=math.fsum(bb_gains),btn_gain=math.fsum(btn_gains),
            bb_entries=self.bb_mass.copy(),bb_fold_entries=bb_fold,bb_jam_entries=bb_jam,bb_class_gains=bb_gains,
            btn_entries=self.btn_mass.copy(),btn_jam_mass=jam_mass,btn_fold_entries=btn_fold_entries,
            btn_call_entries=btn_call_entries,btn_class_gains=btn_gains)
