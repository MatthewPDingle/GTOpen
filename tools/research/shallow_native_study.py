"""Opt-in native shallow correction; no server calls except read-only idle checks."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from functools import lru_cache
import numpy as np
import shallow_continuation_audit as previous
import shallow_continuation_fit as fit

ROOT=previous.ROOT
OUT=previous.prior.BASE/'shallow-native-20260917'
BASE_KERNEL=previous.prior.BASE/'full-precision-20260916/double/interface.cu'
BIN=ROOT/'target/learned-interface-filtered/release/examples/learned_interface.exe'
EXPORT=BIN.with_name('holdem_action_export.exe')
PROBE=ROOT/'target/shallow-research/release/examples/shallow_probe.exe'
read,write,now=previous.read,previous.write,previous.now
MODEL=previous.OUT/'candidate.json'
# Immutable equity inputs: avoid rebuilding the exact compatibility matrix for
# every stack-depth probe. The underlying calculation is unchanged.
previous.pilot.matrices=lru_cache(maxsize=1)(previous.pilot.matrices)


def hybrid(c):
    spr=c['case']['stack']/c['case']['pot']
    low=copy.deepcopy(c); low['case']['stack']=np.clip(spr,.2,.75)*c['case']['pot']
    residual=fit.predict(low,read(MODEL))-c['raw']
    # Below the training band, scale the residual to zero at zero stack.
    if spr<.2: residual*=spr/.2
    value=c['raw']+residual
    if spr>.75:
        high=copy.deepcopy(c['case']); high['stack']=high['pot']*max(1.,spr)
        counts,eq=previous.pilot.matrices(); context=previous.pilot.context(high,counts,eq)
        context.update(case=high,base_x=context['x'].copy(),base_names=list(context['names']))
        endpoint=previous.prior.network.predict(context,read(previous.prior.MODEL))
        t=np.clip((spr-.75)/.25,0,1); t=t*t*(3-2*t)
        value=(1-t)*value+t*endpoint
    return value


def export():
    OUT.mkdir(parents=True,exist_ok=True)
    assert previous.pilot.sha(MODEL)==read(previous.OUT/'candidate-freeze.json')['sha256']
    coeff=','.join(format(v,'.17g') for v in read(MODEL)['coefficients'])
    helper=r'''
// Frozen shallow model; enabled only by the standalone research source switch.
__device__ void shallow_values(double spr,const double* raw,const double* mass,double z,double* out){
 __shared__ double residual[338],mean,scale;
 const double coeff[18]={COEFFICIENTS};
 double at=fmin(.75,fmax(.2,spr)),factor=at/(1.+at),logspr=log1p(at);
 for(int x=threadIdx.x;x<338;x+=blockDim.x){int h=x%169;double q=raw[x]-.5,pos=x/169?1.:-1.;
  double pair=h/13==h%13,suit=h/13>h%13;
  double f[9]={q,q*q,q*q*q,pos,pos*q,pair,suit,pair*q,suit*q};
  double value=0.;for(int k=0;k<9;k++)value+=f[k]*(coeff[k]+logspr*coeff[k+9]);
  residual[x]=factor*value;
 }__syncthreads();
 if(threadIdx.x==0){mean=0.;for(int x=0;x<338;x++)mean+=mass[x]*residual[x]/(2*z);
  scale=1.;for(int x=0;x<338;x++){double r=residual[x]-mean;
   if(r>0.)scale=fmin(scale,(1.+at-raw[x])/r);
   if(r<0.)scale=fmin(scale,(raw[x]+at)/(-r));
  }
 }__syncthreads();
 for(int x=threadIdx.x;x<338;x+=blockDim.x)out[x]=raw[x]+scale*(residual[x]-mean)*fmin(1.,spr/.2);
 __syncthreads();
}
extern "C" __global__ void shallow_probe(const double* spr,const double* raw,const double* mass,const double* endpoint,double* result){
 int i=blockIdx.x;__shared__ double low[338];
 shallow_values(spr[i],raw+i*338,mass+i*338,1.,low);
 double t=fmin(1.,fmax(0.,(spr[i]-.75)/.25));t=t*t*(3.-2.*t);
 for(int x=threadIdx.x;x<338;x+=blockDim.x)result[i*338+x]=(1.-t)*low[x]+t*endpoint[i*338+x];
}
'''.replace('COEFFICIENTS',coeff)
    source=BASE_KERNEL.read_text(encoding='utf-8')
    source=source.replace('extern "C" __global__ void interface_prepare',helper+'\nextern "C" __global__ void interface_prepare',1)
    marker=' bool learned=use_learned && sprs[nd]>=1. && sprs[nd]<=20. && totals[0]>0. && totals[1]>0.;'
    assert source.count(marker)==1
    branch=r'''
 __shared__ double shallow[338];
 bool use_shallow=use_learned && np==2 && sprs[nd]>0. && sprs[nd]<1. && totals[0]>0. && totals[1]>0.;
 if(use_shallow){
  for(int x=threadIdx.x;x<338;x+=blockDim.x){int s=x/169,h=x%169;double den=0.,num=0.;
   for(int j=0;j<169;j++){double w=compatible(h,j)*d[(1-s)*169+j]/combos(j);den+=w;num+=w*eq[j*169+h];}
   qraw[x]=num/den;mass[x]=d[x]/combos(h)*den;
  }__syncthreads();shallow_values(sprs[nd],qraw,mass,z,shallow);
  if(sprs[nd]<=.75){
   for(int h=threadIdx.x;h<169;h+=blockDim.x){double weight=legal(h,d+(1-side)*169,rankmass+(1-side)*13)/ez;
    val[(size_t)slots[nd]*169+h]=(float)(prob*weight*(pots[nd]*shallow[side*169+h]-inv[(size_t)nd*np+p]));}
   return;
  }
 }
 bool learned=use_learned && (sprs[nd]>=1. || use_shallow) && sprs[nd]<=20. && totals[0]>0. && totals[1]>0.;
'''
    source=source.replace(marker,branch)
    assert source.count('log_spr=log1p(sprs[nd])')==1
    source=source.replace('log_spr=log1p(sprs[nd])','log_spr=log1p(fmax(1.,sprs[nd]))')
    marker='double pred=qraw[side*169+h]+correction[side*169+h]-center;'
    assert source.count(marker)==1
    source=source.replace(marker,marker+'\n  if(use_shallow){double t=(sprs[nd]-.75)/.25;t=t*t*(3.-2.*t);pred=(1.-t)*shallow[side*169+h]+t*pred;}')
    target=OUT/'interface.cu'
    if target.exists(): assert target.read_text(encoding='utf-8')==source
    else: target.write_text(source,encoding='utf-8',newline='\n')
    print('Exported opt-in kernel',previous.pilot.sha(target),flush=True)


def command(args,log,env_extra=None):
    previous.prior.idle()
    env=dict(os.environ);env['PATH']=str(ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    env['GTOPEN_INTERFACE_SKIP_REDUNDANT']='1';env['GTOPEN_INTERFACE_WARMUP']='0'
    env.update(env_extra or {})
    with Path(log).open('w',encoding='utf-8',newline='\n') as out:
        subprocess.run([str(a) for a in args],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT,check=True)


def probes():
    export(); cases=read(previous.OUT/'manifest.json')['cases']; fixtures=[]
    for case in cases:
        for spr in [0.,1e-8,.1,.2-1e-7,.2,.2+1e-7,17.5/45,.75-1e-7,.75,.75+1e-7,.85,1.-1e-7,1.,1.+1e-7]:
            c=fit.context(dict(case,stack=case['pot']*spr))
            high=fit.context(dict(case,stack=case['pot']*max(1.,spr)))
            high.update(base_x=high['x'].copy(),base_names=list(high['names']))
            endpoint=previous.prior.network.predict(high,read(previous.prior.MODEL))
            fixtures.append(dict(case=case['id'],spr=spr,raw=c['raw'].ravel().tolist(),mass=c['mass'].ravel().tolist(),
                                 endpoint=endpoint.ravel().tolist(),expected=hybrid(c).ravel().tolist()))
    write(OUT/'probes.json',dict(fixtures=fixtures,model=read(MODEL)))
    command([PROBE,OUT/'probes.json',OUT/'interface.cu',OUT/'probe-results.json'],OUT/'probe.log')
    result=read(OUT/'probe-results.json'); error=0.;accounting=0.;boundary=0.
    for f,r in zip(fixtures,result['results']):
        for key in ['cpu','gpu']:
            error=max(error,float(np.max(abs(np.array(f['expected'])-r[key]))))
            accounting=max(accounting,abs(np.dot(f['mass'],r[key])-1))
    for ident in {f['case'] for f in fixtures}:
        ff=[f for f in fixtures if f['case']==ident]
        for b in [.2,.75,1.]:
            around=[np.array(f['expected']) for f in ff if abs(f['spr']-b)<2e-7]
            boundary=max(boundary,float(np.max(np.ptp(around,axis=0))))
    assert error<1e-9 and accounting<1e-9 and boundary<1e-5,(error,accounting,boundary)
    write(OUT/'probe-check.json',dict(fixtures=len(fixtures),values=len(fixtures)*338,max_cpu_gpu_python_error=error,
          max_pot_error=accounting,max_boundary_change=boundary,passed=True,production_enabled=False))
    print('Boundary / native CPU / CUDA probes passed',error,flush=True)


def all_values(tree,shallow=True,balanced=False):
    counts,eq=previous.pilot.matrices(); combos=previous.pilot.COMBOS; prior=combos/1326
    kernel=counts/combos[:,None]/combos[None,:]; anchor=prior@kernel@prior
    nodes=tree['nodes']; reaches=np.broadcast_to(prior,(len(nodes),2,169)).copy()
    for nd in nodes:
        if nd['kind']!=0:continue
        for a,child in enumerate(nd['children']):
            reaches[child]=reaches[nd['id']]
            reaches[child,nd['actor']]*=np.array(nd['sigma']).reshape(-1,169)[a]
    values=np.zeros((2,len(nodes),169)); info={}
    for nd in nodes[::-1]:
        i=nd['id']
        if nd['kind']==0:
            for p in range(2):
                child=values[p,nd['children']]
                values[p,i]=(child*np.array(nd['sigma']).reshape(-1,169)).sum(axis=0) if nd['actor']==p else child.sum(axis=0)
            continue
        r=reaches[i,[1,0]];total=r.sum(axis=1)
        d=np.array([r[s]/total[s] if total[s]>0 else prior for s in range(2)])
        left=max(0.,min(tree['config']['stack']-v for v in nd['invested']));spr=left/nd['pot']
        case=dict(weights=(d/combos).tolist(),pot=nd['pot'],stack=left)
        c=fit.context(case);pred=c['balanced'];origin='balanced_fallback'
        if nd['kind']==1:
            pred=np.array([np.full(169,float(nd['winner']==p)) for p in [1,0]])
            origin='fold'
        elif left==0:pred=c['raw'];origin='cached_allin_equity'
        elif not balanced and (total>0).all():
            if shallow and 0<spr<1:pred=hybrid(c);origin='shallow'
            elif 1<=spr<=20:
                c.update(base_x=c['x'].copy(),base_names=list(c['names']))
                pred=previous.prior.network.predict(c,read(previous.prior.MODEL));origin='learned'
        for side,p in enumerate([1,0]):
            factor=total[1-side]*(kernel@d[1-side])/anchor
            gross=nd['pot']*pred[side]
            values[p,i]=factor*(gross-nd['invested'][p])
            if p==1:info[i]=dict(factor=factor,gross=gross,origin=origin,raw_equity=c['raw'][0])
    return values,info,reaches


def tree_values(tree,shallow=True,balanced=False):
    values,info,reaches=all_values(tree,shallow,balanced)
    return values[1],info,reaches


def parity(save,tree_path,folder):
    folder.mkdir(parents=True,exist_ok=True)
    if not tree_path.exists(): command([EXPORT,save,tree_path],folder/'export.log')
    tree=read(tree_path); checks=[]
    for arm,kernel,mode in [('baseline',BASE_KERNEL,'candidate'),('shallow',OUT/'interface.cu','candidate'),
                            ('disabled',OUT/'interface.cu','balanced')]:
        output=folder/(arm+'.json'); command([BIN,'evaluate',save,output,mode,kernel],folder/(arm+'.log'))
        v,info,_=all_values(tree,arm=='shallow',arm=='disabled');error=0.;nvalues=0
        for row in read(output)['rows']:
            parent=next(n for n in tree['nodes'] if n['path']==row['path'])
            native=np.array([h['action_values_counterfactual_bb'] for h in row['hands']])
            error=max(error,float(np.max(abs(v[row['actor'],parent['children']].T-native))))
            nvalues+=native.size
        assert error<2e-5,(arm,error)
        checks.append(dict(arm=arm,max_counterfactual_error_bb=error,values=nvalues))
    write(folder/'parity.json',dict(checks=checks,passed=True))
    print('Full-tree parity passed',checks,flush=True)


def solve():
    checked()
    assert read(OUT/'probe-check.json')['passed'] and read(OUT/'original-policy/parity.json')['passed']
    source=previous.prior.SAVE
    for arm,kernel in [('baseline',BASE_KERNEL),('shallow',OUT/'interface.cu')]:
        for end in [500,1500,3000]:
            folder=OUT/arm/str(end); folder.mkdir(parents=True,exist_ok=True)
            start=0 if end==500 else 500 if end==1500 else 1500
            src=source if start==0 else OUT/arm/str(start)/'policy.gtop'
            args=[BIN,'solve',src,folder,'candidate',end-start,kernel]+(['resume'] if start else [])
            command(args,folder/'solve.log')
        parity(OUT/arm/'3000/policy.gtop',OUT/arm/'tree.json',OUT/arm/'audit')
    checked()


def guards():
    folder=OUT/'guards';folder.mkdir(exist_ok=True)
    checks=[]
    for players,mode,zeros in [(2,'balanced',False),(2,'candidate',True),(3,'candidate',False),(8,'candidate',False)]:
        results=[]
        for arm,kernel in [('baseline',BASE_KERNEL),('shallow',OUT/'interface.cu')]:
            name=f'{players}-{mode}-{zeros}-{arm}'
            command([BIN,'oracle',folder/(name+'.json'),kernel,mode,players]+(['zeros'] if zeros else []),folder/(name+'.log'))
            results.append(read(folder/(name+'.json')))
        a,b=results
        # Sparse HU still contains supported shallow leaves. It must remain
        # finite and preserve accounting; disabled and multiway must be identical.
        errs=[]
        for ra,rb in zip(a['frontier']['rows'],b['frontier']['rows']):
            assert ra['path']==rb['path']
            av=np.array([h['action_values_counterfactual_bb'] for h in ra['hands']])
            bv=np.array([h['action_values_counterfactual_bb'] for h in rb['hands']])
            assert np.isfinite(bv).all()
            errs.append(float(abs(av-bv).max()))
        error=max(errs,default=0.)
        if players>2 or mode=='balanced': assert error<2e-5,error
        assert abs(sum(b['evs']))<2e-4,b['evs']
        checks.append(dict(players=players,mode=mode,sparse=zeros,max_change_bb=error,ev_sum=sum(b['evs'])))
    write(OUT/'guard-check.json',dict(checks=checks,passed=True))


def register():
    assert not (OUT/'implementation-freeze.json').exists()
    for p in [OUT/'probe-check.json',OUT/'original-policy/parity.json',OUT/'guard-check.json']:
        assert read(p)['passed']
    sources=[Path(__file__),ROOT/'crates/solver/examples/shallow_probe.rs',OUT/'PROTOCOL.md',
        OUT/'interface.cu',BASE_KERNEL,MODEL,previous.prior.MODEL,PROBE,BIN,EXPORT,previous.prior.SAVE,
        ROOT/'cache/preflop_eq169.bin',ROOT/'cache/realization_fit.json']
    # Imported analysis dependencies, including their frozen model inputs.
    sources += [Path(mod.__file__) for mod in list(sys.modules.values())
                if getattr(mod,'__file__',None) and Path(mod.__file__).parent==ROOT/'tools/research']
    payload=dict(registered_at=now(),inputs={p.relative_to(ROOT).as_posix():previous.pilot.sha(p) for p in sources},
        production_enabled=False,live=previous.prior.idle())
    payload['id']=hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()
    write(OUT/'implementation-freeze.json',payload)


def checked():
    m=read(OUT/'implementation-freeze.json')
    assert hashlib.sha256(json.dumps({k:v for k,v in m.items() if k!='id'},sort_keys=True).encode()).hexdigest()==m['id']
    for p,h in m['inputs'].items():assert previous.pilot.sha(ROOT/p)==h,p
    return m


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['export','probes','parity','guards','register','solve'])
    cmd=p.parse_args().command
    if cmd=='parity':parity(previous.prior.SAVE,OUT/'original-tree.json',OUT/'original-policy')
    else:globals()[cmd]()
