"""The storage amendment preserves the entire worker and scientific reader."""
import ast
from pathlib import Path
import unittest
import test_later_action_complete_review_v1 as semantic
from hu_later_action_compact_evaluation_review_20260925 import verify_batch

BASE=Path(__file__).resolve().parent
def tree(name):return ast.parse((BASE/name).read_text())
def fun(module,name):return next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==name)
def constants(module):
    return {n.targets[0].id:ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign)
            and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('TRAINING','TEST_DEALS','TEST_SEED','BATCH_SIZE')}

class RoutingTests(unittest.TestCase):
    def test_worker_and_experiment_unchanged(self):
        a=tree('hu_later_action_recovered_evaluation_20260925.py')
        b=tree('hu_later_action_compact_evaluation_20260925.py')
        self.assertEqual(ast.dump(fun(a,'worker')),ast.dump(fun(b,'worker')))
        self.assertEqual(constants(a),constants(b))
        self.assertEqual(constants(b)['TEST_DEALS'],65536)
        self.assertEqual(constants(b)['TEST_SEED'],382921)

    def test_independent_reader_unchanged(self):
        a=(BASE/'hu_later_action_recovered_evaluation_review_20260925.py').read_text()
        b=(BASE/'hu_later_action_compact_evaluation_review_20260925.py').read_text()
        self.assertEqual(b,a.replace('later-action-recovered-evaluation-','later-action-compact-evaluation-'))

if __name__=='__main__':
    semantic.verify_batch=verify_batch
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(RoutingTests),
                             unittest.defaultTestLoader.loadTestsFromTestCase(semantic.ReviewTests)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
