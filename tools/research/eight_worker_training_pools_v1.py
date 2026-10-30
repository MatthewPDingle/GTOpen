"""Bounded eight-process dispatch using the unchanged qualified CPU workers.

The caller owns resource admission. No worker policy, target, ordering, fitting,
or checkpoint logic is changed. Each spawned worker retains single-thread BLAS.
"""
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
import weighted_training_workers_v1 as baseline
import river_training_workers_v1 as river

BASE_FIELDS = ('context_path', 'cache', 'targets', 'generation', 'iteration',
               'executable', 'trace_executable', 'integration_executable')


def launch(workers, initializer, fields, args):
    if type(workers) is not int or not 1 <= workers <= 8:
        raise ValueError('One to eight admitted CPU workers required')
    if set(args) != set(fields):
        raise ValueError('Complete explicit worker arguments required')
    return ProcessPoolExecutor(max_workers=workers,
        mp_context=multiprocessing.get_context('spawn'), initializer=initializer,
        initargs=tuple(args[k] for k in fields))


def baseline_pool(workers, **args):
    return launch(workers, baseline.initialize, BASE_FIELDS, args)


def river_pool(workers, **args):
    return launch(workers, river.initialize, BASE_FIELDS+('river_payload', 'river_executable'), args)
