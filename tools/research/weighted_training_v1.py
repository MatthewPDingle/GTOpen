"""Complete research update using one stratified draw per frozen generation."""
import copy
import json
from pathlib import Path
import subprocess
import time
import numpy as np
import sampled_visible_hybrid_checkpoint_v1 as storage
import weighted_training_checkpoint_v1 as checkpoint
from weighted_training_policy_v1 import probabilities
from weighted_training_fit_v1 import fit
from class_stratified_physical_deals_v1 import ClassStratifiedDeals
from weighted_deal_binding_v1 import DealWeightGeneration
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_preflop_table_v1 import build
from weighted_root_accumulator_v1 import WeightedRootRegrets
from weighted_later_action_ingest_v1 import ingest
from exact_btn_regret_accumulator_v1 import ExactBtnRegrets
from exact_initial_training_ingest_v2 import InitialTargets
from preflop_allin_matrix_v1 import AllinMatrix
from sampled_allin_protocol_v3 import policy_document
from sampled_physical_root_evaluation_v1 import sha, save
from later_action_training_v1 import first_action_view
from action_integrated_root_evaluation_v1 import evaluate as integrate_root


def initialize(objects,config,**args):
    checkpoint.require_config(config); source = args['context_source']
    root = WeightedRootRegrets(storage.digest(source),args['matrix_sha256'])
    exact = ExactBtnRegrets(storage.digest(source),args['entry_mass'])
    ref = checkpoint.write_model(objects,0,storage.uniform_networks(),[1.,1.],[None,None],root,exact,**args)
    return dict(completed_iterations=0,sampler=ClassStratifiedDeals(source,seed=config['sampler_seed']),
        action_rng=np.random.Generator(np.random.PCG64(config['action_seed'])),
        reservoirs=[WeightedPhysicalReservoir(config['reservoir_capacity'],p,config['reservoir_seeds'][p],source) for p in (0,1)],
        played_bank=[],next_model=ref,root_regret_state=root,exact_btn_state=exact)


