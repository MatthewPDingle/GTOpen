"""Source-only/mocked board worker boundary controls; never execute native code.

The target values and invocation receipts below are explicitly synthetic. These
controls test rejection and artifact binding, not native/scientific correctness.
"""
import ast
import copy
import itertools
import json
import os
from pathlib import Path
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch

import preflop_expected_board_workers_v1 as worker

GENUINE_V2 = '--genuine-v2' in sys.argv
if GENUINE_V2:
    sys.argv.remove('--genuine-v2')


class SyntheticProvider:
    def __init__(self):
        self._plan = dict(boards=[[0, 4, 8, 12, 16], [1, 5, 9, 13, 17]],
            parent_state_sha256='a'*64)
        self.recipe = dict(generation=0, context_sha256='c'*64,
            registry_sha256='d'*64, model_sha256='e'*64,
            method='synthetic-software-control-no-native-targets')
        self.reductions = 0
        self.after_reduce = lambda: None

    def request(self, board):
        hands = [list(hand) for hand in itertools.combinations(
            [card for card in range(52) if card not in board], 2)]
        return dict(board=board.copy(), hands=[hands, copy.deepcopy(hands)]), list(range(1081))

    def draw_record(self, raw, *, expected_tree_sha256, draw_index):
        self.reductions += 1
        document = json.loads(raw)
        assert document == {'synthetic': True, 'board': self._plan['boards'][draw_index]}
        values = {'synthetic': [[.1, -.1]]}
        record = dict(draw_index=draw_index, board=self._plan['boards'][draw_index].copy(),
            model_sha256=self.recipe['model_sha256'], tree_sha256=expected_tree_sha256,
            policy_recipe_sha256=worker._digest(self.recipe), values=values,
            values_sha256=worker._digest(values))
        self.after_reduce()
        return record


class SyntheticInvocation:
    """File-only stand-in. There is no process launch in this class."""
    def __init__(self):
        self.calls = []
        self.verifications = 0
        self.after_run = lambda: None
        self.caller_pid = os.getpid()

    def run_native(self, executable, arguments, *, folder, label, expected_identities,
                   guard, timeout, max_output_bytes):
        guard()
        self.calls.append(dict(executable=str(executable), arguments=arguments,
            expected_identities=copy.deepcopy(expected_identities), timeout=timeout,
            max_output_bytes=max_output_bytes))
        request = json.loads(Path(arguments[1]).read_bytes())
        stdout, stderr, receipt = folder/'synthetic.stdout', folder/'synthetic.stderr', folder/'synthetic.receipt'
        stdout.write_bytes(json.dumps(dict(synthetic=True, board=request['board'])).encode())
        stderr.write_bytes(b'')
        doc = dict(method='synthetic-no-native-invocation', expected_identities=expected_identities,
            argv=[str(executable), *arguments],
            caller=dict(pid=self.caller_pid,creation_time=worker._STATE['creation_time']),
            timeout_seconds=timeout,max_output_bytes=max_output_bytes,
            started_unix=time.time(),terminal_unix=time.time())
        worker._save(receipt, doc)
        result = dict(receipt_path=str(receipt), receipt_sha256=worker.sha(receipt),
            stdout_path=str(stdout), stdout_sha256=worker.sha(stdout),
            stderr_path=str(stderr), stderr_sha256=worker.sha(stderr), receipt=doc)
        self.after_run()
        return result

    def verify_native(self, result, *, executable, arguments, expected_identities):
        self.verifications += 1
        assert result['receipt']['method'] == 'synthetic-no-native-invocation'
        assert result['receipt']['argv'] == [str(executable), *arguments]
        assert result['receipt']['expected_identities'] == expected_identities
        worker._check_identities(expected_identities)
        for prefix in ('receipt', 'stdout', 'stderr'):
            if worker.sha(result[prefix+'_path']) != result[prefix+'_sha256']:
                raise ValueError('Changed synthetic invocation artifact')


