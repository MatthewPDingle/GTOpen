"""Frozen predictor, anchored legal-pair chance, independent enumeration oracle."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,pathlib,sys,subprocess,hashlib,time
import numpy as np
import range_value_pilot as pilot
import continuation_overnight as night
import continuation_overnight_fit as fit
import learned_decisions as old
ROOT=pilot.ROOT
OUT=ROOT/'research/preflop-evolution/continuation/learned-interface-20260916'
BIN=ROOT/'target/learned-interface/release/examples/learned_interface.exe'
def write(p,v):p.write_bytes((json.dumps(v,indent=2,allow_nan=False)+'\n').encode())
def command(args,log):
    old.idle()
    assert not night.live_busy(),'Live application is busy; research deferred'
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    with log.open('w') as f:subprocess.run([str(BIN),*map(str,args)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT,check=True)
def export():
    OUT.mkdir(exist_ok=True)
    frozen=old.OUT/'candidate.cu'
    expr=frozen.read_text().split('correction[x]=',1)[1].split(';\n }',1)[0].replace('dist[','d[')
    template=(ROOT/'tools/research/learned_interface_kernel.cu').read_text()
    assert '__FEATURE_EXPRESSION__' in template and 'log_spr' in expr
    (OUT/'interface.cu').write_bytes(('// Frozen model '+pilot.sha(night.OUT/'candidate.json')+'\n'+template.replace('__FEATURE_EXPRESSION__',expr)).encode())
    print('Exported unchanged predictor with anchored pair conversion.')

def oracle():
    counts,eq=pilot.matrices();K=counts/pilot.COMBOS[:,None]/pilot.COMBOS[None,:]
    prior=pilot.COMBOS/1326.;model=json.loads((night.OUT/'candidate.json').read_text())
    base=np.array(json.loads((ROOT/'cache/realization_fit.json').read_text())['class_base'])
    # Independently enumerate all physical two-card holdings (pilot.matrices),
    # rather than reuse the GPU's rank-incidence shortcut.
    assert abs(prior@K@prior-1225/1326)<1e-14
    relative=[]
    for side,pos in enumerate([.92,1.08]):
        a=eq*base[:,None]*pos;b=(1-eq)*base[None,:]*(2-pos);relative.append(a/(a+b))
    reports=[]
    for np_ in [2,3,8]:
      for arm,sparse in [(a,z) for z in [False,True] for a in ['balanced','candidate']]:
        name=f'oracle-{np_}-{arm}'+('-zeros' if sparse else '');path=OUT/f'{name}.json'
        args=['oracle',path,OUT/'interface.cu',arm,np_]
        if sparse:args.append('zeros')
        command(args,OUT/f'{name}.log')
        data=json.loads(path.read_text());nodes=data['nodes'];n=len(nodes);plan=data['plan']
        reaches=np.broadcast_to(prior,(n,np_,169)).copy()
        for i,node in enumerate(nodes):
            if node['kind']!=0:continue
            sigma=np.array(node['sigma']).reshape(-1,169)
            for a,c in enumerate(node['children']):reaches[c]=reaches[i];reaches[c,node['actor']]*=sigma[a]
        normalizers=[]
        for c,entry in enumerate(plan['entries']):
            seats=plan['seats'][c*2:c*2+2];r=reaches[entry,seats];d=np.array([v/v.sum() if v.sum()>0 else prior for v in r]);normalizers.append(d[0]@K@d[1])
        values=np.full((n,np_,169),np.nan);folds=allins=learned=0;terminal_error=0.
        for i in range(n-1,-1,-1):
            node=nodes[i];ctx=plan['node_context'][i]
            if ctx==2**32-1:continue
            if node['kind']==0:
                sigma=np.array(node['sigma']).reshape(-1,169)
                for p in range(np_):
                    children=values[node['children'],p]
                    values[i,p]=(children*sigma).sum(axis=0) if node['actor']==p else children.sum(axis=0)
                continue
            seats=plan['seats'][ctx*2:ctx*2+2];r=reaches[i,seats];tot=r.sum(axis=1);d=np.array([v/v.sum() if v.sum()>0 else prior for v in r])
            den=np.array([K@d[1],K@d[0]]);pair_mass=d*den;z=pair_mass[0].sum();ez=normalizers[ctx]
            pot=node['pot'];invested=np.array(node['invested']);spr=max(0,min(data['config']['stack']-invested[p] for p in seats)/pot)
            if node['kind']==1:folds+=1;pred=np.array([np.full(169,float(node['winner']==p)) for p in seats])
            else:
                allins+=int(spr==0)
                raw=np.array([(K*eq)@d[1]/den[0],(K*eq)@d[0]/den[1]])
                pred=np.empty_like(raw)
                for side,p in enumerate(seats):
                    blend=min(1,abs(node['r'][p]-1)/.08)
                    pred[side]=raw[side]+blend*((K*relative[side])@d[1-side]/den[side]-raw[side])
                if arm=='candidate' and 1<=spr<=20 and (tot>0).all():
                    case=dict(weights=(d/pilot.COMBOS).tolist(),pot=pot,stack=pot*spr)
                    context=pilot.context(case,counts,eq);context.update(base_x=context['x'].copy(),base_names=context['names'],case=case)
                    pred=fit.predict(context,model);learned+=1
            for p in range(np_):
                prob=np.prod(np.delete(reaches[i].sum(axis=1),p))
                if p in seats:
                    side=seats.index(p);values[i,p]=prob*den[side]/ez*(pot*pred[side]-invested[p])
                else:values[i,p]=-prob*invested[p]*z/ez
            # Conservation under the SAME terminal chance measure, including
            # folded seats. This is checked before any upward aggregation.
            error=float((reaches[i]*values[i]).sum())
            terminal_error=max(terminal_error,abs(error))
            # Existing Balanced positional weights are stored as f32; opposite
            # blends can differ at float roundoff even in the double oracle.
            assert abs(error)<2e-6,(name,i,error)
        maximum=0.;checked=0
        for row in data['frontier']['rows']:
            i=row['node'];p=row['actor'];expected=values[nodes[i]['children'],p].T
            observed=np.array([h['action_values_counterfactual_bb'] for h in row['hands']])
            maximum=max(maximum,float(abs(expected-observed).max()));checked+=expected.size
        assert maximum<2e-4,(name,maximum)
        evsum=sum(data['evs']);assert abs(evsum)<2e-4,(name,'root accounting',evsum)
        root_error=None
        if np_==2:
            root_error=float(abs(values[0]@prior-np.array(data['evs'])).max());assert root_error<2e-4
        reports.append(dict(case=name,nodes=n,action_values_checked=checked,max_action_error_bb=maximum,root_error_bb=root_error,
                            root_ev_sum_bb=evsum,max_terminal_accounting_error_bb=terminal_error,fold_terminals=folds,allin_terminals=allins,learned_terminals=learned))
        print(name,'passed;',checked,'values; max error',maximum,flush=True)
    write(OUT/'oracle-check.json',dict(passed=True,tests=reports,exact_pair_combinations=int(counts.sum()),
          caveat='Exact two-player class chance using cached approximate equity. Larger-game tests validate the explicitly approximated pair reset, not full multiplayer physical dealing.'))

def freeze():
    paths=[night.OUT/'candidate.json',OUT/'interface.cu',BIN,ROOT/'cache/preflop_eq169.bin',ROOT/'cache/realization_fit.json',ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop']
    manifest=dict(files={str(p.relative_to(ROOT)).replace('\\','/'):pilot.sha(p) for p in paths},
                  scope='Paired-branch chance reset, frozen conditional predictor; no live deployment or full-game convergence guarantee')
    path=OUT/'manifest.json'
    if path.exists():assert json.loads(path.read_text())==manifest,'Frozen input changed'
    else:write(path,manifest)
    return manifest

def run():
    assert json.loads((OUT/'oracle-check.json').read_text())['passed'];freeze()
    target=int(sys.argv[2]);assert target in [50,250,500,1000]
    for arm in ['original','balanced','candidate']:
        folder=OUT/arm;folder.mkdir(exist_ok=True)
        done=[int(f.stem.split('-')[1]) for f in folder.glob('iteration-*.json')];current=max(done,default=0)
        if current>=target:continue
        source=folder/'policy.gtop' if current else ROOT/'saves/preflop/balanced-sb05-continuation-20260915.gtop'
        args=['solve',source,folder,arm,target-current,OUT/'interface.cu']
        if current:args.append('resume')
        print('Starting',arm,current,'to',target,flush=True);command(args,folder/f'run-{target}.log')
        print('Completed',arm,target,flush=True)

if __name__=='__main__':{'export':export,'oracle':oracle,'run':run,'freeze':freeze}[sys.argv[1]]()
