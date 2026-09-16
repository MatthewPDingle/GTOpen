import copy
import unittest
from unittest.mock import patch
import numpy as np
import continuation_policy_transfer as transfer


class PolicyTransferChecks(unittest.TestCase):
    def test_fresh_stratified_boards_are_reproducible_and_exclude_reserved(self):
        fixtures=transfer.study.read(transfer.study.pilot.AUDIT/'fixtures.json')['canonical_flops']
        excluded={b for b,_ in fixtures[:100]}
        a=transfer.board_sample(fixtures,excluded,'fixed-test-seed')
        b=transfer.board_sample(fixtures,excluded,'fixed-test-seed')
        self.assertEqual(a,b)
        self.assertFalse({r['board'] for r in a}&excluded)
        counts={key:sum(r['stratum']==key for r in a) for key in {r['stratum'] for r in a}}
        self.assertEqual(sorted(counts.values()),[10]*5)
        self.assertTrue(all(0<r['inclusion_probability']<=1 for r in a))

    def test_real_snapshot_strategy_layout_and_invalid_values(self):
        p=transfer.runtime.OUT/'repeat-0/original/iteration-150.json'
        snapshot=transfer.study.read(p)
        # Only iteration metadata is changed to exercise the pure validator.
        snapshot.update(iteration=500,start_iteration=150,warmup_iterations=0)
        transfer.validate_snapshot(snapshot)
        broken=copy.deepcopy(snapshot);broken['views'][0]['view']['strategy'][0]=float('nan')
        with self.assertRaises(AssertionError):transfer.validate_snapshot(broken)
        broken=copy.deepcopy(snapshot);broken['leaves'][0]['weights'][0]=[0.]*169
        with self.assertRaises(AssertionError):transfer.validate_snapshot(broken)

    def test_pending_sequencing_parent_blocks_gpu_use(self):
        with patch.object(transfer.bridge,'other_research',return_value=[]),patch.object(transfer.queue,'processes',return_value=[
                dict(ProcessId=-1,Name='python.exe',CommandLine='python continuation_shrunk_queue.py 44092')]):
            with self.assertRaisesRegex(AssertionError,'sequencing controller'):transfer.require_idle()

    def test_failed_accuracy_cannot_qualify_via_good_runtime(self):
        def read(path):
            return {'accuracy_screen_passed':False} if path.name=='evaluation.json' else {'within_runtime_target':True}
        with patch.object(transfer.study,'read',side_effect=read):
            with self.assertRaises(AssertionError):transfer.selection('N09')

    def test_every_case_must_pass_even_when_average_improves(self):
        cases=[dict(case=str(i),mae_pct_pot=dict(candidate=4.,balanced=10.),regression_vs_previous=0.) for i in range(4)]
        self.assertTrue(transfer.case_gate(cases))
        cases[-1]['mae_pct_pot']['candidate']=9.
        self.assertFalse(transfer.case_gate(cases))
        cases[-1]['mae_pct_pot']['candidate']=4.;cases[-1]['regression_vs_previous']=.100001
        self.assertFalse(transfer.case_gate(cases))


if __name__=='__main__':unittest.main()
