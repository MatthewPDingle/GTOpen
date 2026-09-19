"""Freeze a disjoint, outcome-blind systematic validation panel and audit chance."""
import hashlib
import json
from pathlib import Path
import numpy as np
import integrated_coverage as c

ROOT=Path(__file__).resolve().parents[2]
OUT=c.OUT.parent/'representative-coverage-20260919'
SEED='independent-systematic-95-20260919-v1'

def signature(board):
    return min(tuple(sorted(c.cards(c.relabel(board,p)))) for p in c.PERMS)

def run():
    assert not (OUT/'validation-95-freeze.json').exists()
    manifests=[OUT/'report-47.json']+[c.OUT/f'{name}.json' for name in ['old-two-orbits','panel-a','panel-b','reserved']]
    excluded={signature(b['board']) for path in manifests for b in json.loads(path.read_text())['boards']}
    boards=c.s.read(c.s.OUT/'fixtures.json')['canonical_flops']
    eligible=[(b,m) for b,m in boards if signature(b) not in excluded]
    mass=np.cumsum([m for _,m in eligible]);offset=int.from_bytes(hashlib.sha256(SEED.encode()).digest()[:8],'big')/2**64
    chosen=[eligible[i][0] for i in np.searchsorted(mass,(np.arange(95)+offset)*mass[-1]/95)]
    assert len(set(chosen))==95 and all(signature(b) not in excluded for b in chosen)
    manifest=dict(suit_orbits=True,bet_menu='50',reserved=True,seed=SEED,systematic_offset=offset,
                  boards=[dict(board=b,weight=1) for b in chosen],
                  population='Canonical full-deck flops excluding all previously declared development/training/reserved orbits.')
    (OUT/'validation-95.json').write_text(json.dumps(manifest,indent=2))
    data=c.s.read(c.s.OUT.parent/'conditional-hu-20260919/subtree.json')
    w=np.array(data['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES]
    w/=w.max(1)[:,None];w[w<1e-5]=0
    ix=[np.flatnonzero(x) for x in w];masks=[c.MASKS[x] for x in ix]
    joint=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    classes=c.CLASSES[ix[0]];cache={}
    for board,_ in boards:
        cards=c.cards(board);mask=np.uint64(sum(1<<x for x in cards));legal=[(x&mask)==0 for x in masks]
        private_mass=(joint*legal[0][:,None]*legal[1][None,:]).sum(1)
        den=np.array([private_mass[classes==r*14].sum() for r in range(13)])
        cache[board]=(den,den*np.array([any(x//4==r for x in cards) for r in range(13)]))
    def opportunities(items):
        den=sum(cache[b][0]*m for b,m in items);num=sum(cache[b][1]*m for b,m in items)
        return np.divide(num,den,out=np.zeros_like(num),where=den>0).tolist()
    full=opportunities(boards);population=opportunities(eligible);sample=opportunities([(b,1) for b in chosen])
    reserved=opportunities([(b['board'],b['weight']) for b in c.s.read(c.OUT/'reserved.json')['boards']])
    audit=dict(eligible_orbits=len(eligible),excluded_orbits=len(boards)-len(eligible),
        eligible_physical_mass=int(mass[-1]),full_physical_mass=sum(m for _,m in boards),
        excluded_physical_fraction=1-float(mass[-1])/sum(m for _,m in boards),
        ranks=list('23456789TJQKA'),pocket_pair_set_or_quads=dict(full=full,eligible=population,validation95=sample,original_reserved10=reserved),
        max_sample_error_vs_eligible_pp=float(max(abs(np.array(sample)-population))*100),
        max_sample_error_vs_full_pp=float(max(abs(np.array(sample)-full))*100),
        max_reserved10_error_vs_full_pp=float(max(abs(np.array(reserved)-full))*100),
        note='Exact board-structure calculation conditional on the frozen entering live ranges. No strategic outcomes were used.')
    (OUT/'validation-95-structure.json').write_text(json.dumps(audit,indent=2))
    files=[Path(__file__),OUT/'VALIDATION95-PROTOCOL.md',OUT/'validation-95.json',c.s.OUT/'fixtures.json',c.s.OUT.parent/'conditional-hu-20260919/subtree.json',*manifests]
    (OUT/'validation-95-freeze.json').write_text(json.dumps(dict(inputs={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}),indent=2))
    print(json.dumps({k:v for k,v in audit.items() if k not in ['ranks','pocket_pair_set_or_quads']},indent=2))

if __name__=='__main__':run()
