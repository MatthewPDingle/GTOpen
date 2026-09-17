"""Prospective evaluation; coefficients and resulting policy are never refitted."""
import collections
import json
import numpy as np
import shallow_native_feedback as study

native=study.native
pilot=study.pilot


def bootstrap(m):
    rng=np.random.default_rng(m['bootstrap_seed']);groups=collections.defaultdict(list)
    for i,b in enumerate(m['boards']):groups[b['stratum']].append(i)
    draws=np.zeros((m['bootstrap_replicates'],len(m['boards'])))
    for b in range(len(draws)):
        for ids in groups.values():draws[b]+=np.bincount(rng.choice(ids,len(ids)),minlength=len(m['boards']))
    return draws


def weighted_error(prediction,reference,weight):
    return float((abs(prediction-reference)*weight).sum()/weight.sum()) if weight.sum()>0 else None


def leaf_estimates(m,rows,draws):
    estimates={};reports={}
    for case in m['cases']:
        c=native.fit.aggregate(case,rows[case['id']])
        mass,ev,residual,gain=native.fit.arrays(case,rows[case['id']])
        shape=(len(draws),2,169);den=(draws@mass.reshape(len(mass),-1)).reshape(shape)
        assert (den>0).all()
        direct=(draws@ev.reshape(len(ev),-1)).reshape(shape)/den
        corrected=c['raw']+(draws@residual.reshape(len(residual),-1)).reshape(shape)/den
        spr=case['stack']/case['pot']
        c.update(base_x=c['x'].copy(),base_names=list(c['names']))
        old=native.previous.prior.network.predict(c,study.read(native.previous.prior.MODEL)) if 1<=spr<=20 else c['balanced']
        predictions=dict(shallow=native.hybrid(c) if 0<spr<1 else old,baseline=old,balanced=c['balanced'])
        w=c['mass']*c['qualified'];qualified_mass=float(w.sum()/2)
        scores={model:{key:case['pot']*weighted_error(pred,c[key],w) for key in ['direct','corrected']}
                for model,pred in predictions.items()}
        improvements={key:float(1-scores['shallow'][key]/scores['baseline'][key]) for key in ['direct','corrected']}
        cis={}
        for key,boot in [('direct',direct),('corrected',corrected)]:
            reduction=((abs(predictions['baseline']-boot)-abs(predictions['shallow']-boot))*w).sum(axis=(1,2))/w.sum()*case['pot']
            cis[key]=np.quantile(reduction,[.025,.975]).tolist()
        reports[case['id']]=dict(pot=case['pot'],stack=case['stack'],qualified_pair_mass_fraction=qualified_mass,
            qualified_hand_classes=int(c['qualified'].sum()),mae_bb=scores,improvements=improvements,
            mae_reduction_95_interval_bb=cis,hand_records=[dict(hand=pilot.LABELS[k],side=side,
              qualified=bool(c['qualified'][side,k]),pair_mass=float(c['mass'][side,k]),
              br_gain_bb=float(case['pot']*c['gain'][side,k]),
              **{model+'_gross_bb':float(case['pot']*pred[side,k]) for model,pred in predictions.items()},
              direct_gross_bb=float(case['pot']*c['direct'][side,k]),corrected_gross_bb=float(case['pot']*c['corrected'][side,k]))
              for side in [0,1] for k in range(169)])
        estimates[case['node']]=dict(direct=case['pot']*c['direct'][0],corrected=case['pot']*c['corrected'][0],
            direct_boot=case['pot']*direct[:,0],corrected_boot=case['pot']*corrected[:,0],gain=case['pot']*c['gain'][0])
    return estimates,reports


