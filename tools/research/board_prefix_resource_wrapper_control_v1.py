"""Mechanical dependency routing and restoration, without running a study."""
import json
from pathlib import Path
from board_prefix_resource_wrapper_v1 import inventory_override, legacy
from later_average_support_v1 import OUT,read
from sampled_physical_root_evaluation_v1 import sha
from board_prefix_publication_v1 import atomic_json


def main():
    proof_path = OUT/'global-research-inventory-control-v2-result.json'
    proof = read(proof_path)
    assert proof['passed'] and proof['activity_rejections'] == 3
    for p,h in proof['inputs'].items(): assert sha(p)==h,p
    original = legacy.measure; calls=[]
    expected=[dict(root='synthetic',files=1,logical_bytes=27001,allocated_file_bytes=28672)]
    def supplied():
        calls.append(1); return expected
    with inventory_override(supplied):
        from hu_root_retained_storage_admitted_study_20260924 import measure as imported
        assert imported() is expected and calls==[1]
    assert legacy.measure is original
    try:
        with inventory_override(supplied):
            assert legacy.measure() is expected
            raise RuntimeError('Deliberate caller failure')
    except RuntimeError as error: assert str(error)=='Deliberate caller failure'
    else: raise AssertionError('Injected failure disappeared')
    assert legacy.measure is original and calls==[1,1]
    paths=[proof_path,Path(__file__),Path(__file__).with_name('board_prefix_resource_wrapper_v1.py'),
           Path(__file__).with_name('global_research_inventory_v2.py'),
           Path(__file__).with_name('board_matched_prefix_v2.py')]
    result=dict(passed=True,inputs={str(p):sha(p) for p in paths},restoration_cases=2,
        scope='Synthetic routing/restoration only; real accounting and activity qualification is separately bound.',
        scientific_work_started=False, production_modified=False)
    atomic_json(OUT/'board-prefix-resource-wrapper-control-v1-result.json',result)
    print(json.dumps(result),flush=True)


if __name__=='__main__': main()
