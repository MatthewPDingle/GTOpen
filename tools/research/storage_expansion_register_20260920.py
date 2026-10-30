"""Freeze larger training choices and disjoint validation without strategic outcomes."""
import bisect
import hashlib
import itertools
import json
import math
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'research/preflop-evolution/ssd-storage-20260920'
OLD=OUT.parent/'representative-coverage-20260919/combined-population-164.json'
FIXTURE=ROOT/'research/preflop-evolution/wizard-continuation-20260919/fixtures.json'
TRAIN_SEED='stored-expansion-full-population-20260920-v1'
TEST_SEED='stored-expansion-reserved95-20260920-v1'

def signature(board):
    cards=[('23456789TJQKA'.index(board[i]),'cdhs'.index(board[i+1])) for i in range(0,len(board),2)]
    return min(tuple(sorted((r*4+p[s] for r,s in cards))) for p in itertools.permutations(range(4)))

def sample(population,n,seed):
    cumulative=list(itertools.accumulate(m for b,m in population));total=cumulative[-1]
    numerator=int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],'big')
    # Exact integer arithmetic avoids float boundary ambiguity.
    indices=[bisect.bisect_right(cumulative,((i*2**64+numerator)*total)//(n*2**64)) for i in range(n)]
    selected=[population[i][0] for i in indices]
    assert len(set(selected))==n
    return dict(suit_orbits=True,bet_menu='50',future_card_policy='projected_explicit',
        seed=seed,offset_numerator=numerator,offset_denominator=2**64,
        boards=[dict(board=b,weight=1) for b in selected])

def main():
    assert FIXTURE.is_file(),FIXTURE
    assert not (OUT/'expansion-registration-freeze.json').exists()
    population=json.loads(FIXTURE.read_text())['canonical_flops']
    assert len(population)==1755 and sum(m for b,m in population)==math.comb(52,3)
    keys={signature(b):m for b,m in population};assert len(keys)==1755
    excluded={signature(r['board']) for r in json.loads(OLD.read_text())['boards']}
    assert len(excluded)==164
    generated=[];training={}
    for count in [128,112,96]:
        manifest=sample(population,count,TRAIN_SEED)
        manifest.update(reserved=False,population='Full canonical physical-flop population, systematic probability-proportional-to-mass sampling; equal sample weights.')
        training[count]=manifest;excluded.update(signature(r['board']) for r in manifest['boards'])
        path=OUT/f'expansion-train-{count}.json';assert not path.exists()
        path.write_text(json.dumps(manifest,indent=2));generated.append(path)
    eligible=[(b,m) for b,m in population if signature(b) not in excluded]
    held=sample(eligible,95,TEST_SEED)
    held.update(reserved=True,population='Eligible canonical orbits excluding all three candidate training panels and all 164 previous comparison boards; not a full-deck metric.')
    assert not {signature(r['board']) for r in held['boards']} & excluded
    path=OUT/'expansion-reserved-95.json';assert not path.exists();path.write_text(json.dumps(held,indent=2));generated.append(path)
    files=[Path(__file__),FIXTURE,OLD,OUT/'EXPANSION-REGISTRATION.md',*generated]
    result=dict(passed=True,strategy_results_read=False,candidate_counts=[128,112,96],validation_count=95,
        full_physical_mass=sum(keys.values()),excluded_orbits=len(excluded),excluded_physical_mass=sum(keys[k] for k in excluded),
        eligible_orbits=len(eligible),eligible_physical_mass=sum(m for b,m in eligible),
        inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in files})
    (OUT/'expansion-registration-freeze.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

if __name__=='__main__':main()
