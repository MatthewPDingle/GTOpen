"""Check the execution-only memory change before drawing fresh pilot hands."""
import ast
import hashlib
import json
from pathlib import Path

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
TOOLS=ROOT/'tools/research'


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def definitions(path):
    tree=ast.parse(path.read_text(encoding='utf-8'))
    return {n.name:n for n in tree.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))},tree


def main():
    paths=[TOOLS/('board_river_bounds_pilot_'+part+'_v'+str(version)+'.py')
           for part in ('support','run') for version in (1,2)]
    s1,t1=definitions(paths[0]);s2,t2=definitions(paths[1])
    r1,_=definitions(paths[2]);r2,_=definitions(paths[3])
    same=[]
    for a,b,names in ((s1,s2,('PairPreparation','Adapter','load')),
                      (r1,r2,('immutable','status','native_values','execute','transport'))):
        for name in names:
            assert ast.dump(a[name])==ast.dump(b[name]),name
            same.append(name)
    constants={}
    for tree in (t1,t2):
        values={n.targets[0].id:ast.literal_eval(n.value) for n in tree.body
                if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name)
                and n.targets[0].id in ('PREFIX','LIMIT_BYTES','SEED','DEALS')}
        if constants:assert values==constants
        constants=values
    namespace={'CUDA_BUDGET_BYTES':4_000_000_000,'CUDA_HEADROOM_BYTES':2_000_000_000}
    exec(compile(ast.Module(body=[s2['memory_admitted']],type_ignores=[]),'<memory-admission-control>','exec'),namespace)
    cases=[(6_000_000_000,0,True),(5_999_999_999,0,False),
           (4_800_000_000,1_200_000_000,True),(4_799_999_999,1_200_000_000,False),
           (2_000_000_000,4_000_000_000,True),(1_999_999_999,4_000_000_000,False)]
    for free,reserved,expected in cases:assert namespace['memory_admitted'](free,reserved)==expected
    for reserved in (-1,4_000_000_001):
        try:namespace['memory_admitted'](10_000_000_000,reserved)
        except AssertionError:pass
        else:raise AssertionError('Invalid own reservation accepted')
    assert not (OUT/'weighted-complete-river-bounds-pilot-v1-registration.json').exists()
    result=dict(passed=True,inputs={str(p):digest(p) for p in paths+[Path(__file__)]},
        unchanged_policy_and_transport_definitions=same,fixed_design=constants,
        cuda_budget_bytes=4_000_000_000,external_headroom_bytes=2_000_000_000,
        tested_boundaries=cases,invalid_reservations_rejected=2,new_physical_deals=0,
        prior_invocation=dict(pid=53812,session=25215,stopped_before_fresh_registration=True,
            reason='Waiting for fixed 10GB free threshold despite measured qualification peak near 1.2GB; execution-only admission revision.'),
        limitation='Boundary checks validate admission arithmetic, not future workload availability. PyTorch allocator enforces its separate cap during execution.')
    destination=OUT/'weighted-complete-river-bounds-pilot-v1-resource-control-v2.json'
    with destination.open('x',encoding='utf-8') as f:json.dump(result,f,separators=(',',':'),allow_nan=False)
    print(json.dumps(dict(passed=True,unchanged=same,memory_boundaries=len(cases),fixed_design=constants)))


if __name__=='__main__':main()