def actions(tree,leaves,draws):
    values,info,reaches=native.tree_values(tree)
    old,_,_=native.tree_values(tree,shallow=False)
    balanced,_,_=native.tree_values(tree,shallow=False,balanced=True)
    terms,parent,den=study.action.terminal_coefficients(tree,info)
    predictions={name:v[parent['children']]/den for name,v in [('shallow',values),('baseline',old),('balanced',balanced)]}
    base=predictions['shallow'][[1,2]]
    refs={key:base.copy() for key in ['direct','corrected']}
    boots={key:np.broadcast_to(base,(len(draws),2,169)).copy() for key in refs}
    gain=np.zeros((2,169))
    for i,t in terms.items():
        if i not in leaves:continue
        a=t['action']-1;coefficient=t['coefficient'];leaf=leaves[i]
        for key in refs:
            refs[key][a]+=coefficient*(leaf[key]-info[i]['gross'])
            boots[key][:,a]+=coefficient*(leaf[key+'_boot']-info[i]['gross'])
        gain[a]+=coefficient*leaf['gain']
    # Independent full-tree substitution, separate from branch coefficients.
    reconstruction_error=0.
    for key in refs:
        substitute=values.copy()
        for nd in tree['nodes'][::-1]:
            i=nd['id']
            if i in leaves:substitute[i]=info[i]['factor']*(leaves[i][key]-nd['invested'][1])
            elif nd['kind']==0:
                child=substitute[nd['children']]
                substitute[i]=(child*np.array(nd['sigma']).reshape(-1,169)).sum(axis=0) if nd['actor']==1 else child.sum(axis=0)
        reconstruction_error=max(reconstruction_error,float(abs(substitute[np.array(parent['children'])[[1,2]]]/den-refs[key]).max()))
    assert reconstruction_error<2e-5,reconstruction_error
    counts,_=pilot.matrices();r=reaches[parent['id']]
    joint=counts*(r[1]/pilot.COMBOS)[:,None]*(r[0]/pilot.COMBOS)[None,:]
    mass=joint.sum(axis=1)/joint.sum();sigma=np.array(parent['sigma']).reshape(-1,169)
    qualified=(sigma[1]>=.0001)&(sigma[2]>=.0001)&(gain.max(axis=0)<=.025)
    call_qualified=(sigma[1]>=.0001)&(gain[0]<=.025)
    result={};records=[]
    for kind,mask in [('call_vs_raise',qualified),('call_vs_fold',call_qualified)]:
        w=mass*mask
        pred={n:p[2]-p[1] if kind=='call_vs_raise' else p[1]-p[0] for n,p in predictions.items()}
        truth={n:p[1]-p[0] if kind=='call_vs_raise' else p[0]+1 for n,p in refs.items()}
        errors={name:{key:weighted_error(p,t,w) for key,t in truth.items()} for name,p in pred.items()}
        cis={}
        for key,p in boots.items():
            delta=p[:,1]-p[:,0] if kind=='call_vs_raise' else p[:,0]+1
            reduced=(abs(pred['baseline']-delta)-abs(pred['shallow']-delta))@w/w.sum() if w.sum() else np.full(len(draws),np.nan)
            cis[key]=np.quantile(reduced,[.025,.975]).tolist() if w.sum() else None
        result[kind]=dict(qualified_hand_classes=int(mask.sum()),qualified_decision_pair_mass_fraction=float(w.sum()),
            pair_weighted_mae_bb=errors,mae_reduction_95_interval_bb=cis)
    direct_ci=np.quantile(boots['direct'][:,1]-boots['direct'][:,0],[.025,.975],axis=0)
    cv_ci=np.quantile(boots['corrected'][:,1]-boots['corrected'][:,0],[.025,.975],axis=0)
    for k,label in enumerate(pilot.LABELS):
        delta=predictions['shallow'][2,k]-predictions['shallow'][1,k]
        decision=study.action.classify(delta,direct_ci[:,k],cv_ci[:,k],sigma[1,k],sigma[2,k],gain[0,k],gain[1,k])
        records.append(dict(hand=label,call_frequency=float(sigma[1,k]),raise_frequency=float(sigma[2,k]),
            call_br_gain_bb=float(gain[0,k]),raise_br_gain_bb=float(gain[1,k]),decision=decision,
            shallow_delta_bb=float(delta),baseline_delta_bb=float(predictions['baseline'][2,k]-predictions['baseline'][1,k]),
            direct_delta_bb=float(refs['direct'][1,k]-refs['direct'][0,k]),corrected_delta_bb=float(refs['corrected'][1,k]-refs['corrected'][0,k]),
            direct_95_interval=direct_ci[:,k].tolist(),corrected_95_interval=cv_ci[:,k].tolist()))
    result.update(records=records,classification_counts=dict(collections.Counter(r['decision'] for r in records)),
                  max_independent_reconstruction_error_bb=reconstruction_error)
    return result


def evaluate():
    m=study.checked();rows=collections.defaultdict(list);hashes={}
    for j in m['jobs']:
        path=study.OUT/'jobs'/(j['id']+'.json');row=study.read(path)
        native.previous.old.validate(row,j,m);rows[j['case']].append(row);hashes[j['id']]=pilot.sha(path)
    for rr in rows.values():assert [r['job']['board'] for r in rr]==[b['board'] for b in m['boards']]
    draws=bootstrap(m);leaves,reports=leaf_estimates(m,rows,draws)
    action_results=actions(study.read(study.OUT/'shallow/tree.json'),leaves,draws)
    shallow=reports['fourbet-call']
    gates=dict(shallow_corrected_improvement=shallow['improvements']['corrected']>=.1,
        shallow_qualified_mass=shallow['qualified_pair_mass_fraction']>=.95,
        shallow_direct_nonregression=shallow['improvements']['direct']>=-.05)
    for kind in ['call_vs_fold','call_vs_raise']:
        e=action_results[kind]['pair_weighted_mae_bb']
        for key in ['direct','corrected']:
            gates[kind+'_'+key+'_nonregression']=e['shallow'][key] is not None and e['shallow'][key]<=e['baseline'][key]+1e-9
    result=dict(manifest_id=m['id'],evaluated_at=study.now(),leaf_reports=reports,actions=action_results,gates=gates,
        primary_feedback_pass=all(gates.values()),reference_count=len(m['jobs']),
        reference_seconds=sum(r['seconds'] for rr in rows.values() for r in rr),
        max_cpu_gap_pct=max(r['gap_pct'] for rr in rows.values() for r in rr),
        max_gpu_gap_pct=max(r['gpu_gap_pct'] for rr in rows.values() for r in rr),job_sha256=hashes,production_enabled=False)
    study.write(study.OUT/'evaluation.json',result)
    print(json.dumps({k:v for k,v in result.items() if k not in ['leaf_reports','actions','job_sha256']},indent=2),flush=True)


if __name__=='__main__':evaluate()
