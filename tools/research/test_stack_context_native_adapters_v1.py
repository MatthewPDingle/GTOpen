"""Implementation checks only: retained policies, synthetic values, tiny native trees.

No learning comparison, new accuracy claims, GPU work or production mutation.
"""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
import numpy as np

import stack_context_full_policy_v1 as full
from stack_context_inputs_v1 import Registry, digest
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from stack_context_current_policy_v1 import CurrentPolicy
import stack_context_board_components_v1 as parts
import stack_context_board_targets_v1 as targets
import board_root_components_v1 as old_parts
from board_fixed_policy_values_v1 import evaluate
from sampled_physical_root_evaluation_v1 import hand_class
import test_stack_context_full_policy_v1 as retained

ROOT=Path('T:/Dev/GTOpen')
OUT=ROOT/'research/preflop-evolution/blind-defense-20260922'
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES=Path('S:/GTOpen-research/stack-context-model-control-v1')
CONTROL=Path('S:/GTOpen-research/stack-context-full-control-v1')
DEPTHS=(20,40,60,100,150,200,400)
INPUTS={}
NATIVE=[]


def read(path,expected=None):
    path=Path(path);raw=path.read_bytes();sha=hashlib.sha256(raw).hexdigest()
    if expected is not None:assert sha==expected,path
    INPUTS[str(path)]=sha
    return json.loads(raw)


def native(exe,args):
    exe=ROOT/'target/release/examples'/exe
    INPUTS[str(exe)]=hashlib.sha256(exe.read_bytes()).hexdigest()
    done=subprocess.run([str(exe),*map(str,args)],capture_output=True,timeout=30,
                        creationflags=subprocess.CREATE_NO_WINDOW)
    assert done.returncode==0,done.stderr.decode(errors='replace')[-2000:]
    NATIVE.append(dict(executable=str(exe),stdout_sha256=hashlib.sha256(done.stdout).hexdigest(),
                       output_bytes=len(done.stdout),exit_code=done.returncode))
    return json.loads(done.stdout)


class NativeAdapterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        proof=read(OUT/'stack-context-full-control-v1-registration.json')['inputs']
        artifacts=read(OUT/'stack-context-full-control-v1-result.json')['artifacts']
        cls.entries=[];cls.queries={};cls.contexts={};cls.sources={}
        for d in DEPTHS:
            cp=GEOMETRY/'fixtures'/f'stack-{d}-context.json'
            pp=GEOMETRY/f'stack-{d}-public.json';qp=QUERIES/f'stack-{d}-queries.json'
            context=read(cp,proof[str(cp)]);source=cp.read_text();key=digest(source)
            cls.sources[d]=source;cls.contexts[d]=context
            cls.entries.append(dict(name=f'{d}bb',split='heldout' if d in (60,150) else 'fit',
                                    context_source=source,public_document=read(pp,proof[str(pp)])))
            cls.queries[key]=read(qp,proof[str(qp)])
        cls.cases=[]
        for kind,width in ((Registry,362),(RelativeRegistry,387)):
            fixture=read(CONTROL/f'{width}-fixture.json',artifacts[str(CONTROL/f'{width}-fixture.json')])
            registry=kind(cls.entries)
            assert registry.manifest==fixture['registry']
            cls.cases.append((registry,fixture))

    def engine(self,case,depth):
        registry,fixture=case;key=digest(self.sources[depth])
        return CurrentPolicy(fixture['model'],registry,context_sha256=key,resources=fixture['resources'])

    def test_all_depths_streets_and_overrides_match_reference(self):
        for registry,fixture in self.cases:
            for d in DEPTHS:
                key=digest(self.sources[d]);q=self.queries[key]
                engine=self.engine((registry,fixture),d);got=engine.prepare(q)
                expected,prepared,coverage=full.predict(fixture['model'],registry,q,
                    context_sha256=key,resources=fixture['resources'])
                np.testing.assert_array_equal(got['features'],prepared['features'])
                self.assertEqual(got['keys'],prepared['keys'])
                self.assertEqual(got['own_history'],prepared['own_history'])
                np.testing.assert_allclose(engine.infer(got),expected,rtol=0,atol=1e-10)
                self.assertEqual(set(o['phase'] for o in q['observations']),{0,1,2,3})
                if d in (60,150):self.assertFalse(got['mask'].any())
                else:self.assertTrue(coverage['learned_local_state'])
                post=np.array([o['phase']>0 for o in q['observations']])
                bare=[{k:v for k,v in o.items() if k!='own_history'} for o in q['observations'] if o['phase']>0]
                score=engine.prepare(dict(context_source=q['context_source'],observations=bare),require_history=False)
                self.assertIsNone(score['own_history'])
                np.testing.assert_allclose(engine.score_rows(q['context_source'],bare),expected[post],rtol=0,atol=1e-10)

    def test_retained_trained_policy_not_only_synthetic(self):
        retained.FullContextPolicyTests.setUpClass();old=retained.FullContextPolicyTests
        INPUTS.update(old.identities)
        for fixture in old.fixtures:
            for registry in old.registries:
                model=old.lift(fixture['originals'][-1],registry,fixture['resources'])
                engine=CurrentPolicy(model,registry,context_sha256=old.key,resources=fixture['resources'])
                for q in (fixture['queries'],old.catalog_queries):
                    expected,_,_=full.predict(model,registry,q,context_sha256=old.key,resources=fixture['resources'])
                    np.testing.assert_allclose(engine.infer(engine.prepare(q)),expected,rtol=0,atol=1e-10)

    def test_reject_context_keys_menu_history_and_foreign_preparation(self):
        engine=self.engine(self.cases[1],20);key=digest(self.sources[20]);q=self.queries[key]
        with self.assertRaises(ValueError):engine.prepare(q,require_history=False)
        bare=copy.deepcopy(q)
        for o in bare['observations']:o.pop('own_history')
        with self.assertRaises(ValueError):engine.prepare(bare)
        with self.assertRaises(ValueError):engine.prepare(bare,require_history=False)
        for field,value in (('hi','999999'),('lo','0'),('actor',2),('phase',4),('n',5)):
            bad=copy.deepcopy(q);bad['observations'][0][field]=value
            with self.assertRaises((ValueError,IndexError),msg=field):engine.prepare(bad)
        wrong=dict(q,context_source=self.sources[40])
        with self.assertRaises(ValueError):engine.prepare(wrong)
        other=self.engine(self.cases[1],20)
        with self.assertRaises(ValueError):other.infer(engine.prepare(q))

    def test_native_full_physical_preflop_catalogs_and_real_ancestors(self):
        for d in (20,200):
            catalog=native('hu_preflop_visible_catalog_v1.exe',[GEOMETRY/'fixtures'/f'stack-{d}-context.json'])
            for case in self.cases:
                engine=self.engine(case,d);context=self.contexts[d]
                p,error=targets.preflop_policy(catalog,context,engine)
                self.assertLessEqual(error,1e-12)
                self.assertEqual(set(p),{i for i,n in enumerate(context['nodes']) if n['children']})
                for node,values in p.items():
                    self.assertEqual(values.shape,(169,len(context['nodes'][node]['children'])))
                    np.testing.assert_allclose(values.sum(1),1,rtol=0,atol=1e-12)
                bad=copy.deepcopy(catalog);bad['rows'].pop()
                with self.assertRaises(ValueError):targets.preflop_policy(bad,context,engine)

    def test_tiny_native_fixed_boards_score_without_invented_history(self):
        request=dict(board=[0,5,10,15,20],hands=[[[24,28],[32,36]],[[25,29],[32,40]]])
        with tempfile.TemporaryDirectory(prefix='gtopen-stack-native-') as tmp:
            rp=Path(tmp)/'request.json';rp.write_text(json.dumps(request))
            for d in (20,200):
                tree=native('hu_fixed_board_tree_v1.exe',[GEOMETRY/'fixtures'/f'stack-{d}-context.json',rp])
                context=self.contexts[d]
                self.assertEqual({b['branch'] for b in tree['branches']},
                                 {i for i,n in enumerate(context['nodes']) if n['leaf'] and n['leaf']['type']=='postflop'})
                for case in self.cases:
                    engine=self.engine(case,d);policies=targets.policy_rows(tree,engine)
                    for branch,post in zip(tree['branches'],policies):
                        self.assertEqual(set(post),{i for i,n in enumerate(branch['nodes']) if n['kind']==0})
                        self.assertTrue(all('own_history' not in o for n in branch['nodes'] if n['kind']==0 for o in n['observations']))
                    weights=[np.array([.3,.7]),np.array([.6,.4])]
                    classes=[np.array([hand_class(h) for h in hands]) for hands in tree['hands']]
                    pre=synthetic_pre(context)
                    args=(tree,policies,pre,weights,classes,3.7,np.full(169,1/169))
                    result=parts.board_terms(context,*args)
                    self.assertTrue(np.isfinite(result).all())
                    np.testing.assert_array_equal(result[:,[0,3]],0)
                    if d==200:
                        np.testing.assert_allclose(result,old_parts.board_terms(*args),rtol=0,atol=1e-10)
                    else:
                        # 20bb has no non-all-in 4-bet postflop branch.
                        expected=np.zeros((2,4))
                        by_id={b['branch']:(b,p) for b,p in zip(tree['branches'],policies)}
                        expected[:,1]=evaluate(tree,*by_id[2],weights)[0]
                        expected[:,2]=evaluate(tree,*by_id[5],[weights[0],weights[1]*pre[3][classes[1],1]])[0]
                        import math
                        expected=np.column_stack([np.bincount(classes[0],weights=weights[0]*expected[:,a],minlength=169) for a in range(4)])
                        expected*=math.comb(52,5)/math.comb(48,5)/3.7/(1/169)
                        np.testing.assert_allclose(result,expected,rtol=0,atol=1e-10)

    def test_exact_terms_against_independent_pairwise_recursion(self):
        rng=np.random.default_rng(193);mass=rng.random((169,169));mass/=mass.sum()
        matrix=SimpleNamespace(mass=mass,bb_mass=mass.sum(1),bb=mass*rng.normal(0,7,mass.shape),bb_fold=-1.,bb_win=2.5)
        for d,context in self.contexts.items():
            pre=synthetic_pre(context)
            def visit(index):
                n=context['nodes'][index]
                if not n['children']:
                    kind=n['leaf']['type']
                    if kind=='fold':return mass*n['leaf']['utilities'][0]
                    if kind=='showdown':return matrix.bb
                    return np.zeros_like(mass)
                out=np.zeros_like(mass)
                for action,child in enumerate(n['children']):
                    probabilities=pre[index][:,action]
                    out+=visit(child)*(probabilities[:,None] if n['actor']==0 else probabilities[None,:])
                return out
            expected=np.column_stack([visit(c).sum(1)/matrix.bb_mass for c in context['nodes'][0]['children']])
            actual=parts.exact_terms(context,matrix,pre)
            np.testing.assert_allclose(actual,expected,rtol=0,atol=1e-12)
            if d==200:np.testing.assert_allclose(actual,old_parts.exact_terms(matrix,pre),rtol=0,atol=1e-12)

    def test_reject_wrong_topology_economics_and_missing_board_branches(self):
        context=self.contexts[200]
        for kind in ('cycle','menu','showdown'):
            bad=copy.deepcopy(context)
            if kind=='cycle':bad['nodes'][3]['children'][0]=0
            elif kind=='menu':bad['nodes'][0]['actions'][1]['kind']='raise'
            else:bad['nodes'][11]['invested'][0]+=1
            with self.assertRaises(ValueError,msg=kind):parts.routes(bad)
        with self.assertRaises(ValueError):parts.board_terms(context,dict(branches=[]),[],synthetic_pre(context),
            [np.ones(1),np.ones(1)],[np.array([0]),np.array([0])],1,np.full(169,1/169))
        bad=synthetic_pre(context);bad[3][0,0]=-1
        with self.assertRaises(ValueError):parts.path_reach(context,bad,[(3,0)])


def synthetic_pre(context):
    rng=np.random.default_rng(931)
    result={}
    for i,node in enumerate(context['nodes']):
        if node['children']:
            p=rng.random((169,len(node['children'])));p/=p.sum(1)[:,None];result[i]=p
    return result


if __name__=='__main__':unittest.main()