def update(folder,objects,state,config,*,context_path,catalog_source,matrix_source,matrix_sha256,
           cache,executable,integration_executable,trace_executable,batch_prefix,guard):
    guard(); began = time.monotonic(); source = Path(context_path).read_text()
    matrix = AllinMatrix(json.loads(matrix_source),source)
    args = dict(context_source=source,catalog_source=catalog_source,matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass)
    model = checkpoint.validate_state(objects,state,config,**args)
    if cache.sha256 != config['allin_cache_sha256']: raise ValueError('Wrong all-in cache')
    generation = state['completed_iterations']; iteration = generation+1; used = state['next_model']
    response_hi = json.loads(source)['nodes'][0]['children'][3]+1
    catalog = json.loads(catalog_source)
    catalog_query = dict(context_source=source,observations=[r['observation'] for r in catalog['native_observations']])
    p,coverage = probabilities(catalog_query,model,device=config['device'],catalog_source=catalog_source,
        matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass)
    root = np.zeros((169,4)); calls = np.zeros(169)
    for item,row in zip(catalog['native_observations'],p):
        if item['player'] == 0: root[item['hand_class']] = row
        else: calls[item['hand_class']] = row[1]
    exact_values = matrix.evaluate(root,calls)
    targets = InitialTargets(matrix_source,source,root,calls,matrix_sha256=matrix_sha256,generation=generation)
    folder = Path(folder); folder.mkdir(parents=True,exist_ok=False)
    save(folder/'current-initial-policy.json',dict(used_model=used,root=root.tolist(),calls=calls.tolist(),target_identity=targets.identity,coverage=coverage))
    timings = dict(sampling=0.,native_queries=0.,inference=0.,native_updates=0.,native_trace=0.,ingestion=0.,root_integration=0.,fit=0.,publication=0.)
    before = time.monotonic(); sample = state['sampler'].sample(config['deals_per_generation'])
    weighted = DealWeightGeneration(sample,source); timings['sampling'] = time.monotonic()-before
    save(folder/'source-generation.json',sample)
    audits = []; bindings = []; subbatches = []; subsize = config['deals_per_subbatch']
    for chunk,start in enumerate(range(0,config['deals_per_generation'],subsize)):
        guard(); part = folder/f'batch-{chunk:02d}'; part.mkdir()
        batch = cache.batch(dict(format=2,batch_id=f'{batch_prefix}-iteration-{iteration}-batch-{chunk}',
            query_limit=config['query_limit'],seed=int(state['action_rng'].integers(0,2**63)),deals=sample['deals'][start:start+subsize]))
        paths = {n:part/f'{n}.json' for n in ('batch','queries','policies','updates','action-trace')}
        save(paths['batch'],batch)
        def invoke(exe, argv, category):
            guard(); t = time.monotonic()
            result = subprocess.run([str(exe),*map(str,argv)],timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
            timings[category] += time.monotonic()-t
            if result.returncode: raise RuntimeError(result.stderr[-2000:])
        invoke(executable,['queries',context_path,paths['batch'],'-',paths['queries']],'native_queries')
        queries = json.loads(paths['queries'].read_text()); before = time.monotonic()
        p,coverage = probabilities(first_action_view(queries,response_hi),model,device=config['device'],
            catalog_source=catalog_source,matrix_sha256=matrix_sha256,entry_mass=matrix.btn_mass)
        timings['inference'] += time.monotonic()-before
        policy = policy_document(queries,p); save(paths['policies'],policy)
        invoke(executable,['verify',context_path,paths['batch'],paths['policies'],paths['updates']],'native_updates')
        invoke(trace_executable,[context_path,paths['batch'],paths['policies'],paths['action-trace']],'native_trace')
        updates = json.loads(paths['updates'].read_text()); trace = json.loads(paths['action-trace'].read_text())
        before = time.monotonic()
        counts,audit,later,weight_audit = ingest(queries,updates,policy,state['reservoirs'],iteration,cache,targets,trace,
            generation=weighted,start=start,guard=guard)
        timings['ingestion'] += time.monotonic()-before
        for name,value in (('derived-targets',audit),('postflop-targets',later),('weighted-targets',weight_audit)):
            save(part/f'{name}.json',value)
        before = time.monotonic()
        audits.append(integrate_root(context_path,paths['batch'],queries,policy,audit,part,integration_executable,guard))
        timings['root_integration'] += time.monotonic()-before; bindings.append(weight_audit['binding'])
        subbatches.append(dict(chunk=chunk,counts=counts,coverage=coverage,artifacts={p.name:sha(p) for p in part.iterdir()}))
    networks = []; fits = []; before = time.monotonic()
    for player,reservoir in enumerate(state['reservoirs']):
        net,metric = fit(reservoir,seed=config['fit_seed_base']+iteration*200003+player,steps=config['fit_steps'],
            device=config['device'],chunk_size=config['chunk_size'],learning_rate=config['learning_rate'],guard=guard)
        networks.append(net); fits.append(metric)
    timings['fit'] = time.monotonic()-before; before = time.monotonic()
    exact = copy.deepcopy(state['exact_btn_state'])
    delta = exact.step(iteration,calls,exact_values['btn_jam_mass'],exact_values['btn_fold_entries'],exact_values['btn_call_entries'])
    root_state = copy.deepcopy(state['root_regret_state'])
    root_state.step(iteration,audits,generation=weighted,bindings=bindings,
        expected_deals=config['deals_per_generation'],expected_batches=len(audits))
    current = checkpoint.write_model(objects,iteration,networks,[m['advantage_scale'] for m in fits],
        [build(r,source) for r in state['reservoirs']],root_state,exact,**args)
    state.update(completed_iterations=iteration,next_model=current,exact_btn_state=exact,root_regret_state=root_state,
        played_bank=[*state['played_bank'],used])
    reference = checkpoint.save_checkpoint(objects,state,config,**args)
    timings['publication'] = time.monotonic()-before
    metric = dict(iteration=iteration,used_model=used,next_model=current,checkpoint=reference,
        timings=timings,seconds=time.monotonic()-began,fits=fits,subbatches=subbatches,
        root_samples=int(root_state.counts.sum()),root_covered_classes=int(np.count_nonzero(root_state.counts)),
        exact_btn_updates=exact.steps,exact_btn_delta=delta.tolist(),reservoirs=[r.summary() for r in state['reservoirs']])
    save(folder/'metrics.json',metric)
    return metric
