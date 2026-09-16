"""Validate synthetic range construction and prospective reference boundaries."""
import unittest
import copy
import numpy as np
import continuation_bridge_run as run


class BridgeChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.train=run.checked('training');cls.test=run.checked('evaluation')

    def test_fixed_counts_and_source_separation(self):
        self.assertEqual(len(self.train['cases']),36)
        self.assertEqual(len(self.train['jobs']),720)
        self.assertEqual(len(self.test['cases']),8)
        self.assertEqual(len(self.test['jobs']),400)
        self.assertFalse({c['family'] for c in self.train['cases']} & {c['family'] for c in self.test['cases']})
        self.assertEqual({c['stack']/c['pot'] for c in self.train['cases']},{4.,10.,16.})
        for m in [self.train,self.test]:
            self.assertEqual(len({j['id'] for j in m['jobs']}),len(m['jobs']))

    def test_overlap_guard_catches_controllers_between_batches(self):
        processes=[dict(ProcessId=i,Name=name,CommandLine=command) for i,(name,command) in enumerate([
            ('python.exe','python tools/research/continuation_bridge_run.py run'),
            ('python.exe','python tools/research/continuation_interface_reuse.py oracle'),
            ('python.exe','python tools/research/continuation_interface_reuse.py benchmark'),
            ('range-value-reference-night2.exe','reference manifest.json 4'),
            ('python.exe','python tools/research/continuation_refinement_report.py'),
            ('gto-server.exe','gto-server.exe'),
        ])]
        self.assertEqual([p['ProcessId'] for p in run.research_processes(processes,0)],[1,2,3])
        self.assertEqual([p['ProcessId'] for p in run.research_processes(processes,1)],[0,2,3])

    def test_boards_are_new_and_disjoint(self):
        a={b['board'] for b in self.train['boards']};b={b['board'] for b in self.test['boards']}
        self.assertFalse(a & b)
        old=run.study.night.checked_manifest()
        excluded={j['board'] for j in old['jobs']}
        for partition in ['development','evaluation']:
            excluded.update(x['board'] for x in run.study.checked(partition)['boards'])
        self.assertFalse((a | b) & excluded)

    def test_ranges_reproduce_declared_probability_mixtures(self):
        source={c['id']:c for c in run.study.read(run.study.night.OUT/'fixtures.json')['cases']}
        for case in self.train['cases']:
            ds=[]
            for parent in case['parents']:
                w=np.array(source[parent]['weights'])
                ds.append(w/(w*run.study.pilot.COMBOS).sum(axis=1,keepdims=True))
            f=case['broad_fraction']
            expected,_,_=run.study.night.clean_weights((1-f)*ds[0]+f*ds[1])
            np.testing.assert_array_equal(expected,case['weights'])
            actual=np.array([run.study.pilot.weights(case['range_oop']),run.study.pilot.weights(case['range_ip'])])
            np.testing.assert_allclose(actual,expected,atol=5e-10,rtol=0)
            self.assertTrue(np.isfinite(actual).all() and (actual>=0).all() and (actual<=1).all())

    def test_reference_audit_rejects_accounting_or_gap_corruption(self):
        m=run.study.night.checked_manifest();j=m['jobs'][0]
        r=run.study.read(run.study.night.OUT/'jobs'/f"{j['id']}.json")
        run.validate_reference(r,j,m)
        bad=copy.deepcopy(r);bad['gap_pct']=.11
        with self.assertRaises(AssertionError):run.validate_reference(bad,j,m)
        bad=copy.deepcopy(r);bad['means_bb'][0]+=.01
        with self.assertRaises(AssertionError):run.validate_reference(bad,j,m)
        bad=copy.deepcopy(r);bad['hands'][0][0]['ev_bb']+=100.
        with self.assertRaises(AssertionError):run.validate_reference(bad,j,m)


if __name__=='__main__':unittest.main()
