"""Full-context posterior64 workers; ordered insertion remains in the coordinator."""
import json
import os
from pathlib import Path
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import psutil
import numpy as np
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from river_weighted_overlay_ingest_v1 import ingest, METHOD
from stack_context_river_transport_v1 import generate
from stack_context_current_policy_v1 import CurrentPolicy
from exact_initial_training_ingest_v2 import digest
from sampled_physical_deals_v1 import PhysicalDeals
from storage_strategic_common_prior_20260920 import PAIRS
import hashlib
from action_integrated_root_evaluation_v1 import evaluate as integrate_root
from sampled_physical_root_evaluation_v1 import sha,save
from reboot_research_idle_v1 import idle

_STATE = None


class CollectedVisits(WeightedPhysicalReservoir):
    def __init__(self,player,source,events):
        super().__init__(1,player,0,source)
        self.events = events

    def _insert(self,row,iteration,*,deal_weight):
        # Validation remains in the original weighted ingester. No Algorithm R
        # draw is taken here; events are later committed in original visit order.
        self.events.append((self.player,row,iteration,deal_weight))
        self.seen += 1


def initialize(context_path,cache,targets,generation,iteration,executable,trace_executable,integration_executable,river_payload,river_executable,expected_native_identities):
    global _STATE
    os.environ['CUDA_VISIBLE_DEVICES']='-1'
    from threadpoolctl import threadpool_limits
    _STATE = dict(context_path=context_path,cache=cache,targets=targets,generation=generation,iteration=iteration,
        executable=executable,trace_executable=trace_executable,integration_executable=integration_executable,
        thread_limit=threadpool_limits(limits=1),last_guard=0.,began=time.monotonic())
    source=Path(context_path).read_text()
    if hashlib.sha256(river_payload['model_source'].encode()).hexdigest()!=river_payload['policy_id']:
        raise ValueError('River current model source identity changed')
    model=json.loads(river_payload['model_source'])
    if model['generation']+1!=iteration:
        raise ValueError('River model is not the current played generation')
    registry=river_payload['registry'];key=river_payload['context_sha256']
    if (registry.source(key)!=source or generation.context_source!=source
            or targets.context_source!=source or targets.generation+1!=iteration):
        raise ValueError('Worker model, generation or target context changed')
    engine=CurrentPolicy(model,registry,context_sha256=key,resources=river_payload['resources'])
    identities={str(p):sha(p) for p in (context_path,executable,trace_executable,integration_executable,river_executable)}
    if identities!=expected_native_identities:raise ValueError('Native worker source identities changed before initialization')
    args=river_payload['resources'][key]
    if targets.identity['matrix_sha256']!=args['matrix_sha256']:raise ValueError('Targets belong to a different exact matrix')
    catalog=json.loads(args['catalog_source'])['native_observations']
    p=engine.infer(engine.prepare(dict(context_source=source,observations=[r['observation'] for r in catalog])))
    for row,probability in zip(catalog,p):
        c=row['hand_class']
        expected=targets.root[c] if row['player']==0 else np.array([1-targets.calls[c],targets.calls[c],0.,0.])
        if np.max(abs(expected-probability))>1e-10:raise ValueError('Exact targets differ from the frozen current policy')
    _STATE.update(context_sha256=key,registry_sha256=registry.sha256,
                  identities=identities)
    weights=PhysicalDeals(source,mode='full_deck',seed=0).weights
    entry=[{tuple(map(int,p)):float(w) for p,w in zip(PAIRS,row)} for row in weights]
    _STATE.update(river_engine=engine,river_entry=entry,river_policy_id=river_payload['policy_id'],
                  river_executable=river_executable,river_executable_sha256=sha(river_executable))



def guard():
    now = time.monotonic()
    if now-_STATE['began'] > 1200: raise RuntimeError('Worker generation time limit reached')
    if now-_STATE['last_guard'] > 3:
        if psutil.virtual_memory().available < 20_000_000_000: raise RuntimeError('Worker memory headroom exhausted')
        if 'folder' in _STATE and psutil.disk_usage(_STATE['folder'].anchor).free<40_000_000_000:
            raise RuntimeError('Worker disk reserve')
        listening = any(c.status==psutil.CONN_LISTEN and c.laddr.port==56708 for c in psutil.net_connections(kind='tcp'))
        if listening and not idle(): raise RuntimeError('Production application became busy')
        _STATE['last_guard'] = now


