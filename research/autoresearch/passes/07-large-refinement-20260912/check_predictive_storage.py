"""Independent allocation arithmetic and prerequisite completion checks."""
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
RAW=HERE/'raw'


def verify():
    for name in ('predictive-storage-build-v1','predictive-storage-exact-v1','predictive-numerical-v1'):
        r=json.loads((RAW/(name+'-exit.json')).read_text())
        assert r['returncode']==0 and r['reason'] is None, name
    r=json.loads((RAW/'predictive-storage-exact-v1.json').read_text())
    prior=json.loads((RAW/'prediction-storage-inventory-v1.json').read_text())
    s=r['storage']; count=r['players']*r['terminals']
    assert r['read_only'] is True and r['nodes']==prior['nodes']==1567754
    assert r['players']==prior['players']==8 and r['terminals']==prior['terminals']==805640
    assert r['model']=='coupled_deck_v1'
    assert count==s['scalar_terminals']+s['vector_terminals']
    assert s['history_floats']==s['scalar_terminals']+169*s['vector_terminals']
    assert s['history_bytes']==4*s['history_floats']
    assert s['offset_bytes']==count*4
    assert s['policy_bytes']==prior['one_action_array_bytes']
    assert s['persistent_extra_bytes']==s['history_bytes']+s['offset_bytes']+s['policy_bytes']
    assert s['cap_bytes']==4*1024**3 and s['fits_four_gib'] is True
    assert s['persistent_extra_bytes']<=s['cap_bytes']
    dense=count*169*4+s['policy_bytes']
    assert dense==prior['dense_terminals_plus_action_policy_bytes']
    return dict(evidence_verified=True,compressed_extra_bytes=s['persistent_extra_bytes'],
                dense_extra_bytes=dense,bytes_saved=dense-s['persistent_extra_bytes'],
                fraction_saved=1-s['persistent_extra_bytes']/dense,
                source_nodes=r['nodes'],scalar_terminals=s['scalar_terminals'],
                vector_terminals=s['vector_terminals'],large_gpu_allocation_tested=False,
                scope='Exact-tree storage arithmetic plus small numerical compression/update tests')


if __name__=='__main__':
    print(json.dumps(verify(),indent=2))
