"""Frozen-policy pilot support; no new fitting or production changes."""
import os
import gc
import json
from pathlib import Path
import time
import numpy as np
import psutil
from board_later_fit_holdout_run_v1 import ROOT,OUT,LOCK,OTHER,read,sha,verify,gpu_snapshot
from bounded_parallel_evaluation_archive_v2 import production_available
from board_completed_bank_v1 import load_bank
from board_river_bounds_bank_v1 import make_layout,prepare_queries,CudaBank
from preflop_allin_matrix_v1 import AllinMatrix

PREFIX='weighted-complete-river-bounds-pilot-v1'
STORE=Path('S:/GTOpen-research')/PREFIX
CONTROL_STORE=Path('S:/GTOpen-research/weighted-complete-river-bounds-pilot-control-v1')
CONTEXT=OUT/'bb-context-candidate.json'
LIMIT_BYTES=2_000_000_000
SEED=9289901
DEALS=4096


class Guard:
    def __init__(self,*,limit=7200):
        self.started=time.monotonic();self.last=0.;self.last_gpu=0.;self.last_storage=0.
        self.limit=limit;self.probes=[];self.roots=[]
    def __call__(self):
        now=time.monotonic();assert now-self.started<self.limit,'Invocation time limit; resume committed prefix'
        if now-self.last<2:return
        assert production_available() and not OTHER.exists()
        assert psutil.virtual_memory().available>24_000_000_000
        assert psutil.disk_usage('S:/').free>5_000_000_000 and psutil.disk_usage('T:/').free>1_000_000_000
        import torch
        if torch.cuda.is_initialized():
            assert torch.cuda.memory_allocated()<8_000_000_000 and torch.cuda.memory_reserved()<8_000_000_000
        self.last=now
        if now-self.last_storage>20:
            size=0
            for root in self.roots:
                assert root in (STORE,CONTROL_STORE)
                if not root.exists():continue
                for p in root.rglob('*'):
                    try:
                        if p.is_file():size+=p.stat().st_size
                    except FileNotFoundError:
                        assert '.batch-work' in p.relative_to(root).parts
            assert size<LIMIT_BYTES,'Pilot evidence budget reached; preserve files'
            self.last_storage=now
        if now-self.last_gpu>30:self.desktop_probe()
    def desktop_probe(self):
        import torch
        if torch.cuda.is_initialized():torch.cuda.synchronize()
        time.sleep(1.2)
        while True:
            assert time.monotonic()-self.started<self.limit and production_available() and not OTHER.exists()
            value=gpu_snapshot();self.probes.append(dict(elapsed=time.monotonic()-self.started,**value))
            if value['utilization_percent']<65 and value['free_bytes']>10_000_000_000:break
            print(json.dumps(dict(state='yielding_to_other_gpu_work',**value)),flush=True);time.sleep(5)
        self.last_gpu=time.monotonic()


def inputs():
    rp=OUT/'board-river-bounds-bank-v1-registration.json';pp=OUT/'board-river-bounds-bank-v1-result.json'
    ap=OUT/'board-river-bounds-bank-v1-analysis.json';result=read(pp);analysis=read(ap)
    assert result['passed'] and result['complete'] and result['registration_sha256']==sha(rp)
    assert analysis['qualifies_for_separate_policy_evaluation'] and analysis['inputs'][str(pp)]==sha(pp)
    hashes=read(rp)['inputs'].copy();verify(hashes)
    paths=[rp,pp,ap,OUT/'BOARD-RIVER-BOUNDS-POLICY-PILOT-PLAN.md']
    paths += [ROOT/'tools/research'/name for name in (
        'board_river_bounds_pilot_support_v1.py','board_river_bounds_pilot_run_v1.py',
        'board_river_bounds_bank_v1.py','crossed_complete_policy_batch_v1.py','crossed_complete_policy_comparison_v1.py',
        'sampled_batch_protocol_v2.py','sampled_evaluation_intervals_v1.py','sampled_physical_deals_v1.py',
        'weighted_evaluation_checkpoint_v1.py','evaluation_resume_routing_20260927.py','bounded_parallel_evaluation_archive_v2.py',
        'owned_columnar_evaluation_archive_v1.py','crossed_profile_columnar_v1.py','crossed_profile_columnar_v2.py',
        'crossed_profile_decoder_fast_candidate_20260927.py','later_average_support_v1.py','sampled_allin_protocol_v3.py',
        'global_research_inventory_v2.py','board_study_storage_v1.py')]
    paths += [ROOT/'target/release/examples'/name for name in ('hu_sampled_bank_bridge.exe','hu_sampled_profile_allin_evaluation_v1.exe')]
    hashes.update({str(p):sha(p) for p in paths});return hashes,result


class PairPreparation:
    def __init__(self,data,catalog):self.data=data;self.catalog=catalog;self.query=None;self.prepared={};self.calls=0
    def get(self,index,query):
        if self.query is not query:
            self.query=query;self.prepared={};self.calls+=1
        if index not in self.prepared:
            d=self.data[index];cpu=prepare_queries(query,d['layout'],self.catalog)
            self.prepared[index]=d['bank'].prepare(cpu)
        return self.prepared[index]


class Adapter:
    def __init__(self,shared,index,enabled):self.shared=shared;self.index=index;self.enabled=enabled
    def average(self,queries,*,guard):
        return self.shared.data[self.index]['bank'].average_prepared(self.shared.get(self.index,queries),enabled=self.enabled,chunk=8,guard=guard)


def load(guard,qualified):
    source=CONTEXT.read_text();matrix=OUT/'preflop-allin-matrix-control-v1-matrix.json'
    catalog_path=Path('S:/GTOpen-research/preflop-catalog-control-v1/native-preflop-catalog.json')
    args=dict(context_source=source,catalog_source=catalog_path.read_text(),matrix_sha256=sha(matrix),entry_mass=AllinMatrix(read(matrix),source).btn_mass)
    data=[];identities=[]
    for label,expected in zip(('9266201-board-root','9266301-board-root'),read(OUT/'board-river-bounds-bank-v1-registration.json')['banks']):
        guard();began=time.monotonic();docs,weights,identity=load_bank(label,bank_args=args,guard=guard)
        assert identity==expected
        layout=make_layout(docs,weights,completed_iterations=78,root_config=identity['root_config'],guard=guard,**args)
        data.append(dict(layout=layout,bank=CudaBank(layout,guard=guard)));identities.append(identity)
        del docs;gc.collect()
        print(json.dumps(dict(state='loaded_bank',arm=label,seconds=time.monotonic()-began)),flush=True)
    shared=PairPreparation(data,read(OUT/'board-later-public-state-catalog-v1.json'))
    policies=[Adapter(shared,i,enabled) for i in (0,1) for enabled in (False,True)]
    identity=dict(source_banks=identities,order=['A-original','A-bounded','B-original','B-bounded'],
        qualification_result_sha256=sha(OUT/'board-river-bounds-bank-v1-result.json'),
        correction='Exact river Fold/terminal-Call bounds, per-model/player scale, corrected own-action reach.')
    return policies,shared,identity
