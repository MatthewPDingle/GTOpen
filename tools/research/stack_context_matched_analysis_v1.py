"""The frozen seven-depth complete-policy comparison, independent of training.

Inputs are per-deal native full-policy values, not network scores. All final
contrasts and uncertainty rules come from the admitted learning protocol.
"""
from statistics import NormalDist
import numpy as np
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison, differences, CONTRAST_NAMES, PROFILE_NAMES

DEPTHS=(20,40,60,100,150,200,400)
DEALS=4096
ALPHA=.05


def quantile_linear(values, probability):
    values=np.asarray(values,dtype=np.float64)
    if values.ndim!=1 or not len(values) or not np.isfinite(values).all() or not 0<=probability<=1:
        raise ValueError('Finite nonempty vector and bounded quantile required')
    # Explicit convention for reproducible tails across NumPy versions.
    ordered=np.sort(values); point=(len(ordered)-1)*probability
    low=int(np.floor(point)); high=int(np.ceil(point)); fraction=point-low
    return float(ordered[low]*(1-fraction)+ordered[high]*fraction)


def context_analysis(values, *, depth, dead_money):
    if depth not in DEPTHS:
        raise ValueError('Unregistered stack depth')
    values=np.asarray(values,dtype=np.float64)
    if values.shape!=(DEALS,2,4,2) or not np.isfinite(values).all():
        raise ValueError('Exactly the fixed fresh deal count and eight profiles are required')
    comparison=CompletePolicyComparison(stack=depth,dead_money=dead_money,deals=DEALS,alpha=ALPHA/len(DEPTHS))
    comparison.add(values); result=comparison.finish(); delta=differences(values)
    z=NormalDist().inv_cdf(1-ALPHA/(2*len(DEPTHS)*len(CONTRAST_NAMES)))
    for index,row in enumerate(result['contrasts']):
        loss=-delta[:,index]
        row['negative_deal_fraction']=float(np.mean(delta[:,index]<0))
        row['paired_loss_95_bb']=quantile_linear(loss,.95)
        row['paired_loss_99_bb']=quantile_linear(loss,.99)
        row['worst_observed_paired_loss_bb']=float(loss.max())
        row['mean_positive_paired_loss_bb']=float(np.maximum(loss,0).mean())
        row['exploratory_normal_interval']=dict(lower=row['mean']-z*row['standard_error'],
            upper=row['mean']+z*row['standard_error'],z=z,finite_sample_guarantee=False)
    ranges=[]
    flat=values.reshape(DEALS,8,2)
    for index,name in enumerate(PROFILE_NAMES):
        ranges.append(dict(profile=name,minimum_player_value_bb=flat[:,index].min(0).tolist(),
                           maximum_player_value_bb=flat[:,index].max(0).tolist()))
    result.update(depth=depth,dead_money=dead_money,split='heldout' if depth in (60,150) else 'fit',
        per_deal_value_ranges=ranges,scope='Fresh complete-policy fixed-opponent values, not a best-response or equilibrium certificate',
        tail_convention='Signed paired loss = baseline value minus candidate value; linear empirical quantiles; negative loss is a gain',
        exploratory_normal_family_size=len(DEPTHS)*len(CONTRAST_NAMES),exploratory_normal_finite_sample_guarantee=False)
    return result


def finish(contexts):
    if not isinstance(contexts,list) or len(contexts)!=len(DEPTHS):
        raise ValueError('All seven final context analyses required')
    ordered=sorted(contexts,key=lambda row:row['depth'])
    if tuple(row['depth'] for row in ordered)!=DEPTHS:
        raise ValueError('Missing, duplicate or unregistered depth')
    for context in ordered:
        if (context['deals']!=DEALS or context['family_error_probability']!=ALPHA/len(DEPTHS)
                or context['profile_order']!=list(PROFILE_NAMES)
                or tuple(row['name'] for row in context['contrasts'])!=CONTRAST_NAMES
                or any(row['count']!=DEALS for row in context['contrasts'])):
            raise ValueError('Changed budget, ordering or uncertainty allocation')
        for row in context['contrasts']:
            if (not all(np.isfinite(row[key]) for key in ('mean','lower','upper'))
                    or not row['lower']<=row['mean']<=row['upper']):
                raise ValueError('Invalid saved comparison interval')
    pooled=[]
    for index,name in enumerate(CONTRAST_NAMES):
        parts=[context['contrasts'][index] for context in ordered]
        pooled.append(dict(name=name,mean=float(np.mean([row['mean']/context['depth'] for row,context in zip(parts,ordered)])),
            lower=float(np.mean([row['lower']/context['depth'] for row,context in zip(parts,ordered)])),
            upper=float(np.mean([row['upper']/context['depth'] for row,context in zip(parts,ordered)])),
            units='starting-stack fraction per entry',equal_depth_weight=1/len(DEPTHS)))
    positive=all(row['lower']>0 for row in pooled)
    negative=[dict(depth=context['depth'],name=row['name'],mean_bb=row['mean'])
              for context in ordered for row in context['contrasts'] if row['mean']<0]
    return dict(format=1,contexts=ordered,equal_depth_normalized_gains=pooled,
        simultaneous_family_alpha=ALPHA,primary_method='Average endpoints of simultaneous bounded empirical-Bernstein intervals over 56 contrasts',
        all_eight_pooled_lower_bounds_positive=positive,negative_depth_point_estimates=negative,
        registered_policy_improvement_criterion_met=positive and not negative,
        fixed_policy_evaluation_complete=True,preflop_accuracy_qualified=False,production_promotion=False,
        statement='Conditional comparison of these frozen trained banks in the registered fixed-entry HU family; no best-response bound, equilibrium claim, or all-position accuracy claim')
