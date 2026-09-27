"""Deterministic controls on reused evidence; no fresh outcomes inspected."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
from evaluation_resume_routing_20260927 import restore_accumulator,validate_partition,CompositeEvaluationReader,verify_continuation
from crossed_complete_policy_comparison_v1 import CompletePolicyComparison
from sampled_physical_deals_v1 import PhysicalDeals
from owned_columnar_evaluation_archive_v1 import restore
from later_average_support_v1 import OUT


def main():
    root=Path(tempfile.mkdtemp(prefix='gtopen-resume-routing-control-'))
    (root/'old').mkdir();(root/'new').mkdir()
    control=Path('S:/GTOpen-research/showdown-composite-evaluation-control-v1')
    values=[];hashes={};names=['test-000000','test-000032'];summaries={}
    for name,destination in zip(names,['old','new']):
        for ext in ['.xz','.manifest.json']:
            shutil.copyfile(control/(name+ext),root/destination/(name+ext))
        manifest=json.loads((control/(name+'.manifest.json')).read_text())
        hashes[name]=hashlib.sha256((control/(name+'.manifest.json')).read_bytes()).hexdigest()
        raw=restore(control/(name+'.xz'),manifest,guard=lambda:None)
        summaries[name]=raw['summary.json'];values.append(json.loads(raw['summary.json'])['values'])
    old={names[0]:hashes[names[0]]}
    reader=CompositeEvaluationReader(root/'new',hashes,original_store=root/'old',original_hashes=old,total_deals=64,guard=lambda:None)
    for name in names:assert reader.read_bytes(root/'new'/name/'summary.json')==summaries[name]
    source=(OUT/'bb-context-candidate.json').read_text();context=json.loads(source)
    def comparison():return CompletePolicyComparison(stack=context['config']['stack'],dead_money=context['dead_money'],deals=64)
    full=comparison();full.add(values[0]);full.add(values[1])
    first=comparison();first.add(values[0])
    states=[dict(series=s.series,count=s.count,mean=s.mean,m2=s.m2) for s in first.series]
    resumed=comparison();restore_accumulator(resumed,json.loads(json.dumps(states)),32);resumed.add(values[1])
    assert resumed.finish()==full.finish()
    sampler=PhysicalDeals(source,mode='full_deck',seed=9267201);sampler.sample(32)
    resumed_sampler=PhysicalDeals.restore(json.loads(json.dumps(sampler.checkpoint())),source)
    assert resumed_sampler.sample(32)==sampler.sample(32) and resumed_sampler.checkpoint()==sampler.checkpoint()
    negative=0
    for mapping,prefix in [({names[0]:hashes[names[0]]},old),(hashes,{names[1]:hashes[names[1]]}),
        (hashes,{names[0]:'0'*64}),(dict(hashes,**{'test-000064':'0'*64}),old)]:
        try:validate_partition(mapping,prefix,64)
        except AssertionError:negative+=1
        else:raise AssertionError('Bad routing admitted')
    bad=json.loads(json.dumps(states));bad[0]['count']=31
    try:restore_accumulator(comparison(),bad,32)
    except AssertionError:negative+=1
    else:raise AssertionError('Bad count admitted')
    try:verify_continuation(dict(batch_id_prefix='showdown-composite-evaluation-study-v1',original_registration_sha256='0'*64),{})
    except AssertionError:negative+=1
    else:raise AssertionError('Changed registration admitted')
    a=ast.parse(Path('tools/research/hu_showdown_composite_evaluation_review_v1_20260927.py').read_text())
    b=ast.parse(Path('tools/research/hu_showdown_pipelined_evaluation_review_20260927.py').read_text())
    for fn in ['verify_batch','verify_stability','verify_composite_identities']:
        assert ast.dump(next(n for n in a.body if isinstance(n,ast.FunctionDef) and n.name==fn))==ast.dump(next(n for n in b.body if isinstance(n,ast.FunctionDef) and n.name==fn))
    paths=[Path(__file__),Path('tools/research/evaluation_resume_routing_20260927.py'),
        Path('tools/research/hu_showdown_pipelined_evaluation_20260927.py'),
        Path('tools/research/hu_showdown_pipelined_evaluation_review_20260927.py')]
    for p in paths:compile(p.read_text(),str(p),'exec')
    result=dict(passed=True,exact_accumulator_after_resume=True,exact_sampler_after_resume=True,
        composite_archives_read_with_original_decoder=True,negative_cases=negative,
        independent_verification_functions_unchanged=True,
        inputs={str(p.resolve()):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},production_modified=False)
    (OUT/'showdown-resume-routing-control-20260927.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='inputs'}))


if __name__=='__main__':main()