def complete(part,start,expected_inputs):
    began=time.monotonic(); part=Path(part); s=_STATE;s['folder']=part;timings={};guard()
    for path,identity in s['identities'].items():
        if sha(path)!=identity:raise ValueError('Native target source changed')
    paths={n:part/f'{n}.json' for n in ('batch','queries','policies','updates','action-trace')}
    if expected_inputs!={n:sha(paths[n]) for n in ('batch','queries','policies')}:
        raise ValueError('Worker batch/query/policy identity changed')
    def invoke(exe,args,label):
        guard(); t=time.monotonic()
        result=subprocess.run([str(exe),*map(str,args)],timeout=120,capture_output=True,text=True,creationflags=subprocess.CREATE_NO_WINDOW)
        timings[label]=time.monotonic()-t
        if result.returncode:raise RuntimeError(result.stderr[-2000:])
    invoke(s['executable'],['verify',s['context_path'],paths['batch'],paths['policies'],paths['updates']],'native_updates')
    invoke(s['trace_executable'],[s['context_path'],paths['batch'],paths['policies'],paths['action-trace']],'native_trace')
    queries=json.loads(paths['queries'].read_text()); policy=json.loads(paths['policies'].read_text())
    updates=json.loads(paths['updates'].read_text()); trace=json.loads(paths['action-trace'].read_text())
    events=[]; receivers=[CollectedVisits(p,queries['context_source'],events) for p in (0,1)]
    t=time.monotonic()
    if sha(s['river_executable'])!=s['river_executable_sha256']:
        raise ValueError('River native executable changed')
    overlay,evidence=generate(queries,updates,policy,trace,generation=s['generation'],start=start,
        iteration=s['iteration'],policy_id=s['river_policy_id'],case_id=json.loads(paths['batch'].read_text())['batch_id'],
        engine=s['river_engine'],entry=s['river_entry'],executable=s['river_executable'],
        context_path=s['context_path'],folder=part/'conditional',guard=guard,write=save)
    timings['river_targets']=time.monotonic()-t;t=time.monotonic()
    counts,audit,later,weight_audit,river_audit=ingest(queries,updates,policy,receivers,s['iteration'],s['cache'],s['targets'],trace,
        generation=s['generation'],start=start,overlay=overlay,expected_policy_id=s['river_policy_id'],
        expected_evidence_sha256=digest(evidence),guard=guard)
    save(part/'river-targets.json',river_audit)
    timings['ingestion']=time.monotonic()-t
    for name,value in (('derived-targets',audit),('postflop-targets',later),('weighted-targets',weight_audit)):
        save(part/f'{name}.json',value)
    t=time.monotonic()
    integrated=integrate_root(s['context_path'],paths['batch'],queries,policy,audit,part,s['integration_executable'],guard)
    timings['root_integration']=time.monotonic()-t
    return dict(start=start,counts=counts,events=events,integrated=integrated,binding=weight_audit['binding'],
        input_identities=expected_inputs,
        context_sha256=s['context_sha256'],registry_sha256=s['registry_sha256'],model_sha256=s['river_policy_id'],
        native_identities=s['identities'],cuda_visible_devices=os.environ.get('CUDA_VISIBLE_DEVICES'),
        artifacts={str(p.relative_to(part)):sha(p) for p in part.rglob('*') if p.is_file()},
        river=dict(method=METHOD,K=64,replacements=len(overlay['rows']),evidence_sha256=digest(evidence)),
        timings=timings,seconds=time.monotonic()-began,
        pid=os.getpid(),rss_bytes=psutil.Process().memory_info().rss)


def pool(workers,**args):
    if type(workers) is not int or not 1<=workers<=4:raise ValueError('One to four admitted workers required')
    return ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=tuple(args[k] for k in ('context_path','cache','targets','generation','iteration',
            'executable','trace_executable','integration_executable','river_payload','river_executable','expected_native_identities')))


def commit(result,reservoirs,*,expected_start,iteration,expected_context_sha256,expected_model_sha256,expected_registry_sha256):
    if (result['context_sha256']!=expected_context_sha256 or result['model_sha256']!=expected_model_sha256
            or result['registry_sha256']!=expected_registry_sha256
            or any(r.context_sha256!=expected_context_sha256 or r.player!=p for p,r in enumerate(reservoirs))):
        raise ValueError('Worker result belongs to another game or frozen model')
    if result['start']!=expected_start:raise ValueError('Out-of-order worker commit')
    added=[0,0]
    for player,row,it,weight in result['events']:
        if player not in (0,1) or it!=iteration:raise ValueError('Invalid worker event identity')
        added[player]+=1
    if added!=result['counts'] or any(r.seen+n>=2**63 for r,n in zip(reservoirs,added)):
        raise ValueError('Worker event count mismatch or overflow')
    for player,row,it,weight in result['events']:
        reservoirs[player]._insert(row,it,deal_weight=weight)
