"""Normalize outcome masses before applying tie shares, including subnormals."""
import numpy as np
from river_range_reference_v1 import RiverRangeReference as OriginalRangeReference
from stack_price_reference_v1 import price

class RiverRangeReference(OriginalRangeReference):
    def values(self,weights,row):
        cash=price(row);mass=self.masses(weights);total=mass.sum(1)
        if not np.isfinite(total).all() or not np.isfinite([cash['net_pot'],cash['call_cost']]).all():
            raise ValueError('Finite accumulated opponent mass and public payoff required')
        supported=total>0
        # Taking half of the smallest positive float before division erases a tie.
        outcome_probability=np.divide(mass,total[:,None],out=np.full_like(mass,np.nan),where=supported[:,None])
        equity=outcome_probability[:,0]+.5*outcome_probability[:,1]
        advantage=equity*cash['net_pot']-cash['call_cost']
        if not np.isfinite(advantage[supported]).all():raise ValueError('Payoff arithmetic overflow')
        return dict(masses_win_tie_loss=mass,opponent_mass=total,supported=supported,
                    equity=equity,call_minus_fold_bb=advantage)
