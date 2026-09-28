"""Isolated worker pool using qualified preflop-subset query preparation.

The caller owns resource admission. Installation is per worker instance after
the original initializer; no existing source or parent policy object changes.
"""
from types import MethodType
import river_training_workers_v1 as original
from eight_worker_training_pools_v1 import launch, BASE_FIELDS
from river_query_preflop_subset_v1 import prepare


def initialize(*args):
    original.initialize(*args)
    engine = original._STATE['river_engine']
    engine.prepare = MethodType(prepare, engine)


def pool(workers, **args):
    return launch(workers, initialize, BASE_FIELDS+('river_payload', 'river_executable'), args)
