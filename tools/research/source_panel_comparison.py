"""Compare a co-trained source with rebuilt continuations on its SAME panel.

SOURCE_RESULT REBUILT_RESULT OUTPUT_PREFIX. No solves or source mutations.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np
from continuation_transfer_aggregate import policy_bits
from integrated_coverage_review import audit_result


def compare(source, rebuilt):
    assert source['manifest']==rebuilt['manifest'], 'Different original board panel or settings'
    assert source['boards']==rebuilt['boards'], 'Different board ordering'
    assert source['suit_orbits'] is rebuilt['suit_orbits'] is True
    assert source['entry_cutoff']==rebuilt['entry_cutoff']==1e-5
    assert max(abs(np.asarray(source['board_weights'])-rebuilt['board_weights']))<1e-12
    assert rebuilt['preflop_unchanged'] is True
    original=source['records'][-1]
    updated=rebuilt['records'][-1]
    assert original['iteration']==updated['iteration']==2000
    a,b=original['evaluation'],updated['evaluation']
    assert policy_bits(a['preflop_policy'])==policy_bits(b['preflop_policy'])
    assert 0<=a['gap_total']<.01 and 0<=b['postflop_gap_total']<.01
    norm_error=abs(source['root_normalizer']-rebuilt['root_normalizer'])/source['root_normalizer']
    frequency_error=float(max(abs(np.asarray(a['root_frequencies'])-b['root_frequencies'])))
    assert [r['hand'] for r in a['hands']]==[r['hand'] for r in b['hands']]
    mass_error=max(abs(x['root_mass']-y['root_mass']) for x,y in zip(a['hands'],b['hands']))
    assert max(norm_error,frequency_error,mass_error)<1e-7, 'Entering distribution changed'
    audits=[audit_result(data) for data in [source,rebuilt]]
    return dict(preserved_preflop_and_chance=True,boards=len(source['boards']),
                normalizer_relative_error=norm_error,root_frequency_max_error=frequency_error,
                hand_mass_max_error=mass_error,accounting=audits,
                original_full_gap_bb=a['gap_total'],rebuilt_full_gap_bb=b['gap_total'],
                rebuilt_postflop_gap_bb=b['postflop_gap_total'],
                original_ev_bb=a['ev'],rebuilt_ev_bb=b['ev'],
                ev_change_bb=(np.asarray(b['ev'])-a['ev']).tolist(),
                original_player_gaps_bb=a['gaps'],rebuilt_player_gaps_bb=b['gaps'],
                interpretation='The entering policies, private-card distribution and board panel are preserved. Both postflop strategies are rebuilt. A changed combined-game gap demonstrates reconstruction sensitivity; it does not alone distinguish equilibrium selection, averaging effects or implementation error. Raked general-sum game; no zero-sum safety guarantee is claimed.')


def main():
    source_path,rebuilt_path,prefix=sys.argv[1:]
    prefix=Path(prefix)
    assert not prefix.with_suffix('.json').exists() and not prefix.with_suffix('.md').exists()
    source,rebuilt=[json.loads(Path(p).read_text()) for p in [source_path,rebuilt_path]]
    result=compare(source,rebuilt)
    paths=[source_path,rebuilt_path,__file__,sys.modules[policy_bits.__module__].__file__,
           sys.modules[audit_result.__module__].__file__]
    result['inputs_sha256']={str(p):hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in paths}
    prefix.with_suffix('.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    lines=['# Matched training-panel reconstruction','',result['interpretation'],'',
           f'Boards: {result["boards"]}; both runs use 2,000 iterations.','',
           '| Measurement | Original connected solve | Rebuilt postflop responses |',
           '|---|---:|---:|',
           f'| Full deviation gain (bb) | {result["original_full_gap_bb"]:.9f} | {result["rebuilt_full_gap_bb"]:.9f} |',
           f'| OOP EV (bb) | {result["original_ev_bb"][0]:.9f} | {result["rebuilt_ev_bb"][0]:.9f} |',
           f'| IP EV (bb) | {result["original_ev_bb"][1]:.9f} | {result["rebuilt_ev_bb"][1]:.9f} |','',
           f'Rebuilt postflop residual: {result["rebuilt_postflop_gap_bb"]:.9f} bb.',
           f'Entering checks: normalizer relative error {result["normalizer_relative_error"]:.3g}; '
           f'maximum frequency error {result["root_frequency_max_error"]:.3g}; '
           f'maximum hand-mass error {result["hand_mass_max_error"]:.3g}.','',
           'This is a same-training-panel diagnostic, not independent validation or a new acceptance rule.']
    prefix.with_suffix('.md').write_text('\n'.join(lines)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs_sha256'}))


if __name__=='__main__':
    main()
