"""CPU synthetic policies on retained native catalogs; no new solves or fits."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1',PYTHONDONTWRITEBYTECODE='1')
import copy
import hashlib
import json
from pathlib import Path
import time
import numpy as np
from stack_context_preflop_export_v1 import export
from sampled_physical_deals_v1 import PhysicalDeals
from sampled_physical_root_evaluation_v1 import hand_class
from storage_strategic_common_prior_20260920 import PAIRS,MASKS,CLASSES

OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')
NAME='stack-context-preflop-export-check-v1'


def policy(node,cls,arity):
    if node==0:
        return np.array([.15,.35,.5,0.])
    values=1+((np.arange(arity)+cls+node)%7).astype(float)
    return values/values.sum()


class MockBank:
    def average(self,queries,*,guard):
        probabilities=np.zeros((len(queries['observations']),4));support=np.ones(len(probabilities))
        for index,row in enumerate(queries['observations']):
            cls=hand_class([(int(row['lo'])>>(6*j))&63 for j in range(2)])
            probabilities[index,:row['n']]=policy(int(row['hi'])-1,cls,row['n'])
        for index,row in enumerate(queries['observations']):
            for ancestor,action,*_ in row['own_history']:
                support[index]*=probabilities[ancestor,action]
        return probabilities,support


def main():
    result_path=OUT/(NAME+'-result.json');attempt=OUT/(NAME+'-attempt.json')
    if result_path.exists() or attempt.exists():
        raise ValueError('Existing started/completed control')
    resources=json.loads((OUT/'stack-context-population-v1-result.json').read_bytes())
    paths=[Path(__file__).resolve(),Path(__file__).with_name('stack_context_preflop_export_v1.py')]
    with attempt.open('x') as stream:
        json.dump(dict(inputs={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths}),stream)
    began=time.monotonic();records=[]
    for depth in (20,400):
        record=next(row for row in resources['contexts'].values() if row['depth']==depth)
        source=Path(record['context_path']).read_text();context=json.loads(source)
        catalog=json.loads(Path(record['physical_catalog']).read_bytes());matrix=json.loads(Path(record['matrix']).read_bytes())
        answer=export(source,catalog,matrix['class_mass'],MockBank(),guard=lambda:None)
        # Independent physical-combo propagation checks both card removal and
        # node conditioning, rather than repeating the 169x169 implementation.
        sampler=PhysicalDeals(source,mode='full_deck',seed=0)
        joint=sampler.weights[0,:,None]*sampler.weights[1,None,:]*((MASKS[:,None]&MASKS[None,:])==0)
        joint/=joint.sum();errors=[];zero_nodes=0
        bynode={row['node']:row for row in answer['nodes']}
        def walk(node,mass):
            nonlocal zero_nodes
            tree=context['nodes'][node]
            if not tree['children']:return
            actor=tree['actor'];arity=len(tree['children']);total=float(mass.sum())
            marginal=mass.sum(1 if actor==0 else 0)
            p=np.array([policy(node,int(cls),arity) for cls in CLASSES])
            original=bynode[node]
            assert abs(original['probability_of_reaching_node']-total)<1e-12
            class_prior=np.bincount(CLASSES,weights=marginal,minlength=169)
            errors.append(float(np.max(abs(class_prior-original['entry_mass_by_class']))))
            if total:
                exact=(marginal[:,None]*p).sum(0)/total
                errors.append(float(np.max(abs(exact-original['conditional_action_frequencies']))))
            else:
                zero_nodes+=1
                assert original['conditional_range_by_class'] is None and original['conditional_action_frequencies'] is None
            for action,child in enumerate(tree['children']):
                walk(child,mass*(p[:,action,None] if actor==0 else p[None,:,action]))
        walk(0,joint)
        assert max(errors)<1e-11 and zero_nodes>0 and abs(answer['terminal_entry_mass']-1)<1e-12
        negative=0
        for damaged in (dict(catalog,context_source=source+' '),dict(catalog,rows=catalog['rows'][:-1]),
                        dict(catalog,rows=catalog['rows']+[catalog['rows'][0]])):
            try:export(source,damaged,matrix['class_mass'],MockBank(),guard=lambda:None)
            except ValueError:negative+=1
            else:raise AssertionError('Malformed catalog accepted')
        records.append(dict(depth=depth,nodes=len(answer['nodes']),zero_reach_nodes=zero_nodes,
                            maximum_physical_combo_reference_error=max(errors),negative_cases=negative))
    with result_path.open('x') as stream:
        json.dump(dict(complete=True,passed=True,records=records,seconds=time.monotonic()-began,
                       new_labels=False,new_fits=False,new_poker_deals=False,synthetic_policies=True),stream)
    print(json.dumps(dict(passed=True,records=records,seconds=time.monotonic()-began)))


if __name__=='__main__':main()
