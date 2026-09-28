"""Pure synthetic control; no poker draws, GPU, source imports or registrations."""
import ast, copy, json, math
from pathlib import Path
from statistics import NormalDist

folder=Path(__file__).resolve().parent
def extract(file,name,namespace):
    tree=ast.parse((folder/file).read_text())
    functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name]
    assert len(functions)==1
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(folder/file),'exec'),namespace)
    return namespace[name]

count=16384
secondary=extract('river_matched_continuation_v1.py','secondary_analysis',dict(TEST_DEALS=count,NormalDist=NormalDist))
review=extract('river_matched_continuation_review_v1.py','review_secondary',dict(DEALS=count,NormalDist=NormalDist,math=math))
values=[[0.,.25,(-1.)**i,math.sin(i),i/count,1. if i==0 else 0.,10. if i%100==0 else -.1,(i%7)*.001] for i in range(count)]
rows=[]
for i in range(8):
    x=[r[i] for r in values];mean=math.fsum(x)/count
    variance=math.fsum((v-mean)**2 for v in x)/(count-1)
    rows.append(dict(name=str(i),count=count,mean=mean,sample_variance=variance,standard_error=math.sqrt(variance/count)))
analysis=dict(deals=count,contrasts=rows)
result=secondary(analysis);check=review(analysis,result,values)
assert check['passed'] and check['maximum_statistical_error']==0
assert check['tail_diagnostics'][0]['largest_centered_square_fraction']==0
assert check['tail_diagnostics'][5]['largest_centered_square_fraction']>.99
bad=copy.deepcopy(result);bad['contrasts'][2]['lower']+=.1
try:review(analysis,bad,values)
except AssertionError:pass
else:raise AssertionError('Corrupt secondary analysis was accepted')
bad=copy.deepcopy(analysis);bad['contrasts'][0]['count']-=1
try:secondary(bad)
except AssertionError:pass
else:raise AssertionError('Incomplete evaluation was accepted')
print(json.dumps(dict(passed=True,synthetic_deals=count,contrasts=8,corruption_rejected=True,incomplete_rejected=True,no_research_draws=True)))
