"""Chance-only audit; no strategy results or outcome-based board selection."""
import hashlib
import json
import os
from pathlib import Path
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np
import integrated_coverage as c
from storage_expansion_register_20260920 import signature

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
def main():
    dest=OUT/'expansion-geometry-audit.json';assert not dest.exists()
    freeze=json.loads((OUT/'expansion-registration-freeze.json').read_text())
    for p,h in freeze['inputs_sha256'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==h,p
    fixture=c.s.OUT/'fixtures.json';population=json.loads(fixture.read_text())['canonical_flops']
    manifests={str(n):json.loads((OUT/f'expansion-train-{n}.json').read_text()) for n in [128,112,96]}
    manifests['reserved95']=json.loads((OUT/'expansion-reserved-95.json').read_text())
    old=json.loads((OUT.parent/'representative-coverage-20260919/combined-population-164.json').read_text())
    excluded={signature(b['board']) for m in [old,*[manifests[str(n)] for n in [128,112,96]]] for b in m['boards']}
    eligible=[(b,m) for b,m in population if signature(b) not in excluded]
    data=json.loads((OUT.parent/'conditional-hu-20260919/subtree.json').read_text())
    w=np.array(data['incoming_class_mass'])[:,c.CLASSES]/c.COUNTS[c.CLASSES];w/=w.max(1)[:,None];w[w<1e-5]=0
    ix=[np.flatnonzero(x) for x in w];masks=[c.MASKS[x] for x in ix]
    joint=w[0,ix[0]][:,None]*w[1,ix[1]][None,:]*((masks[0][:,None]&masks[1][None,:])==0)
    cls=c.CLASSES[ix[0]];cache={}
    for board,_ in population:
        cards=c.cards(board);mask=np.uint64(sum(1<<x for x in cards));legal=[(x&mask)==0 for x in masks]
        mass=(joint*legal[0][:,None]*legal[1][None,:]).sum(1)
        den=np.array([mass[cls==r*14].sum() for r in range(13)])
        cache[board]=(den,den*np.array([any(x//4==r for x in cards) for r in range(13)]))
    def opportunity(items):
        den=sum(cache[b][0]*m for b,m in items);num=sum(cache[b][1]*m for b,m in items)
        return np.divide(num,den,out=np.zeros_like(num),where=den>0)
    full=opportunity(population);eligible_values=opportunity(eligible)
    report=dict(strategy_results_read=False,ranks=list('23456789TJQKA'),full_opportunity=full.tolist(),eligible_opportunity=eligible_values.tolist(),panels={})
    old_keys={signature(b['board']) for b in old['boards']}
    for name,m in manifests.items():
        rates=opportunity([(b['board'],b['weight']) for b in m['boards']])
        report['panels'][name]=dict(set_or_quads_opportunity=rates.tolist(),
            max_difference_from_full_percentage_points=float(np.max(np.abs(rates-full))*100),
            max_difference_from_eligible_percentage_points=float(np.max(np.abs(rates-eligible_values))*100),
            overlap_previous164=sum(signature(b['board']) in old_keys for b in m['boards']))
    report['note']='Opportunity is conditional on the same entering live ranges. These structural differences are reported, not used to redraw candidates. Fresh validation covers only its eligible population; no full-deck accuracy or sampling confidence interval is claimed.'
    files=[Path(__file__),fixture,OUT/'expansion-registration-freeze.json',ROOT/'tools/research/integrated_coverage.py',ROOT/'tools/research/storage_expansion_register_20260920.py',OUT.parent/'conditional-hu-20260919/subtree.json']
    report['inputs_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
    dest.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
if __name__=='__main__':main()
