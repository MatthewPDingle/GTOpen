"""Synthetic fixtures only: real geometry/entry law, invented payoffs/targets.

Never exports native trees, starts scientific work or imports old control scripts.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

TOOLS = Path(r'T:\Dev\GTOpen\tools\research')
POP = Path(r'S:\GTOpen-research\stack-context-population-v1')
sys.path.append(str(TOOLS))
import preflop_expected_training_checkpoint_v1 as cp
import preflop_expected_training_fit_v1 as fit
from preflop_expected_native_targets_v1 import physical_class_mass, text_sha, canonical_card_keys
from preflop_expected_native_targets_v2 import FrozenExpectedTargets
from stack_context_preflop_expected_components_v2 import PreflopExpectedComponents
from sampled_physical_deals_v1 import PhysicalDeals
from stack_context_inputs_v1 import Registry
from stack_context_relative_inputs_v1 import Registry as RelativeRegistry
import sampled_visible_hybrid_checkpoint_v1 as storage
from board_root_accumulator_v1 import digest

INPUTS = {}

def read(path):
    path = Path(path).resolve(); raw = path.read_bytes()
    INPUTS[str(path)] = hashlib.sha256(raw).hexdigest()
    return raw.decode('utf-8')

def matrix(source):
    c = json.loads(source); sampler = PhysicalDeals(source, mode='full_deck', seed=0)
    raw, total = physical_class_mass(sampler.weights); mass = raw/total
    root = c['nodes'][0]; jam = c['nodes'][root['children'][3]]
    folded, called = [c['nodes'][i] for i in jam['children']]
    net = called['pot']-min(called['pot']*c['rake_fraction'], c['rake_cap'])
    rank = np.arange(169); eq = np.where(rank[:, None] > rank[None, :], .7,
                                       np.where(rank[:, None] < rank[None, :], .3, .5))
    value = dict(format=1, context_sha256=text_sha(source), class_mass=mass.tolist(),
        bb_showdown_entries=(mass*(-called['invested'][0]+net*eq)).tolist(),
        btn_showdown_entries=(mass*(-called['invested'][1]+net*(1-eq))).tolist(),
        bb_fold=c['nodes'][root['children'][0]]['leaf']['utilities'][0],
        bb_uncontested=folded['leaf']['utilities'][0], btn_fold=folded['leaf']['utilities'][1],
        conserved_showdown_total=net-sum(called['invested']), canonical_population_rows=0,
        scope='Invented class strengths with original compatible prior; software controls only')
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)

def fixture(width, *, directory, cycles=3, fit_steps=4):
    entries = []; resources = {}
    for depth, split in ((20,'fit'), (40,'fit'), (100,'fit'), (200,'fit'), (400,'fit'), (60,'heldout'), (150,'heldout')):
        folder = POP/f'stack-{depth}'; source = read(folder/'context.json'); key = text_sha(source)
        entries.append(dict(name=f'{depth}bb', split=split, context_source=source,
                            public_document=json.loads(read(folder/'public.json'))))
        if split != 'fit': continue
        physical = read(folder/'physical-catalog.json'); ms = matrix(source)
        from preflop_expected_regret_accumulator_v1 import PreflopExpectedRegrets
        s = PreflopExpectedRegrets(context_source=source, matrix_source=ms,
            generation_scale=169, boards_per_generation=2, board_seed=depth+318)
        resources[key] = dict(physical_catalog_source=physical, physical_catalog_sha256=text_sha(physical),
                              matrix_source=ms, expected_config=s.config)
    registry = (Registry if width == 362 else RelativeRegistry)(entries)
    locals = {}
    for i,key in enumerate(registry.fit_contexts):
        locals[key] = dict(sampler_seed=600+i, action_seed=900+i, reservoir_seeds=[1100+i,1400+i],
            reservoir_capacity=7, deals_per_generation=169, deals_per_subbatch=13, query_limit=10000,
            expected_preflop=resources[key]['expected_config'], allin_cache_sha256='d'*64,
            river_targets=dict(method=cp.RIVER_METHOD,K=64))
    config = dict(format=1, checkpoint_type=cp.TYPE, execution_mode='software-control',
        registry_sha256=registry.sha256, representation=registry.manifest['representation'],
        target_units=cp.SCALE, fit_runtime=cp.RUNTIME, objective_method=cp.FIT_METHOD,
        preflop_fit_recipe=cp.DENSE_RECIPE, preflop_fraction=.25, initialization=cp.INITIALIZATION,
        optimizer=cp.OPTIMIZER, device='cuda', current_policy_inference='float64-widened-float32-weights-v1',
        fit_steps=fit_steps, chunk_size=512, learning_rate=.001, fit_seed_base=3701,
        context_order=list(registry.fit_contexts), context_weights={k:.2 for k in registry.fit_contexts},
        contexts=locals, source_identities={str(Path(cp.__file__).resolve()):hashlib.sha256(Path(cp.__file__).read_bytes()).hexdigest(),
            str(Path(fit.__file__).resolve()):hashlib.sha256(Path(fit.__file__).read_bytes()).hexdigest()})
    initial = cp.initialize(directory, config, registry, resources)
    return registry, resources, config, initial

def observation(public, actor, hand, board):
    phase = public['phase']; hi = public['hi']
    lo = int(canonical_card_keys(np.asarray([hand]),board,actor,phase)[0])
    cards = [(lo >> (6*i)) & 63 for i in range(7)]; active = []
    for i,c in enumerate(cards): active.extend((19*i+(13 if c == 63 else c//4),19*i+14+(4 if c == 63 else c%4)))
    h = (int(hi)&((1<<63)-1)) >> 4; history=[]
    while h > 1: history.append(h&7); h >>= 3
    history.reverse()
    active.extend((133+actor,135+phase,139+(int(hi)&15)))
    active.extend(155+6*i+(history[i] if i<len(history) else 0) for i in range(19))
    return dict(hi=hi,lo=str(lo),actor=actor,phase=phase,n=len(public['actions']),active_features=active)

def stage(directory, previous, registry, resources):
    local = copy.deepcopy(previous['contexts']); targets = {}; generation=previous['completed_cycles']+1
    source = storage.read_object(directory,previous['next_model']).decode()
    for key,s in local.items():
        s['sampler'].sample(169); s['action_rng'].integers(0,100000,size=23)
        provider = FrozenExpectedTargets(state=previous['contexts'][key]['preflop_state'],
            model_source=source, registry=registry, resources=resources)
        p = provider.played_preflop(); state = s['preflop_state']; plan=state.plan()
        exact = PreflopExpectedComponents(state.context,state.matrix,p).exact(); draws=[]
        for j,board in enumerate(plan['boards']):
            values={}
            for node in state.nodes:
                x = np.zeros_like(p[node]); reach=exact[node]['opponent_history_probability']
                for a in np.flatnonzero(state.post_slots[node]):
                    x[:,a]=reach*state.context['config']['stack']*(.011*(j+generation)+((np.arange(169)+node+a)%9)/500)
                x[~exact[node]['counterfactual_supported']]=0; values[str(node)]=x.tolist()
            draws.append(dict(draw_index=j,board=board,model_sha256=previous['next_model']['sha256'],
                tree_sha256='a'*64,policy_recipe_sha256=digest(provider.recipe),values=values,values_sha256=digest(values)))
        evidence=provider.generation_evidence(previous['contexts'][key]['preflop_state'],plan,draws)
        state.step(plan,evidence,played_policy=p)
        targets[key]=dict(plan=plan,evidence=evidence,recipe=provider.recipe)
        for actor in (0,1):
            public=[v[0] for v in registry._get(key)['lookup'].values() if v[0]['actor']==actor and v[0]['phase']>0]
            by_phase={phase:next(v for v in public if v['phase']==phase) for phase in (1,2,3)}
            for visit in range(19):
                row=observation(by_phase[visit%3+1],actor,[0,5],[8,12,16,20,24]); arity=row['n']
                y=np.zeros(4); y[:arity]=np.arange(arity)*(.3+visit*.01)+generation*.017
                y[:arity]-=y[:arity].mean()
                y*=float(state.context['config']['stack'])
                s['reservoirs'][actor].add(row,y,generation,deal_weight=.5+(visit%5)/3)
    return dict(contexts=local,collected_against={k:previous['next_model']['sha256'] for k in registry.fit_contexts},board_targets=targets)

def receipts(staged, previous, registry, resources, config, networks):
    generation=previous['completed_cycles']+1; result=[]
    for actor,net in enumerate(networks):
        objective=fit.prepare(registry,staged['contexts'],resources,player=actor,
            context_weights=config['context_weights'],preflop_fraction=config['preflop_fraction'])
        result.append(dict(execution_mode=config['execution_mode'],player=actor,generation=generation,
            collected_against=previous['next_model']['sha256'],registry_sha256=registry.sha256,
            local_fit_identities={k:cp.local_fit_identity(staged['contexts'][k]) for k in registry.fit_contexts},
            network_sha256=cp.hash_document(net),objective_method=cp.FIT_METHOD,fit_runtime=cp.RUNTIME,
            target_units=cp.SCALE,preflop_fit_recipe=cp.DENSE_RECIPE,preflop_fraction=config['preflop_fraction'],
            context_weights=config['context_weights'],seed=config['fit_seed_base']+generation*200003+actor,
            steps=config['fit_steps'],learning_rate=config['learning_rate'],chunk_size=config['chunk_size'],
            initialization=cp.INITIALIZATION,optimizer=cp.OPTIMIZER,device='cuda',objective_sha256=objective['objective_sha256']))
    return result

def same_local(a,b):
    for key,x in a.items():
        y=b[key]
        assert x['sampler'].checkpoint()==y['sampler'].checkpoint()
        assert x['action_rng'].bit_generator.state==y['action_rng'].bit_generator.state
        assert x['preflop_state'].document()==y['preflop_state'].document()
        for r,t in zip(x['reservoirs'],y['reservoirs']):
            assert r.seen==t.seen and r.rng.bit_generator.state==t.rng.bit_generator.state
            for name in cp.ARRAYS: assert np.array_equal(getattr(r,name),getattr(t,name))

def inputs():
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).suffix=='.py' and (Path(path).is_relative_to(TOOLS.parents[1]) or Path(path).parent==Path(__file__).parent):
            INPUTS[str(Path(path).resolve())]=hashlib.sha256(Path(path).read_bytes()).hexdigest()
    return copy.deepcopy(INPUTS)