class BoardWorkerControls(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='typed-board-source-control-')
        self.root = Path(self.temp.name).resolve()
        self.context, self.executable, self.source = [self.root/name for name in
            ('context.json', 'never-executed.fake', 'native-source.fake')]
        self.context.write_bytes(b'{"synthetic":true}\r\n')
        self.executable.write_bytes(b'this file must never be executed')
        self.source.write_bytes(b'original synthetic source')
        self.identities = {str(path): worker.sha(path) for path in
            (self.context, self.executable, self.source)}
        self.provider, self.native = SyntheticProvider(), SyntheticInvocation()
        self.memory = types.SimpleNamespace(available=worker.RAM_RESERVE_BYTES)
        self.disk = types.SimpleNamespace(free=worker.DISK_RESERVE_BYTES)
        self.psutil = types.SimpleNamespace(virtual_memory=lambda: self.memory,
            disk_usage=lambda folder: self.disk,
            Process=lambda: types.SimpleNamespace(memory_info=lambda: types.SimpleNamespace(rss=1000)))
        self.previous_state = worker._STATE
        worker._STATE = dict(prepared=self.provider, recipe=copy.deepcopy(self.provider.recipe),
            plan=copy.deepcopy(self.provider._plan), context_path=self.context,
            executable=self.executable, folder=self.root, identities=self.identities,
            source_identities={str(Path(worker.__file__).resolve()):worker.sha(worker.__file__)},
            runtime_limits=worker._limits(dict(max_worker_seconds=60, native_timeout_seconds=10)),
            began=time.monotonic(), initialized_unix=time.time(), pid=os.getpid(),
            creation_time=123.0, psutil=self.psutil, production_available=lambda: True,
            native=self.native)
        self.cuda = patch.dict(os.environ, {'CUDA_VISIBLE_DEVICES':'-1'})
        self.cuda.start()

    def tearDown(self):
        self.cuda.stop()
        worker._STATE = self.previous_state
        self.temp.cleanup()

    def complete(self, index=0):
        return worker.complete(index, self.provider._plan['boards'][index].copy())

    def test_bind_complete_request_tree_recipe_plan_invocation_and_worker(self):
        returned = self.complete()
        result = returned['result']
        self.assertEqual(worker.sha(returned['path']), returned['sha256'])
        self.assertEqual(json.loads(Path(returned['path']).read_bytes()), result)
        request = json.loads(Path(result['request_artifact']).read_bytes())
        self.assertEqual(request, self.provider.request(result['board'])[0])
        self.assertEqual([len(hands) for hands in request['hands']], [1081,1081])
        self.assertEqual(result['request_sha256'], worker.sha(result['request_artifact']))
        self.assertEqual(result['request_document_sha256'], worker._digest(request))
        self.assertEqual(result['native_identities'], self.identities)
        self.assertEqual(result['invocation_identities'],
            {**self.identities, result['request_artifact']:result['request_sha256']})
        self.assertEqual(result['recipe_sha256'], worker._digest(self.provider.recipe))
        self.assertEqual(result['plan_sha256'], worker._digest(self.provider._plan))
        self.assertEqual(result['tree_sha256'], worker.sha(result['tree_artifact']))
        self.assertEqual(result['tree_artifact'], result['native_invocation']['stdout_path'])
        self.assertEqual(result['pid'], os.getpid())
        self.assertEqual(result['creation_time'], 123.0)
        self.assertEqual(result['cuda_visible_devices'], '-1')
        self.assertEqual(result['threadpool_limit'], 1)
        self.assertEqual(len(self.native.calls), 1)
        self.assertEqual(self.native.verifications, 2)
        self.assertEqual(result['record']['tree_sha256'], result['tree_sha256'])
        self.assertGreaterEqual(result['terminal_unix'], result['started_unix'])

    def test_order_is_bound_to_index_even_if_tasks_complete_out_of_order(self):
        second, first = self.complete(1), self.complete(0)
        self.assertEqual([second['result']['record']['draw_index'], first['result']['record']['draw_index']], [1,0])
        self.assertEqual(second['result']['board'], self.provider._plan['boards'][1])
        self.assertEqual(first['result']['plan_sha256'], second['result']['plan_sha256'])

    def test_wrong_board_indices_and_reordered_board_refuse_before_invocation(self):
        for index, board in ((True,self.provider._plan['boards'][0]),
                (-1,self.provider._plan['boards'][0]), (2,self.provider._plan['boards'][0]),
                (0,self.provider._plan['boards'][1]), (0,list(reversed(self.provider._plan['boards'][0])))):
            with self.subTest(index=index,board=board), self.assertRaises(ValueError):
                worker.complete(index, board)
        self.assertEqual(self.native.calls, [])
        self.assertFalse((self.root/'board-000').exists())

    def test_incomplete_private_domains_refuse_before_invocation(self):
        request = self.provider.request
        def incomplete(board):
            req, ids = request(board)
            req['hands'][1].pop()
            return req, ids
        self.provider.request = incomplete
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.native.calls, [])

    def test_changed_original_source_before_invocation_refuses(self):
        self.source.write_bytes(b'altered source')
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.native.calls, [])

    def test_changed_source_after_invocation_refuses_before_reduction(self):
        self.native.after_run = lambda: self.source.write_bytes(b'altered source')
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.provider.reductions, 0)
        self.assertFalse((self.root/'board-000'/'result.json').exists())
        self.assertTrue((self.root/'board-000'/'synthetic.receipt').exists())

    def test_changed_request_after_invocation_refuses_before_reduction(self):
        self.native.after_run = lambda: (self.root/'board-000'/'request.json').write_bytes(b'{}')
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.provider.reductions, 0)
        self.assertFalse((self.root/'board-000'/'result.json').exists())

    def test_changed_native_stdout_refuses_before_reduction(self):
        self.native.after_run = lambda: (self.root/'board-000'/'synthetic.stdout').write_bytes(b'{}')
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.provider.reductions, 0)

    def test_changed_source_during_reduction_refuses_publication(self):
        self.provider.after_reduce = lambda: self.source.write_bytes(b'altered after reduction')
        with self.assertRaises(ValueError): self.complete()
        self.assertFalse((self.root/'board-000'/'result.json').exists())

    def test_native_receipt_from_another_worker_refuses_before_reduction(self):
        self.native.caller_pid += 1
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.provider.reductions, 0)

    def test_frozen_recipe_and_plan_change_refuse(self):
        self.provider.recipe['generation'] = 1
        with self.assertRaises(ValueError): self.complete()
        self.provider.recipe = copy.deepcopy(worker._STATE['recipe'])
        self.provider._plan['boards'][1].reverse()
        with self.assertRaises(ValueError): self.complete()
        self.assertEqual(self.native.calls, [])

    def test_repeated_draw_refuses_and_preserves_first_artifact(self):
        returned = self.complete()
        with self.assertRaises(FileExistsError): self.complete()
        self.assertEqual(worker.sha(returned['path']), returned['sha256'])
        self.assertEqual(len(self.native.calls), 1)

    def test_resource_and_explicit_runtime_guards_refuse_before_invocation(self):
        for kind in ('ram','disk','production','deadline'):
            with self.subTest(kind=kind):
                self.memory.available = worker.RAM_RESERVE_BYTES
                self.disk.free = worker.DISK_RESERVE_BYTES
                worker._STATE['production_available'] = lambda: True
                worker._STATE['began'] = time.monotonic()
                if kind == 'ram': self.memory.available -= 1
                if kind == 'disk': self.disk.free -= 1
                if kind == 'production': worker._STATE['production_available'] = lambda: False
                if kind == 'deadline': worker._STATE['began'] -= 61
                with self.assertRaises((RuntimeError, TimeoutError)): self.complete()
        self.assertEqual(self.native.calls, [])

    def test_limits_are_required_and_validated_without_hidden_1200_deadline(self):
        for limits in ({}, {'max_worker_seconds':1200},
                {'max_worker_seconds':True,'native_timeout_seconds':10},
                {'max_worker_seconds':float('inf'),'native_timeout_seconds':10},
                {'max_worker_seconds':60,'native_timeout_seconds':float('nan')},
                {'max_worker_seconds':60,'native_timeout_seconds':61},
                {'max_worker_seconds':100000,'native_timeout_seconds':90000},
                {'max_worker_seconds':60,'native_timeout_seconds':10,'max_output_bytes':8_000_000_001},
                {'max_worker_seconds':60,'native_timeout_seconds':10,'max_output_bytes':True}):
            with self.subTest(limits=limits), self.assertRaises(ValueError): worker._limits(limits)
        self.assertEqual(worker._limits({'max_worker_seconds':180,'native_timeout_seconds':120}),
            {'max_worker_seconds':180,'native_timeout_seconds':120,'max_output_bytes':2_000_000_000})

    def test_legacy_payload_and_missing_native_identity_refuse(self):
        base = dict(state=None, model_source='', registry=None, resources={})
        worker._payload(base)
        for extra in ('context_sha256','root_state','btn_state','matrix_source','physical_catalog_source'):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                worker._payload({**base,extra:None})
        with self.assertRaises(ValueError):
            worker._identities({str(self.context):worker.sha(self.context)}, self.context, self.executable)

    def test_main_process_initialize_refuses_without_changing_parent_environment(self):
        before = dict(os.environ)
        with self.assertRaises(RuntimeError):
            worker.initialize({},self.context,self.executable,self.root,self.identities,{})
        self.assertEqual(dict(os.environ), before)

    def test_pool_pins_spawn_initializer_without_starting_any_process(self):
        payload = dict(state=None,model_source='',registry=None,resources={})
        with patch.object(worker,'ProcessPoolExecutor',return_value='source-only-executor') as executor:
            result = worker.pool(2,payload=payload,context_path=self.context,executable=self.executable,
                folder=self.root,expected_native_identities=self.identities,
                runtime_limits={'max_worker_seconds':60,'native_timeout_seconds':10})
        self.assertEqual(result, 'source-only-executor')
        call = executor.call_args.kwargs
        self.assertEqual(call['mp_context'].get_start_method(), 'spawn')
        self.assertEqual(call['initializer'], worker.initialize)
        self.assertEqual(call['max_workers'], 2)
        self.assertEqual(call['initargs'][0], payload)
        self.assertEqual(call['initargs'][4], self.identities)

    def test_source_uses_genuine_v2_provider_and_common_authenticated_execution(self):
        tree = ast.parse(Path(worker.__file__).read_text(encoding='utf-8'))
        providers = [node for node in ast.walk(tree) if isinstance(node,ast.ImportFrom)
            and any(alias.name == 'FrozenExpectedTargets' for alias in node.names)]
        self.assertEqual([node.module for node in providers], ['preflop_expected_native_targets_v2'])
        imported = {alias.name for node in ast.walk(tree) if isinstance(node,ast.Import) for alias in node.names}
        self.assertNotIn('subprocess', imported)
        self.assertIn('preflop_expected_native_execution_v1', imported)
        code = Path(worker.__file__).read_text(encoding='utf-8')
        self.assertIn('FrozenExpectedTargets(**payload)',code)


