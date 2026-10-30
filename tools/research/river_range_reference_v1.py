"""Exact finite river payoff reference for a fixed opponent reach vector.

The vector is entry mass times opponent action-history likelihood at one public
state, before excluding hero cards. It must be common to all hero holdings;
hero-dependent policies or correlated policy mixtures require a separate model.
This is a reference calculation, not an opponent model or equilibrium solution.
"""
from itertools import combinations
import numpy as np
from stack_price_reference_v1 import board_group,price

class RiverRangeReference:
    def __init__(self,board,hands,ranks):
        board_group(board)
        expected=np.asarray(list(combinations([c for c in range(52) if c not in board],2)),dtype=np.int64)
        h=np.asarray(hands);r=np.asarray(ranks)
        if h.dtype.kind not in 'iu' or h.shape!=(1081,2) or not np.array_equal(h,expected):
            raise ValueError('Complete ordered board-legal holding list required')
        if r.dtype.kind not in 'iu' or r.shape!=(1081,) or np.any(r<0):
            raise ValueError('Exact nonnegative ranks, larger is stronger, required')
        self.hands=h.copy();self.ranks=r.copy();self.board=tuple(board)
        self.legal=((h[:,0,None]!=h[None,:,0])&(h[:,0,None]!=h[None,:,1])&
                    (h[:,1,None]!=h[None,:,0])&(h[:,1,None]!=h[None,:,1]))
        self.win=self.legal&(r[:,None]>r[None,:])
        self.tie=self.legal&(r[:,None]==r[None,:])
        self.loss=self.legal&(r[:,None]<r[None,:])
        assert np.all(self.legal.sum(1)==990)
        for a in (self.hands,self.ranks,self.legal,self.win,self.tie,self.loss):a.setflags(write=False)

    def masses(self,weights):
        raw=np.asarray(weights)
        if raw.dtype.kind not in 'fiu' or raw.shape!=(1081,):
            raise ValueError('One numeric weight per board-legal opponent holding required')
        w=raw.astype(np.float64)
        if not np.isfinite(w).all() or np.any(w<0) or not np.isfinite(w.sum()):
            raise ValueError('Finite nonnegative opponent mass with a finite total required')
        # Only positive summands; do not subtract blocked mass from totals.
        # This preserves tiny surviving ranges beside large blocked weights.
        mass=np.stack([np.einsum('ij,j->i',mask,w,dtype=np.float64,optimize=False)
                       for mask in (self.win,self.tie,self.loss)],axis=1)
        if not np.isfinite(mass).all():raise ValueError('Opponent mass overflow')
        return mass

    def values(self,weights,row):
        cash=price(row);mass=self.masses(weights);total=mass.sum(1);supported=total>0
        equity=np.divide(mass[:,0]+.5*mass[:,1],total,
                         out=np.full(1081,np.nan),where=supported)
        advantage=equity*cash['net_pot']-cash['call_cost']
        return dict(masses_win_tie_loss=mass,opponent_mass=total,supported=supported,
                    equity=equity,call_minus_fold_bb=advantage)
