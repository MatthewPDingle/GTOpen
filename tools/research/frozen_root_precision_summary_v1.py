"""Descriptive fixed-policy root precision; no confidence or best-response claims."""
import numpy as np

CONTRASTS = ('call_minus_fold', 'raise_minus_fold', 'raise_minus_call')


def summarize(values, classes, masses):
    """Values are bank x original-global-deal-order x (fold,call,raise,jam)."""
    v=np.asarray(values,dtype=np.float64)
    c=np.asarray(classes)
    m=np.asarray(masses,dtype=np.float64)
    if (v.ndim!=3 or v.shape[0]!=4 or v.shape[2]!=4 or v.shape[1]<2
            or c.shape!=(v.shape[1],) or c.dtype.kind not in 'iu'
            or np.any((c<0)|(c>=169)) or not np.isfinite(v).all()
            or m.shape!=(169,) or not np.isfinite(m).all() or np.any(m<0)
            or abs(float(m.sum())-1)>1e-12):
        raise ValueError('Four finite fixed banks, explicit native classes and normalized entry masses required')
    differences=np.stack((v[:,:,1]-v[:,:,0],v[:,:,2]-v[:,:,0],v[:,:,2]-v[:,:,1]),axis=-1)
    parity=np.arange(len(c))%2
    banks=[]
    for b in range(4):
        rows=[]; error_sums=np.zeros(3); error_mass=0.; disagreement=0.; half_mass=0.
        for hand in range(169):
            ids=np.flatnonzero(c==hand); n=len(ids)
            means=differences[b,ids].mean(0).tolist() if n else None
            variance=differences[b,ids].var(0,ddof=1) if n>1 else None
            standard_error=np.sqrt(variance/n) if n>1 else None
            halves=[]
            for half in range(2):
                sub=ids[parity[ids]==half]
                action_means=v[b,sub,:3].mean(0) if len(sub) else None
                halves.append(dict(count=len(sub),
                    non_jam_action_means=action_means.tolist() if action_means is not None else None,
                    maximizing_non_jam_action=int(np.argmax(action_means)) if action_means is not None else None))
            if n>1:
                error_sums+=m[hand]*standard_error**2;error_mass+=m[hand]
            if all(h['count'] for h in halves):
                half_mass+=m[hand]
                if halves[0]['maximizing_non_jam_action']!=halves[1]['maximizing_non_jam_action']:
                    disagreement+=m[hand]
            rows.append(dict(hand_class=hand,count=n,entry_mass=float(m[hand]),
                contrast_means=means,sample_standard_deviations=np.sqrt(variance).tolist() if n>1 else None,
                descriptive_standard_errors=standard_error.tolist() if n>1 else None,halves=halves))
        banks.append(dict(bank=b,classes=rows,standard_error_covered_entry_mass=float(error_mass),
            rms_class_standard_error_on_covered_mass=np.sqrt(error_sums/error_mass).tolist() if error_mass else None,
            half_comparison_covered_entry_mass=float(half_mass),
            half_maximizer_disagreement_entry_mass=float(disagreement)))
    return dict(deals=len(c),contrasts=list(CONTRASTS),banks=banks,
        half_definition='Original global deal index modulo 2; no outcome-based split',
        action_order=['fold','call','raise','jam'],maximizer_actions=['fold','call','raise'],
        units='bb per entry; standard errors are descriptive, not simultaneous confidence intervals',
        jam_excluded_from_precision_comparison=True,exploratory=True,
        bounds_best_response_above=False,accuracy_qualified=False)
