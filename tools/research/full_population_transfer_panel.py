"""Prepare a full-population supplement using chance geometry only.

Does not read source solve results or any held-out strategic outcomes.
Does not launch workers or modify an existing registration.
"""
import hashlib
import json
import math
from pathlib import Path
from fractions import Fraction
import integrated_coverage as c
from independent_validation_panel import signature

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'research/preflop-evolution/representative-coverage-20260919'


def main():
    paths = [c.OUT/'reserved.json', OUT/'report-47.json',
             c.OUT/'old-two-orbits.json', c.OUT/'panel-ab.json']
    fixture_path = c.s.OUT/'fixtures.json'
    validation_path = OUT/'validation-95.json'
    protocol = OUT/'FULL-POPULATION-SUPPLEMENT.md'
    canonical = json.loads(fixture_path.read_text())['canonical_flops']
    mass = {}
    for board, count in canonical:
        key = signature(board)
        assert key not in mass
        physical = {tuple(sorted(c.cards(c.relabel(board, p)))) for p in c.PERMS}
        assert len(physical) == count
        mass[key] = count
    assert len(mass) == 1755 and sum(mass.values()) == math.comb(52, 3)
    excluded = {}
    for path in paths:
        for row in json.loads(path.read_text())['boards']:
            key = signature(row['board'])
            assert key in mass
            excluded.setdefault(key, row['board'])
    validation = json.loads(validation_path.read_text())
    sample = [row['board'] for row in validation['boards']]
    keys = [signature(b) for b in sample]
    assert len(sample) == len(set(keys)) == 95
    assert not set(keys) & excluded.keys()
    assert all(row['weight'] == 1 for row in validation['boards'])
    excluded_mass = sum(mass[k] for k in excluded)
    total = sum(mass.values())
    eligible_mass = total-excluded_mass
    assert len(excluded) == 69 and (excluded_mass, eligible_mass) == (1000, 21100)
    supplement = dict(suit_orbits=True, bet_menu='50', reserved=False,
        population='Exact complete set of orbits excluded from independent validation95; includes training boards.',
        boards=[dict(board=b, weight=mass[k]) for k,b in excluded.items()])
    # Integer weights equivalent to m/22100 per excluded orbit and
    # 21100/(95*22100) per sampled eligible board. Preserve original95.
    combined = dict(suit_orbits=True, bet_menu='50', reserved=False,
        population='Full-deck chance target: exact excluded stratum plus original systematic95 eligible sample.',
        boards=[dict(board=b, weight=eligible_mass) for b in sample] +
               [dict(board=b, weight=mass[k]*len(sample)) for k,b in excluded.items()])
    den = sum(row['weight'] for row in combined['boards'])
    assert den == total*len(sample)
    assert sum(Fraction(row['weight'],den) for row in combined['boards'][:95]) == Fraction(eligible_mass,total)
    for row in combined['boards'][95:]:
        assert Fraction(row['weight'],den) == Fraction(mass[signature(row['board'])],total)
    assert len({signature(row['board']) for row in combined['boards']}) == 164
    # Replacing the sampled eligible stratum by its entire exact population
    # restores every one of the 22,100 physical flops exactly once.
    exact = {k:count for k,count in mass.items() if k not in excluded}
    exact.update({k:mass[k] for k in excluded})
    assert exact == mass and sum(exact.values()) == 22100
    destinations = [OUT/'supplement-excluded-69.json', OUT/'combined-population-164.json',
                    OUT/'full-population-supplement-freeze.json']
    assert not any(p.exists() for p in destinations)
    for path, data in zip(destinations, [supplement, combined]):
        path.write_text(json.dumps(data, indent=2)+'\n')
    inputs = [Path(__file__), protocol, fixture_path, validation_path, *paths, *destinations[:2]]
    audit = dict(passed=True, excluded_orbits=len(excluded), excluded_physical_mass=excluded_mass,
                 eligible_physical_mass=eligible_mass, full_physical_mass=total,
                 sampled_eligible_orbits=95, combined_orbits=164, integer_weight_sum=den,
                 expected_additional_workers_per_source=59,
                 source_results_accessed=False, strategic_workers_launched=False,
                 note='Chance registration only. Combined EV ratios and maximized gains are not unbiased full-deck accuracy estimates.',
                 inputs_sha256={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs})
    destinations[-1].write_text(json.dumps(audit, indent=2)+'\n')
    print(json.dumps({k:v for k,v in audit.items() if k != 'inputs_sha256'}, indent=2))


if __name__ == '__main__':
    main()
