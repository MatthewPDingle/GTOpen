"""Prove mathematical code is unchanged and exercise the recovered reader."""
import ast
from pathlib import Path
import unittest
from sampled_physical_root_evaluation_v1 import ROOT
import test_later_action_complete_review_v1 as semantic
from hu_later_action_recovered_evaluation_review_20260925 import verify_batch

BASE=ROOT/'tools/research'


def tree(name):return ast.parse((BASE/name).read_text())
def function(module,name):return next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name==name)
def constants(module):
    return {n.targets[0].id:ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign)
            and isinstance(n.targets[0],ast.Name) and n.targets[0].id in ('TRAINING','PREFIXES','TEST_DEALS','TEST_SEED','BATCH_SIZE')}


class RoutingTests(unittest.TestCase):
    def test_same_worker_and_fixed_experiment(self):
        old=tree('hu_later_action_complete_evaluation_20260925.py')
        new=tree('hu_later_action_recovered_evaluation_20260925.py')
        self.assertEqual(ast.dump(function(old,'worker')),ast.dump(function(new,'worker')))
        a,b=constants(old),constants(new)
        for key in ('TEST_DEALS','TEST_SEED','BATCH_SIZE'):self.assertEqual(a[key],b[key])
        self.assertEqual(b['TRAINING'],('action-integrated-fresh-pilot-v1','later-action-first-audit-recovery-v1',
            'action-integrated-replication-v1','later-action-replication-volume-continuation-v1'))
        self.assertEqual(b['PREFIXES'],{'control':'later-action-recovered-evaluation-control-v1',
                                     'study':'later-action-recovered-evaluation-study-v1'})
        class LocationOnly(ast.NodeTransformer):
            def visit_Constant(self,node):
                if node.value=='T:/GTOpen-research':node.value='S:/GTOpen-research'
                return node
        self.assertEqual(ast.dump(LocationOnly().visit(function(old,'run'))),ast.dump(function(new,'run')))

    def test_same_independent_numerics_and_replay(self):
        old=tree('hu_later_action_complete_review_20260925.py')
        new=tree('hu_later_action_recovered_evaluation_review_20260925.py')
        for name in ('verify_batch','verify_stability'):
            self.assertEqual(ast.dump(function(old,name)),ast.dump(function(new,name)))
        class PrefixOnly(ast.NodeTransformer):
            def visit_Constant(self,node):
                if isinstance(node.value,str):node.value=node.value.replace('later-action-complete-evaluation-','later-action-recovered-evaluation-')
                return node
        self.assertEqual(ast.dump(PrefixOnly().visit(function(old,'main'))),ast.dump(function(new,'main')))


if __name__=='__main__':
    semantic.verify_batch=verify_batch
    suite=unittest.TestSuite([unittest.defaultTestLoader.loadTestsFromTestCase(RoutingTests),
                             unittest.defaultTestLoader.loadTestsFromTestCase(semantic.ReviewTests)])
    result=unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
