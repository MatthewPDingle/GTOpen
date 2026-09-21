"""Register a disjoint larger comparison without reading its strategic outcomes."""
import json
from pathlib import Path
from storage_phase_run_20260920 import ROOT, OUT, EVIDENCE, read, sha
from storage_expansion_register_20260920 import signature, sample, FIXTURE, OLD

SEED = 'stored-confirm190-independent-20260922-v1'
PANEL = OUT/'strategic-confirm190-v1-manifest.json'
REGISTRATION = OUT/'strategic-confirm190-v1-registration.json'
PROTOCOL = OUT/'STRATEGIC-CONFIRM190-PROTOCOL.md'


def selection():
    exclusions = [OLD, OUT/'expansion-reserved-95-evaluation-v1.json']
    exclusions += [OUT/f'expansion-train-{n}.json' for n in [128,112,96]]
    excluded = set()
    for path in exclusions:
        excluded.update(signature(b['board']) for b in read(path)['boards'])
    population = read(FIXTURE)['canonical_flops']
    assert len(population) == 1755 and sum(m for b,m in population) == 22100
    eligible = [(b,m) for b,m in population if signature(b) not in excluded]
    assert len(eligible) == 1207
    panel = sample(eligible,190,SEED)
    panel.update(future_card_policy='plain_explicit',reserved=True,
                 population='Canonical orbits excluding the three training candidates, old164 and reserved95; not full-deck.')
    signatures = {signature(b['board']) for b in panel['boards']}
    assert len(signatures) == 190 and not signatures & excluded
    return panel, exclusions, len(eligible), sum(m for b,m in eligible)


def main():
    assert not REGISTRATION.exists() and not PANEL.exists()
    assert not list(OUT.glob('strategic-confirm190-v1-*-result*'))
    prior = read(OUT/'strategic-reserved95-v1-review.json')
    assert prior['comparison_complete'] and prior['response_convergence_passed']
    assert read(OUT/'strategic-reserved95-v1-status.json')['step'] == 'complete-awaiting-scientific-review'
    final = read(OUT/'strategic-final-policies-v1-freeze.json')
    assert len(final['policies']) == 2
    sources = []
    for item in final['policies']:
        path = OUT/f"strategic-{item['branch']}112-2000-v1-result.json"
        assert item['target']==2000 and sha(path)==item['result_sha256']
        sources.append(path)
    sources.append(EVIDENCE/'report47-full-result.json')
    controls = read(OUT/'strategic-evaluator-controls-v1-review.json')
    for path in sources: assert sha(path)==controls['inputs_sha256'][str(path.relative_to(ROOT))]
    panel, exclusions, count, mass = selection()
    with PANEL.open('x') as f: json.dump(panel,f,indent=2)
    files = [Path(__file__), ROOT/'tools/research/storage_strategic_confirm_20260922.py',
             ROOT/'tools/research/storage_expansion_register_20260920.py', FIXTURE, PROTOCOL, PANEL,
             OUT/'strategic-final-policies-v1-freeze.json', OUT/'strategic-evaluator-controls-v1-review.json',
             OUT/'strategic-reserved95-v1-review.json', OUT/'strategic-reserved95-v1-analysis.json',
             *exclusions, *sources]
    registration = dict(passed=True,new_panel_outcomes_read=False,seed=SEED,boards=190,workers=570,
                        eligible_orbits=count,eligible_physical_mass=mass,full_physical_mass=22100,
                        disjoint_from_training_candidates_old164_and_reserved95=True,
                        iterations=2000,maximum_total_seconds=43200,maximum_worker_seconds=900,
                        preceding_worker_seconds=14128.577,estimated_worker_seconds=28257.154,
                        inputs_sha256={str(p.relative_to(ROOT)):sha(p) for p in files},production_ready=False)
    with REGISTRATION.open('x') as f: json.dump(registration,f,indent=2)
    print(json.dumps({k:v for k,v in registration.items() if k!='inputs_sha256'},indent=2))


if __name__ == '__main__': main()
