"""Joint save/restart tests with native contexts and explicitly synthetic updates."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',MKL_NUM_THREADS='1')
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
import numpy as np
import stack_context_training_checkpoint_v1 as cp
import stack_context_full_policy_v1 as full
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
from weighted_physical_reservoir_v1 import ARRAYS
from river_weighted_overlay_ingest_v1 import METHOD as RIVER
from board_root_accumulator_v1 import BoardRootRegrets
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets

STORE=Path('S:/GTOpen-research/stack-context-full-control-v1')
GEOMETRY=Path('S:/GTOpen-research/stack-geometry-control-v1')
OUT=Path('T:/Dev/GTOpen/research/preflop-evolution/blind-defense-20260922')


class JointCheckpointTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        proof=json.loads((OUT/'stack-context-full-control-v1-result.json').read_bytes())
        cls.fixtures=[]
        entries=[]
        for depth in (20,40,60,100,150,200,400):
            source=(GEOMETRY/'fixtures'/f'stack-{depth}-context.json').read_text()
            entries.append(dict(name=f'{depth}bb',split='heldout' if depth in (60,150) else 'fit',context_source=source,
                                public_document=json.loads((GEOMETRY/f'stack-{depth}-public.json').read_bytes())))
        for width,registry in ((362,Registry(entries)),(387,RelativeRegistry(entries))):
            path=STORE/f'{width}-fixture.json';raw=path.read_bytes()
            assert hashlib.sha256(raw).hexdigest()==proof['artifacts'][str(path)]
            fixture=json.loads(raw);assert registry.manifest==fixture['registry']
            resources=fixture['resources'];contexts={}
            for i,key in enumerate(registry.fit_contexts):
                contexts[key]=dict(sampler_seed=9300300+i,action_seed=9300400+i,reservoir_seeds=[0,0],reservoir_capacity=2,
                    deals_per_generation=169,deals_per_subbatch=169,query_limit=100000,
                    board_root=resources[key]['root_config'],allin_cache_sha256='a'*64,river_targets=dict(method=RIVER,K=64))
            config=dict(format=1,checkpoint_type=cp.TYPE,registry_sha256=registry.sha256,representation=registry.manifest['representation'],
                target_units=cp.SCALE,fit_runtime=cp.RUNTIME,objective_method=cp.METHOD,initialization=cp.INITIALIZATION,
                optimizer=cp.OPTIMIZER,device='cuda',current_policy_inference='float64-widened-float32-weights-v1',
                fit_steps=256,chunk_size=128,learning_rate=.003,fit_seed_base=9300201,
                context_order=list(registry.fit_contexts),context_weights={k:.2 for k in registry.fit_contexts},contexts=contexts,
                source_identities={str(path):proof['artifacts'][str(path)]})
            cls.fixtures.append((registry,resources,config,fixture['model']))

    def assert_states(self,a,b):
        self.assertEqual(a['completed_cycles'],b['completed_cycles'])
        self.assertEqual(a['played_bank'],b['played_bank']);self.assertEqual(a['next_model'],b['next_model'])
        self.assertEqual(set(a['contexts']),set(b['contexts']))
        for key,first in a['contexts'].items():
            second=b['contexts'][key]
            self.assertEqual(first['sampler'].checkpoint(),second['sampler'].checkpoint())
            self.assertEqual(first['action_rng'].bit_generator.state,second['action_rng'].bit_generator.state)
            for name in ('root_regret_state','exact_btn_state'):
                self.assertEqual(first[name].document(),second[name].document())
            for left,right in zip(first['reservoirs'],second['reservoirs']):
                self.assertEqual(left.summary(),right.summary());self.assertEqual(left.rng.bit_generator.state,right.rng.bit_generator.state)
                for name in ARRAYS:np.testing.assert_array_equal(getattr(left,name),getattr(right,name))

    def staged(self,state,registry,resources,fixture):
        local=copy.deepcopy(state['contexts'])
        for key,s in local.items():
            s['sampler'].sample(169);s['action_rng'].integers(0,2**63)
            catalog=json.loads(resources[key]['catalog_source'])
            for actor,r in enumerate(s['reservoirs']):
                observation=next(o['observation'] for o in catalog['native_observations'] if o['player']==actor)
                r.add(observation,[1.,0.,0.,0.],1,deal_weight=1.)
            saved=fixture['local_states'][key]
            s['root_regret_state']=BoardRootRegrets.restore(saved['board_root_state'],expected_config=resources[key]['root_config'])
            s['exact_btn_state']=ExactBtnRegrets.restore(saved['exact_btn_state'],context_sha256=key,entry_mass=resources[key]['entry_mass'])
        return dict(contexts=local,collected_against={k:state['next_model']['sha256'] for k in registry.fit_contexts})

    def test_initial_and_completed_roundtrip_preserve_all_rng_streams(self):
        for registry,resources,config,fixture in self.fixtures:
            with tempfile.TemporaryDirectory(prefix='gtopen-joint-context-test-') as folder:
                initial=cp.initialize(folder,config,registry,resources)
                initial_ref=cp.save_checkpoint(folder,initial,config,registry,resources)
                restored_initial=cp.restore_checkpoint(folder,initial_ref,config,registry,resources)
                self.assert_states(initial,restored_initial)
                staged=self.staged(initial,registry,resources,fixture)
                complete,ref=cp.complete_cycle(folder,initial,staged,config,registry,resources,networks=fixture['shared']['networks'])
                self.assert_states(initial,restored_initial)
                loaded=cp.restore_checkpoint(folder,ref,config,registry,resources)
                self.assert_states(complete,loaded)
                self.assertEqual(complete['played_bank'],[initial['next_model']])
                self.assertNotIn(complete['next_model'],complete['played_bank'])
                # Sample and insert beyond capacity to exercise all RNG streams.
                for key in registry.fit_contexts:
                    a,b=complete['contexts'][key],loaded['contexts'][key]
                    self.assertEqual(a['sampler'].sample(169),b['sampler'].sample(169))
                    np.testing.assert_array_equal(a['action_rng'].integers(1000,size=17),b['action_rng'].integers(1000,size=17))
                    catalog=json.loads(resources[key]['catalog_source'])
                    for actor in (0,1):
                        obs=next(o['observation'] for o in catalog['native_observations'] if o['player']==actor)
                        for visit in range(20):
                            for s in (a,b):s['reservoirs'][actor].add(obs,[float(visit),0.,0.,0.],2,deal_weight=1.+visit/20)
                self.assert_states(complete,loaded)

    def test_interruption_before_publication_leaves_original_checkpoint_usable(self):
        registry,resources,config,fixture=self.fixtures[1]
        for stop in ('before-model-publication','before-checkpoint-publication'):
            with tempfile.TemporaryDirectory(prefix='gtopen-joint-context-interrupt-') as folder:
                original=cp.initialize(folder,config,registry,resources)
                ref=cp.save_checkpoint(folder,original,config,registry,resources)
                before=copy.deepcopy(original);staged=self.staged(original,registry,resources,fixture)
                def interrupt(stage):
                    if stage==stop:raise InterruptedError(stop)
                with self.assertRaises(InterruptedError):
                    cp.complete_cycle(folder,original,staged,config,registry,resources,networks=fixture['shared']['networks'],on_stage=interrupt)
                self.assert_states(original,before)
                self.assertEqual(len(list(Path(folder).glob('jointcontextcheckpoint-*.json'))),1)
                resumed=cp.restore_checkpoint(folder,ref,config,registry,resources)
                self.assert_states(original,resumed)
                a,ra=cp.complete_cycle(folder,original,staged,config,registry,resources,networks=fixture['shared']['networks'])
                b,rb=cp.complete_cycle(folder,resumed,self.staged(resumed,registry,resources,fixture),config,registry,resources,
                                       networks=fixture['shared']['networks'])
                self.assert_states(a,b);self.assertEqual(ra,rb)

    def test_incomplete_or_mixed_model_cycle_is_rejected(self):
        registry,resources,config,fixture=self.fixtures[0]
        with tempfile.TemporaryDirectory(prefix='gtopen-joint-context-invalid-') as folder:
            original=cp.initialize(folder,config,registry,resources)
            staged=self.staged(original,registry,resources,fixture);key=registry.fit_contexts[0]
            for error in ('missing','wrong_model','stale_sampler','swapped_state'):
                changed=copy.deepcopy(staged)
                if error=='missing':del changed['contexts'][key]
                elif error=='wrong_model':changed['collected_against'][key]='0'*64
                elif error=='stale_sampler':changed['contexts'][key]['sampler']=copy.deepcopy(original['contexts'][key]['sampler'])
                else:changed['contexts'][key]=copy.deepcopy(changed['contexts'][registry.fit_contexts[1]])
                with self.assertRaises(ValueError,msg=error):
                    cp.complete_cycle(folder,original,changed,config,registry,resources,networks=fixture['shared']['networks'])
            self.assertEqual(len(list(Path(folder).glob('jointcontextcheckpoint-*.json'))),0)

    def test_configuration_and_played_bank_tampering_rejected(self):
        registry,resources,config,fixture=self.fixtures[1]
        with tempfile.TemporaryDirectory(prefix='gtopen-joint-context-identity-') as folder:
            original=cp.initialize(folder,config,registry,resources)
            complete,ref=cp.complete_cycle(folder,original,self.staged(original,registry,resources,fixture),config,registry,resources,
                                           networks=fixture['shared']['networks'])
            for field in ('learning_rate','source_identities','context_weights'):
                changed=copy.deepcopy(config)
                if field=='learning_rate':changed[field]=.004
                elif field=='source_identities':changed[field]={'modified':'b'*64}
                else:
                    keys=registry.fit_contexts;changed[field]={k:(.1 if k==keys[0] else .225) for k in keys}
                with self.assertRaises(ValueError):cp.restore_checkpoint(folder,ref,changed,registry,resources)
            bad=copy.deepcopy(complete);bad['played_bank']=[complete['next_model']]
            with self.assertRaises(ValueError):cp.save_checkpoint(folder,bad,config,registry,resources)
            heldout=next(r['context_sha256'] for r in registry.manifest['contexts'] if r['split']=='heldout')
            bad=copy.deepcopy(complete);bad['contexts'][heldout]=copy.deepcopy(next(iter(bad['contexts'].values())))
            with self.assertRaises(ValueError):cp.save_checkpoint(folder,bad,config,registry,resources)


if __name__=='__main__':unittest.main()
