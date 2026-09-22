"""Prepared-pipeline isolation audit and old-fixture protocol readback; no GPU."""
import ast
import copy
import json
import math
from pathlib import Path
import numpy as np
from loopback_research_validation import idle
from sampled_physical_root_evaluation_v1 import ROOT,sha,save
from sampled_physical_reservoir_v1 import PhysicalReservoir
from sampled_allin_protocol_v3 import AllinCache,ingest
from sampled_evaluation_intervals_v1 import Plan,PairedEvaluation

OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
SOURCES=ROOT/'tools/research'
PREFIX='sampled-physical-allin-pipeline-control-v1'


def main():
    assert idle()
    newnames=['hu_sampled_physical_allin_pilot_20260923.py','hu_sampled_physical_allin_review_20260923.py',
        'hu_sampled_physical_allin_evaluation_20260923.py','hu_sampled_physical_allin_evaluation_review_20260923.py',
        'hu_sampled_physical_allin_btn_evaluation_20260923.py','hu_sampled_physical_allin_btn_review_20260923.py',
        'hu_sampled_physical_allin_study_20260923.py','sampled_physical_allin_evaluation_v1.py',
        'sampled_allin_protocol_v3.py']
    trees={n:ast.parse((SOURCES/n).read_text()) for n in newnames}
    def function(tree,name):return next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    def dump(n):return ast.dump(n,include_attributes=False)
    oldpath=SOURCES/'hu_sampled_physical_dense_pilot_20260922.py'
    oldworker=function(ast.parse(oldpath.read_text()),'worker')
    newworker=copy.deepcopy(function(trees[newnames[0]],'worker'))
    old_asserts={}
    for n in ast.walk(oldworker):
        if isinstance(n,ast.Assert):
            if "'verified_traversals'" in dump(n):old_asserts['traversals']=n
            if "'maximum_reference_error'" in dump(n):old_asserts['error']=n
    class WorkerNormalization(ast.NodeTransformer):
        def visit_Assign(self,node):
            names=[n.id for n in node.targets if isinstance(n,ast.Name)]
            if names==['cache']:return None
            if names==['batch'] and isinstance(node.value,ast.Call) and dump(node.value.func)==dump(ast.parse('cache.batch',mode='eval').body):return None
            return self.generic_visit(node)
        def visit_Assert(self,node):
            text=dump(node)
            if "attr='sha256'" in text and "id='cache'" in text:return None
            if "'verified_query_lookup_traversals'" in text:return copy.deepcopy(old_asserts['traversals'])
            if "'maximum_query_lookup_error'" in text:return copy.deepcopy(old_asserts['error'])
            return self.generic_visit(node)
        def visit_Call(self,node):
            if isinstance(node.func,ast.Name) and node.func.id=='ingest':
                assert isinstance(node.args[-1],ast.Name) and node.args[-1].id=='cache';node.args.pop()
            return self.generic_visit(node)
        def visit_Constant(self,node):
            replacements={
                'target/release/examples/hu_sampled_allin_bridge_v3.exe':'target/release/examples/hu_sampled_batch_bridge_v2.exe',
                'Conditional preflop all-in estimator only; dense training schedule and fit unchanged. No strength evaluation or model promotion. Full played bank only.':'Eightfold fresh data per update. No strength evaluation or model promotion. Full played bank only.'}
            if isinstance(node.value,str) and node.value in replacements:node.value=replacements[node.value]
            return node
    normalized=WorkerNormalization().visit(newworker)
    assert dump(normalized)==dump(oldworker),'Training worker differs beyond declared cache/estimator transport'
    oldevalpath=SOURCES/'sampled_physical_root_evaluation_cuda_v1.py'
    original=ast.parse(oldevalpath.read_text());new=copy.deepcopy(trees['sampled_physical_allin_evaluation_v1.py'])
    new.body[0]=copy.deepcopy(original.body[0])
    class AlphaNormalization(ast.NodeTransformer):
        def visit_Constant(self,node):
            if isinstance(node.value,float) and node.value==.025:node.value=.05
            return node
    assert dump(AlphaNormalization().visit(new))==dump(original),'Root evaluation changed beyond alpha allocation'
    # Extract the actual BTN selector expression and execute bounded toy cases.
    btn=trees['hu_sampled_physical_allin_btn_evaluation_20260923.py']
    response=next(n.value for n in ast.walk(btn) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='response' for t in n.targets))
    counts=[0]*169;advantages=[0.]*169;reach_sums=[0.]*169
    for i in range(5):counts[i]=16;reach_sums[i]=1.
    advantages[:5]=[2.,-2.,0.,2.,2.];counts[3]=15;reach_sums[4]=0.
    values=eval(compile(ast.Expression(response),'<registered-selector>','eval'),dict(counts=counts,advantages=advantages,reach_sums=reach_sums))
    assert values['actions'][:5]==[1,0,0,-1,-1] and values['actions'][5:]==[-1]*164
    # Validate the declared three-comparison interval arithmetic independently.
    plan=Plan(-400.5,400.5,('trained-response','always-fold','always-call'),(16,),alpha=.025)
    e=PairedEvaluation(plan,'trained-response');xs=[-2.,3.,0.,.5]*4
    for x in xs:e.add_difference(x)
    mean=math.fsum(xs)/16;variance=math.fsum((x-mean)**2 for x in xs)/15
    radius=math.sqrt(2*variance*math.log(12/.025)/16)+7*801*math.log(12/.025)/45
    assert math.isclose(e.interval()['radius'],radius,rel_tol=1e-14)
    # Independent per-record replay of the adapter's native fixture.
    protocolpath=OUT/'sampled-physical-allin-protocol-control-v1-result.json'
    protocol=json.loads(protocolpath.read_text());assert protocol['passed']
    preg=OUT/'sampled-physical-allin-protocol-control-v1-registration.json'
    assert protocol['registration_sha256']==sha(preg)
    for p,h in {**json.loads(preg.read_text())['inputs'],**protocol['artifacts']}.items():assert sha(p)==h,p
    store=Path('S:/GTOpen-research/sampled-physical-allin-protocol-control-v1')
    cache=AllinCache(store/'cache.json',sha(store/'cache.json'))
    q=json.loads((store/'queries.json').read_text());u=json.loads((store/'updates.json').read_text())
    actual=[PhysicalReservoir(17,i,921+i,q['context_source']) for i in (0,1)]
    expected=[PhysicalReservoir(17,i,921+i,q['context_source']) for i in (0,1)]
    counts=ingest(q,u,actual,1,cache)
    for index,player,tag,values in u['records']:
        if tag>0:expected[player].add(q['observations'][index],values,1)
    for a,b in zip(actual,expected):
        assert a.summary()==b.summary() and a.rng.bit_generator.state==b.rng.bit_generator.state
        for k in ('keys','active','arity','values','iterations'):assert np.array_equal(getattr(a,k),getattr(b,k))
    # The seven ordered stages include both independent evaluation readbacks.
    study=trees['hu_sampled_physical_allin_study_20260923.py']
    stages=ast.literal_eval(next(n.value for n in study.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='STAGES' for t in n.targets)))
    assert [s[0] for s in stages]==['training','training-audit','evaluation-prepare','evaluation','evaluation-audit','btn-evaluation','btn-evaluation-audit']
    assert all((SOURCES/s[1]).is_file() for s in stages)
    paths=[Path(__file__),oldpath,oldevalpath,preg,protocolpath,OUT/'SAMPLED-PHYSICAL-ALLIN-PLAN.md',
        SOURCES/'sampled_evaluation_intervals_v1.py',*[SOURCES/n for n in newnames]]
    report=dict(passed=True,inputs={str(p):sha(p) for p in paths},
        training_worker_identical_except_declared_estimator_transport=True,
        root_evaluator_identical_except_family_alpha=True,btn_selector_cases=5,
        independent_interval_arithmetic=True,adapter_reservoir_arrays_and_rng_exact=True,
        positive_records=counts,stages=stages,training_launched=False,production_modified=False,
        scope='Static change-isolation audit plus executable old-fixture data-routing, reservoir and selection/arithmetic controls. Does not replace complete-run checkpoint/evaluation audits or prove better ranges.')
    save(OUT/f'{PREFIX}-result.json',report);print(json.dumps({k:v for k,v in report.items() if k!='inputs'}))


if __name__=='__main__':main()
