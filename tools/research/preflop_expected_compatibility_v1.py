"""Canonical derived compatibility values for parent/CPU-worker comparison.

The original constructor, matrix, policies, hashes and exact equality checks
are retained. Only these auxiliary matrix reductions use one BLAS thread in
both processes. This does not set the inference/fitting/native worker policy.
"""
from threadpoolctl import threadpool_limits
from exact_initial_training_ingest_v2 import InitialTargets as _InitialTargets

METHOD = 'one-thread-original-initial-target-compatibility-v1'


class CanonicalInitialTargets(_InitialTargets):
    def __init__(self, *args, **kwargs):
        with threadpool_limits(limits=1, user_api='blas'):
            super().__init__(*args, **kwargs)
