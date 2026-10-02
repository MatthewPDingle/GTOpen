"""Board cooperative-cancellation software controls; no native/scientific work.

The existing synthetic worker boundary fixture supplies invented requests and
targets. Native-loop callbacks are file-only mocks. One small Python child tests
that a real spawn-context Event communicates cancellation across processes; it
does not initialize a model, export a tree, query production, or publish state.
Prior controls/evidence and all unrelated source files remain untouched.
"""
import inspect
import json
import multiprocessing
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

import preflop_expected_board_workers_v1 as worker
import preflop_expected_board_workers_check_v1 as fixture

SCOPE = 'Software-only cooperative cancellation; synthetic file-only native-loop callbacks and one Python spawn Event probe; no native exporter, model fit, scientific simulation or state publication.'


def spawned_guard_probe(event, ready, results):
    worker._STATE = dict(cancel_event=event)
    ready.put(os.getpid())
    if not event.wait(timeout=10):
        results.put(dict(error='shared-event-timeout')); return
    try: worker.guard()
    except InterruptedError as exc:
        results.put(dict(pid=os.getpid(),exception=type(exc).__name__,message=str(exc)))
    else: results.put(dict(error='cancellation-not-observed'))


class CancellationControls(unittest.TestCase):
    def setUp(self):
        self.control = fixture.BoardWorkerControls(methodName='runTest')
        self.control.setUp()
        self.event = multiprocessing.get_context('spawn').Event()
        worker._STATE['cancel_event'] = self.event

    def tearDown(self): self.control.tearDown()

    def test_set_event_refuses_before_resource_or_production_probes(self):
        self.event.set()
        with patch.object(self.control.psutil,'virtual_memory',side_effect=AssertionError('RAM probe reached')), \
                patch.object(self.control.psutil,'disk_usage',side_effect=AssertionError('disk probe reached')):
            worker._STATE['production_available'] = lambda: self.fail('production probe reached')
            with self.assertRaises(InterruptedError): worker.guard()

    def test_canceled_draw_refuses_before_request_or_native_work(self):
        self.event.set()
        with self.assertRaises(InterruptedError): self.control.complete()
        self.assertEqual(self.control.native.calls,[])
        self.assertEqual(self.control.provider.reductions,0)
        self.assertFalse((self.control.root/'board-000').exists())

    def test_native_loop_guard_observes_event_and_preserves_failed_artifacts(self):
        loops=[]
        def no_process(executable,arguments,*,folder,label,expected_identities,guard,timeout,max_output_bytes):
            worker._save(folder/'synthetic-started.json',dict(scope=SCOPE,invoked_native=False))
            loops.append('guard-before-cancel'); guard()
            self.event.set(); loops.append('guard-after-cancel')
            try: guard()
            except InterruptedError:
                worker._save(folder/'synthetic-interrupted.json',dict(scope=SCOPE,exception='InterruptedError'))
                raise
            self.fail('mock native loop continued after cancellation')
        self.control.native.run_native = no_process
        with self.assertRaises(InterruptedError): self.control.complete()
        part=self.control.root/'board-000'
        self.assertTrue((part/'request.json').exists())
        self.assertTrue((part/'synthetic-interrupted.json').exists())
        self.assertFalse((part/'result.json').exists())
        self.assertEqual(self.control.provider.reductions,0)
        self.assertEqual(loops,['guard-before-cancel','guard-after-cancel'])

    def test_cancel_during_reduction_refuses_terminal_result(self):
        self.control.provider.after_reduce=self.event.set
        with self.assertRaises(InterruptedError): self.control.complete()
        self.assertEqual(self.control.provider.reductions,1)
        self.assertFalse((self.control.root/'board-000'/'result.json').exists())
        self.assertTrue((self.control.root/'board-000'/'synthetic.receipt').exists())

    def test_unset_event_preserves_existing_result_contract(self):
        returned=self.control.complete(); result=returned['result']
        self.assertEqual(result['record']['draw_index'],0)
        self.assertEqual(result['runtime_limits'],worker._STATE['runtime_limits'])
        self.assertNotIn('cancel_event',result)
        self.assertFalse(self.event.is_set())

    def test_default_no_event_retains_existing_call_compatibility(self):
        for function in (worker.initialize,worker.pool):
            parameters=inspect.signature(function).parameters
            self.assertEqual(list(parameters)[-1],'cancel_event')
            self.assertIsNone(parameters['cancel_event'].default)
        worker._STATE['cancel_event']=None
        self.assertEqual(self.control.complete()['result']['record']['draw_index'],0)

    def test_pool_passes_the_exact_shared_event_to_spawn_initializer(self):
        payload=dict(state=None,model_source='',registry=None,resources={})
        with patch.object(worker,'ProcessPoolExecutor',return_value='software-control') as executor:
            worker.pool(2,payload=payload,context_path=self.control.context,
                executable=self.control.executable,folder=self.control.root,
                expected_native_identities=self.control.identities,
                runtime_limits={'max_worker_seconds':60,'native_timeout_seconds':10},
                cancel_event=self.event)
        call=executor.call_args.kwargs
        self.assertEqual(call['mp_context'].get_start_method(),'spawn')
        self.assertEqual(call['initializer'],worker.initialize)
        self.assertIs(call['initargs'][-1],self.event)

    def test_real_spawn_event_is_observed_in_python_child_guard(self):
        context=multiprocessing.get_context('spawn')
        ready,results=context.Queue(),context.Queue()
        child=context.Process(target=spawned_guard_probe,args=(self.event,ready,results))
        try:
            child.start(); observed_pid=ready.get(timeout=10)
            self.assertNotEqual(observed_pid,os.getpid())
            self.event.set(); output=results.get(timeout=10)
            child.join(timeout=10)
            self.assertFalse(child.is_alive())
            self.assertEqual(child.exitcode,0)
            self.assertEqual(output['pid'],observed_pid)
            self.assertEqual(output['exception'],'InterruptedError')
        finally:
            if child.is_alive(): child.terminate(); child.join(timeout=10)
            ready.close(); results.close()
            ready.join_thread(); results.join_thread()


if __name__=='__main__':
    root=Path(sys.argv[1]).resolve(); root.mkdir(parents=True,exist_ok=False)
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(CancellationControls)
    result=unittest.TextTestRunner(stream=sys.stdout,verbosity=2).run(suite)
    evidence=dict(passed=result.wasSuccessful(),scope=SCOPE,tests=result.testsRun,
        errors=[dict(test=str(test),traceback=trace) for test,trace in result.errors],
        failures=[dict(test=str(test),traceback=trace) for test,trace in result.failures],
        input_identities={str(Path(module.__file__).resolve()):worker.sha(module.__file__)
            for module in (worker,fixture)},
        control_sha256=worker.sha(__file__))
    worker._save(root/'result.json',evidence)
    print(json.dumps(dict(passed=evidence['passed'],tests=evidence['tests'],scope=SCOPE)))
    raise SystemExit(0 if result.wasSuccessful() else 1)
