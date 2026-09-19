"""Independent complete-tree accounting for the configured-rake HU experiment."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
os.environ['OMP_NUM_THREADS']='1'
import subprocess
import sys
import numpy as np
import card_compatible_hu as ref
import wizard_continuation_study as s

OUT=s.OUT.parent/'card-compatible-rake-20260919'
BINARY=s.ROOT/'target/release/examples/card_compatible_rake_audit.exe'
KERNEL=s.ROOT/'research/preflop-evolution/continuation/learned-interface-20260916/interface.cu'


def register():
    assert not (OUT/'freeze.json').exists(),'Preserve registration'
    common=dict(positions=['SB','BB'],posts=[1.,2.],ante=0.,limp=False,open_raises=[],raise_mults=[],
        max_raises=1,add_allin=True,rake_pct=4.,rake_cap=6.,no_flop_no_drop=True,realization='balanced')
    jobs=[]
    for name,overrides in [
        ('zero10',dict(stack=10.,rake_pct=0.,rake_cap=0.)),
        ('four10',dict(stack=10.)),('four200',dict(stack=200.)),
        ('uncapped50',dict(stack=50.,rake_pct=5.,rake_cap=0.,no_flop_no_drop=False)),
        ('full40',dict(stack=40.,posts=[.5,1.],limp=True,open_raises=[2.5],raise_mults=[3.],max_raises=3)),
        ('full40_drop',dict(stack=40.,posts=[.5,1.],limp=True,open_raises=[2.5],raise_mults=[3.],max_raises=3,no_flop_no_drop=False))]:
        cfg=dict(common,**overrides);folder=OUT/name;folder.mkdir(exist_ok=True)
        s.write(folder/'config.json',cfg);jobs.append(dict(name=name,config_hash=s.sha(folder/'config.json')))
    paths=[BINARY,KERNEL,OUT/'PROTOCOL.md',s.ROOT/'tools/research/card_compatible_rake_audit.py',
        s.ROOT/'tools/research/card_compatible_hu.py',s.ROOT/'crates/solver/examples/card_compatible_rake_audit.rs',
        s.ROOT/'crates/solver/src/preflop/gpu/learned_interface.rs',s.ROOT/'crates/solver/src/preflop/gpu.rs',
        s.ROOT/'crates/solver/src/preflop/mod.rs',s.ROOT/'cache/preflop_eq169.bin']
    s.write(OUT/'freeze.json',dict(jobs=jobs,inputs={p.relative_to(s.ROOT).as_posix():s.sha(p) for p in paths}))


def frozen():
    data=s.read(OUT/'freeze.json')
    for path,digest in data['inputs'].items():assert s.sha(s.ROOT/path)==digest,path
    for job in data['jobs']:assert s.sha(OUT/job['name']/'config.json')==job['config_hash']
    return data


def run():
    data=frozen();env=dict(os.environ)
    env['PATH']=str(s.ROOT/'.cuda-nvrtc/nvidia/cuda_nvrtc/bin')+os.pathsep+env.get('PATH','')
    for job in data['jobs']:
        folder=OUT/job['name']
        if (folder/'output.json').exists():continue
        assert s.idle()[0],'Production is busy; preserve remaining registered jobs'
        print('Starting',job['name'],flush=True)
        subprocess.run([str(BINARY),str(folder/'config.json'),str(KERNEL),str(folder/'output.json')],env=env,cwd=s.ROOT,check=True)
    review()


class Oracle:
    def __init__(self,data,record,counts,combos,eq):
        self.data=data;self.nodes=record['nodes'];self.cfg=data['config'];self.actions={}
        self.prior=combos/1326.;self.joint=counts/(1326.*1225.)
        self.conditional=counts/(combos[:,None]*1225.)
        self.payoffs={};self.rakes={}
        base=np.ones(169) if data['class_base'] is None else np.array(data['class_base'])
        # Independent translation of Balanced's relative class scores. Keep
        # mathematical complements in double precision for conservation checks.
        numer=eq*base[:,None]*.92;denom=numer+(1-eq)*base[None,:]*1.08
        oop=numer/np.maximum(denom,1e-12);ip=1-oop.T
        for i,n in enumerate(self.nodes):
            if n['kind']==0:
                sigma=np.array(n['strategy']).reshape(len(n['children']),169)
                assert np.isfinite(sigma).all() and (sigma>=0).all() and (sigma<=1).all()
                assert np.max(abs(sigma.sum(0)-1))<2e-6
                n['sigma']=sigma;continue
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
                    relative=oop if p==data['postflop_order'][0] else ip
                    share=eq+blend*(relative-eq)
                    utility=(n['pot']-rake)*share-n['invested'][p]
                self.payoffs[p,i]=utility*self.conditional

    def traverse(self,p,i,opponent_reach,best=False):
        n=self.nodes[i]
        if n['kind']!=0:return self.payoffs[p,i]@opponent_reach
        if n['actor']==p:
            values=np.array([self.traverse(p,c,opponent_reach,best) for c in n['children']])
            if best:return values.max(0)
            self.actions[p,i]=values
            return (values*n['sigma']).sum(0)
        return sum(self.traverse(p,c,opponent_reach*n['sigma'][a],best) for a,c in enumerate(n['children']))

    def expected_rake(self,i=0,reaches=None):
        if reaches is None:reaches=np.ones((2,169))
        n=self.nodes[i]
        if n['kind']!=0:
            probability=float((self.joint*reaches[0,:,None]*reaches[1,None,:]).sum())
            return probability*self.rakes[i],probability
        rake=mass=0.
        for a,c in enumerate(n['children']):
            nxt=reaches.copy();nxt[n['actor']]*=n['sigma'][a]
            r,m=self.expected_rake(c,nxt);rake+=r;mass+=m
        return rake,mass

    def evaluate(self):
        evs=[float(self.prior@self.traverse(p,0,np.ones(169))) for p in [0,1]]
        br=[float(self.prior@self.traverse(p,0,np.ones(169),True)) for p in [0,1]]
        rake,probability=self.expected_rake()
        return dict(evs=evs,gaps=[b-e for b,e in zip(br,evs)],expected_rake=rake,terminal_probability=probability)


def review():
    data=frozen();counts,combos,_,_=ref.card_pairs()
    eq=np.frombuffer((s.ROOT/'cache/preflop_eq169.bin').read_bytes()[4:],dtype='<f4').reshape(169,169).astype(float)
    eq=(eq+1-eq.T)/2;np.fill_diagonal(eq,.5)
    rows=[]
    for job in data['jobs']:
        output=s.read(OUT/job['name']/'output.json');assert output['guards_passed']
        for record in output['records']:
            oracle=Oracle(output,record,counts,combos,eq);row=oracle.evaluate()
            row.update(name=job['name'],iteration=record['iteration'],nodes=len(record['nodes']))
            row['ev_error']=float(max(abs(np.array(row['evs'])-record['evs'])))
            row['gap_error']=abs(sum(row['gaps'])-sum(record['gaps']))
            row['conservation_error']=abs(sum(row['evs'])+row['expected_rake'])
            error=0.;count=0
            for node in record['frontier']['rows']:
                expected=oracle.actions[node['actor'],node['node']].T
                actual=np.array([h['action_values_counterfactual_bb'] for h in node['hands']])
                assert expected.shape==actual.shape
                error=max(error,float(abs(expected-actual).max()));count+=expected.size
            row['all_action_error']=error;row['action_values_checked']=count
            assert row['ev_error']<=.0001 and row['gap_error']<=.0001 and error<=.0001,row
            assert row['conservation_error']<=.00001 and abs(row['terminal_probability']-1)<2e-6,row
            if job['name']=='zero10':
                old=next(r for r in s.read(ref.OUT/'interface-policies.json')['results'] if r['stack']==10 and r['iteration']==record['iteration'])
                root=record['nodes'][0];jam=next(a for a,v in enumerate(root['actions']) if v['kind']=='jam')
                reply=record['nodes'][root['children'][jam]];call=next(a for a,v in enumerate(reply['actions']) if v['kind']=='call')
                x=np.array(root['strategy']).reshape(-1,169)[jam];y=np.array(reply['strategy']).reshape(-1,169)[call]
                row['old_zero_rake_policy_difference']=float(max(abs(x-old['hero_jam']).max(),abs(y-old['opponent_call']).max()))
                assert row['old_zero_rake_policy_difference']==0,row
            rows.append(row);print(row,flush=True)
    s.write(OUT/'review.json',dict(results=rows,accounting_passed=True,
        note='Exact class-compatible chance, sampled showdown equities, fixed Balanced non-all-in values. Not postflop accuracy or multiway validation.'))


if __name__=='__main__':{'register':register,'run':run,'review':review}[sys.argv[1]]()
