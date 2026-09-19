"""Independent conditional-game CFR reference; never connects to production."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import sys
import time
import numpy as np
import card_compatible_hu as ref
import wizard_continuation_study as s

OUT=s.OUT.parent/'conditional-hu-20260919'
SAVE=s.ROOT/'saves/preflop/wizard-nl25-baseline-20260919-refined.gtop'
EXPECTED='5d3357ad4379871527af9916dd1313f585f709359331985c2ac23a24606fc190'


def register():
    assert not (OUT/'freeze.json').exists()
    assert s.sha(SAVE)==EXPECTED
    files=[OUT/'PROTOCOL.md',OUT/'subtree.json',SAVE,
        s.ROOT/'cache/preflop_eq169.bin',s.ROOT/'tools/research/conditional_hu_audit.py',
        s.ROOT/'tools/research/card_compatible_hu.py',
        s.ROOT/'crates/solver/examples/conditional_hu_export.rs',
        s.ROOT/'target/release/examples/conditional_hu_export.exe']
    s.write(OUT/'freeze.json',dict(inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in files},
        jobs=['independent_fresh','compatible_fresh','compatible_saved_seed'],checkpoints=[1000,10000,50000]))


def frozen():
    data=s.read(OUT/'freeze.json')
    for path,digest in data['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    return data


class Game:
    def __init__(self,data,compatible):
        self.nodes=data['nodes'];self.cfg=data['config'];self.compatible=compatible
        counts,combos,_,_=ref.card_pairs()
        incoming=np.array(data['incoming_class_mass']);incoming/=incoming.sum(1)[:,None]
        joint=incoming[0,:,None]*incoming[1,None,:]
        if compatible:joint*=counts/(combos[:,None]*combos[None,:])
        self.joint=joint/joint.sum();self.prior=np.array([self.joint.sum(1),self.joint.sum(0)])
        assert (self.prior>0).all(),'Unsupported private classes need explicit handling'
        self.conditional=[self.joint/self.prior[0,:,None],self.joint.T/self.prior[1,:,None]]
        eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
        eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
        base=np.array(data['class_base'])
        num=eq*base[:,None]*.92;oop=num/(num+(1-eq)*base[None,:]*1.08)
        self.payoffs={};self.rakes={};self.saved={};self.utilities={}
        self.dead=self.nodes[0]['pot']-sum(self.nodes[0]['invested'])
        for i,n in enumerate(self.nodes):
            if n['kind']==0:
                self.saved[i]=np.array(n['strategy']).reshape(-1,169)
                # Saved float32 averages can miss unit mass by tiny roundoff.
                assert abs(self.saved[i].sum(0)-1).max()<2e-6
                self.saved[i]/=self.saved[i].sum(0)
                continue
            rakepot=n['pot']
            if n['kind']==1:
                w=n['winner'];rakepot-=max(n['invested'][w]-n['invested'][1-w],0)
            rake=rakepot*self.cfg['rake_pct']/100
            if self.cfg['rake_cap']>0:rake=min(rake,self.cfg['rake_cap'])
            if n['kind']==1 and self.cfg['no_flop_no_drop']:rake=0.
            self.rakes[i]=rake
            for p in [0,1]:
                if n['kind']==1:
                    value=(n['pot']-rake if n['winner']==p else 0)-n['invested'][p]
                    utility=np.full((169,169),value)
                else:
                    blend=min(abs(n['r'][p]-1)/.08,1.)
                    relative=oop if p==0 else 1-oop.T
                    share=eq+blend*(relative-eq)
                    utility=(n['pot']-rake)*share-n['invested'][p]
                self.utilities[p,i]=utility
                self.payoffs[p,i]=np.ascontiguousarray(utility*self.conditional[p])

    def values(self,policy,p,i=0,opp=None,best=False,actions=None):
        if opp is None:opp=np.ones(169)
        n=self.nodes[i]
        if n['kind']!=0:return self.payoffs[p,i]@opp
        if n['actor']==p:
            val=np.array([self.values(policy,p,c,opp,best,actions) for c in n['children']])
            if best:return val.max(0)
            if actions is not None:
                mass=self.conditional[p]@opp
                actions[i]=np.divide(val,mass,out=np.zeros_like(val),where=mass>0)
            return (policy[i]*val).sum(0)
        return sum(self.values(policy,p,c,opp*policy[i][a],best,actions) for a,c in enumerate(n['children']))

    def flow(self,policy,i=0,reaches=None,rows=None):
        if reaches is None:reaches=np.ones((2,169))
        n=self.nodes[i];mass=self.joint*reaches[0,:,None]*reaches[1,None,:]
        if n['kind']!=0:return mass.sum()*self.rakes[i],mass.sum()
        prior=mass.sum(axis=1-n['actor']);den=prior.sum()
        if rows is not None:rows[i]=dict(reach_probability=float(den),action_frequencies=(policy[i]@prior/den).tolist())
        rake=prob=0.
        for a,c in enumerate(n['children']):
            nxt=reaches.copy();nxt[n['actor']]*=policy[i][a]
            r,m=self.flow(policy,c,nxt,rows);rake+=r;prob+=m
        return float(rake),float(prob)

    def evaluate(self,policy,detail=False):
        for sigma in policy.values():
            assert np.isfinite(sigma).all() and (sigma>=0).all() and (sigma<=1).all()
            assert abs(sigma.sum(0)-1).max()<1e-10
        actions={};rows={}
        ev=[float(self.prior[p]@self.values(policy,p,actions=actions)) for p in [0,1]]
        br=[float(self.prior[p]@self.values(policy,p,best=True)) for p in [0,1]]
        rake,mass=self.flow(policy,rows=rows)
        conservation=abs(sum(ev)+rake-self.dead)
        assert conservation<1e-5 and abs(mass-1)<1e-8,(conservation,mass)
        gaps=np.array(br)-ev;assert gaps.min()>-1e-9
        out=dict(evs=ev,gaps=gaps.tolist(),gap_total=float(gaps.sum()),expected_rake=rake,
            terminal_probability=mass,conservation_error=conservation,nodes=rows)
        if detail:out['action_values']={i:v.tolist() for i,v in actions.items()}
        return out

    def train(self,seed,targets):
        regrets={i:(v.copy() if seed else np.zeros_like(v)) for i,v in self.saved.items()}
        sigma={i:(v.copy() if seed else np.full_like(v,1/v.shape[0])) for i,v in self.saved.items()}
        sums={i:np.zeros_like(v) for i,v in sigma.items()}
        start=time.monotonic();records=[]
        def traverse(p,i,opp,own,t):
            n=self.nodes[i]
            if n['kind']!=0:return self.payoffs[p,i]@opp
            if n['actor']==p:
                old=sigma[i].copy();sums[i][:]+=t*old*own
                val=np.array([traverse(p,c,opp,own*old[a],t) for a,c in enumerate(n['children'])])
                value=(old*val).sum(0);regrets[i][:]=np.maximum(regrets[i]+val-value,0)
                den=regrets[i].sum(0)
                sigma[i]=np.divide(regrets[i],den,out=np.full_like(old,1/len(old)),where=den>0)
                return value
            return sum(traverse(p,c,opp*sigma[i][a],own,t) for a,c in enumerate(n['children']))
        for t in range(1,max(targets)+1):
            for p in [0,1]:traverse(p,0,np.ones(169),np.ones(169),t)
            if t in targets:
                avg={i:np.divide(v,v.sum(0),out=np.full_like(v,1/len(v)),where=v.sum(0)>0) for i,v in sums.items()}
                stats=self.evaluate(avg,True)
                row=dict(iteration=t,elapsed_seconds=time.monotonic()-start,evaluation=stats,
                    policy={i:v.tolist() for i,v in avg.items()})
                records.append(row);print(t,stats['gap_total'],row['elapsed_seconds'],flush=True)
        return records


def run():
    manifest=frozen();data=s.read(OUT/'subtree.json')
    for name in manifest['jobs']:
        dest=OUT/(name+'.json')
        if dest.exists():continue
        game=Game(data,name.startswith('compatible'))
        print(name,flush=True)
        result=dict(name=name,saved_evaluation=game.evaluate(game.saved,True),
            records=game.train(name.endswith('saved_seed'),manifest['checkpoints']))
        s.write(dest,result)
    review()


def review():
    manifest=frozen();data=s.read(OUT/'subtree.json');rows=[]
    games={name:Game(data,name=='compatible') for name in ['independent','compatible']}
    for job in manifest['jobs']:
        result=s.read(OUT/(job+'.json'))
        for record in result['records']:
            policy={int(i):np.array(v) for i,v in record['policy'].items()}
            row=dict(job=job,iteration=record['iteration'],evaluations={
                name:g.evaluate(policy,True) for name,g in games.items()})
            rows.append(row)
    s.write(OUT/'review.json',dict(results=rows,saved={name:g.evaluate(g.saved,True) for name,g in games.items()},
        note='Conditional branch only; earlier ranges and Balanced postflop values fixed. No folded-card bunching.'))


if __name__=='__main__':{'register':register,'run':run,'review':review}[sys.argv[1]]()
