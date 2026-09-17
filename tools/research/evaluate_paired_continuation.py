"""Prospective paired-context screen; fixed model, paired board uncertainty."""
import collections
import numpy as np
import paired_continuation_study as study
import evaluate_shallow_native_feedback as old_eval


def evaluate():
    m=study.checked();candidate=study.read(study.OUT/'candidate.json');rows=collections.defaultdict(list);hashes={}
    for j in m['jobs']:
        path=study.OUT/'jobs'/(j['id']+'.json');row=study.read(path)
        study.native.previous.old.validate(row,j,m);rows[j['case']].append(row);hashes[j['id']]=study.pilot.sha(path)
    draws=old_eval.bootstrap(m);results={};gates={};boot_reductions=[]
    for family,tree_path in m['trees'].items():
        cases=[c for c in m['cases'] if c['family']==family]
        p=study.model.pack(study.read(study.ROOT/tree_path),cases,rows)
        result=study.model.score(p,candidate)
        boot={key:np.broadcast_to(p['base_delta'],(len(draws),169)).copy() for key in ['direct','corrected']}
        for c in p['contexts']:
            case=c['case']; rr=rows[case['id']]
            assert [r['job']['board'] for r in rr]==[b['board'] for b in m['boards']]
            mass,ev,residual,_=study.native.fit.arrays(case,rr)
            den=draws@mass[:,0];assert (den>0).all()
            sampled=dict(direct=case['pot']*(draws@ev[:,0])/den,
                         corrected=case['pot']*(c['raw'][0]+(draws@residual[:,0])/den))
            term=p['terms'][case['node']];sign=1 if term['action']==2 else -1
            for key in boot:
                boot[key]+=sign*term['coefficient']*(sampled[key]-p['info'][case['node']]['gross'])
        w=p['mass']*p['qualified'];w/=w.sum();pred=study.model.action_prediction(p,candidate)
        reductions={key:(abs(p['base_delta']-truth)-abs(pred-truth))@w for key,truth in boot.items()}
        boot_reductions.append(reductions['corrected'])
        result['mae_reduction_95_interval_bb']={key:np.quantile(v,[.025,.975]).tolist() for key,v in reductions.items()}
        result['hands']=[dict(hand=h,qualified=bool(p['qualified'][k]),baseline_delta_bb=float(p['base_delta'][k]),
                             candidate_delta_bb=float(pred[k]),direct_delta_bb=float(p['reference_delta']['direct'][k]),
                             corrected_delta_bb=float(p['reference_delta']['corrected'][k]),
                             call_br_gain_bb=float(p['gains'][0,k]),raise_br_gain_bb=float(p['gains'][1,k])) for k,h in enumerate(study.pilot.LABELS)]
        # Independent backup of the changed leaf values validates the coefficient route.
        substitute=p['values'].copy()
        replacements={c['case']['node']:c['case']['pot']*study.model.predict(c,candidate)[0] for c in p['contexts']}
        for node in p['tree']['nodes'][::-1]:
            i=node['id']
            if i in replacements:substitute[i]=p['info'][i]['factor']*(replacements[i]-node['invested'][1])
            elif node['kind']==0:
                child=substitute[node['children']]
                substitute[i]=(child*np.array(node['sigma']).reshape(-1,169)).sum(axis=0) if node['actor']==1 else child.sum(axis=0)
        av=substitute[p['parent']['children']]/p['denominator']
        # The exported reference ranges have finite precision; allow the existing 2e-5bb tolerance.
        result['independent_backup_error_bb']=float(abs(pred-(av[2]-av[1])).max())
        assert result['independent_backup_error_bb']<2e-5
        gates[family+'_adjusted_action_improvement']=result['action_mae_bb']['corrected']<=.9*result['baseline_action_mae_bb']['corrected']
        gates[family+'_direct_action_nonregression']=result['action_mae_bb']['direct']<=result['baseline_action_mae_bb']['direct']+1e-9
        gates[family+'_qualified_mass']=result['qualified_mass']>=.2
        for key in ['direct','corrected']:
            gates[family+'_'+key+'_leaf_nonregression']=np.mean([c['candidate'][key] for c in result['leaves']])<=1.05*np.mean([c['baseline'][key] for c in result['leaves']])
        results[family]=result
    ci=np.quantile(np.mean(boot_reductions,axis=0),[.025,.975]).tolist()
    gates['pooled_adjusted_reduction_positive_95_interval']=ci[0]>0
    result=dict(evaluated_at=study.now(),manifest_id=m['id'],families=results,
        pooled_adjusted_mae_reduction_95_interval_bb=ci,gates={k:bool(v) for k,v in gates.items()},
        passed=bool(all(gates.values())),reference_jobs=len(m['jobs']),job_sha256=hashes,production_enabled=False)
    study.write(study.OUT/'evaluation.json',result)
    print({k:v for k,v in result.items() if k not in ['families','job_sha256']},flush=True)


if __name__=='__main__':evaluate()
