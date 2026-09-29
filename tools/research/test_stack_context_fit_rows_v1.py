"""Native-input and direct-visit objective checks; targets are synthetic."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import copy
import json
from pathlib import Path
import unittest
import numpy as np
from stack_context_inputs_v1 import Registry,digest
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from stack_context_fit_rows_v1 import encode_rows,prepare

GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
QUERIES=Path('S:/GTOpen-research/stack-context-model-control-v1')
DEPTHS=(20,40,60,100,150,200,400)


class FitRowsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries=[];cls.queries={};cls.sources={};cls.depth={}
        for d in DEPTHS:
            source=(GEOMETRY/'fixtures'/f'stack-{d}-context.json').read_text()
            key=digest(source);cls.sources[key]=source;cls.depth[key]=d
            cls.entries.append(dict(name=f'{d}bb',split='heldout' if d in (60,150) else 'fit',
                context_source=source,public_document=json.loads((GEOMETRY/f'stack-{d}-public.json').read_bytes())))
            cls.queries[key]=json.loads((QUERIES/f'stack-{d}-queries.json').read_bytes())
        cls.registries=[Registry(cls.entries),RelativeRegistry(cls.entries)]
        cls.reservoirs=[]
        for actor in (0,1):
            stores={}
            for key in cls.registries[0].fit_contexts:
                rows=[o for o in cls.queries[key]['observations'] if o['actor']==actor]
                r=WeightedPhysicalReservoir(len(rows)+3,actor,7,cls.sources[key])
                for i,o in enumerate([*rows,*rows[:3]]):
                    y=np.zeros(4);y[:o['n']]=cls.depth[key]*.01*np.sin(np.arange(o['n'])+i*.3)
                    r.add(o,y,1,deal_weight=.25+(i%5))
                stores[key]=r
            cls.reservoirs.append(stores)

    def weights(self,registry):
        return {k:1/len(registry.fit_contexts) for k in registry.fit_contexts}

    def test_fit_features_equal_real_native_encoder_on_all_streets(self):
        for registry in self.registries:
            for stores in self.reservoirs:
                for key,r in stores.items():
                    q=self.queries[key];native=registry.prepare(q,context_sha256=key,purpose='fit')
                    mapping={k:x for k,x in zip(native['keys'],native['features'])}
                    x,keys=encode_rows(registry,r,np.arange(r.size))
                    np.testing.assert_array_equal(x,np.stack([mapping[k] for k in keys]))
                    self.assertEqual({o['phase'] for o in q['observations']},{0,1,2,3})

    def test_grouped_loss_matches_independent_weighted_visit_sum(self):
        for registry in self.registries:
            for actor,stores in enumerate(self.reservoirs):
                weights=self.weights(registry);g=prepare(registry,stores,player=actor,context_weights=weights)
                predictions=np.asarray([[(int(lo)%11)/37*(a+1) for a in range(4)] for _,_,lo in g['keys']])
                observed=float(np.sum((predictions-g['targets'])**2*g['weights']))+g['within_observation_variance']
                expected=0.
                for key,r in stores.items():
                    prediction=np.asarray([[(int(lo)%11)/37*(a+1) for a in range(4)] for _,lo in r.keys[:r.size]])
                    y=r.values[:r.size]/self.depth[key]
                    legal=np.arange(4)[None,:]<r.arity[:r.size,None]
                    w=r.deal_weights[:r.size,None]*legal
                    expected+=weights[key]*float(np.sum(w*(prediction-y)**2)/np.sum(w))
                self.assertAlmostEqual(observed,expected,places=12)
                self.assertFalse(g['own_history_available'])
                self.assertEqual(g['target_units'],'advantage_bb / context_starting_stack')
                self.assertEqual(len(g['keys']),len(set(g['keys'])))
                # Identical numeric observation keys across games stay separate.
                self.assertLess(len({(hi,lo) for _,hi,lo in g['keys']}),len(g['keys']))

    def test_repeating_a_context_does_not_change_its_mixture_weight(self):
        registry=self.registries[1];stores=self.reservoirs[0];weights=self.weights(registry)
        before=prepare(registry,stores,player=0,context_weights=weights)
        key=registry.fit_contexts[0];source=stores[key];r=WeightedPhysicalReservoir(source.size*2,0,2,self.sources[key])
        by_key={(int(o['hi']),int(o['lo'])):o for o in self.queries[key]['observations']}
        for _ in range(2):
            for i in range(source.size):
                r.add(by_key[tuple(map(int,source.keys[i]))],source.values[i],1,deal_weight=source.deal_weights[i])
        after=prepare(registry,dict(stores,**{key:r}),player=0,context_weights=weights)
        self.assertEqual(before['keys'],after['keys'])
        for name in ('features','targets','weights'):
            np.testing.assert_allclose(before[name],after[name],rtol=0,atol=1e-13)
        self.assertAlmostEqual(before['within_observation_variance'],after['within_observation_variance'],places=13)

    def test_reject_wrong_context_actor_keys_menu_and_illegal_targets(self):
        registry=self.registries[1];stores=self.reservoirs[0];weights=self.weights(registry)
        key=registry.fit_contexts[0]
        with self.assertRaises(ValueError):prepare(registry,{},player=0,context_weights=weights)
        with self.assertRaises(ValueError):prepare(registry,stores,player=1,context_weights=weights)
        with self.assertRaises(ValueError):prepare(registry,stores,player=0,context_weights=dict(weights,**{key:float('nan')}))
        for kind in ('keys','menu','illegal_target'):
            changed=copy.deepcopy(stores);r=changed[key]
            if kind=='keys':r.keys[0,1]+=np.uint64(1)
            elif kind=='menu':r.arity[0]=3 if r.arity[0]!=3 else 2
            else:
                i=next(i for i in range(r.size) if r.arity[i]<4);r.values[i,int(r.arity[i])]=1.
            with self.assertRaises(ValueError,msg=kind):prepare(registry,changed,player=0,context_weights=weights)

    def test_heldout_reservoir_cannot_enter_encoding_or_fitting(self):
        registry=self.registries[1]
        for key,depth in self.depth.items():
            if depth not in (60,150):continue
            r=WeightedPhysicalReservoir(1,0,0,self.sources[key]);o=next(o for o in self.queries[key]['observations'] if o['actor']==0)
            r.add(o,[0.,0.,0.,0.],1,deal_weight=1.)
            with self.assertRaises(ValueError):encode_rows(registry,r,[0])
            with self.assertRaises(ValueError):prepare(registry,dict(self.reservoirs[0],**{key:r}),player=0,context_weights=self.weights(registry))


if __name__=='__main__':unittest.main()
