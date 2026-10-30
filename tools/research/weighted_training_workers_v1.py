"""Bounded CPU workers; real reservoir insertion remains in the coordinator."""
import json
import os
from pathlib import Path
import subprocess
import time
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import psutil
from weighted_physical_reservoir_v1 import WeightedPhysicalReservoir
from weighted_later_action_ingest_v1 import ingest
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


def initialize(context_path,cache,targets,generation,iteration,executable,trace_executable,integration_executable):
    global _STATE
    from threadpoolctl import threadpool_limits
    _STATE = dict(context_path=context_path,cache=cache,targets=targets,generation=generation,iteration=iteration,
        executable=executable,trace_executable=trace_executable,integration_executable=integration_executable,
        thread_limit=threadpool_limits(limits=1),last_guard=0.,began=time.monotonic())


def guard():
    now = time.monotonic()
    if now-_STATE['began'] > 1200: raise RuntimeError('Worker generation time limit reached')
    if now-_STATE['last_guard'] > 3:
        if psutil.virtual_memory().available < 20_000_000_000: raise RuntimeError('Worker memory headroom exhausted')
        listening = any(c.status==psutil.CONN_LISTEN and c.laddr.port==56708 for c in psutil.net_connections(kind='tcp'))
        if listening and not idle(): raise RuntimeError('Production application became busy')
        _STATE['last_guard'] = now


def complete(part,start):
    guard(); began=time.monotonic(); part=Path(part); s=_STATE; timings={}
    paths={n:part/f'{n}.json' for n in ('batch','queries','policies','updates','action-trace')}
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
    counts,audit,later,weight_audit=ingest(queries,updates,policy,receivers,s['iteration'],s['cache'],s['targets'],trace,
        generation=s['generation'],start=start,guard=guard)
    timings['ingestion']=time.monotonic()-t
    for name,value in (('derived-targets',audit),('postflop-targets',later),('weighted-targets',weight_audit)):
        save(part/f'{name}.json',value)
    t=time.monotonic()
    integrated=integrate_root(s['context_path'],paths['batch'],queries,policy,audit,part,s['integration_executable'],guard)
    timings['root_integration']=time.monotonic()-t
    return dict(start=start,counts=counts,events=events,integrated=integrated,binding=weight_audit['binding'],
        artifacts={p.name:sha(p) for p in part.iterdir()},timings=timings,seconds=time.monotonic()-began,
        pid=os.getpid(),rss_bytes=psutil.Process().memory_info().rss)


def pool(workers,**args):
    if type(workers) is not int or not 1<=workers<=4:raise ValueError('One to four admitted workers required')
    return ProcessPoolExecutor(max_workers=workers,mp_context=multiprocessing.get_context('spawn'),
        initializer=initialize,initargs=tuple(args[k] for k in ('context_path','cache','targets','generation','iteration',
            'executable','trace_executable','integration_executable')))


def commit(result,reservoirs,*,expected_start,iteration):
    if result['start']!=expected_start:raise ValueError('Out-of-order worker commit')
    added=[0,0]
    for player,row,it,weight in result['events']:
        if player not in (0,1) or it!=iteration:raise ValueError('Invalid worker event identity')
        added[player]+=1
    if added!=result['counts'] or any(r.seen+n>=2**63 for r,n in zip(reservoirs,added)):
        raise ValueError('Worker event count mismatch or overflow')
    for player,row,it,weight in result['events']:
        reservoirs[player]._insert(row,it,deal_weight=weight)
