"""Record CPU/native adapter implementation evidence; no scientific fitting."""
import os
os.environ.update(OPENBLAS_NUM_THREADS='1', OMP_NUM_THREADS='1', MKL_NUM_THREADS='1')
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest
import test_stack_context_native_adapters_v1 as checks


def sha(path):
    with Path(path).open('rb') as stream:return hashlib.file_digest(stream,'sha256').hexdigest()


def main():
    output=checks.OUT/'stack-context-native-adapters-v1-cpu-tests.json'
    attempt=checks.OUT/'stack-context-native-adapters-v1-cpu-attempt.json'
    if output.exists() or attempt.exists():raise ValueError('Preserve existing recorded implementation attempt')
    inputs={}
    for module in list(sys.modules.values()):
        path=getattr(module,'__file__',None)
        if path and Path(path).is_relative_to(checks.ROOT) and Path(path).suffix=='.py':
            inputs[str(Path(path).resolve())]=sha(path)
    inputs[str(Path(__file__).resolve())]=sha(__file__)
    with attempt.open('x') as stream:
        json.dump(dict(inputs=inputs,scientific_training=False),stream,indent=2)
    started=time.monotonic();log=io.StringIO()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(checks.NativeAdapterTests))
    identities=dict(inputs,**checks.INPUTS)
    changed=[path for path,expected in identities.items() if sha(path)!=expected]
    report=dict(complete=True,passed=result.wasSuccessful() and not changed,tests_run=result.testsRun,
        seconds=time.monotonic()-started,log=log.getvalue(),inputs=identities,changed_inputs=changed,
        native_invocations=checks.NATIVE,scientific_training=False,accuracy_qualified=False,
        full_training_cycle_qualified=False,cuda_worker_qualified=False,
        scope='Retained/synthetic CPU policy parity, native physical catalogs, tiny fixed-board trees and independent synthetic exact-value recursion.',
        limitation='Native outputs are hashed, not retained; no independent numeric readback or complete worker-cycle qualification.')
    with output.open('x') as stream:json.dump(report,stream,indent=2,allow_nan=False)
    print(log.getvalue())
    print(json.dumps(dict(passed=report['passed'],seconds=report['seconds'],native_invocations=len(checks.NATIVE))))
    if not report['passed']:raise SystemExit(1)


if __name__=='__main__':main()
