"""Exact set opportunities in the announced flop panels; no strategy fitting."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import math
import json
import numpy as np
import integrated_coverage as c

def run():
    out=c.OUT;d=c.s.read(c.s.OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(d['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES];w/=w.max(1)[:,None];w[w<1e-5]=0
    ix=[np.flatnonzero(x) for x in w];masks=[c.MASKS[x] for x in ix];classes=[c.CLASSES[x] for x in ix]
    mass=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    full=[]
    opp_cards=np.array(c.PAIRS)[ix[1]]
    for rank in range(13):
        pp=classes[0]==rank*14;remaining=2-(opp_cards//4==rank).sum(1)
        probability=np.array([1-math.comb(48-int(n),3)/math.comb(48,3) for n in remaining])
        den=mass[pp].sum();full.append(float((mass[pp]*probability).sum()/den) if den else None)
    boards=c.s.read(c.s.OUT/'fixtures.json')['canonical_flops'];cache={}
    additional=[(b['board'],1) for b in c.s.read(out/'old-two-orbits.json')['boards']]
    for board,iso in boards+additional:
        cards=c.cards(board);mask=np.uint64(sum(1<<x for x in cards));legal=[(m&mask)==0 for m in masks]
        per_hand=(mass*legal[0][:,None]*legal[1][None,:]).sum(1)
        den=np.array([per_hand[classes[0]==r*14].sum() for r in range(13)])
        cache[board]=(den,den*np.array([any(v//4==r for v in cards) for r in range(13)]))
    panels={'full_deck':[dict(board=b,weight=iso) for b,iso in boards]}
    for name in ['old-two-orbits','panel-a','panel-b','panel-ab']:panels[name]=c.s.read(out/(name+'.json'))['boards']
    cli=[line.split() for line in (out/'canonical-flops-cli.txt').read_text().splitlines() if line.strip()]
    assert [(b,int(w)) for b,w in cli]==[tuple(x) for x in boards]
    cumulative=np.cumsum([w for _,w in boards])
    for n in [47,95,184]:
        chosen=(out/f'report-subset-{n}.txt').read_text().splitlines()
        expected=[boards[i][0] for i in np.searchsorted(cumulative,(np.arange(n)+.5)*cumulative[-1]/n)]
        assert chosen==expected and len(set(chosen))==n
        panels[f'report-{n}']=[dict(board=b,weight=1) for b in chosen]
    result={}
    for name,items in panels.items():
        den=sum(cache[b['board']][0]*b['weight'] for b in items);num=sum(cache[b['board']][1]*b['weight'] for b in items)
        result[name]=[float(n/d) if d else None for n,d in zip(num,den)]
    error=max(abs(x-y) for x,y in zip(full,result['full_deck']) if x is not None)
    assert error<1e-12,error
    data=dict(ranks=list('23456789TJQKA'),flop_set_or_quads_probability=result,closed_form_max_error=error,
        note='Conditional on each UTG pocket pair and the fixed entering LJ range, before the next preflop action. All suits covered, earlier folded cards omitted. Full-deck enumeration checked against physical remaining-rank combinatorics.')
    c.s.write(out/'flop-structure.json',data)
    print(json.dumps(data,indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,ax=plt.subplots(figsize=(9,4.5));x=np.arange(13)
    for name,color in [('full_deck','#333333'),('panel-a','#a366a9'),('panel-b','#cd9342'),('panel-ab','#386b58')]:
        ax.plot(x,np.array(result[name])*100,marker='o',color=color,label=name)
    ax.set(xticks=x,xticklabels=[r+r for r in data['ranks']],ylabel='Flop contains a remaining card of your pair rank (%)',title='Small board panels distort pocket-pair opportunities')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'flop-structure.png',dpi=160);plt.close(fig)
    fig,ax=plt.subplots(figsize=(9,4.5))
    for name,color in [('full_deck','#333333'),('report-47','#a366a9'),('report-95','#cd9342'),('report-184','#386b58')]:
        ax.plot(x,np.array(result[name])*100,marker='o',color=color,label=name)
    ax.set(xticks=x,xticklabels=[r+r for r in data['ranks']],ylabel='Flop contains a remaining card of your pair rank (%)',title='Existing report subsets: card-structure check only')
    ax.legend();ax.grid(alpha=.2);fig.tight_layout();fig.savefig(out/'report-subset-structure.png',dpi=160);plt.close(fig)

if __name__=='__main__':run()