@unittest.skipUnless(GENUINE_V2, 'Pass --genuine-v2 with the established NumPy research runtime')
class GenuineV2SyntheticControls(unittest.TestCase):
    """Real v2 provider, invented payoff fixture; every native method blocked."""
    @classmethod
    def setUpClass(cls):
        import preflop_expected_training_control_fixture_v1 as fixture
        import sampled_visible_hybrid_checkpoint_v1 as storage
        cls.temp = tempfile.TemporaryDirectory(prefix='typed-board-genuine-control-',
            dir=Path(__file__).resolve().parent)
        cls.root = Path(cls.temp.name)
        cls.registry, cls.resources, cls.config, cls.previous = fixture.fixture(362,directory=cls.root)
        cls.key = cls.registry.fit_contexts[0]
        cls.model_source = storage.read_object(cls.root,cls.previous['next_model']).decode('utf-8')
        cls.payload = dict(state=cls.previous['contexts'][cls.key]['preflop_state'],
            model_source=cls.model_source,registry=cls.registry,resources=cls.resources)
        cls.context_path = cls.root/'exact-context.json'
        cls.context_path.write_bytes(cls.registry.source(cls.key).encode('utf-8'))
        cls.executable = cls.root/'never-execute.fake'
        cls.executable.write_bytes(b'synthetic no-native control')
        cls.identities = {str(path.resolve()):worker.sha(path) for path in (cls.context_path,cls.executable)}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_genuine_v2_complete_private_request_and_typed_resources(self):
        from preflop_expected_native_targets_v2 import FrozenExpectedTargets
        from preflop_expected_policy_v1 import RESOURCE_FIELDS
        provider = FrozenExpectedTargets(**self.payload)
        self.assertEqual(provider.recipe['method'],'typed-all-preflop-native-targets-v2')
        self.assertEqual(set(self.resources[self.key]),RESOURCE_FIELDS)
        board = self.payload['state'].plan()['boards'][0]
        req, ids = provider.request(board)
        expected = [list(hand) for hand in itertools.combinations(
            [card for card in range(52) if card not in board],2)]
        self.assertEqual(req,dict(board=board,hands=[expected,expected]))
        self.assertEqual(len(ids),1081)

    def initialize_without_spawn_or_native_work(self,payload=None,context_path=None,identities=None):
        import preflop_expected_native_execution_v1 as native
        # The source-only test deliberately bypasses the process entry check;
        # initialize still instantiates the actual v2 provider and exact sources.
        with patch.object(worker.multiprocessing,'current_process',
                return_value=types.SimpleNamespace(name='SpawnProcess-synthetic-control')), \
                patch.object(worker.multiprocessing,'get_start_method',return_value='spawn'), \
                patch('bounded_parallel_evaluation_archive_v2.production_available',return_value=True), \
                patch('psutil.virtual_memory',return_value=types.SimpleNamespace(available=20_000_000_000)), \
                patch('psutil.disk_usage',return_value=types.SimpleNamespace(free=40_000_000_000)), \
                patch.object(native,'run_native',side_effect=AssertionError('Native execution forbidden in this control')):
            worker.initialize(payload or self.payload,context_path or self.context_path,
                self.executable,self.root,identities or self.identities,
                {'max_worker_seconds':300,'native_timeout_seconds':120})

    def test_initialize_uses_genuine_v2_and_preserves_frozen_plan(self):
        prior = worker._STATE
        environment = dict(os.environ)
        try:
            self.initialize_without_spawn_or_native_work()
            self.assertEqual(worker._STATE['prepared'].__class__.__module__,'preflop_expected_native_targets_v2')
            self.assertEqual(worker._STATE['plan'],self.payload['state'].plan())
            self.assertEqual(worker._STATE['recipe']['model_sha256'],
                worker.sha(self.root/self.previous['next_model']['file']))
            self.assertEqual(os.environ['CUDA_VISIBLE_DEVICES'],'-1')
        finally:
            if worker._STATE is not None and 'limit' in worker._STATE:
                worker._STATE['limit'].restore_original_limits()
            worker._STATE = prior
            os.environ.clear(); os.environ.update(environment)

    def test_altered_model_generation_refuses_genuine_initialize(self):
        prior = worker._STATE
        environment = dict(os.environ)
        source = json.loads(self.model_source); source['generation'] += 1
        payload = {**self.payload,'model_source':json.dumps(source,separators=(',',':'))}
        try:
            with self.assertRaises(ValueError): self.initialize_without_spawn_or_native_work(payload=payload)
            self.assertIsNone(worker._STATE)
        finally:
            worker._STATE = prior
            os.environ.clear(); os.environ.update(environment)

    def test_changed_context_even_with_updated_file_hash_refuses(self):
        prior = worker._STATE
        environment = dict(os.environ)
        wrong = self.root/'different-context.json'
        wrong.write_bytes(self.registry.source(self.key).encode('utf-8')+b'\n')
        identities={str(wrong.resolve()):worker.sha(wrong),str(self.executable.resolve()):worker.sha(self.executable)}
        try:
            with self.assertRaises(ValueError):
                self.initialize_without_spawn_or_native_work(context_path=wrong,identities=identities)
            self.assertIsNone(worker._STATE)
        finally:
            worker._STATE = prior
            os.environ.clear(); os.environ.update(environment)


if __name__ == '__main__':
    unittest.main(verbosity=2)
